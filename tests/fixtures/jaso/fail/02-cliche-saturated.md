---
fixture_kind: fail
target_question: 지원동기
expected_revisions_required: false
banned_phrases_hit: ["성실한", "노력하는", "책임감 있는", "솔선수범하는", "창의적인", "열정적인", "최선을 다해", "임하겠습니다"]
dimensions_failed: ["표현"]
notes: |
  Synthesized composite. Not derived from any specific real 자소서.
  진부 표현 집중 케이스. banned_phrases.json의 high-severity 항목
  (성실한, 노력하는, 책임감 있는, 솔선수범하는, 창의적인, 열정적인,
  최선을 다해, 임하겠습니다) 다수 포함.
  표현(표현) 차원이 복수 hit으로 ≤2로 떨어져야 함.
  구체 수치 없음, 회사 특정성도 낮음.
---
저는 항상 성실한 자세로 어떤 일이든 끝까지 해내는 사람입니다. 주어진 업무에 책임감 있는 태도로 임하고, 팀 내에서도 솔선수범하는 자세를 유지해왔습니다.

대학 생활 내내 창의적인 아이디어를 제안하며 학회와 프로젝트에서 노력하는 모습을 보여왔습니다. 어떤 어려움도 열정적인 마음으로 극복하며, 팀 목표 달성을 위해 최선을 다해 왔습니다.

SOME_COMPANY에 입사하게 된다면, 이러한 마음가짐으로 회사의 발전에 기여하며 임하겠습니다. 부족한 부분은 스스로 채워나가며, 회사와 함께 성장하는 구성원이 되겠습니다.
