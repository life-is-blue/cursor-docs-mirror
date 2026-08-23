# Cursor Docs Mirror

Local mirror for official **Cursor** docs, including Cursor Agent, Rules, MCP, Skills, CLI, Cloud Agents, and Help Center.

## Open-Source Positioning

This repository is an open mirror of publicly available Cursor documentation,
designed to make agent-oriented document ingestion, indexing, and retrieval seamless.

- Canonical source remains the official Cursor site (`https://cursor.com/docs` and `https://cursor.com/help`).
- This mirror does not redefine or replace official documentation.
- We only mirror documentation the site itself publishes as Markdown endpoints.
- Each mirrored file preserves source metadata (`section`, `category_path`, `slug`, `label`, `url`, `sha256`, `fetched_at`) in `docs/docs_manifest.json`.

## How Discovery Works

Cursor publishes docs and markdown endpoints:

- Official docs directory lives at `/llms.txt` and HTML sidebar DOM across Docs, CLI, and Help Center.
- Raw Markdown endpoints live at `/docs/<slug>.md` and `/help/<slug>.md` (`Content-Type: text/plain` / `text/markdown`).

`scripts/fetch_cursor_docs.py` therefore:

1. Discovers the complete hierarchical documentation tree from `/llms.txt` and HTML navigation DOM,
2. Resolves slugs, category hierarchies, and extracts titles from Markdown H1/frontmatter,
3. Downloads each document staged in memory and verifies invariants (`Manifest Files == Sidebar Leaves == SUMMARY Links`),
4. Mirrors docs under `docs/<output_subdir>/<slug>.md`,
5. Generates `docs/starlight_sidebar.json` (Astro Starlight compatible sidebar configuration),
6. Generates `docs/SUMMARY.md` (GitBook / standard nested Markdown index),
7. Writes `docs/docs_manifest.json` with hashes, timestamps, and category paths.

## Using with Astro Starlight

You can directly consume the auto-generated `starlight_sidebar.json` in your Starlight config (`astro.config.mjs`):

```js
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';
import cursorSidebar from './docs/starlight_sidebar.json';

export default defineConfig({
  integrations: [
    starlight({
      title: 'Cursor Docs Mirror',
      sidebar: cursorSidebar,
    }),
  ],
});
```

## Sources

Configured in `config/sources.json`:
- `https://cursor.com` (`llms_path=/llms.txt`, markdown under `/docs/*.md` and `/help/*.md`)

## Layout

- `scripts/fetch_cursor_docs.py`: fetcher + sidebar/llms parser + manifest generator
- `config/sources.json`: source definitions
- `docs/`: mirrored markdown content
- `docs/starlight_sidebar.json`: Starlight sidebar configuration tree
- `docs/SUMMARY.md`: nested markdown index
- `docs/docs_manifest.json`: manifest with hashes and category paths
- `.cnb.yml`: CNB scheduled + manual sync workflow
- `.cnb/web_trigger.yml`: CNB page button configuration
- `.github/workflows/update-docs.yml`: GitHub Actions daily sync workflow
- `tests/test_fetch_cursor_docs.py`: comprehensive unit & integration tests

## Run Locally

```bash
pip install -r scripts/requirements.txt
python3 scripts/fetch_cursor_docs.py
```

Optional strict mode:

```bash
STRICT_FETCH=1 python3 scripts/fetch_cursor_docs.py
```

## Run Tests

```bash
python3 -m unittest discover -s tests -v
```

## Automation

This repository supports both CNB and GitHub Actions automation:

- CNB scheduled sync daily: `main -> "crontab: 0 0 * * *"`
- CNB manual sync button on `main` branch page: **Sync Cursor Docs**
- GitHub Actions scheduled sync daily: `.github/workflows/update-docs.yml`
- Push / PR validation on `main` for fetcher changes (`scripts/**`, `config/**`, `tests/**`, `.cnb.yml`, `.cnb/web_trigger.yml`)

## Notes

- Source content remains property of Anysphere, Inc. (Cursor).
- This repository stores mirrored copies to support machine-readable indexing and agent retrieval workflows.
- Official docs should always be treated as the source of truth when discrepancies appear.
