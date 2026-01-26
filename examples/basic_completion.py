"""
Basic Completion Example
기본 텍스트 생성 예시
"""

from src.llm.gpt_client import GPTClient
from src.prompt_engineering.templates import PromptTemplate


def main():
    """기본 완성 예시"""
    
    # 설정 로드
    config = {
        "api_key": "your-api-key-here",
        "model": "gpt-4",
        "temperature": 0.7
    }
    
    # 클라이언트 초기화
    client = GPTClient(config)
    
    # 프롬프트 템플릿
    template = PromptTemplate()
    system_prompt = template.get_system_prompt("counselor")
    
    # 사용자 입력
    user_input = "요즘 스트레스를 많이 받아요"
    
    # 메시지 구성
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_input}
    ]
    
    # 응답 생성
    response = client.chat(messages)
    
    print(f"사용자: {user_input}")
    print(f"상담사: {response}")


if __name__ == "__main__":
    main()
