"""
Demo Script

This script demonstrates the functionality of the multi-agent scaffolding system
by simulating a full session with interactive scaffolding mechanisms.
"""

import json
import logging
import os
import time
import random
import sys
from typing import Dict, List, Any, Optional

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from mas_system import MultiAgentScaffoldingSystem
from utils.visualization import plot_concept_map

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(f"logs/mas_{time.strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Sample concept map data for testing
SAMPLE_CONCEPT_MAPS = {
    "initial": {
        "concepts": [
            {"id": "1", "text": "Climate Change", "x": 400, "y": 100},
            {"id": "2", "text": "Global Warming", "x": 400, "y": 200},
            {"id": "3", "text": "Carbon Emissions", "x": 200, "y": 300},
            {"id": "4", "text": "Fossil Fuels", "x": 200, "y": 400}
        ],
        "relationships": [
            {"id": "r1", "source": "4", "target": "3", "text": "produces"},
            {"id": "r2", "source": "3", "target": "2", "text": "causes"},
            {"id": "r3", "source": "2", "target": "1", "text": "leads to"}
        ]
    },
    "improved": {
        "concepts": [
            {"id": "1", "text": "Climate Change", "x": 400, "y": 100},
            {"id": "2", "text": "Global Warming", "x": 400, "y": 200},
            {"id": "3", "text": "Carbon Emissions", "x": 200, "y": 300},
            {"id": "4", "text": "Fossil Fuels", "x": 200, "y": 400},
            {"id": "5", "text": "Renewable Energy", "x": 600, "y": 400},
            {"id": "6", "text": "Greenhouse Effect", "x": 300, "y": 250},
            {"id": "7", "text": "Sea Level Rise", "x": 500, "y": 150}
        ],
        "relationships": [
            {"id": "r1", "source": "4", "target": "3", "text": "produces"},
            {"id": "r2", "source": "3", "target": "6", "text": "enhances"},
            {"id": "r3", "source": "6", "target": "2", "text": "causes"},
            {"id": "r4", "source": "2", "target": "1", "text": "is part of"},
            {"id": "r5", "source": "1", "target": "7", "text": "causes"},
            {"id": "r6", "source": "5", "target": "3", "text": "reduces"}
        ]
    },
    "final": {
        "concepts": [
            {"id": "1", "text": "Climate Change", "x": 400, "y": 100},
            {"id": "2", "text": "Global Warming", "x": 400, "y": 200},
            {"id": "3", "text": "Carbon Emissions", "x": 200, "y": 300},
            {"id": "4", "text": "Fossil Fuels", "x": 200, "y": 400},
            {"id": "5", "text": "Renewable Energy", "x": 600, "y": 400},
            {"id": "6", "text": "Greenhouse Effect", "x": 300, "y": 250},
            {"id": "7", "text": "Sea Level Rise", "x": 500, "y": 150},
            {"id": "8", "text": "Extreme Weather", "x": 600, "y": 100},
            {"id": "9", "text": "Deforestation", "x": 100, "y": 350},
            {"id": "10", "text": "Ocean Acidification", "x": 300, "y": 100},
            {"id": "11", "text": "Biodiversity Loss", "x": 200, "y": 150}
        ],
        "relationships": [
            {"id": "r1", "source": "4", "target": "3", "text": "produces"},
            {"id": "r2", "source": "3", "target": "6", "text": "enhances"},
            {"id": "r3", "source": "6", "target": "2", "text": "causes"},
            {"id": "r4", "source": "2", "target": "1", "text": "is part of"},
            {"id": "r5", "source": "1", "target": "7", "text": "causes"},
            {"id": "r6", "source": "1", "target": "8", "text": "increases"},
            {"id": "r7", "source": "1", "target": "10", "text": "leads to"},
            {"id": "r8", "source": "9", "target": "3", "text": "increases"},
            {"id": "r9", "source": "9", "target": "11", "text": "causes"},
            {"id": "r10", "source": "10", "target": "11", "text": "contributes to"},
            {"id": "r11", "source": "5", "target": "3", "text": "reduces"}
        ]
    }
}

# Expert concept map for comparison
EXPERT_CONCEPT_MAP = {
    "concepts": [
        {"id": "1", "text": "Climate Change", "x": 400, "y": 100},
        {"id": "2", "text": "Global Warming", "x": 400, "y": 200},
        {"id": "3", "text": "Carbon Emissions", "x": 200, "y": 300},
        {"id": "4", "text": "Fossil Fuels", "x": 200, "y": 400},
        {"id": "5", "text": "Renewable Energy", "x": 600, "y": 400},
        {"id": "6", "text": "Greenhouse Effect", "x": 300, "y": 250},
        {"id": "7", "text": "Sea Level Rise", "x": 500, "y": 150},
        {"id": "8", "text": "Extreme Weather", "x": 600, "y": 100},
        {"id": "9", "text": "Deforestation", "x": 100, "y": 350},
        {"id": "10", "text": "Ocean Acidification", "x": 300, "y": 100},
        {"id": "11", "text": "Biodiversity Loss", "x": 200, "y": 150},
        {"id": "12", "text": "Carbon Sequestration", "x": 500, "y": 300},
        {"id": "13", "text": "Methane", "x": 100, "y": 250},
        {"id": "14", "text": "Permafrost Melting", "x": 100, "y": 200},
        {"id": "15", "text": "Feedback Loops", "x": 250, "y": 150},
        {"id": "16", "text": "Policy Interventions", "x": 400, "y": 350},
        {"id": "17", "text": "Climate Justice", "x": 500, "y": 350}
    ],
    "relationships": [
        {"id": "r1", "source": "4", "target": "3", "text": "produces"},
        {"id": "r2", "source": "3", "target": "6", "text": "enhances"},
        {"id": "r3", "source": "6", "target": "2", "text": "causes"},
        {"id": "r4", "source": "2", "target": "1", "text": "is part of"},
        {"id": "r5", "source": "1", "target": "7", "text": "causes"},
        {"id": "r6", "source": "1", "target": "8", "text": "increases frequency of"},
        {"id": "r7", "source": "1", "target": "10", "text": "leads to"},
        {"id": "r8", "source": "9", "target": "3", "text": "increases"},
        {"id": "r9", "source": "9", "target": "11", "text": "causes"},
        {"id": "r10", "source": "10", "target": "11", "text": "contributes to"},
        {"id": "r11", "source": "5", "target": "3", "text": "reduces"},
        {"id": "r12", "source": "12", "target": "3", "text": "reduces"},
        {"id": "r13", "source": "13", "target": "6", "text": "contributes to"},
        {"id": "r14", "source": "14", "target": "13", "text": "releases"},
        {"id": "r15", "source": "2", "target": "14", "text": "causes"},
        {"id": "r16", "source": "14", "target": "15", "text": "creates"},
        {"id": "r17", "source": "15", "target": "1", "text": "accelerates"},
        {"id": "r18", "source": "16", "target": "3", "text": "regulates"},
        {"id": "r19", "source": "17", "target": "16", "text": "informs"}
    ]
}

# Sample learner profile
SAMPLE_LEARNER_PROFILE = {
    "prior_knowledge": "moderate",
    "learning_style": "visual",
    "scaffolding_preferences": {
        "strategic": 0.7,
        "metacognitive": 0.6,
        "procedural": 0.5,
        "conceptual": 0.8
    },
    "zpd": {
        "current_level": 0.6,
        "potential_level": 0.8
    }
}

def save_concept_map_as_json(concept_map: Dict[str, Any], file_path: str) -> None:
    """
    Save a concept map as a JSON file.
    
    Args:
        concept_map: Concept map data
        file_path: Path to save the JSON file
    """
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    with open(file_path, 'w') as f:
        json.dump(concept_map, f, indent=2)

def simulate_learner_response(prompt: str) -> str:
    """
    Simulate a learner response to a scaffolding prompt.
    
    Args:
        prompt: Scaffolding prompt
        
    Returns:
        Simulated learner response
    """
    # Define some sample responses
    responses = [
        "I think the concepts are related because they share a common cause.",
        "I organized my map by putting the most important concepts at the top.",
        "I'm not sure about that relationship, but I'll think about it more.",
        "I feel most confident about the relationship between fossil fuels and carbon emissions.",
        "I found it challenging to decide which relationships to include.",
        "I think I need to learn more about feedback loops in climate systems.",
        "I tried to show the causal relationships between concepts.",
        "I think the greenhouse effect is important because it's the mechanism that causes warming."
    ]
    
    # Return a random response
    return random.choice(responses)


#runs the demo. It generates random responses from the dict
def run_demo() -> None:
    """
    Run the demo.
    """
    print("\n=== Multi-Agent Scaffolding System Demo ===\n")
    
    # Create output directory
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    # Save demo configuration
    config = {
        "expert_map_included": True,
        "learner_profile_included": True,
        "scaffolding_enabled": True,
        "rounds": 3
    }
    
    config_path = os.path.join(output_dir, "demo_config.json")
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    # Initialize system with config
    system_config = {
        "expert_map_path": None,  # Will be set directly
        "learner_profile_path": None,  # Will be set directly
        "content_path": None,
        "scaffolding_enabled": True,
        "scaffolding_types": ["strategic", "metacognitive", "procedural", "conceptual"],
        "scaffolding_weights": {
            "strategic": 1.0,
            "metacognitive": 1.0,
            "procedural": 1.0,
            "conceptual": 1.0
        }
    }
    system = MultiAgentScaffoldingSystem(system_config)
    print("Initialized multi-agent scaffolding system")
    
    # Set expert map
    system.set_expert_map(EXPERT_CONCEPT_MAP)
    print("Set expert concept map")
    
    # Set learner profile
    system.set_learner_profile(SAMPLE_LEARNER_PROFILE)
    print("Set learner profile")
    
    # Run rounds
    for round_num in range(3):
        print(f"\n=== Round {round_num} ===\n")
        
        # Get concept map for this round
        if round_num == 0:
            concept_map = SAMPLE_CONCEPT_MAPS["initial"]
        elif round_num == 1:
            concept_map = SAMPLE_CONCEPT_MAPS["improved"]
        else:
            concept_map = SAMPLE_CONCEPT_MAPS["final"]
        
        # Save concept map as JSON
        json_path = os.path.join(output_dir, f"concept_map_round_{round_num}.json")
        save_concept_map_as_json(concept_map, json_path)
        
        # Visualize concept map
        plot_concept_map(concept_map, os.path.join(output_dir, f"concept_map_round_{round_num}.png"))
        
        # Process concept map
        print(f"Processing concept map with {len(concept_map['concepts'])} concepts and {len(concept_map['relationships'])} relationships")
        
        # Conduct scaffolding interaction
        #interactive_mode = True
        
        #if interactive_mode:
            # Interactive mode: Use real user input
        #    scaffolding_result = system.conduct_scaffolding_interaction(concept_map, round_num)
       # else:
            # Simulation mode: Use simulated responses
            # Start scaffolding interaction
       #     interaction_result = system.conduct_scaffolding_interaction(concept_map, round_num)
            
            # Get scaffolding information
        #    scaffolding_type = interaction_result.get("round_info", {}).get("scaffolding_type", "")
         #   scaffolding_intensity = interaction_result.get("round_info", {}).get("scaffolding_intensity", "")
          #  current_prompt = interaction_result.get("current_prompt", "")
            
            # Check if there's a prompt (indicating scaffolding is active)
           # if current_prompt:
            #    print(f"\nAgent Feedback (Scaffolding Type: {scaffolding_type}, Intensity: {scaffolding_intensity})")
                
                # Display prompt
             #   print(f"\n🤖 Agent ({scaffolding_type}): {current_prompt}")
                
                # Process each interaction
              #  while current_prompt and not interaction_result.get("dialogue_complete", False):
                    # Simulate learner response
               #     learner_response = simulate_learner_response(current_prompt)
                #    print(f"👤 Your response: {learner_response}")
                    
                    # Process learner response
                 #   response_result = system.process_scaffolding_response(learner_response)
                    
                    # Check if there's a follow-up
                  #  follow_up = response_result.get("follow_up", "")
                    
                   # if follow_up:
                        # Display follow-up
                    #    print(f"\n🤖 Agent ({scaffolding_type}): {follow_up}")
                    
                    # Get next prompt
                #    next_prompt = response_result.get("next_prompt", "")
                    
                 #   if next_prompt:
                        # Display next prompt
                  #      print(f"\n🤖 Agent ({scaffolding_type}): {next_prompt}")
                        
                        # Update current prompt
                   #     current_prompt = next_prompt
                    #else:
                        # No more prompts
            #            current_prompt = ""
                    
                    # Check if dialogue is complete
             #       if response_result.get("dialogue_complete", False):
                        # Get conclusion
              #          conclusion = response_result.get("conclusion", "")
                        
                        # Display conclusion
               #         if conclusion:
                #            print(f"\n🤖 Agent: {conclusion}")
                        
                        # Break out of loop
                 #       break
            
            # Store scaffolding result
           # scaffolding_result = response_result
        
        # Get scaffolding summary
        scaffolding_summary = system.get_scaffolding_summary()
        
        # Print summary
        print(f"\nRound {round_num} Summary:")
        print(f"- Concepts: {len(concept_map['concepts'])}")
        print(f"- Relationships: {len(concept_map['relationships'])}")
        
        # Print scaffolding effectiveness if available
        if scaffolding_summary.get("engine_summary", {}).get("effectiveness"):
            effectiveness = scaffolding_summary["engine_summary"]["effectiveness"]
            print(f"- Scaffolding Effectiveness: {effectiveness:.2f}")
    
    print("\nDemo completed. Check the output directory for generated files.")

if __name__ == "__main__":
    run_demo()
