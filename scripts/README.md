# Scripts 디렉토리

이 디렉토리는 유틸리티 스크립트와 실행 스크립트를 포함합니다.

## 스크립트 목적

### 데이터 처리
- 데이터 전처리
- 배치 작업
- 데이터 변환

### 배포
- 모델 배포
- 서버 시작
- 환경 설정

### 유틸리티
- 캐시 정리
- 로그 분석
- 성능 모니터링

## 권장 스크립트

### setup_env.sh
개발 환경 초기 설정
```bash
#!/bin/bash
# 가상환경 생성
python -m venv venv
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt

# 디렉토리 생성
mkdir -p logs data/cache data/outputs

echo "환경 설정 완료"
```

### clean_cache.py
캐시 정리 스크립트
```python
#!/usr/bin/env python
"""캐시 정리 스크립트"""

from pathlib import Path
import shutil

def clean_cache():
    cache_dir = Path("data/cache")
    if cache_dir.exists():
        shutil.rmtree(cache_dir)
        cache_dir.mkdir()
        print("캐시 정리 완료")

if __name__ == "__main__":
    clean_cache()
```

### run_server.sh
서버 실행 스크립트
```bash
#!/bin/bash
# 환경 변수 로드
source .env

# 서버 시작
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

### backup_data.sh
데이터 백업 스크립트
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="backups/$DATE"

mkdir -p $BACKUP_DIR
cp -r data/outputs $BACKUP_DIR/
cp -r logs $BACKUP_DIR/

echo "백업 완료: $BACKUP_DIR"
```

### analyze_logs.py
로그 분석 스크립트
```python
#!/usr/bin/env python
"""로그 분석 스크립트"""

import re
from collections import Counter
from pathlib import Path

def analyze_logs():
    log_file = Path("logs/mind-log.log")
    if not log_file.exists():
        print("로그 파일이 없습니다")
        return
    
    with open(log_file, 'r') as f:
        lines = f.readlines()
    
    # 에러 카운트
    errors = [line for line in lines if 'ERROR' in line]
    warnings = [line for line in lines if 'WARNING' in line]
    
    print(f"총 로그 라인: {len(lines)}")
    print(f"에러: {len(errors)}")
    print(f"경고: {len(warnings)}")

if __name__ == "__main__":
    analyze_logs()
```

## 스크립트 작성 가이드

### 1. Shebang 포함
```python
#!/usr/bin/env python
```

### 2. 실행 권한 부여
```bash
chmod +x script_name.py
```

### 3. 명확한 문서화
```python
"""
스크립트 설명

사용법:
    python script_name.py [options]

옵션:
    --option1: 옵션 설명
"""
```

### 4. 에러 핸들링
```python
try:
    # 작업 수행
    pass
except Exception as e:
    print(f"에러 발생: {e}")
    sys.exit(1)
```

### 5. 로깅
```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("작업 시작")
```

## 사용 예시

### 환경 설정
```bash
bash scripts/setup_env.sh
```

### 캐시 정리
```bash
python scripts/clean_cache.py
```

### 서버 실행
```bash
bash scripts/run_server.sh
```

### 데이터 백업
```bash
bash scripts/backup_data.sh
```

## 자동화

### Cron Job 설정
```bash
# 매일 자정에 백업
0 0 * * * /path/to/mind-log/scripts/backup_data.sh

# 매주 일요일에 캐시 정리
0 0 * * 0 python /path/to/mind-log/scripts/clean_cache.py
```

### systemd 서비스
```ini
[Unit]
Description=Mind-Log AI Service
After=network.target

[Service]
Type=simple
User=username
WorkingDirectory=/path/to/mind-log
ExecStart=/path/to/mind-log/scripts/run_server.sh
Restart=always

[Install]
WantedBy=multi-user.target
```

## 주의사항

- 스크립트에 API 키나 비밀번호를 하드코딩하지 마세요
- 실행 권한을 적절히 관리하세요
- 중요한 작업은 백업을 먼저 수행하세요
- 로그를 남겨 추적 가능하도록 하세요
