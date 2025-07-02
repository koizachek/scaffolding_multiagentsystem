"""
Test imports for the multi-agent scaffolding system.
"""

import sys
import os
import json

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """Test all module imports."""
    print("🔧 Testing Multi-Agent Scaffolding System Imports")
    print("=" * 60)
    
    # Test basic package import
    try:
        print("1. Testing MAS package import...")
        import MAS
        print("✓ MAS package imported successfully")
    except Exception as e:
        print(f"✗ MAS package import failed: {e}")
        return False
    
    # Test system import
    try:
        print("2. Testing system import...")
        from MAS.mas_system import MultiAgentScaffoldingSystem
        print("✓ System import successful")
    except Exception as e:
        print(f"✗ System import failed: {e}")
        return False
    
    # Test agent imports
    try:
        print("3. Testing agent imports...")
        from MAS.agents.lead_agent import LeadAgent
        from MAS.agents.strategic_scaffolding_agent import StrategicScaffoldingAgent
        from MAS.agents.metacognitive_scaffolding_agent import MetacognitiveScaffoldingAgent
        from MAS.agents.procedural_scaffolding_agent import ProceduralScaffoldingAgent
        from MAS.agents.conceptual_scaffolding_agent import ConceptualScaffoldingAgent
        print("✓ Agent imports successful")
    except Exception as e:
        print(f"✗ Agent imports failed: {e}")
        return False
    
    # Test core imports
    try:
        print("4. Testing core imports...")
        from MAS.core.scaffolding_engine import ScaffoldingEngine
        from MAS.core.dialogue_manager import DialogueManager
        print("✓ Core imports successful")
    except Exception as e:
        print(f"✗ Core imports failed: {e}")
        return False
    
    # Test config imports
    try:
        print("5. Testing config imports...")
        from MAS.config.scaffolding_config import DEFAULT_SCAFFOLDING_CONFIG
        print("✓ Config imports successful")
    except Exception as e:
        print(f"✗ Config imports failed: {e}")
        return False
    
    # Test utils imports
    try:
        print("6. Testing utils imports...")
        from MAS.utils.logging_utils import setup_logging
        from MAS.utils.scaffolding_utils import analyze_concept_map
        print("✓ Utils imports successful")
    except Exception as e:
        print(f"✗ Utils imports failed: {e}")
        return False
    
    print("\n✅ All imports successful!")
    return True

