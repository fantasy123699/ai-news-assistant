# Site AI streaming-answer audit

Date: 2026-09-16
Scope: real model streaming for the site-wide AI assistant
Release target: local portfolio demonstration for large-model application-development roles

## Goal

Reduce the long silent wait for a local model while preserving the most important trust boundary: users may see only the final answer, never hidden reasoning. The existing drawer, retrieval behavior, citations, and non-streaming endpoint remain intact.

## System and trust boundary

- The browser sends one authenticated question to `POST /ai/chat/stream`.
- FastAPI completes retrieval before opening an NDJSON response.
- Ollama or an OpenAI-compatible provider streams partial model output.
- Provider reasoning fields and untrusted pre-answer content remain server-side.
- Only verified final-answer fragments cross the browser boundary.
- The database stores the answer only after a successful completed stream; citations arrive in the final event.

## Changes

- Added native streaming clients for Ollama and OpenAI-compatible chat-completion endpoints.
- Explicitly enabled Ollama's separate thinking channel and discarded it from user-facing output.
- Added a chunk-safe final-answer filter for split tags, Chinese final-section markers, plain-answer fallback, and dedicated provider final channels.
- Added an authenticated NDJSON endpoint with `delta`, `done`, and safe `error` events while preserving `/ai/chat` compatibility.
- Updated the browser to parse network chunks progressively, disable duplicate submission, preserve the question on failure, and append citations only after completion.
- Added one atomic live status for retrieval, generation, completion, and failure so screen readers do not announce every token.
- Kept scrolling pinned only while the user remains near the bottom of the conversation.

## Verification flows

1. Submit a grounded question -> the field and action disable and the interface announces retrieval.
2. Provider emits reasoning -> no reasoning text appears in the browser.
3. Provider begins final content -> the answer visibly grows while the label reads `AI 正在生成`.
4. Stream completes -> the label changes to `AI 最终回答`, controls re-enable, and focus returns to the field.
5. Final event arrives -> citations appear once, after the answer, with the correct source count.
6. Stream fails -> the partial result is replaced by a safe failure state and the original question is restored for retry.

Health: all 36 unit tests pass; chunk-boundary, fallback, and provider-final-channel cases are covered; JavaScript syntax and Python compilation pass; a real DeepSeek-R1/Ollama request showed progressive final text followed by two citations; all three Compose services are healthy.

## Readiness decision

**CONDITIONAL GO** for the local portfolio target, with high confidence in the reviewed streaming and reasoning-isolation path.

Broad public exposure still requires rate limiting, session hardening, production telemetry, backup/restore evidence, HTTPS, and deployment-specific capacity testing. Streaming retries intentionally require user action after a failure to avoid duplicated partial output.
