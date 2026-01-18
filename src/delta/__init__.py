"""
DELTA - Dynamic Environment for LLM Task Automation

Cloud-based sandbox-as-a-service for self-improving LLM agents.
"""

__version__ = "0.1.0"
__author__ = "DELTA Team"

from delta.sdk.client import Delta, DeltaSandbox, DeltaAgent
from delta.sdk.models import AgentConfig, SandboxConfig, TokenBudget

__all__ = [
    "Delta",
    "DeltaSandbox", 
    "DeltaAgent",
    "AgentConfig",
    "SandboxConfig",
    "TokenBudget",
    "__version__",
]
