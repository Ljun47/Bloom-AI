# Mind-Log 프로젝트 구조 가이드

## 📁 전체 디렉토리 구조

```
mind-log/
├── .env.example              # 환경 변수 템플릿
├── .gitignore                # Git 무시 파일
├── Dockerfile                # Docker 이미지 정의
├── README.md                 # 프로젝트 메인 문서
├── requirements.txt          # Python 의존성
├── setup.py                  # 패키지 설치 설정
│
├── config/                   # 설정 파일 디렉토리
│   ├── README.md            # 설정 가이드
│   ├── model_config.yaml    # 모델 설정
│   ├── prompt_templates.yaml # 프롬프트 템플릿
│   └── logging_config.yaml  # 로깅 설정
│
├── src/                      # 소스 코드 디렉토리
│   ├── README.md            # 소스 코드 가이드
│   ├── __init__.py
│   │
│   ├── llm/                 # LLM 클라이언트
│   │   ├── __init__.py
│   │   ├── base.py          # 추상 기본 클래스
│   │   ├── claude_client.py # Claude API
│   │   └── gpt_client.py    # OpenAI API
│   │
│   ├── prompt_engineering/  # 프롬프트 엔지니어링
│   │   ├── __init__.py
│   │   ├── templates.py     # 템플릿 관리
│   │   ├── few_shot.py      # Few-shot 예시
│   │   └── chainer.py       # 체인 프롬프트
│   │
│   ├── utils/               # 유틸리티 함수
│   │   ├── __init__.py
│   │   ├── logger.py        # 로깅
│   │   ├── rate_limiter.py  # 속도 제한
│   │   ├── token_counter.py # 토큰 계산
│   │   ├── cache.py         # 캐싱
│   │   └── utils.py         # 기타 유틸
│   │
│   ├── handlers/            # 에러 핸들링
│   │   ├── __init__.py
│   │   └── error_handler.py # 에러 처리
│   │
│   ├── api/                 # API 엔드포인트 (개발 예정)
│   ├── models/              # AI 모델 관련 (개발 예정)
│   └── prompts/             # 프롬프트 관리 (개발 예정)
│
├── data/                     # 데이터 디렉토리
│   ├── README.md            # 데이터 가이드
│   ├── cache/               # API 응답 캐시
│   ├── prompts/             # 프롬프트 데이터
│   ├── outputs/             # 생성 결과물
│   └── embeddings/          # 임베딩 데이터
│
├── examples/                 # 사용 예시
│   ├── README.md            # 예시 가이드
│   ├── basic_completion.py  # 기본 완성
│   ├── chat_session.py      # 채팅 세션
│   └── chain_prompts.py     # 체인 프롬프트
│
├── notebooks/                # Jupyter 노트북
│   └── README.md            # 노트북 가이드
│
├── tests/                    # 테스트 코드
│   ├── README.md            # 테스트 가이드
│   └── __init__.py
│
├── scripts/                  # 실행 스크립트
│   └── README.md            # 스크립트 가이드
│
└── docs/                     # 추가 문서
    └── README.md            # 문서 가이드
```

## 🎯 주요 컴포넌트 설명

### 1. LLM 클라이언트 (`src/llm/`)
다양한 LLM 제공자와의 통합을 담당합니다.

**주요 파일:**
- `base.py`: 모든 LLM 클라이언트의 기본 인터페이스
- `claude_client.py`: Anthropic Claude 통합
- `gpt_client.py`: OpenAI GPT 통합

**사용 예시:**
```python
from src.llm.gpt_client import GPTClient
client = GPTClient(config)
response = client.chat(messages)
```

### 2. 프롬프트 엔지니어링 (`src/prompt_engineering/`)
효과적인 프롬프트 관리 및 최적화를 위한 도구입니다.

**주요 파일:**
- `templates.py`: YAML 파일에서 프롬프트 템플릿 로드
- `few_shot.py`: Few-shot 학습 예시 관리
- `chainer.py`: 순차적 프롬프트 체인 실행

**사용 예시:**
```python
from src.prompt_engineering.templates import PromptTemplate
template = PromptTemplate()
system_prompt = template.get_system_prompt("counselor")
```

### 3. 유틸리티 (`src/utils/`)
공통적으로 사용되는 헬퍼 함수들입니다.

**주요 기능:**
- 로깅 설정 및 관리
- API 호출 속도 제한
- 토큰 수 계산
- 응답 캐싱
- 기타 유틸리티 함수

### 4. 설정 파일 (`config/`)
프로젝트의 모든 설정을 중앙 관리합니다.

**파일 구성:**
- `model_config.yaml`: AI 모델 파라미터
- `prompt_templates.yaml`: 프롬프트 템플릿
- `logging_config.yaml`: 로깅 설정

### 5. 데이터 관리 (`data/`)
프로젝트에서 생성되고 사용되는 모든 데이터를 저장합니다.

**디렉토리 구성:**
- `cache/`: API 응답 캐시 (비용 절감)
- `prompts/`: 실험용 프롬프트 데이터
- `outputs/`: AI 생성 결과물
- `embeddings/`: 텍스트 임베딩

## 🔄 워크플로우

### 기본 대화 워크플로우
```
사용자 입력 
    ↓
프롬프트 템플릿 로드 (prompt_engineering)
    ↓
LLM 클라이언트 호출 (llm)
    ↓
응답 생성 및 캐싱 (utils)
    ↓
에러 핸들링 (handlers)
    ↓
결과 반환
```

### 개발 워크플로우
```
1. 프롬프트 실험 (notebooks/)
2. 코드 작성 (src/)
3. 예시 작성 (examples/)
4. 테스트 작성 (tests/)
5. 문서 업데이트 (docs/)
```

## 📝 코딩 컨벤션

### 파일 명명
- Python 파일: `snake_case.py`
- 클래스: `PascalCase`
- 함수/변수: `snake_case`
- 상수: `UPPER_CASE`

### 디렉토리 명명
- 소문자 사용
- 언더스코어로 단어 구분
- 복수형 사용 (예: `utils`, `examples`)

### Import 순서
```python
# 1. 표준 라이브러리
import os
import sys

# 2. 서드파티 라이브러리
import yaml
import openai

# 3. 로컬 모듈
from src.llm.base import BaseLLMClient
from src.utils.logger import get_logger
```

## 🚀 시작 체크리스트

- [ ] Python 3.8+ 설치 확인
- [ ] 가상환경 생성 및 활성화
- [ ] `pip install -r requirements.txt` 실행
- [ ] `.env.example`을 복사하여 `.env` 생성
- [ ] API 키 설정
- [ ] `examples/basic_completion.py` 실행 테스트
- [ ] 프로젝트 구조 이해

## 📚 다음 단계

1. **예시 실행**: `examples/` 디렉토리의 예시들을 실행해보세요
2. **노트북 탐색**: `notebooks/`에서 프롬프트 실험을 시작하세요
3. **문서 읽기**: 각 디렉토리의 `README.md`를 확인하세요
4. **기여하기**: 새로운 기능을 추가하거나 개선하세요

## 💡 팁

- 개발 시작 전에 항상 최신 코드를 pull 받으세요
- 새로운 기능은 feature 브랜치에서 개발하세요
- 커밋 전에 테스트를 실행하세요
- 코드 리뷰를 요청하세요

## 🔗 유용한 링크

- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Anthropic Claude Documentation](https://docs.anthropic.com)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [Pytest Documentation](https://docs.pytest.org)
