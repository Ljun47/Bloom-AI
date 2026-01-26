"""
Chat Session Example
대화 세션 예시
"""

from src.llm.claude_client import ClaudeClient
from src.prompt_engineering.templates import PromptTemplate
from src.utils.logger import setup_logging, get_logger

# 로깅 설정
setup_logging()
logger = get_logger(__name__)


class ChatSession:
    """채팅 세션 관리"""
    
    def __init__(self, client, template):
        self.client = client
        self.template = template
        self.history = []
        
        # 시스템 프롬프트 추가
        system_prompt = template.get_system_prompt("counselor")
        self.history.append({
            "role": "system",
            "content": system_prompt
        })
        
    def add_message(self, role: str, content: str):
        """메시지 추가"""
        self.history.append({
            "role": role,
            "content": content
        })
        
    def get_response(self, user_input: str) -> str:
        """응답 생성"""
        # 사용자 메시지 추가
        self.add_message("user", user_input)
        
        # 응답 생성
        response = self.client.chat(self.history)
        
        # 어시스턴트 응답 추가
        self.add_message("assistant", response)
        
        logger.info(f"User: {user_input}")
        logger.info(f"Assistant: {response}")
        
        return response


def main():
    """채팅 세션 예시"""
    
    config = {"api_key": "your-api-key"}
    client = ClaudeClient(config)
    template = PromptTemplate()
    
    session = ChatSession(client, template)
    
    # 대화 시뮬레이션
    conversations = [
        "안녕하세요, 상담을 받고 싶어요",
        "요즘 일이 너무 많아서 힘들어요",
        "어떻게 하면 스트레스를 관리할 수 있을까요?"
    ]
    
    for user_input in conversations:
        response = session.get_response(user_input)
        print(f"\n사용자: {user_input}")
        print(f"상담사: {response}")
        print("-" * 50)


if __name__ == "__main__":
    main()
