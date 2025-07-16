"""
Experimental Demo

This script demonstrates the enhanced I/O capabilities and experimental data collection
features of the multi-agent scaffolding system.
"""

import json
import logging
import os
from typing import Dict, Any

from MAS.mas_system import MultiAgentScaffoldingSystem
from MAS.core.enhanced_io_manager import create_enhanced_io_manager

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def demonstrate_enhanced_io():
    """Demonstrate the enhanced I/O capabilities."""
    print("=" * 60)
    print("ENHANCED I/O DEMONSTRATION")
    print("=" * 60)
    
    # Create system
    system = MultiAgentScaffoldingSystem("MAS/config.json")
    
    # Configure experimental I/O
    io_config = {
        "max_input_length": 1000,
        "input_timeout": 30,
        "enable_colors": True,
        "log_interactions": True
    }
    
    # Enable experimental mode
    system.enable_experimental_mode(io_config)
    
    print("\n🧪 Experimental mode enabled!")
    print("The system will now collect detailed interaction data for research purposes.\n")
    
    # Simulate a scaffolding interaction
    print("Let's simulate a concept mapping session with enhanced analysis...\n")
    
    # Create mock concept map data
    mock_concept_map = {
        "nodes": ["Photosynthesis", "Chloroplast", "Light", "CO2", "Glucose"],
        "edges": [
            {"source": "Light", "target": "Photosynthesis", "label": "enables"},
            {"source": "CO2", "target": "Photosynthesis", "label": "required for"},
            {"source": "Photosynthesis", "target": "Glucose", "label": "produces"}
        ]
    }
    
    # Update session state with mock data
    system.session_state["current_concept_map"] = mock_concept_map
    system.session_state["current_round"] = 1
    
    # Simulate user responses to different scaffolding types
    test_responses = [
        {
            "scaffolding_type": "conceptual",
            "prompt": "How do you think light and CO2 work together in photosynthesis?",
            "response": "I think light provides energy and CO2 provides carbon atoms that get combined to make glucose. The chloroplast is where this happens."
        },
        {
            "scaffolding_type": "strategic", 
            "prompt": "What strategy did you use to organize these concepts?",
            "response": "I started with the main process in the center and then added the inputs and outputs around it."
        },
        {
            "scaffolding_type": "metacognitive",
            "prompt": "How confident do you feel about your understanding of photosynthesis?",
            "response": "I feel pretty confident about the basic process, but I'm not sure about all the detailed steps that happen inside the chloroplast."
        }
    ]
    
    # Process each response and collect analysis
    for i, test_case in enumerate(test_responses, 1):
        print(f"\n--- Test Case {i}: {test_case['scaffolding_type'].title()} Scaffolding ---")
        print(f"Prompt: {test_case['prompt']}")
        print(f"Simulated Response: {test_case['response']}")
        
        # Simulate the interaction by directly calling the I/O manager
        if system.experimental_io_manager:
            context = {
                "scaffolding_type": test_case["scaffolding_type"],
                "prompt": test_case["prompt"],
                "round": system.session_state["current_round"]
            }
            
            # Analyze the response
            analysis = system.experimental_io_manager.analyzer.analyze_response(
                test_case["response"], context
            )
            
            # Log the interaction
            interaction_record = {
                "timestamp": analysis["timestamp"],
                "type": "user_input",
                "prompt": test_case["prompt"],
                "response": test_case["response"],
                "response_time": 2.5,  # Simulated response time
                "context": context,
                "analysis": analysis
            }
            
            system.experimental_io_manager.interaction_log.append(interaction_record)
            system.experimental_io_manager.session_data["interactions"].append(interaction_record)
            
            # Display key analysis results
            print(f"\n📊 Analysis Results:")
            print(f"   Word count: {analysis['metrics']['word_count']}")
            print(f"   Engagement level: {analysis['engagement_level']}")
            print(f"   Learning state: {analysis['learning_indicators']['learning_state']}")
            print(f"   Sentiment: {analysis['linguistic_features']['sentiment']}")
            
            # Show scaffolding needs
            needs = analysis['scaffolding_needs']
            max_need = max(needs.values())
            if max_need > 0:
                recommended_scaffolding = max(needs, key=needs.get)
                print(f"   Recommended next scaffolding: {recommended_scaffolding} (score: {max_need:.2f})")
    
    # Get comprehensive analysis
    print("\n" + "=" * 60)
    print("COMPREHENSIVE SESSION ANALYSIS")
    print("=" * 60)
    
    session_analysis = system.get_interaction_analysis()
    if session_analysis:
        print("\n📈 Session Summary:")
        summary = session_analysis["session_summary"]
        print(f"   Total interactions: {summary['total_interactions']}")
        print(f"   Total words: {summary['total_words']}")
        print(f"   Average words per response: {summary['avg_words_per_response']:.1f}")
        print(f"   Average response time: {summary['avg_response_time']:.2f}s")
        
        print("\n🎯 Engagement Analysis:")
        engagement = session_analysis["engagement_analysis"]
        print(f"   High engagement: {engagement['high_engagement']} interactions")
        print(f"   Medium engagement: {engagement['medium_engagement']} interactions")
        print(f"   Low engagement: {engagement['low_engagement']} interactions")
        
        print("\n🧠 Learning Analysis:")
        learning = session_analysis["learning_analysis"]
        print(f"   Progressing: {learning['progressing']} interactions")
        print(f"   Struggling: {learning['struggling']} interactions")
        print(f"   Neutral: {learning['neutral']} interactions")
        print(f"   Mixed: {learning['mixed']} interactions")
        
        print("\n🎯 Scaffolding Needs (Average Scores):")
        needs = session_analysis["scaffolding_needs"]
        for scaffolding_type, score in needs.items():
            print(f"   {scaffolding_type.title()}: {score:.3f}")
    
    # Export experimental data
    print("\n💾 Exporting experimental data...")
    export_path = system.export_experimental_data("experimental_demo_data.json")
    if export_path:
        print(f"   Data exported to: {export_path}")
        
        # Show a sample of the exported data
        with open(export_path, 'r') as f:
            exported_data = json.load(f)
        
        print(f"\n📄 Exported data contains:")
        print(f"   Session ID: {exported_data['session_id']}")
        print(f"   Start time: {exported_data['start_time']}")
        print(f"   Total interactions: {len(exported_data['interactions'])}")
        print(f"   Analysis summary: {len(exported_data['analysis_summary'])} metrics")
    
    # Disable experimental mode
    system.disable_experimental_mode()
    print("\n🔄 Experimental mode disabled. System reverted to standard I/O.")

