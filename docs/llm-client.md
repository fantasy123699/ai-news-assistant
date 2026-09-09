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

## Failure behavior

- Timeouts become HTTP 504 responses after the retry budget is exhausted.
- Connection failures, invalid JSON, empty model output, and upstream rejection become safe HTTP 502 responses.
- Logs record provider, model, retry attempt, and latency, but never prompts, responses, or upstream error bodies.

Retries are intentionally limited. They improve tolerance of transient failures without hiding persistent model-service problems or multiplying latency indefinitely.
