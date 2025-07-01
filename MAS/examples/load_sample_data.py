"""
Load Sample Data Example

This script demonstrates how to load and use the sample data files.
"""

import json
import os
import sys
from pathlib import Path

# Add the parent directory to the Python path to import the MAS package
sys.path.append(str(Path(__file__).parent.parent))

from utils.visualization import plot_concept_map

def load_json_file(file_path):
    """
    Load a JSON file.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Loaded JSON data
    """
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    return data

def main():
    """
    Main function for the load sample data example.
    """
    print("Multi-Agent Scaffolding System - Load Sample Data Example")
    
    # Get the path to the data directory
    data_dir = Path(__file__).parent / "data"
    
    # Load sample concept map
    concept_map_path = data_dir / "sample_concept_map.json"
    concept_map = load_json_file(concept_map_path)
    
    print("\nSample Concept Map:")
    print(f"Nodes: {len(concept_map['nodes'])}")
    print(f"Edges: {len(concept_map['edges'])}")
    print("\nNodes:")
    for node in concept_map['nodes']:
        print(f"  - {node}")
    print("\nEdges:")
    for edge in concept_map['edges']:
        print(f"  - {edge['source']} {edge['relation']} {edge['target']}")
    
    # Load expert concept map
    expert_map_path = data_dir / "expert_concept_map.json"
    expert_map = load_json_file(expert_map_path)
    
    print("\nExpert Concept Map:")
    print(f"Nodes: {len(expert_map['nodes'])}")
    print(f"Edges: {len(expert_map['edges'])}")
    
    # Load learner profile
    profile_path = data_dir / "learner_profile.json"
    profile = load_json_file(profile_path)
    
    print("\nLearner Profile:")
    print(f"ID: {profile['id']}")
    print(f"Name: {profile['name']}")
    print(f"Background: {profile['background']}")
    print("\nResponses:")
    for key, value in profile['responses'].items():
        print(f"  {key.replace('_', ' ').title()}: {value}")
    
    # Create output directory
    output_dir = Path(__file__).parent / "output" / "sample_data"
    os.makedirs(output_dir, exist_ok=True)
    
    # Plot concept maps
    sample_plot_path = output_dir / "sample_concept_map.png"
    plot_concept_map(concept_map, sample_plot_path)
    
    expert_plot_path = output_dir / "expert_concept_map.png"
    plot_concept_map(expert_map, expert_plot_path)
    
    print("\nPlotted concept maps:")
    print(f"  Sample: {sample_plot_path}")
    print(f"  Expert: {expert_plot_path}")
    
    # Compare concept maps
    sample_nodes = set(concept_map['nodes'])
    expert_nodes = set(expert_map['nodes'])
    
    # Convert edges to comparable format
    sample_edges = {(edge["source"], edge["target"], edge.get("relation", "")) 
                   for edge in concept_map['edges']}
    expert_edges = {(edge["source"], edge["target"], edge.get("relation", "")) 
                   for edge in expert_map['edges']}
    
    # Calculate coverage
    node_coverage = len(sample_nodes & expert_nodes) / len(expert_nodes)
    edge_coverage = len(sample_edges & expert_edges) / len(expert_edges)
    
    print("\nConcept Map Comparison:")
    print(f"Node coverage: {node_coverage:.2%}")
    print(f"Edge coverage: {edge_coverage:.2%}")
    
    # Find missing concepts
    missing_nodes = expert_nodes - sample_nodes
    print("\nMissing concepts:")
    for node in missing_nodes:
        print(f"  - {node}")
    
    # Find missing relationships
    missing_edges = expert_edges - sample_edges
    print("\nMissing relationships:")
    for edge in missing_edges:
        print(f"  - {edge[0]} {edge[2]} {edge[1]}")
    
    print("\nSample data loaded and analyzed successfully.")

if __name__ == "__main__":
    main()
