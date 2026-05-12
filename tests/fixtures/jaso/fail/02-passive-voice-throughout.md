---
fixture_kind: fail
target_question: 직무경험
expected_dimensions:
  두괄식: 3
  구조화: 3
  구체성: 3
  표현: 2
  적합성: 3
expected_revisions_required: true
banned_phrases_hit: []
dimensions_failed: ["표현"]
prompt: 직무 관련 경험을 서술해주세요
company: SOME_COMPANY
industry: IT 대기업
notes: |
  Failure mode: passive voice throughout — most verbs are passive
  ("수행되었습니다", "진행되었습니다", "발휘되었습니다", "측정되었습니다").
  표현 dimension drops because reviewer counts ≥3 passive constructions.
---
졸업프로젝트에서 추천 시스템 개발이 진행되었습니다. 팀에 의해 데이터 수집이 시작되었고, 모델 학습이 8주에 걸쳐 수행되었습니다.

분석 단계에서는 다양한 알고리즘이 비교되었습니다. 최종 모델로 hybrid 추천이 선정되었고, A/B 테스트가 진행되었습니다. 클릭률 개선이 측정되었으며, 결과는 학과 발표회에서 공유되었습니다.

이 과정에서 협업 능력이 키워졌고, 데이터 분석 역량이 발휘되었습니다. 팀원들과의 의사소통이 강화되었으며, 문제 해결 과정이 학습되었습니다. 이러한 경험들이 직무 수행에 반영될 것이라 기대됩니다.
