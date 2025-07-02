"""
Programmatic Usage Example

This script demonstrates how to use the Multi-Agent Scaffolding System programmatically.
"""

import json
import os
import sys
from pathlib import Path

# Add the parent directory to the Python path to import the MAS package
sys.path.append(str(Path(__file__).parent.parent))

from MAS.mas_system import MultiAgentScaffoldingSystem
from utils.visualization import plot_concept_map

def create_sample_config():
    """
    Create a sample configuration for the example.
    
    Returns:
        Sample configuration
    """
    config = {
        "max_rounds": 3,
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

def create_sample_concept_map():
    """
    Create a sample concept map for the example.
    
    Returns:
        Sample concept map
    """
    concept_map = {
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
    
    return concept_map

def create_expert_concept_map():
    """
    Create an expert concept map for the example.
    
    Returns:
        Expert concept map
    """
    expert_map = {
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
            "Ocean Acidification"
        ],
        "edges": [
            {"source": "Fossil Fuels", "target": "Carbon Emissions", "relation": "produces"},
            {"source": "Carbon Emissions", "target": "Greenhouse Effect", "relation": "enhances"},
            {"source": "Greenhouse Effect", "target": "Global Warming", "relation": "causes"},
            {"source": "Global Warming", "target": "Climate Change", "relation": "is part of"},
            {"source": "Climate Change", "target": "Sea Level Rise", "relation": "causes"},
            {"source": "Climate Change", "target": "Extreme Weather", "relation": "increases"},
            {"source": "Deforestation", "target": "Carbon Emissions", "relation": "increases"},
            {"source": "Renewable Energy", "target": "Carbon Emissions", "relation": "reduces"}
        ]
    }
    
    return expert_map

def main():
    """
    Main function for the example.
    """
    print("Multi-Agent Scaffolding System - Programmatic Usage Example")
    
    # Create output directory
    output_dir = "examples/output"
    os.makedirs(output_dir, exist_ok=True)
    
    # Create and save sample configuration
    config = create_sample_config()
    config["output_dir"] = output_dir
    
    config_path = os.path.join(output_dir, "example_config.json")
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"Created sample configuration at {config_path}")
    
    # Initialize system
    system = MultiAgentScaffoldingSystem(config_path)
    print("Initialized multi-agent scaffolding system")
    
    # Set expert concept map for the example map agent
    expert_map = create_expert_concept_map()
    for agent_id, agent in system.agents.items():
        if agent.agent_type == "example_map":
            agent.set_example_map(expert_map)
            print("Set expert concept map for comparison")
    
    # Create sample concept map
    concept_map = create_sample_concept_map()
    
    # Save concept map as JSON
    json_path = os.path.join(output_dir, "concept_map.json")
    with open(json_path, 'w') as f:
        json.dump(concept_map, f, indent=2)
    
    # Plot concept map
    plot_path = os.path.join(output_dir, "concept_map.png")
    plot_concept_map(concept_map, plot_path)
    
    print(f"Created sample concept map at {json_path} and {plot_path}")
    
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
    
    # Process concept map
    print(f"Processing concept map with {len(concept_map['nodes'])} concepts and {len(concept_map['edges'])} relationships")
    
    # Directly update system's session state with the concept map
    system.session_state["current_concept_map"] = concept_map
    
    # Create input data for agents
    input_data = {
        "type": "concept_map_submission",
        "concept_map_data": concept_map,
        "pdf_path": json_path,  # Using JSON path as a stand-in for PDF path
        "round": system.session_state["current_round"]
    }
    
    # Process with lead agent
    context = {"session_state": system.session_state}
    result = system.lead_agent.process(input_data, context)
    
    # Update session state
    if "session_state_updates" in result:
        system.session_state.update(result["session_state_updates"])
    
    # Store concept map in session state
    if system.session_state["current_round"] > 0:
        system.session_state["previous_concept_maps"].append(concept_map)
    
    # Print feedback from agents
    print("\n--- Agent Feedback ---\n")
    
    responses = result.get("agent_responses", {})
    for agent_type, response in responses.items():
        if response:
            print(f"[{agent_type.replace('_', ' ').title()}]\n")
            print(response)
            print("\n" + "-" * 80 + "\n")
    
    # Increment round counter
    system.session_state["current_round"] += 1
    
    # Finalize session
    print("\n--- Finalizing Session ---\n")
    
    # Create input data for agents
    input_data = {
        "type": "final_round",
        "concept_map_data": concept_map
    }
    
    # Process with lead agent
    context = {"session_state": system.session_state}
    result = system.lead_agent.process(input_data, context)
    
    # Print summary feedback from agents
    print("\n--- Summary Feedback ---\n")
    
    responses = result.get("agent_responses", {})
    for agent_type, response in responses.items():
        if response:
            print(f"[{agent_type.replace('_', ' ').title()}]\n")
            print(response)
            print("\n" + "-" * 80 + "\n")
    
    # Generate session log
    system._generate_session_log()
    
    print("\nExample completed. Check the output directory for generated files.")

if __name__ == "__main__":
    main()
