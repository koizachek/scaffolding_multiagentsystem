"""
AI API Manager GERMAN VERSION

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
                        "response": "Entschuldige, es gibt technische Schwierigkeiten. Bitte versuche es erneut.",
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
        # Import scaffolding utilities to get templates
        try:
            from MAS.utils.scaffolding_utils import generate_default_prompts
            from MAS.config.scaffolding_config import (
                SCAFFOLDING_PROMPT_TEMPLATES,
                SCAFFOLDING_FOLLOWUP_TEMPLATES,
                SCAFFOLDING_CONCLUSION_TEMPLATES
            )
        except ImportError:
            from utils.scaffolding_utils import generate_default_prompts
            from config.scaffolding_config import (
                SCAFFOLDING_PROMPT_TEMPLATES,
                SCAFFOLDING_FOLLOWUP_TEMPLATES,
                SCAFFOLDING_CONCLUSION_TEMPLATES
            )
        
        # Get conversation turn from context
        conversation_turn = context.get("conversation_turn", 0) if context else 0
        conversation_history = context.get("conversation_history", []) if context else []
        
        # Determine if this is a follow-up or initial prompt
        is_followup = conversation_turn > 0 and user_response
        
        # Get appropriate template based on context
        if is_followup:
            # Use follow-up templates for continued conversation
            templates = SCAFFOLDING_FOLLOWUP_TEMPLATES.get(scaffolding_type, [])
            if templates:
                # Select a template that hasn't been used recently
                used_templates = [msg.get("metadata", {}).get("template_used") 
                                for msg in conversation_history 
                                if msg.get("metadata", {}).get("template_used")]
                
                available_templates = [t for t in templates if t not in used_templates]
                if not available_templates:
                    available_templates = templates  # Reset if all used
                
                import random
                selected_template = random.choice(available_templates)
            else:
                selected_template = None
        else:
            # Use initial scaffolding templates
            intensity = "high" if scaffolding_level == "high" else "medium"
            templates = SCAFFOLDING_PROMPT_TEMPLATES.get(scaffolding_type, {}).get(intensity, [])
            
            if templates:
                # Generate prompts using the utility function with correct signature
                prompts, used_indices = generate_default_prompts(
                    scaffolding_type=scaffolding_type,
                    scaffolding_intensity=scaffolding_level,  # Use scaffolding_level as intensity
                    analysis=None,  # We'll pass analysis separately if needed
                    enhanced_concept_map=concept_map,  # Pass the concept map
                    used_template_indices=[],  # Track used templates
                    conversation_turn=conversation_turn
                )
                # Use the first generated prompt (already personalized)
                selected_template = prompts[0] if prompts else None
            else:
                selected_template = None
        
        # Build system message based on scaffolding type and level
        system_message = self._get_scaffolding_system_message(scaffolding_type, scaffolding_level)
        
        # Build prompt incorporating the selected template
        if selected_template:
            # Use the template as the base prompt
            prompt = self._build_scaffolding_prompt_with_template(
                selected_template, scaffolding_type, concept_map, user_response, context, scaffolding_level
            )
        else:
            # Fallback to original prompt building
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
        result["template_used"] = selected_template if selected_template else "none"
        
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
            "conceptual": f"""Du bist ein konzeptueller Scaffolding Agent fur die Aufgabe zu Adaptive Market Gatekeeping (AMG) und internationalem Markteintritt.

SCAFFOLDING LEVEL: {scaffolding_level.upper()}
ROLLE: Hilf Lernenden zu verstehen, was die Beziehungen zwischen AMG-Mechanismen und Markteintrittskonzepten bedeuten.
PRINZIP: Führe zu konzeptuellen Verbindungen, gib keine direkten Antworten.

SCAFFOLDING-ANSATZ:
- Erkläre die vier AMG-Mechanismen (dynamische Anpassung, Regelanderung, Netzwerkkontrolle, Ressourcenblockierung)
- Klarifiziere Beziehungen zwischen AMG und Markteintrittsstrategien
- Leite zu tieferem Nachdenken an, wie AMG Start-ups beeinflusst
- Stelle Fragen, die AMG als Gatekeeper in Marktdynamiken verdeutlichen
- Nutze Scaffolding in {scaffolding_level}-Intensitat

