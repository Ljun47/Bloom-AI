"""
LLM Client Base Module
다양한 LLM 제공자를 위한 기본 클라이언트
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional


class BaseLLMClient(ABC):
    """LLM 클라이언트의 기본 추상 클래스"""
    
    def __init__(self, config: Dict):
        self.config = config
        
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """텍스트 생성"""
        pass
    
    @abstractmethod
    def chat(self, messages: List[Dict], **kwargs) -> str:
        """채팅 형식의 대화"""
        pass
    
    @abstractmethod
    def validate_connection(self) -> bool:
        """연결 상태 확인"""
        pass
