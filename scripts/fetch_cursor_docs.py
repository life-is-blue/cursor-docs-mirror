#!/usr/bin/env python3
"""Fetch Cursor documentation and markdown endpoints with Starlight sidebar alignment.

Cursor (cursor.com) publishes docs and markdown endpoints:
- Raw Markdown is available at `/docs/<slug>.md` and `/help/<slug>.md` (`Content-Type: text/plain` / `text/markdown`),
- `/llms.txt` provides the complete hierarchical resource directory covering Docs, CLI, and Help Center,
- The site sidebar DOM in HTML exposes navigation categories.

This fetcher:
  1. Discovers docs from `/llms.txt` and the official HTML sidebar navigation tree,
  2. Resolves slugs, category hierarchies, and human-friendly labels,
  3. Uses staged downloading and verifies invariants BEFORE committing any changes to disk,
  4. Preserves existing fetched_at timestamps on unchanged files for clean Git diffs,
  5. Enforces strict invariant verification: Manifest Files == Sidebar Leaves == SUMMARY Links,
  6. Disables file deletions on degraded or incomplete discovery to protect against accidental data loss.
"""

from __future__ import annotations

import gzip
import hashlib
import json
import os
import re
import ssl
import time
import zlib
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup
import certifi

REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = REPO_ROOT / "config" / "sources.json"
DOCS_ROOT = REPO_ROOT / "docs"
MANIFEST_PATH = DOCS_ROOT / "docs_manifest.json"
STARLIGHT_SIDEBAR_PATH = DOCS_ROOT / "starlight_sidebar.json"
SUMMARY_PATH = DOCS_ROOT / "SUMMARY.md"

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 (compatible; cursor-docs-mirror/1.0)"

REQUEST_TIMEOUT_SECONDS = 30
MAX_RETRIES = 4
BASE_BACKOFF_SECONDS = 1.5
SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())

ACRONYMS = {
    "mcp": "MCP",
    "cli": "CLI",
    "sdk": "SDK",
    "api": "API",
    "pr": "PR",
    "scim": "SCIM",
    "baa": "BAA",
    "sso": "SSO",
    "llm": "LLM",
    "acp": "ACP",
    "ai": "AI",
    "vscode": "VS Code",
    "jetbrains": "JetBrains",
    "github": "GitHub",
    "gitlab": "GitLab",
}


@dataclass(frozen=True)
class Source:
    source_id: str
    site_root: str
    llms_path: str
    docs_path_prefix: str
    output_subdir: str


@dataclass(frozen=True)
class DocPage:
    section: str
    slug: str
    url: str
    rel_path: str
    label: str
    category_path: Tuple[str, ...] = ()
    sidebar_label: Optional[str] = None
    badge: Optional[Dict[str, str]] = None


@dataclass(frozen=True)
class DiscoveryResult:
    sidebar_tree: List[Dict[str, Any]]
    pages: List[DocPage]
    is_degraded: bool


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def format_slug_as_title(slug: str) -> str:
    """Format a slug part into human readable title text."""
    last_part = slug.strip("/").split("/")[-1]
    words = re.split(r"[-_]+", last_part)
    formatted = []
    for w in words:
        low = w.lower()
        if low in ACRONYMS:
            formatted.append(ACRONYMS[low])
        else:
            formatted.append(w.capitalize())
    return " ".join(formatted)


def extract_title_from_markdown(content: str) -> Optional[str]:
    """Extract document title from frontmatter or first H1 heading."""
    lines = content.splitlines()
    # Check YAML frontmatter
    if lines and lines[0].strip() == "---":
        for line in lines[1:]:
            if line.strip() == "---":
                break
            if line.startswith("title:"):
                raw_title = line.split(":", 1)[1].strip().strip('"\'')
                if raw_title:
                    return raw_title

    # Check Markdown H1
    for line in lines[:25]:
        stripped = line.strip()
        if stripped.startswith("# "):
            title = stripped[2:].strip()
            title = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", title)
            if title:
                return title

    return None


