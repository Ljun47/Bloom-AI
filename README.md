# Mind-Log

> 생성형 AI를 활용한 심리상담 AI 시스템

## 📋 프로젝트 소개

Mind-Log는 생성형 AI 기술을 활용하여 공감적이고 전문적인 심리상담 서비스를 제공하는 AI 프로젝트입니다. 이 저장소는 Mind-Log 프로젝트의 생성형 AI 엔진 부분을 포함하고 있습니다.

### 주요 특징

- 🤖 **다양한 LLM 지원**: GPT-4, Claude, vLLM, Ollama 등
- 💬 **공감적 대화**: 심리상담 특화 프롬프트 엔지니어링
- 🔄 **체인 프롬프트**: 복잡한 상담 워크플로우 구현
- 🎯 **Few-shot 학습**: 고품질 상담 예시 활용
- 📊 **응답 캐싱**: API 비용 최적화
- 🛡️ **안전 장치**: 위기 상황 감지 및 대응

## 🏗️ 프로젝트 구조

```
mind-log/
├── config/                 # 설정 파일
│   ├── model_config.yaml          # 모델 설정
│   ├── prompt_templates.yaml      # 프롬프트 템플릿
│   └── logging_config.yaml        # 로깅 설정
├── src/                    # 소스 코드
│   ├── llm/                       # LLM 클라이언트
│   │   ├── base.py                # 기본 추상 클래스
│   │   ├── claude_client.py       # Claude 클라이언트
│   │   └── gpt_client.py          # GPT 클라이언트
│   ├── prompt_engineering/        # 프롬프트 엔지니어링
│   │   ├── templates.py           # 템플릿 관리
│   │   ├── few_shot.py            # Few-shot 예시
│   │   └── chainer.py             # 체인 프롬프트
│   ├── utils/                     # 유틸리티
│   │   ├── logger.py              # 로깅
│   │   ├── rate_limiter.py        # 속도 제한
│   │   ├── token_counter.py       # 토큰 계산
│   │   └── cache.py               # 캐싱
│   ├── handlers/                  # 에러 핸들링
│   ├── api/                       # API 엔드포인트
│   └── models/                    # AI 모델 관련
├── data/                   # 데이터
│   ├── cache/                     # 캐시 데이터
│   ├── prompts/                   # 프롬프트 데이터
│   ├── outputs/                   # 출력 결과
│   └── embeddings/                # 임베딩 데이터
├── examples/               # 사용 예시
│   ├── basic_completion.py        # 기본 완성
│   ├── chat_session.py            # 채팅 세션
│   └── chain_prompts.py           # 체인 프롬프트
├── notebooks/              # Jupyter 노트북
├── tests/                  # 테스트 코드
├── scripts/                # 실행 스크립트
├── docs/                   # 문서
├── requirements.txt        # Python 의존성
├── setup.py                # 설치 설정
├── Dockerfile              # Docker 이미지
└── README.md               # 프로젝트 문서
```

## 🚀 시작하기

### 필요 조건

- Python 3.8 이상
- pip 또는 conda

### 설치

```bash
# 저장소 클론
git clone https://github.com/your-username/mind-log.git
cd mind-log

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

### 환경 변수 설정

`.env` 파일을 생성하고 API 키를 설정하세요:

```env
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
```

### 기본 사용법

```python
from src.llm.gpt_client import GPTClient
from src.prompt_engineering.templates import PromptTemplate

# 클라이언트 초기화
config = {"api_key": "your-api-key"}
client = GPTClient(config)

# 프롬프트 템플릿 로드
template = PromptTemplate()
system_prompt = template.get_system_prompt("counselor")

# 대화 생성
messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": "요즘 스트레스를 많이 받아요"}
]

response = client.chat(messages)
print(response)
```

더 많은 예시는 [examples/](examples/) 디렉토리를 참고하세요.

## 📚 문서

- [설정 가이드](config/README.md)
- [소스 코드 구조](src/README.md)
- [데이터 관리](data/README.md)
- [사용 예시](examples/README.md)
- [테스트 가이드](tests/README.md)
- [노트북 가이드](notebooks/README.md)
- [스크립트 가이드](scripts/README.md)

## 🧪 테스트

```bash
# 모든 테스트 실행
pytest

# 커버리지 포함
pytest --cov=src --cov-report=html

# 특정 테스트만 실행
pytest tests/test_llm_clients.py
```

## 🐳 Docker

```bash
# 이미지 빌드
docker build -t mind-log:latest .

# 컨테이너 실행
docker run -p 8000:8000 --env-file .env mind-log:latest
```

## 🛠️ 기술 스택

### 언어 및 프레임워크
- **Python 3.8+**: 메인 프로그래밍 언어
- **FastAPI**: API 서버 (예정)

### AI/ML
- **OpenAI GPT**: 주요 언어 모델
- **Anthropic Claude**: 대안 언어 모델
- **vLLM**: 고성능 추론 엔진 (예정)
- **Ollama**: 로컬 LLM 실행 (예정)

### 클라우드 & 배포
- **AWS**: 클라우드 인프라 (예정)
- **Docker**: 컨테이너화

### 개발 도구
- **pytest**: 테스트 프레임워크
- **black**: 코드 포매터
- **flake8**: 린터

## 🗺️ 개발 로드맵

### Phase 1: 기본 기능 (현재)
- [x] 프로젝트 구조 설정
- [x] LLM 클라이언트 인터페이스
- [x] 프롬프트 엔지니어링 도구
- [ ] 기본 API 서버
- [ ] 단위 테스트

### Phase 2: 고급 기능
- [ ] vLLM 통합
- [ ] Ollama 통합
- [ ] 응답 품질 평가
- [ ] 대화 컨텍스트 관리
- [ ] 위기 상황 감지

### Phase 3: 배포 및 최적화
- [ ] AWS 배포
- [ ] 성능 최적화
- [ ] 모니터링 시스템
- [ ] CI/CD 파이프라인

## 🤝 기여

기여는 언제나 환영합니다! 다음 절차를 따라주세요:

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### 코딩 스타일

- PEP 8 준수
- 타입 힌트 사용
- Docstring 작성 (Google 스타일)
- 테스트 코드 포함

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 있습니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 📧 문의

프로젝트 관련 문의사항이 있으시면 이슈를 생성해주세요.

## 🙏 감사의 말

이 프로젝트는 다음 오픈소스 프로젝트들을 참고하였습니다:
- OpenAI API
- Anthropic Claude
- LangChain
- FastAPI

## ⚠️ 주의사항

- 이 프로젝트는 전문적인 의료 또는 정신건강 서비스를 대체하지 않습니다.
- 심각한 정신건강 문제가 있는 경우 전문가의 도움을 받으세요.
- 사용자 데이터는 개인정보 보호 정책에 따라 안전하게 처리됩니다.

---

**Made with ❤️ for better mental health support**
