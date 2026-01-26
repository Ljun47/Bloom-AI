# Examples 디렉토리

이 디렉토리는 Mind-Log AI의 사용 예시를 포함합니다.

## 예시 파일

### basic_completion.py
기본적인 텍스트 생성 예시
- 단일 프롬프트로 응답 생성
- 프롬프트 템플릿 사용
- 기본 설정

**실행:**
```bash
python examples/basic_completion.py
```

### chat_session.py
대화 세션 관리 예시
- 멀티턴 대화
- 대화 히스토리 관리
- 컨텍스트 유지

**실행:**
```bash
python examples/chat_session.py
```

### chain_prompts.py
체인 프롬프트 예시
- 순차적 프롬프트 실행
- 단계별 결과 활용
- 복잡한 작업 분해

**실행:**
```bash
python examples/chain_prompts.py
```

## 사용 전 준비

1. **API 키 설정**
```bash
export OPENAI_API_KEY="your-api-key"
export ANTHROPIC_API_KEY="your-api-key"
```

또는 `.env` 파일 생성:
```
OPENAI_API_KEY=your-api-key
ANTHROPIC_API_KEY=your-api-key
```

2. **의존성 설치**
```bash
pip install -r requirements.txt
```

## 새로운 예시 추가

새로운 예시를 추가할 때는:
1. 명확한 주석과 설명 포함
2. 에러 핸들링 구현
3. README에 예시 설명 추가

## 학습 순서

1. `basic_completion.py` - 기본 개념 이해
2. `chat_session.py` - 대화 관리 학습
3. `chain_prompts.py` - 고급 기법 학습
