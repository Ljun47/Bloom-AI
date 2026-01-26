"""
Cache Module
응답 캐싱
"""

import json
import hashlib
from pathlib import Path
from typing import Optional, Any


class Cache:
    """간단한 파일 기반 캐시"""
    
    def __init__(self, cache_dir: str = "data/cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
    def _get_cache_key(self, data: str) -> str:
        """캐시 키 생성"""
        return hashlib.md5(data.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """캐시에서 데이터 조회"""
        cache_file = self.cache_dir / f"{self._get_cache_key(key)}.json"
        if cache_file.exists():
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    
    def set(self, key: str, value: Any):
        """캐시에 데이터 저장"""
        cache_file = self.cache_dir / f"{self._get_cache_key(key)}.json"
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(value, f, ensure_ascii=False, indent=2)
    
    def clear(self):
        """캐시 전체 삭제"""
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink()