def demonstrate_input_validation():
    """Demonstrate input validation capabilities."""
    print("\n" + "=" * 60)
    print("INPUT VALIDATION DEMONSTRATION")
    print("=" * 60)
    
    from MAS.core.enhanced_io_manager import InputValidator
    
    validator = InputValidator()
    
    test_inputs = [
        ("Valid input", "This is a normal response about photosynthesis."),
        ("Empty input", ""),
        ("Too long input", "x" * 2001),
        ("Potentially harmful", "<script>alert('test')</script>Normal text"),
        ("With JavaScript", "javascript:void(0) and some text"),
        ("Normal with HTML", "This has <b>bold</b> text which is fine")
    ]
    
    print("\n🔍 Testing input validation:")
    
    for test_name, test_input in test_inputs:
        is_valid, error_message = validator.validate_text_input(test_input)
        sanitized = validator.sanitize_input(test_input)
        
        print(f"\n   {test_name}:")
        print(f"      Input: {test_input[:50]}{'...' if len(test_input) > 50 else ''}")
        print(f"      Valid: {is_valid}")
        if not is_valid:
            print(f"      Error: {error_message}")
        print(f"      Sanitized: {sanitized[:50]}{'...' if len(sanitized) > 50 else ''}")

def demonstrate_analysis_features():
    """Demonstrate the analysis features in detail."""
    print("\n" + "=" * 60)
    print("ANALYSIS FEATURES DEMONSTRATION")
    print("=" * 60)
    
    from MAS.core.enhanced_io_manager import InteractionAnalyzer
    
    analyzer = InteractionAnalyzer()
    
    # Test different types of responses
    test_responses = [
        {
            "name": "High engagement, confident response",
            "text": "I'm really excited about this topic! I understand that photosynthesis is the process where plants convert light energy into chemical energy. The chloroplasts contain chlorophyll which captures light, and then CO2 from the air combines with water to produce glucose and oxygen. This is fascinating because it's how plants make their own food!",
            "context": {"scaffolding_type": "conceptual", "round": 1}
        },
        {
            "name": "Uncertain, struggling response", 
            "text": "I'm not sure about this. Maybe photosynthesis has something to do with light? I don't really understand how it works.",
            "context": {"scaffolding_type": "conceptual", "round": 1}
        },
        {
            "name": "Strategic thinking response",
            "text": "I organized my concept map by putting the main process in the center and then connecting the inputs and outputs. I tried to group related concepts together and use different colors for different types of relationships.",
            "context": {"scaffolding_type": "strategic", "round": 2}
        },
        {
            "name": "Metacognitive reflection",
            "text": "I feel more confident now than when I started. I realize I was confused about where exactly photosynthesis happens in the plant. Now I understand it's specifically in the chloroplasts. I think I need to learn more about the detailed chemical reactions.",
            "context": {"scaffolding_type": "metacognitive", "round": 3}
        }
    ]
    
    print("\n🔬 Analyzing different response types:")
    
    for test_case in test_responses:
        print(f"\n--- {test_case['name']} ---")
        print(f"Response: {test_case['text'][:100]}...")
        
        analysis = analyzer.analyze_response(test_case['text'], test_case['context'])
        
        print(f"\n📊 Metrics:")
        metrics = analysis['metrics']
        print(f"   Words: {metrics['word_count']}, Characters: {metrics['character_count']}")
        print(f"   Questions: {metrics['question_count']}, Exclamations: {metrics['exclamation_count']}")
        
        print(f"\n🗣️ Linguistic Features:")
        linguistic = analysis['linguistic_features']
        print(f"   Uncertainty indicators: {linguistic['uncertainty_indicators']}")
        print(f"   Confidence indicators: {linguistic['confidence_indicators']}")
        print(f"   Metacognitive language: {linguistic['metacognitive_language']}")
        print(f"   Sentiment: {linguistic['sentiment']}")
        
        print(f"\n🧠 Cognitive Indicators:")
        cognitive = analysis['cognitive_indicators']
        print(f"   Deep processing: {cognitive['deep_processing_indicators']}")
        print(f"   Conceptual understanding: {cognitive['conceptual_understanding']}")
        print(f"   Cognitive load: {cognitive['cognitive_load']}")
        
        print(f"\n📈 Learning & Engagement:")
        print(f"   Engagement level: {analysis['engagement_level']}")
        learning = analysis['learning_indicators']
        print(f"   Learning state: {learning['learning_state']}")
        print(f"   Progress indicators: {learning['progress_indicators']}")
        print(f"   Confusion indicators: {learning['confusion_indicators']}")
        
        print(f"\n🎯 Scaffolding Recommendations:")
        needs = analysis['scaffolding_needs']
        sorted_needs = sorted(needs.items(), key=lambda x: x[1], reverse=True)
        for scaffolding_type, score in sorted_needs:
            if score > 0:
                print(f"   {scaffolding_type.title()}: {score:.3f}")

