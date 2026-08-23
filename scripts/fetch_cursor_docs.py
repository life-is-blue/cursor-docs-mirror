#!/usr/bin/env python3
"""Fetch Cursor documentation and markdown endpoints with Starlight sidebar alignment.

Cursor (cursor.com) publishes docs and markdown endpoints:
- Raw Markdown is available at `/docs/<slug>.md` and `/help/<slug>.md` (`Content-Type: text/plain` / `text/markdown`),
- `/llms.txt` provides hierarchical resource directory covering Docs, CLI, and Help Center,
- The site sidebar DOM in HTML exposes navigation categories, badges, and hierarchical structure.

This fetcher:
  1. Enforces strict URL whitelisting (/docs/** and /help/**) to prevent pollution from site navigation,
  2. Locates the true documentation sidebar DOM using structural evidence scoring,
  3. Uses explicit category canonicalization to unify cross-source taxonomy without parallel trees,
  4. Performs dual-source discovery (HTML DOM spine + llms.txt union complement with hierarchical category_path mounting),
  5. Tracks discovery degradation (is_degraded) to veto deletions when any discovery channel fails,
  6. Fails closed on corrupted existing manifests to protect historical baselines,
  7. Preserves closed-loop invariants across all modes: Manifest Files == Sidebar Leaves == SUMMARY Links,
     and Sidebar Breadcrumbs == Manifest category_path across every individual document,
  8. Separates versioned repository artifacts from ephemeral run metrics (no transient errors in git-tracked manifest),
  9. Implements application-level snapshot rollback on commit errors,
  10. Enforces zero-noise diff: preserves previous generated_at and skips disk writes when content is unchanged.
"""

from __future__ import annotations

import gzip
import hashlib
import json
import os
import re
import shutil
import ssl
import time
import uuid
import zlib
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup, Tag
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

