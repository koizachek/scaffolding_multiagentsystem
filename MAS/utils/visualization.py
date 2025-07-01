"""
Visualization Utilities

This module provides utility functions for visualizing concept maps.
"""

import logging
import os
import matplotlib.pyplot as plt
import networkx as nx
from typing import Dict, Any

logger = logging.getLogger(__name__)

def plot_concept_map(concept_map: Dict[str, Any], output_path: str) -> None:
    """
    Plot a concept map.
    
    Args:
        concept_map: Concept map data
        output_path: Path to save the plot
    """
    logger.info(f"Plotting concept map to {output_path}")
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Extract concepts and relationships
    concepts = concept_map.get("concepts", [])
    relationships = concept_map.get("relationships", [])
    
    # Create graph
    G = nx.DiGraph()
    
    # Add nodes
    for concept in concepts:
        concept_id = concept.get("id")
        concept_text = concept.get("text")
        G.add_node(concept_id, label=concept_text)
    
    # Add edges
    for relationship in relationships:
        source = relationship.get("source")
        target = relationship.get("target")
        relationship_text = relationship.get("text", "")
        G.add_edge(source, target, label=relationship_text)
    
    # Create positions
    pos = {}
    for concept in concepts:
        concept_id = concept.get("id")
        x = concept.get("x", 0) / 100  # Scale down for better visualization
        y = concept.get("y", 0) / 100  # Scale down for better visualization
        pos[concept_id] = (x, y)
    
    # Create figure
    plt.figure(figsize=(12, 8))
    
    # Draw nodes
    nx.draw_networkx_nodes(G, pos, node_size=2000, node_color="lightblue", alpha=0.8)
    
    # Draw edges
    nx.draw_networkx_edges(G, pos, width=1.0, alpha=0.5, arrowsize=20)
    
    # Draw node labels
    nx.draw_networkx_labels(G, pos, labels=nx.get_node_attributes(G, "label"), font_size=10)
    
    # Draw edge labels
    edge_labels = nx.get_edge_attributes(G, "label")
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)
    
    # Set title
    plt.title("Concept Map")
    
    # Remove axis
    plt.axis("off")
    
    # Save figure
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    
    # Close figure
    plt.close()
    
    logger.info(f"Concept map plotted to {output_path}")
