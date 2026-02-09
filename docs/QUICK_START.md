# 빠른 시작 가이드

Mind-Log 프로젝트 환경 설정부터 첫 에이전트 개발까지의 가이드입니다.

---

## 1. 환경 설정

### 필수 요구사항

- Python 3.11+
- Git
- PostgreSQL (로컬 또는 Docker)
- Redis (로컬 또는 Docker)

### 저장소 클론 및 초기 설정

```bash
# 저장소 클론
git clone https://github.com/your-org/mind-log.git
cd mind-log

# 가상환경 생성 및 활성화
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows

# 의존성 설치
pip install -r requirements.txt

# 환경변수 설정
cp .env.example .env
# .env 파일을 열어 API 키와 DB 접속 정보를 입력
```

### Docker로 서비스 실행 (선택)

```bash
# PostgreSQL + Redis + Neo4j 한번에 실행
docker compose up -d
```

---

## 2. 프로젝트 이해

### 필수 읽기 문서

| 순서 | 문서 | 내용 |
|------|------|------|
| 1 | CLAUDE.md | 아키텍처 요약, 협업 규칙, API 규약 |
| 2 | docs/PROJECT_STRUCTURE.md | 폴더 구조 및 파일 역할 |
| 3 | docs/GIT_WORKFLOW.md | 브랜치 전략, 커밋 컨벤션 |

### 에이전트 설계 문서

에이전트 상세 설계는 `ProjectDocs/` 폴더에 있습니다:

- `ProjectDocs/INDEX.md` — 마스터 인덱스
- `ProjectDocs/ARCHITECTURE_v4.0.md` — v4.0 아키텍처 명세
- `ProjectDocs/agents/conversation/` — 대화모드 에이전트 13개 상세 문서
- `ProjectDocs/agents/podcast/` — 팟캐스트모드 에이전트 7개 상세 문서

---

## 3. 첫 에이전트 개발

### 에이전트 노드 기본 구조

모든 에이전트는 동일한 시그니처를 따릅니다:

```python
# src/agents/conversation/emotion.py 예시

from src.models.agent_state import AgentState

async def emotion_node(state: AgentState) -> AgentState:
    """Emotion Agent: 사용자 입력의 감정을 분석합니다."""

    # 1. 입력 읽기 (자기 담당 읽기 필드만)
    user_input = state["user_input"]

    # 2. 처리 로직 (LLM 호출 등)
    emotion_vectors = await analyze_emotion(user_input)

    # 3. 출력 쓰기 (자기 담당 쓰기 필드만)
    state["emotion_vectors"] = emotion_vectors

    return state
```

### 개발 절차

```bash
# 1. develop에서 기능 브랜치 생성
git checkout develop
git pull origin develop
git checkout -b feature/analysis-emotion-agent

# 2. 에이전트 구현
# src/agents/conversation/emotion.py 작성

# 3. 테스트 작성
# tests/agents/conversation/test_emotion.py 작성

# 4. 테스트 실행
pytest tests/agents/conversation/test_emotion.py -v

# 5. 린트 확인
black src/agents/conversation/emotion.py
ruff check src/agents/conversation/emotion.py

# 6. 커밋 및 PR
git add src/agents/conversation/emotion.py tests/agents/conversation/test_emotion.py
git commit -m "feat(emotion): Emotion Agent 감정 벡터 분석 구현"
git push origin feature/analysis-emotion-agent
# GitHub에서 PR 생성
```

---

## 4. 개발자별 시작점

### Dev-A (분석 도메인)

시작 에이전트: `Intent Classifier` → `Emotion Agent` → `Context Agent` → `Content Analyzer`

참고 문서:
- `ProjectDocs/agents/conversation/01_intent_classifier.md`
- `ProjectDocs/agents/conversation/03_emotion.md`
- `ProjectDocs/agents/conversation/04_context.md`
- `ProjectDocs/agents/podcast/01_content_analyzer.md`

### Dev-B (추론/생성 도메인)

시작 에이전트: `Memory Agent` → `Knowledge Agent` → `Reasoning Agent` → `Synthesis Agent`

참고 문서:
- `ProjectDocs/agents/conversation/05_memory.md`
- `ProjectDocs/agents/conversation/06_knowledge.md`
- `ProjectDocs/agents/conversation/07_reasoning.md`
- `ProjectDocs/agents/conversation/08_synthesis.md`

### Dev-C (검증/부가 도메인)

시작 에이전트: `Safety Agent` → `Validator Agent` → `Personalization Agent` → `Visualization Agent`

참고 문서:
- `ProjectDocs/agents/conversation/02_safety.md`
- `ProjectDocs/agents/conversation/09_validator.md`
- `ProjectDocs/agents/conversation/10_personalization.md`
- `ProjectDocs/agents/conversation/11_visualization.md`

---

## 5. 테스트 실행

```bash
# 전체 테스트
pytest tests/ -v

# 특정 에이전트 테스트
pytest tests/agents/conversation/test_emotion.py -v

# 통합 테스트
pytest tests/integration/ -v

# 커버리지 포함
pytest tests/ --cov=src --cov-report=html
```

---

*자세한 협업 규칙과 API 규약은 CLAUDE.md를 참조하세요.*