INSTRUKTIONEN:
- Bleibe bei konzeptuellem Scaffolding
- Nutze Antworten in {scaffolding_level}-Intensitat
- Fuhre uber Klarstellungen
- Fokussiere AMG-Mechanismen und ihre Beziehungen zu anderen Konzepten
- Beziehe dich auf den aktuellen Zustand der Concept Map
- Fördere Verstandnis von Knoten und Kanten
- Bleibe unterstützend und edukativ""",
            
            "strategic": f"""Du bist ein strategischer Scaffolding Agent fur die AMG-Markteintrittsaufgabe.

SCAFFOLDING LEVEL: {scaffolding_level.upper()}
ROLLE: Hilf Lernenden, Probleme zu erkennen und strategische Losungen für den Markteintritt in ihrer Concept Map zu entwickeln.
PRINZIP: Fuhre zu Organisationsstrategien, gib keine direkten Antworten.

SCAFFOLDING-ANSATZ:
- Hilf, AMG zentral zu platzieren, um die Gatekeeping-Rolle zu zeigen
- Leite an, sowohl AMG-Herausforderungen als auch Losungen abzubilden
- Hilf, die „Story“ der Map-Struktur zu erkennen
- Regt zum Nachdenken an, welche Konzepte betont werden sollten und warum
- Nutze Scaffolding in {scaffolding_level}-Intensitat

INSTRUKTIONEN:
- Bleibe bei strategischem Scaffolding
- Nutze Antworten in {scaffolding_level}-Intensitat
- Fuhre uber Fragen, keine direkten Antworten
- Fokussiere die strategische Anordnung der AMG-Beziehungen
- Beziehe dich auf den aktuellen Zustand der Concept Map
- Bleibe praxisnah und strukturiert""",
            
            "metacognitive": f"""Du bist ein metakognitiver Scaffolding Agent fur die AMG-Markteintrittsaufgabe.

SCAFFOLDING LEVEL: {scaffolding_level.upper()}
ROLLE: Hilf Lernenden, ihren Lernprozess zu reflektieren, wahrend sie AMG und Markteintritt verstehen.
PRINZIP: Fuhre zu Selbstwahrnehmung und Selbststeuerung, gib keine direkten Antworten.

SCAFFOLDING-ANSATZ:
- Fokus auf Reflexion des Lernprozesses und Selbsteinschatzung
- Hilf einzuschätzen, wie Wissenslücken erkannt und geschlossen werden können
- Leite Reflexion darüber an, welche Lernstrategien funktionieren/nicht funktionieren
- Begleite die Lernreise
- Nutze Scaffolding in {scaffolding_level}-Intensitat

INSTRUKTIONEN:
- Bleibe bei metakognitivem Scaffolding
- Nutze Antworten in {scaffolding_level}-Intensitat
- Fuhre uber Fragen, keine direkten Antworten
- Fokussiere Selbstreflexion zum Verstandnis von AMG
- Beziehe dich auf den aktuellen Zustand der Concept Map
- Halte Antworten reflektierend und unterstützend""",
            
            "procedural": f"""Du bist ein prozeduraler Scaffolding Agent fur die AMG-Markteintrittsaufgabe.

SCAFFOLDING LEVEL: {scaffolding_level.upper()}
ROLLE: Hilf Lernenden, den Prozess des Mappings der AMG-Effekte auf den Markteintritt zu organisieren.
PRINZIP: Fuhre durch Ablaufe und Techniken zum gegebenen Inhalt, gib keine direkten Antworten.

SCAFFOLDING-ANSATZ:
- Leite systematisches Mapping der Effekte jedes AMG-Mechanismus Schritt für Schritt an
- Nutze Aktionswörter (blockiert, beeinflusst, kontert) für AMG-Beziehungen
- Schlage Schichtungen vor (AMG-Mechanismen, Strategien, Ressourcen)
- Hilf, Gegenstrategien zu AMG-Barrieren zu identifizieren
- Nutze Scaffolding in {scaffolding_level}-Intensitat

