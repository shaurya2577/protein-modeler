import anthropic
import openai
from typing import Dict, Any, Optional
import json
import time
from tenacity import retry, stop_after_attempt, wait_exponential

from config import settings


class AIExtractor:
    """LLM-powered data extraction for biomedical information"""
    
    def __init__(self):
        self.provider = settings.llm_provider
        self.model = settings.llm_model
        
        if self.provider == "anthropic":
            self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        elif self.provider == "openai":
            self.client = openai.OpenAI(api_key=settings.openai_api_key)
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")
        
        self.cache = {}
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def extract_structured_data(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.3
    ) -> str:
        """Extract structured data using LLM with retry logic"""
        
        # Check cache
        cache_key = f"{prompt}:{system_prompt}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            if self.provider == "anthropic":
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=4096,
                    temperature=temperature,
                    system=system_prompt or "You are a biomedical data extraction expert.",
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                result = response.content[0].text
            
            elif self.provider == "openai":
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})
                
                response = self.client.chat.completions.create(
                    model=self.model or "gpt-4-turbo-preview",
                    messages=messages,
                    temperature=temperature,
                    max_tokens=4096
                )
                result = response.choices[0].message.content
            
            # Cache result
            self.cache[cache_key] = result
            
            # Rate limiting
            time.sleep(0.5)
            
            return result
        
        except Exception as e:
            print(f"Error extracting data: {e}")
            raise
    
    def extract_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """Extract and parse JSON from LLM response"""
        
        full_prompt = f"{prompt}\n\nRespond with valid JSON only. Do not include any other text."
        
        response = self.extract_structured_data(full_prompt, system_prompt)
        
        # Try to extract JSON from response
        try:
            # Find JSON in response (might have markdown code blocks)
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            else:
                json_str = response.strip()
            
            return json.loads(json_str)
        
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON: {e}")
            print(f"Response: {response}")
            return {}


# Global instance
_extractor = None


def get_extractor() -> AIExtractor:
    """Get or create AI extractor instance"""
    global _extractor
    if _extractor is None:
        _extractor = AIExtractor()
    return _extractor

