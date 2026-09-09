# RAG retrieval baseline

The site chat uses a small, explainable retrieval pipeline suited to the current MySQL news dataset:

1. Detect an explicit news category and extract up to five Chinese search terms.
2. Match each term against title, description, and content.
3. Rank matches with title weight 5, description weight 3, and content weight 1.
4. Fall back to recent items in the requested category, then to recent site-wide items.
5. Label context and API references as `来源N` so answers can cite the retrieved record.

This is intentionally a lexical baseline. It is cheap to run, easy to explain, and measurable before the project has enough data to justify embeddings and a vector database.

## Run the retrieval evaluation

Initialize `database/schema.sql` and `database/seed.sql`, configure `.env`, then run:

```bash
python scripts/evaluate_retrieval.py
```

The checked-in cases report Hit@3 and fail with a non-zero exit code when the hit rate is below 75%. Add real anonymized queries and expected titles to `evals/rag_retrieval_cases.json` as the project grows.
