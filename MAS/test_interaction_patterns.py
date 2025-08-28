#!/usr/bin/env python3
"""
Test script for enhanced interaction patterns in the scaffolding system.

This script tests all 8 interaction patterns plus the mandatory interaction rule.
"""

import sys
import os

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.scaffolding_utils import (
    analyze_user_response_type,
    handle_domain_question,
    handle_system_question,
    handle_disagreement,
    handle_empty_input,
    handle_inappropriate_language,
    handle_off_topic,
    handle_frustration,
    handle_premature_ending,
    generate_concrete_idea_followup
)

def test_pattern_detection():
    """Test that all patterns are correctly detected."""
    print("\n" + "="*60)
    print("TESTING PATTERN DETECTION")
    print("="*60)
    
    test_cases = [
        # Pattern 1.1: Domain questions
        ("What is AMG exactly?", "domain_question"),
        ("Can you explain how market entry works?", "domain_question"),
        ("Tell me about international strategy?", "domain_question"),
        
        # Pattern 1.2: System questions
        ("How do I create a node?", "system_question"),
        ("Where is the delete button?", "system_question"),
        ("How to use this tool?", "system_question"),
        
        # Pattern 2: Disagreement
        ("I don't agree with that approach", "disagreement"),
        ("That's not right, I think differently", "disagreement"),
        ("No, but I think it should be organized differently", "disagreement"),
        
        # Pattern 3: Empty input
        ("", "empty"),
        ("  ", "empty"),
        
        # Pattern 4: Inappropriate language (not testing actual profanity)
        ("This is stupid and useless", "statement"),  # Should detect inappropriate
        
        # Pattern 5: Concrete ideas
        ("I think AMG affects market entry because it creates barriers", "concrete_idea"),
        ("I've added the relationship between strategy and resources", "concrete_idea"),
        ("In my map, I connected financing to market success", "concrete_idea"),
        
        # Pattern 6: Off-topic
        ("What's the weather like today?", "off_topic"),
        ("Did you see the game last night?", "off_topic"),
        
        # Pattern 7: Frustration
        ("This is too difficult, I'm struggling", "frustration"),
        ("I don't get it, this is overwhelming", "frustration"),
        
        # Pattern 8: Premature ending
        ("I'm done, that's all", "premature_ending"),
        ("Can't think of anything more", "premature_ending"),
    ]
    
    for response, expected_type in test_cases:
        analysis = analyze_user_response_type(response)
        detected_type = analysis["response_type"]
        status = "✓" if detected_type == expected_type else "✗"
        print(f"{status} '{response[:50]}...' → Expected: {expected_type}, Got: {detected_type}")
        
        # Show additional flags for debugging
        if detected_type != expected_type:
            print(f"   Analysis flags: empty={analysis.get('is_empty')}, "
                  f"question={analysis.get('is_question')}, "
                  f"domain={analysis.get('is_domain_question')}, "
                  f"system={analysis.get('is_system_question')}, "
                  f"disagreement={analysis.get('is_disagreement')}, "
                  f"inappropriate={analysis.get('is_inappropriate')}, "
                  f"off_topic={analysis.get('is_off_topic')}, "
                  f"frustrated={analysis.get('is_frustrated')}, "
                  f"wants_end={analysis.get('wants_to_end')}")

def test_pattern_handlers():
    """Test that pattern handlers generate appropriate responses."""
    print("\n" + "="*60)
    print("TESTING PATTERN HANDLERS")
    print("="*60)
    
    scaffolding_types = ["conceptual", "strategic", "procedural", "metacognitive"]
    
    # Test each pattern handler
    print("\n--- Pattern 1.1: Domain Questions ---")
    for s_type in scaffolding_types:
        response = handle_domain_question("What is AMG?", s_type, ["AMG"])
        print(f"{s_type}: {response[:100]}...")
    
    print("\n--- Pattern 1.2: System Questions ---")
    for s_type in scaffolding_types:
        response = handle_system_question("How do I create nodes?", s_type)
        print(f"{s_type}: {response[:100]}...")
    
    print("\n--- Pattern 2: Disagreement (content) ---")
    for s_type in scaffolding_types:
        response = handle_disagreement("I disagree with that concept", s_type, "content")
        print(f"{s_type}: {response[:100]}...")
    
    print("\n--- Pattern 3: Empty Input ---")
    for s_type in scaffolding_types:
        response = handle_empty_input(s_type)
        print(f"{s_type}: {response[:100]}...")
    
    print("\n--- Pattern 4: Inappropriate Language ---")
    for s_type in scaffolding_types:
        response = handle_inappropriate_language(s_type)
        print(f"{s_type}: {response[:100]}...")
    
    print("\n--- Pattern 6: Off-topic ---")
    for s_type in scaffolding_types:
        response = handle_off_topic(s_type)
        print(f"{s_type}: {response[:100]}...")
    
    print("\n--- Pattern 7: Frustration ---")
    for s_type in scaffolding_types:
        response = handle_frustration("This is too hard", s_type)
        print(f"{s_type}: {response[:100]}...")
    
    print("\n--- Pattern 8: Premature Ending ---")
    for s_type in scaffolding_types:
        response = handle_premature_ending(s_type)
        print(f"{s_type}: {response[:100]}...")
    
    print("\n--- Pattern 5: Concrete Ideas (Critical Fix) ---")
    for s_type in scaffolding_types:
        response = generate_concrete_idea_followup(
            "I think AMG creates barriers", 
            s_type, 
            ["AMG", "barriers"]
        )
        print(f"{s_type}: {response[:100]}...")