CATEGORY_CANONICAL_NAMES = {
    "cloud-agents": "Cloud Agents",
    "cloud agents": "Cloud Agents",
    "cloud agent": "Cloud Agents",
    "cli documentation": "CLI",
    "cli": "CLI",
    "cursor documentation": "Get Started",
    "customizing": "Customize",
    "customize": "Customize",
    "customize cursor": "Customize",
    "teams & enterprise": "Account",
    "teams": "Account",
    "account": "Account",
    "help center": "Help Center",
    "getting started": "Get Started",
    "get started": "Get Started",
    "origin": "Origin",
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


def canonicalize_category_name(name: str) -> str:
    """Explicit canonicalization for category/section names across sources."""
    cleaned = re.sub(r"\s+", " ", name.strip())
    low = cleaned.lower()
    return CATEGORY_CANONICAL_NAMES.get(low, cleaned)


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
    if lines and lines[0].strip() == "---":
        for line in lines[1:]:
            if line.strip() == "---":
                break
            if line.startswith("title:"):
                raw_title = line.split(":", 1)[1].strip().strip('"\'')
                if raw_title:
                    return raw_title

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
    """Convert URL or relative path into normalized slug, strictly bound to documentation endpoints."""
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

    path = (parsed.path or "").strip("/")
    if path.endswith(".md"):
        path = path[:-3]

    if not path or path in {"docs", "docs/home"}:
        return "overview"

    # Strictly whitelist documentation paths
    if path.startswith("docs/"):
        slug = path[len("docs/") :].strip("/")
    elif path.startswith("help/"):
        slug = path
    else:
        return None

    if not slug or slug in {"home", "index"}:
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
            top_h1 = canonicalize_category_name(line[2:].strip())
            continue

        if line.startswith("## "):
            h2 = canonicalize_category_name(line[3:].strip())
            if h2.lower() == "internationalization":
                break
            current_h2 = h2
            continue

        # Match bullet points: '- https://...' or '- [Custom Label](https://...)'
        m_link = re.match(r"^(\s*)-\s+\[([^\]]+)\]\((https?://[^\s\)]+)\)", line)
        if m_link:
            custom_title = m_link.group(2).strip()
            raw_url = m_link.group(3)
        else:
            m_plain = re.match(r"^(\s*)-\s+(https?://[^\s\)]+)", line)
            if not m_plain:
                continue
            custom_title = None
            raw_url = m_plain.group(2)

        clean_url = sanitize_url(raw_url)
        slug = docs_slug_from_url(clean_url, source)
        if not slug:
            continue

        section_name = current_h2 or top_h1 or "Get Started"
        category_tuple: Tuple[str, ...] = ()
        if top_h1 and top_h1 not in {"Get Started", "Cursor Documentation"}:
            category_tuple = (top_h1, section_name) if section_name != top_h1 else (top_h1,)
        elif current_h2:
            category_tuple = (current_h2,)
        else:
            category_tuple = ("Get Started",)

        label = custom_title or format_slug_as_title(slug)
        starlight_slug = f"{source.output_subdir}/{slug}" if source.output_subdir else slug

        item_obj = {
            "label": label,
            "slug": starlight_slug,
        }

        group_key = (top_h1 or "Get Started", current_h2 or "General")
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
        if h1 in {"Get Started", "Cursor Documentation"}:
            sidebar_tree.extend(sub_groups)
        else:
            sidebar_tree.append({
                "label": h1,
                "collapsed": True,
                "items": sub_groups,
            })

    return sidebar_tree, doc_pages


def _extract_badge(tag: Tag) -> Optional[Dict[str, str]]:
    """Extract badge info from HTML tag if present."""
    badge_el = tag.find(
        lambda e: e.name in {"span", "div", "badge"}
        and (
            any(
                "badge" in c or "pill" in c or "tag" in c
                for c in (e.get("class") or [])
            )
            or e.has_attr("data-badge")
        )
    )
    if badge_el:
        text = badge_el.get_text(strip=True)
        if text:
            variant = "note"
            cls_str = " ".join(badge_el.get("class") or []).lower()
            if "danger" in cls_str or "red" in cls_str:
                variant = "danger"
            elif "warning" in cls_str or "yellow" in cls_str or "amber" in cls_str:
                variant = "caution"
            elif "success" in cls_str or "green" in cls_str:
                variant = "success"
            elif "tip" in cls_str or "blue" in cls_str or "purple" in cls_str:
                variant = "tip"
            return {"text": text, "variant": variant}
    return None


def _clean_tag_text(tag: Tag) -> str:
    """Extract clean text from tag, removing inner badges or utility tags."""
    clone = BeautifulSoup(str(tag), "html.parser").find()
    if clone is None or not isinstance(clone, Tag):
        return tag.get_text(strip=True)
    for b in clone.find_all(
        lambda e: any(
            "badge" in c or "pill" in c or "tag" in c
            for c in (e.get("class") or [])
        )
    ):
        b.decompose()
    return clone.get_text(strip=True)


def _find_docs_sidebar_container(soup: BeautifulSoup, source: Source) -> Optional[Tag]:
    """Locate the true documentation sidebar container using structural evidence scoring."""
    candidates = soup.find_all(
        lambda e: isinstance(e, Tag)
        and e.name in {"nav", "aside", "div"}
        and (
            any(
                re.search(r"sidebar|doc-nav|docs-menu|documentation", c, re.I)
                for c in (e.get("class") or [])
            )
            or (e.has_attr("aria-label") and re.search(r"sidebar|docs|documentation", e["aria-label"], re.I))
            or (e.has_attr("data-sidebar"))
            or (e.name == "div" and any("overflow-y-auto" in c for c in (e.get("class") or [])))
        )
    )

    if not candidates:
        candidates = soup.find_all(["nav", "aside"])

    best_candidate: Optional[Tag] = None
    best_score = 0

    for cand in candidates:
        links = cand.find_all("a")
        if not links:
            continue

        doc_links_count = 0
        non_doc_links_count = 0
        for a in links:
            href = a.get("href", "")
            slug = docs_slug_from_url(href, source)
            if slug:
                doc_links_count += 1
            else:
                non_doc_links_count += 1

        if doc_links_count >= 2 and doc_links_count > non_doc_links_count:
            score = doc_links_count * 10 - non_doc_links_count * 5
            if score > best_score:
                best_score = score
                best_candidate = cand

    return best_candidate


def parse_sidebar_from_html(
    html_text: str,
    source: Source,
) -> Tuple[List[Dict[str, Any]], Dict[str, DocPage]]:
    """Parse hierarchical HTML sidebar DOM with sequential DOM child traversal, explicit heading boundaries, and badges."""
    soup = BeautifulSoup(html_text, "html.parser")
    sidebar = _find_docs_sidebar_container(soup, source)

    if not sidebar:
        return [], {}

    doc_pages: Dict[str, DocPage] = {}

    def _parse_link_tag(link: Tag, current_categories: Tuple[str, ...]) -> Optional[Dict[str, Any]]:
        href = link.get("href", "")
        slug = docs_slug_from_url(href, source)
        if not slug:
            return None

        link_text = _clean_tag_text(link)
        label = link_text if link_text and link_text != "Cursor Logo" else format_slug_as_title(slug)
        badge = _extract_badge(link)
        starlight_slug = f"{source.output_subdir}/{slug}" if source.output_subdir else slug

        item_obj: Dict[str, Any] = {
            "label": label,
            "slug": starlight_slug,
        }
        if badge:
            item_obj["badge"] = badge

        sec_name = current_categories[-1] if current_categories else "Get Started"
        if slug not in doc_pages:
            doc_pages[slug] = DocPage(
                section=sec_name,
                slug=slug,
                url=markdown_url_for_slug(source, slug),
                rel_path=safe_rel_path(slug),
                label=label,
                category_path=current_categories or (sec_name,),
                sidebar_label=label,
                badge=badge,
            )
        return item_obj

    def parse_container_children(
        container: Tag,
        current_categories: Tuple[str, ...],
    ) -> List[Dict[str, Any]]:
        items: List[Dict[str, Any]] = []

        for child in container.children:
            if not isinstance(child, Tag):
                continue

            if child.name in {"script", "style", "svg", "summary"}:
                continue

            # 1. Collapsible <details>
            if child.name == "details":
                summary = child.find("summary", recursive=False) or child.find("summary")
                raw_summary_label = _clean_tag_text(summary) if summary else "Section"
                summary_label = canonicalize_category_name(raw_summary_label)
                summary_badge = _extract_badge(summary) if summary else None
                is_collapsed = not child.has_attr("open")

                sub_categories = (*current_categories, summary_label)
                sub_items = parse_container_children(child, sub_categories)

                if sub_items:
                    group_obj: Dict[str, Any] = {
                        "label": summary_label,
                        "collapsed": is_collapsed,
                        "items": sub_items,
                    }
                    if summary_badge:
                        group_obj["badge"] = summary_badge
                    items.append(group_obj)

            # 2. Standalone Link <a>
            elif child.name == "a":
                item_obj = _parse_link_tag(child, current_categories)
                if item_obj:
                    items.append(item_obj)

            # 3. Section/Group containers: <div>, <section>, <ul>, <ol>, <li>, <nav>, <aside>, <main>
            elif child.name in {"div", "section", "ul", "ol", "li", "nav", "aside", "main"}:
                header = child.find(["h1", "h2", "h3", "h4", "h5", "h6"], recursive=False)
                if not header and child.name in {"div", "section"}:
                    first_el = child.find()
                    if first_el and first_el.name in {"h1", "h2", "h3", "h4", "h5", "h6"}:
                        header = first_el

                if header:
                    raw_sec_label = _clean_tag_text(header) or (current_categories[-1] if current_categories else "Get Started")
                    sec_label = canonicalize_category_name(raw_sec_label)
                    sec_badge = _extract_badge(header)
                    sub_categories = (*current_categories, sec_label) if sec_label not in current_categories else current_categories
                    sub_items = parse_container_children(child, sub_categories)
                    if sub_items:
                        group_obj = {
                            "label": sec_label,
                            "collapsed": True,
                            "items": sub_items,
                        }
                        if sec_badge:
                            group_obj["badge"] = sec_badge
                        items.append(group_obj)
                else:
                    inner_items = parse_container_children(child, current_categories)
                    items.extend(inner_items)

        return items

    sidebar_tree = parse_container_children(sidebar, ())

    def sanitize_tree(tree: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        cleaned: List[Dict[str, Any]] = []
        for it in tree:
            if "items" in it:
                sanitized_subs = sanitize_tree(it["items"])
                if sanitized_subs:
                    entry = dict(it)
                    entry["items"] = sanitized_subs
                    cleaned.append(entry)
            elif "slug" in it:
                cleaned.append(it)
        return cleaned

    sidebar_tree = sanitize_tree(sidebar_tree)
    return sidebar_tree, doc_pages


def attach_page_to_sidebar_tree(
    tree: List[Dict[str, Any]],
    page: DocPage,
    starlight_slug: str,
) -> None:
    """Attach a document page into the sidebar tree strictly following its canonicalized category_path hierarchy."""
    item_obj: Dict[str, Any] = {"label": page.label, "slug": starlight_slug}
    if page.badge:
        item_obj["badge"] = page.badge

    raw_path = list(page.category_path) if page.category_path else [page.section or "Get Started"]
    cat_path = [canonicalize_category_name(c) for c in raw_path]

    if len(cat_path) > 1 and cat_path[0] == cat_path[1]:
        cat_path = cat_path[1:]

    current_level = tree
    for i, cat_label in enumerate(cat_path):
        group = None
        for item in current_level:
            if "items" in item and canonicalize_category_name(item.get("label", "")) == cat_label:
                group = item
                break

        if group is None:
            group = {
                "label": cat_label,
                "collapsed": True,
                "items": [],
            }
            current_level.append(group)

        if i == len(cat_path) - 1:
            if not any(sub.get("slug") == starlight_slug for sub in group["items"]):
                group["items"].append(item_obj)
        else:
            has_subgroups = any("items" in sub for sub in group["items"])
            if not has_subgroups and len(cat_path) == 2 and cat_path[1] in {"Get Started", "General", "Overview"}:
                if not any(sub.get("slug") == starlight_slug for sub in group["items"]):
                    group["items"].append(item_obj)
                break
            current_level = group["items"]


def discover_all_doc_pages(
    source: Source,
    fetch_text_fn: Callable[[str], Tuple[str, str | None]] = fetch_text,
) -> DiscoveryResult:
    """Discover docs using true dual-source discovery (HTML DOM spine + llms.txt union complement)."""
    html_tree: List[Dict[str, Any]] = []
    html_pages: Dict[str, DocPage] = {}
    html_ok = False

    # 1. Fetch & Parse HTML Sidebar
    try:
        html_url = f"{source.site_root}/docs"
        html_text, _ = fetch_text_fn(html_url)
        html_tree, html_pages = parse_sidebar_from_html(html_text, source)
        if html_tree and html_pages:
            html_ok = True
            print(f"[INFO] Discovered {len(html_pages)} pages from HTML sidebar DOM")
    except Exception as exc:  # noqa: BLE001
        print(f"[WARN] HTML discovery failed ({exc})")

    # 2. Fetch & Parse llms.txt
    llms_tree: List[Dict[str, Any]] = []
    llms_pages: Dict[str, DocPage] = {}
    llms_ok = False
    try:
        llms_url = urljoin(source.site_root + "/", source.llms_path.lstrip("/"))
        llms_text, _ = fetch_text_fn(llms_url)
        llms_tree, llms_pages = parse_llms_txt(llms_text, source)
        if llms_tree and llms_pages:
            llms_ok = True
            print(f"[INFO] Discovered {len(llms_pages)} pages from {llms_url}")
    except Exception as exc:  # noqa: BLE001
        print(f"[WARN] Failed to fetch llms.txt ({exc})")

    if not html_ok and not llms_ok:
        raise RuntimeError(f"No documentation pages discovered for source {source.source_id}")

    # True Dual-Source Synthesis
    if html_ok and llms_ok:
        is_degraded = False
        merged_pages: Dict[str, DocPage] = dict(html_pages)
        sidebar_tree = [dict(g) for g in html_tree]

        # Union complement: complement missing pages from llms.txt dynamically into matching hierarchy
        missing_slugs = set(llms_pages.keys()) - set(html_pages.keys())
        if missing_slugs:
            print(f"[INFO] Dual-source complement: dynamically mounting {len(missing_slugs)} missing pages from llms.txt")
            for slug in sorted(missing_slugs):
                llms_page = llms_pages[slug]
                merged_pages[slug] = llms_page
                starlight_slug = f"{source.output_subdir}/{slug}" if source.output_subdir else slug
                attach_page_to_sidebar_tree(sidebar_tree, llms_page, starlight_slug)

    elif html_ok:
        is_degraded = True
        print("[WARN] Discovery degraded: llms.txt failed, running in HTML-only mode")
        sidebar_tree = html_tree
        merged_pages = html_pages
    else:
        is_degraded = True
        print("[WARN] Discovery degraded: HTML DOM failed, running in llms.txt-fallback mode")
        sidebar_tree = llms_tree
        merged_pages = llms_pages

    return DiscoveryResult(
        sidebar_tree=sidebar_tree,
        pages=[merged_pages[slug] for slug in sorted(merged_pages.keys())],
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


def extract_sidebar_breadcrumbs(tree: List[Dict[str, Any]]) -> Dict[str, Tuple[str, ...]]:
    """Extract mapping from leaf slug to its full ancestor label path (breadcrumb hierarchy)."""
    breadcrumbs: Dict[str, Tuple[str, ...]] = {}

    def walk(items: List[Dict[str, Any]], current_path: Tuple[str, ...]) -> None:
        for it in items:
            label = it.get("label", "")
            if "items" in it:
                walk(it["items"], (*current_path, canonicalize_category_name(label)))
            elif "slug" in it:
                breadcrumbs[it["slug"]] = current_path

    walk(tree, ())
    return breadcrumbs


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


def load_existing_manifest(path: Path) -> Dict[str, Any]:
    """Load existing manifest, failing closed if the file exists but is corrupted."""
    if not path.exists():
        return {"files": {}}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or "files" not in data or not isinstance(data["files"], dict):
            raise ValueError("Manifest JSON must be an object containing a 'files' mapping.")
        return data
    except Exception as exc:
        print(f"[ERROR] Corrupted or invalid existing manifest at {path}: {exc}")
        raise RuntimeError(f"Corrupted existing manifest at {path}: {exc}. Aborting sync to prevent data loss.") from exc


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
        return False, "Discovery degraded (HTML or llms.txt unavailable); deletions blocked to protect data"

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
    """Prune sidebar tree so it strictly contains only staged pages and removes empty groups."""
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


def merge_preserved_pages_into_tree(
    tree: List[Dict[str, Any]],
    preserved_entries: Dict[str, Dict[str, Any]],
) -> None:
    """Ensure preserved unindexed pages are cleanly mounted in the sidebar navigation tree."""
    existing_slugs = set(extract_sidebar_leaf_slugs(tree))

    for rel_path, entry in preserved_entries.items():
        starlight_slug = rel_path[:-3] if rel_path.endswith(".md") else rel_path
        if starlight_slug in existing_slugs:
            continue

        label = entry.get("label", format_slug_as_title(entry.get("slug", starlight_slug)))
        raw_cat = entry.get("category_path") or [entry.get("section") or "Get Started"]
        cat_path = tuple(canonicalize_category_name(c) for c in raw_cat)
        doc_page = DocPage(
            section=canonicalize_category_name(entry.get("section", "Get Started")),
            slug=entry.get("slug", starlight_slug),
            url=entry.get("url", ""),
            rel_path=rel_path,
            label=label,
            category_path=cat_path,
        )
        attach_page_to_sidebar_tree(tree, doc_page, starlight_slug)


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


def atomic_write_text(path: Path, content: str, encoding: str = "utf-8") -> None:
    """Write text atomically via temporary file in target directory and replace."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.parent / f".tmp_{path.name}_{os.getpid()}_{time.time_ns()}"
    try:
        temp_path.write_text(content, encoding=encoding)
        temp_path.replace(path)
    except Exception:
        if temp_path.exists():
            try:
                temp_path.unlink()
            except Exception:
                pass
        raise


def manifests_and_content_identical(
    existing_manifest: Dict[str, Any],
    staged_files: Dict[str, Any],
    existing_sidebar_path: Path,
    new_sidebar_tree: List[Dict[str, Any]],
    existing_summary_path: Path,
    new_summary_content: str,
    staged_writes: Dict[Path, str],
    removed_paths: List[str],
    any_source_degraded: bool,
) -> bool:
    """Check if the synchronization result is completely identical to current disk state (Zero-Noise Diff)."""
    if staged_writes or removed_paths:
        return False
    if existing_manifest.get("is_degraded") != any_source_degraded:
        return False

    # Check sidebar file
    if not existing_sidebar_path.exists():
        return False
    try:
        existing_sidebar = json.loads(existing_sidebar_path.read_text(encoding="utf-8"))
        if existing_sidebar != new_sidebar_tree:
            return False
    except Exception:
        return False

    # Check SUMMARY.md
    if not existing_summary_path.exists():
        return False
    try:
        existing_summary = existing_summary_path.read_text(encoding="utf-8")
        if existing_summary != new_summary_content:
            return False
    except Exception:
        return False

    # Check files mapping
    existing_files = existing_manifest.get("files", {})
    if set(existing_files.keys()) != set(staged_files.keys()):
        return False

    # Check all versioned repository fields
    for k, new_entry in staged_files.items():
        old_entry = existing_files.get(k, {})
        for field in [
            "source", "section", "category_path", "slug", "label",
            "url", "sha256", "bytes", "sidebar_label", "badge",
        ]:
            if new_entry.get(field) != old_entry.get(field):
                return False

    return True


def commit_transaction(
    docs_root: Path,
    staged_writes: Dict[Path, str],
    removed_paths: List[str],
    sidebar_path: Path,
    combined_sidebar_tree: List[Dict[str, Any]],
    summary_path: Path,
    summary_content: str,
    manifest_path: Path,
    manifest: Dict[str, Any],
) -> None:
    """Commit changes with pre-flight backup snapshot and error rollback (application-level snapshot rollback)."""
    tx_id = uuid.uuid4().hex[:8]
    backup_dir = docs_root.parent / f".rollback_{tx_id}"
    backup_dir.mkdir(parents=True, exist_ok=True)

    backups: Dict[Path, Path] = {}
    newly_created: List[Path] = []

    try:
        # 1. Backup files that will be overwritten or removed
        for dest in staged_writes.keys():
            if dest.exists():
                rel = dest.relative_to(docs_root)
                b_path = backup_dir / rel
                b_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(dest, b_path)
                backups[dest] = b_path
            else:
                newly_created.append(dest)

        for rem_rel in removed_paths:
            rem_dest = docs_root / rem_rel
            if rem_dest.exists():
                b_path = backup_dir / rem_rel
                b_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(rem_dest, b_path)
                backups[rem_dest] = b_path

        for meta_file in [sidebar_path, summary_path, manifest_path]:
            if meta_file.exists():
                rel = meta_file.name
                b_path = backup_dir / rel
                shutil.copy2(meta_file, b_path)
                backups[meta_file] = b_path
            else:
                newly_created.append(meta_file)

        # 2. Write updated markdown files atomically
        for dest_path, content in staged_writes.items():
            atomic_write_text(dest_path, content, encoding="utf-8")

        # 3. Process deletions
        for removed in removed_paths:
            file_path = docs_root / removed
            if file_path.exists():
                file_path.unlink()
                remove_empty_dirs(file_path.parent, docs_root)

        # 4. Write sidebar & SUMMARY atomically
        if combined_sidebar_tree:
            atomic_write_text(
                sidebar_path,
                json.dumps(combined_sidebar_tree, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            atomic_write_text(summary_path, summary_content, encoding="utf-8")

        # 5. Write manifest atomically
        atomic_write_text(
            manifest_path,
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

        # Commit succeeded: cleanup backup directory
        shutil.rmtree(backup_dir, ignore_errors=True)

    except Exception as exc:
        print(f"[ERROR] Transaction failed during commit phase ({exc}); initiating rollback.")
        rollback_errors = []

        # Rollback: restore all backups
        for target, b_path in backups.items():
            if b_path.exists():
                try:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(b_path, target)
                except Exception as r_exc:
                    rollback_errors.append(f"Failed to restore {target}: {r_exc}")

        # Rollback: remove newly created files
        for created in newly_created:
            if created.exists():
                try:
                    created.unlink()
                except Exception as r_exc:
                    rollback_errors.append(f"Failed to clean new file {created}: {r_exc}")

        shutil.rmtree(backup_dir, ignore_errors=True)

        if rollback_errors:
            error_details = "; ".join(rollback_errors)
            raise RuntimeError(f"Commit transaction failed ({exc}) AND rollback encountered errors: {error_details}") from exc

        raise RuntimeError(f"Commit transaction failed ({exc}); pre-transaction state was restored.") from exc


def sync_docs(
    config_path: Path = CONFIG_PATH,
    docs_root: Path = DOCS_ROOT,
    manifest_path: Path = MANIFEST_PATH,
    sidebar_path: Path = STARLIGHT_SIDEBAR_PATH,
    summary_path: Path = SUMMARY_PATH,
    strict_fetch: bool = False,
    fetch_text_fn: Callable[[str], Tuple[str, str | None]] = fetch_text,
) -> Tuple[int, Dict[str, Any]]:
    """Execute complete doc synchronization with atomic staging, closed-loop invariant validation, and zero-noise diffs."""
    docs_root.mkdir(parents=True, exist_ok=True)
    sources = load_sources(config_path)

    # Fail closed on corrupted manifest
    try:
        existing_manifest = load_existing_manifest(manifest_path)
    except Exception as exc:
        print(f"[ERROR] Sync aborted due to unreadable manifest: {exc}")
        return 1, {"error": "corrupted_manifest", "details": str(exc)}

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
        print(f"[INFO] Source={source.source_id} total_target_pages={len(discovery.pages)} degraded={discovery.is_degraded}")
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
                time.sleep(0.01)
            except Exception as exc:  # noqa: BLE001
                print(f"[WARN] failed url={page.url} err={exc}")
                failed_pages.append((page.url, str(exc)))

                # Defensive hybrid preservation:
                # 1. Inherit content hashes from existing on-disk file (sha256, bytes, fetched_at)
                # 2. Update structural taxonomy from current DiscoveryResult (section, category_path, sidebar_label, badge, url)
                # 3. Omit ephemeral error strings from versioned repository manifest
                if manifest_key in existing_files and dest.exists():
                    print(f"[INFO] Retaining existing local copy for failed page: {manifest_key}")
                    old_entry = existing_files[manifest_key]
                    preserved_entry: Dict[str, Any] = {
                        "source": source.source_id,
                        "section": page.section,
                        "category_path": list(page.category_path),
                        "slug": page.slug,
                        "label": old_entry.get("label", page.label),
                        "url": page.url,
                        "sha256": old_entry.get("sha256", ""),
                        "bytes": old_entry.get("bytes", 0),
                        "fetched_at": old_entry.get("fetched_at", fetch_started_at),
                    }
                    if page.sidebar_label:
                        preserved_entry["sidebar_label"] = page.sidebar_label
                    if page.badge:
                        preserved_entry["badge"] = page.badge

                    staged_files[manifest_key] = preserved_entry

    if failed_pages and strict_fetch:
        print(f"[ERROR] STRICT_FETCH=1 and {len(failed_pages)} failures detected; aborting without disk mutations.")
        return 1, {"error": "strict_fetch_failures", "failed": failed_pages}

    if len(staged_files) == 0 and total_pages > 0:
        print("[ERROR] Zero documents fetched or staged; aborting sync.")
        return 1, {"error": "zero_staged_pages"}

    # Deletion Integrity Check (Mass-Drop & Degraded Guard)
    allow_deletions, deletion_ineligibility_reason = check_deletion_integrity(
        discovered_target_keys, existing_files, any_source_degraded
    )

    if not allow_deletions and strict_fetch and (set(existing_files.keys()) - discovered_target_keys):
        print(f"[ERROR] STRICT_FETCH=1 and deletion integrity verification failed: {deletion_ineligibility_reason}")
        return 1, {"error": "deletion_integrity_failed", "reason": deletion_ineligibility_reason}

    previous_paths = set(existing_files.keys())
    removed_paths: List[str] = []
    if not allow_deletions:
        print(f"[WARN] {deletion_ineligibility_reason}; retaining existing unindexed files.")
        unindexed_entries = {}
        for prev_key in sorted(previous_paths - discovered_target_keys):
            if prev_key in existing_files:
                staged_files[prev_key] = existing_files[prev_key]
                unindexed_entries[prev_key] = existing_files[prev_key]
        merge_preserved_pages_into_tree(combined_sidebar_tree, unindexed_entries)
    else:
        removed_paths = sorted(previous_paths - discovered_target_keys)

    # Apply title updates from Markdown
    update_tree_labels_with_content(combined_sidebar_tree, h1_titles)

    # Prune tree to staged slugs (eliminates unstageable failed items)
    staged_slugs_set = {k[:-3] for k in staged_files.keys() if k.endswith(".md")}
    combined_sidebar_tree = prune_tree_to_staged(combined_sidebar_tree, staged_slugs_set)
    summary_content = generate_summary_md(combined_sidebar_tree) if combined_sidebar_tree else ""

    # Strict Invariant Verification:
    # 1. Sidebar Leaves == SUMMARY Links == Staged Files
    # 2. Sidebar Breadcrumbs == Manifest category_path across every individual document
    sidebar_slugs = extract_sidebar_leaf_slugs(combined_sidebar_tree)
    summary_slugs = extract_summary_links(summary_content)
    staged_slugs = sorted(list(staged_slugs_set))
    sidebar_breadcrumbs = extract_sidebar_breadcrumbs(combined_sidebar_tree)

    invariant_errors: List[str] = []
    if sidebar_slugs != staged_slugs:
        diff_sm = set(sidebar_slugs) ^ set(staged_slugs)
        invariant_errors.append(f"Sidebar slugs mismatch with Staged files: diff={diff_sm}")
    if summary_slugs != staged_slugs:
        diff_sum = set(summary_slugs) ^ set(staged_slugs)
        invariant_errors.append(f"SUMMARY.md links mismatch with Staged files: diff={diff_sum}")

    # Verify per-page hierarchical category path consistency
    for manifest_key, entry in staged_files.items():
        starlight_slug = manifest_key[:-3] if manifest_key.endswith(".md") else manifest_key
        sb_breadcrumb = sidebar_breadcrumbs.get(starlight_slug)
        entry_cat_path = tuple(canonicalize_category_name(c) for c in entry.get("category_path", []))
        if sb_breadcrumb is not None:
            if sb_breadcrumb != entry_cat_path and sb_breadcrumb != ():
                invariant_errors.append(
                    f"Hierarchy mismatch for {starlight_slug}: Sidebar breadcrumb {sb_breadcrumb} != Manifest category_path {entry_cat_path}"
                )

    if invariant_errors:
        for err in invariant_errors:
            print(f"[ERROR] Invariant violated: {err}")
        print("[ERROR] Aborting sync to prevent committing inconsistent artifacts.")
        return 1, {"error": "invariant_violation", "details": invariant_errors}

    # Zero-Noise Diff Evaluation
    is_identical = manifests_and_content_identical(
        existing_manifest=existing_manifest,
        staged_files=staged_files,
        existing_sidebar_path=sidebar_path,
        new_sidebar_tree=combined_sidebar_tree,
        existing_summary_path=summary_path,
        new_summary_content=summary_content,
        staged_writes=staged_writes,
        removed_paths=removed_paths,
        any_source_degraded=any_source_degraded,
    )

    if is_identical:
        print("[INFO] Zero content or navigation changes detected; skipping disk writes (Zero-Noise Diff preserved).")
        manifest = dict(existing_manifest)
        manifest["stats"]["invariants_passed"] = True
        return 0, manifest

    # Changes detected: construct clean versioned repository manifest
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
            "synced_pages": len(staged_files),
            "removed_files": len(removed_paths),
            "invariants_passed": True,
        },
        "files": {k: staged_files[k] for k in sorted(staged_files.keys())},
    }

    # --- REPO-LEVEL TRANSACTIONAL COMMIT ---
    commit_transaction(
        docs_root=docs_root,
        staged_writes=staged_writes,
        removed_paths=removed_paths,
        sidebar_path=sidebar_path,
        combined_sidebar_tree=combined_sidebar_tree,
        summary_path=summary_path,
        summary_content=summary_content,
        manifest_path=manifest_path,
        manifest=manifest,
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
