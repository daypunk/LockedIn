<p align="center">
  <img src="docs/assets/logo.png" alt="LockedIn" width="200" />
</p>

# LockedIn

[English](README.md) | **한국어**

*LinkedIn 가기 전에, Locked In.*

먼저 자기 경험을 안에서 정리하고 나면, 구직이 시작됐을 때 이력서와 자소서와 면접 답변은 빈 페이지를 처음부터 채우는 일이 아니라 정리해 둔 한 곳에 대한 질의가 됩니다.

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

## 왜 만들었나

대부분의 커리어 도구는 산출물을 매번 처음부터 다시 만듭니다. 산출물이 목적이고, 그 기반은 휘발됩니다. LockedIn은 그 순서를 뒤집습니다. 구조화된 경험은 로컬의 `~/Documents/LockedIn/`에 마크다운 파일로 쌓이며, 사용자가 직접 소유하고 다른 도구로 가져갈 수 있습니다. 이력서, 자소서, 회의록은 그 기억에 대한 산출물이지 기억 자체가 아닙니다.

## 아키텍처

<p align="center">
  <img src="docs/assets/architecture.png" alt="LockedIn 아키텍처" width="720" />
</p>

이미지의 레이아웃 레퍼런스는 [`docs/diagram-reference.md`](./docs/diagram-reference.md)에 있습니다.

## 작동 방식

경험들은 frontmatter가 붙은 평범한 마크다운 파일들입니다. 모든 entity가 하나의 파일이 됩니다. Entity 타입은 15개입니다. person, company, role, project, achievement, skill, education, certificate, publication, volunteer, language, document, meeting, decision, topic. Entity 사이의 관계는 frontmatter 안의 link로 저장되며, schema가 어떤 타입에서 어떤 타입으로 연결될 수 있는지 검증합니다.

렌더 요청이 들어오면 LockedIn은 경험을 조회하고, 한 Claude turn에서 초안을 작성한 뒤, 별도의 Claude turn에서 calibrated 평가표 기준으로 초안을 검토합니다. 두 turn을 분리하는 이유는 자기 평가의 편향을 막기 위해서입니다. 같은 Claude 호출이 글을 쓰면서 동시에 자기 글을 채점하면, 자신에게 후한 점수를 주는 경향이 있습니다 (실측 약 1점 부풀림). 그래서 작성 호출과 검토 호출을 별개의 Claude turn으로 나누고, 검토 turn은 평가표를 처음부터 다시 로드합니다.

vault 루트에는 `EXPERIENCE.md` 마스터 파일이 자동으로 갱신됩니다. 모든 entity를 타입별로 묶어 한 곳에 정리하여, per-type 폴더를 일일이 열지 않고도 vault 전체를 한 번에 훑을 수 있습니다.

LockedIn은 사용자가 이미 가진 Claude Code 구독으로 동작합니다. Anthropic API key가 필요하지 않으며, 어떤 데이터도 외부로 전송하지 않습니다.

## 스킬

| 스킬 | 역할 |
|---|---|
| `lockedin` | 메인 스킬. 자연어 요청을 적절한 하위 흐름으로 라우팅하고, vault를 채우는 Q&A 인터뷰를 주도하며, ingest와 render 흐름을 조율합니다. |
| `lockedin-render-jaso` | 한국어 자소서 렌더러. 다섯 차원으로 평가합니다. 두괄식, 구조화, 구체성, 표현, 적합성. 여러 출처에서 교차 확인된 진부 표현 사전을 갖고 있고, 작성 turn과 검토 turn을 분리해 평가표를 새로 로드합니다. |
| `lockedin-render-resume-en` | 영문 이력서 렌더러. 다섯 차원으로 평가합니다. metric density, action verb quality, structural adherence, banned phrase cleanliness, persona fit. 빌트인 페르소나는 us-tech-senior, us-tech-mid, pm-product 셋이며, 그 외 직무로 지원할 때도 동작합니다. 5개 평가 차원은 직무에 무관하게 적용되지만, 페르소나 적합성 차원은 빌트인 셋 기준으로 calibrate되어 있어 그 외 직무에서는 채점이 다소 보수적일 수 있습니다. |

## 문서

| 파일 | 내용 |
|---|---|
| [`docs/architecture.md`](./docs/architecture.md) | 구성 요소가 어떻게 맞물리는지 |
| [`docs/diagram-reference.md`](./docs/diagram-reference.md) | 위 아키텍처 이미지의 ASCII 레퍼런스 |
| [`docs/ontology-spec.md`](./docs/ontology-spec.md) | Frontmatter 계약 |
| [`docs/ontology-mapping.md`](./docs/ontology-mapping.md) | JSON Resume, Schema.org, FOAF와의 매핑 |
| [`docs/orchestration.md`](./docs/orchestration.md) | 렌더와 ingest 파이프라인 |
| [`docs/cli.md`](./docs/cli.md) | 선택적인 파워 유저 CLI |
| [`docs/hud.md`](./docs/hud.md) | 상태 표시줄 연동 |

## License

MIT. [LICENSE](./LICENSE) 참조.
