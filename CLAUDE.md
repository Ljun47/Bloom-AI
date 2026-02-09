# CLAUDE.md - Mind-Log AI 프로젝트 가이드

## 프로젝트 개요

**Mind-Log**: 초개인화 AI 멘탈케어 & 시각화 플랫폼

사용자의 감정과 생각을 AI가 분석하여 개인화된 멘탈케어 서비스를 제공하고, 내면 상태를 시각적 이미지로 표현하는 플랫폼.

---

## 아키텍처 요약

### 듀얼모드 시스템

대화모드(실시간 상담)와 팟캐스트모드(에피소드 생성)를 지원하며, LangGraph StateGraph로 동적 오케스트레이션한다.

```
사용자 입력 → Router Agent → [Safety 검사] → [분석 병렬] → [추론/생성] → [검증] → 최종 응답
```

### 에이전트 구성 (14개)

| 도메인 | 에이전트 | 모델 | 담당 개발자 |
|--------|---------|------|------------|
| **분석** | Intent Classifier (Router) | Haiku | Dev-A |
| **분석** | Emotion Agent | Sonnet 4 | Dev-A |
| **분석** | Context Agent | Haiku | Dev-A |
| **분석** | Content Analyzer (팟캐스트) | Sonnet 4 | Dev-A |
| **추론/생성** | Reasoning Agent | Opus 4.5 | Dev-B |
| **추론/생성** | Memory Agent | Sonnet 4 | Dev-B |
| **추론/생성** | Knowledge Agent | Sonnet 4 | Dev-B |
| **추론/생성** | Synthesis Agent | Sonnet 4 | Dev-B |
| **추론/생성** | Script Generator (팟캐스트) | Sonnet 4 | Dev-B |
| **검증/부가** | Safety Agent | Sonnet 4 | Dev-C |
| **검증/부가** | Validator Agent | Sonnet 4 | Dev-C |
| **검증/부가** | Personalization Agent | Sonnet 4 | Dev-C |
| **검증/부가** | Visualization Agent | Sonnet 4 | Dev-C |
| **검증/부가** | Learning Agent / Telemetry | Haiku | Dev-C |

### 실행 흐름

```
Phase 1 (병렬): Safety + Emotion + Context + [Content Analyzer]
Phase 2 (조건부): Memory + Knowledge ← Reasoning이 필요시 호출
Phase 3 (순차): Reasoning → Synthesis [또는 Script Generator]
Phase 4 (검증): Validator ↔ Synthesis (피드백 루프, 최대 3회)
Phase 5 (후처리): Personalization → 최종 응답
Phase 6 (비동기): Visualization + Telemetry + Learning
```

---

## 개발자 협업 규칙

### 개발자별 담당 영역

| 개발자 | 도메인 | 브랜치 접두사 | 에이전트 |
|--------|--------|-------------|---------|
| **Dev-A** | 분석 (Analysis) | `feature/analysis-*` | Router, Emotion, Context, Content Analyzer |
| **Dev-B** | 추론/생성 (Reasoning) | `feature/reasoning-*` | Reasoning, Memory, Knowledge, Synthesis, Script Generator |
| **Dev-C** | 검증/부가 (Validation) | `feature/validation-*` | Safety, Validator, Personalization, Visualization, Learning, Telemetry |

### 브랜치 전략

```
main ← PR 머지 (리뷰 통과 필수)
 └── develop ← 통합 테스트 브랜치
      ├── feature/analysis-*     (Dev-A)
      ├── feature/reasoning-*    (Dev-B)
      └── feature/validation-*   (Dev-C)
```

**규칙:**
- 각 개발자는 자기 도메인 브랜치에서만 작업한다
- `develop`에 머지할 때 최소 1명 이상의 다른 개발자 리뷰 필수
- `main`에 머지할 때 3명 전원 승인 필수
- 공용 파일(AgentState, 메시지 프로토콜 등) 수정 시 **반드시 전원 리뷰**

### 수정 불가 영역 (Protected Files)

