"""
Ablation Study Example

This script demonstrates how to run an ablation study by enabling/disabling different design features.
"""

import json
import os
import sys
from pathlib import Path

# Add the parent directory to the Python path to import the MAS package
sys.path.append(str(Path(__file__).parent.parent))

from MAS.mas_system import MultiAgentScaffoldingSystem
from utils.visualization import plot_concept_map

# Sample concept map data for testing
SAMPLE_CONCEPT_MAP = {
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

def create_base_config():
    """
    Create a base configuration for the ablation study.
    
    Returns:
        Base configuration
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

def run_experiment(config, experiment_name):
    """
    Run an experiment with the given configuration.
    
    Args:
        config: System configuration
        experiment_name: Name of the experiment
    """
    print(f"\n=== Running Experiment: {experiment_name} ===\n")
    
    # Create output directory
    output_dir = f"examples/output/{experiment_name}"
    os.makedirs(output_dir, exist_ok=True)
    
    # Update output directory in config
    config["output_dir"] = output_dir
    
    # Save configuration
    config_path = os.path.join(output_dir, "config.json")
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"Created configuration at {config_path}")
    
    # Initialize system
    system = MultiAgentScaffoldingSystem(config_path)
    print("Initialized multi-agent scaffolding system")
    
    # Set expert concept map for the example map agent if enabled
    if config["design_features"]["df3_example_map"]:
        for agent_id, agent in system.agents.items():
            if agent.agent_type == "example_map":
                agent.set_example_map(EXPERT_CONCEPT_MAP)
                print("Set expert concept map for comparison")
    
    # Save concept map as JSON
    json_path = os.path.join(output_dir, "concept_map.json")
    with open(json_path, 'w') as f:
        json.dump(SAMPLE_CONCEPT_MAP, f, indent=2)
    
    # Plot concept map
    plot_path = os.path.join(output_dir, "concept_map.png")
    plot_concept_map(SAMPLE_CONCEPT_MAP, plot_path)
    
    print(f"Created sample concept map at {json_path} and {plot_path}")
    
    # Simulate learner profile input if enabled
    if config["design_features"]["df1_learner_profiling"]:
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
    print(f"Processing concept map with {len(SAMPLE_CONCEPT_MAP['nodes'])} concepts and {len(SAMPLE_CONCEPT_MAP['edges'])} relationships")
    
    # Directly update system's session state with the concept map
    system.session_state["current_concept_map"] = SAMPLE_CONCEPT_MAP
    
    # Create input data for agents
    input_data = {
        "type": "concept_map_submission",
        "concept_map_data": SAMPLE_CONCEPT_MAP,
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
        system.session_state["previous_concept_maps"].append(SAMPLE_CONCEPT_MAP)
    
    # Save agent responses
    responses_path = os.path.join(output_dir, "agent_responses.json")
    with open(responses_path, 'w') as f:
        json.dump(result.get("agent_responses", {}), f, indent=2)
    
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
        "concept_map_data": SAMPLE_CONCEPT_MAP
    }
    
    # Process with lead agent
    context = {"session_state": system.session_state}
    result = system.lead_agent.process(input_data, context)
    
    # Save summary responses
    summary_path = os.path.join(output_dir, "summary_responses.json")
    with open(summary_path, 'w') as f:
        json.dump(result.get("agent_responses", {}), f, indent=2)
    
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
    
    print(f"\nExperiment '{experiment_name}' completed. Check the output directory for generated files.")

def main():
    """
    Main function for the ablation study.
    """
    print("Multi-Agent Scaffolding System - Ablation Study Example")
    
    # Create base output directory
    os.makedirs("examples/output", exist_ok=True)
    
    # Define experiments
    experiments = [
        {
            "name": "all_features",
            "description": "All design features enabled",
            "config_updates": {
                "design_features": {
                    "df1_learner_profiling": True,
                    "df2_scaffolding": True,
                    "df3_example_map": True,
                    "df4_content_ingestion": True
                }
            }
        },
        {
            "name": "no_learner_profiling",
            "description": "Learner profiling disabled",
            "config_updates": {
                "design_features": {
                    "df1_learner_profiling": False,
                    "df2_scaffolding": True,
                    "df3_example_map": True,
                    "df4_content_ingestion": True
                }
            }
        },
        {
            "name": "no_scaffolding",
            "description": "Scaffolding disabled",
            "config_updates": {
                "design_features": {
                    "df1_learner_profiling": True,
                    "df2_scaffolding": False,
                    "df3_example_map": True,
                    "df4_content_ingestion": True
                }
            }
        },
        {
            "name": "no_example_map",
            "description": "Example map disabled",
            "config_updates": {
                "design_features": {
                    "df1_learner_profiling": True,
                    "df2_scaffolding": True,
                    "df3_example_map": False,
                    "df4_content_ingestion": True
                }
            }
        },
        {
            "name": "no_content_ingestion",
            "description": "Content ingestion disabled",
            "config_updates": {
                "design_features": {
                    "df1_learner_profiling": True,
                    "df2_scaffolding": True,
                    "df3_example_map": True,
                    "df4_content_ingestion": False
                }
            }
        },
        {
            "name": "minimal_features",
            "description": "Only scaffolding enabled",
            "config_updates": {
                "design_features": {
                    "df1_learner_profiling": False,
                    "df2_scaffolding": True,
                    "df3_example_map": False,
                    "df4_content_ingestion": False
                }
            }
        }
    ]
    
    # Run each experiment
    for experiment in experiments:
        # Create config for this experiment
        config = create_base_config()
        
        # Update config with experiment-specific settings
        for key, value in experiment["config_updates"].items():
            if isinstance(value, dict):
                if key not in config:
                    config[key] = {}
                for subkey, subvalue in value.items():
                    config[key][subkey] = subvalue
            else:
                config[key] = value
        
        # Run the experiment
        run_experiment(config, experiment["name"])
    
    print("\nAblation study completed. Check the output directories for results.")

if __name__ == "__main__":
    main()
