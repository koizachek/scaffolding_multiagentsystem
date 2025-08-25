"""
Test script for improved template selection system.
This verifies that templates are not repeated and are selected intelligently.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.scaffolding_utils import (
    generate_default_prompts,
    analyze_user_response_type,
    select_appropriate_followup
)
from core.scaffolding_engine import ScaffoldingEngine

def test_template_non_repetition():
    """Test that templates are not repeated within a conversation."""
    print("\n=== Testing Template Non-Repetition ===")
    
    # Test data
    analysis = {
        "node_count": 5,
        "edge_count": 3,
        "isolated_nodes": ["node1", "node2"],
        "connectivity_ratio": 0.6
    }
    
    enhanced_map = {
        "nodes": [
            {"id": "1", "label": "Market Analysis"},
            {"id": "2", "label": "AMG"},
            {"id": "3", "label": "Entry Barriers"}
        ],
        "edges": [
            {"source": "1", "target": "2", "label": "influences"}
        ]
    }
    
    # Test for each scaffolding type
    for scaffolding_type in ["strategic", "metacognitive", "procedural", "conceptual"]:
        print(f"\nTesting {scaffolding_type} scaffolding:")
        
        used_indices = []
        prompts_generated = []
        
        # Generate multiple prompts and ensure no repetition
        for turn in range(5):
            prompts, indices = generate_default_prompts(
                scaffolding_type,
                "high",  # Using high intensity
                analysis,
                enhanced_map,
                used_indices,
                turn
            )
            
            print(f"  Turn {turn}: Generated prompt (index {indices[0]})")
            print(f"    Prompt: {prompts[0][:100]}...")
            
            # Check for repetition
            if indices[0] in used_indices:
                print(f"    WARNING: Template index {indices[0]} was already used!")
            
            used_indices.extend(indices)
            prompts_generated.append(prompts[0])
        
        # Check uniqueness
        unique_prompts = len(set(prompts_generated))
        print(f"  Summary: {unique_prompts}/{len(prompts_generated)} unique prompts generated")


def test_response_analysis():
    """Test response type analysis."""
    print("\n=== Testing Response Analysis ===")
    
    test_responses = [
        ("How do I connect AMG to market entry?", "question"),
        ("I'm not sure about the relationship between financing and strategy.", "confusion"),
        ("I think AMG influences entry barriers through resource blocking.", "concrete_idea"),
        ("The market analysis helps identify target markets.", "concrete_idea"),
        ("What should I do next?", "question"),
        ("I don't understand how to show this.", "confusion")
    ]
    
    for response, expected_type in test_responses:
        analysis = analyze_user_response_type(response)
        print(f"\nResponse: '{response[:50]}...'")
        print(f"  Expected: {expected_type}")
        print(f"  Detected: {analysis['response_type']}")
        print(f"  Analysis: is_question={analysis['is_question']}, "
              f"is_confused={analysis['is_confused']}, "
              f"has_concrete_idea={analysis['has_concrete_idea']}")


def test_followup_selection():
    """Test intelligent follow-up selection."""
    print("\n=== Testing Follow-up Selection ===")
    
    test_cases = [
        ("I think AMG creates barriers through network control.", "conceptual"),
        ("How should I organize these concepts?", "strategic"),
        ("I'm confused about the relationships.", "procedural"),
        ("I feel like I understand AMG better now.", "metacognitive")
    ]
    
    for response, scaffolding_type in test_cases:
        print(f"\nScaffolding type: {scaffolding_type}")
        print(f"User response: '{response}'")
        
        used_indices = []
        
        # Generate multiple follow-ups
        for i in range(3):
            followup, index = select_appropriate_followup(
                response,
                scaffolding_type,
                used_indices
            )
            
            print(f"  Follow-up {i+1} (index {index}): {followup[:80]}...")
            
            if index >= 0:
                used_indices.append(index)


def test_scaffolding_engine_integration():
    """Test the integrated scaffolding engine with new features."""
    print("\n=== Testing Scaffolding Engine Integration ===")
    
    # Create engine
    config = {}
    engine = ScaffoldingEngine(config, None)
    
    # Simulate concept map
    concept_map = {
        "nodes": ["Market Analysis", "AMG", "Entry Barriers", "Financing"],
        "edges": [
            {"source": "AMG", "target": "Entry Barriers", "relation": "increases"},
            {"source": "Market Analysis", "target": "AMG", "relation": "identifies"}
        ]
    }
    
    # Conduct initial interaction
    result = engine.conduct_scaffolding_interaction(concept_map)
    
    if result["status"] == "success":
        print(f"\nInitial scaffolding type: {result['scaffolding_type']}")
        print(f"Intensity: {result['scaffolding_intensity']}")
        print(f"Initial prompt: {result['interaction_results']['prompts'][0][:100]}...")
        
        # Simulate user responses
        test_responses = [
            "I'm not sure how to connect these concepts better.",
            "I think AMG affects multiple aspects of market entry through its mechanisms."
        ]
        
        for i, user_response in enumerate(test_responses):
            print(f"\n--- User Response {i+1} ---")
            print(f"User: {user_response}")
            
            response_result = engine.process_learner_response(user_response)
            
            if response_result["status"] == "success" and response_result.get("needs_follow_up"):
                print(f"Response type detected: {response_result.get('response_type', 'unknown')}")
                print(f"Agent follow-up: {response_result['follow_up'][:100]}...")
        
        # Conclude interaction
        conclusion_result = engine.conclude_interaction()
        if conclusion_result["status"] == "success":
            print(f"\n--- Conclusion ---")
            print(f"Conclusion: {conclusion_result['conclusion'][:150]}...")
    else:
        print(f"Error: {result.get('message', 'Unknown error')}")


def main():
    """Run all tests."""
    print("=" * 60)
    print("TESTING IMPROVED TEMPLATE SELECTION SYSTEM")
    print("=" * 60)
    
    test_template_non_repetition()
    test_response_analysis()
    test_followup_selection()
    test_scaffolding_engine_integration()
    
    print("\n" + "=" * 60)
    print("TESTS COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()
