#!/usr/bin/env python3
import json
import os
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from fetch_cursor_docs import (
    Source,
    DocPage,
    docs_slug_from_url,
    safe_rel_path,
    format_slug_as_title,
    canonicalize_category_name,
    extract_title_from_markdown,
    parse_llms_txt,
    parse_sidebar_from_html,
    discover_all_doc_pages,
    generate_summary_md,
    extract_sidebar_leaf_slugs,
    extract_sidebar_breadcrumbs,
    extract_summary_links,
    prune_tree_to_staged,
    merge_preserved_pages_into_tree,
    atomic_write_text,
    commit_transaction,
    sha256_text,
    sync_docs,
)


class TestFetchCursorDocsPure(unittest.TestCase):
    def setUp(self):
        self.source = Source(
            source_id="cursor",
            site_root="https://cursor.com",
            llms_path="/llms.txt",
            docs_path_prefix="/docs/",
            output_subdir="cursor",
        )

    def test_category_canonicalization(self):
        self.assertEqual(canonicalize_category_name("cloud-agents"), "Cloud Agents")
        self.assertEqual(canonicalize_category_name("Cloud Agents"), "Cloud Agents")
        self.assertEqual(canonicalize_category_name("CLI Documentation"), "CLI")
        self.assertEqual(canonicalize_category_name("cli"), "CLI")
        self.assertEqual(canonicalize_category_name("Teams & Enterprise"), "Account")
        self.assertEqual(canonicalize_category_name("Getting Started"), "Get Started")
        self.assertEqual(canonicalize_category_name("origin"), "Origin")

    def test_docs_slug_from_url(self):
        self.assertEqual(docs_slug_from_url("/docs/get-started/quickstart", self.source), "get-started/quickstart")
        self.assertEqual(docs_slug_from_url("/docs/get-started/quickstart.md", self.source), "get-started/quickstart")
        self.assertEqual(docs_slug_from_url("https://cursor.com/docs/agent/overview.md", self.source), "agent/overview")
        self.assertEqual(docs_slug_from_url("https://cursor.com/docs.md", self.source), "overview")
        self.assertEqual(docs_slug_from_url("https://cursor.com/docs", self.source), "overview")
        self.assertEqual(docs_slug_from_url("https://cursor.com/docs/home", self.source), "overview")
        self.assertEqual(docs_slug_from_url("https://cursor.com/help/getting-started/install.md", self.source), "help/getting-started/install")
        self.assertEqual(docs_slug_from_url("https://cursor.comhttps://cursor.com/docs/cli/changelog.md", self.source), "cli/changelog")

    def test_url_whitelisting_rejects_site_and_marketing_paths(self):
        self.assertIsNone(docs_slug_from_url("https://cursor.com/api", self.source))
        self.assertIsNone(docs_slug_from_url("https://cursor.com/pricing", self.source))
        self.assertIsNone(docs_slug_from_url("https://cursor.com/blog", self.source))
        self.assertIsNone(docs_slug_from_url("https://cursor.com/learn", self.source))
        self.assertIsNone(docs_slug_from_url("https://cursor.com/changelog", self.source))
        self.assertIsNone(docs_slug_from_url("https://cursor.com/changelog.md", self.source))
        self.assertIsNone(docs_slug_from_url("https://cursor.com/download", self.source))
        self.assertIsNone(docs_slug_from_url("https://cursor.com/login", self.source))
        self.assertIsNone(docs_slug_from_url("https://github.com/cursor", self.source))
        self.assertIsNone(docs_slug_from_url("/docs/../etc/passwd", self.source))

    def test_safe_rel_path(self):
        self.assertEqual(safe_rel_path("agent/overview"), "agent/overview.md")
        self.assertEqual(safe_rel_path("overview"), "overview.md")
        self.assertEqual(safe_rel_path("help/getting-started/install"), "help/getting-started/install.md")
        with self.assertRaises(RuntimeError):
            safe_rel_path("../secret")

    def test_format_slug_as_title(self):
        self.assertEqual(format_slug_as_title("mcp"), "MCP")
        self.assertEqual(format_slug_as_title("cli/overview"), "Overview")
        self.assertEqual(format_slug_as_title("claude-sonnet-5"), "Claude Sonnet 5")
        self.assertEqual(format_slug_as_title("api-keys"), "API Keys")
        self.assertEqual(format_slug_as_title("scim"), "SCIM")

    def test_extract_title_from_markdown(self):
        md1 = "# Quickstart Guide\n\nThis guide gets you started."
        self.assertEqual(extract_title_from_markdown(md1), "Quickstart Guide")

        md2 = "---\ntitle: 'Advanced Agent'\n---\n\nBody content"
        self.assertEqual(extract_title_from_markdown(md2), "Advanced Agent")

        md3 = "# [Documentation](https://cursor.com) Home\n\nWelcome."
        self.assertEqual(extract_title_from_markdown(md3), "Documentation Home")

        md4 = "No header line\nJust regular text"
        self.assertIsNone(extract_title_from_markdown(md4))

    def test_parse_llms_txt_hierarchy(self):
        sample_llms = """# Cursor Documentation

## Get Started

- https://cursor.com/docs.md
- https://cursor.com/docs/get-started/quickstart.md
- https://cursor.com/docs/models-and-pricing.md
  - https://cursor.com/docs/models/claude-sonnet-5.md

## Agent

- https://cursor.com/docs/agent/overview.md
- [Custom Plan Mode](https://cursor.com/docs/agent/plan-mode.md)

# CLI Documentation

## Get Started

- https://cursor.com/docs/cli/overview.md

## Internationalization

- Spanish: `https://cursor.com/es/docs/bugbot.md`
"""
        sidebar_tree, doc_pages = parse_llms_txt(sample_llms, self.source)

        self.assertIn("overview", doc_pages)
        self.assertIn("get-started/quickstart", doc_pages)
        self.assertIn("models/claude-sonnet-5", doc_pages)
        self.assertIn("agent/overview", doc_pages)
        self.assertIn("agent/plan-mode", doc_pages)
        self.assertEqual(doc_pages["agent/plan-mode"].label, "Custom Plan Mode")
        self.assertIn("cli/overview", doc_pages)

        self.assertNotIn("es/docs/bugbot", doc_pages)

        summary_md = generate_summary_md(sidebar_tree)
        self.assertIn("- [Overview](cursor/overview.md)", summary_md)
        self.assertIn("- [Quickstart](cursor/get-started/quickstart.md)", summary_md)

        sidebar_slugs = extract_sidebar_leaf_slugs(sidebar_tree)
        summary_slugs = extract_summary_links(summary_md)
        self.assertEqual(sidebar_slugs, summary_slugs)

    def test_parse_sidebar_from_html_semantic_details_and_badges(self):
        sample_html = """
        <nav aria-label="Documentation Sidebar">
          <details open>
            <summary>Getting Started <span class="badge badge-success">New</span></summary>
            <div>
              <a href="/docs">Overview</a>
              <a href="/docs/get-started/quickstart">Quickstart <span class="tag-pill">Beta</span></a>
            </div>
          </details>
          <details>
            <summary>Advanced Features</summary>
            <details>
              <summary>Agent Modes</summary>
              <a href="/docs/agent/plan-mode">Plan Mode</a>
            </details>
          </details>
        </nav>
        """
        sidebar_tree, doc_pages = parse_sidebar_from_html(sample_html, self.source)

        self.assertEqual(len(sidebar_tree), 2)
        self.assertEqual(sidebar_tree[0]["label"], "Get Started")
        self.assertFalse(sidebar_tree[0]["collapsed"])
        self.assertEqual(sidebar_tree[0].get("badge"), {"text": "New", "variant": "success"})

        self.assertIn("get-started/quickstart", doc_pages)
        self.assertEqual(doc_pages["get-started/quickstart"].badge, {"text": "Beta", "variant": "note"})

        self.assertEqual(sidebar_tree[1]["label"], "Advanced Features")
        self.assertTrue(sidebar_tree[1]["collapsed"])
        self.assertEqual(sidebar_tree[1]["items"][0]["label"], "Agent Modes")

    def test_real_sidebar_dom_structure_boundary_and_canonicalization(self):
        sample_html = """
        <div class="flex-1 overflow-y-auto p-6">
          <div class="space-y-8">
            <div class="space-y-1">
              <h2 class="text-[12px] text-muted-foreground tracking-wider whitespace-nowrap">Get Started</h2>
              <div class="space-y-0">
                <a href="/docs">Welcome</a>
                <a href="/docs/get-started/quickstart">Quickstart</a>
              </div>
            </div>
            <div class="space-y-1">
              <h2 class="text-[12px] text-muted-foreground tracking-wider whitespace-nowrap">Agent</h2>
              <div class="space-y-0">
                <a href="/docs/agent/overview">Overview</a>
                <a href="/docs/agent/agents-window">Agents Window</a>
              </div>
            </div>
            <div class="space-y-1">
              <h2 class="text-[12px] text-muted-foreground tracking-wider whitespace-nowrap">Teams & Enterprise</h2>
              <div class="space-y-0">
                <a href="/docs/account/teams/setup">Setup</a>
              </div>
            </div>
          </div>
        </div>
        """
        sidebar_tree, doc_pages = parse_sidebar_from_html(sample_html, self.source)

        self.assertEqual(doc_pages["overview"].category_path, ("Get Started",))
        self.assertEqual(doc_pages["get-started/quickstart"].category_path, ("Get Started",))
        self.assertNotIn("Models & Pricing", doc_pages["overview"].category_path)
        self.assertNotIn("Models & Pricing", doc_pages["get-started/quickstart"].category_path)

        self.assertEqual(doc_pages["agent/overview"].category_path, ("Agent",))
        self.assertNotIn("Tools", doc_pages["agent/overview"].category_path)

        self.assertEqual(doc_pages["account/teams/setup"].category_path, ("Account",))

        # Check breadcrumbs extraction
        breadcrumbs = extract_sidebar_breadcrumbs(sidebar_tree)
        self.assertEqual(breadcrumbs["cursor/overview"], ("Get Started",))
        self.assertEqual(breadcrumbs["cursor/agent/overview"], ("Agent",))

    def test_sidebar_container_structural_scoring_rejects_site_header(self):
        sample_html = """
        <header>
          <nav aria-label="Main site navigation">
            <a href="/pricing">Pricing</a>
            <a href="/blog">Blog</a>
            <a href="/api">API</a>
            <a href="/docs">Docs</a>
            <a href="/login">Login</a>
          </nav>
        </header>
        <aside class="docs-sidebar overflow-y-auto">
          <nav aria-label="Documentation Sidebar">
            <div>
              <h2>Account</h2>
              <a href="/docs/account/sso">SSO</a>
              <a href="/docs/account/scim">SCIM</a>
            </div>
            <div>
              <h2>Agent</h2>
              <a href="/docs/agent/overview">Agent Overview</a>
            </div>
          </nav>
        </aside>
        """
        sidebar_tree, doc_pages = parse_sidebar_from_html(sample_html, self.source)

        self.assertNotIn("pricing", doc_pages)
        self.assertNotIn("blog", doc_pages)
        self.assertNotIn("api", doc_pages)

        self.assertIn("account/sso", doc_pages)
        self.assertIn("account/scim", doc_pages)
        self.assertIn("agent/overview", doc_pages)

    def test_prune_tree_to_staged(self):
        tree = [
            {
                "label": "Group 1",
                "items": [
                    {"label": "Page A", "slug": "cursor/page-a"},
                    {"label": "Page B", "slug": "cursor/page-b"},
                ],
            },
            {
                "label": "Group 2",
                "items": [
                    {"label": "Page C", "slug": "cursor/page-c"},
                ],
            },
        ]
        pruned = prune_tree_to_staged(tree, {"cursor/page-a"})
        self.assertEqual(len(pruned), 1)
        self.assertEqual(pruned[0]["label"], "Group 1")
        self.assertEqual(len(pruned[0]["items"]), 1)
        self.assertEqual(pruned[0]["items"][0]["slug"], "cursor/page-a")

    def test_merge_preserved_pages_into_tree(self):
        tree = [
            {
                "label": "Account",
                "items": [{"label": "Teams", "slug": "cursor/account/teams"}],
            }
        ]
        preserved = {
            "cursor/account/billing.md": {
                "section": "Account",
                "label": "Billing",
                "slug": "account/billing",
                "category_path": ["Account"],
            },
            "cursor/other/orphan.md": {
                "section": "Other",
                "label": "Orphan Doc",
                "slug": "other/orphan",
                "category_path": ["Other"],
            },
        }
        merge_preserved_pages_into_tree(tree, preserved)
        self.assertEqual(len(tree), 2)
        self.assertEqual(len(tree[0]["items"]), 2)
        self.assertEqual(tree[0]["items"][1]["slug"], "cursor/account/billing")
        self.assertEqual(tree[1]["label"], "Other")
        self.assertEqual(tree[1]["items"][0]["slug"], "cursor/other/orphan")

    def test_atomic_write_text(self):
        with TemporaryDirectory() as tmp_dir:
            target = Path(tmp_dir) / "sub" / "test.txt"
            atomic_write_text(target, "Hello World")
            self.assertTrue(target.exists())
            self.assertEqual(target.read_text(encoding="utf-8"), "Hello World")


