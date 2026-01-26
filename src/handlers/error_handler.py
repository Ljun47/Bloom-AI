"""
Error Handler Module
에러 핸들링
"""

import logging
from typing import Optional, Callable, Any
from functools import wraps

logger = logging.getLogger(__name__)


class MindLogException(Exception):
    """Mind-Log 기본 예외"""
    pass


class ModelException(MindLogException):
    """모델 관련 예외"""
    pass


class APIException(MindLogException):
    """API 호출 예외"""
    pass


class ConfigException(MindLogException):
    """설정 관련 예외"""
    pass


def handle_errors(fallback_response: Optional[str] = None):
    """에러 핸들링 데코레이터"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except ModelException as e:
                logger.error(f"Model error in {func.__name__}: {str(e)}")
                if fallback_response:
                    return fallback_response
                raise
            except APIException as e:
                logger.error(f"API error in {func.__name__}: {str(e)}")
                if fallback_response:
                    return fallback_response
                raise
            except Exception as e:
                logger.error(f"Unexpected error in {func.__name__}: {str(e)}")
                if fallback_response:
                    return fallback_response
                raise
        return wrapper
    return decorator


class ErrorHandler:
    """중앙 집중식 에러 핸들러"""
    
    def __init__(self):
        self.error_counts = {}
        
    def log_error(self, error_type: str, error: Exception):
        """에러 로깅"""
        logger.error(f"{error_type}: {str(error)}")
        
        # 에러 카운트
        if error_type not in self.error_counts:
            self.error_counts[error_type] = 0
        self.error_counts[error_type] += 1
        
    def get_error_stats(self) -> dict:
        """에러 통계"""
        return self.error_counts.copy()
    
    def reset_stats(self):
        """통계 초기화"""
        self.error_counts.clear()