def load_sources(config_path: Path) -> List[Source]:
    payload = json.loads(config_path.read_text(encoding="utf-8"))
    raw_sources = payload.get("sources", [])
    if not raw_sources:
        raise RuntimeError("No sources configured in config/sources.json")

    result: List[Source] = []
    for raw in raw_sources:
        source_id = raw.get("id")
        site_root = raw.get("site_root")
        llms_path = raw.get("llms_path", "/llms.txt")
        docs_path_prefix = raw.get("docs_path_prefix", "/docs/")
        output_subdir = raw.get("output_subdir")

        if not source_id or not site_root or not output_subdir:
            raise RuntimeError(f"Invalid source entry: {raw}")

        if not docs_path_prefix.startswith("/"):
            raise RuntimeError(f"docs_path_prefix must start with '/': {docs_path_prefix}")

        result.append(
            Source(
                source_id=source_id,
                site_root=site_root.rstrip("/"),
                llms_path=llms_path,
                docs_path_prefix="/" + docs_path_prefix.strip("/") + "/",
                output_subdir=output_subdir,
            )
        )
    return result


def _decode_body(raw: bytes, content_encoding: str | None) -> str:
    encoding = (content_encoding or "").lower()
    if encoding == "gzip" or (not encoding and raw[:2] == b"\x1f\x8b"):
        raw = gzip.decompress(raw)
    elif encoding == "deflate":
        raw = zlib.decompress(raw)
    elif encoding and encoding != "identity":
        raise RuntimeError(f"Unsupported content-encoding: {encoding}")
    return raw.decode("utf-8")


def fetch_bytes(url: str) -> Tuple[bytes, str | None, str | None]:
    last_error: Exception | None = None
    for attempt in range(1, MAX_RETRIES + 1):
        req = Request(
            url,
            headers={
                "User-Agent": USER_AGENT,
                "Accept": "text/markdown,text/plain,text/html,*/*",
                "Accept-Encoding": "gzip",
            },
        )
        try:
            with urlopen(req, timeout=REQUEST_TIMEOUT_SECONDS, context=SSL_CONTEXT) as response:
                raw = response.read()
                content_encoding = response.headers.get("Content-Encoding")
                content_type = response.headers.get("Content-Type")
            return raw, content_encoding, content_type
        except (HTTPError, URLError, TimeoutError) as exc:
            last_error = exc
            if attempt == MAX_RETRIES:
                break
            sleep_seconds = BASE_BACKOFF_SECONDS * (2 ** (attempt - 1))
            time.sleep(sleep_seconds)
    raise RuntimeError(f"Failed to fetch {url}: {last_error}")


def fetch_text(url: str) -> Tuple[str, str | None]:
    raw, content_encoding, content_type = fetch_bytes(url)
    return _decode_body(raw, content_encoding), content_type


def sanitize_url(url: str) -> str:
    """Sanitize URLs, fixing known upstream issues like duplicated hostnames."""
    url = url.strip()
    if "https://cursor.comhttps://cursor.com" in url:
        url = url.replace("https://cursor.comhttps://cursor.com", "https://cursor.com")
    return url


def docs_slug_from_url(url: str, source: Source) -> Optional[str]:
    """Convert URL or relative path into normalized slug."""
    if not url:
        return None

    cleaned_url = sanitize_url(url)
    raw_path = urlparse(cleaned_url).path if urlparse(cleaned_url).netloc else cleaned_url
    if any(p in {"..", "."} for p in raw_path.split("/")):
        return None

    full_url = urljoin(source.site_root + "/", cleaned_url)
    parsed = urlparse(full_url)
    expected_host = urlparse(source.site_root).netloc
    if parsed.netloc and parsed.netloc != expected_host:
        return None

    path = parsed.path or ""
    path = path.strip("/")

    if path.endswith(".md"):
        path = path[:-3]

    if not path or path == "docs" or path == "docs/home":
        return "overview"

    if path == "changelog":
        return None

    if path.startswith("docs/"):
        slug = path[len("docs/") :].strip("/")
    else:
        slug = path.strip("/")

    if not slug:
        return "overview"

    parts = slug.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        return None

    return "/".join(parts)


