# Prompt versioning and citation-grounding evaluation

The site-news chat prompt is maintained in `toutiao_backend/utils/prompts.py`. Its version is returned as `prompt_version` by `POST /ai/chat`, so evaluation results and API responses can be associated with the prompt that produced them.

Change the version only when prompt behavior changes. Keep retrieval, provider, and model changes separate so evaluation comparisons remain understandable.

## Run the offline evaluation

```bash
python scripts/evaluate_faithfulness.py
```

The evaluator checks two deterministic answer-level properties:

- every cited `来源N` exists in the API reference list;
- every substantive statement contains at least one valid citation.

This is a citation-grounding proxy, not proof that a source semantically entails a statement. Semantic faithfulness should be evaluated later with reviewed production examples or a separately calibrated model judge.
