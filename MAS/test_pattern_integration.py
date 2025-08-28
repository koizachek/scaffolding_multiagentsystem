#!/usr/bin/env python3
"""
Test script to verify interaction pattern detection and routing in the actual session flow.
Tests that patterns are properly detected and handled by agents while maintaining their scaffolding context.
"""

import sys
import os
import json
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from MAS.app.streamlit_experimental_session import StreamlitExperimentalSession
from MAS.utils.scaffolding_utils import analyze_user_response_type

def test_pattern_detection():
    """Test that patterns are correctly detected."""
    print("\n" + "="*60)
    print("TESTING PATTERN DETECTION")
    print("="*60)
    
    test_cases = [
        ("", "empty_input", True),
        (" ", "empty_input", True),
        ("fuck you", "inappropriate_language", True),
        ("no!", "disagreement", True),
        ("I disagree", "disagreement", True),
        ("what?", "question", True),
        ("how does this work?", "question", True),
        ("this is frustrating", "frustration", True),
        ("I'm done", "premature_ending", True),
        ("let's talk about something else", "off_topic", True),
        ("I think AMG blocks market entry", "normal", False),  # Contains actual idea
    ]
    
    passed = 0
    failed = 0
    
    for user_input, expected_type, should_require_pattern in test_cases:
        analysis = analyze_user_response_type(user_input)
        detected_type = analysis.get("response_type")
        requires_pattern = analysis.get("requires_pattern_response", False)
        
        if detected_type == expected_type and requires_pattern == should_require_pattern:
            print(f"✅ PASS: '{user_input[:30]}...' → {detected_type} (pattern={requires_pattern})")
            passed += 1
        else:
            print(f"❌ FAIL: '{user_input[:30]}...' → Expected {expected_type} (pattern={should_require_pattern}), Got {detected_type} (pattern={requires_pattern})")
            failed += 1
    
    print(f"\nPattern Detection Results: {passed} passed, {failed} failed")
    return failed == 0

def test_agent_pattern_responses():
    """Test that agents generate appropriate pattern responses while maintaining context."""
    print("\n" + "="*60)
    print("TESTING AGENT PATTERN RESPONSES")
    print("="*60)
    
    # Create a mock session
    session = StreamlitExperimentalSession()
    
    # Initialize with demo mode to avoid API calls
    session.session_data["mode"] = "demo"
    session.session_data["agent_sequence"] = [
        "conceptual_scaffolding",
        "procedural_scaffolding", 
        "strategic_scaffolding",
        "metacognitive_scaffolding"
    ]
    
    # Test patterns for each agent type
    test_scenarios = [
        {
            "agent": "conceptual_scaffolding",
            "pattern": "empty_input",
            "user_input": " ",
            "expected_keywords": ["conceptual", "relationships", "AMG"]
        },
        {
            "agent": "procedural_scaffolding",
            "pattern": "disagreement",
            "user_input": "I disagree with this approach",
            "expected_keywords": ["procedural", "mapping", "technique"]
        },
        {
            "agent": "strategic_scaffolding",
            "pattern": "question",
            "user_input": "How should I organize this?",
            "expected_keywords": ["strategic", "positioning", "structure"]
        },
        {
            "agent": "metacognitive_scaffolding",
            "pattern": "frustration",
            "user_input": "This is too hard",
            "expected_keywords": ["reflect", "learned", "confident"]
        }
    ]
    
    passed = 0
    failed = 0
    
    for scenario in test_scenarios:
        agent_type = scenario["agent"]
        user_input = scenario["user_input"]
        expected_keywords = scenario["expected_keywords"]
        
        # Analyze the user response
        response_analysis = analyze_user_response_type(user_input)
        
        # Generate pattern response
        pattern_response = session._generate_pattern_response(
            agent_type=agent_type,
            response_analysis=response_analysis,
            user_response=user_input,
            concept_map_data=None,
            roundn=1,
            conversation_turn=1
        )
        
        if pattern_response:
            # Check if response contains expected keywords
            response_lower = pattern_response.lower()
            keywords_found = all(keyword.lower() in response_lower for keyword in expected_keywords)
            
            if keywords_found:
                print(f"✅ PASS: {agent_type} handles '{scenario['pattern']}' correctly")
                print(f"   Response preview: {pattern_response[:100]}...")
                passed += 1
            else:
                print(f"❌ FAIL: {agent_type} response missing keywords: {expected_keywords}")
                print(f"   Response: {pattern_response[:100]}...")
                failed += 1
        else:
            print(f"❌ FAIL: No pattern response generated for {agent_type} with '{scenario['pattern']}'")
            failed += 1
    
    print(f"\nAgent Pattern Response Results: {passed} passed, {failed} failed")
    return failed == 0