def markdown_url_for_slug(source: Source, slug: str) -> str:
    """Derive canonical markdown endpoint for a given slug."""
    slug = slug.strip().strip("/")
    if slug == "overview":
        return f"{source.site_root}/docs.md"
    if slug == "changelog":
        return f"{source.site_root}/changelog.md"
    if slug.startswith("help/"):
        return f"{source.site_root}/{slug}.md"
    return f"{source.site_root}/docs/{slug}.md"


def safe_rel_path(slug: str) -> str:
    slug = slug.strip().strip("/")
    if not slug:
        raise RuntimeError("Empty slug")
    parts = slug.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        raise RuntimeError(f"Unsafe slug: {slug}")
    return "/".join(parts) + ".md"


def parse_llms_txt(
    llms_text: str,
    source: Source,
) -> Tuple[List[Dict[str, Any]], Dict[str, DocPage]]:
    """Parse hierarchy, sections, and pages from cursor.com/llms.txt."""
    lines = llms_text.splitlines()
    top_h1: Optional[str] = None
    current_h2: Optional[str] = None

    doc_pages: Dict[str, DocPage] = {}
    sidebar_tree: List[Dict[str, Any]] = []

    # Map of (top_h1, current_h2) -> list of items
    h2_groups: Dict[Tuple[str, str], List[Dict[str, Any]]] = {}

    for raw_line in lines:
        line = raw_line.rstrip()
        if not line:
            continue

        if line.startswith("# "):
            top_h1 = line[2:].strip()
            continue

        if line.startswith("## "):
            h2 = line[3:].strip()
            if h2.lower() == "internationalization":
                break
            current_h2 = h2
            continue

        m = re.match(r"^(\s*)-\s+(https?://[^\s\)]+)", line)
        if not m:
            continue

        raw_url = m.group(2)
        clean_url = sanitize_url(raw_url)
        slug = docs_slug_from_url(clean_url, source)
        if not slug:
            continue

        section_name = current_h2 or top_h1 or "Documentation"
        category_tuple: Tuple[str, ...] = ()
        if top_h1 and top_h1 != "Cursor Documentation":
            category_tuple = (top_h1, section_name)
        elif current_h2:
            category_tuple = (current_h2,)
        else:
            category_tuple = ("Documentation",)

        label = format_slug_as_title(slug)
        starlight_slug = f"{source.output_subdir}/{slug}" if source.output_subdir else slug

        item_obj = {
            "label": label,
            "slug": starlight_slug,
        }

        group_key = (top_h1 or "Cursor Documentation", current_h2 or "General")
        h2_groups.setdefault(group_key, []).append(item_obj)

        if slug not in doc_pages:
            doc_pages[slug] = DocPage(
                section=section_name,
                slug=slug,
                url=clean_url if clean_url.endswith(".md") else markdown_url_for_slug(source, slug),
                rel_path=safe_rel_path(slug),
                label=label,
                category_path=category_tuple,
                sidebar_label=label,
            )

    # Build structured sidebar tree
    processed_top_sections: Dict[str, List[Dict[str, Any]]] = {}
    for (h1, h2), items in h2_groups.items():
        # Deduplicate items by slug within group
        seen_group_slugs = set()
        deduped_items = []
        for it in items:
            if it["slug"] not in seen_group_slugs:
                seen_group_slugs.add(it["slug"])
                deduped_items.append(it)

        group_obj = {
            "label": h2,
            "collapsed": True,
            "items": deduped_items,
        }
        processed_top_sections.setdefault(h1, []).append(group_obj)

    for h1, sub_groups in processed_top_sections.items():
        if h1 in {"Cursor Documentation"}:
            sidebar_tree.extend(sub_groups)
        else:
            sidebar_tree.append({
                "label": h1,
                "collapsed": True,
                "items": sub_groups,
            })

    return sidebar_tree, doc_pages


