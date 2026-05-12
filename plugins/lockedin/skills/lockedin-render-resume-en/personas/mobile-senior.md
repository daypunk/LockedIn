# mobile-senior

## Snapshot

Senior iOS or Android engineer (or both, including React Native / Flutter
cross-platform experience) with 7-12 years of experience. Owns a significant
surface area of a shipped consumer or enterprise mobile app: release
management, app-size optimization, launch-performance profiling, and
sometimes SDK design for internal or third-party consumers. Distinct from a
generic `us-tech-senior` in that mobile-senior must demonstrate mastery of
platform-specific constraints: app store review cycles, binary size budgets,
cold-start latency, battery/network efficiency, and OS-version compatibility
strategy. Targets roles at companies where the mobile app is the primary
product surface.

## Skill cluster

Hard skills (8-12 items):
- Swift + UIKit / SwiftUI (iOS) or Kotlin + Jetpack Compose (Android),
  or one plus a cross-platform layer (React Native, Flutter)
- Instruments / Android Studio Profiler for CPU, memory, and energy audits
- App size optimization (app thinning, dynamic frameworks, R8 / ProGuard)
- Launch performance profiling (pre-main time, dylib load, first-frame
  rendering)
- Push notification delivery pipelines (APNs / FCM) at production scale
- App distribution: App Store Connect / Google Play, staged rollouts,
  TestFlight / Firebase App Distribution
- CI/CD for mobile: Fastlane, Bitrise, GitHub Actions with code signing
- Crash reporting and stability tooling (Crashlytics, Sentry, Bugsnag)
- Network stack: URLSession / OkHttp, caching strategy, offline-first
  patterns, certificate pinning
- Feature flag and remote configuration systems (in-app A/B testing)
- Deep linking and universal links, routing architecture

Soft / cross-functional skills (4-6 items):
- Release management: coordinating app store submissions, rollback decisions,
  phased rollout judgment
- Cross-platform design collaboration — articulating platform idiom
  differences to product designers
- SDK interface design for internal consumers or third-party integrators
- Incident response for production crashes: triage, hotfix coordination,
  store submission under pressure

## Responsibility patterns

- Owns the mobile release process end-to-end: build pipeline, code signing,
  staged rollout policy, app store submission, and emergency hotfix protocol.
- Profiles and reduces app cold-start time using Instruments / Android
  Profiler, addressing pre-main work, dylib loading, and first-frame
  rendering independently.
- Reduces binary size by auditing asset catalogs, enabling app thinning,
  eliminating dead code through static analysis, and right-sizing third-party
  SDKs.
- Architects offline-first data synchronization patterns that handle conflict
  resolution, background fetch budgets, and network reachability gracefully.
- Designs internal SDK or module boundaries that let feature teams ship
  independently without coupling their release cadence to the main app.
- Leads adoption of new OS capabilities (SwiftUI, Jetpack Compose, background
  task APIs) through phased migration with parallel-run strategies.
- Reviews pull requests for memory safety (retain cycle detection, object
  lifetime), battery impact (background CPU budgets), and accessibility
  compliance (Dynamic Type, VoiceOver labels).

## Tone guidance

Vocabulary register: platform-specific and metric-dense. Bullets must name a
concrete platform concept (cold-start, dylib, app thinning, memory graph,
UIKit/Compose) and a before/after metric (launch time in ms, binary delta in
MB, crash-free session rate, ANR rate). Avoid platform-agnostic server-side
language for things that are distinctly mobile problems.

Lean on: Reduced, Profiled, Eliminated, Shipped, Owned, Migrated, Hardened,
Built, Optimized, Accelerated, Authored, Designed, Automated.

Avoid: "built mobile apps" (too generic), "iOS/Android development" without
a specific challenge, "improved user experience" without a metric, "worked
with the backend team" (masks ownership of the client-side contract).

## Action verb cluster

Profiled, Reduced, Shipped, Owned, Migrated, Eliminated, Hardened, Built,
Automated, Designed, Accelerated, Authored, Optimized, Instrumented, Led,
Standardized, Refactored, Integrated

## Banned phrases (persona-specific additions to global banned_phrases.json)

- "improved app performance" — quantify: launch time, frame rate, battery
  drain, crash-free session rate
- "mobile-first" — design philosophy claim, not an engineering claim
- "smooth user experience" — too vague; name the frame-rate budget or the
  janky-frames reduction
- "cross-platform solution" — acceptable only with the specific framework
  (React Native 0.73, Flutter 3.x) and the specific trade-off addressed
- "pushed to App Store" — routine release is not a bullet; include the
  metric or the scope signal (staged rollout percentage, user count, SLA)
- "app optimization" — always qualify: binary size, cold-start, or runtime
  memory

## Persona fit scoring guidance

- `mobile-senior` persona_fit >= 4 requires at least 1 platform-specific
  metric (cold-start ms, binary size MB, crash-free rate %, or ANR rate)
  AND at least 1 explicit platform noun (Swift, Kotlin, Xcode Instruments,
  Android Profiler, APNs, FCM, App Store, Google Play).
- A resume that reads as fullstack or backend with one line about "mobile
  experience" cannot score above 2.0.
- Release ownership evidence (store submission, staged rollout, or hotfix
  protocol) is a strong plus for senior scope.
- Crash-free session rate or ANR rate improvement is the strongest single
  signal for mobile-senior persona_fit.

## Quality bar examples

Before: "Optimized app performance and reduced crashes."
After: "Profiled cold-start with Instruments, eliminating 340ms of pre-main
dylib-loading time by converting 3 dynamic frameworks to static, reducing
average cold-start from 2.1s to 1.6s on iPhone 12."

Before: "Worked on the mobile CI pipeline."
After: "Automated iOS code signing and TestFlight distribution via Fastlane
+ GitHub Actions, cutting release-candidate build time from 47 minutes to
11 minutes and eliminating manual provisioning profile errors across a
6-engineer team."

Before: "Built features for the iOS app."
After: "Migrated 4 high-traffic screens from UIKit to SwiftUI using a
parallel-host strategy, achieving zero user-visible regressions while
reducing view-controller line count by 62% across the migrated surfaces."
