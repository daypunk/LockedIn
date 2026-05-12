---
fixture_kind: pass
target_question: 지원동기
expected_score: 4.4
expected_revisions_required: false
banned_phrases_hit: []
dimensions_failed: []
notes: |
  Synthesized composite. Not derived from any specific real 자소서.
  ㅇㅇ테크 핀테크 지원동기. 두괄식 첫 문장에 핵심 동기 명시. STAR 구조.
  구체 프로젝트([[project/payment-latency-2023]]) + 수치 언급.
  회사 방향(실시간 정산) + 역할 연결. 진부 표현 없음.
---
ㅇㅇ테크의 실시간 정산 인프라가 1일 평균 340만 건의 결제를 처리한다는 공개 기술 블로그를 읽고, 그 처리량 뒤편의 아키텍처를 직접 설계하고 싶다는 확신이 생겼습니다.

[[project/payment-latency-2023]]에서 저는 레거시 배치 정산 시스템의 지연 원인을 분석하여, 메시지 큐 기반 파이프라인으로 전환함으로써 정산 완료 시간을 기존 4시간에서 18분으로 단축했습니다. 이 프로젝트를 통해 대규모 트랜잭션 처리의 병목은 DB 쓰기 경합이 아니라 배치 스케줄링의 불균형 분산에 있음을 체감했고, 이벤트 드리븐 설계에 대한 이해를 실서비스 수준으로 높였습니다.

ㅇㅇ테크는 현재 오픈뱅킹 API 연동 확대와 다중 PG사 통합 과제를 공개적으로 추진 중입니다. [[skill/distributed-transaction]] 경험을 바탕으로 Saga 패턴 기반 분산 트랜잭션 설계에 즉시 기여할 수 있으며, 입사 6개월 안에 기존 정산 파이프라인의 처리 지연 구간 2개 이상을 식별하고 개선안을 제안하는 것을 첫 목표로 설정하겠습니다.