def parse_sidebar_from_html(
    html_text: str,
    source: Source,
) -> Tuple[List[Dict[str, Any]], Dict[str, DocPage]]:
    """Parse HTML sidebar DOM if available."""
    soup = BeautifulSoup(html_text, "html.parser")
    sidebar = soup.find("div", class_=lambda c: c and "overflow-y-auto" in c)
    if not sidebar:
        return [], {}

    sidebar_tree: List[Dict[str, Any]] = []
    doc_pages: Dict[str, DocPage] = {}

    for section in sidebar.find_all("div", recursive=False):
        h2 = section.find("h2")
        section_label = h2.get_text(strip=True) if h2 else "Documentation"
        items: List[Dict[str, Any]] = []

        for link in section.find_all("a"):
            href = link.get("href", "")
            slug = docs_slug_from_url(href, source)
            if not slug:
                continue

            link_text = link.get_text(strip=True)
            label = link_text if link_text and link_text != "Cursor Logo" else format_slug_as_title(slug)
            starlight_slug = f"{source.output_subdir}/{slug}" if source.output_subdir else slug

            items.append({
                "label": label,
                "slug": starlight_slug,
            })

            if slug not in doc_pages:
                doc_pages[slug] = DocPage(
                    section=section_label,
                    slug=slug,
                    url=markdown_url_for_slug(source, slug),
                    rel_path=safe_rel_path(slug),
                    label=label,
                    category_path=(section_label,),
                    sidebar_label=label,
                )

        if items:
            sidebar_tree.append({
                "label": section_label,
                "collapsed": True,
                "items": items,
            })

    return sidebar_tree, doc_pages


def discover_all_doc_pages(
    source: Source,
    fetch_text_fn: Callable[[str], Tuple[str, str | None]] = fetch_text,
) -> DiscoveryResult:
    """Discover all docs using llms.txt and HTML sidebar."""
    llms_pages: Dict[str, DocPage] = {}
    sidebar_tree: List[Dict[str, Any]] = []
    is_degraded = False

    # 1. Fetch llms.txt
    try:
        llms_url = urljoin(source.site_root + "/", source.llms_path.lstrip("/"))
        llms_text, _ = fetch_text_fn(llms_url)
        sidebar_tree, llms_pages = parse_llms_txt(llms_text, source)
        print(f"[INFO] Discovered {len(llms_pages)} pages from {llms_url}")
    except Exception as exc:  # noqa: BLE001
        print(f"[WARN] Failed to fetch llms.txt ({exc})")

    # 2. Try HTML sidebar discovery if needed
    if not sidebar_tree:
        try:
            html_url = f"{source.site_root}/docs"
            html_text, _ = fetch_text_fn(html_url)
            html_tree, html_pages = parse_sidebar_from_html(html_text, source)
            if html_tree and html_pages:
                print(f"[INFO] Discovered {len(html_pages)} pages from HTML sidebar DOM")
                sidebar_tree = html_tree
                llms_pages = html_pages
        except Exception as exc:  # noqa: BLE001
            print(f"[WARN] HTML discovery failed ({exc})")

    if not llms_pages or not sidebar_tree:
        raise RuntimeError(f"No documentation pages discovered for source {source.source_id}")

    return DiscoveryResult(
        sidebar_tree=sidebar_tree,
        pages=[llms_pages[slug] for slug in sorted(llms_pages.keys())],
        is_degraded=is_degraded,
    )


def generate_summary_md(sidebar_tree: List[Dict[str, Any]]) -> str:
    lines = ["# Cursor Documentation\n"]

    def walk(items: List[Dict[str, Any]], depth: int = 0) -> None:
        indent = "  " * depth
        for item in items:
            label = item.get("label", "")
            badge = item.get("badge")
            badge_str = f" `{badge['text']}`" if badge and "text" in badge else ""
            if "items" in item:
                lines.append(f"{indent}- {label}{badge_str}")
                walk(item["items"], depth + 1)
            elif "slug" in item:
                slug = item["slug"]
                rel_file = f"{slug}.md"
                lines.append(f"{indent}- [{label}]({rel_file}){badge_str}")

    walk(sidebar_tree)
    return "\n".join(lines) + "\n"


def extract_sidebar_leaf_slugs(tree: List[Dict[str, Any]]) -> List[str]:
    slugs: List[str] = []

    def walk(items: List[Dict[str, Any]]) -> None:
        for it in items:
            if "items" in it:
                walk(it["items"])
            elif "slug" in it:
                slugs.append(it["slug"])

    walk(tree)
    return sorted(list(set(slugs)))


