"""
Chain Prompts Module
체인 프롬프트 관리
"""

from typing import List, Dict, Callable


class ChainPrompt:
    """순차적 프롬프트 체인"""
    
    def __init__(self):
        self.steps: List[Dict] = []
        
    def add_step(self, name: str, prompt_fn: Callable, **kwargs):
        """프롬프트 단계 추가"""
        self.steps.append({
            "name": name,
            "prompt_fn": prompt_fn,
            "kwargs": kwargs
        })
        
    def execute(self, llm_client, initial_input: str) -> Dict:
        """체인 실행"""
        results = {"initial_input": initial_input}
        current_input = initial_input
        
        for step in self.steps:
            # 프롬프트 생성
            prompt = step["prompt_fn"](current_input, **step["kwargs"])
            
            # LLM 호출
            response = llm_client.generate(prompt)
            
            # 결과 저장
            results[step["name"]] = {
                "prompt": prompt,
                "response": response
            }
            
            # 다음 단계 입력으로 사용
            current_input = response
            
        return results


# 예시: 감정 분석 -> 공감 응답 생성 체인
def create_counseling_chain() -> ChainPrompt:
    """상담 체인 생성"""
    chain = ChainPrompt()
    
    # 1단계: 감정 분석
    chain.add_step(
        "emotion_analysis",
        lambda text: f"다음 텍스트에서 표현된 감정을 분석하세요:\n{text}"
    )
    
    # 2단계: 공감 응답 생성
    chain.add_step(
        "empathetic_response",
        lambda emotion: f"다음 감정에 대해 공감적인 응답을 생성하세요:\n{emotion}"
    )
    
    return chain
