# Homepage and news-list UI audit

Date: 2026-09-10
Scope: homepage, news search/list, article selection, and the global AI drawer shell
Target: local portfolio demonstration for large-model application-development roles

## Goal

Make the existing workflow easier to understand and operate without changing the application architecture or adding speculative features. The first screen should communicate the product's AI-news purpose, support fast scanning, and behave predictably on desktop and mobile.

## Before

- The page resembled a generic administration screen and did not explain its AI value above the fold.
- On a narrow viewport, the full sidebar consumed the first screen before any news appeared.
- News rows had no keyboard interaction or persistent selected state.
- Search had no loading, error, or useful empty-result feedback, and one-page pagination remained enabled.
- The AI drawer opened on hover and could obscure the reading view accidentally.

Evidence: `01-home-before-desktop.png`, `02-home-before-mobile.png`, and `03-news-detail-before.png`.

## Changes

- Kept the original sidebar and two-column information architecture while introducing a restrained news-workbench hierarchy and reusable color tokens.
- Added a short product-value statement, clearer feed/reading labels, and a useful reading empty state.
- Added loading, inline error, empty-result, disabled-pagination, hover, focus, and selected states.
- Made news rows keyboard operable with Enter or Space and exposed current navigation/category state to assistive technology.
- Compressed mobile navigation, made categories horizontally scrollable, removed page-level horizontal overflow, and kept primary targets at least 44 px high.
- Replaced hover-only AI drawer activation with a button, `aria-expanded`, and Escape-to-close behavior.

Evidence: `04-home-after-desktop.png`, `05-search-empty-after.png`, `06-home-after-mobile.png`, and `07-news-detail-after.png`.

## Verification

- Browser checks passed at 1440×900 and 390×844.
- Search empty state, reset, keyboard article opening, selected state, AI drawer toggle, and Escape close were exercised.
- Mobile document width equals its client width; checked navigation, category, search, and pagination controls are 44 px high.
- Browser console contained no errors during the verified flow.

## Readiness decision

**CONDITIONAL GO** for a local portfolio demonstration. Confidence: high for this UI scope.

This is not approval for a public production launch. Authentication abuse controls, production secrets, TLS, backups, monitoring, and real-provider end-to-end checks remain outside this module.
