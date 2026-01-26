# Data 디렉토리

이 디렉토리는 프로젝트의 데이터 파일을 저장합니다.

## 디렉토리 구조

### cache/
- API 응답 캐싱
- 중복 요청 방지로 비용 절감
- JSON 형식으로 저장

**주의:** 이 디렉토리는 `.gitignore`에 포함되어 있습니다.

### prompts/
- 프롬프트 데이터 저장
- 사용자 정의 프롬프트
- 실험용 프롬프트

### outputs/
- AI 생성 결과물 저장
- 대화 로그
- 분석 결과

**주의:** 개인정보가 포함될 수 있으므로 `.gitignore`에 포함되어 있습니다.

### embeddings/
- 텍스트 임베딩 저장
- 벡터 데이터베이스
- 유사도 검색용 데이터

## 사용 방법

### 캐시 사용
```python
from src.utils.cache import Cache

cache = Cache("data/cache")
cache.set("my_key", {"result": "value"})
result = cache.get("my_key")
```

### 출력 저장
```python
import json
from pathlib import Path

output_dir = Path("data/outputs")
output_dir.mkdir(exist_ok=True)

with open(output_dir / "result.json", "w") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
```

## 데이터 관리

### 캐시 정리
캐시가 너무 커지면 주기적으로 정리하세요:
```python
cache.clear()
```

### 데이터 백업
중요한 데이터는 정기적으로 백업하세요.

## 보안

- **개인정보 보호**: 사용자 데이터는 암호화하여 저장
- **접근 제어**: 민감한 데이터에 대한 접근 권한 관리
- **로그 관리**: 개인식별정보(PII)가 로그에 포함되지 않도록 주의
