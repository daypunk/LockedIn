---
fixture_kind: pass
persona: mobile-senior
expected_score: 4.3
expected_revisions_required: false
banned_phrases_hit: []
dimensions_failed: []
notes: |
  Synthesized composite. Placeholders only (SAMPLE_USER, GLOBAL_TECH, ACME_CORP).
  Demonstrates strong persona_fit for mobile-senior: cold-start metric,
  binary size delta, crash-free session rate improvement, release management
  ownership, and platform-specific nouns (Instruments, Fastlane, UIKit,
  SwiftUI, Xcode). Verbs: Profiled, Reduced, Shipped, Owned, Automated,
  Migrated.
---

## SAMPLE_USER

sample@placeholder.invalid | github.com/placeholder | New York, NY

---

### GLOBAL_TECH — Senior iOS Engineer
*2021 – Present*

Owned the release pipeline and performance budget for a consumer app with 2.1M MAU; primary release manager for App Store submissions.

- Profiled cold-start latency using Xcode Instruments on a fleet of A12–A16 devices; eliminated 380ms of pre-main time by converting 4 dynamic frameworks to static and lazy-loading 2 non-critical third-party SDKs, reducing median cold start from 2.4s to 1.5s across the device matrix.
- Reduced binary size from 121 MB to 74 MB by auditing the asset catalog with Instruments' Asset Catalog inspector, enabling app thinning for device-specific slices, and removing 3 redundant third-party libraries with in-house replacements.
- Owned the staged rollout process for 18 consecutive App Store releases: configured phased rollouts starting at 1%, monitored crash-free session rate in Crashlytics, and made hold/proceed decisions with a defined SLA of 4 hours per rollout stage.
- Migrated 5 high-traffic screens from UIKit to SwiftUI using a parallel-host container strategy, achieving zero user-visible regressions while reducing view controller code by 58% across the migrated surfaces.

### ACME_CORP — iOS Engineer
*2018 – 2021*

- Automated the iOS code signing and TestFlight distribution workflow using Fastlane + GitHub Actions, cutting release-candidate build time from 52 minutes to 9 minutes and eliminating manual provisioning profile management for a 7-engineer mobile team.
- Shipped offline-first sync for the note-taking module using Core Data with conflict resolution via a last-write-wins policy on per-field timestamps; offline read coverage grew from 0% to 100% with a 5-minute maximum staleness window.

---

### Skills

Swift · SwiftUI · UIKit · Xcode Instruments · Fastlane · Crashlytics · Core Data · APNs · GitHub Actions · Firebase App Distribution
