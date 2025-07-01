"""
Batch Processing Example

This script demonstrates how to process multiple concept maps in a batch.
"""

import json
import os
import sys
from pathlib import Path
import time

# Add the parent directory to the Python path to import the MAS package
sys.path.append(str(Path(__file__).parent.parent))

from system import MultiAgentScaffoldingSystem
from utils.visualization import plot_concept_map

# Sample concept maps for batch processing
SAMPLE_CONCEPT_MAPS = [
    {
        "name": "map1",
        "topic": "Climate Change - Basic",
        "data": {
            "nodes": [
                "Climate Change",
                "Global Warming",
                "Carbon Emissions",
                "Fossil Fuels"
            ],
            "edges": [
                {"source": "Fossil Fuels", "target": "Carbon Emissions", "relation": "produces"},
                {"source": "Carbon Emissions", "target": "Global Warming", "relation": "causes"},
                {"source": "Global Warming", "target": "Climate Change", "relation": "leads to"}
            ]
        }
    },
    {
        "name": "map2",
        "topic": "Climate Change - Intermediate",
        "data": {
            "nodes": [
                "Climate Change",
                "Global Warming",
                "Carbon Emissions",
                "Fossil Fuels",
                "Renewable Energy",
                "Greenhouse Effect",
                "Sea Level Rise"
            ],
            "edges": [
                {"source": "Fossil Fuels", "target": "Carbon Emissions", "relation": "produces"},
                {"source": "Carbon Emissions", "target": "Greenhouse Effect", "relation": "enhances"},
                {"source": "Greenhouse Effect", "target": "Global Warming", "relation": "causes"},
                {"source": "Global Warming", "target": "Climate Change", "relation": "is part of"},
                {"source": "Climate Change", "target": "Sea Level Rise", "relation": "causes"},
                {"source": "Renewable Energy", "target": "Carbon Emissions", "relation": "reduces"}
            ]
        }
    },
    {
        "name": "map3",
        "topic": "Climate Change - Advanced",
        "data": {
            "nodes": [
                "Climate Change",
                "Global Warming",
                "Carbon Emissions",
                "Fossil Fuels",
                "Renewable Energy",
                "Greenhouse Effect",
                "Sea Level Rise",
                "Extreme Weather",
                "Deforestation",
                "Ocean Acidification",
                "Biodiversity Loss"
            ],
            "edges": [
                {"source": "Fossil Fuels", "target": "Carbon Emissions", "relation": "produces"},
                {"source": "Carbon Emissions", "target": "Greenhouse Effect", "relation": "enhances"},
                {"source": "Greenhouse Effect", "target": "Global Warming", "relation": "causes"},
                {"source": "Global Warming", "target": "Climate Change", "relation": "is part of"},
                {"source": "Climate Change", "target": "Sea Level Rise", "relation": "causes"},
                {"source": "Climate Change", "target": "Extreme Weather", "relation": "increases"},
                {"source": "Climate Change", "target": "Ocean Acidification", "relation": "leads to"},
                {"source": "Deforestation", "target": "Carbon Emissions", "relation": "increases"},
                {"source": "Deforestation", "target": "Biodiversity Loss", "relation": "causes"},
                {"source": "Ocean Acidification", "target": "Biodiversity Loss", "relation": "contributes to"},
                {"source": "Renewable Energy", "target": "Carbon Emissions", "relation": "reduces"}
            ]
        }
    }
]

# Expert concept map for comparison
EXPERT_CONCEPT_MAP = {
    "nodes": [
        "Climate Change",
        "Global Warming",
        "Carbon Emissions",
        "Fossil Fuels",
        "Renewable Energy",
        "Greenhouse Effect",
        "Sea Level Rise",
        "Extreme Weather",
        "Deforestation",
        "Ocean Acidification",
        "Biodiversity Loss",
        "Carbon Sequestration",
        "Methane",
        "Permafrost Melting",
        "Feedback Loops",
        "Policy Interventions",
        "Climate Justice"
    ],
    "edges": [
        {"source": "Fossil Fuels", "target": "Carbon Emissions", "relation": "produces"},
        {"source": "Carbon Emissions", "target": "Greenhouse Effect", "relation": "enhances"},
        {"source": "Greenhouse Effect", "target": "Global Warming", "relation": "causes"},
        {"source": "Global Warming", "target": "Climate Change", "relation": "is part of"},
        {"source": "Climate Change", "target": "Sea Level Rise", "relation": "causes"},
        {"source": "Climate Change", "target": "Extreme Weather", "relation": "increases frequency of"},
        {"source": "Climate Change", "target": "Ocean Acidification", "relation": "leads to"},
        {"source": "Deforestation", "target": "Carbon Emissions", "relation": "increases"},
        {"source": "Deforestation", "target": "Biodiversity Loss", "relation": "causes"},
        {"source": "Ocean Acidification", "target": "Biodiversity Loss", "relation": "contributes to"},
        {"source": "Renewable Energy", "target": "Carbon Emissions", "relation": "reduces"},
        {"source": "Carbon Sequestration", "target": "Carbon Emissions", "relation": "reduces"},
        {"source": "Methane", "target": "Greenhouse Effect", "relation": "contributes to"},
        {"source": "Permafrost Melting", "target": "Methane", "relation": "releases"},
        {"source": "Global Warming", "target": "Permafrost Melting", "relation": "causes"},
        {"source": "Permafrost Melting", "target": "Feedback Loops", "relation": "creates"},
        {"source": "Feedback Loops", "target": "Climate Change", "relation": "accelerates"},
        {"source": "Policy Interventions", "target": "Carbon Emissions", "relation": "regulates"},
        {"source": "Climate Justice", "target": "Policy Interventions", "relation": "informs"}
    ]
}

