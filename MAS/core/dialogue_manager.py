"""
Dialogue Manager

This module provides the dialogue manager for the multi-agent scaffolding system.
It handles the interactive dialogue with the learner.
"""

import logging
import random
from typing import Dict, List, Any, Optional, Callable

logger = logging.getLogger(__name__)

class DialogueManager:
    """
    Dialogue manager for the multi-agent scaffolding system.
    
    This class handles the interactive dialogue with the learner, including
    presenting scaffolding prompts, collecting responses, and analyzing responses.
    """
    
    def __init__(self, 
                config: Dict[str, Any],
                input_handler: Optional[Callable] = None,
                output_handler: Optional[Callable] = None):
        """
        Initialize the dialogue manager.
        
        Args:
            config: System configuration
            input_handler: Function for handling user input (optional)
            output_handler: Function for handling system output (optional)
        """
        self.config = config
        self.input_handler = input_handler or self._default_input_handler
        self.output_handler = output_handler or self._default_output_handler
        
        # Initialize dialogue history
        self.dialogue_history = []
        
        logger.info("Initialized dialogue manager")
    
    def present_scaffolding_prompts(self, 
                                   scaffolding_type: str,
                                   prompts: List[str],
                                   require_response: bool = True) -> List[str]:
        """
        Present scaffolding prompts to the learner and collect responses.
        
        Args:
            scaffolding_type: Type of scaffolding
            prompts: List of scaffolding prompts
            require_response: Whether to require a response from the learner
            
        Returns:
            List of learner responses
        """
        logger.info(f"Presenting {scaffolding_type} scaffolding prompts")
        
        responses = []
        
        # Present each prompt and collect response
        for i, prompt in enumerate(prompts):
            # Format prompt with scaffolding type
            formatted_prompt = self._format_prompt(scaffolding_type, prompt)
            
            # Present prompt
            self.output_handler(formatted_prompt)
            
            # Record prompt in dialogue history
            self.dialogue_history.append({
                "type": "prompt",
                "scaffolding_type": scaffolding_type,
                "prompt": prompt,
                "formatted_prompt": formatted_prompt
            })
            
            # Collect response if required
            if require_response:
                response_prompt = "Your response: "
                response = self.input_handler(response_prompt)
                
                # Record response in dialogue history
                self.dialogue_history.append({
                    "type": "response",
                    "scaffolding_type": scaffolding_type,
                    "response": response
                })
                
                responses.append(response)
            
            # Add a separator between prompts
            if i < len(prompts) - 1:
                self.output_handler("\n")
        
        return responses
    
    def present_follow_up(self, 
                         scaffolding_type: str,
                         follow_up: str,
                         require_response: bool = True) -> Optional[str]:
        """
        Present a follow-up prompt to the learner and collect response.
        
        Args:
            scaffolding_type: Type of scaffolding
            follow_up: Follow-up prompt
            require_response: Whether to require a response from the learner
            
        Returns:
            Learner response, or None if no response is required
        """
        logger.info(f"Presenting {scaffolding_type} follow-up prompt")
        
        # Format follow-up prompt
        formatted_follow_up = self._format_prompt(scaffolding_type, follow_up)
        
        # Present follow-up prompt
        self.output_handler(formatted_follow_up)
        
        # Record follow-up prompt in dialogue history
        self.dialogue_history.append({
            "type": "follow_up",
            "scaffolding_type": scaffolding_type,
            "prompt": follow_up,
            "formatted_prompt": formatted_follow_up
        })
        
        # Collect response if required
        if require_response:
            response_prompt = "Your response: "
            response = self.input_handler(response_prompt)
            
            # Record response in dialogue history
            self.dialogue_history.append({
                "type": "response",
                "scaffolding_type": scaffolding_type,
                "response": response
            })
            
            return response
        
        return None
    
    def present_conclusion(self, 
                          scaffolding_type: str,
                          conclusion: str) -> None:
        """
        Present a conclusion to the learner.
        
        Args:
            scaffolding_type: Type of scaffolding
            conclusion: Conclusion text
        """
        logger.info(f"Presenting {scaffolding_type} conclusion")
        
        # Format conclusion
        formatted_conclusion = self._format_conclusion(scaffolding_type, conclusion)
        
        # Present conclusion
        self.output_handler(formatted_conclusion)
        
        # Record conclusion in dialogue history
        self.dialogue_history.append({
            "type": "conclusion",
            "scaffolding_type": scaffolding_type,
            "conclusion": conclusion,
            "formatted_conclusion": formatted_conclusion
        })
    
    def analyze_response(self, response: str) -> Dict[str, Any]:
        """
        Analyze a learner response.
        
        Args:
            response: Learner response
            
        Returns:
            Analysis results
        """
        logger.info("Analyzing learner response")
        
        # Calculate response length
        response_length = len(response)
        
        # Check for indicators of understanding
        understanding_indicators = [
            "understand", "clear", "makes sense", "I see", "I get it", "got it"
        ]
        
        understanding_count = 0
        for indicator in understanding_indicators:
            if indicator.lower() in response.lower():
                understanding_count += 1
        
        # Check for indicators of confusion
        confusion_indicators = [
            "confused", "don't understand", "unclear", "not sure", "difficult", "hard to"
        ]
        
        confusion_count = 0
        for indicator in confusion_indicators:
            if indicator.lower() in response.lower():
                confusion_count += 1
        
        # Check for questions
        question_count = response.count("?")
        
        # Determine response sentiment
        if understanding_count > confusion_count:
            sentiment = "positive"
        elif confusion_count > understanding_count:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        
        # Determine response engagement level
        if response_length > 200 or question_count > 2:
            engagement = "high"
        elif response_length > 100 or question_count > 0:
            engagement = "medium"
        else:
            engagement = "low"
        
        # Return analysis results
        return {
            "length": response_length,
            "understanding_indicators": understanding_count,
            "confusion_indicators": confusion_count,
            "question_count": question_count,
            "sentiment": sentiment,
            "engagement": engagement
        }
    
    def get_dialogue_history(self) -> List[Dict[str, Any]]:
        """
        Get the dialogue history.
        
        Returns:
            The dialogue history
        """
        return self.dialogue_history
    
    def _format_prompt(self, scaffolding_type: str, prompt: str) -> str:
        """
        Format a scaffolding prompt with the appropriate prefix.
        
        Args:
            scaffolding_type: Type of scaffolding
            prompt: Scaffolding prompt
            
        Returns:
            Formatted prompt
        """
        # Get emoji for scaffolding type
        emoji = self._get_scaffolding_emoji(scaffolding_type)
        
        # Format prompt
        return f"{emoji} {prompt}"
    
    def _format_conclusion(self, scaffolding_type: str, conclusion: str) -> str:
        """
        Format a conclusion with the appropriate prefix.
        
        Args:
            scaffolding_type: Type of scaffolding
            conclusion: Conclusion text
            
        Returns:
            Formatted conclusion
        """
        # Get emoji for scaffolding type
        emoji = self._get_scaffolding_emoji(scaffolding_type)
        
        # Format conclusion
        return f"{emoji} {conclusion}"
    
    def _get_scaffolding_emoji(self, scaffolding_type: str) -> str:
        """
        Get the emoji for a scaffolding type.
        
        Args:
            scaffolding_type: Type of scaffolding
            
        Returns:
            Emoji for the scaffolding type
        """
        emojis = {
            "strategic": "🧭",  # Compass
            "metacognitive": "🧠",  # Brain
            "procedural": "🛠️",  # Tools
            "conceptual": "💡"   # Light bulb
        }
        
        return emojis.get(scaffolding_type, "🤖")
    
    def _default_input_handler(self, prompt: str) -> str:
        """
        Default input handler.
        
        Args:
            prompt: Input prompt
            
        Returns:
            User input
        """
        return input(prompt)
    
    def _default_output_handler(self, text: str) -> None:
        """
        Default output handler.
        
        Args:
            text: Output text
        """
        print(text)
