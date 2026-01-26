# Tests 디렉토리

이 디렉토리는 Mind-Log AI의 테스트 코드를 포함합니다.

## 테스트 구조

### 단위 테스트 (Unit Tests)
개별 모듈과 함수를 테스트합니다.

**예시:**
```python
# test_llm_clients.py
import pytest
from src.llm.gpt_client import GPTClient

def test_gpt_client_initialization():
    config = {"api_key": "test-key"}
    client = GPTClient(config)
    assert client is not None

def test_token_counting():
    from src.utils.token_counter import TokenCounter
    counter = TokenCounter()
    assert counter.count_tokens("hello world") > 0
```

### 통합 테스트 (Integration Tests)
여러 컴포넌트 간의 상호작용을 테스트합니다.

**예시:**
```python
# test_integration.py
def test_full_chat_flow():
    # 클라이언트 + 템플릿 + 로거 통합 테스트
    pass
```

### 엔드투엔드 테스트 (E2E Tests)
전체 시스템 워크플로우를 테스트합니다.

## 테스트 실행

### 모든 테스트 실행
```bash
pytest
```

### 특정 테스트 파일 실행
```bash
pytest tests/test_llm_clients.py
```

### 커버리지 포함
```bash
pytest --cov=src --cov-report=html
```

### 상세 출력
```bash
pytest -v
```

## 테스트 작성 가이드

### 1. 테스트 파일 명명
- `test_` 접두사 사용
- 테스트할 모듈명 포함
- 예: `test_prompt_templates.py`

### 2. 테스트 함수 명명
- `test_` 접두사 사용
- 명확한 동작 설명
- 예: `test_load_config_success()`

### 3. 픽스처 사용
```python
import pytest

@pytest.fixture
def mock_client():
    return MockLLMClient(config={})

def test_with_fixture(mock_client):
    assert mock_client.validate_connection()
```

### 4. Mocking
외부 API 호출은 모킹하여 테스트:
```python
from unittest.mock import Mock, patch

@patch('src.llm.gpt_client.openai.ChatCompletion.create')
def test_gpt_call(mock_create):
    mock_create.return_value = {"choices": [{"message": {"content": "test"}}]}
    # 테스트 로직
```

## 테스트 카테고리

### 필수 테스트
- [ ] LLM 클라이언트 초기화
- [ ] 프롬프트 템플릿 로드
- [ ] 에러 핸들링
- [ ] 토큰 카운팅
- [ ] 캐시 동작

### 권장 테스트
- [ ] Rate limiting
- [ ] Few-shot 예시 관리
- [ ] 체인 프롬프트 실행
- [ ] 로깅 동작

## CI/CD 통합

GitHub Actions 예시:
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest
```

## 테스트 품질 목표

- **커버리지**: 최소 80% 이상
- **실행 시간**: 전체 테스트 5분 이내
- **격리**: 각 테스트는 독립적으로 실행 가능
