# Source Code 디렉토리

이 디렉토리는 Mind-Log AI의 핵심 소스 코드를 포함합니다.

## 디렉토리 구조

### llm/
다양한 LLM 제공자와의 통합을 관리합니다.
- `base.py`: LLM 클라이언트 기본 추상 클래스
- `claude_client.py`: Anthropic Claude API 클라이언트
- `gpt_client.py`: OpenAI GPT API 클라이언트
- 추가 예정: vLLM, Ollama 클라이언트

**사용 예시:**
```python
from src.llm.gpt_client import GPTClient

client = GPTClient(config)
response = client.chat(messages)
```

### prompt_engineering/
프롬프트 템플릿 및 엔지니어링 도구
- `templates.py`: 프롬프트 템플릿 관리
- `few_shot.py`: Few-shot 학습 예시 관리
- `chainer.py`: 체인 프롬프트 (순차 실행)

**사용 예시:**
```python
from src.prompt_engineering.templates import PromptTemplate

template = PromptTemplate()
system_prompt = template.get_system_prompt("counselor")
```

### utils/
공통 유틸리티 함수들
- `logger.py`: 로깅 유틸리티
- `rate_limiter.py`: API 호출 속도 제한
- `token_counter.py`: 토큰 수 계산
- `cache.py`: 응답 캐싱
- `utils.py`: 기타 유틸리티

### handlers/
에러 핸들링 및 예외 처리
- `error_handler.py`: 중앙 집중식 에러 핸들러

### api/
API 엔드포인트 (개발 예정)

### models/
AI 모델 관련 코드 (개발 예정)

### prompts/
추가 프롬프트 관리 (개발 예정)

## 개발 가이드

### 새로운 LLM 클라이언트 추가
1. `llm/base.py`의 `BaseLLMClient`를 상속
2. `generate()`, `chat()`, `validate_connection()` 메서드 구현

### 새로운 프롬프트 템플릿 추가
1. `config/prompt_templates.yaml`에 템플릿 정의
2. `PromptTemplate` 클래스로 로드하여 사용
