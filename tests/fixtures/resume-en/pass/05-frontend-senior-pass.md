---
fixture_kind: pass
persona: frontend-senior
expected_score: 4.3
expected_revisions_required: false
banned_phrases_hit: []
dimensions_failed: []
notes: |
  Synthesized composite. Placeholders only (JANE_DOE, SOME_COMPANY, BLUE_LABS).
  Demonstrates strong persona_fit for frontend-senior: specific framework
  mentions (React, TypeScript, Vite), Lighthouse / Core Web Vitals metrics,
  design system ownership with adoption evidence, and accessibility work
  quantified by WCAG violation count. Verbs: Shipped, Reduced, Audited,
  Enforced, Built, Standardized, Established.
---

## JANE_DOE

jane@placeholder.invalid | github.com/placeholder | Austin, TX

---

### SOME_COMPANY — Senior Frontend Engineer (Design Systems)
*2021 – Present*

Owned the shared component library adopted by 5 product squads; co-led the Vite migration from Create React App.

- Shipped a 64-component React + TypeScript design system with Storybook documentation and Chromatic visual regression gates; reduced new-feature UI scaffolding time from ~3 days to ~5 hours per squad per sprint after full adoption.
- Reduced LCP from 5.2s to 1.9s on the marketing landing page by replacing client-rendered skeleton screens with server-streamed HTML (Next.js App Router), adding `<link rel="preload">` for above-fold images, and enabling Brotli compression at the CDN layer.
- Enforced Core Web Vitals budgets in CI via Lighthouse CI on every PR, catching 4 INP regressions before they reached production and maintaining a p75 INP below 150ms across the top-5 product surfaces.
- Audited the checkout funnel with axe-core and VoiceOver on macOS, eliminating 41 WCAG 2.1 AA violations in 8 weeks and achieving full keyboard-navigable checkout end-to-end.

### BLUE_LABS — Frontend Engineer
*2018 – 2021*

- Built the multi-step form wizard component used across 7 product flows, reducing form-abandon rate from 38% to 22% by replacing a full-page-reload validation pattern with inline real-time validation.
- Standardized CSS architecture across the codebase by migrating 14k lines of global stylesheets to CSS Modules + design token variables, eliminating 3 recurring z-index conflict classes over 6 months.
- Established ESLint + TypeScript strict-mode configuration in CI, catching 200+ implicit-any type errors in the first run and holding the codebase at zero `any` declarations for 18 months.

---

### Skills

React · TypeScript · Next.js · Vite · Storybook · Chromatic · Playwright · axe-core · CSS Modules · Tailwind · Lighthouse CI
