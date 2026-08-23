#!/usr/bin/env python3
import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from fetch_cursor_docs import (
    Source,
    DocPage,
    docs_slug_from_url,
    safe_rel_path,
    format_slug_as_title,
    extract_title_from_markdown,
    parse_llms_txt,
    parse_sidebar_from_html,
    generate_summary_md,
    extract_sidebar_leaf_slugs,
    extract_summary_links,
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

    def test_docs_slug_from_url(self):
        self.assertEqual(docs_slug_from_url("/docs/get-started/quickstart", self.source), "get-started/quickstart")
        self.assertEqual(docs_slug_from_url("/docs/get-started/quickstart.md", self.source), "get-started/quickstart")
        self.assertEqual(docs_slug_from_url("https://cursor.com/docs/agent/overview.md", self.source), "agent/overview")
        self.assertEqual(docs_slug_from_url("https://cursor.com/docs.md", self.source), "overview")
        self.assertEqual(docs_slug_from_url("https://cursor.com/docs", self.source), "overview")
        self.assertEqual(docs_slug_from_url("https://cursor.com/docs/home", self.source), "overview")
        self.assertIsNone(docs_slug_from_url("https://cursor.com/changelog.md", self.source))
        self.assertEqual(docs_slug_from_url("https://cursor.com/help/getting-started/install.md", self.source), "help/getting-started/install")
        self.assertEqual(docs_slug_from_url("https://cursor.comhttps://cursor.com/docs/cli/changelog.md", self.source), "cli/changelog")
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
- https://cursor.com/docs/agent/plan-mode.md

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
        self.assertIn("cli/overview", doc_pages)

        # Check that internationalization was ignored
        self.assertNotIn("es/docs/bugbot", doc_pages)

        self.assertTrue(len(sidebar_tree) > 0)
        # Check summary and leaf slugs invariant
        summary_md = generate_summary_md(sidebar_tree)
        self.assertIn("- [Overview](cursor/overview.md)", summary_md)
        self.assertIn("- [Quickstart](cursor/get-started/quickstart.md)", summary_md)

        sidebar_slugs = extract_sidebar_leaf_slugs(sidebar_tree)
        summary_slugs = extract_summary_links(summary_md)
        self.assertEqual(sidebar_slugs, summary_slugs)


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
        self.assertEqual(manifest["stats"]["successful_pages"], 2)
        self.assertTrue((self.docs_dir / "cursor" / "overview.md").exists())
        self.assertTrue((self.docs_dir / "cursor" / "get-started" / "quickstart.md").exists())
        self.assertTrue(self.sidebar_file.exists())
        self.assertTrue(self.summary_file.exists())
        self.assertTrue(manifest["stats"]["invariants_passed"])

    def test_invariant_violation_aborts_commit_in_all_modes(self):
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

        self.assertEqual(code, 1)
        self.assertEqual(res["error"], "invariant_violation")
        self.assertFalse(self.sidebar_file.exists())
        self.assertFalse(self.summary_file.exists())

    def test_idempotency_keeps_original_timestamp(self):
        source_dir = self.docs_dir / "cursor"
        source_dir.mkdir(parents=True, exist_ok=True)
        (source_dir / "overview.md").write_text("# Cursor Docs", encoding="utf-8")

        initial_manifest = {
            "files": {
                "cursor/overview.md": {
                    "source": "cursor",
                    "section": "Get Started",
                    "category_path": ["Get Started"],
                    "slug": "overview",
                    "label": "Cursor Docs",
                    "url": "https://cursor.test/docs.md",
                    "sha256": sha256_text("# Cursor Docs"),
                    "bytes": len("# Cursor Docs"),
                    "fetched_at": "2026-08-01T00:00:00Z",
                }
            }
        }
        self.manifest_file.write_text(json.dumps(initial_manifest), encoding="utf-8")

        llms_content = """# Cursor Documentation
## Get Started
- https://cursor.test/docs.md
"""

        def mock_fetch(url: str):
            if "llms.txt" in url:
                return llms_content, "text/plain"
            if "docs.md" in url:
                return "# Cursor Docs", "text/markdown"
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
        self.assertEqual(manifest["files"]["cursor/overview.md"]["fetched_at"], "2026-08-01T00:00:00Z")

    def test_partial_discovery_blocks_mass_deletion(self):
        source_dir = self.docs_dir / "cursor"
        source_dir.mkdir(parents=True, exist_ok=True)
        initial_files = {}

        for i in range(1, 11):
            doc_name = f"doc{i}.md"
            (source_dir / doc_name).write_text(f"# Doc {i}", encoding="utf-8")
            initial_files[f"cursor/{doc_name}"] = {
                "source": "cursor",
                "section": "General",
                "category_path": [],
                "slug": f"doc{i}",
                "label": f"Doc {i}",
                "url": f"https://cursor.test/docs/doc{i}.md",
                "sha256": sha256_text(f"# Doc {i}"),
                "bytes": len(f"# Doc {i}"),
                "fetched_at": "2026-08-01T00:00:00Z",
            }

        self.manifest_file.write_text(json.dumps({"files": initial_files}), encoding="utf-8")

        # Truncated llms.txt returning only 1 page
        truncated_llms = """# Cursor Documentation
## Get Started
- https://cursor.test/docs/doc1.md
"""

        def mock_fetch(url: str):
            if "llms.txt" in url:
                return truncated_llms, "text/plain"
            if "doc1.md" in url:
                return "# Doc 1", "text/markdown"
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
        for i in range(2, 11):
            self.assertTrue((source_dir / f"doc{i}.md").exists())
            self.assertIn(f"cursor/doc{i}.md", manifest["files"])


if __name__ == "__main__":
    unittest.main()
