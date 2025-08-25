"""
AI API Manager

This module provides centralized AI API integration with fallback support
for the multi-agent scaffolding system.
"""

import os
import logging
import time

from typing import Dict, List, Any, Optional
from openai import OpenAI
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

logger = logging.getLogger(__name__)

class AIManager:
    """
    Manages AI API calls with fallback model support and error handling.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the AI manager.

        Args:
            config: Configuration dictionary with API settings
        """
        self.config = config or {}
        client_type = self.config.get("client")
        if not client_type:
            raise ValueError("Missing 'client' key in config")

        # Set shared defaults
        self.max_tokens = self.config.get("max_tokens", 500)
        self.temperature = self.config.get("temperature", 0.7)
        self.max_retries = self.config.get("max_retries", 3)

        # Initialize OpenAI-compatible client
        match client_type:
            case "openai":
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    raise ValueError(f"OpenAI was set as the primary client in the config but OPENAI_API_KEY environment variable not found")

                self.client = OpenAI(api_key=api_key)
                self.client_name = "OpenAI"
                self.primary_model = self.config.get("primary_model",   "gpt-4o")
                self.fallback_model = self.config.get("fallback_model", "gpt-4o-mini")
            case "groq":
                api_key = os.getenv("GROQ_API_KEY")
                if not api_key:
                    raise ValueError("Groq was set as the primary client in the config file but GROQ_API_KEY environment variable not found")

                self.client = OpenAI(
                    api_key=api_key,
                    base_url="https://api.groq.com/openai/v1"
                )
                self.client_name = "Groq"
                self.primary_model = self.config.get("primary_model",   "llama3-70b-8192")
                self.fallback_model = self.config.get("fallback_model", "llama3-8b-8192")
            case "open_router":
                api_key = os.getenv("OPEN_ROUTER_API_KEY")
                if not api_key:
                    raise ValueError("Open Router was set as the primary client in the config file but OPEN_ROUTER_API_KEY environment variable not found")            
                self.client = OpenAI(
                    api_key=api_key,
                    base_url="https://openrouter.ai/api/v1"
                )
                self.client_name = "Open Router"
                self.primary_model = self.config.get("primary_model",   "openai/gpt-oss-20b:free")
                self.fallback_model = self.config.get("fallback_model", "qwen/qwen3-coder:free")
            case _:
                raise ValueError(f"Unsupported client '{client_type}'")

        # Tracking
        self.current_model = self.primary_model
        self.api_calls = 0
        self.fallback_count = 0
        self.total_tokens = 0

        logger.info(f"AI Manager initialized: {self.client_name} with primary model {self.primary_model}")

    def generate_response(self, 
                         prompt: str, 
                         system_message: Optional[str] = None,
                         max_tokens: Optional[int] = None,
                         temperature: Optional[float] = None) -> Dict[str, Any]:
        """
        Generate a response using AI API with fallback support.
        
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
                logger.info(f"{self.client_name} API call successful - Model: {self.current_model}, "
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
                logger.warning(f"{self.client_name} call failed (attempt {attempt + 1}): {e}")
                
                # Try fallback model if primary failed
                if self.current_model == self.primary_model and attempt == 0:
                    logger.info(f"Switching to fallback model: {self.fallback_model}")
                    self.current_model = self.fallback_model
                    self.fallback_count += 1
                
                # If this was the last attempt, raise the error
                if attempt == self.max_retries - 1:
                    logger.error(f"All {self.client_name} API attempts failed: {e}")
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
                                    context: Optional[Dict[str, Any]] = None,
                                    scaffolding_level: str = "medium") -> Dict[str, Any]:
        """
        Generate scaffolding response based on type, level, and context.
        
        Args:
            scaffolding_type: Type of scaffolding (conceptual, strategic, etc.)
            concept_map: Current concept map data
            user_response: Previous user response (if any)
            context: Additional context information
            scaffolding_level: Level of scaffolding (low, medium, high)
            
        Returns:
            Generated scaffolding response with metadata
        """
        # Build system message based on scaffolding type and level
        system_message = self._get_scaffolding_system_message(scaffolding_type, scaffolding_level)
        
        # Build prompt with scaffolding level consideration
        prompt = self._build_scaffolding_prompt(
            scaffolding_type, concept_map, user_response, context, scaffolding_level
        )
        
        # Generate response
        result = self.generate_response(prompt, system_message)
        
        # Add scaffolding-specific metadata
        result["scaffolding_type"] = scaffolding_type
        result["scaffolding_level"] = scaffolding_level
        result["concept_map_nodes"] = len(concept_map.get("concepts", []))
        result["concept_map_edges"] = len(concept_map.get("relationships", []))
        
        return result
    
    def _get_scaffolding_system_message(self, scaffolding_type: str, scaffolding_level: str = "medium") -> str:
        """Get system message for specific scaffolding type and level."""
        
        # Import scaffolding templates
        try:
            from MAS.config.amg_scaffolding_config import AMG_SCAFFOLDING_PROMPT_TEMPLATES
        except ImportError:
            # Fallback if import fails
            try:
                from config.amg_scaffolding_config import AMG_SCAFFOLDING_PROMPT_TEMPLATES
            except ImportError:
                # Use default templates if AMG not available
                from MAS.config.scaffolding_config import SCAFFOLDING_PROMPT_TEMPLATES as AMG_SCAFFOLDING_PROMPT_TEMPLATES
        
        base_messages = {
            "conceptual": f"""You are a Conceptual Scaffolding Agent for the Adaptive Market Gatekeeping (AMG) international market entry task.

