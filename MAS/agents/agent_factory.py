"""
Agent Factory

This module provides factory functions for creating and configuring agents
in the multi-agent scaffolding system.
"""

import logging
from typing import Dict, List, Any, Optional, Callable

from MAS.agents.base_agent import BaseAgent
from MAS.agents.lead_agent import LeadAgent
from MAS.agents.learner_profiling_agent import LearnerProfilingAgent
from MAS.agents.strategic_scaffolding_agent import StrategicScaffoldingAgent
from MAS.agents.conceptual_scaffolding_agent import ConceptualScaffoldingAgent
from MAS.agents.metacognitive_scaffolding_agent import MetacognitiveScaffoldingAgent
from MAS.agents.procedural_scaffolding_agent import ProceduralScaffoldingAgent
from MAS.agents.example_map_agent import ExampleMapAgent
from MAS.agents.content_ingestion_agent import ContentIngestionAgent

logger = logging.getLogger(__name__)

def create_agent(agent_type: str, 
                name: str, 
                config: Dict[str, Any],
                logger_callback: Optional[Callable] = None) -> Optional[BaseAgent]:
    """
    Create an agent of the specified type.
    
    Args:
        agent_type: Type of agent to create
        name: Name of the agent
        config: Agent configuration
        logger_callback: Callback function for logging
        
    Returns:
        The created agent, or None if the agent type is not recognized
    """
    agent_creators = {
        "lead": create_lead_agent,
        "learner_profiling": create_learner_profiling_agent,
        "strategic_scaffolding": create_strategic_scaffolding_agent,
        "conceptual_scaffolding": create_conceptual_scaffolding_agent,
        "metacognitive_scaffolding": create_metacognitive_scaffolding_agent,
        "procedural_scaffolding": create_procedural_scaffolding_agent,
        "example_map": create_example_map_agent,
        "content_ingestion": create_content_ingestion_agent
    }
    
    creator = agent_creators.get(agent_type)
    if creator:
        return creator(name, config, logger_callback)
    else:
        logger.error(f"Unknown agent type: {agent_type}")
        return None

def create_lead_agent(name: str, 
                     config: Dict[str, Any],
#                     logger_callback: Optional[Callable] = None) -> LeadAgent:
                     logger_callback: Optional[Callable] = None):
    """
    Create a lead agent.
    
    Args:
        name: Name of the agent
        config: Agent configuration
        logger_callback: Callback function for logging
        
    Returns:
        The created lead agent
    """
    logger.info(f"Creating lead agent: {name}")
    return LeadAgent(name, config, logger_callback)

def create_learner_profiling_agent(name: str, 
                                  config: Dict[str, Any],
                                  logger_callback: Optional[Callable] = None) -> LearnerProfilingAgent:
    """
    Create a learner profiling agent.
    
    Args:
        name: Name of the agent
        config: Agent configuration
        logger_callback: Callback function for logging
        
    Returns:
        The created learner profiling agent
    """
    logger.info(f"Creating learner profiling agent: {name}")
    return LearnerProfilingAgent(name, config, logger_callback)

def create_strategic_scaffolding_agent(name: str, 
                                      config: Dict[str, Any],
                                      logger_callback: Optional[Callable] = None) -> StrategicScaffoldingAgent:
    """
    Create a strategic scaffolding agent.
    
    Args:
        name: Name of the agent
        config: Agent configuration
        logger_callback: Callback function for logging
        
    Returns:
        The created strategic scaffolding agent
    """
    logger.info(f"Creating strategic scaffolding agent: {name}")
    return StrategicScaffoldingAgent(name, config, logger_callback)

def create_conceptual_scaffolding_agent(name: str, 
                                       config: Dict[str, Any],
                                       logger_callback: Optional[Callable] = None) -> ConceptualScaffoldingAgent:
    """
    Create a conceptual scaffolding agent.
    
    Args:
        name: Name of the agent
        config: Agent configuration
        logger_callback: Callback function for logging
        
    Returns:
        The created conceptual scaffolding agent
    """
    logger.info(f"Creating conceptual scaffolding agent: {name}")
    return ConceptualScaffoldingAgent(name, config, logger_callback)

def create_metacognitive_scaffolding_agent(name: str, 
                                          config: Dict[str, Any],
                                          logger_callback: Optional[Callable] = None) -> MetacognitiveScaffoldingAgent:
    """
    Create a metacognitive scaffolding agent.
    
    Args:
        name: Name of the agent
        config: Agent configuration
        logger_callback: Callback function for logging
        
    Returns:
        The created metacognitive scaffolding agent
    """
    logger.info(f"Creating metacognitive scaffolding agent: {name}")
    return MetacognitiveScaffoldingAgent(name, config, logger_callback)

def create_procedural_scaffolding_agent(name: str, 
                                       config: Dict[str, Any],
                                       logger_callback: Optional[Callable] = None) -> ProceduralScaffoldingAgent:
    """
    Create a procedural scaffolding agent.
    
    Args:
        name: Name of the agent
        config: Agent configuration
        logger_callback: Callback function for logging
        
    Returns:
        The created procedural scaffolding agent
    """
    logger.info(f"Creating procedural scaffolding agent: {name}")
    return ProceduralScaffoldingAgent(name, config, logger_callback)

def create_example_map_agent(name: str, 
                            config: Dict[str, Any],
                            logger_callback: Optional[Callable] = None) -> ExampleMapAgent:
    """
    Create an example map agent.
    
    Args:
        name: Name of the agent
        config: Agent configuration
        logger_callback: Callback function for logging
        
    Returns:
        The created example map agent
    """
    logger.info(f"Creating example map agent: {name}")
    return ExampleMapAgent(name, config, logger_callback)

def create_content_ingestion_agent(name: str, 
                                  config: Dict[str, Any],
                                  logger_callback: Optional[Callable] = None) -> ContentIngestionAgent:
    """
    Create a content ingestion agent.
    
    Args:
        name: Name of the agent
        config: Agent configuration
        logger_callback: Callback function for logging
        
    Returns:
        The created content ingestion agent
    """
    logger.info(f"Creating content ingestion agent: {name}")
    return ContentIngestionAgent(name, config, logger_callback)

def create_agents_from_config(config: Dict[str, Any],
                             logger_callback: Optional[Callable] = None) -> Dict[str, BaseAgent]:
    """
    Create agents based on the provided configuration.
    
    Args:
        config: System configuration
        logger_callback: Callback function for logging
        
    Returns:
        Dictionary of created agents, keyed by agent ID
    """
    agents = {}
    
    # Get agent configurations
    agent_configs = config.get("agents", {})
    
    # Create each agent if enabled
    for agent_id, agent_config in agent_configs.items():
        if agent_config.get("enabled", True):
            agent_type = agent_config.get("type")
            agent_name = agent_config.get("name", agent_id)
            
            if agent_type:
                agent = create_agent(agent_type, agent_name, agent_config, logger_callback)
                if agent:
                    agents[agent_id] = agent
                    logger.info(f"Created agent: {agent_id} ({agent_type})")
            else:
                logger.warning(f"Missing agent type for agent: {agent_id}")
    
    return agents
