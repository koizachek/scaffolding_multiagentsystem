"""
Multi-Agent Scaffolding System - Agents Package

This package contains the agent modules for the multi-agent scaffolding system.
"""

from .base_agent import BaseAgent
from .lead_agent import LeadAgent
from .learner_profiling_agent import LearnerProfilingAgent
from .strategic_scaffolding_agent import StrategicScaffoldingAgent
from .conceptual_scaffolding_agent import ConceptualScaffoldingAgent
from .metacognitive_scaffolding_agent import MetacognitiveScaffoldingAgent
from .procedural_scaffolding_agent import ProceduralScaffoldingAgent
from .example_map_agent import ExampleMapAgent
from .content_ingestion_agent import ContentIngestionAgent
from .agent_factory import create_agent, create_agents_from_config

__all__ = [
    'BaseAgent',
    'LeadAgent',
    'LearnerProfilingAgent',
    'StrategicScaffoldingAgent',
    'ConceptualScaffoldingAgent',
    'MetacognitiveScaffoldingAgent',
    'ProceduralScaffoldingAgent',
    'ExampleMapAgent',
    'ContentIngestionAgent',
    'create_agent',
    'create_agents_from_config'
]
