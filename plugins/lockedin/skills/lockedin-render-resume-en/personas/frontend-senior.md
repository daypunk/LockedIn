# frontend-senior

## Snapshot

Senior frontend engineer with 7-12 years of experience. Owns or significantly
contributes to a design system or component library, ships production-grade
UI at scale, and carries accountability for Core Web Vitals or equivalent
performance budgets. Distinct from `us-tech-senior` in that frontend-senior
foregrounds browser rendering, component architecture, accessibility
compliance, and cross-functional collaboration with product designers. May
operate as a design-engineer hybrid at companies without a dedicated design
system team. Targets roles at companies where frontend complexity is the
competitive differentiator: rich web apps, high-traffic consumer products,
or B2B platforms with demanding UX fidelity requirements.

## Skill cluster

Hard skills (8-12 items):
- React (or Vue / Svelte) at advanced composition depth (custom hooks,
  concurrent features, Suspense boundaries)
- TypeScript — strict mode, type-level utilities, discriminated unions
- State management (Zustand, Jotai, TanStack Query, or Redux Toolkit)
- Performance tooling: Lighthouse CI, WebPageTest, browser DevTools flame
  graphs, INP/LCP/CLS budgets
- Accessibility — WCAG 2.1 AA, screen reader testing, aria-live regions
- Build tooling (Vite, esbuild, Webpack 5, module federation)
- CSS architecture at scale (CSS Modules, Tailwind, CSS custom properties,
  design tokens)
- Testing: Vitest / Jest, Playwright, axe-core for accessibility regression
- Design system tooling (Storybook, Chromatic, Figma tokens)
- SSR / SSG (Next.js, Remix, or Astro) including hydration strategies
- Web performance APIs (PerformanceObserver, Resource Hints, lazy loading)
- Browser compatibility strategy and polyfill budgeting

Soft / cross-functional skills (4-6 items):
- Design-engineering collaboration: translating design tokens and comp redlines
  into production components with minimal back-and-forth
- Code review leadership for component API design and accessibility correctness
- Cross-squad component governance and design system adoption advocacy
- Performance review facilitation with product and design stakeholders

## Responsibility patterns

- Owns or co-owns the shared component library, maintaining API stability,
  Storybook documentation, and migration guides across consuming squads.
- Sets and enforces performance budgets (Core Web Vitals thresholds) via CI
  gates; diagnoses and resolves regressions using browser profiling tools.
- Ships accessibility-compliant components verified against WCAG 2.1 AA and
  validated with screen-reader and keyboard-navigation testing.
- Architects client-side data-fetching patterns (server state vs. client state
  boundaries, cache invalidation strategies) that other engineers follow.
- Reviews pull requests from mid-level frontend engineers with focus on
  component API design, re-render surface, and accessibility correctness.
- Drives adoption of new browser platform features (CSS container queries,
  View Transitions API, native lazy loading) through phased rollouts with
  fallback strategies.
- Collaborates with design to establish and maintain a design-token pipeline
  that keeps Figma and production in sync with a CI-enforced contract.

## Tone guidance

Vocabulary register: outcome-led, component-and-metric grounded. Bullets
should name a specific technology (React, Playwright, Lighthouse) and a
measurable result (Lighthouse score, LCP delta, Storybook component count,
accessibility violation count). Avoid pure description of activity without
the performance or user-impact anchor.

Lean on: Owned, Shipped, Reduced, Improved, Enforced, Built, Architected,
Instrumented, Standardized, Audited, Accelerated.

Avoid: "worked on UI", "made the site faster" (quantify), "user-friendly"
(design-speak, not engineering-speak), "pixel-perfect" (vague), "modern
frontend stack" (list the actual technologies).

## Action verb cluster

Shipped, Owned, Reduced, Built, Architected, Enforced, Audited, Standardized,
Instrumented, Accelerated, Established, Migrated, Refactored, Led, Defined,
Upgraded, Adopted, Composed

## Banned phrases (persona-specific additions to global banned_phrases.json)

- "pixel-perfect" — aesthetic claim with no measurable definition; replace
  with design-token fidelity or visual regression test count
- "user-friendly" — design opinion, not an engineering claim; replace with
  a usability metric or accessibility score
- "modern frontend" — vague; name the actual framework and version
- "responsive design" — table stakes since 2015; acceptable only when paired
  with a specific breakpoint challenge or measured layout-shift improvement
- "cross-browser compatibility" — only meaningful with specific browser list
  and test methodology
- "reusable components" — filler without a count (N components shared across
  X squads)

## Persona fit scoring guidance

- `frontend-senior` persona_fit >= 4 requires at least 2 framework-specific
  mentions (e.g., React, TypeScript, Vite — not just "JavaScript") and at
  least 1 performance or accessibility metric (Lighthouse score, LCP
  reduction, WCAG compliance, axe-core violation count).
- A resume that reads as general fullstack with thin frontend detail cannot
  score above 3.0 on persona_fit.
- Design system ownership or component library scope (component count, squad
  adoption rate) is a strong signal for senior frontend scope and elevates
  persona_fit toward 5.0.
- Absence of any performance metric is a cap at 3.5 — senior frontend
  engineers are expected to quantify rendering work.

## Quality bar examples

Before: "Improved frontend performance across the application."
After: "Reduced LCP from 4.1s to 1.8s on the product listing page by
replacing a client-rendered skeleton with server-streamed HTML and adding
image preload hints, raising Lighthouse Performance score from 54 to 87."

Before: "Built reusable React components for the team."
After: "Shipped 58-component design system in React + Storybook, adopted by
4 product squads within one quarter; reduced new-feature UI scaffolding time
from ~2 days to ~3 hours per squad per sprint."

Before: "Worked on accessibility improvements."
After: "Audited the checkout funnel with axe-core and VoiceOver, eliminating
34 WCAG 2.1 AA violations and achieving keyboard-navigable checkout end-to-end
in 6 weeks."