def extract_summary_links(summary_text: str) -> List[str]:
    matches = re.findall(r"\]\(([^)]+\.md)\)", summary_text)
    return sorted(list(set([m[:-3] for m in matches])))


def looks_like_markdown(content: str, content_type: str | None) -> bool:
    ct = (content_type or "").lower()
    if "html" in ct:
        return False
    stripped = content.lstrip()
    if stripped.startswith("<!DOCTYPE") or stripped.lower().startswith("<html"):
        return False
    if "markdown" in ct or "text/plain" in ct:
        return True
    return stripped.startswith("#") or stripped.startswith("---")


def sha256_text(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def load_existing_manifest(path: Path) -> Dict:
    if not path.exists():
        return {"files": {}}
    return json.loads(path.read_text(encoding="utf-8"))


def remove_empty_dirs(start: Path, stop: Path) -> None:
    current = start
    while current != stop and current.exists():
        if any(current.iterdir()):
            break
        current.rmdir()
        current = current.parent


def check_deletion_integrity(
    discovered_keys: Set[str],
    existing_files: Dict[str, Any],
    is_degraded: bool,
    max_drop_ratio: float = 0.2,
) -> Tuple[bool, Optional[str]]:
    """Verify if discovery has sufficient completeness proof before deleting files."""
    if is_degraded:
        return False, "Discovery degraded"

    previous_keys = set(existing_files.keys())
    if not previous_keys:
        return True, None

    previous_count = len(previous_keys)
    discovered_count = len(discovered_keys)

    if previous_count >= 5 and discovered_count < int(previous_count * (1.0 - max_drop_ratio)):
        return False, (
            f"Discovery integrity check failed: discovered {discovered_count} pages vs "
            f"{previous_count} previously tracked pages (drop exceeds {int(max_drop_ratio * 100)}% threshold). "
            "Deletions blocked to protect against partial discovery/upstream layout truncation."
        )

    return True, None


def prune_tree_to_staged(tree: List[Dict[str, Any]], staged_slugs: Set[str]) -> List[Dict[str, Any]]:
    """Prune sidebar tree so it strictly contains only staged pages."""
    pruned: List[Dict[str, Any]] = []
    for item in tree:
        if "items" in item:
            sub_items = prune_tree_to_staged(item["items"], staged_slugs)
            if sub_items:
                new_item = dict(item)
                new_item["items"] = sub_items
                pruned.append(new_item)
        elif "slug" in item:
            if item["slug"] in staged_slugs:
                pruned.append(item)
    return pruned


def update_tree_labels_with_content(
    tree: List[Dict[str, Any]],
    titles_by_slug: Dict[str, str],
) -> None:
    """Update sidebar item labels if higher quality markdown H1 titles were found."""
    for item in tree:
        if "items" in item:
            update_tree_labels_with_content(item["items"], titles_by_slug)
        elif "slug" in item:
            slug = item["slug"]
            if slug in titles_by_slug:
                item["label"] = titles_by_slug[slug]


def sync_docs(
    config_path: Path = CONFIG_PATH,
    docs_root: Path = DOCS_ROOT,
    manifest_path: Path = MANIFEST_PATH,
    sidebar_path: Path = STARLIGHT_SIDEBAR_PATH,
    summary_path: Path = SUMMARY_PATH,
    strict_fetch: bool = False,
    fetch_text_fn: Callable[[str], Tuple[str, str | None]] = fetch_text,
) -> Tuple[int, Dict[str, Any]]:
    """Execute complete doc synchronization with atomic staging and strict validation."""
    docs_root.mkdir(parents=True, exist_ok=True)
    sources = load_sources(config_path)
    existing_manifest = load_existing_manifest(manifest_path)
    existing_files = existing_manifest.get("files", {})

    fetch_started_at = now_iso()
    staged_files: Dict[str, Dict[str, Any]] = {}
    staged_writes: Dict[Path, str] = {}
    combined_sidebar_tree: List[Dict[str, Any]] = []
    discovered_target_keys: Set[str] = set()
    h1_titles: Dict[str, str] = {}

    any_source_degraded = False
    total_pages = 0
    successful_pages = 0
    failed_pages: List[Tuple[str, str]] = []

    for source in sources:
        print(f"[INFO] Source={source.source_id} site={source.site_root}")
        discovery = discover_all_doc_pages(source, fetch_text_fn)
        if discovery.is_degraded:
            any_source_degraded = True
        combined_sidebar_tree.extend(discovery.sidebar_tree)
        print(f"[INFO] Source={source.source_id} total_target_pages={len(discovery.pages)}")
        total_pages += len(discovery.pages)

        source_root = docs_root / source.output_subdir

        for page in discovery.pages:
            manifest_key = f"{source.output_subdir}/{page.rel_path}"
            discovered_target_keys.add(manifest_key)
            dest = source_root / page.rel_path

            try:
                content, content_type = fetch_text_fn(page.url)
                if not looks_like_markdown(content, content_type):
                    raise RuntimeError(
                        f"Expected markdown from {page.url}, got content-type={content_type!r}"
                    )

                # Extract human title from markdown if available
                doc_title = extract_title_from_markdown(content) or page.label
                starlight_slug = f"{source.output_subdir}/{page.slug}" if source.output_subdir else page.slug
                h1_titles[starlight_slug] = doc_title

                digest = sha256_text(content)
                existing = existing_files.get(manifest_key, {})
                content_changed = existing.get("sha256") != digest or not dest.exists()

                if content_changed:
                    staged_writes[dest] = content
                    fetched_at = fetch_started_at
                else:
                    fetched_at = existing.get("fetched_at", fetch_started_at)

                entry: Dict[str, Any] = {
                    "source": source.source_id,
                    "section": page.section,
                    "category_path": list(page.category_path),
                    "slug": page.slug,
                    "label": doc_title,
                    "url": page.url,
                    "sha256": digest,
                    "bytes": len(content.encode("utf-8")),
                    "fetched_at": fetched_at,
                }
                if page.sidebar_label:
                    entry["sidebar_label"] = page.sidebar_label
                if page.badge:
                    entry["badge"] = page.badge

                staged_files[manifest_key] = entry
                successful_pages += 1
                print(f"[OK] {manifest_key} ({doc_title})")
                time.sleep(0.02)  # Polite pacing
            except Exception as exc:  # noqa: BLE001
                print(f"[WARN] failed url={page.url} err={exc}")
                failed_pages.append((page.url, str(exc)))

                # Defensive preservation
                if manifest_key in existing_files and dest.exists():
                    print(f"[INFO] Retaining existing local copy for failed page: {manifest_key}")
                    preserved_entry = dict(existing_files[manifest_key])
                    preserved_entry["last_fetch_status"] = "failed"
                    preserved_entry["last_fetch_error"] = str(exc)
                    staged_files[manifest_key] = preserved_entry

    # In strict mode, fail immediately on any download error
    if failed_pages and strict_fetch:
        print(f"[ERROR] STRICT_FETCH=1 and {len(failed_pages)} failures detected; aborting without disk mutations.")
        return 1, {"error": "strict_fetch_failures", "failed": failed_pages}

    # Update sidebar tree labels with extracted markdown H1 titles
    update_tree_labels_with_content(combined_sidebar_tree, h1_titles)
    summary_content = generate_summary_md(combined_sidebar_tree) if combined_sidebar_tree else ""

    # Invariant Verification across ALL modes: Sidebar Leaves == SUMMARY Links == Staged Files
    sidebar_slugs = extract_sidebar_leaf_slugs(combined_sidebar_tree)
    summary_slugs = extract_summary_links(summary_content)
    staged_slugs = sorted([k[:-3] for k in staged_files.keys()])

    invariant_errors: List[str] = []
    if sidebar_slugs != staged_slugs:
        diff_sm = set(sidebar_slugs) ^ set(staged_slugs)
        invariant_errors.append(f"Sidebar slugs mismatch with Staged files: diff={diff_sm}")
    if summary_slugs != staged_slugs:
        diff_sum = set(summary_slugs) ^ set(staged_slugs)
        invariant_errors.append(f"SUMMARY.md links mismatch with Staged files: diff={diff_sum}")

    if invariant_errors:
        for err in invariant_errors:
            print(f"[ERROR] Invariant violated: {err}")
        print("[ERROR] Aborting sync to prevent committing inconsistent artifacts.")
        return 1, {"error": "invariant_violation", "details": invariant_errors}

    if successful_pages == 0 and total_pages > 0:
        print("[ERROR] Zero documents fetched successfully; aborting sync.")
        return 1, {"error": "zero_successful_pages"}

    # Deletion Integrity Check
    allow_deletions, deletion_ineligibility_reason = check_deletion_integrity(
        discovered_target_keys, existing_files, any_source_degraded
    )

    if not allow_deletions and strict_fetch and (set(existing_files.keys()) - discovered_target_keys):
        print(f"[ERROR] STRICT_FETCH=1 and deletion integrity verification failed: {deletion_ineligibility_reason}")
        return 1, {"error": "deletion_integrity_failed", "reason": deletion_ineligibility_reason}

    # --- ATOMIC COMMIT PHASE ---

    # 1. Write updated markdown files
    for dest_path, content in staged_writes.items():
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        dest_path.write_text(content, encoding="utf-8")

    # 2. Deletions
    previous_paths = set(existing_files.keys())
    if not allow_deletions:
        print(f"[WARN] {deletion_ineligibility_reason}; skipping file deletions to protect data.")
        removed_paths: List[str] = []
        for prev_key in sorted(previous_paths - discovered_target_keys):
            if prev_key in existing_files:
                staged_files[prev_key] = existing_files[prev_key]
    else:
        removed_paths = sorted(previous_paths - discovered_target_keys)

    for removed in removed_paths:
        file_path = docs_root / removed
        if file_path.exists():
            print(f"[INFO] Removing deleted upstream document: {removed}")
            file_path.unlink()
            remove_empty_dirs(file_path.parent, docs_root)

    # 3. Write sidebar & SUMMARY
    if combined_sidebar_tree:
        sidebar_path.write_text(
            json.dumps(combined_sidebar_tree, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(f"[INFO] Wrote Starlight sidebar configuration to {sidebar_path}")

        summary_path.write_text(summary_content, encoding="utf-8")
        print(f"[INFO] Wrote SUMMARY.md index to {summary_path}")

    # 4. Write manifest
    manifest = {
        "generated_at": now_iso(),
        "tool": "scripts/fetch_cursor_docs.py",
        "strict_fetch": strict_fetch,
        "is_degraded": any_source_degraded,
        "sources": [
            {
                "id": s.source_id,
                "site_root": s.site_root,
                "llms_path": s.llms_path,
                "docs_path_prefix": s.docs_path_prefix,
                "output_subdir": s.output_subdir,
            }
            for s in sources
        ],
        "sidebar_file": str(sidebar_path.relative_to(docs_root.parent) if sidebar_path.is_relative_to(docs_root.parent) else sidebar_path.name),
        "summary_file": str(summary_path.relative_to(docs_root.parent) if summary_path.is_relative_to(docs_root.parent) else summary_path.name),
        "stats": {
            "total_pages": total_pages,
            "successful_pages": successful_pages,
            "failed_pages": len(failed_pages),
            "removed_files": len(removed_paths),
            "invariants_passed": True,
        },
        "failed": [{"url": url, "error": err} for url, err in failed_pages],
        "files": {k: staged_files[k] for k in sorted(staged_files.keys())},
    }

    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    print("\n[SUMMARY]")
    print(f"total_pages={total_pages}")
    print(f"successful_pages={successful_pages}")
    print(f"failed_pages={len(failed_pages)}")
    print(f"removed_files={len(removed_paths)}")
    print(f"is_degraded={any_source_degraded}")
    print("invariants_passed=True")

    return 0, manifest


def main() -> int:
    strict_fetch = os.environ.get("STRICT_FETCH", "0") == "1"
    code, _ = sync_docs(strict_fetch=strict_fetch)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
