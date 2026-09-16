# LLM client

The backend supports its model connection through one asynchronous client in `utils/local_llm.py`. It supports Ollama and OpenAI-compatible local servers such as LM Studio and vLLM.

## Configuration

| Variable | Default | Purpose |
| --- | --- | --- |
| `LOCAL_LLM_PROVIDER` | `ollama` | `ollama`, `openai`, `lmstudio`, or `vllm` |
| `LOCAL_LLM_MODEL` | `deepseek-r1:1.5b` | Model name sent to the provider |
| `LOCAL_LLM_BASE_URL` | `http://127.0.0.1:11435` | Provider base URL |
| `LOCAL_LLM_TIMEOUT_SECONDS` | `60` | Per-request timeout in seconds |
| `LOCAL_LLM_MAX_RETRIES` | `2` | Retries after timeouts, connection errors, 408, 429, or 5xx responses |
| `LOCAL_LLM_RETRY_BACKOFF_SECONDS` | `0.5` | Initial exponential-backoff delay |

Ollama requests use `/api/chat`. OpenAI-compatible providers use `/v1/chat/completions`. The client does not read system proxy variables because the supported services are expected to be local.

## Streaming behavior

`POST /ai/chat/stream` returns newline-delimited JSON (`application/x-ndjson`). Each line is one of:

- `delta`: a verified final-answer fragment;
- `done`: the complete saved answer, citations, prompt version, and retrieval metadata;
- `error`: a safe user-facing failure message after the HTTP stream has started.

For Ollama thinking models, the request enables the provider's separate `thinking` field and only streams `message.content`. OpenAI-compatible reasoning fields are likewise kept separate when the provider exposes them. A final-answer stream filter still buffers untrusted content until it sees a `<final>` block or supported final-answer marker, and falls back to the existing completed-answer extraction when a provider does not expose a separate channel.

The browser announces retrieval, generation, completion, and failure as atomic status changes instead of announcing every token. Citations are rendered only with the final `done` event.

## Failure behavior

- Timeouts become HTTP 504 responses after the retry budget is exhausted.
- Connection failures, invalid JSON, empty model output, and upstream rejection become safe HTTP 502 responses.
- Logs record provider, model, retry attempt, and latency, but never prompts, responses, or upstream error bodies.

Retries are intentionally limited. They improve tolerance of transient failures without hiding persistent model-service problems or multiplying latency indefinitely.

The streaming path does not restart a response after content has begun, because retrying could duplicate partial text. A failed stream ends with a safe `error` event and leaves the user's question available for an intentional retry.
