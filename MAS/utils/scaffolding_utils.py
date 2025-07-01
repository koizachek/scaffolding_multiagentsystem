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
                            analysis: Optional[Dict[str, Any]] = None) -> List[str]:
    """
    Generate default scaffolding prompts.
    
    Args:
        scaffolding_type: Type of scaffolding
        scaffolding_intensity: Intensity of scaffolding
        analysis: Concept map analysis (optional)
        
    Returns:
        List of default scaffolding prompts
    """
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
