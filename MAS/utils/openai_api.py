"""
OpenAI API Manager

This module provides centralized OpenAI API integration with fallback support
for the multi-agent scaffolding system.
"""

import os
import logging
import time
from typing import Dict, List, Any, Optional
import openai
from openai import OpenAI

logger = logging.getLogger(__name__)

class OpenAIManager:
    """
    Manages OpenAI API calls with fallback model support and error handling.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the OpenAI manager.
        
        Args:
            config: Configuration dictionary with API settings
        """
        self.config = config or {}
        
        # Set up API key
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        self.client = OpenAI(api_key=api_key)
        
        # Model configuration
        self.primary_model = self.config.get("primary_model", "gpt-4o")
        self.fallback_model = self.config.get("fallback_model", "gpt-4o-mini")
        self.current_model = self.primary_model
        
        # API parameters
        self.max_tokens = self.config.get("max_tokens", 500)
        self.temperature = self.config.get("temperature", 0.7)
        self.max_retries = self.config.get("max_retries", 3)
        
        # Usage tracking
        self.api_calls = 0
        self.fallback_count = 0
        self.total_tokens = 0
        
        logger.info(f"OpenAI Manager initialized with primary model: {self.primary_model}")
    
    def generate_response(self, 
                         prompt: str, 
                         system_message: Optional[str] = None,
                         max_tokens: Optional[int] = None,
                         temperature: Optional[float] = None) -> Dict[str, Any]:
        """
        Generate a response using OpenAI API with fallback support.
        
        Args:
            prompt: User prompt
            system_message: Optional system message
            max_tokens: Override default max tokens
            temperature: Override default temperature
            
        Returns:
            Dictionary containing response and metadata
        """
        start_time = time.time()
        
        # Prepare messages
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})
        
        # Use provided parameters or defaults
        tokens = max_tokens or self.max_tokens
        temp = temperature or self.temperature
        
        # Try primary model first, then fallback
        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.current_model,
                    messages=messages,
                    max_tokens=tokens,
                    temperature=temp
                )
                
                # Extract response data
                response_text = response.choices[0].message.content
                usage = response.usage
                
                # Update tracking
                self.api_calls += 1
                self.total_tokens += usage.total_tokens
                
                response_time = time.time() - start_time
                
                # Log successful call
                logger.info(f"OpenAI API call successful - Model: {self.current_model}, "
                           f"Tokens: {usage.total_tokens}, Time: {response_time:.2f}s")
                
                return {
                    "response": response_text,
                    "model_used": self.current_model,
                    "tokens_used": usage.total_tokens,
                    "response_time": response_time,
                    "fallback_occurred": self.current_model != self.primary_model,
                    "attempt": attempt + 1,
                    "success": True
                }
                
            except Exception as e:
                logger.warning(f"OpenAI API call failed (attempt {attempt + 1}): {e}")
                
                # Try fallback model if primary failed
                if self.current_model == self.primary_model and attempt == 0:
                    logger.info(f"Switching to fallback model: {self.fallback_model}")
                    self.current_model = self.fallback_model
                    self.fallback_count += 1
                
                # If this was the last attempt, raise the error
                if attempt == self.max_retries - 1:
                    logger.error(f"All OpenAI API attempts failed: {e}")
                    return {
                        "response": "I apologize, but I'm experiencing technical difficulties. Please try again.",
                        "model_used": None,
                        "tokens_used": 0,
                        "response_time": time.time() - start_time,
                        "fallback_occurred": True,
                        "attempt": attempt + 1,
                        "success": False,
                        "error": str(e)
                    }
                
                # Wait before retry
                time.sleep(1)
        
        # Reset to primary model for next call
        self.current_model = self.primary_model
    
    def generate_scaffolding_response(self, 
                                    scaffolding_type: str,
                                    concept_map: Dict[str, Any],
                                    user_response: Optional[str] = None,
                                    context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate scaffolding response based on type and context.
        
        Args:
            scaffolding_type: Type of scaffolding (conceptual, strategic, etc.)
            concept_map: Current concept map data
            user_response: Previous user response (if any)
            context: Additional context information
            
        Returns:
            Generated scaffolding response with metadata
        """
        # Build system message based on scaffolding type
        system_message = self._get_scaffolding_system_message(scaffolding_type)
        
        # Build prompt
        prompt = self._build_scaffolding_prompt(
            scaffolding_type, concept_map, user_response, context
        )
        
        # Generate response
        result = self.generate_response(prompt, system_message)
        
        # Add scaffolding-specific metadata
        result["scaffolding_type"] = scaffolding_type
        result["concept_map_nodes"] = len(concept_map.get("concepts", []))
        result["concept_map_edges"] = len(concept_map.get("relationships", []))
        
        return result
    
    def _get_scaffolding_system_message(self, scaffolding_type: str) -> str:
        """Get system message for specific scaffolding type."""
        
        system_messages = {
            "conceptual": """You are a conceptual scaffolding agent helping learners understand relationships between concepts in their concept maps. Your role is to:
- Help learners identify missing conceptual connections
- Clarify relationships between concepts
- Encourage deeper thinking about concept meanings
- Ask questions that promote conceptual understanding
Keep responses supportive, educational, and focused on concept relationships.""",
            
            "strategic": """You are a strategic scaffolding agent helping learners organize and structure their concept maps effectively. Your role is to:
- Help learners plan their concept map organization
- Suggest effective mapping strategies
- Guide learners in prioritizing important concepts
- Encourage systematic thinking about map structure
Keep responses practical, organized, and focused on strategic planning.""",
            
            "metacognitive": """You are a metacognitive scaffolding agent helping learners reflect on their learning process and understanding. Your role is to:
- Encourage self-reflection on learning progress
- Help learners assess their own understanding
- Promote awareness of thinking processes
- Guide learners in monitoring their comprehension
Keep responses reflective, supportive, and focused on self-awareness.""",
            
            "procedural": """You are a procedural scaffolding agent helping learners with the process and methods of concept mapping. Your role is to:
- Guide learners through concept mapping procedures
- Explain effective mapping techniques
- Help with technical aspects of map creation
- Provide step-by-step guidance when needed
Keep responses clear, instructional, and focused on procedures."""
        }
        
        return system_messages.get(scaffolding_type, system_messages["conceptual"])
    
    def _build_scaffolding_prompt(self, 
                                scaffolding_type: str,
                                concept_map: Dict[str, Any],
                                user_response: Optional[str] = None,
                                context: Optional[Dict[str, Any]] = None) -> str:
        """Build prompt for scaffolding interaction."""
        
        # Extract concept map information
        concepts = concept_map.get("concepts", [])
        relationships = concept_map.get("relationships", [])
        
        concept_list = [f"- {c.get('text', 'Unknown')}" for c in concepts]
        relationship_list = [
            f"- {r.get('source', 'A')} → {r.get('text', 'relates to')} → {r.get('target', 'B')}"
            for r in relationships
        ]
        
        prompt_parts = [
            f"I'm analyzing a concept map with the following elements:",
            f"\nConcepts ({len(concepts)}):",
            "\n".join(concept_list),
            f"\nRelationships ({len(relationships)}):",
            "\n".join(relationship_list) if relationship_list else "- No relationships defined yet"
        ]
        
        # Add context if available
        if context:
            round_num = context.get("round_number", 0)
            prompt_parts.append(f"\nThis is round {round_num + 1} of the concept mapping session.")
        
        # Add user response if this is a follow-up
        if user_response:
            prompt_parts.extend([
                f"\nThe learner responded: \"{user_response}\"",
                f"\nPlease provide appropriate {scaffolding_type} scaffolding based on this response."
            ])
        else:
            prompt_parts.append(f"\nPlease provide {scaffolding_type} scaffolding to help improve this concept map.")
        
        prompt_parts.extend([
            f"\nProvide a helpful, encouraging response that guides the learner's thinking.",
            f"Keep your response concise (2-3 sentences) and ask one specific question to promote engagement."
        ])
        
        return "\n".join(prompt_parts)
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get API usage statistics."""
        return {
            "total_api_calls": self.api_calls,
            "fallback_count": self.fallback_count,
            "total_tokens_used": self.total_tokens,
            "primary_model": self.primary_model,
            "fallback_model": self.fallback_model,
            "fallback_rate": self.fallback_count / max(1, self.api_calls)
        }
    
    def reset_stats(self):
        """Reset usage statistics."""
        self.api_calls = 0
        self.fallback_count = 0
        self.total_tokens = 0
        logger.info("OpenAI usage statistics reset")
