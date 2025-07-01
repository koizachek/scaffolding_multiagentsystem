"""
Strategic Scaffolding Agent

This module provides the strategic scaffolding agent that offers structured support
for planning, sequencing, and selecting learning strategies.
"""

import logging
import random
from typing import Dict, List, Any, Optional, Callable

from MAS.agents.base_agent import BaseAgent
from MAS.config.scaffolding_config import DEFAULT_SCAFFOLDING_CONFIG, SCAFFOLDING_FOLLOWUP_TEMPLATES
from MAS.utils.scaffolding_utils import analyze_concept_map, generate_default_prompts

logger = logging.getLogger(__name__)

class StrategicScaffoldingAgent(BaseAgent):
    """
    Strategic scaffolding agent for the multi-agent scaffolding system.
    
    This agent offers structured, temporary support for planning, sequencing,
    and selecting learning strategies.
    """
    
    def __init__(self, 
                name: str,
                config: Dict[str, Any],
                logger_callback: Optional[Callable] = None):
        """
        Initialize the strategic scaffolding agent.
        
        Args:
            name: Name of the agent
            config: Agent configuration
            logger_callback: Callback function for logging
        """
        super().__init__(name, "strategic_scaffolding", config, logger_callback)
        
        # Initialize scaffolding level
        self.scaffolding_level = "medium"  # low, medium, high
        
        # Initialize scaffolding history
        self.scaffolding_history = []
        
        # Load scaffolding configuration
        self.scaffolding_config = DEFAULT_SCAFFOLDING_CONFIG.get("strategic", {})
        
        logger.info(f"Initialized strategic scaffolding agent: {name}")
    
    def _process_impl(self, 
                     input_data: Dict[str, Any], 
                     context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input data and generate strategic scaffolding.
        
        Args:
            input_data: Input data to process
            context: Context information
            
        Returns:
            Response data with strategic scaffolding
        """
        # Extract input type
        input_type = input_data.get("type", "unknown")
        
        # Get session state
        session_state = context.get("session_state", {})
        
        # Update scaffolding level based on ZPD estimate if available
        zpd_estimate = session_state.get("zpd_estimate", {})
        if zpd_estimate and "scaffolding_needs" in zpd_estimate:
            strategic_need = zpd_estimate["scaffolding_needs"].get("strategic")
            if strategic_need:
                self.scaffolding_level = strategic_need
        
        # Process based on input type
        if input_type == "concept_map_submission":
            return self._handle_concept_map_submission(input_data, context)
        elif input_type == "generate_scaffolding_prompts":
            return self._handle_generate_prompts(input_data, context)
        elif input_type == "generate_follow_up":
            return self._handle_generate_follow_up(input_data, context)
        elif input_type == "conclude_scaffolding":
            return self._handle_conclude_scaffolding(input_data, context)
        elif input_type == "final_round":
            return self._handle_final_round(input_data, context)
        else:
            logger.warning(f"Unknown input type: {input_type}")
            return {
                "response": None,
                "agent_type": self.agent_type,
                "status": "error"
            }
    
    def _handle_concept_map_submission(self, 
                                      input_data: Dict[str, Any], 
                                      context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle concept map submission by providing strategic scaffolding.
        
        Args:
            input_data: Input data containing concept map
            context: Context information
            
        Returns:
            Response data with strategic scaffolding
        """
        # Extract concept map data
        concept_map_data = input_data.get("concept_map_data")
        
        if not concept_map_data:
            return {
                "response": None,
                "agent_type": self.agent_type,
                "status": "error"
            }
        
        logger.info("Generating strategic scaffolding for concept map")
        
        # Get session state
        session_state = context.get("session_state", {})
        
        # Get current round
        current_round = session_state.get("current_round", 0)
        
        # Analyze the concept map
        map_analysis = analyze_concept_map(concept_map_data)
        
        # Generate strategic scaffolding based on concept map and scaffolding level
        scaffolding = self._generate_strategic_scaffolding(
            concept_map_data, 
            current_round,
            session_state,
            map_analysis
        )
        
        # Record scaffolding provided
        self.scaffolding_history.append({
            "round": current_round,
            "scaffolding_level": self.scaffolding_level,
            "scaffolding_provided": scaffolding,
            "map_analysis": map_analysis
        })
        
        # Adjust scaffolding level for next round (fade scaffolding)
        self._adjust_scaffolding_level(session_state)
        
        return {
            "response": scaffolding,
            "agent_type": self.agent_type,
            "status": "success",
            "scaffolding_level": self.scaffolding_level,
            "reasoning": f"Provided strategic scaffolding at {self.scaffolding_level} level",
            "map_analysis": map_analysis
        }
    
    def _handle_final_round(self, 
                           input_data: Dict[str, Any], 
                           context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle final round by providing strategic next steps.
        
        Args:
            input_data: Input data
            context: Context information
            
        Returns:
            Response data with strategic next steps
        """
        logger.info("Generating strategic next steps for final round")
        
        # Get session state
        session_state = context.get("session_state", {})
        
        # Generate strategic next steps
        next_steps = self._generate_strategic_next_steps(session_state)
        
        return {
            "response": next_steps,
            "agent_type": self.agent_type,
            "status": "success"
        }
    
    def _generate_strategic_scaffolding(self, 
                                       concept_map_data: Dict[str, Any],
                                       current_round: int,
                                       session_state: Dict[str, Any],
                                       map_analysis: Dict[str, Any] = None) -> str:
        """
        Generate strategic scaffolding based on concept map and scaffolding level.
        
        Args:
            concept_map_data: Concept map data
            current_round: Current round number
            session_state: Current session state
            map_analysis: Analysis of the concept map (optional)
            
        Returns:
            Strategic scaffolding text
        """
        # Extract nodes and edges
        nodes = concept_map_data.get("nodes", [])
        edges = concept_map_data.get("edges", [])
        
        # Get previous concept map if available
        previous_maps = session_state.get("previous_concept_maps", [])
        previous_map = previous_maps[-1] if previous_maps else None
        
        # If map_analysis is not provided, generate it
        if not map_analysis:
            map_analysis = analyze_concept_map(concept_map_data)
        
        # Create analysis dictionary for prompt generation
        analysis = {
            "map_analysis": map_analysis,
            "current_round": current_round,
            "previous_map": previous_map
        }
        
        # Get prompt templates from config
        prompt_templates = self.scaffolding_config.get("prompt_templates", {})
        intensity_templates = prompt_templates.get(self.scaffolding_level, [])
        
        # If no templates are available, fall back to default generation
        if not intensity_templates:
            # Generate scaffolding based on level
            if self.scaffolding_level == "high":
                return self._generate_high_level_scaffolding(nodes, edges, previous_map, current_round)
            elif self.scaffolding_level == "medium":
                return self._generate_medium_level_scaffolding(nodes, edges, previous_map, current_round)
            else:  # low
                return self._generate_low_level_scaffolding(nodes, edges, previous_map, current_round)
        
        # Select a template and format it with map analysis data
        selected_template = random.choice(intensity_templates)
        
        try:
            # Format the template with map analysis data
            formatted_prompt = selected_template.format(
                node_count=map_analysis.get("node_count", 0),
                edge_count=map_analysis.get("edge_count", 0),
                connectivity_ratio=map_analysis.get("connectivity_ratio", 0),
                isolated_node_count=map_analysis.get("isolated_node_count", 0)
            )
            
            return formatted_prompt
        except KeyError as e:
            logger.warning(f"Error formatting prompt template: {e}")
            
            # Fall back to default generation
            if self.scaffolding_level == "high":
                return self._generate_high_level_scaffolding(nodes, edges, previous_map, current_round)
            elif self.scaffolding_level == "medium":
                return self._generate_medium_level_scaffolding(nodes, edges, previous_map, current_round)
            else:  # low
                return self._generate_low_level_scaffolding(nodes, edges, previous_map, current_round)
    
    def _generate_high_level_scaffolding(self, 
                                        nodes: List[str],
                                        edges: List[Dict[str, str]],
                                        previous_map: Optional[Dict[str, Any]],
                                        current_round: int) -> str:
        """
        Generate high-level strategic scaffolding.
        
        Args:
            nodes: List of concept nodes
            edges: List of edges between concepts
            previous_map: Previous concept map data
            current_round: Current round number
            
        Returns:
            High-level strategic scaffolding text
        """
        # This is a simplified implementation
        # In a real implementation, this would provide more detailed and personalized scaffolding
        
        # Start with a supportive introduction
        scaffolding = "Let's work on improving your concept map with a step-by-step approach:\n\n"
        
        # Provide specific steps based on the current state of the map
        if len(nodes) < 5:
            scaffolding += (
                "1. Start by identifying 3-5 more key concepts related to your topic. "
                "Look for important terms, ideas, or principles that are missing.\n\n"
                "2. For each new concept you add, think about how it connects to your existing concepts. "
                "Try to add at least one connection for each new concept.\n\n"
                "3. Label each connection to show the relationship between concepts. "
                "For example, 'causes', 'is part of', or 'influences'.\n\n"
            )
        elif len(edges) < len(nodes):
            scaffolding += (
                "1. Your map has several concepts but could use more connections between them. "
                "Review each concept and ask yourself: 'What other concepts is this related to?'\n\n"
                "2. Add at least 3-5 new connections between your existing concepts.\n\n"
                "3. Make sure each connection has a clear label that describes the relationship.\n\n"
                "4. Consider organizing your concepts into groups or clusters of related ideas.\n\n"
            )
        else:
            scaffolding += (
                "1. Your concept map has a good number of concepts and connections. "
                "Now, focus on refining the relationships between them.\n\n"
                "2. Review each connection and make sure the relationship label is specific and accurate.\n\n"
                "3. Look for opportunities to add cross-links between different branches of your map.\n\n"
                "4. Consider adding examples for some of your concepts to illustrate their meaning.\n\n"
            )
        
        # Add a reflection prompt
        scaffolding += (
            "After making these changes, take a moment to review your map as a whole. "
            "Does it accurately represent your understanding of the topic? "
            "Are there any important concepts or relationships still missing?"
        )
        
        return scaffolding
    
    def _generate_medium_level_scaffolding(self, 
                                          nodes: List[str],
                                          edges: List[Dict[str, str]],
                                          previous_map: Optional[Dict[str, Any]],
                                          current_round: int) -> str:
        """
        Generate medium-level strategic scaffolding.
        
        Args:
            nodes: List of concept nodes
            edges: List of edges between concepts
            previous_map: Previous concept map data
            current_round: Current round number
            
        Returns:
            Medium-level strategic scaffolding text
        """
        # This is a simplified implementation
        # In a real implementation, this would provide more detailed and personalized scaffolding
        
        # Start with a supportive introduction
        scaffolding = "Here are some strategies to enhance your concept map:\n\n"
        
        # Provide general guidance based on the current state of the map
        if len(nodes) < 5:
            scaffolding += (
                "- Consider expanding your map by adding more key concepts related to your topic.\n\n"
                "- Think about the connections between your concepts and make sure to label these relationships.\n\n"
                "- Try organizing your concepts in a way that shows their hierarchy or importance.\n\n"
            )
        elif len(edges) < len(nodes):
            scaffolding += (
                "- Your map has several concepts but could benefit from more connections between them.\n\n"
                "- Look for relationships between concepts that aren't currently connected.\n\n"
                "- Make sure your connection labels clearly describe the relationship between concepts.\n\n"
                "- Consider if any concepts could be grouped together or organized differently.\n\n"
            )
        else:
            scaffolding += (
                "- Your map shows good connectivity between concepts.\n\n"
                "- Consider refining your relationship labels to be more specific and informative.\n\n"
                "- Look for opportunities to add cross-links between different areas of your map.\n\n"
                "- Think about whether any important concepts or relationships are still missing.\n\n"
            )
        
        # Add a reflection prompt
        scaffolding += (
            "As you revise your map, consider: What is the main idea or concept that everything connects to? "
            "How do the relationships between concepts help explain the topic as a whole?"
        )
        
        return scaffolding
    
    def _generate_low_level_scaffolding(self, 
                                       nodes: List[str],
                                       edges: List[Dict[str, str]],
                                       previous_map: Optional[Dict[str, Any]],
                                       current_round: int) -> str:
        """
        Generate low-level strategic scaffolding.
        
        Args:
            nodes: List of concept nodes
            edges: List of edges between concepts
            previous_map: Previous concept map data
            current_round: Current round number
            
        Returns:
            Low-level strategic scaffolding text
        """
        # This is a simplified implementation
        # In a real implementation, this would provide more detailed and personalized scaffolding
        
        # Start with a supportive introduction
        scaffolding = "As you continue developing your concept map, consider these questions:\n\n"
        
        # Provide open-ended questions to prompt thinking
        scaffolding += (
            "- What other important concepts might be related to this topic?\n\n"
            "- How are the concepts in your map connected to each other?\n\n"
            "- Are there different ways you could organize these concepts to show their relationships?\n\n"
            "- What do the connections between concepts tell you about the topic as a whole?\n\n"
        )
        
        # Add a reflection prompt
        scaffolding += (
            "Take some time to reflect on your map and consider what it reveals about your understanding "
            "of the topic and what areas you might want to explore further."
        )
        
        return scaffolding
    
    def _generate_strategic_next_steps(self, session_state: Dict[str, Any]) -> str:
        """
        Generate strategic next steps for the final round.
        
        Args:
            session_state: Current session state
            
        Returns:
            Strategic next steps text
        """
        # This is a simplified implementation
        # In a real implementation, this would provide more personalized next steps
        
        next_steps = (
            "Now that you've completed this concept mapping exercise, here are some strategic next steps "
            "to continue developing your understanding:\n\n"
            
            "1. **Review and Reflect**: Take time to review your final concept map and reflect on how your "
            "understanding has evolved throughout this process. What new connections or insights did you discover?\n\n"
            
            "2. **Identify Knowledge Gaps**: Look for areas in your map that seem less developed or where "
            "you had difficulty establishing connections. These may be areas for further study.\n\n"
            
            "3. **Expand Your Map**: Consider how you might expand your concept map by integrating new "
            "information from additional resources or connecting it to other topics you're studying.\n\n"
            
            "4. **Apply Your Knowledge**: Think about how the concepts and relationships in your map "
            "apply to real-world situations or problems. How might you use this knowledge?\n\n"
            
            "5. **Share and Discuss**: Consider sharing your concept map with peers or instructors to "
            "get feedback and discuss different perspectives on the topic.\n\n"
            
            "Remember that concept mapping is an iterative process, and your understanding will continue "
            "to develop as you engage with the material in different ways."
        )
        
        return next_steps
    
    def _adjust_scaffolding_level(self, session_state: Dict[str, Any]) -> None:
        """
        Adjust scaffolding level based on learner progress (fading).
        
        Args:
            session_state: Current session state
        """
        # This is a simplified implementation of scaffolding fading
        # In a real implementation, this would use more sophisticated analysis
        
        # Get current round
        current_round = session_state.get("current_round", 0)
        
        # Get ZPD estimate
        zpd_estimate = session_state.get("zpd_estimate", {})
        
        # If we have a ZPD estimate with scaffolding needs, use that
        if zpd_estimate and "scaffolding_needs" in zpd_estimate:
            strategic_need = zpd_estimate["scaffolding_needs"].get("strategic")
            if strategic_need:
                # Only reduce scaffolding if current level is higher than the estimated need
                if self._scaffolding_level_value(self.scaffolding_level) > self._scaffolding_level_value(strategic_need):
                    self.scaffolding_level = strategic_need
                return
        
        # Otherwise, gradually reduce scaffolding level based on round
        if current_round >= 2 and self.scaffolding_level == "high":
            self.scaffolding_level = "medium"
            logger.info("Reduced scaffolding level from high to medium")
        elif current_round >= 3 and self.scaffolding_level == "medium":
            self.scaffolding_level = "low"
            logger.info("Reduced scaffolding level from medium to low")
    
    def _scaffolding_level_value(self, level: str) -> int:
        """
        Convert scaffolding level string to numeric value for comparison.
        
        Args:
            level: Scaffolding level string
            
        Returns:
            Numeric value (1 for low, 2 for medium, 3 for high)
        """
        if level == "high":
            return 3
        elif level == "medium":
            return 2
        else:  # low
            return 1
    
    def get_scaffolding_level(self) -> str:
        """
        Get the current scaffolding level.
        
        Returns:
            The current scaffolding level
        """
        return self.scaffolding_level
    
    def _handle_generate_prompts(self, 
                                input_data: Dict[str, Any], 
                                context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle request to generate scaffolding prompts.
        
        Args:
            input_data: Input data containing analysis and scaffolding intensity
            context: Context information
            
        Returns:
            Response data with scaffolding prompts
        """
        # Extract analysis and intensity
        analysis = input_data.get("analysis", {})
        intensity = input_data.get("scaffolding_intensity", self.scaffolding_level)
        
        logger.info(f"Generating strategic scaffolding prompts at {intensity} intensity")
        
        # Generate prompts using utility function
        prompts = generate_default_prompts("strategic", intensity, analysis)
        
        # If no prompts were generated, use templates from config
        if not prompts:
            # Get prompt templates from config
            prompt_templates = self.scaffolding_config.get("prompt_templates", {})
            intensity_templates = prompt_templates.get(intensity, [])
            
            # Select up to 3 templates
            if intensity_templates:
                if len(intensity_templates) > 3:
                    prompts = random.sample(intensity_templates, 3)
                else:
                    prompts = intensity_templates
        
        # Format prompts with map analysis data if needed
        formatted_prompts = []
        map_analysis = analysis.get("map_analysis", {})
        
        for prompt in prompts:
            try:
                # Format the prompt with map analysis data
                formatted_prompt = prompt.format(
                    node_count=map_analysis.get("node_count", 0),
                    edge_count=map_analysis.get("edge_count", 0),
                    connectivity_ratio=map_analysis.get("connectivity_ratio", 0),
                    isolated_node_count=map_analysis.get("isolated_node_count", 0)
                )
                
                formatted_prompts.append(formatted_prompt)
            except KeyError:
                # If formatting fails, use the prompt as is
                formatted_prompts.append(prompt)
        
        return {
            "prompts": formatted_prompts,
            "agent_type": self.agent_type,
            "status": "success",
            "scaffolding_level": intensity
        }
    
    def _handle_generate_follow_up(self, 
                                  input_data: Dict[str, Any], 
                                  context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle request to generate a follow-up question.
        
        Args:
            input_data: Input data containing learner response
            context: Context information
            
        Returns:
            Response data with follow-up question
        """
        # Extract learner response and intensity
        learner_response = input_data.get("learner_response", "")
        intensity = input_data.get("scaffolding_intensity", self.scaffolding_level)
        
        logger.info("Generating strategic scaffolding follow-up")
        
        # Get follow-up templates from config
        follow_up_templates = SCAFFOLDING_FOLLOWUP_TEMPLATES.get("strategic", [])
        
        # Select a follow-up template
        if follow_up_templates:
            follow_up = random.choice(follow_up_templates)
        else:
            # Fallback follow-up
            follow_up = "That's interesting. Could you elaborate on how that approach helped you organize your concepts?"
        
        return {
            "follow_up": follow_up,
            "agent_type": self.agent_type,
            "status": "success",
            "scaffolding_level": intensity
        }
    
    def _handle_conclude_scaffolding(self, 
                                    input_data: Dict[str, Any], 
                                    context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle request to conclude a scaffolding interaction.
        
        Args:
            input_data: Input data containing interaction history
            context: Context information
            
        Returns:
            Response data with conclusion message
        """
        # Extract interaction history
        interaction_history = input_data.get("interaction_history", [])
        
        logger.info("Concluding strategic scaffolding interaction")
        
        # Generate conclusion based on interaction history
        conclusion = "Thank you for reflecting on your strategic approach to concept mapping. Consider applying these insights as you revise your map. Think about how you might organize your concepts more effectively and what strategies you could use to identify important relationships."
        
        return {
            "conclusion": conclusion,
            "agent_type": self.agent_type,
            "status": "success"
        }
    
    def get_scaffolding_history(self) -> List[Dict[str, Any]]:
        """
        Get the scaffolding history.
        
        Returns:
            The scaffolding history
        """
        return self.scaffolding_history
