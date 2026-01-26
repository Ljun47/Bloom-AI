"""
Few-shot Learning Module
Few-shot 프롬프팅
"""

from typing import List, Dict


class FewShotManager:
    """Few-shot 예시 관리"""
    
    def __init__(self, examples: List[Dict] = None):
        self.examples = examples or []
        
    def add_example(self, user_input: str, assistant_response: str):
        """예시 추가"""
        self.examples.append({
            "user": user_input,
            "assistant": assistant_response
        })
    
    def get_examples_as_messages(self) -> List[Dict]:
        """메시지 형식으로 변환"""
        messages = []
        for example in self.examples:
            messages.append({
                "role": "user",
                "content": example["user"]
            })
            messages.append({
                "role": "assistant",
                "content": example["assistant"]
            })
        return messages
    
    def get_examples_as_text(self) -> str:
        """텍스트 형식으로 변환"""
        text = ""
        for i, example in enumerate(self.examples, 1):
            text += f"예시 {i}:\n"
            text += f"사용자: {example['user']}\n"
            text += f"상담사: {example['assistant']}\n\n"
        return text
