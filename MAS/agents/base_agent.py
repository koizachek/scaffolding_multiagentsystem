"""
Base Agent

This module provides the base agent class that all agents will inherit from.
"""

import logging
from typing import Dict, List, Any, Optional, Callable

logger = logging.getLogger(__name__)

class BaseAgent:
    """
    Base class for all agents in the multi-agent scaffolding system.
    
    This class provides common functionality and interface for all agents.
    """
    
    def __init__(self, 
                name: str,
                agent_type: str,
                config: Dict[str, Any],
                logger_callback: Optional[Callable] = None):
        """
        Initialize the base agent.
        
        Args:
            name: Name of the agent
            agent_type: Type of agent (e.g., 'lead', 'strategic_scaffolding')
            config: Agent configuration
            logger_callback: Callback function for logging
        """
        self.name = name
        self.agent_type = agent_type
        self.config = config
        self.logger_callback = logger_callback
        self.enabled = True
        self.state = {}
        
        logger.info(f"Initialized {agent_type} agent: {name}")
    
    def is_enabled(self) -> bool:
        """
        Check if the agent is enabled.
        
        Returns:
            True if the agent is enabled, False otherwise
        """
        return self.enabled
    
    def enable(self) -> None:
        """
        Enable the agent.
        """
        self.enabled = True
        logger.info(f"Enabled {self.agent_type} agent: {self.name}")
    
    def disable(self) -> None:
        """
        Disable the agent.
        """
        self.enabled = False
        logger.info(f"Disabled {self.agent_type} agent: {self.name}")
    
    def process(self, 
               input_data: Dict[str, Any], 
               context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input data and generate a response.
        
        Args:
            input_data: Input data to process
            context: Context information
                        
        Returns:
            Response data
        """
        if not self.is_enabled():
            logger.warning(f"Agent {self.name} is disabled. Skipping processing.")
            return {"response": None, "agent_type": self.agent_type, "status": "disabled"}
        
        # Log the processing start
        logger.debug(f"Agent {self.name} processing input: {input_data}")
        
        # Perform processing (to be implemented by subclasses)
        response = self._process_impl(input_data, context)
        
        # Log the processing result
        if self.logger_callback:
            self.logger_callback(
                self.name,  # agent_id
                "process",  # action_type
                {
                    "agent_type": self.agent_type,
                    "input": input_data,
                    "output": response.get("response", ""),
                    "reasoning": response.get("reasoning", ""),
                    "zpd_estimate": response.get("zpd_estimate", None),
                    "timestamp": None  # In a real implementation, this would be a timestamp
                }
            )
        
        logger.debug(f"Agent {self.name} generated response: {response}")
        
        return response
    
    def _process_impl(self, 
                     input_data: Dict[str, Any], 
                     context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Implementation of the processing logic.
        
        This method should be overridden by subclasses.
        
        Args:
            input_data: Input data to process
            context: Context information
            
        Returns:
            Response data
        """
        raise NotImplementedError("Subclasses must implement _process_impl")
    
    def update_state(self, state_updates: Dict[str, Any]) -> None:
        """
        Update the agent's state.
        
        Args:
            state_updates: State updates to apply
        """
        self.state.update(state_updates)
        logger.debug(f"Updated state for agent {self.name}: {state_updates}")
    
    def get_state(self) -> Dict[str, Any]:
        """
        Get the agent's current state.
        
        Returns:
            The agent's state
        """
        return self.state
    
    def reset_state(self) -> None:
        """
        Reset the agent's state.
        """
        self.state = {}
        logger.debug(f"Reset state for agent {self.name}")
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get information about the agent.
        
        Returns:
            Agent information
        """
        return {
            "name": self.name,
            "type": self.agent_type,
            "enabled": self.is_enabled(),
            "state": self.get_state()
        }