def test_system_instantiation():
    """Test system instantiation and basic functionality."""
    print("\n🚀 Testing System Instantiation")
    print("=" * 60)
    
    try:
        from MAS.mas_system import MultiAgentScaffoldingSystem
        
        # Use the existing config file
        config_path = os.path.join(os.path.dirname(__file__), "config.json")
        if not os.path.exists(config_path):
            # Use demo config as fallback
            config_path = os.path.join(os.path.dirname(__file__), "output", "demo_config.json")
        
        print(f"1. Loading configuration from: {config_path}")
        
        # Initialize the system
        print("2. Initializing MultiAgentScaffoldingSystem...")
        system = MultiAgentScaffoldingSystem(config_path)
        print("✓ System initialized successfully")
        
        # Check agents
        agents = system.get_agents()
        print(f"3. System has {len(agents)} agents:")
        for agent_id, agent in agents.items():
            print(f"   - {agent_id}: {agent.agent_type}")
        
        # Check session state
        session_state = system.get_session_state()
        print(f"4. Session state initialized:")
        print(f"   - Current round: {session_state.get('current_round', 0)}")
        print(f"   - Max rounds: {session_state.get('max_rounds', 4)}")
        print(f"   - Interactive scaffolding: {session_state.get('interactive_scaffolding', False)}")
        
        print("\n✅ System instantiation successful!")
        return system
        
    except Exception as e:
        print(f"✗ System instantiation failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def simulate_scaffolding_interaction(system):
    """Simulate a full scaffolding interaction."""
    print("\n🎯 Simulating Scaffolding Interaction")
    print("=" * 60)
    
    try:
        # Create a sample concept map
        sample_concept_map = {
            "nodes": [
                {"id": "1", "label": "Climate Change", "x": 100, "y": 100},
                {"id": "2", "label": "Greenhouse Gases", "x": 200, "y": 150},
                {"id": "3", "label": "Global Warming", "x": 300, "y": 100},
                {"id": "4", "label": "Carbon Dioxide", "x": 150, "y": 200}
            ],
            "edges": [
                {"source": "2", "target": "1", "label": "causes"},
                {"source": "1", "target": "3", "label": "leads to"},
                {"source": "4", "target": "2", "label": "is a type of"}
            ]
        }
        
        print("1. Created sample concept map with 4 concepts and 3 relationships")
        
        # Create input data for the system
        input_data = {
            "type": "concept_map_submission",
            "concept_map_data": sample_concept_map,
            "round": 0
        }
        
        print("2. Processing concept map through lead agent...")
        
        # Get the lead agent
        lead_agent = None
        for agent_id, agent in system.get_agents().items():
            if agent.agent_type == "lead":
                lead_agent = agent
                break
        
        if not lead_agent:
            print("✗ No lead agent found")
            return False
        
        # Process the concept map
        context = {"session_state": system.get_session_state()}
        result = lead_agent.process(input_data, context)
        
        print("3. Lead agent processing result:")
        print(f"   - Status: {result.get('status', 'unknown')}")
        print(f"   - Agent type: {result.get('agent_type', 'unknown')}")
        
        # Check if scaffolding was triggered
        if "scaffolding_interactions" in result:
            interactions = result["scaffolding_interactions"]
            print(f"4. Scaffolding interactions generated: {len(interactions)}")
            
            for i, interaction in enumerate(interactions):
                print(f"\n   Interaction {i+1}:")
                print(f"   - Scaffolding type: {interaction.get('scaffolding_type', 'unknown')}")
                print(f"   - Agent: {interaction.get('agent_type', 'unknown')}")
                
                # Show the prompt
                prompts = interaction.get('prompts', [])
                if prompts:
                    print(f"   - Agent prompt: {prompts[0][:100]}...")
                
                # Simulate learner response
                simulated_responses = [
                    "I think greenhouse gases trap heat in the atmosphere.",
                    "I'm not sure how carbon dioxide specifically contributes.",
                    "I want to add more concepts about renewable energy.",
                    "This helps me see the connections better."
                ]
                
                learner_response = simulated_responses[i % len(simulated_responses)]
                print(f"   - Simulated learner response: {learner_response}")
                
                # Process the response (if the system supports it)
                if hasattr(system, 'process_user_response'):
                    response_result = system.process_user_response(learner_response)
                    print(f"   - System adaptation: {response_result.get('status', 'processed')}")
        
        elif "response" in result and result["response"]:
            print("4. Agent feedback generated:")
            response = result["response"]
            if isinstance(response, str):
                print(f"   - Response: {response[:200]}...")
            else:
                print(f"   - Response type: {type(response)}")
        
        print("\n✅ Scaffolding interaction simulation completed!")
        return True
        
    except Exception as e:
        print(f"✗ Scaffolding simulation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function."""
    print("🧪 Multi-Agent Scaffolding System Test Suite")
    print("=" * 60)
    
    # Test imports
    if not test_imports():
        print("\n❌ Import tests failed. Exiting.")
        return False
    
    # Test system instantiation
    system = test_system_instantiation()
    if not system:
        print("\n❌ System instantiation failed. Exiting.")
        return False
    
    # Test scaffolding interaction
    if not simulate_scaffolding_interaction(system):
        print("\n❌ Scaffolding simulation failed.")
        return False
    
    print("\n🎉 All tests passed successfully!")
    print("The Multi-Agent Scaffolding System is working correctly.")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
