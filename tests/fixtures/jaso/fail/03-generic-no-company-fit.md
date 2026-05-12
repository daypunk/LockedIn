---
fixture_kind: fail
target_question: 지원동기
expected_dimensions:
  두괄식: 3
  구조화: 3
  구체성: 3
  표현: 3
  적합성: 1
expected_revisions_required: true
banned_phrases_hit: []
dimensions_failed: ["적합성"]
prompt: 우리 회사에 지원한 동기를 서술해주세요
company: SOME_COMPANY
industry: 일반
notes: |
  Failure mode: zero company-specific facts. The text could be submitted
  to any company in any industry verbatim. 적합성 (company / role fit)
  dimension drops to ≤2.
---
저는 성장 가능성이 있는 회사에서 일하고 싶어 지원합니다. 좋은 동료들과 함께 배우는 환경을 추구합니다.

대학에서 컴퓨터공학을 전공했고, 졸업프로젝트로 추천 시스템을 개발했습니다. 6개월 동안 진행했고, 클릭률을 23% 개선했습니다. 이 과정에서 협업과 문제 해결의 중요성을 배웠습니다.

좋은 회사에서 좋은 일을 하고 싶다는 마음으로 지원합니다. 입사 후에는 회사의 성장에 함께 기여할 수 있는 인재가 되고자 합니다. 산업의 변화에 발맞춰 지속적으로 학습하며, 팀과 함께 성장하는 모습을 보이겠습니다.
