"""
Neutral Agent for Control Group

This agent provides context-aware acknowledgments without any scaffolding.
Used for the CG_NEUTRAL experimental condition.
"""

import random
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class NeutralAgent:
    """
    Neutral agent that provides acknowledgments only and refers back to task instructions.
    Provides no scaffolding, no concepts, no strategies, no solutions.
    Responses are ≤ 2 sentences and context-aware but non-scaffolding.
    """
    
    def __init__(self):
        self.name = "neutral"
        self.agent_type = "neutral"
    
    def generate_response(self, 
                         user_message: Optional[str] = None, 
                         concept_map: Optional[Dict[str, Any]] = None,
                         context: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate neutral, non-scaffolding response.
        
        Args:
            user_message: User's input message
            concept_map: Current concept map data
            context: Additional context information
            
        Returns:
            Context-aware neutral response (≤ 2 sentences)
        """
        # Extract context information
        node_count = 0
        edge_count = 0
        observation = "your concept map"
        
        if concept_map:
            concepts = concept_map.get("concepts", [])
            relationships = concept_map.get("relationships", [])
            node_count = len(concepts)
            edge_count = len(relationships)
            
            # Create observation based on map content
            if node_count > 0:
                # Get first few concept labels for context
                concept_labels = []
                for c in concepts[:2]:  # First 2 concepts
                    label = c.get('text', c.get('label', c.get('id', 'concept')))
                    # Avoid showing UUIDs
                    if '-' not in label or len(label) < 30:
                        concept_labels.append(label)
                
                if concept_labels:
                    if len(concept_labels) == 1:
                        observation = f"concepts like {concept_labels[0]}"
                    else:
                        observation = f"concepts like {concept_labels[0]} and {concept_labels[1]}"
                else:
                    observation = "your concept map"
            
        # Select appropriate template based on context
        if user_message and len(user_message.strip()) > 0:
            # User provided input - acknowledge it
            templates = self._get_acknowledgment_templates(observation, node_count, edge_count)
        elif node_count == 0:
            # Empty map - encourage starting
            templates = self._get_initial_templates()
        elif node_count > 0:
            # Map has content - acknowledge progress
            templates = self._get_progress_templates(observation, node_count, edge_count)
        else:
            # Default templates
            templates = self._get_general_templates()
        
        # Select random template
        response = random.choice(templates)
        
        # Log the neutral response
        logger.info(f"Neutral agent response: {response[:50]}...")
        
        return response
    
    def _get_acknowledgment_templates(self, observation: str, node_count: int, edge_count: int) -> List[str]:
        """Templates for acknowledging user input."""
        return [
            f"You already have added concepts such as {observation}. Continue developing your concept map as you think best.",
            f"I see you're working with {observation}. Keep building your map according to the task requirements.",
            f"You already have added concepts such as {observation}. Please continue with your concept mapping as outlined in the task.",
            f"I notice you're exploring {observation}. Feel free to keep developing your map however you'd like.",
            f"I see your progress with {observation}. Continue working on the task as described.",
            f"I can see you've been thinking about {observation}. Please continue with the concept mapping task.",
            f"I can grasp your ideas about {observation}. Keep working on your concept map as instructed."
        ]
    
    def _get_progress_templates(self, observation: str, node_count: int, edge_count: int) -> List[str]:
        """Templates for acknowledging map progress."""
        return [
            f"I notice your map has {node_count} concepts so far. Please continue working on it as described in the instructions.",
            f"Your concept map currently shows {node_count} concepts and {edge_count} connections. Keep going with your work.",
            f"I see you have {node_count} concepts in your map now. Continue building it according to the task description.",
            f"Seeing your progress with {node_count} concepts, you may keep working on the task as outlined.",
            f"I can see your map has grown to {node_count} concepts and {edge_count} relationships. Please continue as instructed.",
            f"I notice you're working with {observation} in your {node_count}-concept map. Continue developing it as you see fit.",
            f"Your concept map with {node_count} concepts is taking shape. Keep building according to the task requirements."
        ]
    
    def _get_initial_templates(self) -> List[str]:
        """Templates for when map is empty."""
        return [
            "Please start creating your concept map according to the task description. Add concepts and relationships as you see fit.",
            "Begin building your concept map based on the provided materials. Continue working as outlined in the instructions.",
            "Start developing your concept map using the task description and extra materials. Work at your own pace.",
            "Please begin with your concept mapping task as described. Add the concepts you think are most important.",
            "Start creating your concept map according to the provided instructions. Build it as you think appropriate."
        ]
    
    def _get_general_templates(self) -> List[str]:
        """General neutral templates."""
        return [
            "Just continue developing it as you see fit.",
            "I appreciate you sharing your progress. Keep working on the task according to the provided instructions.",
            "Please continue with your concept map development.",
            "I see you're making progress on your concept map. Keep going with the task as described.",
            "Continue building your concept map as outlined in the ressources."
        ]
    
    def _get_question_response_templates(self) -> List[str]:
        """Templates for responding to user questions (non-scaffolding)."""
        return [
            "That's something for you to decide based on the task instructions. Continue working as you think appropriate.",
            "I can't provide specific guidance on that. Please refer to the task description and continue as instructed.",
            "You'll need to make that decision yourself. Keep working on your concept map according to the task requirements.",
            "That's up to you to determine. Please continue with the task as described in the instructions.",
            "Please use your own judgment for that. Continue with your concept mapping as outlined in the materials."
        ]
    
    def handle_pattern_response(self, 
                              pattern_type: str, 
                              user_response: str,
                              concept_map: Optional[Dict[str, Any]] = None) -> str:
        """
        Handle specific patterns with neutral responses.
        
        Args:
            pattern_type: Type of pattern detected
            user_response: User's input
            concept_map: Current concept map data
            
        Returns:
            Appropriate neutral response for the pattern
        """
        # Extract context
        node_count = len(concept_map.get("concepts", [])) if concept_map else 0
        edge_count = len(concept_map.get("relationships", [])) if concept_map else 0
        
        # Handle different patterns with neutral responses
        if pattern_type in ["question", "domain_question", "system_question"]:
            return random.choice(self._get_question_response_templates())
        
        elif pattern_type in ["help_seeking"]:
            return "Please refer to the task description and help button for guidance. Continue working on your concept map as instructed."
        
        elif pattern_type in ["greeting"]:
            return "Hello! Please continue with your concept mapping task as described in the instructions."
        
        elif pattern_type in ["minimal_input"]:
            return f"Thanks for the update. Please continue developing your concept map as outlined in the task."
        
        elif pattern_type in ["concrete_idea", "conversational"]:
            # Acknowledge without scaffolding
            idea_snippet = user_response[:30] + "..." if len(user_response) > 30 else user_response
            return f"I see you mentioned '{idea_snippet}'. Continue developing your concept map as you think best."
        
        elif pattern_type in ["frustration"]:
            return "Please take your time with the concept mapping task. Continue working according to the provided instructions."
        
        elif pattern_type in ["off_topic"]:
            return "Please focus on the concept mapping task as described. Continue building your map according to the instructions."
        
        else:
            # Default neutral response
            if node_count > 0:
                return f"Thanks for the update. Your map has {node_count} concepts so far - please continue as instructed."
            else:
                return "Thanks for the update. Please continue with your concept mapping task as described."
