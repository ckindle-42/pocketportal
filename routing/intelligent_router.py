"""
Intelligent Router - Model selection based on task analysis
"""

import logging
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from enum import Enum

from .model_registry import ModelRegistry, ModelMetadata, ModelCapability, SpeedClass
from .task_classifier import TaskClassifier, TaskClassification, TaskComplexity, TaskCategory

logger = logging.getLogger(__name__)


class RoutingStrategy(Enum):
    """Available routing strategies"""
    AUTO = "auto"                    # Balanced automatic selection
    SPEED = "speed"                  # Prioritize fastest response
    QUALITY = "quality"              # Prioritize best quality
    BALANCED = "balanced"            # Balance speed and quality
    COST_OPTIMIZED = "cost_optimized"  # Minimize resource usage


@dataclass
class RoutingDecision:
    """Result of routing decision"""
    model_id: str
    model_metadata: ModelMetadata
    classification: TaskClassification
    strategy_used: RoutingStrategy
    fallback_models: List[str]
    reasoning: str


class IntelligentRouter:
    """
    Routes queries to optimal models based on task classification
    
    Supports multiple strategies and automatic fallback selection
    """
    
    def __init__(self, registry: ModelRegistry, strategy: RoutingStrategy = RoutingStrategy.AUTO):
        self.registry = registry
        self.strategy = strategy
        self.classifier = TaskClassifier()

        # Verify model availability on initialization
        self._verify_model_preferences()
    
    def route(self, query: str, max_cost: float = 1.0) -> RoutingDecision:
        """
        Route query to optimal model
        
        Args:
            query: User query
            max_cost: Maximum cost factor (0.0-1.0)
            
        Returns:
            RoutingDecision with selected model and fallbacks
        """
        
        # Classify the task
        classification = self.classifier.classify(query)
        
        # Select model based on strategy
        if self.strategy == RoutingStrategy.AUTO:
            model = self._route_auto(classification, max_cost)
        elif self.strategy == RoutingStrategy.SPEED:
            model = self._route_speed(classification)
        elif self.strategy == RoutingStrategy.QUALITY:
            model = self._route_quality(classification, max_cost)
        elif self.strategy == RoutingStrategy.BALANCED:
            model = self._route_balanced(classification, max_cost)
        elif self.strategy == RoutingStrategy.COST_OPTIMIZED:
            model = self._route_cost_optimized(classification)
        else:
            model = self._route_auto(classification, max_cost)
        
        # Build fallback chain
        fallbacks = self._build_fallback_chain(model, classification)
        
        # Generate reasoning
        reasoning = self._generate_reasoning(model, classification)
        
        return RoutingDecision(
            model_id=model.model_id,
            model_metadata=model,
            classification=classification,
            strategy_used=self.strategy,
            fallback_models=fallbacks,
            reasoning=reasoning
        )
    
    def _route_auto(self, classification: TaskClassification,
                   max_cost: float) -> ModelMetadata:
        """Automatic balanced routing"""

        # NOTE: These model IDs should match your actual model registry.
        # The routing system will fall back gracefully if specific models are unavailable.
        # To customize: Update these preferences based on your available models.

        # Map complexity to model tiers (prefer size-based selection)
        complexity_model_map = {
            TaskComplexity.TRIVIAL: ["ollama_qwen25_05b", "ollama_qwen25_1.5b"],
            TaskComplexity.SIMPLE: ["ollama_qwen25_1.5b", "ollama_llama32_3b", "ollama_qwen25_7b"],
            TaskComplexity.MODERATE: ["ollama_qwen25_7b", "ollama_qwen25_14b"],
            TaskComplexity.COMPLEX: ["ollama_qwen25_14b", "ollama_qwen25_32b"],
            TaskComplexity.EXPERT: ["ollama_qwen25_32b", "ollama_qwen25_14b"]
        }

        # Get category-specific preferences
        if classification.category == TaskCategory.CODE and classification.requires_code:
            preferred = ["ollama_qwen25_coder", "ollama_deepseek_coder", "ollama_qwen25_14b"]
        else:
            preferred = complexity_model_map.get(
                classification.complexity,
                ["ollama_qwen25_7b"]
            )

        # Find first available model from preferences
        for model_id in preferred:
            model = self.registry.get_model(model_id)
            if model and model.available and model.cost <= max_cost:
                return model

        # If no preferred model available, try capability-based fallback
        if classification.requires_code:
            capability_fallback = self.registry.get_fastest_model(ModelCapability.CODE)
            if capability_fallback and capability_fallback.available:
                logger.info(f"Using capability-based fallback: {capability_fallback.model_id}")
                return capability_fallback

        # Fallback to any available model
        logger.warning("No preferred models available, using fallback")
        return self._get_any_available_model()
    
    def _route_speed(self, classification: TaskClassification) -> ModelMetadata:
        """Route for maximum speed"""
        
        # Get capability based on task
        capability = None
        if classification.requires_code:
            capability = ModelCapability.CODE
        elif classification.requires_math:
            capability = ModelCapability.MATH
        
        fastest = self.registry.get_fastest_model(capability)
        if fastest:
            return fastest
        
        # Fallback to any available
        return self._get_any_available_model()
    
    def _route_quality(self, classification: TaskClassification,
                      max_cost: float) -> ModelMetadata:
        """Route for maximum quality"""
        
        # Determine capability
        if classification.requires_code:
            capability = ModelCapability.CODE
        elif classification.requires_math:
            capability = ModelCapability.MATH
        elif classification.category == TaskCategory.ANALYSIS:
            capability = ModelCapability.REASONING
        else:
            capability = ModelCapability.GENERAL
        
        best = self.registry.get_best_quality_model(capability, max_cost)
        if best:
            return best
        
        return self._get_any_available_model()
    
    def _route_balanced(self, classification: TaskClassification,
                       max_cost: float) -> ModelMetadata:
        """Balanced routing - quality vs speed tradeoff"""
        
        # For simple tasks, prioritize speed
        if classification.complexity in [TaskComplexity.TRIVIAL, TaskComplexity.SIMPLE]:
            return self._route_speed(classification)
        
        # For complex tasks, prioritize quality
        if classification.complexity in [TaskComplexity.COMPLEX, TaskComplexity.EXPERT]:
            return self._route_quality(classification, max_cost)
        
        # For moderate, find middle ground
        return self._route_auto(classification, max_cost * 0.7)
    
    def _route_cost_optimized(self, classification: TaskClassification) -> ModelMetadata:
        """Route for minimum resource usage"""
        
        # Always use smallest model that can handle the task
        all_models = self.registry.get_all_models()
        available = [m for m in all_models if m.available]
        
        if not available:
            return self._get_any_available_model()
        
        # Sort by cost
        available.sort(key=lambda m: m.cost)
        
        # For code tasks, need at least moderate capability
        if classification.requires_code:
            code_capable = [m for m in available if ModelCapability.CODE in m.capabilities]
            if code_capable:
                return code_capable[0]
        
        return available[0]
    
    def _build_fallback_chain(self, primary: ModelMetadata,
                             classification: TaskClassification) -> List[str]:
        """Build fallback model chain"""
        
        fallbacks = []
        all_models = self.registry.get_all_models()
        available = [m for m in all_models if m.available and m.model_id != primary.model_id]
        
        # Sort by quality (descending)
        available.sort(key=lambda m: m.general_quality, reverse=True)
        
        # Add up to 3 fallbacks
        for model in available[:3]:
            fallbacks.append(model.model_id)
        
        return fallbacks
    
    def _get_any_available_model(self) -> ModelMetadata:
        """Get any available model as last resort"""
        all_models = self.registry.get_all_models()
        available = [m for m in all_models if m.available]
        
        if available:
            return available[0]
        
        # Return first registered model even if marked unavailable
        if all_models:
            return all_models[0]
        
        raise RuntimeError("No models available in registry")
    
    def _verify_model_preferences(self):
        """Verify that preferred models exist in registry and log warnings if not"""

        # All hardcoded model IDs used in routing
        preferred_model_ids = {
            # Complexity-based
            "ollama_qwen25_05b", "ollama_qwen25_1.5b", "ollama_llama32_3b",
            "ollama_qwen25_7b", "ollama_qwen25_14b", "ollama_qwen25_32b",
            # Code-specific
            "ollama_qwen25_coder", "ollama_deepseek_coder"
        }

        missing_models = []
        for model_id in preferred_model_ids:
            model = self.registry.get_model(model_id)
            if not model:
                missing_models.append(model_id)

        if missing_models:
            logger.warning(
                f"Routing preferences reference {len(missing_models)} unavailable models: "
                f"{', '.join(missing_models[:3])}{'...' if len(missing_models) > 3 else ''}. "
                f"Routing will fall back to available models."
            )
        else:
            logger.info("All preferred models found in registry")

    def _generate_reasoning(self, model: ModelMetadata,
                           classification: TaskClassification) -> str:
        """Generate human-readable reasoning for selection"""

        parts = []

        # Complexity
        parts.append(f"Task: {classification.complexity.value} complexity")

        # Category
        parts.append(f"Category: {classification.category.value}")

        # Model choice
        parts.append(f"Selected: {model.display_name}")

        # Speed/quality tradeoff
        parts.append(f"Speed: {model.speed_class.value}")

        return " | ".join(parts)
