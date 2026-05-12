---
fixture_kind: pass
target_question: 성장과정
expected_score: 4.5
expected_revisions_required: false
banned_phrases_hit: []
dimensions_failed: []
notes: |
  Synthesized composite. Not derived from any specific real 자소서.
  ㅁㅁ페이 지원, 성장 과정 응답. STAR 구조 명확. 단일 경험([[project/fraud-detection-2022]])을
  깊이 있게 전개. 구체 수치(정밀도 71%→89%, FP 43% 감소). 두괄식 첫 문장에
  핵심 변화 서술. 진부 표현 없음.
---
머신러닝 모델이 실제 사용자에게 해를 끼칠 수 있다는 사실을 직접 목격한 순간이 저를 데이터 품질 문제에 집중하게 만든 전환점이었습니다.

[[project/fraud-detection-2022]]에서 저는 이상거래 탐지 모델의 정밀도가 71%에 머무르며 정상 사용자 거래의 약 29%가 잘못 차단되는 문제를 발견했습니다. 원인 분석 결과 훈련 데이터에서 특정 연령대 거래 패턴이 과소 표현된 데이터 편향이 확인되었습니다.

저는 [[skill/stratified-sampling]]을 적용한 재샘플링 파이프라인을 설계하고, 피처 엔지니어링 과정에서 시간대 가중치와 디바이스 핑거프린트 조합 피처 7종을 추가했습니다. 4주간의 A/B 테스트 결과, 정밀도는 71%에서 89%로 향상되었고, 정상 거래 오차단율(FP)은 43% 감소했습니다.

이 경험에서 얻은 핵심 교훈은 모델 성능 지표보다 데이터 파이프라인의 신뢰성이 먼저라는 점이었습니다. ㅁㅁ페이의 실시간 사기 탐지 시스템 확장 계획을 보며, 데이터 품질 파이프라인과 모델 모니터링을 동시에 다룰 수 있는 역할로 기여하고 싶습니다.
