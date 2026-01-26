# Config 디렉토리

이 디렉토리는 프로젝트의 모든 설정 파일을 포함합니다.

## 파일 설명

### model_config.yaml
- AI 모델 관련 설정
- 모델 선택, 파라미터, vLLM/Ollama 설정
- 심리상담 특화 설정
- 안전 설정

### prompt_templates.yaml
- 프롬프트 템플릿 정의
- 시스템 프롬프트 (역할 정의)
- 대화 템플릿
- Few-shot 예시

### logging_config.yaml
- 로깅 설정
- 로그 레벨, 포맷, 핸들러
- 파일 출력 설정

## 사용 방법

```python
import yaml

with open('config/model_config.yaml', 'r') as f:
    config = yaml.safe_load(f)
```

## 주의사항

- API 키와 같은 민감한 정보는 `.env` 파일에 저장하세요
- 설정 파일을 수정한 후에는 애플리케이션을 재시작해야 합니다
