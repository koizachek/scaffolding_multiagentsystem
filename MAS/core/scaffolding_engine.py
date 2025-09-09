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
        
        # Initialize template tracking
        self.used_template_indices = {}  # Track per scaffolding type
        self.used_followup_indices = {}  # Track per scaffolding type
        self.conversation_turn = 0
        
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
            # Build ID-to-text lookup dictionary for concept maps
            id_to_text = self._build_id_to_text_lookup(concept_map)
            previous_id_to_text = self._build_id_to_text_lookup(previous_map) if previous_map else {}
            expert_id_to_text = self._build_id_to_text_lookup(expert_map) if expert_map else {}
            
            # Enhance concept maps with resolved labels
            enhanced_concept_map = self._enhance_map_with_labels(concept_map, id_to_text)
            enhanced_previous_map = self._enhance_map_with_labels(previous_map, previous_id_to_text) if previous_map else None
            enhanced_expert_map = self._enhance_map_with_labels(expert_map, expert_id_to_text) if expert_map else None
            
            # Analyze concept map with previous and expert maps (using enhanced versions)
            map_analysis = analyze_concept_map(enhanced_concept_map, enhanced_previous_map, enhanced_expert_map)
            
            # Get current round
            current_round = self.session_state.get("current_round", 0)
            
            # Get enabled scaffolding types
            # enabled_types = ["strategic", "metacognitive", "procedural", "conceptual"]
            # weights = {"strategic": 1.0, "metacognitive": 1.0, "procedural": 1.0, "conceptual": 1.0}
            
            # Wrong scaffolding group order: metacognitive, strategic, procedural, conceptual
            fixed_sequence = ["metacognitive", "strategic", "procedural", "conceptual"]
            round_index = current_round % len(fixed_sequence)
            scaffolding_type = fixed_sequence[round_index]
            scaffolding_intensity = "medium"  # Default intensity
            selection_reasoning = f"Wrong scaffolding group experiment - Round {current_round + 1}: {scaffolding_type}"
            
            # dynamic selection 
            # scaffolding_type, scaffolding_intensity, selection_reasoning = select_scaffolding_type(
            #     map_analysis,
            #     enabled_types,
            #     weights,
            #     self.interaction_history
            # )
            
            # Initialize template tracking for this type if needed
            if scaffolding_type not in self.used_template_indices:
                self.used_template_indices[scaffolding_type] = []
            if scaffolding_type not in self.used_followup_indices:
                self.used_followup_indices[scaffolding_type] = []
            
            # Generate scaffolding prompts with enhanced map data and tracking
            prompts, indices_used = generate_default_prompts(
                scaffolding_type,
                scaffolding_intensity,
                map_analysis,
                enhanced_concept_map,
                self.used_template_indices[scaffolding_type],
                self.conversation_turn
            )
            
            # Update used indices
            self.used_template_indices[scaffolding_type].extend(indices_used)
            
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
            
            # Analyze the response to determine type
            from MAS.utils.scaffolding_utils import analyze_user_response_type
            response_analysis = analyze_user_response_type(response)
            
            # CRITICAL: Check for interface help FIRST before any other logic
            if response_analysis.get("is_interface_help", False):
                from MAS.utils.scaffolding_utils import handle_interface_help
                interface_help_response = handle_interface_help(response)
                
                # Store the interface help response as a follow-up
                self.current_interaction["follow_ups"].append(interface_help_response)
                
                return {
                    "status": "success",
                    "needs_follow_up": True,
                    "follow_up": interface_help_response,
                    "scaffolding_type": self.current_scaffolding_type,
                    "response_type": "interface_help"
                }
            
            # Increment conversation turn
            self.conversation_turn += 1
            
            # Determine follow-up strategy based on response type
            if response_analysis["is_question"] or response_analysis["is_confused"]:
                # User needs more scaffolding - provide another prompt from the same type
                follow_up = self._generate_scaffolding_prompt_for_confusion(
                    response,
                    response_analysis
                )
            elif response_analysis["has_concrete_idea"]:
                # User has concrete ideas - use follow-up templates
                follow_up = self._generate_intelligent_follow_up(
                    response,
                    response_analysis
                )
            else:
                # Default follow-up logic
                needs_follow_up = self._needs_follow_up(response)
                if needs_follow_up:
                    follow_up = self._generate_intelligent_follow_up(
                        response,
                        response_analysis
                    )
                else:
                    return {
                        "status": "success",
                        "needs_follow_up": False
                    }
            
            # Store follow-up
            self.current_interaction["follow_ups"].append(follow_up)
            
            # Return follow-up
            return {
                "status": "success",
                "needs_follow_up": True,
                "follow_up": follow_up,
                "scaffolding_type": self.current_scaffolding_type,
                "response_type": response_analysis["response_type"]
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
            
            # Clear current interaction and reset conversation turn
            current_interaction = self.current_interaction
            self.current_interaction = None
            self.conversation_turn = 0
            
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
    
    def _generate_intelligent_follow_up(self, response: str, response_analysis: Dict[str, Any]) -> str:
        """
        Generate an intelligent follow-up based on response analysis with pattern-specific handling.
        
        Args:
            response: Learner response
            response_analysis: Analysis of the response
            
        Returns:
            Follow-up prompt
        """
        from MAS.utils.scaffolding_utils import (
            select_appropriate_followup,
            handle_domain_question,
            handle_system_question,
            handle_disagreement,
            handle_empty_input,
            handle_inappropriate_language,
            handle_off_topic,
            handle_frustration,
            handle_premature_ending,
            generate_concrete_idea_followup,
            handle_greeting,
            handle_minimal_input,
            handle_help_seeking,
            handle_gibberish,
            handle_intention_without_action,
            handle_reassurance_seeking
        )
        
        # Pattern-specific handling based on response type
        response_type = response_analysis.get("response_type", "statement")
        
        # UNIVERSAL INTERFACE HELP PATTERN - applies to ALL agents
        if response_analysis.get("is_interface_help", False):
            from MAS.utils.scaffolding_utils import handle_interface_help
            return handle_interface_help(response)
        
        # NEW UNIVERSAL PATTERNS - apply to ALL agents
        if response_analysis.get("is_greeting", False):
            return handle_greeting(self.current_scaffolding_type)
        
        if response_analysis.get("is_minimal_input", False):
            return handle_minimal_input(self.current_scaffolding_type)
        
        if response_analysis.get("is_gibberish", False):
            return handle_gibberish(self.current_scaffolding_type)
        
        if response_analysis.get("is_help_seeking", False):
            return handle_help_seeking(response, self.current_scaffolding_type)
        
        if response_analysis.get("is_reassurance_seeking", False):
            # Get current concept map for context-aware reassurance
            concept_map = self.current_interaction.get("map_analysis", {})
            return handle_reassurance_seeking(response, concept_map)
        
        if response_analysis.get("has_intention_without_action", False):
            return handle_intention_without_action(response, self.current_scaffolding_type)
        
        # Pattern 3: Empty input
        if response_analysis.get("is_empty", False):
            return handle_empty_input(self.current_scaffolding_type)
        
        # Pattern 4: Inappropriate language (handle first as it needs redirection)
        if response_analysis.get("is_inappropriate", False):
            return handle_inappropriate_language(self.current_scaffolding_type)
        
        # Pattern 1.1: Domain questions
        if response_type == "domain_question":
            return handle_domain_question(
                response, 
                self.current_scaffolding_type,
                response_analysis.get("key_phrases", [])
            )
        
        # Pattern 1.2: System questions
        if response_type == "system_question":
            return handle_system_question(response, self.current_scaffolding_type)
        
        # Pattern 2: Disagreement
        if response_type == "disagreement":
            return handle_disagreement(
                response,
                self.current_scaffolding_type,
                response_analysis.get("disagreement_type", "general")
            )
        
        # Pattern 6: Off-topic
        if response_type == "off_topic":
            return handle_off_topic(self.current_scaffolding_type)
        
        # Pattern 7: Frustration
        if response_type == "frustration":
            return handle_frustration(response, self.current_scaffolding_type)
        
        # Pattern 8: Premature ending
        if response_type == "premature_ending":
            return handle_premature_ending(self.current_scaffolding_type)
        
        # Pattern 5: Concrete ideas (Critical Fix - only affirm actual ideas)
        if response_type == "concrete_idea" and response_analysis.get("has_concrete_idea", False):
            return generate_concrete_idea_followup(
                response,
                self.current_scaffolding_type,
                response_analysis.get("mentions_concepts", [])
            )
        
        # Default: Use template-based follow-ups for other cases
        # Get used indices for this scaffolding type
        used_indices = self.used_followup_indices.get(self.current_scaffolding_type, [])
        
        # Select appropriate follow-up
        follow_up, index_used = select_appropriate_followup(
            response,
            self.current_scaffolding_type,
            used_indices
        )
        
        # Track used index if valid
        if index_used >= 0:
            if self.current_scaffolding_type not in self.used_followup_indices:
                self.used_followup_indices[self.current_scaffolding_type] = []
            self.used_followup_indices[self.current_scaffolding_type].append(index_used)
        
        return follow_up
    
    def _generate_scaffolding_prompt_for_confusion(self, response: str, response_analysis: Dict[str, Any]) -> str:
        """
        Generate another scaffolding prompt when user is confused or asking questions.
        
        Args:
            response: Learner response
            response_analysis: Analysis of the response
            
        Returns:
            Scaffolding prompt
        """
        # Get current map analysis from interaction
        map_analysis = self.current_interaction.get("map_analysis", {})
        
        # Generate another prompt from the same scaffolding type
        prompts, indices_used = generate_default_prompts(
            self.current_scaffolding_type,
            self.current_scaffolding_intensity,
            map_analysis,
            None,  # We might not have enhanced map in current interaction
            self.used_template_indices.get(self.current_scaffolding_type, []),
            self.conversation_turn
        )
        
        # Update used indices
        if self.current_scaffolding_type not in self.used_template_indices:
            self.used_template_indices[self.current_scaffolding_type] = []
        self.used_template_indices[self.current_scaffolding_type].extend(indices_used)
        
        # Return the first prompt (we only generate one at a time)
        return prompts[0] if prompts else "Let me help you think about this differently. What specific aspect would you like to explore?"
    
    def _generate_follow_up(self, response: str, scaffolding_type: str) -> str:
        """
        Legacy follow-up generation (kept for compatibility).
        
        Args:
            response: Learner response
            scaffolding_type: Type of scaffolding
            
        Returns:
            Follow-up prompt
        """
        from MAS.utils.scaffolding_utils import analyze_user_response_type
        response_analysis = analyze_user_response_type(response)
        return self._generate_intelligent_follow_up(response, response_analysis)
    
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
    
    def _build_id_to_text_lookup(self, concept_map: Optional[Dict[str, Any]]) -> Dict[str, str]:
        """
        Build a lookup dictionary from concept IDs to their text labels.
        
        Args:
            concept_map: Concept map containing concepts
            
        Returns:
            Dictionary mapping IDs to text labels
        """
        if not concept_map:
            return {}
        
        id_to_text = {}
        
        # Handle both 'concepts' and 'nodes' keys for compatibility
        concepts = concept_map.get("concepts", concept_map.get("nodes", []))
        
        for concept in concepts:
            if isinstance(concept, dict):
                concept_id = concept.get("id")
                concept_text = concept.get("text", concept.get("label", concept.get("id", "")))
                if concept_id:
                    id_to_text[concept_id] = concept_text
            elif isinstance(concept, str):
                # If concepts are stored as strings, use them as both ID and text
                id_to_text[concept] = concept
        
        return id_to_text
    
    def _enhance_map_with_labels(self, concept_map: Optional[Dict[str, Any]], 
                                 id_to_text: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """
        Enhance a concept map by adding human-readable labels to relationships.
        
        Args:
            concept_map: Original concept map
            id_to_text: Dictionary mapping IDs to text labels
            
        Returns:
            Enhanced concept map with resolved labels
        """
        if not concept_map:
            return None
        
        # Create a copy to avoid modifying the original
        enhanced_map = concept_map.copy()
        
        # Handle both 'relationships' and 'edges' keys for compatibility
        relationships = enhanced_map.get("relationships", enhanced_map.get("edges", []))
        enhanced_relationships = []
        
        for rel in relationships:
            if isinstance(rel, dict):
                enhanced_rel = rel.copy()
                
                # Add resolved text labels
                source_id = rel.get("source")
                target_id = rel.get("target")
                
                enhanced_rel["source_id"] = source_id
                enhanced_rel["target_id"] = target_id
                enhanced_rel["source_text"] = id_to_text.get(source_id, source_id)
                enhanced_rel["target_text"] = id_to_text.get(target_id, target_id)
                
                # Also update the source and target to use text for compatibility
                enhanced_rel["source_label"] = enhanced_rel["source_text"]
                enhanced_rel["target_label"] = enhanced_rel["target_text"]
                
                enhanced_relationships.append(enhanced_rel)
            else:
                enhanced_relationships.append(rel)
        
        # Update the map with enhanced relationships
        if "relationships" in enhanced_map:
            enhanced_map["relationships"] = enhanced_relationships
        if "edges" in enhanced_map:
            enhanced_map["edges"] = enhanced_relationships
        
        # Also enhance the nodes/concepts with explicit text labels
        concepts = enhanced_map.get("concepts", enhanced_map.get("nodes", []))
        enhanced_concepts = []
        
        for concept in concepts:
            if isinstance(concept, dict):
                enhanced_concept = concept.copy()
                concept_id = concept.get("id")
                if concept_id and concept_id in id_to_text:
                    enhanced_concept["label"] = id_to_text[concept_id]
                enhanced_concepts.append(enhanced_concept)
            else:
                enhanced_concepts.append(concept)
        
        if "concepts" in enhanced_map:
            enhanced_map["concepts"] = enhanced_concepts
        if "nodes" in enhanced_map:
            enhanced_map["nodes"] = enhanced_concepts
        
        return enhanced_map
