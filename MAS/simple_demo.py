"""
Simple Interactive Scaffolding Demo

This script demonstrates the core interactive scaffolding functionality
without complex system dependencies.
"""

import json
import os
import sys
import random
from typing import Dict, List, Any

# Add current directory and parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(current_dir)
sys.path.append(parent_dir)

from MAS.core.scaffolding_engine import ScaffoldingEngine
from MAS.config.scaffolding_config import DEFAULT_SCAFFOLDING_CONFIG

def create_sample_concept_map(round_num: int) -> Dict[str, Any]:
    """Create a sample concept map for the given round."""
    
    if round_num == 0:
        # Initial simple map
        return {
            "nodes": ["Climate Change", "Global Warming", "Carbon Emissions", "Fossil Fuels"],
            "edges": [
                {"source": "Fossil Fuels", "target": "Carbon Emissions", "relation": "produces"},
                {"source": "Carbon Emissions", "target": "Global Warming", "relation": "causes"},
                {"source": "Global Warming", "target": "Climate Change", "relation": "leads to"}
            ]
        }
    elif round_num == 1:
        # Improved map with more concepts
        return {
            "nodes": [
                "Climate Change", "Global Warming", "Carbon Emissions", "Fossil Fuels",
                "Renewable Energy", "Greenhouse Effect", "Sea Level Rise"
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
    else:
        # Final comprehensive map
        return {
            "nodes": [
                "Climate Change", "Global Warming", "Carbon Emissions", "Fossil Fuels",
                "Renewable Energy", "Greenhouse Effect", "Sea Level Rise", "Extreme Weather",
                "Deforestation", "Ocean Acidification", "Biodiversity Loss"
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

def simulate_interactive_scaffolding():
    """Simulate an interactive scaffolding session."""
    
    print("\n🎓 Interactive Scaffolding System Demo")
    print("=" * 50)
    print("This demo shows how the system provides personalized scaffolding")
    print("based on your concept map and learning needs.\n")
    
    # Initialize scaffolding engine (with None for lead_agent since this is a simple demo)
    scaffolding_engine = ScaffoldingEngine(DEFAULT_SCAFFOLDING_CONFIG, None)
    
    # Create session state
    session_state = {
        "current_round": 0,
        "max_rounds": 3,
        "previous_concept_maps": [],
        "zpd_estimate": {
            "scaffolding_needs": {
                "strategic": "medium",
                "metacognitive": "high", 
                "procedural": "low",
                "conceptual": "medium"
            }
        }
    }
    
    # Run through 3 rounds
    for round_num in range(3):
        print(f"\n🔄 Round {round_num + 1}")
        print("-" * 30)
        
        # Get concept map for this round
        concept_map = create_sample_concept_map(round_num)
        
        print(f"📊 Your concept map has {len(concept_map['nodes'])} concepts and {len(concept_map['edges'])} relationships")
        print(f"Concepts: {', '.join(concept_map['nodes'][:5])}{'...' if len(concept_map['nodes']) > 5 else ''}")
        
        # Update session state
        session_state["current_round"] = round_num
        scaffolding_engine.update_session_state(session_state)
        
        previous_map = None
        if round_num > 0:
            previous_map = create_sample_concept_map(round_num - 1)
            session_state["previous_concept_maps"].append(previous_map)
        
        # Conduct scaffolding interaction
        scaffolding_result = scaffolding_engine.conduct_scaffolding_interaction(
            concept_map, previous_map
        )
        
        if scaffolding_result["status"] == "success":
            scaffolding_type = scaffolding_result["scaffolding_type"]
            interaction_results = scaffolding_result.get("interaction_results", {})
            prompts = interaction_results.get("prompts", [])
            
            print(f"\n🤖 Agent Scaffolding ({scaffolding_type.title()})")
            print(f"Intensity: {scaffolding_result['scaffolding_intensity']}")
            
            # Display scaffolding prompts
            for i, prompt in enumerate(prompts, 1):
                print(f"\n🤖 Agent: {prompt}")
                
                # Simulate user response (in real system, this would be user input)
                user_responses = [
                    "I think they're connected because one causes the other.",
                    "I organized my map by putting the main concept at the center.",
                    "I'm not completely sure about that relationship.",
                    "I feel confident about the basic connections but less sure about the details.",
                    "I found it challenging to decide which concepts to include.",
                    "I think I need to learn more about the underlying mechanisms.",
                    "I tried to show the cause-and-effect relationships.",
                    "The greenhouse effect seems important because it's the mechanism behind warming."
                ]
                
                user_response = random.choice(user_responses)
                print(f"👤 Your response: {user_response}")
                
                # Process response and get follow-up
                follow_up_result = scaffolding_engine.process_learner_response(user_response)
                
                if follow_up_result["status"] == "success" and follow_up_result.get("needs_follow_up") and follow_up_result.get("follow_up"):
                    print(f"🤖 Agent: {follow_up_result['follow_up']}")
                    
                    # Simulate another response
                    follow_up_response = random.choice([
                        "That makes sense, I'll think about it more.",
                        "I see what you mean about organizing it differently.",
                        "Yes, I think I can make those connections clearer.",
                        "That's a good point about the relationships."
                    ])
                    print(f"👤 Your response: {follow_up_response}")
            
            # Conclude scaffolding
            conclusion_result = scaffolding_engine.conclude_interaction()
            
            if conclusion_result["status"] == "success":
                print(f"\n🤖 Agent: {conclusion_result['conclusion']}")
        
        # Show round summary
        print(f"\n📈 Round {round_num + 1} Summary:")
        print(f"   • Scaffolding Type: {scaffolding_result.get('scaffolding_type', 'N/A')}")
        print(f"   • Intensity Level: {scaffolding_result.get('scaffolding_intensity', 'N/A')}")
        interaction_results = scaffolding_result.get('interaction_results', {})
        prompts_count = len(interaction_results.get('prompts', []))
        print(f"   • Prompts Provided: {prompts_count}")
        
        if round_num < 2:
            print("\n⏳ Preparing for next round...")
            print("   (In a real system, you would revise your concept map based on the scaffolding)")
    
    print(f"\n🎉 Session Complete!")
    print("=" * 50)
    print("This demo showed how the interactive scaffolding system:")
    print("• Analyzes your concept map to identify learning needs")
    print("• Selects appropriate scaffolding type and intensity")
    print("• Provides personalized guidance through interactive dialogue")
    print("• Adapts support based on your responses")
    print("• Fades scaffolding as your competence develops")
    print("\nThe system transforms from a passive analyzer to an active educational partner!")

def main():
    """Run the demo."""
    try:
        simulate_interactive_scaffolding()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        print(f"\nError running demo: {e}")
        print("This might be due to missing dependencies or configuration issues.")

if __name__ == "__main__":
    main()
