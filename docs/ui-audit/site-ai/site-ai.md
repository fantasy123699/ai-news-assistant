# Site-wide AI news assistant audit

Date: 2026-09-16
Scope: site-wide AI drawer, final-answer handling, and cited-source navigation
Target: local portfolio demonstration for large-model application-development roles

## Goal

Make the existing retrieval-augmented assistant visibly trustworthy without changing its drawer structure, API route, retrieval strategy, or frontend stack. A user should be able to distinguish the final answer from its sources, open a cited article, and understand empty, loading, and failure states.

## Before

- The model could expose untagged reasoning before the user-facing answer.
- The answer and reference cards were injected through raw `innerHTML`, so model and database content were not safely escaped.
- References were generic clickable containers without citation identifiers or keyboard semantics.
- The drawer did not clearly communicate grounding, final-answer status, input requirements, or request progress.
- The closed off-canvas panel left its controls available to keyboard navigation.

Fresh evidence was reviewed in the Codex in-app browser before implementation, including a live answer that exposed reasoning text.

## Changes

- Versioned the site-news prompt as `site-news-chat-v2`, required a final-only response contract, and applied final-answer extraction before saving or returning site and article chat answers.
- Added deterministic handling for `<final>` blocks and the observed Chinese final-section pattern while preserving existing plain-answer compatibility.
- Rebuilt the drawer message renderer around escaped content and native source buttons.
- Separated `AI 最终回答` from an explicit `引用来源` section with citation IDs, result count, article title, category, and views.
- Added a grounding statement, persistent field label and hint, inline empty-input validation, disabled/loading feedback, friendly failure recovery, and input restoration.
- Added accessible log/alert semantics, dynamic open/close labels, focus recovery, and an inert closed-panel state.
- Preserved the current blue/cyan visual language and existing desktop/mobile drawer behavior.

## Verification flows

1. Open assistant -> the drawer opens, focus moves to the labeled question field, and the tab is announced as “关闭 AI 新闻助手”.
2. Submit an empty question -> inline validation appears and focus remains on the field.
3. Submit a grounded question while logged in -> the request completes with only `AI 最终回答`; no reasoning text is visible.
4. Review citations -> a `引用来源` region lists the matching `来源1` article as a native button.
5. Open the citation -> the drawer closes, focus returns to its tab, and the cited article detail loads.
6. Close with Escape -> the drawer closes and focus returns to the trigger.

Health: all 32 unit tests pass; JavaScript syntax and Python compilation pass; the rebuilt Compose application, MySQL, and Redis containers are healthy; the verified `/ai/chat` request returned HTTP 200; application logs contained no request errors.

## Readiness decision

**CONDITIONAL GO** for a local portfolio demonstration. Confidence: high for the tested final-answer, citation, safety, and interaction scope.

Public-production readiness still requires hardened session storage, rate limiting, deployment secrets, HTTPS, backup/restore evidence, and operational monitoring. Streaming output remains a separate product module.
