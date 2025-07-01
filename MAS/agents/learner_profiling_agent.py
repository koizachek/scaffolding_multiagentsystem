"""
Learner Profiling Agent (DF1)

This module provides the learner profiling agent that handles learner profiling and ZPD estimation.
"""

import logging
from typing import Dict, List, Any, Optional, Callable

from .base_agent import BaseAgent

logger = logging.getLogger(__name__)

class LearnerProfilingAgent(BaseAgent):
    """
    Learner profiling agent for the multi-agent scaffolding system.
    
    This agent handles learner profiling and Zone of Proximal Development (ZPD) estimation.
    """
    
    def __init__(self, 
                name: str,
                config: Dict[str, Any],
                logger_callback: Optional[Callable] = None):
        """
        Initialize the learner profiling agent.
        
        Args:
            name: Name of the agent
            config: Agent configuration
            logger_callback: Callback function for logging
        """
        super().__init__(name, "learner_profiling", config, logger_callback)
        
        # Initialize learner profile
        self.learner_profile = {}
        
        # Initialize ZPD estimate
        self.zpd_estimate = {
            "conceptual_understanding": "medium",  # low, medium, high
            "metacognitive_skills": "medium",      # low, medium, high
            "technical_proficiency": "medium",     # low, medium, high
            "scaffolding_needs": {
                "strategic": "medium",             # low, medium, high
                "conceptual": "medium",            # low, medium, high
                "metacognitive": "medium",         # low, medium, high
                "procedural": "medium"             # low, medium, high
            }
        }
        
        logger.info(f"Initialized learner profiling agent: {name}")
    
    def _process_impl(self, 
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
        # Extract input type
        input_type = input_data.get("type", "unknown")
        
        # Process based on input type
        if input_type == "session_start":
            return self._handle_session_start(input_data, context)
        elif input_type == "user_response":
            return self._handle_user_response(input_data, context)
        elif input_type == "concept_map_submission":
            return self._handle_concept_map_submission(input_data, context)
        elif input_type == "final_round":
            return self._handle_final_round(input_data, context)
        else:
            logger.warning(f"Unknown input type: {input_type}")
            return {
                "response": None,
                "agent_type": self.agent_type,
                "status": "error"
            }
    
    def _handle_session_start(self, 
                             input_data: Dict[str, Any], 
                             context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle session start by collecting initial learner information.
        
        Args:
            input_data: Input data
            context: Context information
            
        Returns:
            Response data with initial questions for the learner
        """
        logger.info("Handling session start")
        
        # Reset learner profile and ZPD estimate
        self.learner_profile = {}
        self.zpd_estimate = {
            "conceptual_understanding": "medium",
            "metacognitive_skills": "medium",
            "technical_proficiency": "medium",
            "scaffolding_needs": {
                "strategic": "medium",
                "conceptual": "medium",
                "metacognitive": "medium",
                "procedural": "medium"
            }
        }
        
        # Generate initial questions to profile the learner
        questions = (
            "Before we begin working with concept maps, I'd like to learn a bit about you to better "
            "tailor my guidance. Please share:\n\n"
            "1. What is your prior knowledge or experience with the topic you'll be mapping?\n"
            "2. Have you created concept maps before? If so, how comfortable are you with the process?\n"
            "3. What are your learning goals for this session?\n"
            "4. Do you prefer step-by-step guidance or more open-ended exploration?\n"
            "5. What aspects of concept mapping do you find most challenging?"
        )
        
        return {
            "response": questions,
            "agent_type": self.agent_type,
            "status": "success",
            "learner_profile": self.learner_profile,
            "zpd_estimate": self.zpd_estimate
        }
    
    def _handle_user_response(self, 
                             input_data: Dict[str, Any], 
                             context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle user response by updating the learner profile and ZPD estimate.
        
        Args:
            input_data: Input data containing user response
            context: Context information
            
        Returns:
            Response data with updated learner profile and ZPD estimate
        """
        # Extract user response
        user_response = input_data.get("text", "")
        
        if not user_response:
            return {
                "response": None,
                "agent_type": self.agent_type,
                "status": "error"
            }
        
        logger.info("Processing user response for profiling")
        
        # Get current session state
        session_state = context.get("session_state", {})
        
        # Update learner profile based on user response
        self._update_learner_profile(user_response, session_state)
        
        # Update ZPD estimate based on updated learner profile
        self._update_zpd_estimate(session_state)
        
        # No direct response to the user from this agent
        return {
            "response": None,
            "agent_type": self.agent_type,
            "status": "success",
            "learner_profile": self.learner_profile,
            "zpd_estimate": self.zpd_estimate,
            "reasoning": "Updated learner profile and ZPD estimate based on user response"
        }
    
    def _handle_concept_map_submission(self, 
                                      input_data: Dict[str, Any], 
                                      context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle concept map submission by analyzing it and updating the ZPD estimate.
        
        Args:
            input_data: Input data containing concept map
            context: Context information
            
        Returns:
            Response data with updated ZPD estimate
        """
        # Extract concept map data
        concept_map_data = input_data.get("concept_map_data")
        
        if not concept_map_data:
            return {
                "response": None,
                "agent_type": self.agent_type,
                "status": "error"
            }
        
        logger.info("Analyzing concept map for ZPD estimation")
        
        # Get current session state
        session_state = context.get("session_state", {})
        
        # Update ZPD estimate based on concept map analysis
        self._update_zpd_from_concept_map(concept_map_data, session_state)
        
        # No direct response to the user from this agent
        return {
            "response": None,
            "agent_type": self.agent_type,
            "status": "success",
            "zpd_estimate": self.zpd_estimate,
            "reasoning": "Updated ZPD estimate based on concept map analysis"
        }
    
    def _handle_final_round(self, 
                           input_data: Dict[str, Any], 
                           context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle final round by providing a summary of the learner's progress.
        
        Args:
            input_data: Input data
            context: Context information
            
        Returns:
            Response data with final assessment
        """
        logger.info("Generating final learner assessment")
        
        # Get current session state
        session_state = context.get("session_state", {})
        
        # Generate final assessment based on learner profile and ZPD estimate
        assessment = self._generate_final_assessment(session_state)
        
        return {
            "response": assessment,
            "agent_type": self.agent_type,
            "status": "success",
            "learner_profile": self.learner_profile,
            "zpd_estimate": self.zpd_estimate
        }
    
    def _update_learner_profile(self, 
                               user_response: str, 
                               session_state: Dict[str, Any]) -> None:
        """
        Update the learner profile based on user response.
        
        Args:
            user_response: User's response text
            session_state: Current session state
        """
        # This is a simplified implementation
        # In a real implementation, this would use NLP to extract information from the user response
        
        # Check if this is the first response (to initial profiling questions)
        if not self.learner_profile:
            # Extract prior knowledge
            if "beginner" in user_response.lower() or "new to" in user_response.lower():
                prior_knowledge = "low"
            elif "expert" in user_response.lower() or "advanced" in user_response.lower():
                prior_knowledge = "high"
            else:
                prior_knowledge = "medium"
            
            # Extract experience with concept maps
            if "never" in user_response.lower() or "first time" in user_response.lower():
                concept_map_experience = "low"
            elif "experienced" in user_response.lower() or "many times" in user_response.lower():
                concept_map_experience = "high"
            else:
                concept_map_experience = "medium"
            
            # Extract guidance preference
            if "step-by-step" in user_response.lower() or "detailed" in user_response.lower():
                guidance_preference = "structured"
            elif "open-ended" in user_response.lower() or "explore" in user_response.lower():
                guidance_preference = "exploratory"
            else:
                guidance_preference = "balanced"
            
            # Update learner profile
            self.learner_profile = {
                "prior_knowledge": prior_knowledge,
                "concept_map_experience": concept_map_experience,
                "guidance_preference": guidance_preference,
                "responses": [user_response]
            }
        else:
            # For subsequent responses, append to the responses list
            if "responses" in self.learner_profile:
                self.learner_profile["responses"].append(user_response)
            else:
                self.learner_profile["responses"] = [user_response]
            
            # Update profile based on response content
            # This is a simplified implementation
            if "struggle" in user_response.lower() or "difficult" in user_response.lower():
                self.learner_profile["challenges_expressed"] = True
            
            if "understand" in user_response.lower() or "clear" in user_response.lower():
                self.learner_profile["understanding_expressed"] = True
        
        logger.debug(f"Updated learner profile: {self.learner_profile}")
    
    def _update_zpd_estimate(self, session_state: Dict[str, Any]) -> None:
        """
        Update the ZPD estimate based on the learner profile and session state.
        
        Args:
            session_state: Current session state
        """
        # This is a simplified implementation
        # In a real implementation, this would use more sophisticated analysis
        
        # Update conceptual understanding based on prior knowledge
        if self.learner_profile.get("prior_knowledge") == "low":
            self.zpd_estimate["conceptual_understanding"] = "low"
        elif self.learner_profile.get("prior_knowledge") == "high":
            self.zpd_estimate["conceptual_understanding"] = "high"
        
        # Update technical proficiency based on concept map experience
        if self.learner_profile.get("concept_map_experience") == "low":
            self.zpd_estimate["technical_proficiency"] = "low"
            self.zpd_estimate["scaffolding_needs"]["procedural"] = "high"
        elif self.learner_profile.get("concept_map_experience") == "high":
            self.zpd_estimate["technical_proficiency"] = "high"
            self.zpd_estimate["scaffolding_needs"]["procedural"] = "low"
        
        # Update scaffolding needs based on guidance preference
        if self.learner_profile.get("guidance_preference") == "structured":
            self.zpd_estimate["scaffolding_needs"]["strategic"] = "high"
        elif self.learner_profile.get("guidance_preference") == "exploratory":
            self.zpd_estimate["scaffolding_needs"]["strategic"] = "low"
        
        # Update based on challenges expressed
        if self.learner_profile.get("challenges_expressed"):
            self.zpd_estimate["scaffolding_needs"]["metacognitive"] = "high"
        
        # Update based on understanding expressed
        if self.learner_profile.get("understanding_expressed"):
            self.zpd_estimate["conceptual_understanding"] = "high"
            self.zpd_estimate["scaffolding_needs"]["conceptual"] = "low"
        
        logger.debug(f"Updated ZPD estimate: {self.zpd_estimate}")
    
    def _update_zpd_from_concept_map(self, 
                                    concept_map_data: Dict[str, Any], 
                                    session_state: Dict[str, Any]) -> None:
        """
        Update the ZPD estimate based on concept map analysis.
        
        Args:
            concept_map_data: Concept map data
            session_state: Current session state
        """
        # This is a simplified implementation
        # In a real implementation, this would use more sophisticated analysis
        
        # Extract nodes and edges
        nodes = concept_map_data.get("nodes", [])
        edges = concept_map_data.get("edges", [])
        
        # Analyze concept map complexity
        num_nodes = len(nodes)
        num_edges = len(edges)
        
        # Calculate connectivity ratio (edges per node)
        connectivity_ratio = num_edges / num_nodes if num_nodes > 0 else 0
        
        # Update conceptual understanding based on map complexity
        if num_nodes < 5:
            self.zpd_estimate["conceptual_understanding"] = "low"
            self.zpd_estimate["scaffolding_needs"]["conceptual"] = "high"
        elif num_nodes > 15:
            self.zpd_estimate["conceptual_understanding"] = "high"
            self.zpd_estimate["scaffolding_needs"]["conceptual"] = "low"
        
        # Update metacognitive skills based on connectivity
        if connectivity_ratio < 1:
            self.zpd_estimate["metacognitive_skills"] = "low"
            self.zpd_estimate["scaffolding_needs"]["metacognitive"] = "high"
        elif connectivity_ratio > 2:
            self.zpd_estimate["metacognitive_skills"] = "high"
            self.zpd_estimate["scaffolding_needs"]["metacognitive"] = "low"
        
        # Check for relation labels
        has_relation_labels = any(edge.get("relation") for edge in edges)
        
        if has_relation_labels:
            self.zpd_estimate["technical_proficiency"] = "high"
        else:
            self.zpd_estimate["scaffolding_needs"]["procedural"] = "high"
        
        # If this is not the first map, compare with previous maps
        previous_maps = session_state.get("previous_concept_maps", [])
        
        if previous_maps:
            # Get the most recent previous map
            prev_map = previous_maps[-1]
            prev_nodes = prev_map.get("nodes", [])
            prev_edges = prev_map.get("edges", [])
            
            # Calculate growth
            node_growth = num_nodes - len(prev_nodes)
            edge_growth = num_edges - len(prev_edges)
            
            # Update ZPD based on growth
            if node_growth > 3 and edge_growth > 5:
                # Significant improvement
                self.zpd_estimate["conceptual_understanding"] = "high"
                self.zpd_estimate["metacognitive_skills"] = "high"
                
                # Reduce scaffolding needs
                for scaffold_type in self.zpd_estimate["scaffolding_needs"]:
                    if self.zpd_estimate["scaffolding_needs"][scaffold_type] == "high":
                        self.zpd_estimate["scaffolding_needs"][scaffold_type] = "medium"
            elif node_growth < 0 or edge_growth < 0:
                # Regression or confusion
                self.zpd_estimate["scaffolding_needs"]["strategic"] = "high"
                self.zpd_estimate["scaffolding_needs"]["metacognitive"] = "high"
        
        logger.debug(f"Updated ZPD estimate from concept map: {self.zpd_estimate}")
    
    def _generate_final_assessment(self, session_state: Dict[str, Any]) -> str:
        """
        Generate a final assessment of the learner's progress.
        
        Args:
            session_state: Current session state
            
        Returns:
            Final assessment text
        """
        # Extract relevant information from session state
        num_maps = len(session_state.get("previous_concept_maps", [])) + (1 if session_state.get("current_concept_map") else 0)
        num_responses = len(session_state.get("user_responses", []))
        
        # Generate assessment based on ZPD estimate
        conceptual = self.zpd_estimate["conceptual_understanding"]
        metacognitive = self.zpd_estimate["metacognitive_skills"]
        technical = self.zpd_estimate["technical_proficiency"]
        
        assessment = (
            "Based on your work throughout this session, I've observed the following:\n\n"
        )
        
        # Conceptual understanding assessment
        if conceptual == "high":
            assessment += (
                "Your conceptual understanding appears strong. You've demonstrated the ability to "
                "identify key concepts and establish meaningful relationships between them. "
                "Your concept maps show depth and nuance in your understanding of the topic.\n\n"
            )
        elif conceptual == "medium":
            assessment += (
                "You've shown a solid grasp of the main concepts in this topic. "
                "With continued practice, you can further develop the connections between "
                "concepts and explore more complex relationships.\n\n"
            )
        else:
            assessment += (
                "You're beginning to develop your understanding of this topic. "
                "Consider focusing on identifying the core concepts first, then gradually "
                "building connections between them as your understanding grows.\n\n"
            )
        
        # Metacognitive skills assessment
        if metacognitive == "high":
            assessment += (
                "Your reflective thinking skills are well-developed. You've shown the ability "
                "to evaluate your own understanding, identify gaps, and make thoughtful revisions "
                "to your concept maps.\n\n"
            )
        elif metacognitive == "medium":
            assessment += (
                "You've demonstrated some reflective thinking in your approach. "
                "Continue to ask yourself questions about why concepts are related and "
                "how they fit into the bigger picture.\n\n"
            )
        else:
            assessment += (
                "Developing your reflective thinking skills will help you create more "
                "comprehensive concept maps. Try to regularly pause and ask yourself what "
                "you understand well and what areas need more clarity.\n\n"
            )
        
        # Technical proficiency assessment
        if technical == "high":
            assessment += (
                "You appear comfortable with the concept mapping process and tools. "
                "Your maps are well-structured and make good use of the format.\n\n"
            )
        elif technical == "medium":
            assessment += (
                "You've developed a functional understanding of concept mapping techniques. "
                "With practice, you'll become more fluent in representing your knowledge visually.\n\n"
            )
        else:
            assessment += (
                "As you continue to practice concept mapping, focus on the basic structure: "
                "concepts as nodes, relationships as labeled connections between them. "
                "This foundation will help you express your understanding more clearly.\n\n"
            )
        
        # Overall progress
        if num_maps > 1:
            assessment += (
                f"Over the course of creating {num_maps} concept maps, I've seen growth in your "
                "approach and understanding. Continue to use concept mapping as a tool for "
                "organizing and reflecting on your knowledge."
            )
        else:
            assessment += (
                "This initial concept mapping exercise provides a foundation for future learning. "
                "Regular practice with concept mapping will help you develop both your understanding "
                "of the topic and your ability to represent knowledge visually."
            )
        
        return assessment
    
    def get_learner_profile(self) -> Dict[str, Any]:
        """
        Get the current learner profile.
        
        Returns:
            The current learner profile
        """
        return self.learner_profile
    
    def get_zpd_estimate(self) -> Dict[str, Any]:
        """
        Get the current ZPD estimate.
        
        Returns:
            The current ZPD estimate
        """
        return self.zpd_estimate
