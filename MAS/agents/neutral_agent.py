"""
Neutral Agent for Control Group

This agent provides task-helpful but learning-neutral responses.
Used for the CG_NEUTRAL experimental condition.
Acts like ChatGPT helping complete an assignment - provides factual information
and task guidance without facilitating learning or reflection.
"""

import random
import logging
import re
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class NeutralAgent:
    """
    Neutral agent that provides task completion assistance without learning scaffolding.
    - Answers questions with factual information from task materials
    - Answers directly on what to add/connect
    - Analyzes current map against task requirements
    - Acts as a people-pleasing task assistant
    - No pedagogical framing or reflection prompts
    """
    
    def __init__(self):
        self.name = "neutral"
        self.agent_type = "neutral"
        self.conversation_history = []  # Track conversation for context
    
    def generate_response(self, 
                         user_message: Optional[str] = None, 
                         concept_map: Optional[Dict[str, Any]] = None,
                         context: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate task-helpful but learning-neutral response.
        
        Args:
            user_message: User's input message
            concept_map: Current concept map data
            context: Additional context information
            
        Returns:
            Helpful, factual response for task completion
        """
        # Import pattern analysis from scaffolding_utils
        from MAS.utils.scaffolding_utils import analyze_user_response_type
        
        # Track conversation
        if user_message:
            self.conversation_history.append(user_message)
        
        # Extract map information
        node_count = 0
        edge_count = 0
        concept_labels = []
        missing_concepts = []
        
        if concept_map:
            concepts = concept_map.get("concepts", [])
            relationships = concept_map.get("relationships", [])
            node_count = len(concepts)
            edge_count = len(relationships)
            
            # Get concept labels for context
            for c in concepts:
                label = c.get('text', c.get('label', c.get('id', 'concept')))
                # Avoid showing UUIDs
                if '-' not in label or len(label) < 30:
                    concept_labels.append(label)
            
            # Identify missing concepts from task requirements
            missing_concepts = self._identify_missing_concepts(concept_labels)
        
        # Handle user input with pattern detection
        if user_message and len(user_message.strip()) > 0:
            response_analysis = analyze_user_response_type(user_message)
            
            # Handle specific patterns that need special responses
            if response_analysis.get("requires_pattern_response", False):
                return self._handle_pattern_response(user_message, response_analysis, concept_map)
            
            # Handle content questions with factual information
            if response_analysis.get("is_question", False):
                return self._handle_question(user_message, concept_map, concept_labels, missing_concepts)
            
            # Handle concrete ideas with agreement and suggestions
            if response_analysis.get("has_concrete_idea", False):
                return self._handle_concrete_idea(user_message, concept_map, concept_labels)
            
            # Default: provide contextual task guidance
            return self._provide_contextual_guidance(concept_map, concept_labels, missing_concepts)
        
        # No user input - provide progress-based guidance
        return self._provide_progress_guidance(concept_map, concept_labels, missing_concepts)
    
    def _identify_missing_concepts(self, current_concepts: List[str]) -> List[str]:
        """Identify concepts missing from task requirements."""
        # Required concept areas from task
        required_areas = {
            "market_analysis": ["Market Analysis", "market analysis", "target markets", "competitive environment", "competition"],
            "resources": ["Resources", "resources", "capital", "staff", "financing", "know-how", "expertise"],
            "entry_strategies": ["Export", "export", "Joint Venture", "joint venture", "Direct Investment", "direct investment", "entry strategies"],
            "amg": ["AMG", "Adaptive Market Gatekeeping", "gatekeeping", "amg"]
        }
        
        missing = []
        current_lower = [c.lower() for c in current_concepts]
        
        for area, keywords in required_areas.items():
            if not any(keyword.lower() in current_lower for keyword in keywords):
                if area == "market_analysis":
                    missing.append("Market Analysis")
                elif area == "resources":
                    missing.append("Resources (capital, staff, know-how)")
                elif area == "entry_strategies":
                    missing.append("Entry Strategies (Export, Joint Venture, Direct Investment)")
                elif area == "amg":
                    missing.append("AMG (Adaptive Market Gatekeeping)")
        
        return missing
    
    def _handle_pattern_response(self, user_message: str, response_analysis: Dict[str, Any], concept_map: Optional[Dict[str, Any]]) -> str:
        """Handle special patterns that need specific responses."""
        
        # Handle interface/system questions - direct to help (use pattern analysis result)
        if response_analysis.get("is_interface_help", False):
            return "For help with creating nodes and connections, please click the '❓ Help' button next to the task description."
        
        # Handle swear words/inappropriate language
        if response_analysis.get("is_inappropriate", False):
            return "Let's keep our discussion focused on the concept mapping task. Please continue working as instructed."
        
        # Handle empty input
        if response_analysis.get("is_empty", False):
            return "I didn't receive any input. Please continue with your concept mapping task."
        
        # Handle gibberish
        if response_analysis.get("is_gibberish", False):
            return "I didn't understand that. Please continue with your concept mapping task as described."
        
        # Handle minimal input
        if response_analysis.get("is_minimal_input", False):
            return "I need more information to help you. What would you like to know about the task?"
        
        # Handle greetings
        if response_analysis.get("is_greeting", False):
            return "Hello! Please continue with your concept mapping task as described in the task description."
        
        # Handle help seeking
        if response_analysis.get("is_help_seeking", False):
            return "Please check the 'Task Description' and 'Extra Materials' buttons for guidance. Continue working on your concept map as instructed."
        
        # Handle off-topic
        if response_analysis.get("is_off_topic", False):
            return "Please focus on the concept mapping task as described. Continue building your map according to the instructions."
        
        # Handle frustration
        if response_analysis.get("is_frustrated", False):
            return "I understand you have a different view. Please continue with your concept mapping as you see fit."
        
        # Default pattern response
        return "Please continue with your concept mapping task as described."
    
    def _is_interface_question(self, user_message: str) -> bool:
        """Check if user is asking about interface/system functionality."""
        interface_patterns = [
            r'how\s+(can|do)\s+i\s+(add|create|make)\s+(nodes?|concepts?|connections?|edges?|relationships?)',
            r'where\s+(can|do)\s+i\s+(add|create|click)',
            r'how\s+to\s+(add|create|make|use)',
            r'where\s+is\s+the\s+(button|tool|interface)',
            r'how\s+does\s+(this|the)\s+(tool|interface|system)\s+work'
        ]
        
        user_lower = user_message.lower()
        return any(re.search(pattern, user_lower) for pattern in interface_patterns)
    
    def _handle_question(self, user_message: str, concept_map: Optional[Dict[str, Any]], 
                        concept_labels: List[str], missing_concepts: List[str]) -> str:
        """Handle user questions with factual information from task materials."""
        
        user_lower = user_message.lower()
        
        # Questions about what to add
        if any(phrase in user_lower for phrase in ["what can i add", "what else can i add", "what should i add", "what to add"]):
            return self._suggest_missing_concepts(concept_labels, missing_concepts)
        
        # Questions about how to proceed
        if any(phrase in user_lower for phrase in ["how", "what should i do", "what next"]):
            return self._provide_next_steps(concept_map, missing_concepts)
        
        # Questions about connections
        if any(phrase in user_lower for phrase in ["what connections", "what relationships", "how to connect", "what to connect"]):
            return self._suggest_connections(concept_labels)
        
        # Questions about AMG
        if "amg" in user_lower or "adaptive market gatekeeping" in user_lower:
            return self._explain_amg()
        
        # Questions about entry strategies
        if any(phrase in user_lower for phrase in ["entry strategies", "export", "joint venture", "direct investment"]):
            return self._explain_entry_strategies()
        
        # Questions about task requirements
        if any(phrase in user_lower for phrase in ["task", "requirement", "supposed to", "need to"]):
            return self._explain_task_requirements(concept_map)
        
        # Default question response
        return "Please check the 'Task Description' and 'Extra Materials' buttons for detailed information about the concepts and requirements."
    
    def _suggest_missing_concepts(self, current_concepts: List[str], missing_concepts: List[str]) -> str:
        """Suggest specific missing concepts based on task requirements."""
        if missing_concepts:
            if len(current_concepts) > 0:
                current_text = f"You have {', '.join(current_concepts[:3])}{'...' if len(current_concepts) > 3 else ''}. "
            else:
                current_text = ""
            
            return f"{current_text}You still need to include: {', '.join(missing_concepts)}. The task requires concepts from all four main areas: Market Analysis, Resources, Entry Strategies, and AMG."
        else:
            return f"You have the main concept areas covered with {', '.join(current_concepts[:4])}. You can add more specific concepts like 'Financing', 'Target Markets', 'Competitive Environment', or 'Success Factors'."
    
    def _provide_next_steps(self, concept_map: Optional[Dict[str, Any]], missing_concepts: List[str]) -> str:
        """Provide specific next steps based on current map state."""
        if not concept_map or len(concept_map.get("concepts", [])) == 0:
            return "Start by adding the core concept 'AMG (Adaptive Market Gatekeeping)' to your map. Then add concepts for Market Analysis, Resources, and Entry Strategies."
        
        if missing_concepts:
            return f"Add the missing concept areas: {', '.join(missing_concepts)}. Then create labeled connections showing how AMG affects these other factors."
        
        edge_count = len(concept_map.get("relationships", []))
        if edge_count < 6:
            return f"You have {edge_count} connections but need at least 6. Add more relationships showing how AMG influences Market Analysis, Resources, and Entry Strategies."
        
        return "Your map covers the main areas. You can refine it by adding more specific concepts or strengthening the relationships between AMG and other factors."
    
    def _suggest_connections(self, concept_labels: List[str]) -> str:
        """Suggest specific connections based on current concepts."""
        suggestions = []
        
        # Check what concepts they have and suggest relevant connections
        has_amg = any("amg" in label.lower() or "gatekeeping" in label.lower() for label in concept_labels)
        has_market = any("market" in label.lower() for label in concept_labels)
        has_resources = any("resource" in label.lower() or "capital" in label.lower() or "financing" in label.lower() for label in concept_labels)
        has_strategies = any("export" in label.lower() or "joint" in label.lower() or "investment" in label.lower() or "strategy" in label.lower() for label in concept_labels)
        
        if has_amg and has_market:
            suggestions.append("AMG → Market Analysis (complicates)")
        if has_amg and has_resources:
            suggestions.append("AMG → Resources (blocks access to)")
        if has_amg and has_strategies:
            suggestions.append("AMG → Entry Strategies (restricts)")
        if has_market and has_strategies:
            suggestions.append("Market Analysis → Entry Strategies (informs)")
        if has_resources and has_strategies:
            suggestions.append("Resources → Entry Strategies (enables)")
        
        if suggestions:
            return f"You could connect: {', '.join(suggestions[:3])}. The task requires at least 6 connections showing how AMG affects other factors."
        else:
            return "Add connections like: AMG → Entry Barriers (increases), Resources → Entry Strategies (determines), Market Analysis → Target Markets (identifies)."
    
    def _explain_amg(self) -> str:
        """Explain AMG using task materials."""
        return "AMG (Adaptive Market Gatekeeping) uses four mechanisms: Dynamic adaptation (monitoring newcomers), Rule-changing (altering industry standards), Network control (controlling suppliers/distributors), and Resource blocking (tying up skilled workers, production capacity). Established firms use these to make market entry harder for start-ups."
    
    def _explain_entry_strategies(self) -> str:
        """Explain entry strategies from task materials."""
        return "The three entry strategies are: Export (shipping goods from home country), Joint Venture (partnership with local company), and Direct Investment (establishing own subsidiary). Each has different risk, control, and resource requirements."
    
    def _explain_task_requirements(self, concept_map: Optional[Dict[str, Any]]) -> str:
        """Explain task requirements with current progress."""
        node_count = len(concept_map.get("concepts", [])) if concept_map else 0
        edge_count = len(concept_map.get("relationships", [])) if concept_map else 0
        
        return f"The task requires concepts from four areas (Market Analysis, Resources, Entry Strategies, AMG) and at least 6 connections. You currently have {node_count} concepts and {edge_count} connections. Focus on how AMG affects the other factors."
    
    def _handle_concrete_idea(self, user_message: str, concept_map: Optional[Dict[str, Any]], concept_labels: List[str]) -> str:
        """Handle when user shares concrete ideas - agree and suggest implementation."""
        # Extract key concepts mentioned
        mentioned_concepts = []
        for label in concept_labels:
            if label.lower() in user_message.lower():
                mentioned_concepts.append(label)
        
        if mentioned_concepts:
            response = f"Good point about {', '.join(mentioned_concepts[:2])}. "
        else:
            response = "That's a useful insight. "
        
        # Check if their map reflects their ideas
        if concept_map and len(concept_map.get("concepts", [])) > 0:
            response += "Does your current map show these relationships? You can add or modify connections to better represent these ideas."
        else:
            response += "You can add these concepts to your map and connect them to show these relationships."
        
        return response
    
    def _provide_contextual_guidance(self, concept_map: Optional[Dict[str, Any]], concept_labels: List[str], missing_concepts: List[str]) -> str:
        """Provide contextual guidance based on current map state."""
        if not concept_map or len(concept_map.get("concepts", [])) == 0:
            return "Start by adding the main concepts: AMG (Adaptive Market Gatekeeping), Market Analysis, Resources, and Entry Strategies. Then connect them to show how AMG affects market entry."
        
        if missing_concepts:
            return f"You have {', '.join(concept_labels[:3])}. Add the missing areas: {', '.join(missing_concepts)}."
        
        edge_count = len(concept_map.get("relationships", []))
        if edge_count < 6:
            return f"You have {edge_count} connections but need at least 6. Add relationships showing how AMG mechanisms (rule-changing, network control, resource blocking) affect market entry factors."
        
        return f"Your map has {len(concept_labels)} concepts and {edge_count} connections. You can refine it by adding more specific concepts or strengthening the relationships between AMG and other factors."
    
    def _provide_progress_guidance(self, concept_map: Optional[Dict[str, Any]], concept_labels: List[str], missing_concepts: List[str]) -> str:
        """Provide progress-based guidance when no user input."""
        if not concept_map or len(concept_map.get("concepts", [])) == 0:
            return "Begin by adding the core concept 'AMG (Adaptive Market Gatekeeping)' and the three other main areas: Market Analysis, Resources, and Entry Strategies."
        
        if missing_concepts:
            return f"Looking at your current concepts {', '.join(concept_labels[:3])}, you still need: {', '.join(missing_concepts)}."
        
        edge_count = len(concept_map.get("relationships", []))
        node_count = len(concept_labels)
        
        if edge_count < 6:
            return f"You have {node_count} concepts and {edge_count} connections. The task requires at least 6 connections showing how AMG affects the other factors."
        
        return f"Your map has {node_count} concepts and {edge_count} connections, covering the main task requirements. You can continue refining the relationships."
