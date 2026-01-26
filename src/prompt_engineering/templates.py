"""
Prompt Templates Module
프롬프트 템플릿 관리
"""

from typing import Dict, List
import yaml
from pathlib import Path


class PromptTemplate:
    """프롬프트 템플릿 관리 클래스"""
    
    def __init__(self, config_path: str = "config/prompt_templates.yaml"):
        self.config_path = Path(config_path)
        self.templates = self._load_templates()
        
    def _load_templates(self) -> Dict:
        """템플릿 파일 로드"""
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        return {}
    
    def get_system_prompt(self, role: str = "counselor") -> str:
        """시스템 프롬프트 가져오기"""
        prompts = self.templates.get("system_prompts", {})
        prompt_data = prompts.get(role, {})
        
        role_desc = prompt_data.get("role", "")
        guidelines = prompt_data.get("guidelines", [])
        
        full_prompt = f"{role_desc}\n\n"
        if guidelines:
            full_prompt += "가이드라인:\n"
            for guideline in guidelines:
                full_prompt += f"- {guideline}\n"
                
        return full_prompt
    
    def get_template(self, name: str) -> str:
        """특정 템플릿 가져오기"""
        return self.templates.get("templates", {}).get(name, "")
    
    def get_few_shot_examples(self) -> List[Dict]:
        """Few-shot 예시 가져오기"""
        return self.templates.get("few_shot_examples", [])
    
    def format_prompt(self, template_name: str, **kwargs) -> str:
        """템플릿에 변수 삽입"""
        template = self.get_template(template_name)
        return template.format(**kwargs)
