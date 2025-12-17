"""
Cloud LLM Backends - OpenAI and Anthropic Adapters
==================================================

Provides backend adapters for cloud LLM providers.
These follow the same interface as local backends (Ollama, LM Studio, MLX)
so they can be used interchangeably.

Supported:
- OpenAI (GPT-4, GPT-3.5)
- Anthropic (Claude 3.5 Sonnet, Claude 3 Opus/Sonnet/Haiku)

Configuration via .env:
  OPENAI_API_KEY=your_key
  ANTHROPIC_API_KEY=your_key
"""

import asyncio
import logging
import os
from typing import Optional
import aiohttp

logger = logging.getLogger(__name__)


class CloudBackend:
    """Base class for cloud LLM backends"""
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=120)
            )
        return self.session
    
    async def close(self):
        """Close session"""
        if self.session and not self.session.closed:
            await self.session.close()


class OpenAIBackend(CloudBackend):
    """
    OpenAI API backend
    
    Supports: GPT-4, GPT-4 Turbo, GPT-3.5 Turbo
    
    Models:
      - gpt-4-turbo-preview: Latest GPT-4 Turbo
      - gpt-4: GPT-4
      - gpt-3.5-turbo: GPT-3.5 Turbo
    """
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__()
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY in .env")
        
        self.base_url = "https://api.openai.com/v1"
    
    async def generate(
        self,
        prompt: str,
        model_name: str = "gpt-4-turbo-preview",
        system_prompt: Optional[str] = None,
        max_tokens: int = 2048,
        temperature: float = 0.7
    ) -> dict:
        """
        Generate completion using OpenAI API
        
        Returns:
            {
                'content': str,
                'model': str,
                'tokens': int,
                'finish_reason': str
            }
        """
        import time
        start_time = time.time()
        
        try:
            session = await self._get_session()
            
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            payload = {
                "model": model_name,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            async with session.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    elapsed = (time.time() - start_time) * 1000
                    
                    return {
                        'content': data['choices'][0]['message']['content'],
                        'model': data['model'],
                        'tokens': data.get('usage', {}).get('total_tokens', 0),
                        'finish_reason': data['choices'][0]['finish_reason'],
                        'elapsed_ms': elapsed
                    }
                else:
                    error_text = await response.text()
                    logger.error(f"OpenAI API error: {response.status} - {error_text}")
                    raise Exception(f"OpenAI API returned {response.status}")
        
        except Exception as e:
            logger.error(f"OpenAI generation error: {e}")
            raise
    
    async def is_available(self) -> bool:
        """Check if OpenAI API is available"""
        try:
            session = await self._get_session()
            headers = {"Authorization": f"Bearer {self.api_key}"}
            
            async with session.get(
                f"{self.base_url}/models",
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                return response.status == 200
        except Exception:
            return False


class AnthropicBackend(CloudBackend):
    """
    Anthropic API backend
    
    Supports: Claude 3.5 Sonnet, Claude 3 Opus/Sonnet/Haiku
    
    Models:
      - claude-3-5-sonnet-20241022: Claude 3.5 Sonnet (latest)
      - claude-3-opus-20240229: Claude 3 Opus (most capable)
      - claude-3-sonnet-20240229: Claude 3 Sonnet (balanced)
      - claude-3-haiku-20240307: Claude 3 Haiku (fast)
    """
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__()
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API key not found. Set ANTHROPIC_API_KEY in .env")
        
        self.base_url = "https://api.anthropic.com/v1"
        self.api_version = "2023-06-01"
    
    async def generate(
        self,
        prompt: str,
        model_name: str = "claude-3-5-sonnet-20241022",
        system_prompt: Optional[str] = None,
        max_tokens: int = 2048,
        temperature: float = 0.7
    ) -> dict:
        """
        Generate completion using Anthropic API
        
        Returns:
            {
                'content': str,
                'model': str,
                'tokens': int,
                'stop_reason': str
            }
        """
        import time
        start_time = time.time()
        
        try:
            session = await self._get_session()
            
            payload = {
                "model": model_name,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }
            
            if system_prompt:
                payload["system"] = system_prompt
            
            headers = {
                "x-api-key": self.api_key,
                "anthropic-version": self.api_version,
                "Content-Type": "application/json"
            }
            
            async with session.post(
                f"{self.base_url}/messages",
                json=payload,
                headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    elapsed = (time.time() - start_time) * 1000
                    
                    return {
                        'content': data['content'][0]['text'],
                        'model': data['model'],
                        'tokens': data.get('usage', {}).get('input_tokens', 0) + 
                                 data.get('usage', {}).get('output_tokens', 0),
                        'stop_reason': data['stop_reason'],
                        'elapsed_ms': elapsed
                    }
                else:
                    error_text = await response.text()
                    logger.error(f"Anthropic API error: {response.status} - {error_text}")
                    raise Exception(f"Anthropic API returned {response.status}")
        
        except Exception as e:
            logger.error(f"Anthropic generation error: {e}")
            raise
    
    async def is_available(self) -> bool:
        """Check if Anthropic API is available"""
        try:
            # Anthropic doesn't have a dedicated health endpoint
            # Try a minimal request to check
            await self.generate(
                prompt="test",
                max_tokens=1
            )
            return True
        except Exception:
            return False


# ============================================================================
# MODEL REGISTRY ADDITIONS
# ============================================================================

# Add these to your model_registry.py to enable cloud models:

OPENAI_MODELS = [
    {
        'model_id': 'openai_gpt4_turbo',
        'backend': 'openai',
        'display_name': 'GPT-4 Turbo',
        'api_model_name': 'gpt-4-turbo-preview',
        'context_window': 128000,
        'capabilities': ['general', 'code', 'reasoning', 'vision'],
        'cost': 0.9  # Relative cost
    },
    {
        'model_id': 'openai_gpt4',
        'backend': 'openai',
        'display_name': 'GPT-4',
        'api_model_name': 'gpt-4',
        'context_window': 8192,
        'capabilities': ['general', 'code', 'reasoning'],
        'cost': 0.8
    },
    {
        'model_id': 'openai_gpt35_turbo',
        'backend': 'openai',
        'display_name': 'GPT-3.5 Turbo',
        'api_model_name': 'gpt-3.5-turbo',
        'context_window': 16385,
        'capabilities': ['general', 'code'],
        'cost': 0.3
    }
]

ANTHROPIC_MODELS = [
    {
        'model_id': 'anthropic_claude35_sonnet',
        'backend': 'anthropic',
        'display_name': 'Claude 3.5 Sonnet',
        'api_model_name': 'claude-3-5-sonnet-20241022',
        'context_window': 200000,
        'capabilities': ['general', 'code', 'reasoning', 'vision'],
        'cost': 0.9
    },
    {
        'model_id': 'anthropic_claude3_opus',
        'backend': 'anthropic',
        'display_name': 'Claude 3 Opus',
        'api_model_name': 'claude-3-opus-20240229',
        'context_window': 200000,
        'capabilities': ['general', 'code', 'reasoning', 'vision'],
        'cost': 1.0
    },
    {
        'model_id': 'anthropic_claude3_sonnet',
        'backend': 'anthropic',
        'display_name': 'Claude 3 Sonnet',
        'api_model_name': 'claude-3-sonnet-20240229',
        'context_window': 200000,
        'capabilities': ['general', 'code', 'reasoning'],
        'cost': 0.6
    },
    {
        'model_id': 'anthropic_claude3_haiku',
        'backend': 'anthropic',
        'display_name': 'Claude 3 Haiku',
        'api_model_name': 'claude-3-haiku-20240307',
        'context_window': 200000,
        'capabilities': ['general', 'speed'],
        'cost': 0.2
    }
]


# ============================================================================
# BACKEND FACTORY UPDATE
# ============================================================================

# Add to model_backends.py ModelAdapterFactory.create_adapter():
"""
elif metadata.backend == "openai":
    backend = OpenAIBackend()

elif metadata.backend == "anthropic":
    backend = AnthropicBackend()
"""


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

async def example_usage():
    """Example usage of cloud backends"""
    
    # OpenAI
    print("Testing OpenAI...")
    openai = OpenAIBackend()
    
    if await openai.is_available():
        result = await openai.generate(
            prompt="What is the capital of France?",
            model_name="gpt-3.5-turbo",
            max_tokens=50
        )
        print(f"OpenAI: {result['content']}")
        print(f"Tokens: {result['tokens']}, Time: {result['elapsed_ms']:.0f}ms")
    
    await openai.close()
    
    # Anthropic
    print("\nTesting Anthropic...")
    anthropic = AnthropicBackend()
    
    if await anthropic.is_available():
        result = await anthropic.generate(
            prompt="What is the capital of France?",
            model_name="claude-3-haiku-20240307",
            max_tokens=50
        )
        print(f"Anthropic: {result['content']}")
        print(f"Tokens: {result['tokens']}, Time: {result['elapsed_ms']:.0f}ms")
    
    await anthropic.close()


if __name__ == "__main__":
    asyncio.run(example_usage())
