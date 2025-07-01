"""
Metacognitive Scaffolding Agent

This module provides the metacognitive scaffolding agent that prompts learners
to plan, monitor, and self-regulate their thinking.
"""

import logging
import random
from typing import Dict, List, Any, Optional, Callable

from MAS.agents.base_agent import BaseAgent
from MAS.config.scaffolding_config import DEFAULT_SCAFFOLDING_CONFIG, SCAFFOLDING_FOLLOWUP_TEMPLATES
from MAS.utils.scaffolding_utils import analyze_concept_map, generate_default_prompts

logger = logging.getLogger(__name__)

class MetacognitiveScaffoldingAgent(BaseAgent):
    """
    Metacognitive scaffolding agent for the multi-agent scaffolding system.
    
    This agent prompts learners to plan, monitor, and self-regulate their thinking,
    encouraging goal setting, self-assessment, and reflection.
    """
    
    def __init__(self, 
                name: str,
                config: Dict[str, Any],
                logger_callback: Optional[Callable] = None):
        """
        Initialize the metacognitive scaffolding agent.
        
        Args:
            name: Name of the agent
            config: Agent configuration
            logger_callback: Callback function for logging
        """
        super().__init__(name, "metacognitive_scaffolding", config, logger_callback)
        
        # Initialize scaffolding level
        self.scaffolding_level = "medium"  # low, medium, high
        
        # Initialize scaffolding history
        self.scaffolding_history = []
        
        # Load scaffolding configuration
        self.scaffolding_config = DEFAULT_SCAFFOLDING_CONFIG.get("metacognitive", {})
        
        # Initialize reflection prompts
        self.reflection_prompts = {
            "planning": [
                "What are your goals for this concept map?",
                "What key concepts do you want to include?",
                "How will you organize your concept map?",
                "What connections do you want to emphasize?",
                "What aspects of the topic do you find most challenging to understand?"
            ],
            "monitoring": [
                "How well does your map represent your understanding of the topic?",
                "Which parts of your map are you most confident about?",
                "Which parts of your map are you least confident about?",
                "Are there any concepts or relationships that you're struggling to represent?",
                "How does your current map compare to what you initially planned?"
            ],
            "evaluating": [
                "What have you learned from creating this concept map?",
                "What new connections or insights did you discover?",
                "What areas of your understanding have improved?",
                "What areas still need development?",
                "How might you approach concept mapping differently next time?"
            ]
        }
        
        logger.info(f"Initialized metacognitive scaffolding agent: {name}")
    
    def _process_impl(self, 
                     input_data: Dict[str, Any], 
                     context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input data and generate metacognitive scaffolding.
        
        Args:
            input_data: Input data to process
            context: Context information
            
        Returns:
            Response data with metacognitive scaffolding
        """
        # Extract input type
        input_type = input_data.get("type", "unknown")
        
        # Get session state
        session_state = context.get("session_state", {})
        
        # Update scaffolding level based on ZPD estimate if available
        zpd_estimate = session_state.get("zpd_estimate", {})
        if zpd_estimate and "scaffolding_needs" in zpd_estimate:
            metacognitive_need = zpd_estimate["scaffolding_needs"].get("metacognitive")
            if metacognitive_need:
                self.scaffolding_level = metacognitive_need
        
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
        Handle concept map submission by providing metacognitive scaffolding.
        
        Args:
            input_data: Input data containing concept map
            context: Context information
            
        Returns:
            Response data with metacognitive scaffolding
        """
        # Extract concept map data
        concept_map_data = input_data.get("concept_map_data")
        
        if not concept_map_data:
            return {
                "response": None,
                "agent_type": self.agent_type,
                "status": "error"
            }
        
        logger.info("Generating metacognitive scaffolding for concept map")
        
        # Get session state
        session_state = context.get("session_state", {})
        
        # Get current round
        current_round = session_state.get("current_round", 0)
        
        # Analyze the concept map
        map_analysis = analyze_concept_map(concept_map_data)
        
        # Generate metacognitive scaffolding based on concept map and scaffolding level
        scaffolding = self._generate_metacognitive_scaffolding(
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
            "reasoning": f"Provided metacognitive scaffolding at {self.scaffolding_level} level",
            "map_analysis": map_analysis
        }
    
    def _handle_final_round(self, 
                           input_data: Dict[str, Any], 
                           context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle final round by providing metacognitive reflection prompts.
        
        Args:
            input_data: Input data
            context: Context information
            
        Returns:
            Response data with metacognitive reflection prompts
        """
        logger.info("Generating metacognitive reflection prompts for final round")
        
        # Get session state
        session_state = context.get("session_state", {})
        
        # Generate metacognitive reflection prompts
        reflection_prompts = self._generate_final_reflection_prompts(session_state)
        
        return {
            "response": reflection_prompts,
            "agent_type": self.agent_type,
            "status": "success"
        }
    
    def _generate_metacognitive_scaffolding(self, 
                                          concept_map_data: Dict[str, Any],
                                          current_round: int,
                                          session_state: Dict[str, Any],
                                          map_analysis: Dict[str, Any] = None) -> str:
        """
        Generate metacognitive scaffolding based on concept map and scaffolding level.
        
        Args:
            concept_map_data: Concept map data
            current_round: Current round number
            session_state: Current session state
            
        Returns:
            Metacognitive scaffolding text
        """
        # Determine the metacognitive focus based on the round
        if current_round == 0:
            focus = "planning"
        elif current_round == session_state.get("max_rounds", 4) - 1:
            focus = "evaluating"
        else:
            focus = "monitoring"
        
        # Generate scaffolding based on level
        if self.scaffolding_level == "high":
            return self._generate_high_level_metacognitive_scaffolding(concept_map_data, focus, current_round)
        elif self.scaffolding_level == "medium":
            return self._generate_medium_level_metacognitive_scaffolding(concept_map_data, focus, current_round)
        else:  # low
            return self._generate_low_level_metacognitive_scaffolding(concept_map_data, focus, current_round)
    
    def _generate_high_level_metacognitive_scaffolding(self, 
                                                     concept_map_data: Dict[str, Any],
                                                     focus: str,
                                                     current_round: int) -> str:
        """
        Generate high-level metacognitive scaffolding.
        
        Args:
            concept_map_data: Concept map data
            focus: Metacognitive focus (planning, monitoring, evaluating)
            current_round: Current round number
            
        Returns:
            High-level metacognitive scaffolding text
        """
        # This is a simplified implementation
        # In a real implementation, this would provide more detailed and personalized scaffolding
        
        # Extract nodes and edges for analysis
        nodes = concept_map_data.get("nodes", [])
        edges = concept_map_data.get("edges", [])
        
        # Start with a supportive introduction
        scaffolding = "Let's take some time to reflect on your thinking process:\n\n"
        
        # Add specific prompts based on the focus
        if focus == "planning":
            scaffolding += (
                "**Planning Your Concept Map:**\n\n"
                "1. What are your specific goals for this concept map? What do you want to understand better?\n\n"
                "2. Before you continue developing your map, take a moment to identify the 3-5 most important concepts "
                "related to this topic. Why do you think these are the most important?\n\n"
                "3. How do you plan to organize these concepts? Will you use a hierarchical structure, a network, "
                "or another arrangement? Why is this organization appropriate for the topic?\n\n"
                "4. What types of relationships do you expect to find between these concepts? How will you represent "
                "these relationships in your map?\n\n"
                "5. What aspects of this topic do you find most challenging to understand? How might creating "
                "this concept map help you address these challenges?\n\n"
            )
        elif focus == "monitoring":
            scaffolding += (
                "**Monitoring Your Progress:**\n\n"
                f"1. Looking at your current map with {len(nodes)} concepts and {len(edges)} relationships, "
                f"how well does it represent your understanding of the topic? What's missing or incomplete?\n\n"
                "2. Which parts of your map are you most confident about? Why?\n\n"
                "3. Which parts are you least confident about or find confusing? What specific questions do you have?\n\n"
                "4. How has your understanding changed since you started creating this map?\n\n"
                "5. What strategies could you use to improve the areas you're less confident about?\n\n"
            )
        else:  # evaluating
            scaffolding += (
                "**Evaluating Your Learning:**\n\n"
                "1. What new insights or connections have you discovered through creating this concept map?\n\n"
                "2. How has your understanding of the topic evolved since you began this exercise?\n\n"
                "3. What specific areas of your understanding have improved the most?\n\n"
                "4. What questions or uncertainties do you still have about this topic?\n\n"
                "5. How might you use what you've learned from this concept mapping exercise in the future?\n\n"
            )
        
        # Add a metacognitive strategy
        scaffolding += (
            "**Metacognitive Strategy:**\n\n"
            "Before making your next revision, try this approach:\n\n"
        )
        
        if focus == "planning":
            scaffolding += (
                "1. Write down your top 3 goals for your concept map\n"
                "2. List the key concepts you want to include\n"
                "3. Sketch a rough organization of how these concepts relate to each other\n"
                "4. Identify any areas where you need more information or clarity\n"
                "5. Use this plan to guide your next revision\n\n"
            )
        elif focus == "monitoring":
            scaffolding += (
                "1. Review your map and mark concepts/relationships you're confident about with a '+'\n"
                "2. Mark concepts/relationships you're uncertain about with a '?'\n"
                "3. For each '?', write down a specific question or what's unclear\n"
                "4. Identify resources or strategies that could help clarify these uncertainties\n"
                "5. Focus your next revision on addressing these specific areas\n\n"
            )
        else:  # evaluating
            scaffolding += (
                "1. Compare your final map to your initial understanding of the topic\n"
                "2. Identify the 3 most important insights you've gained\n"
                "3. Note any misconceptions that you've corrected\n"
                "4. List questions you still have about the topic\n"
                "5. Consider how you might apply this knowledge in different contexts\n\n"
            )
        
        # Add a reflection prompt
        scaffolding += (
            "Take a few minutes to think about these questions before proceeding. "
            "Your responses will help guide your next steps and deepen your understanding."
        )
        
        return scaffolding
    
    def _generate_medium_level_metacognitive_scaffolding(self, 
                                                       concept_map_data: Dict[str, Any],
                                                       focus: str,
                                                       current_round: int) -> str:
        """
        Generate medium-level metacognitive scaffolding.
        
        Args:
            concept_map_data: Concept map data
            focus: Metacognitive focus (planning, monitoring, evaluating)
            current_round: Current round number
            
        Returns:
            Medium-level metacognitive scaffolding text
        """
        # This is a simplified implementation
        # In a real implementation, this would provide more detailed and personalized scaffolding
        
        # Start with a supportive introduction
        scaffolding = "Let's reflect on your thinking process as you develop your concept map:\n\n"
        
        # Add specific prompts based on the focus
        if focus == "planning":
            scaffolding += (
                "**Reflection Questions:**\n\n"
                "- What are your main goals for this concept map?\n\n"
                "- What key concepts do you want to include?\n\n"
                "- How do you plan to organize these concepts?\n\n"
                "- What aspects of this topic do you find most challenging?\n\n"
            )
        elif focus == "monitoring":
            scaffolding += (
                "**Reflection Questions:**\n\n"
                "- How well does your map represent your understanding of the topic?\n\n"
                "- Which parts of your map are you most confident about?\n\n"
                "- Which parts are you least confident about?\n\n"
                "- What could you do to improve the areas you're less confident about?\n\n"
            )
        else:  # evaluating
            scaffolding += (
                "**Reflection Questions:**\n\n"
                "- What new insights have you gained through creating this concept map?\n\n"
                "- How has your understanding of the topic changed?\n\n"
                "- What questions do you still have about this topic?\n\n"
                "- How might you use what you've learned in the future?\n\n"
            )
        
        # Add a metacognitive strategy
        scaffolding += (
            "**Metacognitive Strategy:**\n\n"
        )
        
        if focus == "planning":
            scaffolding += (
                "Before your next revision, take a few minutes to outline your goals and the key concepts "
                "you want to include. This planning will help guide your work.\n\n"
            )
        elif focus == "monitoring":
            scaffolding += (
                "As you review your map, identify areas you're confident about and areas where you're less certain. "
                "Focus your next revision on clarifying these uncertain areas.\n\n"
            )
        else:  # evaluating
            scaffolding += (
                "Compare your current understanding to your initial understanding of the topic. "
                "What are the most important things you've learned? What questions do you still have?\n\n"
            )
        
        # Add a reflection prompt
        scaffolding += (
            "Consider these questions as you continue developing your concept map. "
            "This reflection will help you deepen your understanding of the topic."
        )
        
        return scaffolding
    
    def _generate_low_level_metacognitive_scaffolding(self, 
                                                    concept_map_data: Dict[str, Any],
                                                    focus: str,
                                                    current_round: int) -> str:
        """
        Generate low-level metacognitive scaffolding.
        
        Args:
            concept_map_data: Concept map data
            focus: Metacognitive focus (planning, monitoring, evaluating)
            current_round: Current round number
            
        Returns:
            Low-level metacognitive scaffolding text
        """
        # This is a simplified implementation
        # In a real implementation, this would provide more detailed and personalized scaffolding
        
        # Start with a supportive introduction
        scaffolding = "As you work on your concept map, consider these reflection questions:\n\n"
        
        # Select 2-3 prompts from the appropriate category
        prompts = self.reflection_prompts.get(focus, [])
        selected_prompts = prompts[:min(3, len(prompts))]
        
        for prompt in selected_prompts:
            scaffolding += f"- {prompt}\n\n"
        
        # Add a gentle encouragement
        scaffolding += (
            "Taking time to reflect on these questions can help you deepen your understanding "
            "and improve your concept map."
        )
        
        return scaffolding
    
    def _generate_final_reflection_prompts(self, session_state: Dict[str, Any]) -> str:
        """
        Generate metacognitive reflection prompts for the final round.
        
        Args:
            session_state: Current session state
            
        Returns:
            Metacognitive reflection prompts text
        """
        # This is a simplified implementation
        # In a real implementation, this would provide more personalized prompts
        
        reflection_prompts = (
            "Now that you've completed your concept map, take some time for final reflection:\n\n"
            
            "**Learning Process Reflection:**\n\n"
            
            "1. **Knowledge Development**: How has your understanding of this topic evolved through "
            "the process of creating and revising your concept map? What new connections or insights "
            "did you discover?\n\n"
            
            "2. **Metacognitive Awareness**: What have you learned about your own thinking and learning "
            "process through this exercise? What strategies were most effective for you?\n\n"
            
            "3. **Conceptual Change**: Were there any misconceptions or incomplete understandings that "
            "you identified and corrected? How did your concept map help you recognize these?\n\n"
            
            "4. **Remaining Questions**: What questions or areas of uncertainty do you still have about "
            "this topic? How might you address these in future learning?\n\n"
            
            "5. **Application**: How might you apply the knowledge represented in your concept map to "
            "new situations or problems? What connections do you see to other topics or areas?\n\n"
            
            "Reflecting on these questions will help you consolidate your learning and identify areas "
            "for future development. This metacognitive process is a valuable skill that can enhance "
            "your learning across different subjects and contexts."
        )
        
        return reflection_prompts
    
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
            metacognitive_need = zpd_estimate["scaffolding_needs"].get("metacognitive")
            if metacognitive_need:
                # Only reduce scaffolding if current level is higher than the estimated need
                if self._scaffolding_level_value(self.scaffolding_level) > self._scaffolding_level_value(metacognitive_need):
                    self.scaffolding_level = metacognitive_need
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
        
        logger.info(f"Generating metacognitive scaffolding prompts at {intensity} intensity")
        
        # Determine the metacognitive focus based on the round
        current_round = context.get("session_state", {}).get("current_round", 0)
        max_rounds = context.get("session_state", {}).get("max_rounds", 4)
        
        if current_round == 0:
            focus = "planning"
        elif current_round == max_rounds - 1:
            focus = "evaluating"
        else:
            focus = "monitoring"
        
        # Generate prompts using utility function
        prompts = generate_default_prompts("metacognitive", intensity, analysis)
        
        # If no prompts were generated, use templates from reflection prompts
        if not prompts:
            focus_prompts = self.reflection_prompts.get(focus, [])
            if focus_prompts:
                if len(focus_prompts) > 3:
                    prompts = random.sample(focus_prompts, 3)
                else:
                    prompts = focus_prompts
        
        return {
            "prompts": prompts,
            "agent_type": self.agent_type,
            "status": "success",
            "scaffolding_level": intensity,
            "focus": focus
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
        
        logger.info("Generating metacognitive scaffolding follow-up")
        
        # Get follow-up templates from config
        follow_up_templates = SCAFFOLDING_FOLLOWUP_TEMPLATES.get("metacognitive", [])
        
        # Select a follow-up template
        if follow_up_templates:
            follow_up = random.choice(follow_up_templates)
        else:
            # Fallback follow-up
            follow_up = "Thank you for sharing that. How do you think this insight might influence your next revision?"
        
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
        
        logger.info("Concluding metacognitive scaffolding interaction")
        
        # Generate conclusion based on interaction history
        conclusion = "Thank you for reflecting on your learning process. Being aware of your own thinking and learning strategies is a valuable skill. As you continue working on your concept map, keep monitoring your understanding and identifying areas where you can deepen your knowledge."
        
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