def main():
    """Run the experimental demonstration."""
    print("🧪 MULTI-AGENT SCAFFOLDING SYSTEM")
    print("Enhanced I/O and Experimental Features Demo")
    print("=" * 60)
    
    try:
        # Demonstrate enhanced I/O
        demonstrate_enhanced_io()
        
        # Demonstrate input validation
        demonstrate_input_validation()
        
        # Demonstrate analysis features
        demonstrate_analysis_features()
        
        print("\n" + "=" * 60)
        print("✅ DEMONSTRATION COMPLETE")
        print("=" * 60)
        print("\nKey improvements demonstrated:")
        print("• Enhanced input validation and sanitization")
        print("• Comprehensive user response analysis")
        print("• Experimental data collection for research")
        print("• Detailed interaction logging and metrics")
        print("• Scaffolding effectiveness assessment")
        print("• Learning progress tracking")
        print("• Engagement level monitoring")
        print("• Exportable session data for analysis")
        
        print("\nThese enhancements support:")
        print("• Experimental research on scaffolding effectiveness")
        print("• Adaptive scaffolding based on user analysis")
        print("• Longitudinal learning progress studies")
        print("• User experience optimization")
        print("• Safety and security through input validation")
        
    except Exception as e:
        logger.error(f"Error in demonstration: {e}")
        print(f"\n❌ Error occurred: {e}")

if __name__ == "__main__":
    main()
