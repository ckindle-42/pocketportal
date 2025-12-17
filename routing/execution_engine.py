"""
Execution Engine - Handles model execution with fallbacks and retries
"""

import asyncio
import logging
import time
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

from .model_registry import ModelRegistry, ModelMetadata
from .model_backends import OllamaBackend, LMStudioBackend, MLXBackend, GenerationResult
from .intelligent_router import IntelligentRouter, RoutingDecision

logger = logging.getLogger(__name__)


@dataclass
class ExecutionResult:
    """Result from query execution"""
    success: bool
    response: str
    model_used: str
    execution_time_ms: float
    tokens_generated: int
    routing_decision: Optional[RoutingDecision] = None
    fallbacks_used: int = 0
    error: Optional[str] = None


class ExecutionEngine:
    """
    Executes queries with intelligent routing and fallback handling
    """
    
    def __init__(self, registry: ModelRegistry, router: IntelligentRouter,
                 config: Optional[Dict[str, Any]] = None):
        self.registry = registry
        self.router = router
        self.config = config or {}
        
        # Initialize backends
        self.backends = {
            'ollama': OllamaBackend(
                base_url=self.config.get('ollama_base_url', 'http://localhost:11434')
            ),
            'lmstudio': LMStudioBackend(
                base_url=self.config.get('lmstudio_base_url', 'http://localhost:1234/v1')
            ),
            'mlx': MLXBackend(
                model_path=self.config.get('mlx_model_path')
            )
        }
        
        # Execution settings
        self.max_retries = self.config.get('max_retries', 3)
        self.timeout_seconds = self.config.get('timeout_seconds', 60)
    
    async def execute(self, query: str, system_prompt: Optional[str] = None,
                     max_tokens: int = 2048, temperature: float = 0.7,
                     max_cost: float = 1.0) -> ExecutionResult:
        """
        Execute query with intelligent routing and fallback
        
        Args:
            query: User query
            system_prompt: Optional system prompt
            max_tokens: Maximum output tokens
            temperature: Generation temperature
            max_cost: Maximum cost factor
            
        Returns:
            ExecutionResult with response or error
        """
        start_time = time.time()
        
        # Get routing decision
        decision = self.router.route(query, max_cost)
        
        # Build model chain (primary + fallbacks)
        model_chain = [decision.model_id] + decision.fallback_models
        
        fallbacks_used = 0
        last_error = None
        
        # Try each model in chain
        for model_id in model_chain:
            try:
                model = self.registry.get_model(model_id)
                if not model:
                    continue
                
                # Get backend
                backend = self.backends.get(model.backend)
                if not backend:
                    logger.warning(f"No backend for {model.backend}")
                    continue
                
                # Check availability
                if not await backend.is_available():
                    logger.warning(f"Backend {model.backend} not available")
                    continue
                
                # Execute generation
                result = await self._execute_with_timeout(
                    backend=backend,
                    model=model,
                    query=query,
                    system_prompt=system_prompt,
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                
                if result.success:
                    elapsed = (time.time() - start_time) * 1000
                    
                    return ExecutionResult(
                        success=True,
                        response=result.text,
                        model_used=model.display_name,
                        execution_time_ms=elapsed,
                        tokens_generated=result.tokens_generated,
                        routing_decision=decision,
                        fallbacks_used=fallbacks_used
                    )
                else:
                    last_error = result.error
                    fallbacks_used += 1
                    logger.warning(f"Model {model_id} failed: {result.error}")
            
            except Exception as e:
                last_error = str(e)
                fallbacks_used += 1
                logger.error(f"Error with model {model_id}: {e}")
        
        # All models failed
        elapsed = (time.time() - start_time) * 1000
        
        return ExecutionResult(
            success=False,
            response="",
            model_used="none",
            execution_time_ms=elapsed,
            tokens_generated=0,
            routing_decision=decision,
            fallbacks_used=fallbacks_used,
            error=f"All models failed. Last error: {last_error}"
        )
    
    async def _execute_with_timeout(self, backend, model: ModelMetadata,
                                   query: str, system_prompt: Optional[str],
                                   max_tokens: int, temperature: float) -> GenerationResult:
        """Execute with timeout handling"""
        
        try:
            result = await asyncio.wait_for(
                backend.generate(
                    prompt=query,
                    model_name=model.api_model_name or model.model_id,
                    system_prompt=system_prompt,
                    max_tokens=max_tokens,
                    temperature=temperature
                ),
                timeout=self.timeout_seconds
            )
            return result
        
        except asyncio.TimeoutError:
            return GenerationResult(
                text="",
                tokens_generated=0,
                time_ms=self.timeout_seconds * 1000,
                model_id=model.model_id,
                success=False,
                error=f"Timeout after {self.timeout_seconds}s"
            )
    
    async def execute_parallel(self, queries: List[str],
                              system_prompt: Optional[str] = None) -> List[ExecutionResult]:
        """Execute multiple queries in parallel"""
        
        tasks = [
            self.execute(query, system_prompt)
            for query in queries
        ]
        
        return await asyncio.gather(*tasks)
    
    async def close(self):
        """Close all backends"""
        for backend in self.backends.values():
            if hasattr(backend, 'close'):
                await backend.close()
    
    async def health_check(self) -> Dict[str, bool]:
        """Check health of all backends"""
        
        health = {}
        
        for name, backend in self.backends.items():
            try:
                health[name] = await backend.is_available()
            except Exception as e:
                health[name] = False
                logger.error(f"Health check failed for {name}: {e}")
        
        return health