class TestDualSourceDiscovery(unittest.TestCase):
    def setUp(self):
        self.source = Source(
            source_id="cursor",
            site_root="https://cursor.test",
            llms_path="/llms.txt",
            docs_path_prefix="/docs/",
            output_subdir="cursor",
        )

    def test_dual_source_hierarchical_category_path_mounting(self):
        html_content = """
        <nav aria-label="Documentation Sidebar">
          <div>
            <h2>Get Started</h2>
            <a href="/docs">Overview</a>
            <a href="/docs/get-started/quickstart">Quickstart</a>
          </div>
          <div>
            <h2>CLI</h2>
            <a href="/docs/cli/overview">Overview</a>
          </div>
        </nav>
        """
        llms_content = """# Cursor Documentation
## Get Started
- https://cursor.test/docs.md
- https://cursor.test/docs/get-started/quickstart.md

# CLI Documentation
## Get Started
- https://cursor.test/docs/cli/installation.md

# cloud-agents
## Overview
- https://cursor.test/docs/cloud-agents/overview.md
"""
        def mock_fetch(url: str):
            if "docs" in url and "llms.txt" not in url and ".md" not in url:
                return html_content, "text/html"
            if "llms.txt" in url:
                return llms_content, "text/plain"
            raise RuntimeError(f"Unexpected {url}")

        discovery = discover_all_doc_pages(self.source, fetch_text_fn=mock_fetch)
        self.assertFalse(discovery.is_degraded)
        slugs = [p.slug for p in discovery.pages]
        self.assertIn("overview", slugs)
        self.assertIn("get-started/quickstart", slugs)
        self.assertIn("cli/installation", slugs)
        self.assertIn("cloud-agents/overview", slugs)

        top_labels = [g.get("label") for g in discovery.sidebar_tree]
        self.assertIn("CLI", top_labels)
        self.assertNotIn("CLI Documentation", top_labels)
        self.assertIn("Cloud Agents", top_labels)
        self.assertNotIn("cloud-agents", top_labels)

    def test_html_failure_degrades_to_llms(self):
        llms_content = """# Cursor Documentation
## Get Started
- https://cursor.test/docs.md
- https://cursor.test/docs/quickstart.md
"""
        def mock_fetch(url: str):
            if "llms.txt" in url:
                return llms_content, "text/plain"
            raise RuntimeError("HTML endpoint down 500")

        discovery = discover_all_doc_pages(self.source, fetch_text_fn=mock_fetch)
        self.assertTrue(discovery.is_degraded)
        self.assertEqual(len(discovery.pages), 2)

    def test_llms_failure_degrades_to_html(self):
        html_content = """
        <nav aria-label="Docs Sidebar">
          <div>
            <h2>Get Started</h2>
            <a href="/docs">Overview</a>
            <a href="/docs/quickstart">Quickstart</a>
          </div>
        </nav>
        """
        def mock_fetch(url: str):
            if "llms.txt" in url:
                raise RuntimeError("llms.txt 404")
            return html_content, "text/html"

        discovery = discover_all_doc_pages(self.source, fetch_text_fn=mock_fetch)
        self.assertTrue(discovery.is_degraded)
        self.assertEqual(len(discovery.pages), 2)


