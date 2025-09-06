"""
Scaffolding Utilities

This module provides utility functions for scaffolding in the multi-agent scaffolding system.
"""

import logging
import random
from typing import Dict, List, Any, Optional, Tuple

logger = logging.getLogger(__name__)

def analyze_concept_map(concept_map: Dict[str, Any],
                       previous_map: Optional[Dict[str, Any]] = None,
                       expert_map: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Analyze a concept map to identify areas for scaffolding.
    
    Args:
        concept_map: Concept map to analyze
        previous_map: Previous concept map (optional)
        expert_map: Expert concept map (optional)
        
    Returns:
        Analysis results
    """
    logger.info("Analyzing concept map")
    
    # Extract nodes and edges
    nodes = concept_map.get("nodes", [])
    edges = concept_map.get("edges", [])
    
    # Initialize analysis results
    analysis = {
        "node_count": len(nodes),
        "edge_count": len(edges),
        "connectivity_ratio": len(edges) / max(1, len(nodes)),
        "isolated_nodes": [],
        "central_nodes": [],
        "missing_nodes": [],
        "missing_edges": [],
        "zpd_estimate": {
            "strategic": 0.5,
            "metacognitive": 0.5,
            "procedural": 0.5,
            "conceptual": 0.5
        }
    }
    
    # Identify isolated nodes
    connected_nodes = set()
    for edge in edges:
        source = edge.get("source")
        target = edge.get("target")
        if source:
            connected_nodes.add(source)
        if target:
            connected_nodes.add(target)
    
    analysis["isolated_nodes"] = [node for node in nodes if node not in connected_nodes]
    
    # Identify central nodes (nodes with the most connections)
    node_connections = {}
    for edge in edges:
        source = edge.get("source")
        target = edge.get("target")
        if source:
            node_connections[source] = node_connections.get(source, 0) + 1
        if target:
            node_connections[target] = node_connections.get(target, 0) + 1
    
    # Sort nodes by connection count
    sorted_nodes = sorted(node_connections.items(), key=lambda x: x[1], reverse=True)
    
    # Get top 3 central nodes
    analysis["central_nodes"] = [node for node, count in sorted_nodes[:min(3, len(sorted_nodes))]]
    
    # Compare with expert map if available
    if expert_map:
        expert_nodes = expert_map.get("nodes", [])
        expert_edges = expert_map.get("edges", [])
        
        # Identify missing nodes
        analysis["missing_nodes"] = [node for node in expert_nodes if node not in nodes]
        
        # Identify missing edges
        expert_edge_pairs = [(edge.get("source"), edge.get("target")) for edge in expert_edges]
        map_edge_pairs = [(edge.get("source"), edge.get("target")) for edge in edges]
        
        analysis["missing_edges"] = [
            {"source": source, "target": target}
            for source, target in expert_edge_pairs
            if (source, target) not in map_edge_pairs and source in nodes and target in nodes
        ]
    
    # Compare with previous map if available
    if previous_map:
        previous_nodes = previous_map.get("nodes", [])
        previous_edges = previous_map.get("edges", [])
        
        # Calculate growth
        node_growth = len(nodes) - len(previous_nodes)
        edge_growth = len(edges) - len(previous_edges)
        
        analysis["node_growth"] = node_growth
        analysis["edge_growth"] = edge_growth
    
    # Estimate ZPD based on analysis
    # This is a simplified implementation
    # In a real implementation, this would use more sophisticated analysis
    
    # Strategic scaffolding need based on organization and growth
    if analysis["connectivity_ratio"] < 0.5 or (previous_map and analysis["node_growth"] == 0):
        analysis["zpd_estimate"]["strategic"] = 0.8  # High need
    elif analysis["connectivity_ratio"] < 1.0:
        analysis["zpd_estimate"]["strategic"] = 0.5  # Medium need
    else:
        analysis["zpd_estimate"]["strategic"] = 0.2  # Low need
    
    # Metacognitive scaffolding need based on map complexity
    if len(nodes) < 5:
        analysis["zpd_estimate"]["metacognitive"] = 0.8  # High need
    elif len(nodes) < 10:
        analysis["zpd_estimate"]["metacognitive"] = 0.5  # Medium need
    else:
        analysis["zpd_estimate"]["metacognitive"] = 0.2  # Low need
    
    # Procedural scaffolding need based on isolated nodes
    if len(analysis["isolated_nodes"]) > 2:
        analysis["zpd_estimate"]["procedural"] = 0.8  # High need
    elif len(analysis["isolated_nodes"]) > 0:
        analysis["zpd_estimate"]["procedural"] = 0.5  # Medium need
    else:
        analysis["zpd_estimate"]["procedural"] = 0.2  # Low need
    
    # Conceptual scaffolding need based on missing nodes and edges
    if expert_map and (len(analysis["missing_nodes"]) > 5 or len(analysis["missing_edges"]) > 5):
        analysis["zpd_estimate"]["conceptual"] = 0.8  # High need
    elif expert_map and (len(analysis["missing_nodes"]) > 2 or len(analysis["missing_edges"]) > 2):
        analysis["zpd_estimate"]["conceptual"] = 0.5  # Medium need
    else:
        analysis["zpd_estimate"]["conceptual"] = 0.2  # Low need
    
    return analysis

def select_scaffolding_type(analysis: Dict[str, Any],
                           enabled_types: List[str],
                           weights: Dict[str, float],
                           interaction_history: List[Dict[str, Any]] = None) -> Tuple[str, str, str]:
    """
    Select the appropriate scaffolding type based on the current state.
    
    Args:
        analysis: Concept map analysis
        enabled_types: List of enabled scaffolding types
        weights: Weights for each scaffolding type
        interaction_history: History of previous interactions
        
    Returns:
        Tuple of (scaffolding_type, scaffolding_intensity, selection_reasoning)
    """
    logger.info("Selecting scaffolding type")
    
    # If no types are enabled, return None
    if not enabled_types:
        return None, None, "No scaffolding types are enabled"
    
    # Filter weights to only include enabled types
    filtered_weights = {t: w for t, w in weights.items() if t in enabled_types}
    
    # Adjust weights based on ZPD estimate
    if analysis and "zpd_estimate" in analysis:
        zpd_estimate = analysis["zpd_estimate"]
        for scaffolding_type in filtered_weights:
            if scaffolding_type in zpd_estimate:
                # Higher ZPD estimate = higher weight
                filtered_weights[scaffolding_type] *= (1.0 + zpd_estimate[scaffolding_type])
    
    # Adjust weights based on interaction history
    if interaction_history:
        # Reduce weight for recently used types
        for interaction in reversed(interaction_history[-3:]):
            scaffolding_type = interaction.get("scaffolding_type")
            if scaffolding_type in filtered_weights:
                filtered_weights[scaffolding_type] *= 0.8  # Reduce weight by 20%
    
    # Select scaffolding type based on weights
    if not filtered_weights:
        return None, None, "No scaffolding types have positive weights"
    
    # Normalize weights
    total_weight = sum(filtered_weights.values())
    if total_weight > 0:
        normalized_weights = {t: w / total_weight for t, w in filtered_weights.items()}
    else:
        normalized_weights = {t: 1.0 / len(filtered_weights) for t in filtered_weights}
    
    # Select scaffolding type
    scaffolding_type = weighted_selection(list(normalized_weights.keys()), list(normalized_weights.values()))
    
    # Determine scaffolding intensity based on ZPD estimate
    intensity = "medium"  # Default intensity
    if analysis and "zpd_estimate" in analysis and scaffolding_type in analysis["zpd_estimate"]:
        zpd = analysis["zpd_estimate"][scaffolding_type]
        if zpd > 0.7:
            intensity = "high"
        elif zpd < 0.3:
            intensity = "low"
    
    # Generate selection reasoning
    selection_reasoning = f"Selected {scaffolding_type} scaffolding at {intensity} intensity "
    
    if analysis:
        if scaffolding_type == "strategic":
            if "connectivity_ratio" in analysis:
                selection_reasoning += f"based on connectivity ratio of {analysis['connectivity_ratio']:.2f}"
            elif "node_growth" in analysis:
                selection_reasoning += f"based on node growth of {analysis['node_growth']}"
        elif scaffolding_type == "metacognitive":
            selection_reasoning += f"based on concept map complexity ({analysis['node_count']} nodes)"
        elif scaffolding_type == "procedural":
            selection_reasoning += f"based on {len(analysis.get('isolated_nodes', []))} isolated nodes"
        elif scaffolding_type == "conceptual":
            if "missing_nodes" in analysis:
                selection_reasoning += f"based on {len(analysis['missing_nodes'])} missing concepts"
            elif "missing_edges" in analysis:
                selection_reasoning += f"based on {len(analysis['missing_edges'])} missing relationships"
    
    return scaffolding_type, intensity, selection_reasoning

def weighted_selection(items: List[Any], weights: List[float]) -> Any:
    """
    Select an item from a list based on weights.
    
    Args:
        items: List of items
        weights: List of weights
        
    Returns:
        Selected item
    """
    # Ensure weights are non-negative
    weights = [max(0, w) for w in weights]
    
    # If all weights are zero, use equal weights
    if sum(weights) == 0:
        weights = [1.0] * len(items)
    
    # Select an item based on weights
    return random.choices(items, weights=weights, k=1)[0]

def analyze_learner_response(response: str, scaffolding_type: str) -> Dict[str, Any]:
    """
    Analyze a learner response to a scaffolding prompt.
    
    Args:
        response: Learner response
        scaffolding_type: Type of scaffolding
        
    Returns:
        Analysis results
    """
    logger.info(f"Analyzing learner response to {scaffolding_type} prompt")
    
    # Initialize analysis results
    analysis = {
        "length": len(response),
        "word_count": len(response.split()),
        "question_count": response.count("?"),
        "needs_follow_up": False
    }
    
    # Determine if a follow-up is needed
    # This is a simplified implementation
    # In a real implementation, this would use more sophisticated analysis
    
    # Short responses may need follow-up
    if analysis["word_count"] < 5:
        analysis["needs_follow_up"] = True
        analysis["follow_up_reason"] = "Short response"
    
    # Responses with questions may need follow-up
    elif analysis["question_count"] > 0:
        analysis["needs_follow_up"] = True
        analysis["follow_up_reason"] = "Response contains questions"
    
    # Some responses need follow-up based on content
    elif "not sure" in response.lower() or "don't know" in response.lower():
        analysis["needs_follow_up"] = True
        analysis["follow_up_reason"] = "Uncertainty in response"
    
    # Randomly decide to follow up sometimes
    elif random.random() < 0.3:
        analysis["needs_follow_up"] = True
        analysis["follow_up_reason"] = "Random follow-up"
    
    return analysis

def generate_default_prompts(scaffolding_type: str, 
                            scaffolding_intensity: str,
                            analysis: Optional[Dict[str, Any]] = None,
                            enhanced_concept_map: Optional[Dict[str, Any]] = None,
                            used_template_indices: Optional[List[int]] = None,
                            conversation_turn: int = 0) -> Tuple[List[str], List[int]]:
    """
    Generate default scaffolding prompts without repetition.
    
    Args:
        scaffolding_type: Type of scaffolding
        scaffolding_intensity: Intensity of scaffolding (high or medium only)
        analysis: Concept map analysis (optional)
        enhanced_concept_map: Enhanced concept map with resolved labels (optional)
        used_template_indices: List of already used template indices
        conversation_turn: Current turn in the conversation
        
    Returns:
        Tuple of (List of scaffolding prompts, List of template indices used)
    """
    from MAS.config.scaffolding_config import SCAFFOLDING_PROMPT_TEMPLATES
    
    # Initialize used indices if not provided
    if used_template_indices is None:
        used_template_indices = []
    
    # Ensure we only use high or medium intensity
    if scaffolding_intensity not in ["high", "medium"]:
        scaffolding_intensity = "medium"
    
    # Get available templates for this type and intensity
    available_templates = SCAFFOLDING_PROMPT_TEMPLATES.get(scaffolding_type, {}).get(scaffolding_intensity, [])
    
    if not available_templates:
        # Fallback to medium if high not available
        available_templates = SCAFFOLDING_PROMPT_TEMPLATES.get(scaffolding_type, {}).get("medium", [])
    
    # Filter out already used templates
    unused_indices = [i for i in range(len(available_templates)) if i not in used_template_indices]
    
    # If all templates have been used, we need a fallback strategy
    if not unused_indices:
        logger.warning(f"All templates for {scaffolding_type}/{scaffolding_intensity} have been used")
        # Reset and use all templates again, but try to pick the least recently used
        unused_indices = list(range(len(available_templates)))
    
    # Select template based on context
    selected_index = _select_best_template_index(
        unused_indices,
        available_templates,
        analysis,
        enhanced_concept_map,
        conversation_turn
    )
    
    # Get the selected template
    selected_template = available_templates[selected_index]
    
    # Fill in the template with context
    filled_prompt = _fill_template_with_context(
        selected_template,
        analysis,
        enhanced_concept_map
    )
    
    # Return the prompt and the index used
    return [filled_prompt], [selected_index]
    
    # Default prompts by scaffolding type and intensity
    default_prompts = {
        "strategic": {
            "high": [
                "How did you decide which concepts to include in your map?",
                "What strategy did you use to organize the concepts in your map?",
                "How did you determine which relationships to include between concepts?"
            ],
            "medium": [
                "What approach did you take when creating your concept map?",
                "How did you decide which concepts to connect with relationships?"
            ],
            "low": [
                "What was your overall approach to creating this concept map?"
            ]
        },
        "metacognitive": {
            "high": [
                "Which parts of your concept map are you most confident about?",
                "Which parts are you least confident about?",
                "How has your understanding of this topic changed as you created this map?"
            ],
            "medium": [
                "What have you learned from creating this concept map?",
                "What aspects of the topic do you feel you understand well or not so well?"
            ],
            "low": [
                "How do you feel about your understanding of this topic?"
            ]
        },
        "procedural": {
            "high": [
                "What steps did you follow to create your concept map?",
                "What techniques did you use to identify relationships between concepts?",
                "How did you decide on the layout of your concept map?"
            ],
            "medium": [
                "What process did you use to create your concept map?",
                "How did you approach adding relationships between concepts?"
            ],
            "low": [
                "What was your process for creating this concept map?"
            ]
        },
        "conceptual": {
            "high": [
                "How do you think these concepts relate to each other?",
                "What do you think is the most important concept in your map and why?",
                "Are there any concepts you considered including but decided not to? Why?"
            ],
            "medium": [
                "What do you think are the key concepts in this topic?",
                "How do you understand the relationships between these concepts?"
            ],
            "low": [
                "What do you think is the main idea represented in your concept map?"
            ]
        }
    }
    
    # Get prompts for the specified type and intensity
    if scaffolding_type in default_prompts and scaffolding_intensity in default_prompts[scaffolding_type]:
        return default_prompts[scaffolding_type][scaffolding_intensity]
    
    # Fallback to medium intensity if specified intensity is not available
    if scaffolding_type in default_prompts and "medium" in default_prompts[scaffolding_type]:
        return default_prompts[scaffolding_type]["medium"]
    
    # Fallback to strategic prompts if specified type is not available
    if "strategic" in default_prompts and scaffolding_intensity in default_prompts["strategic"]:
        return default_prompts["strategic"][scaffolding_intensity]
    
    # Final fallback
    return [
        "How did you approach creating this concept map?",
        "What do you think about the concepts and relationships you've included?"
    ]

def generate_default_follow_up(response: str,
                              analysis: Dict[str, Any],
                              scaffolding_type: str) -> str:
    """
    Generate a default follow-up prompt.
    
    Args:
        response: Learner response
        analysis: Response analysis
        scaffolding_type: Type of scaffolding
        
    Returns:
        Default follow-up prompt
    """
    # Default follow-ups by scaffolding type
    default_follow_ups = {
        "strategic": [
            "That's interesting. Can you tell me more about your approach?",
            "How did that strategy help you understand the topic better?",
            "Have you considered other ways to organize these concepts?"
        ],
        "metacognitive": [
            "Why do you feel that way about your understanding?",
            "How has your thinking about this topic changed?",
            "What aspects of this topic would you like to understand better?"
        ],
        "procedural": [
            "What was the most challenging part of that process?",
            "How might you approach it differently next time?",
            "What tools or techniques would help you improve your map?"
        ],
        "conceptual": [
            "How does that concept relate to the others in your map?",
            "Why do you think that relationship is important?",
            "What might be some real-world examples of this concept?"
        ]
    }
    
    # Get follow-ups for the specified type
    if scaffolding_type in default_follow_ups:
        return random.choice(default_follow_ups[scaffolding_type])
    
    # Fallback
    return "Can you elaborate on that a bit more?"

def generate_default_conclusion(scaffolding_type: str) -> str:
    """
    Generate a default conclusion for a scaffolding interaction.
    
    Args:
        scaffolding_type: Type of scaffolding
        
    Returns:
        Default conclusion text
    """
    # Default conclusions by scaffolding type
    default_conclusions = {
        "strategic": "Thank you for sharing your approach to concept mapping. Thinking strategically about how you organize and connect concepts can help deepen your understanding of the topic.",
        "metacognitive": "Thank you for reflecting on your learning process. Being aware of your own thinking and understanding is a valuable skill that can help you learn more effectively.",
        "procedural": "Thank you for explaining your process. Having a systematic approach to concept mapping can help you create more comprehensive and organized maps.",
        "conceptual": "Thank you for sharing your understanding of these concepts. Exploring the relationships between concepts is key to developing a deeper understanding of the topic."
    }
    
    # Get conclusion for the specified type
    if scaffolding_type in default_conclusions:
        return default_conclusions[scaffolding_type]
    
    # Fallback
    return "Thank you for your responses. This reflection will help you develop a deeper understanding of the topic."

def format_scaffolding_text(text: str, scaffolding_type: str) -> str:
    """
    Format scaffolding text with appropriate prefix.
    
    Args:
        text: Scaffolding text
        scaffolding_type: Type of scaffolding
        
    Returns:
        Formatted scaffolding text
    """
    # Get emoji for scaffolding type
    emoji = {
        "strategic": "🧭",
        "metacognitive": "🧠",
        "procedural": "🛠️",
        "conceptual": "💡"
    }.get(scaffolding_type, "🤖")
    
    # Format text
    return f"{emoji} {text}"

def _select_best_template_index(unused_indices: List[int],
                               available_templates: List[str],
                               analysis: Optional[Dict[str, Any]],
                               enhanced_concept_map: Optional[Dict[str, Any]],
                               conversation_turn: int) -> int:
    """
    Select the best template index based on context.
    
    Args:
        unused_indices: List of unused template indices
        available_templates: All available templates
        analysis: Concept map analysis
        enhanced_concept_map: Enhanced concept map
        conversation_turn: Current conversation turn
        
    Returns:
        Selected template index
    """
    if not unused_indices:
        return 0
    
    # Score each unused template based on relevance
    template_scores = {}
    
    for idx in unused_indices:
        template = available_templates[idx]
        score = 0
        
        # Check for placeholders that can be filled
        if analysis:
            if "{observation}" in template and analysis.get("isolated_nodes"):
                score += 2
            if "{node_count}" in template and "node_count" in analysis:
                score += 1
            if "{edge_count}" in template and "edge_count" in analysis:
                score += 1
            if "{concept}" in template and analysis.get("central_nodes"):
                score += 2
        
        # Prefer templates appropriate for conversation turn
        if conversation_turn == 0:
            # First turn: prefer broader questions
            if "overall" in template.lower() or "approach" in template.lower():
                score += 2
        else:
            # Later turns: prefer more specific questions
            if "specific" in template.lower() or "particular" in template.lower():
                score += 2
        
        template_scores[idx] = score
    
    # Sort by score and select the best
    sorted_indices = sorted(template_scores.keys(), key=lambda x: template_scores[x], reverse=True)
    return sorted_indices[0] if sorted_indices else unused_indices[0]


def _fill_template_with_context(template: str,
                               analysis: Optional[Dict[str, Any]],
                               enhanced_concept_map: Optional[Dict[str, Any]]) -> str:
    """
    Fill a template with contextual information.
    
    Args:
        template: Template string with placeholders
        analysis: Concept map analysis
        enhanced_concept_map: Enhanced concept map
        
    Returns:
        Filled template string
    """
    filled = template
    
    if analysis:
        # Fill basic counts
        if "{node_count}" in filled:
            filled = filled.replace("{node_count}", str(analysis.get("node_count", 0)))
        if "{edge_count}" in filled:
            filled = filled.replace("{edge_count}", str(analysis.get("edge_count", 0)))
        
        # Fill observations
        if "{observation}" in filled:
            observation = _generate_observation(analysis, enhanced_concept_map)
            filled = filled.replace("{observation}", observation)
        
        # Fill concept references
        if "{concept}" in filled or "{another_concept}" in filled:
            concepts = _get_concept_labels(enhanced_concept_map)
            if concepts:
                filled = filled.replace("{concept}", concepts[0] if concepts else "a key concept")
                if "{another_concept}" in filled and len(concepts) > 1:
                    filled = filled.replace("{another_concept}", concepts[1])
                elif "{another_concept}" in filled:
                    filled = filled.replace("{another_concept}", "another concept")
    
    return filled


def _generate_observation(analysis: Dict[str, Any], 
                         enhanced_concept_map: Optional[Dict[str, Any]]) -> str:
    """
    Generate an observation about the concept map.
    
    Args:
        analysis: Concept map analysis
        enhanced_concept_map: Enhanced concept map
        
    Returns:
        Observation string
    """
    observations = []
    
    if analysis.get("isolated_nodes"):
        count = len(analysis["isolated_nodes"])
        observations.append(f"you have {count} unconnected concept{'s' if count > 1 else ''}")
    
    if analysis.get("connectivity_ratio", 0) < 0.5:
        observations.append("your map has relatively few connections between concepts")
    
    if analysis.get("node_growth", 0) == 0 and analysis.get("edge_growth") is not None:
        observations.append("your map hasn't grown much from the previous round")
    
    if enhanced_concept_map:
        concepts = _get_concept_labels(enhanced_concept_map)
        if concepts and len(concepts) > 3:
            observations.append(f"you've included concepts like '{concepts[0]}' and '{concepts[1]}'")
    
    return observations[0] if observations else "your concept map is developing"


def _get_concept_labels(enhanced_concept_map: Optional[Dict[str, Any]]) -> List[str]:
    """
    Extract concept labels from an enhanced concept map.
    
    Args:
        enhanced_concept_map: Enhanced concept map
        
    Returns:
        List of concept labels
    """
    if not enhanced_concept_map:
        return []
    
    labels = []
    concepts = enhanced_concept_map.get("concepts", enhanced_concept_map.get("nodes", []))
    
    for concept in concepts:
        if isinstance(concept, dict):
            label = concept.get("label", concept.get("text", concept.get("id", "")))
            if label and label not in labels:
                labels.append(label)
        elif isinstance(concept, str) and concept not in labels:
            labels.append(concept)
    
    return labels


def analyze_user_response_type(response: str) -> Dict[str, Any]:
    """
    Analyze user response to detect interaction patterns and extract key information.
    
    Args:
        response: User's response text
        
    Returns:
        Dictionary with comprehensive response analysis
    """
    analysis = {
        "is_question": False,
        "is_confused": False,
        "has_concrete_idea": False,
        "mentions_concepts": [],
        "response_type": "statement",
        "key_phrases": [],
        # New pattern detection fields
        "is_empty": False,
        "is_domain_question": False,
        "is_system_question": False,
        "is_disagreement": False,
        "disagreement_type": None,
        "is_inappropriate": False,
        "is_off_topic": False,
        "is_frustrated": False,
        "wants_to_end": False,
        "needs_encouragement": False,
        "requires_pattern_response": False,  # CRITICAL: Add this flag
        "is_help_seeking": False,  # NEW: For "what should I do" questions
        "is_gibberish": False,  # NEW: For random text
        "has_intention_without_action": False,  # NEW: For "I can add X" without doing it
        "is_greeting": False,  # NEW: For greetings like "hi", "hello"
        "is_reassurance_seeking": False  # NEW: For "how am I doing?" questions
    }
    
    # Enhanced empty input detection - includes whitespace-only
    if not response or not response.strip() or len(response.strip()) == 0:
        analysis["is_empty"] = True
        analysis["response_type"] = "empty_input"
        analysis["requires_pattern_response"] = True  # Pattern needs handling
        return analysis
    
    response_lower = response.lower().strip()
    
    # NEW: Detect minimal/single character input (e, eh, a, etc.)
    if len(response_lower) <= 2:
        # Single characters or very short responses that aren't meaningful
        minimal_patterns = ['e', 'eh', 'ey', 'a', 'ah', 'ok', 'no', 'ye', 'ya']
        if response_lower in minimal_patterns or (len(response_lower) == 1 and response_lower.isalpha()):
            analysis["is_minimal_input"] = True
            analysis["response_type"] = "minimal_input"
            analysis["requires_pattern_response"] = True
            return analysis
    
    # NEW: Enhanced gibberish/random text detection
    import re
    
    # Multiple gibberish detection strategies
    if len(response_lower) > 2:  # Check anything longer than minimal input
        # Remove spaces for analysis
        text_no_spaces = response_lower.replace(" ", "")
        
        # Strategy 1: Check vowel ratio (too few vowels = likely gibberish)
        # Include 'y' as a vowel in certain contexts
        vowel_count = len(re.findall(r'[aeiouy]', text_no_spaces))
        vowel_ratio = vowel_count / len(text_no_spaces) if text_no_spaces else 0
        
        # Strategy 2: Check for excessive consonant clusters
        consonant_clusters = re.findall(r'[bcdfghjklmnpqrstvwxyz]{5,}', text_no_spaces)
        
        # Strategy 3: Check for excessive special characters
        special_char_count = len(re.findall(r'[^a-z0-9\s]', response_lower))
        special_char_ratio = special_char_count / len(response_lower)
        
        # Strategy 4: Check for repeated character patterns (e.g., "asdfasdf", "qweqweqwe")
        repeated_patterns = re.findall(r'(.{2,})\1{1,}', text_no_spaces)  # Changed to detect even 2x repetition
        
        # Strategy 5: Check for keyboard mashing patterns (e.g., "asdf", "qwerty", "zxcv")
        keyboard_patterns = [
            'qwer', 'asdf', 'zxcv', 'qweasd', 'asdzxc', 'qazwsx', 'wsxedc',
            'poiu', 'lkjh', 'mnbv', 'rtyu', 'fghj', 'vbnm', 'tyui', 'ghjk',
            'qwertyuiop', 'asdfghjkl', 'zxcvbnm', 'qazxsw', 'wsxcde',
            '1234', '4321', 'abcd', 'dcba', 'aaaa', 'bbbb', 'cccc'
        ]
        has_keyboard_pattern = any(pattern in text_no_spaces for pattern in keyboard_patterns)
        
        # Strategy 6: Check for alternating hands keyboard pattern (e.g., "fjfjfj", "dkdkdk")
        alternating_pattern = re.findall(r'([a-z])([a-z])\1\2{2,}', text_no_spaces)
        
        # Strategy 7: Check for single repeated character (e.g., "aaaaa", "zzzzz")
        single_char_repeat = re.findall(r'([a-z])\1{4,}', text_no_spaces)
        
        # Strategy 8: Check for random number-letter mix without meaning
        # Look for alternating patterns like a1b2c3
        random_mix = []
        if re.search(r'[a-z]\d[a-z]\d', text_no_spaces) or re.search(r'\d[a-z]\d[a-z]', text_no_spaces):
            # Check if it's truly random (not something like "a1b2" in a larger context)
            if len(re.findall(r'[a-z]\d', text_no_spaces)) >= 3 or len(re.findall(r'\d[a-z]', text_no_spaces)) >= 3:
                random_mix = ['detected']
        
        # Strategy 9: Check if it's just random punctuation or symbols
        if len(text_no_spaces) == 0 and special_char_count > 2:
            analysis["is_gibberish"] = True
            analysis["response_type"] = "gibberish"
            analysis["requires_pattern_response"] = True
            return analysis
        
        # Determine if gibberish based on multiple factors
        is_gibberish = False
        
        # Check conditions (more lenient for shorter inputs)
        if len(text_no_spaces) <= 10:
            # For short inputs, be more strict
            # Special case: common short words with 'y' as vowel
            common_y_words = ['why', 'try', 'fly', 'cry', 'dry', 'sky', 'spy', 'shy', 'my', 'by']
            if response_lower in common_y_words:
                is_gibberish = False
            elif (vowel_ratio < 0.1 and len(text_no_spaces) > 3) or \
               has_keyboard_pattern or \
               single_char_repeat or \
               repeated_patterns or \
               (special_char_ratio > 0.5 and special_char_count > 2) or \
               (len(text_no_spaces) == 3 and vowel_ratio == 0):  # xyz case
                is_gibberish = True
            # Check for mixed keyboard mash with symbols/numbers
            elif len(text_no_spaces) >= 4 and (
                (has_keyboard_pattern and special_char_count > 0) or  # qwe!@#
                (re.search(r'[a-z]{3,}', text_no_spaces) and re.search(r'\d', text_no_spaces) and vowel_ratio < 0.2)  # asdlkj123
            ):
                is_gibberish = True
        else:
            # For longer inputs, use combined criteria
            if (vowel_ratio < 0.15) or \
               consonant_clusters or \
               (special_char_ratio > 0.3 and special_char_count > 3) or \
               repeated_patterns or \
               has_keyboard_pattern or \
               alternating_pattern or \
               single_char_repeat or \
               (random_mix and len(random_mix) > 0):  # More sensitive to number-letter patterns
                is_gibberish = True
        
        # Special check for multiple character repeats (aaabbbccc pattern)
        multi_char_repeat = re.findall(r'([a-z])\1{2,}', text_no_spaces)
        if len(multi_char_repeat) >= 2:  # At least 2 different characters repeated
            is_gibberish = True
        
        # Check for gibberish in context (e.g., "qwerty is my password" should be valid)
        # If the text contains common English words, it's probably not gibberish
        common_words = ['is', 'my', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
                       'password', 'name', 'code', 'text', 'word', 'key']
        words = response_lower.split()
        if len(words) > 2 and any(word in common_words for word in words):
            # Contains common words in context, probably not gibberish
            is_gibberish = False
        
        # Additional check: If it's mostly numbers with few letters
        digit_ratio = len(re.findall(r'\d', response_lower)) / len(response_lower) if response_lower else 0
        if digit_ratio > 0.7 and vowel_ratio < 0.1:
            is_gibberish = True
        
        if is_gibberish:
            analysis["is_gibberish"] = True
            analysis["response_type"] = "gibberish"
            analysis["requires_pattern_response"] = True
            return analysis
    
    # NEW: Greeting pattern detection - "hi", "hello", etc.
    greeting_patterns = ['hi', 'hello', 'hey', 'greetings', 'good morning', 'good afternoon', 'good evening']
    if response_lower.strip() in greeting_patterns or (len(response_lower) <= 10 and any(g in response_lower for g in greeting_patterns)):
        analysis["is_greeting"] = True
        analysis["response_type"] = "greeting"
        analysis["requires_pattern_response"] = True
        return analysis
    
    # NEW: Help-seeking pattern - "what should I do", "where is the task", etc.
    help_seeking_patterns = [
        r'what\s+(should|can|do|shall)\s+i\s+(even\s+)?do',
        r'where\s+is\s+the\s+task',
        r'where\s+(is|are)\s+the\s+(instruction|material|resource)',
        r'how\s+do\s+i\s+start',
        r'what\s+am\s+i\s+supposed\s+to\s+do',
        r'i\s+don\'?t\s+know\s+what\s+to\s+do',
        r'help\s+me\s+understand\s+the\s+task',
        r'what\s+shall\s+i\s+do'  # Added "shall" variant
    ]
    
    for pattern in help_seeking_patterns:
        if re.search(pattern, response_lower, re.IGNORECASE):
            analysis["is_help_seeking"] = True
            analysis["is_question"] = True
            analysis["response_type"] = "help_seeking"
            analysis["requires_pattern_response"] = True
            return analysis
    
    # NEW: Reassurance-seeking pattern - "how am I doing?", "how would you rate my map?", etc.
    reassurance_patterns = [
        r'how\s+am\s+i\s+doing',
        r'how\s+would\s+you\s+rate',
        r'is\s+this\s+(good|correct|right|okay|ok)',
        r'am\s+i\s+on\s+(the\s+right\s+)?track',
        r'what\s+do\s+you\s+think\s+(of\s+my|about\s+my)',
        r'how\'?s\s+my\s+(progress|map|work)',
        r'is\s+my\s+map\s+(good|okay|ok|correct)',
        r'how\s+is\s+my\s+(concept\s+)?map',
        r'what\'?s\s+your\s+(opinion|thoughts?)\s+(on|about)',
        r'do\s+you\s+think\s+(this\s+is|i\'?m)',
        r'feedback\s+on\s+my',
        r'evaluate\s+my'
    ]
    
    for pattern in reassurance_patterns:
        if re.search(pattern, response_lower, re.IGNORECASE):
            analysis["is_reassurance_seeking"] = True
            analysis["is_question"] = True
            analysis["response_type"] = "reassurance_seeking"
            analysis["requires_pattern_response"] = True
            return analysis
    
    # Pattern 1: Domain/Content Questions
    domain_indicators = ["what is", "what does", "explain", "tell me about", "how does", "why is", 
                        "amg", "market", "strategy", "concept", "international", "entry"]
    if (any(indicator in response_lower for indicator in domain_indicators) and "?" in response) or response_lower == "what?":
        analysis["is_domain_question"] = True
        analysis["is_question"] = True
        analysis["response_type"] = "question"
        analysis["requires_pattern_response"] = True  # Pattern needs handling
    
    # Pattern 1: System Questions
    system_indicators = ["how to use", "how do i", "where is", "button", "tool", "system", 
                         "interface", "click", "create", "delete", "edit", "map"]
    if any(indicator in response_lower for indicator in system_indicators) and "?" in response:
        analysis["is_system_question"] = True
        analysis["is_question"] = True
        if not analysis["is_domain_question"]:  # System takes precedence only if not domain
            analysis["response_type"] = "system_question"
    
    # Pattern 2: Disagreement Detection  
    disagreement_indicators = ["disagree", "don't agree", "not right", "wrong", "incorrect", 
                              "that's not", "i don't think so", "no!", "no,", "but i think", "however"]
    if any(indicator in response_lower for indicator in disagreement_indicators) or response_lower == "no":
        analysis["is_disagreement"] = True
        analysis["response_type"] = "disagreement"
        analysis["requires_pattern_response"] = True  # Pattern needs handling
        
        # Determine disagreement type
        if any(word in response_lower for word in ["concept", "relationship", "connection", "meaning"]):
            analysis["disagreement_type"] = "content"
        elif any(word in response_lower for word in ["approach", "method", "way", "strategy"]):
            analysis["disagreement_type"] = "approach"
        else:
            analysis["disagreement_type"] = "general"
    
    # Pattern 4: Inappropriate Language
    inappropriate_indicators = ["fuck", "shit", "stupid", "dumb", "hate", "sucks", "awful", "terrible", 
                               "waste", "useless", "pointless", "damn", "hell", "ass", "bitch", "crap"]
    if any(indicator in response_lower for indicator in inappropriate_indicators):
        analysis["is_inappropriate"] = True
        analysis["needs_encouragement"] = True
        analysis["response_type"] = "inappropriate_language"
        analysis["requires_pattern_response"] = True  # Pattern needs handling
    
    # Pattern 6: Off-topic Detection (ENHANCED)
    off_topic_indicators = ["weather", "sports", "news", "politics", "movie", "game", 
                           "lunch", "dinner", "weekend", "vacation", "something else", 
                           "different topic", "change subject", "soup", "recipe", "food", 
                           "cooking", "sauce", "ingredient"]
    concept_map_terms = ["concept", "map", "node", "edge", "relationship", "amg", "market", 
                         "strategy", "entry", "barrier", "gatekeeping", "adaptive"]
    
    # More strict off-topic detection
    off_topic_count = sum(1 for indicator in off_topic_indicators if indicator in response_lower)
    concept_count = sum(1 for term in concept_map_terms if term in response_lower)
    
    if off_topic_count > 0 and concept_count == 0:
        analysis["is_off_topic"] = True
        analysis["response_type"] = "off_topic"
        analysis["requires_pattern_response"] = True  # Pattern needs handling
    
    # Pattern 7: Frustration/Confusion
    frustration_indicators = ["frustrated", "frustrating", "annoying", "difficult", "hard", "struggling", 
                             "can't", "don't get it", "too complex", "overwhelming", "stuck"]
    if any(indicator in response_lower for indicator in frustration_indicators):
        analysis["is_frustrated"] = True
        analysis["needs_encouragement"] = True
        analysis["response_type"] = "frustration"
        analysis["requires_pattern_response"] = True  # Pattern needs handling
    
    # Pattern 8: Premature Ending
    ending_indicators = ["i'm done", "i am done", "finished", "stop", "quit", "enough", "that's all", 
                        "nothing more", "can't think", "out of ideas"]
    if any(indicator in response_lower for indicator in ending_indicators) and len(response_lower) < 50:
        analysis["wants_to_end"] = True
        analysis["response_type"] = "premature_ending"
        analysis["requires_pattern_response"] = True  # Pattern needs handling
    
    # Original confusion detection (enhanced)
    confusion_indicators = ["don't understand", "not sure", "confused", "unclear", "difficult", 
                           "hard to", "struggling", "don't know", "unsure", "lost", "help me"]
    if any(indicator in response_lower for indicator in confusion_indicators):
        analysis["is_confused"] = True
        analysis["needs_encouragement"] = True
        if analysis["response_type"] == "statement":  # Only override if not already set
            analysis["response_type"] = "confusion"
    
    # NEW: Detect intention without action (e.g., "I can add X" but didn't)
    intention_patterns = [
        r'i\s+(can|could|should|might|will)\s+add',
        r'i\s+(want|need)\s+to\s+add',
        r'maybe\s+i\s+(can|should|will)\s+add',
        r'i\s+think\s+i\s+(can|should|will)\s+add'
    ]
    
    for pattern in intention_patterns:
        if re.search(pattern, response_lower, re.IGNORECASE):
            analysis["has_intention_without_action"] = True
            # Don't override response_type yet, check for other patterns first
            
    # Pattern 5: Concrete Ideas (Critical Fix)
    # More comprehensive detection of concrete ideas
    concrete_indicators = [
        "i think", "i believe", "in my map", "i've added", "i connected", 
        "i included", "the relationship", "because", "this shows", "demonstrates",
        "my understanding", "i see", "i noticed", "i realized", "it seems",
        "amg creates", "amg blocks", "market entry", "barriers", "regulatory",
        "financing", "joint venture", "export", "strategy", "bidirectional",
        "influences", "affects", "leads to", "results in", "causes"
    ]
    
    # Check for concrete ideas with more nuanced detection
    has_concrete_content = any(indicator in response_lower for indicator in concrete_indicators)
    has_sufficient_length = len(response) > 20
    
    # Also check for specific patterns that indicate sharing ideas
    idea_patterns = [
        r'\b(amg|market|strategy|financing|export|joint\s+venture)\b.*\b(creates?|blocks?|affects?|influences?)\b',
        r'\brelationship\s+between\b.*\band\b',
        r'\b(think|believe)\b.*\b(that|because|since)\b',
        r'\b(added|included|connected)\b.*\b(node|concept|relationship)\b'
    ]
    
    matches_idea_pattern = any(re.search(pattern, response_lower, re.IGNORECASE) for pattern in idea_patterns)
    
    # Check if it's an intention with actual content (not off-topic)
    if analysis["has_intention_without_action"] and not analysis["is_off_topic"]:
        analysis["has_concrete_idea"] = True
        analysis["contains_idea"] = True
        analysis["response_type"] = "intention_without_action"
        analysis["requires_pattern_response"] = True  # Need to encourage actual action
    elif (has_concrete_content and has_sufficient_length) or matches_idea_pattern:
        analysis["has_concrete_idea"] = True
        analysis["contains_idea"] = True  # Add this field for Pattern 5 detection
        if analysis["response_type"] == "statement":  # Only override if not already set
            analysis["response_type"] = "concrete_idea"
    else:
        analysis["contains_idea"] = False  # Explicitly set to False when no idea detected
    
    # General question detection (if not already categorized)
    if "?" in response or any(q in response_lower for q in ["how", "what", "why", "when", "where", "which", "can i", "should i", "could i"]):
        analysis["is_question"] = True
        if analysis["response_type"] == "statement":
            analysis["response_type"] = "question"
    
    # Extract mentioned concepts (simple heuristic - words in quotes or capitalized)
    import re
    quoted = re.findall(r'"([^"]*)"', response)
    analysis["mentions_concepts"].extend(quoted)
    
    # Extract key phrases for context
    if "amg" in response_lower:
        analysis["key_phrases"].append("AMG")
    if "market" in response_lower:
        analysis["key_phrases"].append("market")
    if "strategy" in response_lower or "strategies" in response_lower:
        analysis["key_phrases"].append("strategy")
    if "international" in response_lower:
        analysis["key_phrases"].append("international")
    if "entry" in response_lower:
        analysis["key_phrases"].append("entry")
    
    return analysis


def select_appropriate_followup(response: str,
                               scaffolding_type: str,
                               used_followup_indices: List[int] = None) -> Tuple[str, int]:
    """
    Select an appropriate follow-up based on user response, without repetition.
    
    Args:
        response: User's response
        scaffolding_type: Type of scaffolding
        used_followup_indices: List of already used follow-up indices
        
    Returns:
        Tuple of (follow-up text, index used)
    """
    from MAS.config.scaffolding_config import SCAFFOLDING_FOLLOWUP_TEMPLATES
    
    if used_followup_indices is None:
        used_followup_indices = []
    
    # Analyze the response
    response_analysis = analyze_user_response_type(response)
    
    # Get available follow-ups
    available_followups = SCAFFOLDING_FOLLOWUP_TEMPLATES.get(scaffolding_type, [])
    
    if not available_followups:
        return "Can you elaborate on that?", -1
    
    # Filter out used follow-ups
    unused_indices = [i for i in range(len(available_followups)) if i not in used_followup_indices]
    
    if not unused_indices:
        # All follow-ups used, generate a contextual one
        return _generate_contextual_followup(response_analysis, scaffolding_type), -1
    
    # Select best follow-up based on response type
    selected_index = _select_best_followup_index(
        unused_indices,
        available_followups,
        response_analysis,
        scaffolding_type
    )
    
    return available_followups[selected_index], selected_index


def _select_best_followup_index(unused_indices: List[int],
                               available_followups: List[str],
                               response_analysis: Dict[str, Any],
                               scaffolding_type: str) -> int:
    """
    Select the best follow-up index based on response analysis.
    """
    if not unused_indices:
        return 0
    
    # Score each follow-up based on appropriateness
    scores = {}
    
    for idx in unused_indices:
        followup = available_followups[idx].lower()
        score = 0
        
        # Match follow-up to response type
        if response_analysis["has_concrete_idea"]:
            if "interesting" in followup or "elaborate" in followup:
                score += 2
            if "how" in followup or "why" in followup:
                score += 1
        
        if response_analysis["is_confused"]:
            if "help" in followup or "clarify" in followup:
                score += 2
        
        # Prefer follow-ups that build on mentioned concepts
        if response_analysis["mentions_concepts"]:
            if "that" in followup or "this" in followup:
                score += 1
        
        scores[idx] = score
    
    # Select highest scoring
    sorted_indices = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)
    return sorted_indices[0] if sorted_indices else unused_indices[0]


def _generate_contextual_followup(response_analysis: Dict[str, Any], 
                                 scaffolding_type: str) -> str:
    """
    Generate a contextual follow-up when all templates are exhausted.
    """
    if response_analysis["is_confused"]:
        if scaffolding_type == "conceptual":
            return "Let's think about this differently. What aspects of these concepts are clearest to you?"
        elif scaffolding_type == "strategic":
            return "Let's break this down. What's one small step you could take to organize these ideas?"
        elif scaffolding_type == "procedural":
            return "Let's simplify the process. What's the first thing you would do?"
        elif scaffolding_type == "metacognitive":
            return "That's okay. What parts do you feel you understand, even partially?"
    
    elif response_analysis["has_concrete_idea"]:
        if scaffolding_type == "conceptual":
            return "That's a good insight. How does this understanding affect other parts of your map?"
        elif scaffolding_type == "strategic":
            return "Good thinking. How might you apply this approach to other areas?"
        elif scaffolding_type == "procedural":
            return "That's a clear process. What would be your next step?"
        elif scaffolding_type == "metacognitive":
            return "You're developing your understanding well. What new questions does this raise?"
    
    # Generic fallback
    return "Thank you for sharing that. Let's continue developing these ideas."


def handle_domain_question(response: str, scaffolding_type: str, key_phrases: List[str] = None) -> str:
    """
    Handle domain/content questions by referencing task materials.
    Pattern 1.1: User asks content/domain questions
    
    Args:
        response: User's response
        scaffolding_type: Current scaffolding type
        key_phrases: Key phrases extracted from response
        
    Returns:
        Appropriate response for domain questions
    """
    base_response = "I see you have a question about the content. Please check the 'Task Description' and 'Extra Materials' buttons at the top of the screen for detailed information about "
    
    # Add specific guidance based on key phrases
    if key_phrases:
        if "AMG" in key_phrases or "amg" in response.lower():
            base_response += "Adaptive Market Gatekeeping and its mechanisms. "
        elif "market" in key_phrases:
            base_response += "international market entry challenges. "
        elif "strategy" in key_phrases:
            base_response += "entry strategies and approaches. "
        else:
            base_response += "the concepts you're asking about. "
    else:
        base_response += "this topic. "
    
    # Add scaffolding-specific guidance
    if scaffolding_type == "conceptual":
        base_response += "After reviewing those materials, think about how these concepts relate to each other in your map."
    elif scaffolding_type == "strategic":
        base_response += "After reviewing those materials, consider how you might organize these concepts strategically."
    elif scaffolding_type == "procedural":
        base_response += "After reviewing those materials, think about the steps to incorporate this into your map."
    elif scaffolding_type == "metacognitive":
        base_response += "After reviewing those materials, reflect on how this changes your understanding."
    
    return base_response


def handle_system_question(response: str, scaffolding_type: str) -> str:
    """
    Handle system/interface questions by directing to help.
    Pattern 1.2: User asks about concept mapping system
    
    Args:
        response: User's response
        scaffolding_type: Current scaffolding type
        
    Returns:
        Appropriate response for system questions
    """
    base_response = "For help with the concept mapping tool, please click the '❓ Help' button at the top right of the screen. It provides detailed instructions on creating nodes, edges, and organizing your map. "
    
    # Add scaffolding-specific encouragement
    if scaffolding_type == "procedural":
        base_response += "Once you're familiar with the tools, we can focus on your mapping process."
    elif scaffolding_type == "strategic":
        base_response += "Once you're comfortable with the interface, we can discuss your strategic approach."
    elif scaffolding_type == "conceptual":
        base_response += "After learning the interface, let's focus on the conceptual relationships."
    elif scaffolding_type == "metacognitive":
        base_response += "Understanding the tool will help you express your thoughts more effectively."
    
    return base_response


def handle_disagreement(response: str, scaffolding_type: str, disagreement_type: str) -> str:
    """
    Handle user disagreement based on type.
    Pattern 2: User disagreement
    
    Args:
        response: User's response
        scaffolding_type: Current scaffolding type
        disagreement_type: Type of disagreement (content/approach/general)
        
    Returns:
        Appropriate response for disagreement
    """
    if disagreement_type == "content":
        # Pattern 2.1: Content-level disagreement
        base_response = "I appreciate your perspective. Could you elaborate on why you see it differently? "
        base_response += "There's often multiple valid ways to understand these relationships. "
        
        if scaffolding_type == "conceptual":
            base_response += "What evidence or reasoning supports your view of this concept?"
        elif scaffolding_type == "strategic":
            base_response += "How does your understanding affect your organizational strategy?"
        else:
            base_response += "Let's explore your interpretation further."
            
    elif disagreement_type == "approach":
        # Pattern 2.2: Approach disagreement
        base_response = "Your approach is valid too! There's no single correct way to create a concept map. "
        base_response += "Feel free to modify or delete any nodes that don't align with your thinking. "
        
        if scaffolding_type == "strategic":
            base_response += "What alternative strategy would you prefer to use?"
        elif scaffolding_type == "procedural":
            base_response += "What process feels more natural to you?"
        else:
            base_response += "How would you like to proceed instead?"
            
    else:
        # Pattern 2.3: General disagreement
        base_response = "I understand you have a different view. Let's explore other aspects of your concept map. "
        
        if scaffolding_type == "metacognitive":
            base_response += "What parts of your map do you feel most confident about?"
        elif scaffolding_type == "conceptual":
            base_response += "Which relationships in your map feel most clear to you?"
        else:
            base_response += "What would you like to focus on next?"
    
    return base_response


def handle_empty_input(scaffolding_type: str) -> str:
    """
    Handle empty user input.
    Pattern 3: Empty user input
    
    Args:
        scaffolding_type: Current scaffolding type
        
    Returns:
        Appropriate response for empty input
    """
    responses = {
        "strategic": "I notice you haven't typed anything. If you'd like to share your thoughts about your mapping strategy, please type your response. Or if you're ready to move on, you can click 'Finish Round'.",
        "metacognitive": "It seems you haven't entered a response. Would you like to reflect on your learning process? Please type your thoughts, or click 'Finish Round' if you're ready to proceed.",
        "procedural": "You haven't typed a response yet. If you'd like to describe your mapping process, please share your thoughts. Otherwise, feel free to click 'Finish Round'.",
        "conceptual": "I see no response yet. If you have thoughts about the concepts and their relationships, please type them. Or click 'Finish Round' to continue."
    }
    
    return responses.get(scaffolding_type, "Please type your response if you'd like to continue the conversation, or click 'Finish Round' to proceed to the next round.")


def handle_inappropriate_language(scaffolding_type: str) -> str:
    """
    Handle inappropriate language with gentle reminder.
    Pattern 4: Inappropriate language
    
    Args:
        scaffolding_type: Current scaffolding type
        
    Returns:
        Appropriate response for inappropriate language
    """
    base_response = "I understand this can be challenging. Let's keep our discussion respectful and focused on improving your concept map. "
    
    # Add scaffolding-specific redirection
    if scaffolding_type == "metacognitive":
        base_response += "What aspects of the learning process are you finding most difficult?"
    elif scaffolding_type == "strategic":
        base_response += "What strategies might help you work through this challenge?"
    elif scaffolding_type == "procedural":
        base_response += "Let's break down the process into smaller, manageable steps."
    elif scaffolding_type == "conceptual":
        base_response += "Which concepts would you like to clarify first?"
    
    return base_response


def handle_off_topic(scaffolding_type: str) -> str:
    """
    Handle off-topic responses by redirecting to task.
    Pattern 6: Off-topic responses
    
    Args:
        scaffolding_type: Current scaffolding type
        
    Returns:
        Appropriate response for off-topic content
    """
    base_response = "Let's refocus on your concept map about international market entry and AMG. "
    
    # Add scaffolding-specific redirection
    if scaffolding_type == "conceptual":
        base_response += "What concepts from the task materials have you included in your map?"
    elif scaffolding_type == "strategic":
        base_response += "How are you organizing the concepts related to market entry challenges?"
    elif scaffolding_type == "procedural":
        base_response += "What's your next step in developing your concept map?"
    elif scaffolding_type == "metacognitive":
        base_response += "How is your understanding of the AMG topic developing?"
    
    return base_response


def handle_frustration(response: str, scaffolding_type: str) -> str:
    """
    Handle learning frustration with encouragement.
    Pattern 7: Learning process confusion/frustration
    
    Args:
        response: User's response
        scaffolding_type: Current scaffolding type
        
    Returns:
        Encouraging response for frustration
    """
    base_response = "I understand this can feel overwhelming. Concept mapping is an iterative process - it's perfectly normal to feel challenged. "
    base_response += "Remember, there's no perfect map, just your evolving understanding. "
    
    # Add scaffolding-specific encouragement
    if scaffolding_type == "metacognitive":
        base_response += "You're doing well by reflecting on your learning. What small insight have you gained so far?"
    elif scaffolding_type == "strategic":
        base_response += "Let's simplify your strategy. What's one connection you feel confident about?"
    elif scaffolding_type == "procedural":
        base_response += "Let's take it step by step. What's one thing you can add or modify right now?"
    elif scaffolding_type == "conceptual":
        base_response += "Start with what you know. Which concept feels clearest to you?"
    
    return base_response


def handle_premature_ending(scaffolding_type: str) -> str:
    """
    Handle premature session ending attempts.
    Pattern 8: Premature session ending
    
    Args:
        scaffolding_type: Current scaffolding type
        
    Returns:
        Encouraging response to continue
    """
    base_response = "I see you might want to finish, but your contribution is valuable for this research. "
    base_response += "Completing all rounds helps us understand how learners develop concept maps. "
    base_response += "You're making good progress! "
    
    # Add scaffolding-specific encouragement
    if scaffolding_type == "metacognitive":
        base_response += "Even small reflections about your learning are helpful. What's one thing you've noticed?"
    elif scaffolding_type == "strategic":
        base_response += "Your mapping strategy, even if simple, provides valuable insights. Can you share one approach you've used?"
    elif scaffolding_type == "procedural":
        base_response += "Every step you take in building your map matters. What's been your process so far?"
    elif scaffolding_type == "conceptual":
        base_response += "Any connections you've made between concepts are worth exploring. Which relationship seems most important?"
    
    return base_response


def handle_greeting(scaffolding_type: str) -> str:
    """
    Handle greeting inputs like "hi", "hello", etc.
    NEW Pattern: Greeting
    
    Args:
        scaffolding_type: Current scaffolding type
        
    Returns:
        Appropriate response for greeting
    """
    base_response = "Hello! Let's focus on your concept map about AMG and international market entry. "
    
    # Add scaffolding-specific guidance
    if scaffolding_type == "conceptual":
        base_response += "What concepts have you included so far, and how do they relate to each other?"
    elif scaffolding_type == "procedural":
        base_response += "What's your next step in building your concept map?"
    elif scaffolding_type == "strategic":
        base_response += "How are you organizing your concepts to show the relationships between AMG and market entry?"
    elif scaffolding_type == "metacognitive":
        base_response += "How is your understanding of the AMG topic developing as you work on your map?"
    
    return base_response


def handle_minimal_input(scaffolding_type: str) -> str:
    """
    Handle minimal/single character input like "e", "eh", "a", etc.
    NEW Pattern: Minimal input
    
    Args:
        scaffolding_type: Current scaffolding type
        
    Returns:
        Appropriate response for minimal input
    """
    base_response = "I need more information to understand your response. Please provide a more detailed answer about "
    
    # Add scaffolding-specific prompts
    if scaffolding_type == "conceptual":
        base_response += "the concepts and relationships in your map. What specific ideas are you working with?"
    elif scaffolding_type == "procedural":
        base_response += "your mapping process. Can you describe what steps you're taking?"
    elif scaffolding_type == "strategic":
        base_response += "your organizational strategy. How are you structuring your concept map?"
    elif scaffolding_type == "metacognitive":
        base_response += "your learning experience. What are you understanding or finding challenging?"
    
    return base_response


def handle_help_seeking(response: str, scaffolding_type: str) -> str:
    """
    Handle help-seeking questions like "what should I do?" or "where is the task?"
    NEW Pattern: Help-seeking
    
    Args:
        response: User's response
        scaffolding_type: Current scaffolding type
        
    Returns:
        Appropriate response directing to resources
    """
    base_response = "I see you need guidance on getting started. Please check the 'Task Description' button at the top of the screen for detailed information about the AMG concept mapping task. "
    base_response += "The 'Extra Materials' button provides additional resources about international market entry and AMG mechanisms. "
    
    # Add scaffolding-specific guidance
    if scaffolding_type == "conceptual":
        base_response += "Start by adding key concepts from the materials, like 'AMG', 'market entry barriers', and 'gatekeeping mechanisms'."
    elif scaffolding_type == "procedural":
        base_response += "Begin by clicking to add nodes for main concepts, then connect them with labeled relationships."
    elif scaffolding_type == "strategic":
        base_response += "Consider organizing your map with AMG at the center and its effects branching outward."
    elif scaffolding_type == "metacognitive":
        base_response += "Think about what you already know about market entry and build from there."
    
    return base_response


def handle_gibberish(scaffolding_type: str) -> str:
    """
    Handle gibberish or random text input.
    NEW Pattern: Gibberish
    
    Args:
        scaffolding_type: Current scaffolding type
        
    Returns:
        Appropriate response for gibberish input
    """
    base_response = "I didn't quite understand that. Let's refocus on your concept map. "
    
    # Add scaffolding-specific redirection
    if scaffolding_type == "conceptual":
        base_response += "What concepts from the AMG materials would you like to explore?"
    elif scaffolding_type == "procedural":
        base_response += "What's your next step in building your concept map?"
    elif scaffolding_type == "strategic":
        base_response += "How are you planning to organize your AMG concepts?"
    elif scaffolding_type == "metacognitive":
        base_response += "What aspects of AMG are you finding clear or confusing?"
    
    return base_response


def handle_intention_without_action(response: str, scaffolding_type: str) -> str:
    """
    Handle when user says they'll add something but doesn't actually do it.
    NEW Pattern: Intention without action
    
    Args:
        response: User's response
        scaffolding_type: Current scaffolding type
        
    Returns:
        Encouraging response to take action
    """
    # Extract what they mentioned adding (simple extraction)
    import re
    match = re.search(r'add\s+(.+?)(?:\.|$)', response.lower())
    concept_mentioned = match.group(1) if match else "that concept"
    
    base_response = f"Good idea to add {concept_mentioned}! "
    base_response += "Go ahead and add it to your concept map now - click to create a new node and label it. "
    
    # Add scaffolding-specific encouragement
    if scaffolding_type == "conceptual":
        base_response += "Once you've added it, think about how it relates to your existing concepts."
    elif scaffolding_type == "procedural":
        base_response += "After adding the node, you can create edges to show its relationships."
    elif scaffolding_type == "strategic":
        base_response += "Consider where to position it strategically in relation to other concepts."
    elif scaffolding_type == "metacognitive":
        base_response += "Adding it will help solidify your understanding of how it fits in the bigger picture."
    
    return base_response


def handle_reassurance_seeking(response: str, concept_map: Optional[Dict[str, Any]] = None, expert_map: Optional[Dict[str, Any]] = None) -> str:
    """
    Handle reassurance-seeking questions with context-aware progress feedback.
    NEW Pattern: Reassurance-seeking
    
    Args:
        response: User's response
        concept_map: Current concept map data
        expert_map: Expert concept map for comparison
        
    Returns:
        Context-aware reassurance response
    """
    # Extract map information
    node_count = 0
    edge_count = 0
    concept_labels = []
    
    if concept_map:
        concepts = concept_map.get("concepts", [])
        relationships = concept_map.get("relationships", [])
        node_count = len(concepts)
        edge_count = len(relationships)
        
        # Get concept labels for context
        for c in concepts[:3]:  # First 3 concepts
            label = c.get('text', c.get('label', c.get('id', 'concept')))
            # Avoid showing UUIDs
            if '-' not in label or len(label) < 30:
                concept_labels.append(label)
    
    # Compare to expert expectations (typical AMG maps have 5-8 concepts)
    if node_count >= 6:
        progress_assessment = "making excellent progress"
    elif node_count >= 4:
        progress_assessment = "developing well"
    elif node_count >= 2:
        progress_assessment = "getting started nicely"
    else:
        progress_assessment = "beginning to explore the topic"
    
    # Build context-aware response
    if concept_labels:
        if len(concept_labels) == 1:
            concept_context = f"concepts like '{concept_labels[0]}'"
        elif len(concept_labels) == 2:
            concept_context = f"concepts like '{concept_labels[0]}' and '{concept_labels[1]}'"
        else:
            concept_context = f"concepts like '{concept_labels[0]}', '{concept_labels[1]}', and '{concept_labels[2]}'"
    else:
        concept_context = "your concept map"
    
    # Generate response based on progress
    if node_count >= 4:
        base_response = f"Your map has {node_count} concepts and {edge_count} connections, showing you're {progress_assessment} with the AMG task. "
        base_response += f"You've included important {concept_context} - there's always room to discover new connections by examining how AMG mechanisms interact with these concepts."
    elif node_count >= 2:
        base_response = f"With {node_count} concepts including {concept_context}, you're {progress_assessment}. "
        base_response += "You can feel free to think outside the given examples and add your own observations about how AMG influences market entry."
    else:
        base_response = f"You're {progress_assessment} - concept maps typically develop with 5-8 key concepts. "
        base_response += "There are always new relationships to discover when you examine how AMG aspects interact with different market entry factors."
    
    return base_response


def generate_concrete_idea_followup(response: str, scaffolding_type: str, mentions_concepts: List[str] = None) -> str:
    """
    Generate appropriate follow-up for concrete ideas (Pattern 5 fix).
    Only use affirmative responses when user actually shares ideas.
    
    Args:
        response: User's response
        scaffolding_type: Current scaffolding type
        mentions_concepts: Concepts mentioned by user
        
    Returns:
        Action-oriented follow-up
    """
    # Pattern 5.2 & 5.3: Ask if map reflects ideas and suggest additions
    base_response = ""
    
    if mentions_concepts and len(mentions_concepts) > 0:
        base_response = f"You've mentioned interesting ideas about {', '.join(mentions_concepts[:2])}. "
    else:
        base_response = "You've shared some valuable insights. "
    
    base_response += "Does your current concept map reflect these ideas? "
    
    # Add scaffolding-specific call to action
    if scaffolding_type == "conceptual":
        base_response += "Consider adding these concepts as new nodes or strengthening the relationships that represent these ideas."
    elif scaffolding_type == "strategic":
        base_response += "You might reorganize your map to better highlight these strategic insights you've identified."
    elif scaffolding_type == "procedural":
        base_response += "Try implementing this process you've described by adding or modifying the relevant connections."
    elif scaffolding_type == "metacognitive":
        base_response += "Based on this reflection, what changes would better represent your evolved understanding?"
    
    return base_response


def _generate_context_aware_prompts(scaffolding_type: str,
                                   scaffolding_intensity: str,
                                   analysis: Dict[str, Any],
                                   enhanced_concept_map: Dict[str, Any],
                                   used_template_indices: Optional[List[int]] = None) -> List[str]:
    """
    Generate context-aware prompts using resolved concept labels.
    
    Args:
        scaffolding_type: Type of scaffolding
        scaffolding_intensity: Intensity of scaffolding
        analysis: Concept map analysis
        enhanced_concept_map: Enhanced concept map with resolved labels
        
    Returns:
        List of context-aware scaffolding prompts
    """
    prompts = []
    
    # Get relationships with resolved labels
    relationships = enhanced_concept_map.get("relationships", enhanced_concept_map.get("edges", []))
    
    # Get concepts with labels
    concepts = enhanced_concept_map.get("concepts", enhanced_concept_map.get("nodes", []))
    
    # Build a list of concept labels for reference
    concept_labels = []
    for concept in concepts:
        if isinstance(concept, dict):
            label = concept.get("label", concept.get("text", concept.get("id", "")))
            if label:
                concept_labels.append(label)
        elif isinstance(concept, str):
            concept_labels.append(concept)
    
    if scaffolding_type == "conceptual":
        # Generate conceptual prompts with actual concept names
        if scaffolding_intensity == "high":
            if relationships:
                # Pick a specific relationship to discuss
                rel = relationships[0]
                source_text = rel.get("source_text", rel.get("source_label", rel.get("source", "")))
                target_text = rel.get("target_text", rel.get("target_label", rel.get("target", "")))
                rel_text = rel.get("text", rel.get("relation", "relates to"))
                
                prompts.append(
                    f"You've indicated that '{source_text}' {rel_text} '{target_text}'. "
                    f"Can you elaborate on this relationship and explain why it's important?"
                )
            
            if len(concept_labels) > 2:
                prompts.append(
                    f"How do concepts like '{concept_labels[0]}' and '{concept_labels[1]}' "
                    f"relate to the overall theme of your concept map?"
                )
            
            prompts.append(
                "Are there any additional concepts or relationships you're considering adding? "
                "What would they contribute to your understanding?"
            )
        
        elif scaffolding_intensity == "medium":
            if concept_labels:
                central_concept = concept_labels[0] if concept_labels else "your main concept"
                prompts.append(
                    f"What makes '{central_concept}' a key concept in your map?"
                )
            
            prompts.append(
                "How do the relationships you've identified help explain the topic?"
            )
        
        else:  # low
            prompts.append(
                "What is the main idea that connects all the concepts in your map?"
            )
    
    elif scaffolding_type == "strategic":
        if scaffolding_intensity == "high":
            if concept_labels:
                prompts.append(
                    f"How did you decide to position concepts like '{concept_labels[0]}' "
                    f"in relation to other concepts?"
                )
            
            prompts.append(
                "What organizing principle did you use to structure your concept map?"
            )
            
            if relationships:
                prompts.append(
                    "How did you determine which relationships were most important to include?"
                )
        
        elif scaffolding_intensity == "medium":
            prompts.append(
                "What was your strategy for organizing these concepts?"
            )
            
            if len(relationships) > 0:
                prompts.append(
                    f"You've identified {len(relationships)} relationships. "
                    f"How did you decide which connections to make?"
                )
        
        else:  # low
            prompts.append(
                "What approach did you take to create this concept map?"
            )
    
    elif scaffolding_type == "metacognitive":
        if scaffolding_intensity == "high":
            if concept_labels:
                prompts.append(
                    f"How confident are you about your understanding of concepts like "
                    f"'{concept_labels[0]}' and their relationships?"
                )
            
            prompts.append(
                "Which parts of your concept map do you feel need more development?"
            )
            
            prompts.append(
                "How has creating this map changed your understanding of the topic?"
            )
        
        elif scaffolding_intensity == "medium":
            prompts.append(
                "What have you learned from creating this concept map?"
            )
            
            if concept_labels:
                prompts.append(
                    f"Which concepts (like '{concept_labels[0]}') do you feel you understand well?"
                )
        
        else:  # low
            prompts.append(
                "How do you feel about your current understanding of this topic?"
            )
    
    elif scaffolding_type == "procedural":
        if scaffolding_intensity == "high":
            prompts.append(
                "What was your step-by-step process for creating this concept map?"
            )
            
            if relationships:
                rel = relationships[0]
                source_text = rel.get("source_text", rel.get("source_label", "one concept"))
                target_text = rel.get("target_text", rel.get("target_label", "another concept"))
                prompts.append(
                    f"How did you identify the relationship between '{source_text}' and '{target_text}'?"
                )
            
            prompts.append(
                "What techniques did you use to organize your concepts spatially?"
            )
        
        elif scaffolding_intensity == "medium":
            prompts.append(
                "What process did you follow to build your concept map?"
            )
            
            if len(concepts) > 0:
                prompts.append(
                    f"How did you decide to include these {len(concepts)} concepts?"
                )
        
        else:  # low
            prompts.append(
                "Can you describe your process for creating this concept map?"
            )
    
    # If we couldn't generate enough context-aware prompts, add some defaults
    if len(prompts) < 2:
        if scaffolding_type == "conceptual":
            prompts.append("How do the concepts in your map relate to each other?")
        elif scaffolding_type == "strategic":
            prompts.append("What was your strategy for organizing these concepts?")
        elif scaffolding_type == "metacognitive":
            prompts.append("What aspects of this topic do you understand well?")
        elif scaffolding_type == "procedural":
            prompts.append("What steps did you take to create your map?")
    
    return prompts
