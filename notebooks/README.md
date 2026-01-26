# Notebooks 디렉토리

이 디렉토리는 실험, 분석, 프로토타이핑을 위한 Jupyter 노트북을 포함합니다.

## 노트북 목적

### 프롬프트 테스트
- 다양한 프롬프트 실험
- A/B 테스트
- 성능 비교

### 응답 분석
- 모델 응답 품질 평가
- 감정 분석 검증
- 패턴 발견

### 모델 실험
- 다양한 모델 비교
- 파라미터 튜닝
- Few-shot 예시 최적화

## 권장 노트북 구조

### 1. 프롬프트 테스팅 노트북
```markdown
# Prompt Testing - [날짜]

## 목적
실험하려는 프롬프트의 목적 설명

## 설정
- 모델: GPT-4
- Temperature: 0.7
- Max tokens: 2000

## 실험
### 프롬프트 버전 1
[프롬프트 내용]

### 결과
[응답 결과]

### 평가
[평가 내용]

## 결론
[실험 결과 요약]
```

### 2. 응답 분석 노트북
```python
import pandas as pd
import matplotlib.pyplot as plt

# 응답 데이터 로드
responses = pd.read_json('data/outputs/responses.json')

# 분석
# ...

# 시각화
# ...
```

### 3. 모델 비교 노트북
```python
from src.llm.gpt_client import GPTClient
from src.llm.claude_client import ClaudeClient

# 동일한 프롬프트로 여러 모델 테스트
# 결과 비교 및 분석
```

## 사용 방법

### Jupyter 설치
```bash
pip install jupyter notebook
```

### 노트북 실행
```bash
jupyter notebook
```

### JupyterLab 사용 (권장)
```bash
pip install jupyterlab
jupyter lab
```

## 노트북 작성 가이드

### 1. 명확한 제목과 설명
```markdown
# [실험명] - [날짜]
**목적:** 이 노트북의 목적을 한 문장으로
**작성자:** 이름
```

### 2. 셀 구성
- 설명 셀과 코드 셀을 적절히 배치
- 각 단계에 주석 추가
- 중간 결과 출력으로 확인

### 3. 재현 가능성
- 사용한 패키지 버전 명시
- 랜덤 시드 고정
- 데이터 경로 명확히 지정

### 4. 시각화
```python
import matplotlib.pyplot as plt
import seaborn as sns

plt.figure(figsize=(10, 6))
# 시각화 코드
plt.show()
```

## 노트북 관리

### 버전 관리
- 중요한 실험은 날짜를 포함한 이름으로 저장
- 예: `prompt_testing_2024_01_26.ipynb`

### 정리
- 완료된 실험은 `archive/` 폴더로 이동
- 결과는 문서화하여 `docs/`에 정리

### 공유
- 노트북을 공유할 때는 출력을 포함하여 저장
- 민감한 정보 (API 키 등) 제거

## 추천 노트북 주제

1. **prompt_testing.ipynb** - 프롬프트 A/B 테스트
2. **response_analysis.ipynb** - 응답 품질 분석
3. **model_experimentation.ipynb** - 모델 비교 실험
4. **few_shot_optimization.ipynb** - Few-shot 예시 최적화
5. **emotion_analysis.ipynb** - 감정 분석 검증

## 환경 설정

### 커널 생성
```bash
python -m ipykernel install --user --name=mind-log --display-name "Mind-Log"
```

### 필요한 패키지
```bash
pip install jupyter pandas matplotlib seaborn plotly
```

## 주의사항

- ⚠️ 노트북에 API 키를 직접 입력하지 마세요
- ⚠️ 대용량 출력은 저장 전에 정리하세요
- ⚠️ 실험 데이터는 정기적으로 백업하세요
