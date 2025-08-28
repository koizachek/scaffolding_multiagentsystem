#!/usr/bin/env python3
"""
Verification script to test pattern detection in real usage scenarios.
This simulates actual session flow to ensure patterns are properly detected.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.scaffolding_utils import analyze_user_response_type
from app.streamlit_experimental_session import StreamlitExperimentalSession
import json
from datetime import datetime

def test_pattern_detection():
    """Test that patterns are detected correctly."""
    print("=" * 60)
    print("PATTERN DETECTION VERIFICATION")
    print("=" * 60)
    
    # Test cases representing real user inputs
    test_cases = [
        # Pattern 1: User Questions
        {
            "input": "What is AMG exactly?",
            "expected_pattern": "question",
            "expected_flag": True,
            "description": "Domain question"
        },
        {
            "input": "How do I use this concept mapping tool?",
            "expected_pattern": "question",
            "expected_flag": True,
            "description": "System question"
        },
        
        # Pattern 2: User Disagreement
        {
            "input": "I don't agree with that approach",
            "expected_pattern": "disagreement",
            "expected_flag": True,
            "description": "Disagreement"
        },
        
        # Pattern 3: Empty Input
        {
            "input": "",
            "expected_pattern": "empty_input",
            "expected_flag": True,
            "description": "Empty input"
        },
        
        # Pattern 4: Inappropriate Language
        {
            "input": "This is damn confusing",
            "expected_pattern": "inappropriate_language",
            "expected_flag": True,
            "description": "Inappropriate language"
        },
        
        # Pattern 5: Conversational with idea
        {
            "input": "I think AMG creates barriers through regulatory capture",
            "expected_pattern": "concrete_idea",
            "expected_flag": False,  # Ideas don't require pattern response
            "description": "User sharing concrete idea"
        },
        
        # Pattern 6: Off-topic
        {
            "input": "What's the weather like today?",
            "expected_pattern": "off_topic",
            "expected_flag": True,
            "description": "Off-topic question"
        },
        
        # Pattern 7: Frustration
        {
            "input": "This is too hard, I can't do this",
            "expected_pattern": "frustration",
            "expected_flag": True,
            "description": "Frustration expression"
        },
        
        # Pattern 8: Premature ending
        {
            "input": "I think I'm done here",
            "expected_pattern": "premature_ending",
            "expected_flag": True,
            "description": "Premature ending"
        },
        
        # Normal response
        {
            "input": "I've added the export strategy node",
            "expected_pattern": "normal",
            "expected_flag": False,
            "description": "Normal response"
        }
    ]
    
    print("\n1. Testing Pattern Detection:")
    print("-" * 40)
    
    passed = 0
    failed = 0
    
    for test in test_cases:
        result = analyze_user_response_type(test["input"])
        pattern = result.get("response_type", "unknown")
        flag = result.get("requires_pattern_response", False)
        
        # Check if pattern matches expected
        pattern_match = pattern == test["expected_pattern"]
        flag_match = flag == test["expected_flag"]
        
        if pattern_match and flag_match:
            status = "✅ PASS"
            passed += 1
        else:
            status = "❌ FAIL"
            failed += 1
        
        print(f"\n{test['description']}:")
        print(f"  Input: '{test['input'][:50]}...' if len(test['input']) > 50 else '{test['input']}'")
        print(f"  Expected: pattern={test['expected_pattern']}, flag={test['expected_flag']}")
        print(f"  Got: pattern={pattern}, flag={flag}")
        print(f"  {status}")
    
    print(f"\n{'-' * 40}")
    print(f"Pattern Detection Results: {passed}/{len(test_cases)} passed")
    
    return passed == len(test_cases)

def test_session_integration():
    """Test that patterns work in actual session context."""
    print("\n2. Testing Session Integration:")
    print("-" * 40)
    
    # Create a mock session
    session = StreamlitExperimentalSession()
    
    # Initialize with demo mode (no API needed)
    session.session_data["mode"] = "demo"
    session.session_data["learner_profile"] = {
        "name": "Test User",
        "unique_id": "TEST123",
        "scaffolding_level": "medium"
    }
    session.session_data["agent_sequence"] = [
        "conceptual_scaffolding",
        "procedural_scaffolding", 
        "strategic_scaffolding",
        "metacognitive_scaffolding"
    ]
    
    # Test pattern responses for each agent
    test_scenarios = [
        {
            "agent": "conceptual_scaffolding",
            "round": 1,
            "user_input": "",
            "expected_contains": "conceptual relationships"
        },
        {
            "agent": "procedural_scaffolding",
            "round": 2,
            "user_input": "How do I add nodes?",
            "expected_contains": "mapping tools"
        },
        {
            "agent": "strategic_scaffolding",
            "round": 3,
            "user_input": "I disagree with this organization",
            "expected_contains": "reorganize"
        },
        {
            "agent": "metacognitive_scaffolding",
            "round": 4,
            "user_input": "This is frustrating",
            "expected_contains": "reflect"
        }
    ]
    
    print("\nTesting agent-specific pattern responses:")
    passed = 0
    
    for scenario in test_scenarios:
        # Get agent response with pattern detection
        response = session.get_agent_response(
            roundn=scenario["round"],
            concept_map_data=None,
            user_response=scenario["user_input"],
            conversation_turn=1
        )
        
        # Check if response contains expected keywords
        if scenario["expected_contains"].lower() in response.lower():
            print(f"✅ {scenario['agent']}: Pattern handled correctly")
            passed += 1
        else:
            print(f"❌ {scenario['agent']}: Pattern not handled properly")
            print(f"   Expected keyword: '{scenario['expected_contains']}'")
            print(f"   Got response: '{response[:100]}...'")
    
    print(f"\n{'-' * 40}")
    print(f"Session Integration Results: {passed}/{len(test_scenarios)} passed")
    
    return passed == len(test_scenarios)

def test_pattern_5_fix():
    """Test that Pattern 5 (conversational engagement) is fixed."""
    print("\n3. Testing Pattern 5 Fix (Critical):")
    print("-" * 40)
    
    test_cases = [
        {
            "input": "That's interesting",
            "should_affirm": False,
            "description": "Generic response (should NOT affirm)"
        },
        {
            "input": "I see",
            "should_affirm": False,
            "description": "Acknowledgment (should NOT affirm)"
        },
        {
            "input": "I think AMG blocks market entry through regulatory barriers",
            "should_affirm": True,
            "description": "Concrete idea (SHOULD affirm)"
        },
        {
            "input": "The relationship between financing and joint ventures is bidirectional",
            "should_affirm": True,
            "description": "Specific insight (SHOULD affirm)"
        }
    ]
    
    passed = 0
    
    for test in test_cases:
        result = analyze_user_response_type(test["input"])
        contains_idea = result.get("contains_idea", False)
        
        if contains_idea == test["should_affirm"]:
            print(f"✅ {test['description']}: Correctly identified")
            passed += 1
        else:
            print(f"❌ {test['description']}: Incorrectly identified")
            print(f"   Expected contains_idea={test['should_affirm']}, got {contains_idea}")
    
    print(f"\n{'-' * 40}")
    print(f"Pattern 5 Fix Results: {passed}/{len(test_cases)} passed")
    
    return passed == len(test_cases)

def main():
    """Run all verification tests."""
    print("\n" + "=" * 60)
    print("RUNNING PATTERN DETECTION VERIFICATION")
    print("=" * 60)
    
    results = []
    
    # Run all tests
    results.append(("Pattern Detection", test_pattern_detection()))
    results.append(("Session Integration", test_session_integration()))
    results.append(("Pattern 5 Fix", test_pattern_5_fix()))
    
    # Summary
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL VERIFICATIONS PASSED!")
        print("The interaction patterns are working correctly in real usage.")
    else:
        print("⚠️ Some verifications failed. Please review the output above.")
    print("=" * 60)
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