아래 파일은 단독 수정 금지. 반드시 3인 합의 후 수정:

- `src/models/agent_state.py` — 공유 상태 스키마
- `src/models/message.py` — 에이전트 간 메시지 포맷
- `src/api/contracts.py` — 백엔드 API 요청/응답 스키마
- `src/graph/workflow.py` — LangGraph 워크플로우 정의

---

## 에이전트 간 입출력 규약

### AgentState (공유 상태)

모든 에이전트는 하나의 `AgentState`를 읽고 쓴다. 각 에이전트는 **자기 담당 필드만 쓰고**, 다른 에이전트 필드는 읽기만 한다.

```python
class AgentState(TypedDict):
    # === 입력 (Router가 설정) ===
    user_input: str
    user_id: str
    session_id: str
    mode: Literal["conversation", "podcast"]

    # === Dev-A 담당 (분석) ===
    intent: dict              # Router → 의도 분류 결과
    emotion_vectors: dict     # Emotion → 감정 벡터
    context: dict             # Context → 대화 맥락
    content_analysis: dict    # Content Analyzer → 팟캐스트 주제 분석

    # === Dev-B 담당 (추론/생성) ===
    memory_results: dict      # Memory → 개인 기억 검색 결과
    knowledge_results: dict   # Knowledge → 전문 지식 검색 결과
    reasoning_result: dict    # Reasoning → GoT/ToT/CoT 추론 결과
    response_draft: str       # Synthesis → 응답 초안
    script_draft: dict        # Script Generator → 팟캐스트 스크립트

    # === Dev-C 담당 (검증/부가) ===
    risk_level: int           # Safety → 위험 레벨 (0-4)
    risk_score: float         # Safety → Risk Score (0.0-1.0)
    safety_flags: dict        # Safety → 안전 플래그
    validation_result: dict   # Validator → 검증 결과
    final_output: str         # Personalization → 최종 응답
    visual_data: dict         # Visualization → 시각화 메타데이터

    # === 제어 ===
    next_step: str            # 워크플로우 라우팅 플래그
    execution_plan: dict      # Router가 결정한 실행 계획
    iteration_count: int      # 피드백 루프 카운터
```

### 필드 접근 규칙

| 개발자 | 쓰기 가능 필드 | 읽기 가능 필드 |
|--------|--------------|--------------|
| Dev-A | intent, emotion_vectors, context, content_analysis | user_input, user_id, session_id, mode |
| Dev-B | memory_results, knowledge_results, reasoning_result, response_draft, script_draft | intent, emotion_vectors, context, content_analysis + Dev-A 읽기 필드 |
| Dev-C | risk_level, risk_score, safety_flags, validation_result, final_output, visual_data | 전체 필드 읽기 가능 |

### 에이전트 간 메시지 포맷

에이전트가 다른 에이전트에게 직접 요청할 때 (예: Reasoning → Memory):

```python
class AgentMessage(TypedDict):
    sender: str           # 발신 에이전트 이름
    receiver: str         # 수신 에이전트 이름
    type: Literal["request", "response", "crisis"]
    payload: dict         # 요청/응답 데이터
    priority: int         # 1(긴급) ~ 5(일반)
    timestamp: str        # ISO 8601
```

**CRISIS 메시지**: Safety Agent가 risk_level ≥ 3 판단 시, 모든 병렬 작업을 중단하고 즉시 위기 대응 경로로 전환.

---

## 백엔드 API 규약

백엔드 서버와는 REST API + JSON으로 통신한다. API 명세는 백엔드 팀이 작성하며, 프론트엔드 AI 파트는 아래 인터페이스를 따른다.

### 저장 API (Save)

```
POST /api/v1/{resource}
Content-Type: application/json

요청 예시:
{
  "user_id": "uuid",
  "session_id": "uuid",
  "type": "conversation | emotion_log | memory | visualization",
  "data": { ... },
  "timestamp": "2026-02-10T12:00:00Z"
}

응답:
{
  "success": true,
  "id": "uuid",
  "message": "saved"
}
```

