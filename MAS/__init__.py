"""
Multi-Agent Scaffolding System

Hallo. A modular, experiment-ready prototype of a multi-agent scaffolding system for higher education research.
This system implements a hierarchical multi-agent architecture with a lead/orchestrator agent and
specialized sub-agents, each operationalizing a specific "Design Feature" (DF) and associated scaffolding type.
"""

__version__ = "0.1.0"
__author__ = "Diana Kozachek"

# Lazy import to avoid circular dependencies
def get_system_class():
    """Get the MultiAgentScaffoldingSystem class with lazy import."""
    from .mas_system import MultiAgentScaffoldingSystem
    return MultiAgentScaffoldingSystem

__all__ = [
    'get_system_class'
]