SCAFFOLDING LEVEL: {scaffolding_level.upper()}
ROLE: Help learners understand relationships between AMG mechanisms and market entry concepts.
PRINCIPLE: Guide learners to discover conceptual connections, don't provide direct answers.

SCAFFOLDING APPROACH:
- Help learners understand AMG's four mechanisms (dynamic adaptation, rule-changing, network control, resource blocking)
- Clarify relationships between AMG and market entry strategies
- Encourage deeper thinking about how AMG affects start-ups
- Ask questions that promote understanding of AMG's gatekeeping role
- Use {scaffolding_level} intensity scaffolding

INSTRUCTIONS:
- Stay within conceptual scaffolding only
- Use {scaffolding_level} intensity responses
- Guide through questions, don't provide direct answers
- Focus on AMG mechanisms and their relationships to other concepts
- Reference the learner's current concept map state
- Keep responses supportive and educational""",
            
            "strategic": f"""You are a Strategic Scaffolding Agent for the Adaptive Market Gatekeeping (AMG) international market entry task.

SCAFFOLDING LEVEL: {scaffolding_level.upper()}
ROLE: Help learners organize their concept maps to show AMG's impact on market entry.
PRINCIPLE: Guide learners to discover organizational strategies, don't provide direct answers.

SCAFFOLDING APPROACH:
- Help learners position AMG centrally to show its gatekeeping role
- Guide organization to show both AMG challenges and solutions
- Encourage showing temporal dynamics (how AMG adapts over time)
- Help differentiate between AMG's blocking vs. adapting functions
- Use {scaffolding_level} intensity scaffolding

INSTRUCTIONS:
- Stay within strategic scaffolding only
- Use {scaffolding_level} intensity responses
- Guide through questions, don't provide direct answers
- Focus on organizing AMG relationships strategically
- Reference the learner's current concept map state
- Keep responses practical and organized""",
            
            "metacognitive": f"""You are a Metacognitive Scaffolding Agent for the Adaptive Market Gatekeeping (AMG) international market entry task.

SCAFFOLDING LEVEL: {scaffolding_level.upper()}
ROLE: Help learners reflect on their understanding of AMG and market entry.
PRINCIPLE: Guide learners to self-reflect and assess their understanding, don't provide direct answers.

