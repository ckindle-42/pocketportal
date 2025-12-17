"""
Intelligent Routing System
Provides optimal model selection and execution management
"""

from .model_registry import (
    ModelRegistry,
    ModelMetadata,
    ModelCapability,
    SpeedClass
)

from .model_backends import (
    ModelBackend,
    OllamaBackend,
    LMStudioBackend,
    MLXBackend
)

from .task_classifier import (
    TaskClassifier,
    TaskClassification,
    TaskComplexity,
    TaskCategory
)

from .intelligent_router import (
    IntelligentRouter,
    RoutingStrategy,
    RoutingDecision
)

from .execution_engine import (
    ExecutionEngine,
    ExecutionResult
)

from .response_formatter import ResponseFormatter

__all__ = [
    # Registry
    'ModelRegistry',
    'ModelMetadata',
    'ModelCapability',
    'SpeedClass',
    
    # Backends
    'ModelBackend',
    'OllamaBackend',
    'LMStudioBackend',
    'MLXBackend',
    
    # Classification
    'TaskClassifier',
    'TaskClassification',
    'TaskComplexity',
    'TaskCategory',
    
    # Routing
    'IntelligentRouter',
    'RoutingStrategy',
    'RoutingDecision',
    
    # Execution
    'ExecutionEngine',
    'ExecutionResult',
    
    # Formatting
    'ResponseFormatter',
]
