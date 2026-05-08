# selfgraph

[English](README.md) | **한국어**

selfgraph는 Claude Code 안에서 동작하는 플러그인입니다. 사용자의 경력 경험을 구조화된 지식 그래프로 정리하고, 그 그래프를 바탕으로 영문 이력서, 한국어 자소서, 인터랙티브 그래프 뷰를 만듭니다. 시간이 지날수록 그래프가 자라며, 산출물은 항상 그 그래프에 대한 질의로 만들어집니다.

## 설치

Claude Code 안에서 다음 세 명령을 차례로 실행합니다.

```
/plugin marketplace add daypunk/selfgraph
/plugin install selfgraph@selfgraph
/selfgraph:setup
```

세 번째 명령은 한 번만 실행하는 위자드입니다. 채팅 하단의 상태 표시줄을 연결하고, 기본 인터뷰 언어를 선택하고, vault 위치를 정합니다.

## 사용법

selfgraph는 Claude Code에서 자신의 경험에 대해 자연어로 이야기할 때 자동으로 활성화됩니다. 외워야 할 명령은 없습니다.

경험을 기록하고 싶을 때 쓰는 표현:

- "내 경험 정리 시작"
- "오늘 디자인팀 미팅 정리해줘"
- "이 이력서 PDF 흡수해줘"
- "이번 주 LLM 에이전트 논문에서 배운 거 추가"

이미 쌓인 vault에서 산출물을 만들고 싶을 때 쓰는 표현:

- "us-tech-senior 타겟으로 영문 이력서 만들어줘"
- "X 회사 자소서 1번 문항 써줘"
- "지난 분기 의사결정 요약해줘"
- "내 그래프 보여줘"

selfgraph는 추가 정보가 필요할 때 한 번에 한 질문씩만 묻고, 충분해지면 멈춥니다.

## 왜 만들었나

대부분의 커리어 도구는 산출물을 매번 처음부터 다시 만듭니다. 산출물이 목적이고, 그 기반은 잊힙니다. selfgraph는 그 순서를 뒤집습니다. 구조화된 경험은 사용자 디스크의 `~/.selfgraph/`에 마크다운 파일로 쌓이며, 사용자가 직접 소유하고 다른 도구로 가져갈 수 있습니다. 이력서, 자소서, 그래프 시각화는 그 기억에 대한 질의이지 기억 자체가 아닙니다.

## 작동 방식

Vault는 frontmatter가 붙은 평범한 마크다운 파일들입니다. 모든 entity가 하나의 파일이 됩니다. Entity 타입은 15개입니다. person, company, role, project, achievement, skill, education, certificate, publication, volunteer, language, document, meeting, decision, topic. Entity 사이의 관계는 frontmatter 안의 link로 저장되며, schema가 어떤 타입에서 어떤 타입으로 연결될 수 있는지 검증합니다.

렌더 요청이 들어오면 selfgraph는 vault를 조회하고, 한 Claude turn에서 초안을 작성한 뒤, 별도의 Claude turn에서 calibrated 평가표 기준으로 초안을 검토합니다. 두 turn을 분리하는 이유는, 같은 컨텍스트에서 자기 평가를 하면 점수가 약 1점 부풀려진다는 사실 때문입니다.

selfgraph는 사용자가 이미 가진 Claude Code 구독으로 동작합니다. Anthropic API key가 필요하지 않으며, 어떤 데이터도 외부로 전송하지 않습니다.

## 스킬

| 스킬 | 역할 |
|---|---|
| `selfgraph` | 메인 스킬. 자연어 요청을 적절한 하위 흐름으로 라우팅하고, vault를 채우는 Q&A 인터뷰를 주도하며, ingest와 render 흐름을 조율합니다. |
| `selfgraph-render-jaso` | 한국어 자소서 렌더러. 다섯 차원으로 평가합니다. 두괄식, 구조화, 구체성, 표현, 적합성. 여러 출처에서 교차 확인된 진부 표현 사전을 갖고 있고, 작성 turn과 검토 turn을 분리해 평가표를 새로 로드합니다. |
| `selfgraph-render-resume-en` | 영문 이력서 렌더러. 다섯 차원으로 평가합니다. metric density, action verb quality, structural adherence, banned phrase cleanliness, persona fit. 세 가지 페르소나를 지원합니다. us-tech-senior, us-tech-mid, pm-product. |

## 문서

| 파일 | 내용 |
|---|---|
| [`docs/architecture.md`](./docs/architecture.md) | 구성 요소가 어떻게 맞물리는지 |
| [`docs/ontology-spec.md`](./docs/ontology-spec.md) | Frontmatter 계약 |
| [`docs/ontology-mapping.md`](./docs/ontology-mapping.md) | JSON Resume, Schema.org, FOAF와의 매핑 |
| [`docs/orchestration.md`](./docs/orchestration.md) | 렌더와 ingest 파이프라인 |
| [`docs/cli.md`](./docs/cli.md) | 선택적인 파워 유저 CLI |
| [`docs/hud.md`](./docs/hud.md) | 상태 표시줄 연동 |

## License

MIT. [LICENSE](./LICENSE) 참조.
