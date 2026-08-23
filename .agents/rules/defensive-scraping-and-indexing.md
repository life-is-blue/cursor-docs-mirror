---
trigger: model_decision
description: Defensive web scraping, hierarchical document ingestion, and closed-loop invariant validation.
---

# Defensive Scraping & Document Ingestion Invariants

When implementing web scraping, documentation mirroring, or multi-source tree indexers:

## 1. Strict State Modeling Separation
- Never write transient poll/fetch errors or ephemeral failure lists into versioned, git-tracked manifests.
- Versioned manifests must exclusively track persistent physical state (content hashes, canonical category paths, byte counts, and initial fetch timestamps).

## 2. Hybrid Fallback on Fetch Failures
- When a tracked document download fails but a local copy exists:
  - Preserve existing content body metadata (`sha256`, `bytes`, `fetched_at`).
  - Update structural navigation metadata (`section`, `category_path`, `sidebar_label`, `badge`, `url`) from the current discovery result.
  - Never retain outdated category paths that conflict with the newly computed sidebar topology.

## 3. Strict Breadcrumb Invariant
- Verify that every leaf node's ancestor category path in the navigation tree strictly equals the corresponding manifest entry's `category_path`.

## 4. Semantic DOM Heading Boundaries
- Demarcate section boundaries only using semantic heading elements (`<h1>`–`<h6>`) or `<details>/<summary>`. Do not allow generic interactive elements (`<button>`) to redefine parent container scopes.

## 5. Explicit Cross-Source Category Canonicalization
- Apply explicit canonicalization mappings (e.g., `cloud-agents` -> `Cloud Agents`, `CLI Documentation` -> `CLI`) before mounting complementary sources to prevent duplicate parallel trees.

## 6. Decouple PR CI Gates from Live Upstream Health
- In PR / commit validation gates, run comprehensive offline unit tests against fixed mock fixtures.
- Reserve live upstream network synchronization for scheduled/manual background jobs to avoid blocking PRs on transient third-party network issues.

## 7. Bit-for-Bit Idempotency
- Assert zero-noise diff across consecutive runs: bit-for-bit file identity, unchanged `generated_at`, and untouched file modification times, even when transient network errors are absorbed.
