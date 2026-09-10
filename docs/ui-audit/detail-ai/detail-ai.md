# Article detail and AI-reading UI audit

Date: 2026-09-10
Scope: article detail, AI summary, article-scoped question entry, and unauthenticated guidance
Target: local portfolio demonstration for large-model application-development roles

## Goal

Turn the existing detail-page AI controls into a clear reading workflow without changing routes, API contracts, frameworks, or the two-column product structure. The page should explain what the model can do, what content it uses, and what the user should expect before and during a request.

## Before

- The AI controls appeared as an unlabeled button, textarea, and second button with little product context.
- The page did not explain that answers are grounded in the current article.
- Empty, loading, failure, and result states were not visibly represented.
- Unauthenticated actions used a disruptive browser alert and moved the user away from the article.
- Article metadata and the boundary between AI assistance and source content were difficult to scan.

Evidence: `01-detail-before.png`.

## Changes

- Preserved the existing detail layout and blue/cyan visual language while strengthening article title, metadata, body, and related-news hierarchy.
- Added a labeled `AI 阅读助手` region with a concise grounding statement and explicit availability badge.
- Added one-click summary, practical quick prompts, a labeled question field, and a persistent result area that identifies AI-generated content.
- Added disabled/loading states, escaped response rendering, stale-response protection, inline error feedback, and accessible live-region semantics.
- Replaced alert-and-redirect behavior with an inline login explanation and an intentional login action.
- Added inline empty-question validation and kept controls usable at the existing mobile breakpoint.

Evidence: `02-detail-after.png`, `03-login-guidance-after.png`, and `04-detail-after-mobile.png`.

## Verification

- Browser checks passed at 1440×900 and 390×844.
- Article selection, quick-prompt insertion, and inline unauthenticated guidance were exercised using the rendered UI.
- Accessible names, region labels, status/alert semantics, and mobile wrapping were checked from the live document structure.
- The before and after screenshots were reviewed together at the same desktop viewport.
- JavaScript syntax, backend regression, offline citation evaluation, Python compilation, OpenAPI generation, dependency integrity, Compose rendering, and container health are rerun before commit.

## Readiness decision

**CONDITIONAL GO** for a local portfolio demonstration. Confidence: high for the unauthenticated UI and responsive-layout scope.

An authenticated request against a real model provider was not exercised in this module. That end-to-end provider check remains required before a public production claim.