SCAFFOLDING APPROACH:
- Encourage reflection on understanding of AMG mechanisms
- Help learners assess their grasp of how AMG affects market entry
- Promote awareness of assumptions about AMG operations
- Guide reflection on the Veyra example and its implications
- Use {scaffolding_level} intensity scaffolding

INSTRUCTIONS:
- Stay within metacognitive scaffolding only
- Use {scaffolding_level} intensity responses
- Guide through questions, don't provide direct answers
- Focus on self-reflection about AMG understanding
- Reference the learner's current concept map state
- Keep responses reflective and supportive""",
            
            "procedural": f"""You are a Procedural Scaffolding Agent for the Adaptive Market Gatekeeping (AMG) international market entry task.

SCAFFOLDING LEVEL: {scaffolding_level.upper()}
ROLE: Help learners with the process of mapping AMG's impact on market entry.
PRINCIPLE: Guide learners through procedures and techniques, don't provide direct answers.

SCAFFOLDING APPROACH:
- Guide systematic mapping of each AMG mechanism's effects
- Help use action words (blocks, influences, counters) for AMG relationships
- Suggest layered organization (AMG mechanisms, strategies, resources)
- Guide identification of counter-strategies to AMG barriers
- Use {scaffolding_level} intensity scaffolding

INSTRUCTIONS:
- Stay within procedural scaffolding only
- Use {scaffolding_level} intensity responses
- Guide through questions, don't provide direct answers
- Focus on procedures for mapping AMG relationships
- Reference the learner's current concept map state
- Keep responses clear and instructional"""
        }
        
        return base_messages.get(scaffolding_type, base_messages["conceptual"])
    
    def _build_scaffolding_prompt(self, 
                                scaffolding_type: str,
                                concept_map: Dict[str, Any],
                                user_response: Optional[str] = None,
                                context: Optional[Dict[str, Any]] = None,
                                scaffolding_level: str = "medium") -> str:
        """Build prompt for scaffolding interaction."""
        
        # Extract concept map information
        concepts = concept_map.get("concepts", [])
        relationships = concept_map.get("relationships", [])
        
        # Build concept list with text labels
        concept_list = []
        for c in concepts:
            # Use 'text' or 'label' field, fallback to 'id' if neither exists
            label = c.get('text', c.get('label', c.get('id', 'Unknown')))
            concept_list.append(f"- {label}")
        
        # Build relationship list with resolved labels
        relationship_list = []
        for r in relationships:
            # Use enhanced labels if available (from ScaffoldingEngine enhancement)
            source_label = r.get('source_text', r.get('source_label', r.get('source', 'Unknown')))
            target_label = r.get('target_text', r.get('target_label', r.get('target', 'Unknown')))
            relation_text = r.get('text', r.get('relation', 'relates to'))
            
            # Final UUID check - if still showing UUIDs, use generic labels
            # This should rarely happen if UUID resolution is working correctly
            if '-' in source_label and len(source_label) > 30:  # Likely a UUID
                # Try to find the concept text from the concepts list
                source_concept = next((c for c in concepts if c.get('id') == r.get('source')), None)
                if source_concept:
                    source_label = source_concept.get('text', source_concept.get('label', 'Unknown Concept'))
                else:
                    source_label = 'Unknown Concept'
                    
            if '-' in target_label and len(target_label) > 30:  # Likely a UUID
                # Try to find the concept text from the concepts list
                target_concept = next((c for c in concepts if c.get('id') == r.get('target')), None)
                if target_concept:
                    target_label = target_concept.get('text', target_concept.get('label', 'Unknown Concept'))
                else:
                    target_label = 'Unknown Concept'
            
            relationship_list.append(f"- {source_label} → {relation_text} → {target_label}")
        
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
        logger.info(f"{self.client_name} usage statistics reset")