def create_sample_config():
    """
    Create a sample configuration for the batch processing.
    
    Returns:
        Sample configuration
    """
    config = {
        "max_rounds": 1,  # Only one round per map in batch processing
        "agents": {
            "lead": {
                "type": "lead",
                "name": "Lead Agent",
                "enabled": True
            },
            "learner_profiling": {
                "type": "learner_profiling",
                "name": "Learner Profiling Agent",
                "enabled": True
            },
            "strategic_scaffolding": {
                "type": "strategic_scaffolding",
                "name": "Strategic Scaffolding Agent",
                "enabled": True
            },
            "conceptual_scaffolding": {
                "type": "conceptual_scaffolding",
                "name": "Conceptual Scaffolding Agent",
                "enabled": True
            },
            "metacognitive_scaffolding": {
                "type": "metacognitive_scaffolding",
                "name": "Metacognitive Scaffolding Agent",
                "enabled": True
            },
            "procedural_scaffolding": {
                "type": "procedural_scaffolding",
                "name": "Procedural Scaffolding Agent",
                "enabled": True
            },
            "example_map": {
                "type": "example_map",
                "name": "Example Map Agent",
                "enabled": True
            },
            "content_ingestion": {
                "type": "content_ingestion",
                "name": "Content Ingestion Agent",
                "enabled": True
            }
        },
        "design_features": {
            "df1_learner_profiling": True,
            "df2_scaffolding": True,
            "df3_example_map": True,
            "df4_content_ingestion": True
        },
        "logging": {
            "log_dir": "logs",
            "log_level": "INFO"
        },
        "output_dir": "output"
    }
    
    return config

def process_concept_map(system, concept_map, output_dir):
    """
    Process a concept map with the multi-agent scaffolding system.
    
    Args:
        system: The multi-agent scaffolding system
        concept_map: Concept map data
        output_dir: Output directory
        
    Returns:
        Processing result
    """
    # Save concept map as JSON
    json_path = os.path.join(output_dir, f"{concept_map['name']}.json")
    with open(json_path, 'w') as f:
        json.dump(concept_map['data'], f, indent=2)
    
    # Plot concept map
    plot_path = os.path.join(output_dir, f"{concept_map['name']}.png")
    plot_concept_map(concept_map['data'], plot_path)
    
    print(f"Processing concept map: {concept_map['name']} - {concept_map['topic']}")
    print(f"Nodes: {len(concept_map['data']['nodes'])}, Edges: {len(concept_map['data']['edges'])}")
    
    # Reset session state for new concept map
    system.session_state["current_round"] = 0
    system.session_state["previous_concept_maps"] = []
    
    # Directly update system's session state with the concept map
    system.session_state["current_concept_map"] = concept_map['data']
    
    # Create input data for agents
    input_data = {
        "type": "concept_map_submission",
        "concept_map_data": concept_map['data'],
        "pdf_path": json_path,  # Using JSON path as a stand-in for PDF path
        "round": system.session_state["current_round"],
        "topic": concept_map['topic']
    }
    
    # Process with lead agent
    context = {"session_state": system.session_state}
    result = system.lead_agent.process(input_data, context)
    
    # Update session state
    if "session_state_updates" in result:
        system.session_state.update(result["session_state_updates"])
    
    # Save agent responses
    responses_path = os.path.join(output_dir, f"{concept_map['name']}_responses.json")
    with open(responses_path, 'w') as f:
        json.dump(result.get("agent_responses", {}), f, indent=2)
    
    # Save summary text file
    summary_path = os.path.join(output_dir, f"{concept_map['name']}_summary.txt")
    with open(summary_path, 'w') as f:
        f.write(f"Concept Map: {concept_map['name']} - {concept_map['topic']}\n")
        f.write(f"Nodes: {len(concept_map['data']['nodes'])}, Edges: {len(concept_map['data']['edges'])}\n\n")
        
        f.write("Agent Feedback:\n\n")
        
        responses = result.get("agent_responses", {})
        for agent_type, response in responses.items():
            if response:
                f.write(f"[{agent_type.replace('_', ' ').title()}]\n\n")
                f.write(response)
                f.write("\n\n" + "-" * 80 + "\n\n")
    
    print(f"Processed concept map: {concept_map['name']}")
    print(f"Results saved to {output_dir}")
    
    return result

