"""
Scaffolding Engine

This module provides the scaffolding engine for the multi-agent scaffolding system.
It orchestrates the scaffolding interactions.
"""

import logging
import random
from typing import Dict, List, Any, Optional

from MAS.utils.scaffolding_utils import (
    analyze_concept_map,
    select_scaffolding_type,
    generate_default_prompts 
)
from MAS.config.scaffolding_config import (
    SCAFFOLDING_PROMPT_TEMPLATES,
    SCAFFOLDING_FOLLOWUP_TEMPLATES,
    SCAFFOLDING_CONCLUSION_TEMPLATES,
    DEFAULT_SCAFFOLDING_INTENSITY
)

logger = logging.getLogger(__name__)

class ScaffoldingEngine:
    """
    Scaffolding engine for the multi-agent scaffolding system.
    
    This class orchestrates the scaffolding interactions, including selecting
    the appropriate scaffolding type, generating prompts, and adapting the
    scaffolding intensity based on learner responses.
    """
    
    def __init__(self, 
                config: Dict[str, Any],
                lead_agent: Any):
        """
        Initialize the scaffolding engine.
        
        Args:
            config: System configuration
            lead_agent: Lead agent
        """
        self.config = config
        self.lead_agent = lead_agent
        
        # Initialize scaffolding state
        self.current_scaffolding_type = None
        self.current_scaffolding_intensity = None
        self.current_interaction = None
        
        # Initialize interaction history
        self.interaction_history = []
        
        # Initialize session state
        self.session_state = {}
        
        logger.info("Initialized scaffolding engine")
    
    def conduct_scaffolding_interaction(self, 
                                       concept_map: Dict[str, Any],
                                       previous_map: Optional[Dict[str, Any]] = None,
                                       expert_map: Optional[Dict[str, Any]] = None,
                                       learner_profile: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Conduct a scaffolding interaction.
        
        Args:
            concept_map: Current concept map
            previous_map: Previous concept map (optional)
            expert_map: Expert concept map (optional)
            learner_profile: Learner profile (optional)
            
        Returns:
            Interaction results
        """
        logger.info("Conducting scaffolding interaction")
        
        try:
            # Analyze concept map with previous and expert maps
            map_analysis = analyze_concept_map(concept_map, previous_map, expert_map)
            
            # Get current round
            current_round = self.session_state.get("current_round", 0)
            
            # Get enabled scaffolding types
            enabled_types = ["strategic", "metacognitive", "procedural", "conceptual"]
            weights = {"strategic": 1.0, "metacognitive": 1.0, "procedural": 1.0, "conceptual": 1.0}
            
            # Select scaffolding type
            scaffolding_type, scaffolding_intensity, selection_reasoning = select_scaffolding_type(
                map_analysis,
                enabled_types,
                weights,
                self.interaction_history
            )
            
            # Generate scaffolding prompts
            prompts = generate_default_prompts(
                scaffolding_type,
                scaffolding_intensity,
                map_analysis
            )
            
            # Store current interaction
            self.current_scaffolding_type = scaffolding_type
            self.current_scaffolding_intensity = scaffolding_intensity
            self.current_interaction = {
                "scaffolding_type": scaffolding_type,
                "scaffolding_intensity": scaffolding_intensity,
                "map_analysis": map_analysis,
                "prompts": prompts,
                "responses": [],
                "follow_ups": [],
                "follow_up_responses": [],
                "conclusion": None,
                "timestamp": None  # In a real implementation, this would be a timestamp
            }
            
            # Format prompts for presentation
            formatted_prompts = prompts
            
            # Return interaction results
            return {
                "status": "success",
                "scaffolding_type": scaffolding_type,
                "scaffolding_intensity": scaffolding_intensity,
                "selection_reasoning": selection_reasoning,
                "interaction_results": {
                    "prompts": prompts,
                    "formatted_prompts": formatted_prompts
                }
            }
        
        except Exception as e:
            logger.error(f"Error conducting scaffolding interaction: {e}")
            return {
                "status": "error",
                "message": f"Error conducting scaffolding interaction: {str(e)}"
            }
    
    def process_learner_response(self, response: str) -> Dict[str, Any]:
        """
        Process a learner response.
        
        Args:
            response: Learner response
            
        Returns:
            Processing results
        """
        logger.info("Processing learner response")
        
        if not self.current_interaction:
            logger.warning("No active interaction")
            return {
                "status": "error",
                "message": "No active interaction"
            }
        
        try:
            # Store response
            self.current_interaction["responses"].append(response)
            
            # Determine if a follow-up is needed
            needs_follow_up = self._needs_follow_up(response)
            
            if needs_follow_up:
                # Generate follow-up
                follow_up = self._generate_follow_up(
                    response,
                    self.current_scaffolding_type
                )
                
                # Store follow-up
                self.current_interaction["follow_ups"].append(follow_up)
                
                # Return follow-up
                return {
                    "status": "success",
                    "needs_follow_up": True,
                    "follow_up": follow_up,
                    "scaffolding_type": self.current_scaffolding_type
                }
            
            # If no follow-up is needed, return success
            return {
                "status": "success",
                "needs_follow_up": False
            }
        
        except Exception as e:
            logger.error(f"Error processing learner response: {e}")
            return {
                "status": "error",
                "message": f"Error processing learner response: {str(e)}"
            }
    
    def conclude_interaction(self) -> Dict[str, Any]:
        """
        Conclude the current scaffolding interaction.
        
        Returns:
            Conclusion results
        """
        logger.info("Concluding scaffolding interaction")
        
        if not self.current_interaction:
            logger.warning("No active interaction")
            return {
                "status": "error",
                "message": "No active interaction"
            }
        
        try:
            # Generate conclusion
            conclusion = self._generate_conclusion(
                self.current_scaffolding_type,
                self.current_interaction
            )
            
            # Store conclusion
            self.current_interaction["conclusion"] = conclusion
            
            # Add interaction to history
            self.interaction_history.append(self.current_interaction)
            
            # Clear current interaction
            current_interaction = self.current_interaction
            self.current_interaction = None
            
            # Adapt scaffolding intensity for next interaction
            self._adapt_scaffolding_intensity(
                current_interaction["responses"],
                self.current_scaffolding_type,
                self.current_scaffolding_intensity
            )
            
            # Format conclusion for presentation
            formatted_conclusion = conclusion
            
            # Return conclusion results
            return {
                "status": "success",
                "conclusion": conclusion,
                "formatted_conclusion": formatted_conclusion,
                "scaffolding_type": current_interaction["scaffolding_type"]
            }
        
        except Exception as e:
            logger.error(f"Error concluding scaffolding interaction: {e}")
            return {
                "status": "error",
                "message": f"Error concluding scaffolding interaction: {str(e)}"
            }
    
    def evaluate_scaffolding_effectiveness(self) -> Dict[str, float]:
        """
        Evaluate the effectiveness of different scaffolding types.
        
        Returns:
            Effectiveness scores for each scaffolding type
        """
        logger.info("Evaluating scaffolding effectiveness")
        
        # Simple effectiveness evaluation based on interaction history
        effectiveness = {
            "strategic": 0.5,
            "metacognitive": 0.5,
            "procedural": 0.5,
            "conceptual": 0.5
        }
        
        # Adjust based on interaction history
        for interaction in self.interaction_history:
            scaffolding_type = interaction.get("scaffolding_type")
            responses = interaction.get("responses", [])
            
            if scaffolding_type and responses:
                # Simple heuristic: longer responses indicate better engagement
                avg_response_length = sum(len(r) for r in responses) / len(responses)
                if avg_response_length > 100:
                    effectiveness[scaffolding_type] = min(1.0, effectiveness[scaffolding_type] + 0.1)
                elif avg_response_length < 50:
                    effectiveness[scaffolding_type] = max(0.0, effectiveness[scaffolding_type] - 0.1)
        
        return effectiveness
    
    def get_scaffolding_history(self) -> List[Dict[str, Any]]:
        """
        Get the scaffolding interaction history.
        
        Returns:
            The scaffolding interaction history
        """
        return self.interaction_history
    
    def get_interaction_history(self) -> List[Dict[str, Any]]:
        """
        Get the scaffolding interaction history.
        
        Returns:
            The scaffolding interaction history
        """
        return self.interaction_history
    
    def update_session_state(self, state_updates: Dict[str, Any]) -> None:
        """
        Update the session state.
        
        Args:
            state_updates: State updates to apply
        """
        self.session_state.update(state_updates)
        logger.debug(f"Updated session state: {state_updates}")
    
    def _get_scaffolding_intensity(self, scaffolding_type: str) -> str:
        """
        Get the scaffolding intensity for a scaffolding type.
        
        Args:
            scaffolding_type: Type of scaffolding
            
        Returns:
            Scaffolding intensity
        """
        # Check if ZPD estimate includes scaffolding needs
        zpd_estimate = self.session_state.get("zpd_estimate", {})
        
        if zpd_estimate and "scaffolding_needs" in zpd_estimate:
            scaffolding_needs = zpd_estimate["scaffolding_needs"]
            
            if scaffolding_type in scaffolding_needs:
                return scaffolding_needs[scaffolding_type]
        
        # Otherwise, use default intensity
        return DEFAULT_SCAFFOLDING_INTENSITY.get(scaffolding_type, "medium")
    
    def _needs_follow_up(self, response: str) -> bool:
        """
        Determine if a follow-up is needed based on the learner response.
        
        Args:
            response: Learner response
            
        Returns:
            Whether a follow-up is needed
        """
        # Calculate response length
        response_length = len(response)
        
        # Check for questions
        question_count = response.count("?")
        
        # Check for indicators of confusion
        confusion_indicators = [
            "confused", "don't understand", "unclear", "not sure", "difficult", "hard to"
        ]
        
        confusion_count = 0
        for indicator in confusion_indicators:
            if indicator.lower() in response.lower():
                confusion_count += 1
        
        # Determine if follow-up is needed
        if question_count > 0 or confusion_count > 0:
            return True
        
        if response_length > 200:
            # Long responses often indicate engagement and may benefit from follow-up
            return random.random() < 0.7  # 70% chance of follow-up
        
        if response_length > 100:
            # Medium-length responses may benefit from follow-up
            return random.random() < 0.5  # 50% chance of follow-up
        
        # Short responses may indicate low engagement
        return random.random() < 0.3  # 30% chance of follow-up
    
    def _generate_follow_up(self, response: str, scaffolding_type: str) -> str:
        """
        Generate a follow-up prompt based on the learner response.
        
        Args:
            response: Learner response
            scaffolding_type: Type of scaffolding
            
        Returns:
            Follow-up prompt
        """
        # Get follow-up templates for this scaffolding type
        templates = SCAFFOLDING_FOLLOWUP_TEMPLATES.get(scaffolding_type, [])
        
        if not templates:
            # Fallback templates
            templates = [
                "That's interesting. Can you tell me more about that?",
                "Could you elaborate on that point?",
                "How does that relate to your concept map?",
                "What made you think of that?"
            ]
        
        # Select a random template
        template = random.choice(templates)
        
        # Return the follow-up prompt
        return template
    
    def _generate_conclusion(self, 
                            scaffolding_type: str,
                            interaction: Dict[str, Any]) -> str:
        """
        Generate a conclusion for the scaffolding interaction.
        
        Args:
            scaffolding_type: Type of scaffolding
            interaction: Interaction data
            
        Returns:
            Conclusion text
        """
        # Get conclusion templates for this scaffolding type
        templates = SCAFFOLDING_CONCLUSION_TEMPLATES.get(scaffolding_type, [])
        
        if not templates:
            # Fallback templates
            templates = [
                "Thank you for sharing your thoughts. Consider these ideas as you continue developing your concept map.",
                "Your insights are valuable. Keep these points in mind as you revise your map.",
                "This reflection will help you improve your concept map. Consider these ideas in your next revision."
            ]
        
        # Select a random template
        template = random.choice(templates)
        
        # Format template with interaction data
        try:
            # Prepare formatting data
            format_data = {}
            
            # Add specific data based on scaffolding type
            if scaffolding_type == "strategic":
                format_data["specific_approach"] = "hierarchical relationships" if random.random() < 0.5 else "thematic grouping"
            
            elif scaffolding_type == "conceptual":
                # Get concepts from map analysis
                map_analysis = interaction.get("map_analysis", {})
                central_concepts = map_analysis.get("central_concepts", [])
                
                if central_concepts and len(central_concepts) >= 2:
                    format_data["concept_1"] = central_concepts[0].get("label", "key concepts")
                    format_data["concept_2"] = central_concepts[1].get("label", "related concepts")
                    format_data["key_concept"] = central_concepts[0].get("label", "the central concept")
                else:
                    format_data["concept_1"] = "key concepts"
                    format_data["concept_2"] = "related concepts"
                    format_data["key_concept"] = "the central concept"
            
            # Format the template
            conclusion = template.format(**format_data)
            
            return conclusion
        except KeyError:
            # If formatting fails, return the template as is
            return template
    
    def _adapt_scaffolding_intensity(self, 
                                    responses: List[str],
                                    scaffolding_type: str,
                                    current_intensity: str) -> None:
        """
        Adapt scaffolding intensity based on learner responses.
        
        Args:
            responses: List of learner responses
            scaffolding_type: Type of scaffolding
            current_intensity: Current scaffolding intensity
        """
        # Simple intensity adaptation based on response analysis
        if not responses:
            return
        
        # Analyze responses for adaptation cues
        total_length = sum(len(r) for r in responses)
        avg_length = total_length / len(responses)
        
        # Adapt intensity based on response patterns
        adapted_intensity = current_intensity
        
        if avg_length > 150:
            # Long responses suggest good engagement, can reduce intensity
            if current_intensity == "high":
                adapted_intensity = "medium"
            elif current_intensity == "medium":
                adapted_intensity = "low"
        elif avg_length < 50:
            # Short responses suggest need for more support
            if current_intensity == "low":
                adapted_intensity = "medium"
            elif current_intensity == "medium":
                adapted_intensity = "high"
        
        # Update ZPD estimate if it exists
        zpd_estimate = self.session_state.get("zpd_estimate", {})
        if zpd_estimate and "scaffolding_needs" not in zpd_estimate:
            zpd_estimate["scaffolding_needs"] = {}
        
        if zpd_estimate:
            zpd_estimate["scaffolding_needs"][scaffolding_type] = adapted_intensity
            self.session_state["zpd_estimate"] = zpd_estimate
            logger.info(f"Adapted {scaffolding_type} scaffolding intensity to {adapted_intensity}")