class TestSyncIntegration(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.tmp_path = Path(self.tmp.name)
        self.docs_dir = self.tmp_path / "docs"
        self.docs_dir.mkdir(parents=True)
        self.config_file = self.tmp_path / "sources.json"
        self.config_data = {
            "sources": [
                {
                    "id": "cursor",
                    "site_root": "https://cursor.test",
                    "llms_path": "/llms.txt",
                    "docs_path_prefix": "/docs/",
                    "output_subdir": "cursor",
                }
            ]
        }
        self.config_file.write_text(json.dumps(self.config_data), encoding="utf-8")
        self.manifest_file = self.docs_dir / "docs_manifest.json"
        self.sidebar_file = self.docs_dir / "starlight_sidebar.json"
        self.summary_file = self.docs_dir / "SUMMARY.md"

    def tearDown(self):
        self.tmp.cleanup()

    def test_sync_docs_success(self):
        llms_content = """# Cursor Documentation
## Get Started
- https://cursor.test/docs.md
- https://cursor.test/docs/get-started/quickstart.md
"""

        def mock_fetch(url: str):
            if "llms.txt" in url:
                return llms_content, "text/plain"
            if "docs.md" in url:
                return "# Cursor Documentation\nWelcome to Cursor.", "text/markdown"
            if "quickstart.md" in url:
                return "# Quickstart\nGet started in 5 minutes.", "text/markdown"
            if url == "https://cursor.test/docs":
                return "<nav aria-label='Docs Sidebar'><div><h2>Get Started</h2><a href='/docs'>Overview</a><a href='/docs/get-started/quickstart'>Quickstart</a></div></nav>", "text/html"
            raise RuntimeError(f"Unexpected url {url}")

        code, manifest = sync_docs(
            config_path=self.config_file,
            docs_root=self.docs_dir,
            manifest_path=self.manifest_file,
            sidebar_path=self.sidebar_file,
            summary_path=self.summary_file,
            strict_fetch=True,
            fetch_text_fn=mock_fetch,
        )

        self.assertEqual(code, 0)
        self.assertEqual(manifest["stats"]["synced_pages"], 2)
        self.assertTrue((self.docs_dir / "cursor" / "overview.md").exists())
        self.assertTrue((self.docs_dir / "cursor" / "get-started" / "quickstart.md").exists())
        self.assertTrue(self.sidebar_file.exists())
        self.assertTrue(self.summary_file.exists())
        self.assertTrue(manifest["stats"]["invariants_passed"])

    def test_corrupted_manifest_fails_closed_zero_writes(self):
        self.manifest_file.write_text("{ corrupted json invalid ", encoding="utf-8")

        def mock_fetch(url: str):
            return "# Should Not Be Fetched", "text/markdown"

        code, res = sync_docs(
            config_path=self.config_file,
            docs_root=self.docs_dir,
            manifest_path=self.manifest_file,
            sidebar_path=self.sidebar_file,
            summary_path=self.summary_file,
            strict_fetch=False,
            fetch_text_fn=mock_fetch,
        )

        self.assertEqual(code, 1)
        self.assertEqual(res["error"], "corrupted_manifest")
        self.assertFalse((self.docs_dir / "cursor").exists())

    def test_failed_download_updates_taxonomy_from_discovery_while_preserving_body_hash(self):
        source_dir = self.docs_dir / "cursor"
        source_dir.mkdir(parents=True, exist_ok=True)
        quickstart_path = source_dir / "get-started" / "quickstart.md"
        quickstart_path.parent.mkdir(parents=True, exist_ok=True)
        quickstart_path.write_text("# Quickstart Original Content", encoding="utf-8")

        initial_manifest = {
            "generated_at": "2026-08-01T00:00:00Z",
            "is_degraded": False,
            "stats": {"invariants_passed": True},
            "files": {
                "cursor/get-started/quickstart.md": {
                    "source": "cursor",
                    "section": "Old Stale Section",
                    "category_path": ["Get Started", "Models & Pricing"],  # Old buggy path
                    "slug": "get-started/quickstart",
                    "label": "Quickstart",
                    "url": "https://cursor.test/docs/get-started/quickstart.md",
                    "sha256": sha256_text("# Quickstart Original Content"),
                    "bytes": len("# Quickstart Original Content"),
                    "fetched_at": "2026-08-01T00:00:00Z",
                }
            },
        }
        self.manifest_file.write_text(json.dumps(initial_manifest), encoding="utf-8")

        html_content = """
        <div class="flex-1 overflow-y-auto p-6">
          <div>
            <h2>Get Started</h2>
            <a href="/docs/get-started/quickstart">Quickstart</a>
          </div>
        </div>
        """
        llms_content = """# Cursor Documentation
## Get Started
- https://cursor.test/docs/get-started/quickstart.md
"""

        def mock_fetch(url: str):
            if "llms.txt" in url:
                return llms_content, "text/plain"
            if url == "https://cursor.test/docs":
                return html_content, "text/html"
            if "quickstart.md" in url:
                raise RuntimeError("504 Gateway Timeout")
            raise RuntimeError(f"Unexpected url {url}")

        code, manifest = sync_docs(
            config_path=self.config_file,
            docs_root=self.docs_dir,
            manifest_path=self.manifest_file,
            sidebar_path=self.sidebar_file,
            summary_path=self.summary_file,
            strict_fetch=False,
            fetch_text_fn=mock_fetch,
        )

        self.assertEqual(code, 0)
        entry = manifest["files"]["cursor/get-started/quickstart.md"]
        # Structural metadata is updated from current DiscoveryResult
        self.assertEqual(entry["category_path"], ["Get Started"])
        self.assertEqual(entry["section"], "Get Started")
        # Body metadata is safely preserved from existing file
        self.assertEqual(entry["sha256"], sha256_text("# Quickstart Original Content"))
        self.assertEqual(entry["fetched_at"], "2026-08-01T00:00:00Z")
        self.assertNotIn("last_fetch_status", entry)
        self.assertNotIn("last_fetch_error", entry)

        # Hierarchy invariant holds
        sidebar_data = json.loads(self.sidebar_file.read_text(encoding="utf-8"))
        breadcrumbs = extract_sidebar_breadcrumbs(sidebar_data)
        self.assertEqual(breadcrumbs["cursor/get-started/quickstart"], ("Get Started",))

    def test_unstageable_download_failure_is_pruned_and_invariants_hold(self):
        llms_content = """# Cursor Documentation
## Get Started
- https://cursor.test/docs.md
- https://cursor.test/docs/doc2.md
"""

        def mock_fetch(url: str):
            if "llms.txt" in url:
                return llms_content, "text/plain"
            if "docs.md" in url:
                return "# Cursor Docs", "text/markdown"
            if "doc2.md" in url:
                raise RuntimeError("504 Gateway Timeout on new doc2")
            if url == "https://cursor.test/docs":
                return "<nav aria-label='Docs Sidebar'><a href='/docs'>Docs</a><a href='/docs/doc2'>Doc2</a></nav>", "text/html"
            raise RuntimeError(f"Unexpected {url}")

        code, res = sync_docs(
            config_path=self.config_file,
            docs_root=self.docs_dir,
            manifest_path=self.manifest_file,
            sidebar_path=self.sidebar_file,
            summary_path=self.summary_file,
            strict_fetch=False,
            fetch_text_fn=mock_fetch,
        )

        self.assertEqual(code, 0)
        self.assertEqual(res["stats"]["synced_pages"], 1)

    def test_true_zero_noise_diff_on_consecutive_runs(self):
        llms_content = """# Cursor Documentation
## Get Started
- https://cursor.test/docs.md
- https://cursor.test/docs/quickstart.md
"""
        html_content = """<div class="flex-1 overflow-y-auto p-6"><div><h2>Get Started</h2><a href='/docs'>Overview</a><a href='/docs/quickstart'>Quickstart</a></div></div>"""

        def mock_fetch(url: str):
            if "llms.txt" in url:
                return llms_content, "text/plain"
            if "docs.md" in url:
                return "# Cursor Docs", "text/markdown"
            if "quickstart.md" in url:
                return "# Quickstart", "text/markdown"
            if url == "https://cursor.test/docs":
                return html_content, "text/html"
            raise RuntimeError(f"Unexpected url {url}")

        # First run: creates files
        code1, manifest1 = sync_docs(
            config_path=self.config_file,
            docs_root=self.docs_dir,
            manifest_path=self.manifest_file,
            sidebar_path=self.sidebar_file,
            summary_path=self.summary_file,
            strict_fetch=False,
            fetch_text_fn=mock_fetch,
        )
        self.assertEqual(code1, 0)
        orig_gen_at = manifest1["generated_at"]
        orig_manifest_content = self.manifest_file.read_text(encoding="utf-8")
        orig_manifest_mtime = self.manifest_file.stat().st_mtime_ns
        orig_sidebar_mtime = self.sidebar_file.stat().st_mtime_ns
        orig_summary_mtime = self.summary_file.stat().st_mtime_ns

        # Second run: identical content -> MUST be zero noise
        code2, manifest2 = sync_docs(
            config_path=self.config_file,
            docs_root=self.docs_dir,
            manifest_path=self.manifest_file,
            sidebar_path=self.sidebar_file,
            summary_path=self.summary_file,
            strict_fetch=False,
            fetch_text_fn=mock_fetch,
        )
        self.assertEqual(code2, 0)
        self.assertEqual(manifest2["generated_at"], orig_gen_at)
        self.assertEqual(self.manifest_file.read_text(encoding="utf-8"), orig_manifest_content)
        self.assertEqual(self.manifest_file.stat().st_mtime_ns, orig_manifest_mtime)
        self.assertEqual(self.sidebar_file.stat().st_mtime_ns, orig_sidebar_mtime)
        self.assertEqual(self.summary_file.stat().st_mtime_ns, orig_summary_mtime)

    def test_zero_noise_diff_when_transient_failure_occurs(self):
        llms_content = """# Cursor Documentation
## Get Started
- https://cursor.test/docs.md
- https://cursor.test/docs/quickstart.md
"""
        html_content = """<div class="flex-1 overflow-y-auto p-6"><div><h2>Get Started</h2><a href='/docs'>Overview</a><a href='/docs/quickstart'>Quickstart</a></div></div>"""

        def mock_fetch_success(url: str):
            if "llms.txt" in url:
                return llms_content, "text/plain"
            if "docs.md" in url:
                return "# Cursor Docs", "text/markdown"
            if "quickstart.md" in url:
                return "# Quickstart", "text/markdown"
            if url == "https://cursor.test/docs":
                return html_content, "text/html"
            raise RuntimeError(f"Unexpected url {url}")

        code1, manifest1 = sync_docs(
            config_path=self.config_file,
            docs_root=self.docs_dir,
            manifest_path=self.manifest_file,
            sidebar_path=self.sidebar_file,
            summary_path=self.summary_file,
            strict_fetch=False,
            fetch_text_fn=mock_fetch_success,
        )
        self.assertEqual(code1, 0)
        orig_gen_at = manifest1["generated_at"]
        orig_manifest_mtime = self.manifest_file.stat().st_mtime_ns

        # Second run: quickstart.md fails transiently with 504 Gateway Timeout
        def mock_fetch_transient_fail(url: str):
            if "llms.txt" in url:
                return llms_content, "text/plain"
            if "docs.md" in url:
                return "# Cursor Docs", "text/markdown"
            if "quickstart.md" in url:
                raise RuntimeError("504 Gateway Timeout")
            if url == "https://cursor.test/docs":
                return html_content, "text/html"
            raise RuntimeError(f"Unexpected url {url}")

        code2, manifest2 = sync_docs(
            config_path=self.config_file,
            docs_root=self.docs_dir,
            manifest_path=self.manifest_file,
            sidebar_path=self.sidebar_file,
            summary_path=self.summary_file,
            strict_fetch=False,
            fetch_text_fn=mock_fetch_transient_fail,
        )
        self.assertEqual(code2, 0)
        # generated_at and manifest mtime must be preserved (Zero Noise despite transient upstream error)
        self.assertEqual(manifest2["generated_at"], orig_gen_at)
        self.assertEqual(self.manifest_file.stat().st_mtime_ns, orig_manifest_mtime)

    def test_partial_discovery_blocks_mass_deletion_and_preserves_3_invariants(self):
        source_dir = self.docs_dir / "cursor"
        source_dir.mkdir(parents=True, exist_ok=True)
        initial_files = {}

        for i in range(1, 11):
            doc_name = f"doc{i}.md"
            (source_dir / doc_name).write_text(f"# Doc {i}", encoding="utf-8")
            initial_files[f"cursor/{doc_name}"] = {
                "source": "cursor",
                "section": "General",
                "category_path": ["General"],
                "slug": f"doc{i}",
                "label": f"Doc {i}",
                "url": f"https://cursor.test/docs/doc{i}.md",
                "sha256": sha256_text(f"# Doc {i}"),
                "bytes": len(f"# Doc {i}"),
                "fetched_at": "2026-08-01T00:00:00Z",
            }

        self.manifest_file.write_text(json.dumps({"files": initial_files}), encoding="utf-8")

        truncated_llms = """# Cursor Documentation
## Get Started
- https://cursor.test/docs/doc1.md
- https://cursor.test/docs/doc2.md
"""

        def mock_fetch(url: str):
            if "llms.txt" in url:
                return truncated_llms, "text/plain"
            if "doc1.md" in url:
                return "# Doc 1", "text/markdown"
            if "doc2.md" in url:
                return "# Doc 2", "text/markdown"
            if url == "https://cursor.test/docs":
                return "<nav aria-label='Docs Sidebar'><a href='/docs/doc1'>Doc 1</a><a href='/docs/doc2'>Doc 2</a></nav>", "text/html"
            raise RuntimeError(f"Unexpected url {url}")

        code, manifest = sync_docs(
            config_path=self.config_file,
            docs_root=self.docs_dir,
            manifest_path=self.manifest_file,
            sidebar_path=self.sidebar_file,
            summary_path=self.summary_file,
            strict_fetch=False,
            fetch_text_fn=mock_fetch,
        )

        self.assertEqual(code, 0)
        self.assertEqual(manifest["stats"]["removed_files"], 0)
        for i in range(1, 11):
            self.assertTrue((source_dir / f"doc{i}.md").exists())
            self.assertIn(f"cursor/doc{i}.md", manifest["files"])

        # 3-way invariant verification on disk
        sidebar_data = json.loads(self.sidebar_file.read_text(encoding="utf-8"))
        summary_data = self.summary_file.read_text(encoding="utf-8")

        sidebar_slugs = extract_sidebar_leaf_slugs(sidebar_data)
        summary_slugs = extract_summary_links(summary_data)
        manifest_slugs = sorted([k[:-3] for k in manifest["files"].keys()])

        self.assertEqual(len(sidebar_slugs), 10)
        self.assertEqual(sidebar_slugs, manifest_slugs)
        self.assertEqual(summary_slugs, manifest_slugs)

    def test_transaction_rollback_on_failure(self):
        source_dir = self.docs_dir / "cursor"
        source_dir.mkdir(parents=True, exist_ok=True)
        original_file = source_dir / "overview.md"
        original_file.write_text("# Original Content", encoding="utf-8")

        staged_writes = {original_file: "# New Content"}
        removed_paths = []

        with patch("fetch_cursor_docs.atomic_write_text") as mock_write:
            def side_effect(path, content, encoding="utf-8"):
                if "manifest" in str(path):
                    raise IOError("Simulated disk full error on manifest")
                path.write_text(content, encoding=encoding)
            mock_write.side_effect = side_effect

            with self.assertRaises(RuntimeError):
                commit_transaction(
                    docs_root=self.docs_dir,
                    staged_writes=staged_writes,
                    removed_paths=removed_paths,
                    sidebar_path=self.sidebar_file,
                    combined_sidebar_tree=[],
                    summary_path=self.summary_file,
                    summary_content="",
                    manifest_path=self.manifest_file,
                    manifest={},
                )

        self.assertEqual(original_file.read_text(encoding="utf-8"), "# Original Content")
        rollback_dirs = list(self.tmp_path.glob(".rollback_*"))
        self.assertEqual(len(rollback_dirs), 0)


if __name__ == "__main__":
    unittest.main()
