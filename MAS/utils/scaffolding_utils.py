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
    Analyze whether user response is a question or statement, and extract key information.
    
    Args:
        response: User's response text
        
    Returns:
        Dictionary with response analysis
    """
    analysis = {
        "is_question": False,
        "is_confused": False,
        "has_concrete_idea": False,
        "mentions_concepts": [],
        "response_type": "statement",
        "key_phrases": []
    }
    
    response_lower = response.lower()
    
    # Check if it's a question
    if "?" in response or any(q in response_lower for q in ["how", "what", "why", "when", "where", "which", "can i", "should i", "could i"]):
        analysis["is_question"] = True
        analysis["response_type"] = "question"
    
    # Check for confusion indicators
    confusion_indicators = ["don't understand", "not sure", "confused", "unclear", "difficult", "hard to", "struggling", "don't know", "unsure"]
    if any(indicator in response_lower for indicator in confusion_indicators):
        analysis["is_confused"] = True
        analysis["response_type"] = "confusion"
    
    # Check for concrete ideas
    concrete_indicators = ["i think", "i believe", "in my map", "i've added", "i connected", "i included", "the relationship", "because", "this shows", "demonstrates"]
    if any(indicator in response_lower for indicator in concrete_indicators):
        analysis["has_concrete_idea"] = True
        analysis["response_type"] = "concrete_idea"
    
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
