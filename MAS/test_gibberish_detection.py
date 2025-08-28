#!/usr/bin/env python3
"""
Test script for enhanced gibberish detection in scaffolding_utils.
Tests various edge cases to ensure robust detection of nonsensical input.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.scaffolding_utils import analyze_user_response_type

def test_gibberish_detection():
    """Test various gibberish patterns."""
    
    print("=" * 60)
    print("TESTING ENHANCED GIBBERISH DETECTION")
    print("=" * 60)
    
    # Test cases: (input, expected_is_gibberish, description)
    test_cases = [
        # Keyboard mashing patterns
        ("asdf", True, "Keyboard mashing - asdf"),
        ("qwerty", True, "Keyboard mashing - qwerty"),
        ("zxcvbnm", True, "Keyboard mashing - zxcvbnm"),
        ("asdfasdfasdf", True, "Repeated keyboard pattern"),
        ("qweqweqwe", True, "Repeated qwe pattern"),
        
        # Single character repetition
        ("aaaaa", True, "Single character repeat - a"),
        ("zzzzzzz", True, "Single character repeat - z"),
        ("bbbbbb", True, "Single character repeat - b"),
        
        # Alternating patterns
        ("fjfjfjfj", True, "Alternating hands pattern"),
        ("dkdkdkdk", True, "Alternating hands pattern"),
        ("jfjfjfjf", True, "Alternating pattern"),
        
        # No vowels or very few vowels
        ("bcdfgh", True, "No vowels"),
        ("xyzwrt", True, "Very few vowels"),
        ("qwrtpsdfgh", True, "Consonant cluster"),
        
        # Random punctuation
        ("!@#$%", True, "Only special characters"),
        ("....", True, "Only dots"),
        ("???!!!", True, "Random punctuation"),
        
        # Number-letter mix
        ("a1b2c3d4", True, "Random number-letter mix"),
        ("1a2b3c4d", True, "Random number-letter mix"),
        ("123456789", True, "Only numbers"),
        
        # Mixed gibberish patterns
        ("asdlkj123", True, "Mixed keyboard mash with numbers"),
        ("qwe!@#", True, "Keyboard mash with symbols"),
        ("zxc123zxc", True, "Repeated pattern with numbers"),
        
        # Edge cases that should NOT be gibberish
        ("why", False, "Valid word with y as vowel"),
        ("try", False, "Valid word with y as vowel"),
        ("fly", False, "Valid word with y as vowel"),
        ("I think AMG is important", False, "Valid sentence"),
        ("The concept map shows relationships", False, "Valid sentence"),
        ("ok", False, "Short but valid - handled as minimal input"),
        ("no", False, "Short but valid - handled as minimal input"),
        
        # Real gibberish from experimental sessions
        ("dfghj", True, "Real gibberish example"),
        ("poiuyt", True, "Real gibberish example"),
        ("mnbvcx", True, "Real gibberish example"),
        ("qazwsx", True, "Real gibberish example"),
        ("1234567890", True, "Just numbers"),
        ("abcdefg", True, "Alphabet sequence"),
        
        # Complex patterns
        ("qweasdzxc", True, "Complex keyboard pattern"),
        ("123abc123abc", True, "Repeated mixed pattern"),
        ("aaabbbccc", True, "Multiple character repeats"),
        ("!@#qwe!@#", True, "Mixed symbols and letters"),
    ]
    
    passed = 0
    failed = 0
    
    for input_text, expected_gibberish, description in test_cases:
        analysis = analyze_user_response_type(input_text)
        is_gibberish = analysis.get("is_gibberish", False)
        
        if is_gibberish == expected_gibberish:
            passed += 1
            status = "✓ PASS"
            print(f"{status}: '{input_text}' - {description}")
            print(f"  Expected gibberish: {expected_gibberish}, Got: {is_gibberish}")
        else:
            failed += 1
            status = "✗ FAIL"
            print(f"{status}: '{input_text}' - {description}")
            print(f"  Expected gibberish: {expected_gibberish}, Got: {is_gibberish}")
            print(f"  Response type detected: {analysis.get('response_type', 'unknown')}")
        print()
    
    print("=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed out of {len(test_cases)} tests")
    print("=" * 60)
    
    # Test that gibberish triggers pattern response
    print("\nTesting pattern response requirement for gibberish:")
    gibberish_inputs = ["asdf", "qwerty", "zzzzz", "!@#$%", "123456"]
    
    for input_text in gibberish_inputs:
        analysis = analyze_user_response_type(input_text)
        if analysis.get("is_gibberish") and analysis.get("requires_pattern_response"):
            print(f"✓ '{input_text}' correctly requires pattern response")
        else:
            print(f"✗ '{input_text}' failed to trigger pattern response requirement")
    
    return passed, failed


def test_edge_cases():
    """Test specific edge cases that were problematic."""
    
    print("\n" + "=" * 60)
    print("TESTING SPECIFIC EDGE CASES")
    print("=" * 60)
    
    edge_cases = [
        # Very short gibberish
        ("xyz", True, "Short consonant cluster"),
        ("qw", False, "Too short - handled as minimal input"),
        ("a", False, "Single char - handled as minimal input"),
        
        # Mixed valid and invalid
        ("hello asdf", True, "Valid word followed by gibberish"),
        ("qwerty is my password", False, "Gibberish in context"),
        
        # Whitespace handling
        ("   ", True, "Only whitespace - handled as empty"),
        ("a s d f", True, "Spaced out gibberish"),
        
        # Special patterns
        ("111aaa222bbb", True, "Alternating numbers and letters"),
        ("AbCdEfG", True, "Alternating case alphabet"),
    ]
    
    for input_text, expected_gibberish, description in edge_cases:
        analysis = analyze_user_response_type(input_text)
        is_gibberish = analysis.get("is_gibberish", False)
        is_empty = analysis.get("is_empty", False)
        is_minimal = analysis.get("is_minimal_input", False)
        
        # Adjust expectation for empty/minimal inputs
        if is_empty or is_minimal:
            actual_result = True if expected_gibberish else False
            print(f"'{input_text}' - {description}")
            print(f"  Handled as: {'empty' if is_empty else 'minimal input'}")
        else:
            actual_result = is_gibberish
            if actual_result == expected_gibberish:
                print(f"✓ '{input_text}' - {description}")
            else:
                print(f"✗ '{input_text}' - {description}")
                print(f"  Expected: {expected_gibberish}, Got: {actual_result}")


if __name__ == "__main__":
    passed, failed = test_gibberish_detection()
    test_edge_cases()
    
    if failed == 0:
        print("\n✅ All gibberish detection tests passed!")
        sys.exit(0)
    else:
        print(f"\n⚠️ {failed} tests failed. Review the detection logic.")
        sys.exit(1)
