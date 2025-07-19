"""
Multi-Agent Scaffolding System

This module provides the main system class for the multi-agent scaffolding system.
It initializes the system, creates the agents, and handles the interaction flow.
"""

import json
import logging
import os
import sys
from typing import Dict, List, Any, Optional, Callable

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from MAS.agents.agent_factory import create_agents_from_config
from MAS.agents.base_agent import BaseAgent
from MAS.utils.logging_utils import setup_logging
from MAS.utils.pdf_parser import parse_pdf_to_json
from MAS.utils.visualization import plot_concept_map
from MAS.core.scaffolding_engine import ScaffoldingEngine
from MAS.core.dialogue_manager import DialogueManager
from MAS.core.enhanced_io_manager import create_experimental_handlers, ExperimentalIOManager

logger = logging.getLogger(__name__)

class MultiAgentScaffoldingSystem:
    """
    Main system class for the multi-agent scaffolding system.
    
    This class initializes the system, creates the agents, and handles the interaction flow.
    """
    
    def __init__(self, config_path: str = "config.json"):
        """
        Initialize the multi-agent scaffolding system.
        
        Args:
            config_path: Path to the configuration file
        """
        # Load configuration
        self.config = self._load_config(config_path)
        
        # Setup logging
        log_config = self.config.get("logging", {})
        self.log_file = setup_logging(
            log_dir=log_config.get("log_dir", "logs"),
            log_level=log_config.get("log_level", "INFO")
        )
        
        logger.info("Initializing multi-agent scaffolding system")
        
        # Initialize session state
        self.session_state = {
            "current_round": 0,
            "max_rounds": self.config.get("max_rounds", 4),
            "learner_profile": {},
            "zpd_estimate": {},
            "previous_concept_maps": [],
            "current_concept_map": None,
            "uploaded_materials": [],
            "active_design_features": self._get_active_design_features(),
            "interactive_scaffolding": self.config.get("session", {}).get("interactive_scaffolding", True),
            "require_reflection": self.config.get("session", {}).get("require_reflection", True),
            "user_responses": [],
            "pending_reflection": False
        }
        
        # Create agents
        self.agents = create_agents_from_config(self.config, self._log_agent_action)
        
        # Get lead agent
        self.lead_agent = self._get_lead_agent()
        if not self.lead_agent:
            raise ValueError("No lead agent found in configuration")
        
        # Initialize enhanced I/O manager for experimental features
        self.experimental_io_manager = None
        self.enhanced_input_handler = None
        self.enhanced_output_handler = None
        
        # Initialize scaffolding engine and dialogue manager
        self.scaffolding_engine = ScaffoldingEngine(self.config, self.lead_agent)
        self.dialogue_manager = DialogueManager(
            self.config,
            self._handle_user_input,
            self._handle_system_output
        )
        
        # Register scaffolding engine and dialogue manager with lead agent
        if hasattr(self.lead_agent, 'scaffolding_engine') and hasattr(self.lead_agent, 'dialogue_manager'):
            self.lead_agent.scaffolding_engine = self.scaffolding_engine
            self.lead_agent.dialogue_manager = self.dialogue_manager
        
        logger.info("Multi-agent scaffolding system initialized")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """
        Load the configuration from a JSON file.
        
        Args:
            config_path: Path to the configuration file
            
        Returns:
            The loaded configuration
        """
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            logger.info(f"Loaded configuration from {config_path}")
            return config
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            # Return default configuration
            return {
                "max_rounds": 4,
                "agents": {
                    "lead": {
                        "type": "lead",
                        "name": "Lead Agent",
                        "enabled": True
                    }
                },
                "design_features": {
                    "df1_learner_profiling": True,
                    "df2_scaffolding": True,
                    "df3_example_map": True,
                    "df4_content_ingestion": True
                },
                "logging": {
                    "log_dir": "logs",
                    "log_level": "INFO"
                }
            }
    
    def _get_active_design_features(self) -> Dict[str, bool]:
        """
        Get the active design features from the configuration.
        
        Returns:
            Dictionary of design features and their activation status
        """
        design_features = self.config.get("design_features", {})
        
        # Ensure all design features have a value
        default_features = {
            "df1_learner_profiling": True,
            "df2_scaffolding": True,
            "df3_example_map": True,
            "df4_content_ingestion": True
        }
        
        # Update default features with configured values
        for feature, enabled in design_features.items():
            default_features[feature] = enabled
        
        return default_features
    
    def _get_lead_agent(self) -> Optional[BaseAgent]:
        """
        Get the lead agent from the created agents.
        
        Returns:
            The lead agent, or None if not found
        """
        for agent_id, agent in self.agents.items():
            if agent.agent_type == "lead":
                return agent
        return None
    
    def _log_agent_action(self, 
                         agent_id: str, 
                         action_type: str, 
                         details: Dict[str, Any]) -> None:
        """
        Log an agent action.
        
        Args:
            agent_id: ID of the agent
            action_type: Type of action
            details: Action details
        """
        log_entry = {
            "timestamp": details.get("timestamp"),
            "agent_id": agent_id,
            "agent_type": details.get("agent_type"),
            "action_type": action_type,
            "input": details.get("input"),
            "output": details.get("output"),
            "reasoning": details.get("reasoning"),
            "zpd_estimate": details.get("zpd_estimate"),
            "active_design_features": self.session_state.get("active_design_features")
        }
        
        logger.info(f"Agent action: {agent_id} - {action_type}")
        
        # In a real implementation, this would write to a structured log file
        # For now, just log to the console
    
    def process_concept_map(self, pdf_path: str) -> Dict[str, Any]:
        """
        Process a concept map PDF.
        
        Args:
            pdf_path: Path to the concept map PDF
            
        Returns:
            Processing result
        """
        logger.info(f"Processing concept map: {pdf_path}")
        
        try:
            # Parse PDF to JSON
            concept_map_data = parse_pdf_to_json(pdf_path)
            
            # Visualize concept map
            output_dir = self.config.get("output_dir", "output")
            os.makedirs(output_dir, exist_ok=True)
            
            output_path = os.path.join(
                output_dir, 
                f"concept_map_round_{self.session_state['current_round']}.png"
            )
            
            plot_concept_map(concept_map_data, output_path)
            
            # Store concept map in session state
            if self.session_state.get("current_concept_map"):
                self.session_state["previous_concept_maps"].append(
                    self.session_state["current_concept_map"]
                )
            
            # Update current concept map
            self.session_state["current_concept_map"] = concept_map_data
            
            # Save concept map as JSON
            json_output_path = os.path.join(
                output_dir, 
                f"concept_map_round_{self.session_state['current_round']}.json"
            )
            
            with open(json_output_path, 'w') as f:
                json.dump(concept_map_data, f, indent=2)
            
            # Create input data for agents
            input_data = {
                "type": "concept_map_submission",
                "concept_map_data": concept_map_data,
                "pdf_path": pdf_path,
                "round": self.session_state["current_round"]
            }
            
            # Process with lead agent
            context = {"session_state": self.session_state}
            result = self.lead_agent.process(input_data, context)
            
            # Update session state
            if "session_state" in result:
                self.session_state = result["session_state"]
            elif "session_state_updates" in result:
                self.session_state.update(result["session_state_updates"])
            
            # Increment round counter if not already incremented by lead agent
            if "current_round" not in result.get("session_state_updates", {}) and "session_state" not in result:
                self.session_state["current_round"] += 1
            
            return result
        
        except Exception as e:
            logger.error(f"Error processing concept map: {e}")
            return {
                "status": "error",
                "message": f"Error processing concept map: {str(e)}"
            }
    
    def process_material_upload(self, 
                               file_path: str, 
                               material_type: str, 
                               material_name: str) -> Dict[str, Any]:
        """
        Process an uploaded material.
        
        Args:
            file_path: Path to the uploaded file
            material_type: Type of material
            material_name: Name of the material
            
        Returns:
            Processing result
        """
        logger.info(f"Processing material upload: {material_name} ({material_type})")
        
        try:
            # Read file data
            with open(file_path, 'rb') as f:
                material_data = f.read()
            
            # Create input data for agents
            input_data = {
                "type": "material_upload",
                "material_data": material_data,
                "material_type": material_type,
                "material_name": material_name,
                "file_path": file_path,
                "timestamp": None  # In a real implementation, this would be a timestamp
            }
            
            # Process with lead agent
            context = {"session_state": self.session_state}
            result = self.lead_agent.process(input_data, context)
            
            # Update session state
            if "session_state_updates" in result:
                self.session_state.update(result["session_state_updates"])
            
            # Store material in session state
            self.session_state["uploaded_materials"].append({
                "name": material_name,
                "type": material_type,
                "path": file_path
            })
            
            return result
        
        except Exception as e:
            logger.error(f"Error processing material upload: {e}")
            return {
                "status": "error",
                "message": f"Error processing material upload: {str(e)}"
            }
    
    def finalize_session(self) -> Dict[str, Any]:
        """
        Finalize the session and generate summary feedback.
        
        Returns:
            Finalization result
        """
        logger.info("Finalizing session")
        
        try:
            # Create input data for agents
            input_data = {
                "type": "final_round",
                "concept_map_data": self.session_state.get("current_concept_map")
            }
            
            # Process with lead agent
            context = {"session_state": self.session_state}
            result = self.lead_agent.process(input_data, context)
            
            # Generate session log
            self._generate_session_log()
            
            return result
        
        except Exception as e:
            logger.error(f"Error finalizing session: {e}")
            return {
                "status": "error",
                "message": f"Error finalizing session: {str(e)}"
            }
    
    def _generate_session_log(self) -> None:
        """
        Generate a comprehensive session log.
        """
        logger.info("Generating session log")
        
        # In a real implementation, this would generate a structured log file
        # with all the session data, agent interactions, etc.
        
        # For now, just log a summary
        logger.info(f"Session completed: {self.session_state['current_round']} rounds")
        logger.info(f"Active design features: {self.session_state['active_design_features']}")
    
    def get_session_state(self) -> Dict[str, Any]:
        """
        Get the current session state.
        
        Returns:
            The current session state
        """
        return self.session_state
    
    def get_agents(self) -> Dict[str, BaseAgent]:
        """
        Get all agents in the system.
        
        Returns:
            Dictionary of agents, keyed by agent ID
        """
        return self.agents
    
    def get_config(self) -> Dict[str, Any]:
        """
        Get the system configuration.
        
        Returns:
            The system configuration
        """
        return self.config
    
    def process_user_response(self, response_text: str) -> Dict[str, Any]:
        """
        Process a user response.
        
        Args:
            response_text: User response text
            
        Returns:
            Processing result
        """
        logger.info(f"Processing user response: {response_text[:50]}...")
        
        try:
            # Create input data for agents
            input_data = {
                "type": "user_response",
                "text": response_text
            }
            
            # Process with lead agent
            context = {"session_state": self.session_state}
            result = self.lead_agent.process(input_data, context)
            
            # Update session state
            if "session_state" in result:
                self.session_state = result["session_state"]
            elif "session_state_updates" in result:
                self.session_state.update(result["session_state_updates"])
            
            # Store user response in session state
            self.session_state["user_responses"].append(response_text)
            
            # Clear pending reflection flag
            self.session_state["pending_reflection"] = False
            
            return result
        
        except Exception as e:
            logger.error(f"Error processing user response: {e}")
            return {
                "status": "error",
                "message": f"Error processing user response: {str(e)}"
            }  
    def conduct_interactive_scaffolding(self, concept_map: Dict[str, Any], round_number: int) -> Dict[str, Any]:
        """
        Conduct interactive scaffolding with the given concept map and round number.
        Args:
            concept_map: The learner's concept map.
            round_number: The current round number.
        Returns:
            A dictionary with interaction results.
        """
        logger.info(f"Starting interactive scaffolding for round {round_number}")
        if hasattr(self.scaffolding_engine, "conduct_interactive_scaffolding"):
            return self.scaffolding_engine.conduct_interactive_scaffolding(concept_map, round_number)
        else:
            raise NotImplementedError("Scaffolding engine does not support interactive scaffolding.")
    
    def _handle_user_input(self, prompt: str) -> str:
        """
        Handle user input.
        
        Args:
            prompt: Input prompt
            
        Returns:
            User input
        """
        # In a real implementation, this would interact with the user interface
        # For now, just use the standard input
        return input(prompt)
    
    def _handle_system_output(self, text: str) -> None:
        """
        Handle system output.
        
        Args:
            text: Output text
        """
        # In a real implementation, this would interact with the user interface
        # For now, just print to the console
        print(text)
    
    def enable_experimental_mode(self, io_config: Optional[Dict[str, Any]] = None) -> None:
        """
        Enable experimental mode with enhanced I/O and analysis capabilities.
        
        Args:
            io_config: Configuration for enhanced I/O manager
        """
        logger.info("Enabling experimental mode")
        
        # Create enhanced I/O handlers
        self.enhanced_input_handler, self.enhanced_output_handler = create_experimental_handlers(io_config)
        self.experimental_io_manager = self.enhanced_input_handler.io_manager
        
        # Update dialogue manager to use enhanced handlers
        self.dialogue_manager = DialogueManager(
            self.config,
            self.enhanced_input_handler,
            self.enhanced_output_handler
        )
        
        # Update lead agent's dialogue manager reference
        if hasattr(self.lead_agent, 'dialogue_manager'):
            self.lead_agent.dialogue_manager = self.dialogue_manager
        
        logger.info("Experimental mode enabled with enhanced I/O analysis")
    
    def disable_experimental_mode(self) -> None:
        """Disable experimental mode and revert to standard I/O."""
        logger.info("Disabling experimental mode")
        
        # Revert to standard handlers
        self.dialogue_manager = DialogueManager(
            self.config,
            self._handle_user_input,
            self._handle_system_output
        )
        
        # Update lead agent's dialogue manager reference
        if hasattr(self.lead_agent, 'dialogue_manager'):
            self.lead_agent.dialogue_manager = self.dialogue_manager
        
        # Clear experimental references
        self.experimental_io_manager = None
        self.enhanced_input_handler = None
        self.enhanced_output_handler = None
        
        logger.info("Experimental mode disabled")
    
    def get_interaction_analysis(self) -> Optional[Dict[str, Any]]:
        """
        Get comprehensive interaction analysis from experimental mode.
        
        Returns:
            Interaction analysis if experimental mode is enabled, None otherwise
        """
        if self.experimental_io_manager:
            return self.experimental_io_manager.get_interaction_analysis()
        else:
            logger.warning("Experimental mode not enabled. No interaction analysis available.")
            return None
    
    def export_experimental_data(self, filepath: Optional[str] = None) -> Optional[str]:
        """
        Export experimental session data for research analysis.
        
        Args:
            filepath: Optional filepath for export
            
        Returns:
            Filepath where data was saved, or None if experimental mode not enabled
        """
        if self.experimental_io_manager:
            return self.experimental_io_manager.export_session_data(filepath)
        else:
            logger.warning("Experimental mode not enabled. No data to export.")
            return None
    
    def get_experimental_session_data(self) -> Optional[Dict[str, Any]]:
        """
        Get current experimental session data.
        
        Returns:
            Session data if experimental mode is enabled, None otherwise
        """
        if self.experimental_io_manager:
            return self.experimental_io_manager.get_session_data()
        else:
            return None
    
    def reset_experimental_session(self) -> None:
        """Reset experimental session data for a new session."""
        if self.experimental_io_manager:
            self.experimental_io_manager.reset_session()
            logger.info("Experimental session data reset")
        else:
            logger.warning("Experimental mode not enabled. No session to reset.")

    def set_expert_map(self, expert_map: Dict[str, Any]) -> None:
        """ 
        Set expert concept map in the scaffolding engine.
        """
        if hasattr(self.scaffolding_engine, "set_expert_map"):
            self.scaffolding_engine.set_expert_map(expert_map)
        else:
            self.expert_map = expert_map #fallbaclk

    def set_learner_profile(self, learner_profile: Dict[str, Any]) -> None:
        """
        Set the learner profile in the scaffolding engine.
        """
        if hasattr(self.scaffolding_engine, "set_learner_profile"):
            self.scaffolding_engine.set_learner_profile(learner_profile)
        else:
            self.session_state["learner_profile"] = learner_profile #fallback
    
    def is_experimental_mode_enabled(self) -> bool:
        """Check if experimental mode is currently enabled."""
        return self.experimental_io_manager is not None
    
    def process_concept_map_experimental(self, pdf_path: str, 
                                       collect_detailed_analysis: bool = True) -> Dict[str, Any]:
        """
        Process a concept map with enhanced experimental data collection.
        
        Args:
            pdf_path: Path to the concept map PDF
            collect_detailed_analysis: Whether to collect detailed interaction analysis
            
        Returns:
            Processing result with experimental data
        """
        if not self.is_experimental_mode_enabled():
            logger.warning("Experimental mode not enabled. Using standard processing.")
            return self.process_concept_map(pdf_path)
        
        logger.info(f"Processing concept map in experimental mode: {pdf_path}")
        
        # Process concept map normally, whatever normally means in that context
        result = self.process_concept_map(pdf_path)
        
        # Add experimental analysis if requested
        if collect_detailed_analysis and self.experimental_io_manager:
            experimental_analysis = self.experimental_io_manager.get_interaction_analysis()
            result["experimental_analysis"] = experimental_analysis
            
            # Log experimental metrics
            if experimental_analysis and "session_summary" in experimental_analysis:
                summary = experimental_analysis["session_summary"]
                logger.info(f"Experimental metrics - Total interactions: {summary.get('total_interactions', 0)}, "
                           f"Avg response time: {summary.get('avg_response_time', 0):.2f}s")
        
        return result