### 조회 API (Load)

```
GET /api/v1/{resource}?user_id={uuid}&type={type}&limit={n}
Content-Type: application/json

응답:
{
  "success": true,
  "data": [ ... ],
  "total": 10,
  "page": 1
}
```

### 에러 응답 (공통)

```json
{
  "success": false,
  "error": {
    "code": "NOT_FOUND | VALIDATION_ERROR | SERVER_ERROR",
    "message": "상세 에러 메시지"
  }
}
```

### API 연동 원칙

- 모든 API 호출은 `src/api/` 모듈을 통해서만 한다 (직접 HTTP 호출 금지)
- API 스키마 변경은 백엔드 팀과 합의 후 `src/api/contracts.py`에 반영
- 타임아웃: 기본 5초, LLM 관련 30초
- 실패 시 최대 3회 재시도 (exponential backoff)

---

## LangGraph 워크플로우

### 노드 등록 규칙

각 개발자가 만든 에이전트는 LangGraph의 노드로 등록된다. 노드 등록은 `src/graph/workflow.py`에서 통합한다.

```python
# 각 개발자는 자기 에이전트를 함수로 구현
# src/agents/analysis/router.py → router_node(state) -> state
# src/agents/reasoning/reasoning.py → reasoning_node(state) -> state
# src/agents/validation/safety.py → safety_node(state) -> state

# workflow.py에서 통합 (3인 합의 영역)
graph = StateGraph(AgentState)
graph.add_node("router", router_node)         # Dev-A
graph.add_node("safety", safety_node)         # Dev-C
graph.add_node("emotion", emotion_node)       # Dev-A
graph.add_node("reasoning", reasoning_node)   # Dev-B
graph.add_node("synthesis", synthesis_node)    # Dev-B
graph.add_node("validator", validator_node)    # Dev-C
# ... 조건부 엣지, 병렬 그룹 설정
```

### 노드 인터페이스 규칙

모든 에이전트 노드는 동일한 시그니처를 따른다:

```python
async def agent_node(state: AgentState) -> AgentState:
    # 1. 자기 담당 입력 필드 읽기
    # 2. 처리 로직
    # 3. 자기 담당 출력 필드 쓰기
    # 4. next_step 설정 (필요시)
    return state
```

---

## 코딩 컨벤션

- **Python 3.11+**, 타입 힌팅 필수
- **포맷터**: Black + isort
- **린터**: Ruff + mypy
- **테스트**: pytest + pytest-asyncio
- **네이밍**: 에이전트 클래스 `{Name}Agent`, 노드 함수 `{name}_node`, 상태 키 `snake_case`
- **커밋**: `feat:`, `fix:`, `docs:`, `refactor:`, `test:` 접두사 사용

---

## 기술 스택

| 구분 | 기술 |
|------|------|
| LLM | Anthropic Claude (Opus 4.5, Sonnet 4, Haiku) |
| 오케스트레이션 | LangGraph StateGraph |
| 벡터 DB | Pinecone / pgvector |
| 관계형 DB | PostgreSQL |
| 그래프 DB | Neo4j |
| 캐시 | Redis |
| 이미지 저장 | S3 / CDN |
| 프레임워크 | FastAPI + Uvicorn |
| CI/CD | GitHub Actions |

---

## 참고 문서

- `docs/GIT_WORKFLOW.md` — 브랜치/커밋/PR 상세 가이드
- `docs/PROJECT_STRUCTURE.md` — 디렉토리 구조 설명
- `docs/QUICK_START.md` — 환경 설정 및 빠른 시작
- ProjectDocs/INDEX.md — 에이전트 상세 설계 문서 (20개 에이전트)
- ProjectDocs/ARCHITECTURE_v4.0.md — v4.0 아키텍처 명세
- ProjectDocs/AGENT_MESSAGE_PROTOCOL_v1.0.md — 메시지 프로토콜 상세

---

*마지막 업데이트: 2026-02-10*
