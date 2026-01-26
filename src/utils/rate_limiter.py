"""
Rate Limiter Module
API 호출 속도 제한
"""

import time
from typing import Dict
from collections import deque


class RateLimiter:
    """API 호출 속도 제한 관리"""
    
    def __init__(self, calls_per_minute: int = 60):
        self.calls_per_minute = calls_per_minute
        self.calls = deque()
        
    def wait_if_needed(self):
        """필요시 대기"""
        now = time.time()
        
        # 1분 이상 지난 호출 제거
        while self.calls and now - self.calls[0] > 60:
            self.calls.popleft()
            
        # 제한 초과시 대기
        if len(self.calls) >= self.calls_per_minute:
            sleep_time = 60 - (now - self.calls[0])
            if sleep_time > 0:
                time.sleep(sleep_time)
                
        self.calls.append(now)
        
    def reset(self):
        """카운터 리셋"""
        self.calls.clear()
