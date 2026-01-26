"""
Chain Prompts Example
체인 프롬프트 예시
"""

from src.llm.gpt_client import GPTClient
from src.prompt_engineering.chainer import ChainPrompt


def main():
    """체인 프롬프트 예시"""
    
    config = {"api_key": "your-api-key"}
    client = GPTClient(config)
    
    # 체인 생성
    chain = ChainPrompt()
    
    # 1단계: 감정 추출
    chain.add_step(
        "extract_emotion",
        lambda text: f"다음 텍스트에서 주요 감정을 추출하세요 (한 단어로):\n{text}"
    )
    
    # 2단계: 감정 분석
    chain.add_step(
        "analyze_emotion",
        lambda emotion: f"'{emotion}' 감정에 대해 심리학적으로 분석하세요."
    )
    
    # 3단계: 조언 생성
    chain.add_step(
        "generate_advice",
        lambda analysis: f"다음 분석을 바탕으로 공감적인 조언을 생성하세요:\n{analysis}"
    )
    
    # 실행
    user_input = "최근에 친구와 다퉈서 속상하고 화가 나요. 어떻게 해야 할지 모르겠어요."
    results = chain.execute(client, user_input)
    
    # 결과 출력
    print("=== 체인 프롬프트 결과 ===\n")
    print(f"원본 입력: {user_input}\n")
    
    for step_name, step_result in results.items():
        if step_name == "initial_input":
            continue
        print(f"--- {step_name} ---")
        print(f"응답: {step_result['response']}\n")


if __name__ == "__main__":
    main()
