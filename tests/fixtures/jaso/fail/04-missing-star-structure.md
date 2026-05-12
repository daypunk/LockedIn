---
fixture_kind: fail
target_question: 직무경험
expected_dimensions:
  두괄식: 3
  구조화: 1
  구체성: 4
  표현: 4
  적합성: 4
expected_revisions_required: true
banned_phrases_hit: []
dimensions_failed: ["구조화"]
prompt: 가장 도전적이었던 경험을 서술해주세요
company: SOME_COMPANY
industry: IT 대기업
notes: |
  Failure mode: continuous prose, no STAR / PAR / paragraph structure.
  Has metrics and active voice but reader cannot easily map S → T → A
  → R. The 구조화 dimension drops because paragraphs do not delimit
  the structural slots.
---
대학 시절 추천 시스템 프로젝트가 가장 도전적이었습니다. 추천 모델을 개발했고 클릭률을 23% 끌어올렸으며 그 과정에서 8주 동안 hybrid 임베딩 모델을 설계했고 베이스라인은 클릭률 4.2%에 그쳤으며 신규 사용자에게 인기 기사만 노출되는 cold-start 문제가 있었고 저는 콘텐츠 임베딩과 사용자 발화의 유사도를 결합하는 접근을 시도했고 데이터셋은 1만 건이었으며 학과 졸업프로젝트로 채택되었고 A/B 테스트로 클릭률 5.2%를 측정했고 이탈률도 38%에서 29%로 감소했고 이 과정에서 추천이 사용자의 시간을 설계하는 일이라는 것을 배웠고 SOME_COMPANY가 멀티모달 추천에 투자하고 있다는 점을 주목하며 입사 후 6개월 안에 실서비스 메트릭에 기여하고자 합니다.
