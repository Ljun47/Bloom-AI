"""
Logger Module
로깅 유틸리티
"""

import logging
import logging.config
from pathlib import Path
import yaml


def setup_logging(config_path: str = "config/logging_config.yaml"):
    """로깅 설정 초기화"""
    
    # logs 디렉토리 생성
    Path("logs").mkdir(exist_ok=True)
    
    if Path(config_path).exists():
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            logging.config.dictConfig(config)
    else:
        # 기본 설정
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )


def get_logger(name: str) -> logging.Logger:
    """로거 인스턴스 반환"""
    return logging.getLogger(name)
