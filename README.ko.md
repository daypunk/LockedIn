# selfgraph

[English](README.md) · **한국어**

> **Claude Code 위에서 동작하는 개인 경험 지식 그래프. Zero learning curve.**
> 스키마 배울 필요 없음. 커맨드 외울 필요 없음. Claude에게 말 걸면
> selfgraph가 경험을 구조화하고 원하는 산출물을 만든다.

[![Status](https://img.shields.io/badge/status-beta-blue.svg)]()
[![Version](https://img.shields.io/badge/version-1.0.0--beta-blue.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](./LICENSE)

## 설치

Claude Code 안에서 세 줄:

```
/plugin marketplace add daypunk/selfgraph
/plugin install selfgraph@selfgraph
/selfgraph:setup
```

세 번째는 일회성 wizard (HUD 연결 + 환경설정 두 가지). wizard 끝나고
Claude Code를 재시작하면 채팅 하단에 Claude Code 사용량 + vault 상태
한 줄이 노출되고, 스킬은 자연어에 자동으로 활성화된다.

## 쓰기

원하는 걸 말하면 된다.

경험을 기록:

- *"내 경험 정리 시작"*
- *"오늘 디자인팀 미팅 정리해줘"*
- *"이 PDF 이력서 흡수해줘"*
- *"이번 주 LLM 에이전트 논문 학습한 내용 추가"*

이미 쌓인 것에서 뽑기:

- *"us-tech-senior 타겟으로 영문 이력서 만들어줘"*
- *"X 회사 자소서 1번 문항 써줘"*
- *"지난 분기 의사결정 요약해줘"*
- *"내 그래프 보여줘"*

selfgraph가 알아서 적합한 흐름을 골라 실행하고, 필요할 때 한 번에 한
질문씩만 물어본다. 슬래시 커맨드(`/selfgraph init`, `/selfgraph render
resume` 등)도 동작한다.

## 두 개의 저장소

<!-- diagram-store-ab : leave this block empty for the image to be inserted -->

## 왜 이걸 만드나

selfgraph는 **경험을 정리하는 도구**다. 회의·학습·일·사이드 프로젝트·
의사결정 — 모든 도메인이 본인이 소유하는 typed 마크다운 노트 폴더가
된다. 그 구조화된 저장소가 생기면 후속 작업은 그것에 대한 쿼리에
불과하다: 이력서, 자소서, 면접 토킹포인트, 분기 회고, 과거 작업에서
유도한 새 아이디어.

대부분 도구는 매번 산출물을 처음부터 다시 만든다. 진짜 자료는 글이
아니라 **글 뒤의 구조화된 경험**이다.

## Features

- **말 걸면 동작.** 자연어 활성화. 커맨드 외울 필요 없다.
- **하나의 그래프, 여러 렌더.** 영문 이력서, 한국 자소서, 인터랙티브
  그래프 viz — 모두 같은 vault에서.
- **Two-turn writer / reviewer.** 렌더러가 분리된 Claude turn에서 rubric에
  맞춰 자기 평가. JSON 점수로 제출 전에 괜찮은지 안다.
- **구독으로 동작, API key 불필요.** 추론은 Claude Code 스킬을 통해. 작업
  종류에 따라 가장 작은 모델 tier 자동 선택.
- **모든 것을 본인이 소유.** `~/.selfgraph/`의 평범한 마크다운. Obsidian
  호환, 이식 가능, 외부 송신 없음.

## 상태

**v1.0 (Beta)**. 첫 공개 릴리스. 렌더러는 도메인당 20+ 가이드의
cross-source 합의 신호로 research-based calibration 적용. 실명 도메인
리뷰어 engagement은 v1.1 타겟. Ontology는 v0.2 (15 entity types, 15
edge predicates, JSON Resume / Schema.org / FOAF 정렬).

## Advanced

power-user CLI, statusLine HUD, vault 스키마, 아키텍처, ontology 정렬,
오케스트레이션 — `docs/` 참조:

- `docs/architecture.md` · `docs/ontology-spec.md` · `docs/ontology-mapping.md`
- `docs/orchestration.md` · `docs/hud.md` · `docs/cli.md`
- `docs/adr/` — 아키텍처 의사결정 기록

## License

MIT. [LICENSE](./LICENSE) 참조.