def test_critical_pattern_5_fix():
    """Test the critical fix for Pattern 5 - no generic affirmations without ideas."""
    print("\n" + "="*60)
    print("TESTING CRITICAL PATTERN 5 FIX")
    print("="*60)
    
    test_cases = [
        # Should NOT trigger affirmative response
        ("okay", False, "Simple acknowledgment"),
        ("yes", False, "Simple agreement"),
        ("I see", False, "Simple understanding"),
        ("hmm", False, "Non-committal response"),
        ("I don't know", False, "Uncertainty"),
        
        # SHOULD trigger affirmative response
        ("I think AMG affects market entry through regulatory barriers", True, "Concrete idea"),
        ("I've added connections between financing and market success", True, "Map modification"),
        ("In my understanding, the strategy depends on resources", True, "Conceptual insight"),
        ("I believe the main challenge is adapting to local markets", True, "Analytical thought"),
    ]
    
    for response, should_affirm, description in test_cases:
        analysis = analyze_user_response_type(response)
        has_concrete = analysis.get("has_concrete_idea", False)
        
        if should_affirm:
            if has_concrete:
                print(f"✓ {description}: Correctly identified concrete idea")
                # Test that it generates appropriate follow-up
                followup = generate_concrete_idea_followup(response, "conceptual", [])
                if "Does your current concept map reflect" in followup:
                    print(f"  ✓ Generates action-oriented follow-up")
                else:
                    print(f"  ✗ Follow-up missing call to action")
            else:
                print(f"✗ {description}: Failed to identify concrete idea")
        else:
            if not has_concrete:
                print(f"✓ {description}: Correctly avoided false positive")
            else:
                print(f"✗ {description}: False positive - would trigger inappropriate affirmation")

def test_mandatory_interaction():
    """Test that the system enforces mandatory interaction."""
    print("\n" + "="*60)
    print("TESTING MANDATORY INTERACTION ENFORCEMENT")
    print("="*60)
    
    from core.scaffolding_engine import ScaffoldingEngine
    
    # Create a mock scaffolding engine
    config = {}
    lead_agent = None
    engine = ScaffoldingEngine(config, lead_agent)
    
    # Simulate a scaffolding interaction
    concept_map = {
        "nodes": ["concept1", "concept2"],
        "edges": [{"source": "concept1", "target": "concept2"}]
    }
    
    result = engine.conduct_scaffolding_interaction(concept_map)
    
    if result["status"] == "success":
        print("✓ Scaffolding interaction initiated successfully")
        print(f"  Type: {result['scaffolding_type']}")
        print(f"  Intensity: {result['scaffolding_intensity']}")
        
        # Test that it generates initial prompts
        prompts = result["interaction_results"]["prompts"]
        if prompts and len(prompts) > 0:
            print(f"✓ Initial prompt generated: {prompts[0][:100]}...")
        else:
            print("✗ No initial prompt generated")
        
        # Simulate user response
        user_response = "I think the main strategy is to focus on market adaptation"
        response_result = engine.process_learner_response(user_response)
        
        if response_result["status"] == "success" and response_result.get("needs_follow_up"):
            print("✓ Follow-up required after user response")
            print(f"  Follow-up: {response_result['follow_up'][:100]}...")
        else:
            print("✗ No follow-up generated for user response")
    else:
        print(f"✗ Failed to initiate scaffolding: {result.get('message')}")

def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("ENHANCED INTERACTION PATTERNS TEST SUITE")
    print("="*60)
    
    test_pattern_detection()
    test_pattern_handlers()
    test_critical_pattern_5_fix()
    test_mandatory_interaction()
    
    print("\n" + "="*60)
    print("TEST SUITE COMPLETED")
    print("="*60)
    print("\nSummary:")
    print("- Pattern detection: Tests how well the system identifies different interaction patterns")
    print("- Pattern handlers: Tests appropriate responses for each pattern")
    print("- Pattern 5 fix: Tests that generic affirmations are avoided")
    print("- Mandatory interaction: Tests that at least one exchange is required per round")

if __name__ == "__main__":
    main()