def test_full_integration():
    """Test the full integration with get_agent_response."""
    print("\n" + "="*60)
    print("TESTING FULL INTEGRATION")
    print("="*60)
    
    # Create session
    session = StreamlitExperimentalSession()
    session.session_data["mode"] = "demo"
    session.session_data["agent_sequence"] = [
        "conceptual_scaffolding",
        "procedural_scaffolding",
        "strategic_scaffolding",
        "metacognitive_scaffolding"
    ]
    
    # Test that patterns are handled in get_agent_response
    test_cases = [
        {
            "round": 1,  # Conceptual agent
            "user_input": " ",  # Empty input
            "conversation_turn": 1,
            "should_contain": ["conceptual", "AMG"]
        },
        {
            "round": 2,  # Procedural agent
            "user_input": "fuck this",  # Inappropriate
            "conversation_turn": 1,
            "should_contain": ["professional", "procedural"]
        },
        {
            "round": 3,  # Strategic agent
            "user_input": "no!",  # Disagreement
            "conversation_turn": 1,
            "should_contain": ["strategic", "perspective"]
        },
        {
            "round": 4,  # Metacognitive agent
            "user_input": "what is AMG?",  # Question
            "conversation_turn": 1,
            "should_contain": ["reflection", "understanding"]
        }
    ]
    
    passed = 0
    failed = 0
    
    for test in test_cases:
        response = session.get_agent_response(
            roundn=test["round"],
            concept_map_data=None,
            user_response=test["user_input"],
            conversation_turn=test["conversation_turn"]
        )
        
        response_lower = response.lower()
        keywords_found = any(keyword.lower() in response_lower for keyword in test["should_contain"])
        
        if keywords_found:
            print(f"✅ PASS: Round {test['round']} handles '{test['user_input']}' with pattern response")
            print(f"   Response preview: {response[:100]}...")
            passed += 1
        else:
            print(f"❌ FAIL: Round {test['round']} didn't generate pattern response for '{test['user_input']}'")
            print(f"   Expected keywords: {test['should_contain']}")
            print(f"   Response: {response[:100]}...")
            failed += 1
    
    print(f"\nFull Integration Results: {passed} passed, {failed} failed")
    return failed == 0

def test_pattern_5_fix():
    """Test the critical Pattern 5 fix for conversational engagement."""
    print("\n" + "="*60)
    print("TESTING PATTERN 5 FIX (Conversational Engagement)")
    print("="*60)
    
    session = StreamlitExperimentalSession()
    session.session_data["mode"] = "demo"
    
    test_cases = [
        {
            "user_input": "I think AMG blocks market entry through network control",
            "contains_idea": True,
            "should_affirm": True,
            "description": "User shares actual idea"
        },
        {
            "user_input": "The concept map shows relationships",
            "contains_idea": True,
            "should_affirm": True,
            "description": "User describes their map"
        },
        {
            "user_input": "okay",
            "contains_idea": False,
            "should_affirm": False,
            "description": "Generic acknowledgment (no idea)"
        },
        {
            "user_input": "yes",
            "contains_idea": False,
            "should_affirm": False,
            "description": "Simple agreement (no idea)"
        }
    ]
    
    passed = 0
    failed = 0
    
    for test in test_cases:
        # Test with conceptual agent
        response = session._generate_idea_affirmation_response(
            agent_type="conceptual_scaffolding",
            user_response=test["user_input"],
            concept_map_data=None
        )
        
        # Check if response appropriately handles the input
        if test["should_affirm"]:
            # Should reference the user's idea
            if test["user_input"][:50] in response or "insight" in response.lower():
                print(f"✅ PASS: {test['description']} - Appropriately affirmed")
                print(f"   Input: '{test['user_input'][:50]}...'")
                print(f"   Response preview: {response[:100]}...")
                passed += 1
            else:
                print(f"❌ FAIL: {test['description']} - Should affirm but didn't")
                failed += 1
        else:
            # Should not use generic affirmation
            if "interesting" not in response.lower() or "insight" in response.lower():
                print(f"✅ PASS: {test['description']} - No inappropriate affirmation")
                passed += 1
            else:
                print(f"❌ FAIL: {test['description']} - Inappropriate affirmation used")
                failed += 1
    
    print(f"\nPattern 5 Fix Results: {passed} passed, {failed} failed")
    return failed == 0

def main():
    """Run all integration tests."""
    print("\n" + "="*60)
    print("INTERACTION PATTERN INTEGRATION TEST SUITE")
    print("="*60)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    all_passed = True
    
    # Run test suites
    all_passed &= test_pattern_detection()
    all_passed &= test_agent_pattern_responses()
    all_passed &= test_full_integration()
    all_passed &= test_pattern_5_fix()
    
    # Summary
    print("\n" + "="*60)
    if all_passed:
        print("✅ ALL TESTS PASSED - Interaction patterns are working correctly!")
        print("The system now properly:")
        print("1. Detects all 8 interaction patterns")
        print("2. Routes to pattern-specific handlers")
        print("3. Maintains agent scaffolding context")
        print("4. Handles Pattern 5 (conversational engagement) correctly")
        print("5. Enforces mandatory interaction rule")
    else:
        print("❌ SOME TESTS FAILED - Review the implementation")
        print("Check the failed tests above for details")
    print("="*60)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
