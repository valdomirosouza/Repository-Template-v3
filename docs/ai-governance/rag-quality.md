# RAG / Retrieval Quality

> **Owner:** AI Governance Lead | **Implements against:** `src/memory/{vector_store,document_indexer,bug_history_store}.py` | ADR-0017 (agent memory)

The system's retrieval-augmented path is agent **memory**: `DocumentIndexer` indexes `specs/` and
`docs/adr/` into a vector store (`PostgresVectorStore` on pgvector; `InMemoryVectorStore` for tests),
and agents retrieve relevant context (incl. past HITL rejections via `BugHistoryStore`) before acting.
This doc sets the quality bar for that path.

---

## 1. Document ingestion policy

- **Sources** are explicit (`DocumentIndexer` scans `specs/`, `docs/adr/`); never index untrusted or
  PII-bearing content. Text is **PII-masked before embedding** (`pii_filter.py`, LLM06).
- Re-index on change (CI on push to `main`, or `make memory-index`); a stale index is a known failure
  mode — see §4.

## 2. Chunking strategy

- Chunk by semantic unit (a spec section, an ADR decision) rather than fixed tokens, so a retrieved
  chunk is self-contained and citable.
- Record the chunking version with the index; a chunking change invalidates retrieval-eval baselines.

## 3. Retrieval evaluation

| Metric                | Definition                                      | Target |
| --------------------- | ----------------------------------------------- | ------ |
| Retrieval precision@k | fraction of top-k chunks actually relevant      | ↑      |
| Grounding coverage    | answer claims traceable to a retrieved chunk    | → 1.0  |
| Recall on a gold set  | known-relevant docs retrieved for known queries | ↑      |

Maintain a small gold query→doc set; treat a precision/recall drop as a regression (`eval-scorecard.md`).

## 4. Grounding & citation

- Retrieved context must be **cited** — an agent claim that isn't supported by a retrieved chunk is a
  hallucination (CLAUDE.md §3.6) and must be marked `uncertain — verify`.
- **Stale-knowledge detection:** track index freshness (last re-index vs. source change); flag answers
  served from a stale index. The `gs_aggregate_freshness`-style pattern applies — freshness is an SLI.

## 5. Data retention for indexes

- Indexed memory follows `memory_docs_retention_days` (90d default, aligns with ADR-0013) — see
  [`memory-governance.md`](memory-governance.md).
- Re-embedding on a model change: a new embedding model means re-indexing (embeddings are not
  comparable across models); record the embedding model version with the index.
