"""
Lead Agent (Orchestrator)

This module provides the lead agent that orchestrates the multi-agent scaffolding system.
"""

import logging
import json
import os
import sys
from typing import Dict, List, Any, Optional, Callable, Type

from .base_agent import BaseAgent
from ..core.scaffolding_engine import ScaffoldingEngine
from ..core.dialogue_manager import DialogueManager

logger = logging.getLogger(__name__)

class LeadAgent(BaseAgent):
    """
    Lead agent (orchestrator) for the multi-agent scaffolding system.
    
    This agent controls the workflow, phases, user prompts, and sub-agent activation.
    """
    
    def __init__(self, 
                name: str,
                config: Dict[str, Any],
                logger_callback: Optional[Callable] = None,
                input_handler: Optional[Callable] = None,
                output_handler: Optional[Callable] = None):
        """
        Initialize the lead agent.
        
        Args:
            name: Name of the agent
            config: Agent configuration
            logger_callback: Callback function for logging
            input_handler: Function for handling user input (optional)
            output_handler: Function for handling system output (optional)
        """
        super().__init__(name, "lead", config, logger_callback)
        
        # Initialize sub-agents registry
        self.sub_agents = {}
        
        # Initialize session state
        self.session_state = {
            "current_round": 0,
            "max_rounds": config.get("session", {}).get("max_rounds", 4),
            "require_reflection": config.get("session", {}).get("require_reflection", True),
            "learner_profile": {},
            "zpd_estimate": {},
            "current_concept_map": None,
            "previous_concept_maps": [],
            "user_responses": [],
            "pending_reflection": False,
            "interactive_scaffolding": config.get("session", {}).get("interactive_scaffolding", True)
        }
        
        # Initialize scaffolding engine
        self.scaffolding_engine = ScaffoldingEngine(config, self)
        
        # Initialize dialogue manager
        self.dialogue_manager = DialogueManager(config, input_handler, output_handler)
        
        logger.info(f"Initialized lead agent: {name}")
    
    def register_sub_agent(self, agent: BaseAgent) -> None:
        """
        Register a sub-agent with the lead agent.
        
        Args:
            agent: Sub-agent to register
        """
        agent_type = agent.agent_type
        self.sub_agents[agent_type] = agent
        logger.info(f"Registered sub-agent: {agent.name} (type: {agent_type})")
    
    def get_sub_agent(self, agent_type: str) -> Optional[BaseAgent]:
        """
        Get a sub-agent by type.
        
        Args:
            agent_type: Type of the sub-agent to get
            
        Returns:
            The sub-agent, or None if not found
        """
        return self.sub_agents.get(agent_type)
    
    def get_active_sub_agents(self) -> List[BaseAgent]:
        """
        Get all active sub-agents.
        
        Returns:
            List of active sub-agents
        """
        return [agent for agent in self.sub_agents.values() if agent.is_enabled()]
    
    def _process_impl(self, 
                     input_data: Dict[str, Any], 
                     context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input data and coordinate sub-agents.
        
        Args:
            input_data: Input data to process
            context: Context information
            
        Returns:
            Response data
        """
        # Extract input type
        input_type = input_data.get("type", "unknown")
        
        # Process based on input type
        if input_type == "session_start":
            return self._handle_session_start(input_data, context)
        elif input_type == "concept_map_submission":
            return self._handle_concept_map_submission(input_data, context)
        elif input_type == "user_response":
            return self._handle_user_response(input_data, context)
        elif input_type == "session_end":
            return self._handle_session_end(input_data, context)
        else:
            logger.warning(f"Unknown input type: {input_type}")
            return {
                "response": f"I don't understand the input type: {input_type}",
                "agent_type": self.agent_type,
                "status": "error"
            }
    
    def _handle_session_start(self, 
                             input_data: Dict[str, Any], 
                             context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle session start.
        
        Args:
            input_data: Input data
            context: Context information
            
        Returns:
            Response data
        """
        logger.info("Starting new session")
        
        # Reset session state
        self.session_state = {
            "current_round": 0,
            "max_rounds": self.config.get("session", {}).get("max_rounds", 4),
            "require_reflection": self.config.get("session", {}).get("require_reflection", True),
            "learner_profile": {},
            "zpd_estimate": {},
            "current_concept_map": None,
            "previous_concept_maps": [],
            "user_responses": [],
            "pending_reflection": False
        }
        
        # Check if learner profiling is enabled
        df1_enabled = self.config.get("design_features", {}).get("df1_learner_profiling", True)
        
        if df1_enabled:
            # Get learner profiling agent
            profiling_agent = self.get_sub_agent("learner_profiling")
            
            if profiling_agent and profiling_agent.is_enabled():
                # Process with learner profiling agent
                profiling_response = profiling_agent.process(
                    {"type": "session_start"},
                    {"session_state": self.session_state}
                )
                
                # Update session state with learner profile and ZPD estimate
                if profiling_response.get("learner_profile"):
                    self.session_state["learner_profile"] = profiling_response["learner_profile"]
                
                if profiling_response.get("zpd_estimate"):
                    self.session_state["zpd_estimate"] = profiling_response["zpd_estimate"]
                
                # Return the profiling agent's response
                return {
                    "response": profiling_response.get("response", ""),
                    "agent_type": self.agent_type,
                    "status": "success",
                    "session_state": self.session_state
                }
        
        # If learner profiling is disabled or not available, provide a generic welcome
        welcome_message = (
            "Welcome to the concept mapping session. "
            "Please upload your concept map as a PDF file to begin. "
            "I'll provide scaffolded feedback to help you improve your map."
        )
        
        return {
            "response": welcome_message,
            "agent_type": self.agent_type,
            "status": "success",
            "session_state": self.session_state
        }
    
    def _handle_concept_map_submission(self, 
                                      input_data: Dict[str, Any], 
                                      context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle concept map submission.
        
        Args:
            input_data: Input data
            context: Context information
            
        Returns:
            Response data
        """
        # Extract concept map data
        concept_map_data = input_data.get("concept_map_data")
        
        if not concept_map_data:
            return {
                "response": "No concept map data provided. Please upload a valid concept map.",
                "agent_type": self.agent_type,
                "status": "error"
            }
        
        # Store previous concept map if exists
        if self.session_state["current_concept_map"]:
            self.session_state["previous_concept_maps"].append(
                self.session_state["current_concept_map"]
            )
        
        # Update current concept map
        self.session_state["current_concept_map"] = concept_map_data
        
        # Increment round if not the first submission
        if self.session_state["current_round"] > 0 or len(self.session_state["previous_concept_maps"]) > 0:
            self.session_state["current_round"] += 1
        
        # Check if we've reached the maximum number of rounds
        if self.session_state["current_round"] >= self.session_state["max_rounds"]:
            return self._handle_final_round(input_data, context)
        
        # Process with content ingestion agent first if enabled
        df4_enabled = self.config.get("design_features", {}).get("df4_content_ingestion", True)
        
        if df4_enabled:
            content_agent = self.get_sub_agent("content_ingestion")
            
            if content_agent and content_agent.is_enabled():
                # Process with content ingestion agent
                content_response = content_agent.process(
                    {"type": "concept_map_submission", "concept_map_data": concept_map_data},
                    {"session_state": self.session_state}
                )
                
                # Update session state with any content analysis
                if content_response.get("content_analysis"):
                    self.session_state["content_analysis"] = content_response["content_analysis"]
        
        # Process with example map agent if enabled
        df3_enabled = self.config.get("design_features", {}).get("df3_example_map", True)
        expert_map = None
        
        if df3_enabled:
            example_agent = self.get_sub_agent("example_map")
            
            if example_agent and example_agent.is_enabled():
                # Process with example map agent
                example_response = example_agent.process(
                    {"type": "concept_map_submission", "concept_map_data": concept_map_data},
                    {"session_state": self.session_state}
                )
                
                # Get expert map if available
                expert_map = example_response.get("expert_map")
        
        # Check if interactive scaffolding is enabled
        if self.session_state.get("interactive_scaffolding", True):
            # Get previous map if available
            previous_map = None
            if self.session_state["previous_concept_maps"]:
                previous_map = self.session_state["previous_concept_maps"][-1]
            
            # Get learner profile if available
            learner_profile = self.session_state.get("learner_profile")
            
            # Conduct scaffolding interaction
            interaction_results = self.scaffolding_engine.conduct_scaffolding_interaction(
                concept_map_data,
                previous_map,
                expert_map,
                learner_profile
            )
            
            if interaction_results.get("status") == "success":
                # Get scaffolding type and prompts
                scaffolding_type = interaction_results.get("scaffolding_type")
                prompts = interaction_results.get("interaction_results", {}).get("formatted_prompts", [])
                
                if scaffolding_type and prompts:
                    # Present scaffolding prompts and collect responses
                    learner_responses = self.dialogue_manager.present_scaffolding_prompts(
                        scaffolding_type,
                        prompts,
                        require_response=True
                    )
                    
                    # Process learner responses
                    for response in learner_responses:
                        # Process the response
                        follow_up_result = self.scaffolding_engine.process_learner_response(response)
                        
                        # Check if a follow-up is needed
                        if follow_up_result.get("follow_up"):
                            # Present follow-up and collect response
                            follow_up_response = self.dialogue_manager.present_follow_up(
                                scaffolding_type,
                                follow_up_result["follow_up"],
                                require_response=True
                            )
                    
                    # Conclude the interaction
                    conclusion_result = self.scaffolding_engine.conclude_interaction()
                    
                    if conclusion_result.get("formatted_conclusion"):
                        # Present conclusion
                        self.dialogue_manager.present_conclusion(
                            scaffolding_type,
                            conclusion_result["conclusion"]
                        )
                    
                    # Return success response
                    return {
                        "response": "Scaffolding interaction completed successfully.",
                        "agent_type": self.agent_type,
                        "status": "success",
                        "session_state": self.session_state,
                        "scaffolding_type": scaffolding_type,
                        "interaction_results": interaction_results
                    }
        
        # If interactive scaffolding is disabled or failed, fall back to traditional approach
        responses = []
        
        # Process with scaffolding agents if enabled
        df2_config = self.config.get("design_features", {}).get("df2_scaffolding", {})
        
        scaffolding_types = [
            ("strategic", "strategic_scaffolding"),
            ("conceptual", "conceptual_scaffolding"),
            ("metacognitive", "metacognitive_scaffolding"),
            ("procedural", "procedural_scaffolding")
        ]
        
        for config_key, agent_type in scaffolding_types:
            if df2_config.get(config_key, True):
                agent = self.get_sub_agent(agent_type)
                
                if agent and agent.is_enabled():
                    # Process with scaffolding agent
                    agent_response = agent.process(
                        {"type": "concept_map_submission", "concept_map_data": concept_map_data},
                        {"session_state": self.session_state}
                    )
                    
                    if agent_response.get("response"):
                        responses.append(agent_response["response"])
        
        # Combine responses
        combined_response = "\n\n".join(responses)
        
        if not combined_response:
            combined_response = (
                "I've analyzed your concept map. "
                "Please reflect on the relationships between concepts and consider "
                "how you might improve the organization and connections in your map."
            )
        
        # Set pending reflection flag if required
        if self.session_state["require_reflection"]:
            self.session_state["pending_reflection"] = True
            
            reflection_prompt = (
                "\n\nPlease take a moment to reflect on this feedback. "
                "What aspects of your concept map do you think need improvement? "
                "What changes are you considering making in your next revision?"
            )
            
            combined_response += reflection_prompt
        
        return {
            "response": combined_response,
            "agent_type": self.agent_type,
            "status": "success",
            "session_state": self.session_state
        }
    
    def _handle_user_response(self, 
                             input_data: Dict[str, Any], 
                             context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle user response.
        
        Args:
            input_data: Input data
            context: Context information
            
        Returns:
            Response data
        """
        # Extract user response
        user_response = input_data.get("text", "")
        
        if not user_response:
            return {
                "response": "I didn't receive your response. Please try again.",
                "agent_type": self.agent_type,
                "status": "error"
            }
        
        # Store user response
        self.session_state["user_responses"].append(user_response)
        
        # Clear pending reflection flag
        self.session_state["pending_reflection"] = False
        
        # Process with learner profiling agent to update ZPD if enabled
        df1_enabled = self.config.get("design_features", {}).get("df1_learner_profiling", True)
        
        if df1_enabled:
            profiling_agent = self.get_sub_agent("learner_profiling")
            
            if profiling_agent and profiling_agent.is_enabled():
                # Process with learner profiling agent
                profiling_response = profiling_agent.process(
                    {"type": "user_response", "text": user_response},
                    {"session_state": self.session_state}
                )
                
                # Update ZPD estimate if provided
                if profiling_response.get("zpd_estimate"):
                    self.session_state["zpd_estimate"] = profiling_response["zpd_estimate"]
                    
                    # Update scaffolding engine session state
                    self.scaffolding_engine.update_session_state({
                        "zpd_estimate": profiling_response["zpd_estimate"]
                    })
        
        # Analyze the response
        response_analysis = self.dialogue_manager.analyze_response(user_response)
        
        # Update session state with response analysis
        if "response_analyses" not in self.session_state:
            self.session_state["response_analyses"] = []
        
        self.session_state["response_analyses"].append(response_analysis)
        
        # Check if this is part of an active scaffolding interaction
        if self.scaffolding_engine.get_interaction_history():
            # Process the response with the scaffolding engine
            follow_up_result = self.scaffolding_engine.process_learner_response(user_response)
            
            # Check if a follow-up is needed
            if follow_up_result.get("follow_up"):
                # Present follow-up and collect response
                scaffolding_type = follow_up_result.get("scaffolding_type", "strategic")
                follow_up_response = self.dialogue_manager.present_follow_up(
                    scaffolding_type,
                    follow_up_result["follow_up"],
                    require_response=True
                )
                
                # Process the follow-up response
                if follow_up_response:
                    self.scaffolding_engine.process_learner_response(follow_up_response)
            
            # Conclude the interaction
            conclusion_result = self.scaffolding_engine.conclude_interaction()
            
            if conclusion_result.get("formatted_conclusion"):
                # Present conclusion
                self.dialogue_manager.present_conclusion(
                    conclusion_result.get("scaffolding_type", "strategic"),
                    conclusion_result["conclusion"]
                )
            
            # Generate response based on user input
            if self.session_state["current_round"] == 0:
                # First round, ask for concept map
                response = (
                    "Thank you for sharing your thoughts. "
                    "Now, please upload your concept map as a PDF file. "
                    "I'll analyze it and provide feedback to help you improve."
                )
            else:
                # Subsequent rounds, encourage next revision
                response = (
                    "Thank you for your reflection. "
                    "Please revise your concept map based on the feedback and your reflections, "
                    "then upload the new version when you're ready."
                )
            
            return {
                "response": response,
                "agent_type": self.agent_type,
                "status": "success",
                "session_state": self.session_state,
                "response_analysis": response_analysis
            }
        
        # If not part of an active scaffolding interaction, proceed with normal flow
        # Generate response based on user input
        if self.session_state["current_round"] == 0:
            # First round, ask for concept map
            response = (
                "Thank you for sharing your thoughts. "
                "Now, please upload your concept map as a PDF file. "
                "I'll analyze it and provide feedback to help you improve."
            )
        else:
            # Subsequent rounds, encourage next revision
            response = (
                "Thank you for your reflection. "
                "Please revise your concept map based on the feedback and your reflections, "
                "then upload the new version when you're ready."
            )
        
        return {
            "response": response,
            "agent_type": self.agent_type,
            "status": "success",
            "session_state": self.session_state,
            "response_analysis": response_analysis
        }
    
    def _handle_final_round(self, 
                           input_data: Dict[str, Any], 
                           context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle the final round of the session.
        
        Args:
            input_data: Input data
            context: Context information
            
        Returns:
            Response data
        """
        # Extract concept map data
        concept_map_data = input_data.get("concept_map_data") or self.session_state["current_concept_map"]
        
        # Check if interactive scaffolding is enabled for final round
        if self.session_state.get("interactive_scaffolding", True):
            # Evaluate scaffolding effectiveness
            effectiveness = self.scaffolding_engine.evaluate_scaffolding_effectiveness()
            
            # Store effectiveness in session state
            self.session_state["scaffolding_effectiveness"] = effectiveness
            
            # Get previous map if available
            previous_map = None
            if self.session_state["previous_concept_maps"]:
                previous_map = self.session_state["previous_concept_maps"][-1]
            
            # Get expert map if available
            expert_map = None
            df3_enabled = self.config.get("design_features", {}).get("df3_example_map", True)
            
            if df3_enabled:
                example_agent = self.get_sub_agent("example_map")
                
                if example_agent and example_agent.is_enabled():
                    # Process with example map agent
                    example_response = example_agent.process(
                        {"type": "final_round", "concept_map_data": concept_map_data},
                        {"session_state": self.session_state}
                    )
                    
                    # Get expert map if available
                    expert_map = example_response.get("expert_map")
            
            # Conduct final scaffolding interaction
            interaction_results = self.scaffolding_engine.conduct_scaffolding_interaction(
                concept_map_data,
                previous_map,
                expert_map,
                self.session_state.get("learner_profile")
            )
            
            if interaction_results.get("status") == "success":
                # Get scaffolding type and prompts
                scaffolding_type = interaction_results.get("scaffolding_type")
                prompts = interaction_results.get("interaction_results", {}).get("formatted_prompts", [])
                
                if scaffolding_type and prompts:
                    # Present scaffolding prompts and collect responses
                    learner_responses = self.dialogue_manager.present_scaffolding_prompts(
                        scaffolding_type,
                        prompts,
                        require_response=True
                    )
                    
                    # Process learner responses
                    for response in learner_responses:
                        # Process the response
                        follow_up_result = self.scaffolding_engine.process_learner_response(response)
                        
                        # Check if a follow-up is needed
                        if follow_up_result.get("follow_up"):
                            # Present follow-up and collect response
                            follow_up_response = self.dialogue_manager.present_follow_up(
                                scaffolding_type,
                                follow_up_result["follow_up"],
                                require_response=True
                            )
                    
                    # Conclude the interaction
                    conclusion_result = self.scaffolding_engine.conclude_interaction()
                    
                    if conclusion_result.get("formatted_conclusion"):
                        # Present conclusion
                        self.dialogue_manager.present_conclusion(
                            scaffolding_type,
                            conclusion_result["conclusion"]
                        )
        
        # Process with active sub-agents for final feedback
        responses = []
        
        # Get all active sub-agents
        active_agents = self.get_active_sub_agents()
        
        for agent in active_agents:
            if agent.agent_type != "lead":
                # Process with sub-agent
                agent_response = agent.process(
                    {"type": "final_round", "concept_map_data": concept_map_data},
                    {"session_state": self.session_state}
                )
                
                if agent_response.get("response"):
                    responses.append(agent_response["response"])
        
        # Combine responses
        combined_response = "\n\n".join(responses)
        
        if not combined_response:
            combined_response = (
                "Thank you for completing all rounds of the concept mapping session. "
                "Your final map shows your understanding of the relationships between concepts. "
                "Continue to reflect on these connections as you deepen your knowledge in this area."
            )
        
        # Add session completion message
        completion_message = (
            "\n\nYou have completed all rounds of this concept mapping session. "
            "Thank you for your participation and engagement in the process."
        )
        
        combined_response += completion_message
        
        return {
            "response": combined_response,
            "agent_type": self.agent_type,
            "status": "success",
            "session_state": self.session_state,
            "session_complete": True,
            "scaffolding_history": self.scaffolding_engine.get_scaffolding_history(),
            "dialogue_history": self.dialogue_manager.get_dialogue_history()
        }
    
    def _handle_session_end(self, 
                           input_data: Dict[str, Any], 
                           context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle session end.
        
        Args:
            input_data: Input data
            context: Context information
            
        Returns:
            Response data
        """
        logger.info("Ending session")
        
        # Generate session summary
        summary = {
            "rounds_completed": self.session_state["current_round"],
            "concept_maps_submitted": len(self.session_state["previous_concept_maps"]) + 
                                     (1 if self.session_state["current_concept_map"] else 0),
            "user_responses": len(self.session_state["user_responses"]),
            "final_zpd_estimate": self.session_state.get("zpd_estimate", {})
        }
        
        # Generate farewell message
        farewell_message = (
            "Thank you for participating in this concept mapping session. "
            f"You completed {summary['rounds_completed']} rounds and submitted "
            f"{summary['concept_maps_submitted']} concept maps. "
            "I hope the scaffolded feedback was helpful in developing your understanding."
        )
        
        return {
            "response": farewell_message,
            "agent_type": self.agent_type,
            "status": "success",
            "session_state": self.session_state,
            "session_summary": summary
        }
    
    def get_session_state(self) -> Dict[str, Any]:
        """
        Get the current session state.
        
        Returns:
            The current session state
        """
        return self.session_state
    
    def update_session_state(self, state_updates: Dict[str, Any]) -> None:
        """
        Update the session state.
        
        Args:
            state_updates: State updates to apply
        """
        self.session_state.update(state_updates)
        logger.debug(f"Updated session state: {state_updates}")
    
    def reset_session_state(self) -> None:
        """
        Reset the session state.
        """
        self.session_state = {
            "current_round": 0,
            "max_rounds": self.config.get("session", {}).get("max_rounds", 4),
            "require_reflection": self.config.get("session", {}).get("require_reflection", True),
            "learner_profile": {},
            "zpd_estimate": {},
            "current_concept_map": None,
            "previous_concept_maps": [],
            "user_responses": [],
            "pending_reflection": False
        }
        logger.debug("Reset session state")
