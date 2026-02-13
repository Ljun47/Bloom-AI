# 프로젝트 구조

Mind-Log 멀티에이전트 AI 시스템의 디렉토리 구조 및 각 파일의 역할을 설명합니다.

---

## 전체 구조

```
mind-log/
│
├── CLAUDE.md                    # AI 개발 통합 가이드 (아키텍처 + 협업 규칙)
├── README.md                    # 프로젝트 소개
├── CONTRIBUTING.md              # 기여 가이드
├── requirements.txt             # Python 의존성
├── Dockerfile                   # Docker 빌드 설정
├── .env.example                 # 환경변수 템플릿
├── .gitignore                   # Git 무시 파일
│
├── src/                         # 소스 코드
│   ├── __init__.py
│   │
│   ├── models/                  # 공유 데이터 모델 (Protected - 3인 합의 필수)
│   │   ├── __init__.py
│   │   ├── agent_state.py       # AgentState TypedDict 정의
│   │   └── message.py           # AgentMessage 통신 프로토콜
│   │
│   ├── agents/                  # 에이전트 구현
│   │   ├── __init__.py
│   │   │
│   │   ├── conversation/        # 대화모드 에이전트 (13개)
│   │   │   ├── __init__.py
│   │   │   ├── intent_classifier.py   # [개발자1] TIER 0: 의도 분류
│   │   │   ├── safety.py              # [개발자2] TIER 1: 안전성 검사
│   │   │   ├── emotion.py             # [개발자2] TIER 1: 감정 분석
│   │   │   ├── context.py             # [개발자3] TIER 1: 맥락 관리
│   │   │   ├── memory.py              # [개발자2] 독립: 개인 기억 검색
│   │   │   ├── knowledge.py           # [개발자1] 독립: 전문 지식 검색
│   │   │   ├── reasoning.py           # [개발자3] TIER 1: 심층 추론
│   │   │   ├── synthesis.py           # [개발자1] TIER 2: 응답 생성
│   │   │   ├── validator.py           # [개발자3] TIER 3: 품질 검증
│   │   │   ├── personalization.py     # [개발자1] TIER 4: 개인화
│   │   │   ├── visualization.py       # [개발자2] 비동기: 시각화
│   │   │   ├── telemetry.py           # [미정] 비동기: 텔레메트리
│   │   │   └── learning.py            # [개발자3] 비동기: 학습
│   │   │
│   │   ├── podcast/             # 팟캐스트모드 에이전트 (7개)
│   │   │   ├── __init__.py
│   │   │   ├── content_analyzer.py    # [개발자3] TIER 1: 콘텐츠 분석
│   │   │   ├── episode_memory.py      # [개발자2] 독립: 에피소드 기억
│   │   │   ├── podcast_reasoning.py   # [개발자3] TIER 1: 팟캐스트 추론
│   │   │   ├── script_generator.py    # [개발자1] TIER 2: 스크립트 생성
│   │   │   ├── batch_validator.py     # [개발자3] TIER 3: 배치 검증
│   │   │   ├── script_personalizer.py # [개발자1] TIER 4: 스크립트 개인화
│   │   │   └── visualization.py       # [개발자2] TIER 2/비동기: 커버 이미지
│   │   │
│   │   └── shared/              # 공용 에이전트 유틸리티
│   │       ├── __init__.py
│   │       ├── base_agent.py    # 에이전트 기본 클래스
│   │       ├── llm_client.py    # 듀얼 LLM 클라이언트 (Anthropic + Bedrock)
│   │       └── message_router.py # 메시지 라우팅 유틸리티
│   │
│   ├── api/                     # 백엔드 API 통신 (Protected - 3인 합의 필수)
│   │   ├── __init__.py
│   │   ├── client.py            # HTTP 클라이언트 (재시도, 타임아웃)
│   │   └── contracts.py         # 요청/응답 스키마 정의
│   │
│   ├── graph/                   # LangGraph 워크플로우 (Protected - 3인 합의 필수)
│   │   ├── __init__.py
│   │   ├── workflow.py          # 메인 StateGraph 정의
│   │   ├── conversation.py      # 대화모드 서브그래프
│   │   └── podcast.py           # 팟캐스트모드 서브그래프
│   │
│   └── utils/                   # 공통 유틸리티
│       ├── __init__.py
│       ├── logger.py            # 로깅 설정
│       ├── cache.py             # 캐시 유틸리티
│       └── retry.py             # 재시도 유틸리티
│
├── config/                      # 환경 설정
│   └── settings.yaml            # 모델, 타임아웃, 기능 플래그 설정
│
├── tests/                       # 테스트 코드
│   ├── __init__.py
│   ├── agents/
│   │   ├── conversation/        # 대화모드 에이전트 단위 테스트
│   │   └── podcast/             # 팟캐스트모드 에이전트 단위 테스트
│   └── integration/             # 통합 테스트 (에이전트 간 연동)
│
├── docs/                        # 프로젝트 문서
│   ├── PROJECT_STRUCTURE.md     # 이 파일
│   ├── GIT_WORKFLOW.md          # 브랜치/커밋/PR 가이드
│   └── QUICK_START.md           # 환경 설정 및 빠른 시작
│
├── .github/
│   ├── workflows/ci.yml         # CI/CD 파이프라인
│   ├── pull_request_template.md # PR 템플릿
│   └── ISSUE_TEMPLATE/          # 이슈 템플릿
│
└── _deprecated/                 # 삭제 예정 파일 보관 (확인 후 삭제)
```

---

## 핵심 디렉토리 설명

### src/models/ — 공유 데이터 모델

모든 에이전트가 사용하는 공통 스키마를 정의합니다. 3명의 개발자 모두에게 영향을 미치므로 **수정 시 전원 리뷰가 필수**입니다.

- `agent_state.py`: LangGraph에서 사용하는 AgentState TypedDict. 각 에이전트의 입출력 필드를 정의.
- `message.py`: 에이전트 간 직접 통신에 사용하는 AgentMessage 포맷.

### src/agents/ — 에이전트 구현

에이전트는 모드별로 분리되어 있으며, 각 파일은 하나의 에이전트 노드를 구현합니다. 모든 에이전트 노드는 동일한 시그니처를 따릅니다: `async def {name}_node(state: AgentState) -> AgentState`

### src/api/ — 백엔드 API 통신

백엔드 서버와의 통신을 담당합니다. 모든 HTTP 호출은 이 모듈을 통해서만 수행합니다.

### src/graph/ — LangGraph 워크플로우

에이전트 노드들을 연결하는 StateGraph를 정의합니다. 대화모드와 팟캐스트모드는 각각 별도의 서브그래프를 가지며, workflow.py에서 통합합니다.

---

## 파일 소유권 규칙

| 표시 | 의미 |
|------|------|
| [개발자1] | 개발자1 소유 (브랜치: feature/analysis-*) |
| [개발자2] | 개발자2 소유 (브랜치: feature/reasoning-*) |
| [개발자3] | 개발자3 소유 (브랜치: feature/validation-*) |
| [미정] | 담당자 미정 (전체 에이전트 완료 후 배정) |
| Protected | 3인 합의 후에만 수정 가능 |

---

*참고: 에이전트 상세 설계는 ProjectDocs/ 폴더의 개별 에이전트 문서를 참조하세요.*
