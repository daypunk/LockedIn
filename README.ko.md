<p align="center">
  <img src="docs/assets/logo.png" alt="LockedIn" width="100%" />
</p>

# LockedIn

[English](README.md) | **한국어**

[![version](https://img.shields.io/badge/version-1.1.0-orange.svg)](https://github.com/daypunk/LockedIn/releases)
[![license](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)

> ***Linked In 하기 전에, Locked In.***

Claude Code에 이력서를 던지거나 짧은 질문 몇 개에 답해 본인의 경험을 구조화하세요. 그 다음부터는 묻기만 하면 됩니다. 영문 레쥬메, 한국 자소서, 면접 답변, 새 프로젝트 아이디어가 구조화된 경험을 기반으로 나옵니다.

## 설치

Claude Code 안에서 다음 세 명령을 차례로 실행합니다.

```
/plugin marketplace add daypunk/LockedIn
/plugin install lockedin@lockedin
/lockedin:setup
```

세 번째 명령은 한 번만 실행하는 wizard입니다. 채팅 하단의 상태 표시줄을 연결하고, 기본 인터뷰 언어를 선택하고, 경험 저장 위치를 정합니다.

## 사용법

LockedIn은 Claude Code에서 자신의 경험에 대해 자연어로 이야기할 때 자동으로 활성화됩니다. 외워야 할 명령은 없습니다.

경험을 기록하고 싶을 때 쓰는 표현:

- "내 경험 정리 시작할게"
- "오늘 디자인팀 미팅 정리해줘"
- "이력서 PDF 흡수해줘"
- "이번 주 논문에서 배운 거 추가할게"

이미 쌓인 경험에서 산출물을 만들고 싶을 때 쓰는 표현:

- "영문 이력서 만들어줘"
- "XX 회사의 XX 직무에 지원할건데, XX 문항의 답변을 써줘"
- "지난 분기 의사결정 요약해줘"

LockedIn은 추가 정보가 필요할 때 한 번에 한 질문씩만 묻고, 충분해지면 멈춥니다.

<p align="center">
  <img src="docs/assets/architecture.png" alt="LockedIn 아키텍처" width="100%" />
</p>

## 왜 만들었나

대부분의 커리어 도구는 산출물을 매번 처음부터 다시 만듭니다. 산출물이 목적이고, 그 기반은 휘발됩니다. LockedIn은 그 순서를 뒤집습니다. 구조화된 경험은 로컬의 `~/Documents/LockedIn/`에 마크다운 파일로 쌓이며, 사용자가 직접 소유하고 다른 도구로 가져갈 수 있습니다. 이력서, 자소서, 회의록은 그 기억에 대한 산출물이지 기억 자체가 아닙니다.

## 특징

- **자연어로 활성화.** 외울 명령 없이 Claude Code에 평소처럼 말 걸면 됩니다.
- **하나의 vault, 네 가지 산출물.** 영문 이력서, 한국 자소서, 면접 답변, 새 프로젝트 아이디어가 같은 출처에서 나옵니다.
- **두 turn으로 검증된 출력.** 작성과 채점을 별개의 Claude turn으로 나누고 5차원 JSON 점수를 함께 보여줍니다.
- **구독으로만 동작.** 별도 API 키나 결제 없이 이미 가진 Claude Code 구독으로 돌아갑니다.

## 작동 방식

경험들은 frontmatter가 붙은 평범한 마크다운 파일들입니다. 모든 entity가 하나의 파일이 됩니다. Entity 타입은 15개입니다. person, company, role, project, achievement, skill, education, certificate, publication, volunteer, language, document, meeting, decision, topic. Entity 사이의 관계는 frontmatter 안의 link로 저장되며, schema가 어떤 타입에서 어떤 타입으로 연결될 수 있는지 검증합니다.

렌더 요청이 들어오면 LockedIn은 경험을 조회하고, 한 Claude turn에서 초안을 작성한 뒤, 별도의 Claude turn에서 calibrated 평가표 기준으로 초안을 검토합니다. 두 turn을 분리하는 이유는 자기 평가의 편향을 막기 위해서입니다. 같은 Claude 호출이 글을 쓰면서 동시에 자기 글을 채점하면, 자신에게 후한 점수를 주는 경향이 있습니다 (실측 약 1점 부풀림). 그래서 작성 호출과 검토 호출을 별개의 Claude turn으로 나누고, 검토 turn은 평가표를 처음부터 다시 로드합니다.

vault 루트인 `~/Documents/LockedIn/`에는 `EXPERIENCE.md`라는 마스터 파일이 자동으로 갱신됩니다. 사람, 회사, 역할, 프로젝트처럼 타입별로 나뉜 폴더를 매번 열어보지 않고 전체 내용을 한 번에 훑을 수 있습니다. 사용자가 직접 마크다운을 편집한 뒤에 마스터 파일이 stale해 보이면 `lockedin refresh`로 다시 모을 수 있습니다.

LockedIn은 사용자가 이미 가진 Claude Code 구독으로 동작합니다. Anthropic API key가 필요하지 않으며, 어떤 데이터도 외부로 전송하지 않습니다.

## 스킬

| 스킬 | 역할 |
|---|---|
| `lockedin` | 메인 스킬. 자연어 요청을 적절한 하위 흐름으로 라우팅하고, vault를 채우는 Q&A 인터뷰를 주도하며, ingest와 render 흐름을 조율합니다. |
| `lockedin-render-jaso` | 한국어 자소서 렌더러. 다섯 차원으로 평가합니다. 두괄식, 구조화, 구체성, 표현, 적합성. 여러 출처에서 교차 확인된 진부 표현 사전을 갖고 있고, 작성 turn과 검토 turn을 분리해 평가표를 새로 로드합니다. |
| `lockedin-render-resume-en` | 영문 이력서 렌더러. 다섯 차원으로 평가합니다. metric density, action verb quality, structural adherence, banned phrase cleanliness, persona fit. 빌트인 페르소나는 us-tech-senior, us-tech-mid, pm-product 셋이며, 그 외 직무로 지원할 때도 동작합니다. 5개 평가 차원은 직무에 무관하게 적용되지만, 페르소나 적합성 차원은 빌트인 셋 기준으로 calibrate되어 있어 그 외 직무에서는 채점이 다소 보수적일 수 있습니다. |
| `lockedin-render-interview` | 면접 답변 렌더러. STAR 또는 PAR 구조로, 한 문단당 한 경험을 명시하고 그 사이에 명시적 전환 문장을 둡니다. 다섯 차원으로 평가합니다. clarity, evidence density, persona fit, conciseness, tone. |
| `lockedin-render-ideas` | vault를 바탕으로 다음 프로젝트, 사이드 프로젝트, 커리어 전환 아이디어를 3~5개 surface합니다. 각 아이디어는 한 문단입니다. 한 줄 피치 + 실제 vault entity를 인용한 근거. 다섯 차원으로 평가합니다. feasibility, novelty, evidence ground, scope match, motivation alignment. |

## 문서

| 파일 | 내용 |
|---|---|
| [`docs/architecture.md`](./docs/architecture.md) | 구성 요소가 어떻게 맞물리는지 |
| [`docs/ontology-spec.md`](./docs/ontology-spec.md) | Frontmatter 계약 |
| [`docs/ontology-mapping.md`](./docs/ontology-mapping.md) | JSON Resume, Schema.org, FOAF와의 매핑 |
| [`docs/orchestration.md`](./docs/orchestration.md) | 렌더와 ingest 파이프라인 |
| [`docs/cli.md`](./docs/cli.md) | 선택적인 파워 유저 CLI |
| [`docs/hud.md`](./docs/hud.md) | 상태 표시줄 연동 |

## 라이선스

MIT. [LICENSE](./LICENSE) 참조.