def main():
    """
    Main function for the batch processing example.
    """
    print("Multi-Agent Scaffolding System - Batch Processing Example")
    
    # Create output directory
    output_dir = "examples/output/batch_processing"
    os.makedirs(output_dir, exist_ok=True)
    
    # Create and save sample configuration
    config = create_sample_config()
    config["output_dir"] = output_dir
    
    config_path = os.path.join(output_dir, "config.json")
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"Created sample configuration at {config_path}")
    
    # Initialize system
    system = MultiAgentScaffoldingSystem(config_path)
    print("Initialized multi-agent scaffolding system")
    
    # Set expert concept map for the example map agent
    for agent_id, agent in system.agents.items():
        if agent.agent_type == "example_map":
            agent.set_example_map(EXPERT_CONCEPT_MAP)
            print("Set expert concept map for comparison")
    
    # Simulate learner profile input
    learner_responses = {
        "prior_knowledge": "I have a basic understanding of climate change from high school science classes.",
        "experience": "I've read some news articles about climate change but haven't studied it formally.",
        "goals": "I want to understand the causes and effects of climate change more deeply.",
        "confidence": "I'm somewhat confident in my understanding of the basic concepts.",
        "interests": "I'm particularly interested in solutions to climate change and renewable energy."
    }
    
    print("Collecting learner profile information...")
    
    # Create input data for agents
    input_data = {
        "type": "learner_profile",
        "learner_responses": learner_responses
    }
    
    # Process with lead agent
    context = {"session_state": system.session_state}
    result = system.lead_agent.process(input_data, context)
    
    # Update session state
    if "session_state_updates" in result:
        system.session_state.update(result["session_state_updates"])
    
    print("Learner profile collected and ZPD estimated.")
    
    # Process each concept map
    results = []
    for concept_map in SAMPLE_CONCEPT_MAPS:
        # Create map-specific output directory
        map_output_dir = os.path.join(output_dir, concept_map["name"])
        os.makedirs(map_output_dir, exist_ok=True)
        
        # Process concept map
        result = process_concept_map(system, concept_map, map_output_dir)
        results.append(result)
        
        # Add a small delay between maps
        time.sleep(1)
    
    # Generate comparative analysis
    print("\nGenerating comparative analysis...")
    
    analysis = {
        "maps": [],
        "comparison": {}
    }
    
    for i, concept_map in enumerate(SAMPLE_CONCEPT_MAPS):
        map_data = {
            "name": concept_map["name"],
            "topic": concept_map["topic"],
            "node_count": len(concept_map["data"]["nodes"]),
            "edge_count": len(concept_map["data"]["edges"]),
            "coverage": {
                "nodes": len(concept_map["data"]["nodes"]) / len(EXPERT_CONCEPT_MAP["nodes"]),
                "edges": len(concept_map["data"]["edges"]) / len(EXPERT_CONCEPT_MAP["edges"])
            }
        }
        
        analysis["maps"].append(map_data)
    
    # Save comparative analysis
    analysis_path = os.path.join(output_dir, "comparative_analysis.json")
    with open(analysis_path, 'w') as f:
        json.dump(analysis, f, indent=2)
    
    # Generate summary report
    report_path = os.path.join(output_dir, "batch_summary_report.txt")
    with open(report_path, 'w') as f:
        f.write("Multi-Agent Scaffolding System - Batch Processing Summary Report\n")
        f.write("=" * 80 + "\n\n")
        
        f.write("Processed Concept Maps:\n\n")
        
        for map_data in analysis["maps"]:
            f.write(f"- {map_data['name']} - {map_data['topic']}\n")
            f.write(f"  Nodes: {map_data['node_count']}, Edges: {map_data['edge_count']}\n")
            f.write(f"  Coverage: {map_data['coverage']['nodes']:.2%} of nodes, {map_data['coverage']['edges']:.2%} of edges\n\n")
        
        f.write("\nComparative Analysis:\n\n")
        
        # Sort maps by node coverage
        sorted_maps = sorted(analysis["maps"], key=lambda x: x["coverage"]["nodes"], reverse=True)
        
        f.write("Maps ranked by concept coverage:\n\n")
        
        for i, map_data in enumerate(sorted_maps):
            f.write(f"{i+1}. {map_data['name']} - {map_data['topic']}: {map_data['coverage']['nodes']:.2%}\n")
        
        f.write("\nMaps ranked by relationship coverage:\n\n")
        
        # Sort maps by edge coverage
        sorted_maps = sorted(analysis["maps"], key=lambda x: x["coverage"]["edges"], reverse=True)
        
        for i, map_data in enumerate(sorted_maps):
            f.write(f"{i+1}. {map_data['name']} - {map_data['topic']}: {map_data['coverage']['edges']:.2%}\n")
    
    print(f"Comparative analysis saved to {analysis_path}")
    print(f"Summary report saved to {report_path}")
    print("\nBatch processing completed. Check the output directory for results.")

if __name__ == "__main__":
    main()