INSTRUKTIONEN:
- Bleibe bei prozeduralem Scaffolding
- Nutze Antworten in {scaffolding_level}-Intensitat
- Fuhre uber Fragen, keine direkten Antworten
- Fokussiere Ablaufe für das Mapping der AMG-Beziehungen
- Beziehe dich auf den aktuellen Zustand der Concept Map
- Fördere die Strukturierung von Knoten und Kanten
- Halte Antworten klar und anleitend"""
        }
        
        return base_messages.get(scaffolding_type, base_messages["conceptual"])
    
    def _build_scaffolding_prompt_with_template(self,
                                              template: str,
                                              scaffolding_type: str,
                                              concept_map: Dict[str, Any],
                                              user_response: Optional[str] = None,
                                              context: Optional[Dict[str, Any]] = None,
                                              scaffolding_level: str = "medium") -> str:
        """Build prompt using a specific template."""
        
        # Extract concept map information for context
        concepts = concept_map.get("concepts", [])
        relationships = concept_map.get("relationships", [])
        
        # Build concept list with text labels
        concept_list = []
        id_to_text = {}
        for c in concepts:
            label = c.get('text', c.get('label', c.get('id', 'Unknown')))
            concept_list.append(label)
            id_to_text[c.get('id', '')] = label
        
        # Build relationship descriptions
        relationship_descriptions = []
        for r in relationships:
            source_label = id_to_text.get(r.get('source'), r.get('source_text', r.get('source', 'Unknown')))
            target_label = id_to_text.get(r.get('target'), r.get('target_text', r.get('target', 'Unknown')))
            relation_text = r.get('text', r.get('relation', 'relates to'))
            relationship_descriptions.append(f"{source_label} {relation_text} {target_label}")
        
        # Build the prompt
        prompt_parts = [
            "Du lieferst Scaffolding fur eine Concept-Mapping-Aufgabe zu Adaptive Market Gatekeeping (AMG).",
            f"\nDie aktuelle Concept Map hat {len(concepts)} Konzepte und {len(relationships)} Beziehungen.",
            f"\nKonzepte enthalten: {', '.join(concept_list[:5])}{'...' if len(concept_list) > 5 else ''}",
        ]
        
        if relationship_descriptions:
            prompt_parts.append(f"\nWichtige Beziehungen: {'; '.join(relationship_descriptions[:3])}{'...' if len(relationship_descriptions) > 3 else ''}")
        
        # Add the template as the main instruction
        prompt_parts.extend([
            f"\n\nNutze diese Vorlage fur deine Antwort (personalisiere sie mit konkreten Konzepten aus der Map):",
            f'"{template}"',
            "\n\nWICHTIG: Verwende die Struktur und den Stil der Vorlage, ersetze Platzhalter mit konkreten Konzepten aus der Map.",
            "Behalte den gleichen Fragenstil und Scaffolding-Ansatz wie in der Vorlage bei."
        ])
        
        # Add user response context if available
        if user_response:
            prompt_parts.append(f"\n\nDie lernende Person hat geantwortet: \"{user_response}\"")
            prompt_parts.append("Wuerdige die Antwort passend und bleibe beim Scaffolding-Ansatz.")
        
        return "\n".join(prompt_parts)
    
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
            f"Ich analysiere eine Concept Map mit folgenden Elementen:",
            f"\nKonzepte ({len(concepts)}):",
            "\n".join(concept_list),
            f"\nBeziehungen ({len(relationships)}):",
            "\n".join(relationship_list) if relationship_list else "- Noch keine Beziehungen definiert"
        ]
        
        # Add context if available
        if context:
            round_num = context.get("round_number", 0)
            prompt_parts.append(f"\nDies ist Runde {round_num + 1} der Concept-Mapping-Session.")
        
        # Add user response if this is a follow-up
        if user_response:
            prompt_parts.extend([
                f"\nDie lernende Person antwortete: \"{user_response}\"",
                f"\nBitte liefere passende {scaffolding_type}-Unterstützung basierend auf dieser Antwort."
            ])
        else:
            prompt_parts.append(f"\nBitte liefere {scaffolding_type}-Scaffolding, um diese Concept Map zu verbessern.")
        
        prompt_parts.extend([
            f"\nGib eine hilfreiche, motivierende Antwort, die das Denken anleitet.",
            f"Halte die Antwort kurz (2-3 Satze) und stelle eine konkrete Frage, um Engagement zu fördern."
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
