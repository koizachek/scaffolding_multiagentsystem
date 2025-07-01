"""
Command Line Interface

This module provides a command-line interface for the multi-agent scaffolding system.
"""

import argparse
import json
import logging
import os
import sys
from typing import Dict, List, Any, Optional

from MAS.system import MultiAgentScaffoldingSystem

logger = logging.getLogger(__name__)

def setup_argparse() -> argparse.ArgumentParser:
    """
    Set up the argument parser for the CLI.
    
    Returns:
        The configured argument parser
    """
    parser = argparse.ArgumentParser(
        description="Multi-Agent Scaffolding System for Concept Mapping"
    )
    
    parser.add_argument(
        "--config", 
        type=str, 
        default="config.json",
        help="Path to the configuration file"
    )
    
    parser.add_argument(
        "--output-dir", 
        type=str, 
        default="output",
        help="Directory for output files"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Process concept map command
    process_parser = subparsers.add_parser(
        "process", 
        help="Process a concept map PDF"
    )
    process_parser.add_argument(
        "pdf_path", 
        type=str,
        help="Path to the concept map PDF"
    )
    
    # Upload material command
    upload_parser = subparsers.add_parser(
        "upload", 
        help="Upload a learning material"
    )
    upload_parser.add_argument(
        "file_path", 
        type=str,
        help="Path to the file to upload"
    )
    upload_parser.add_argument(
        "--type", 
        type=str, 
        default="pdf",
        help="Type of material (pdf, text, etc.)"
    )
    upload_parser.add_argument(
        "--name", 
        type=str, 
        default=None,
        help="Name of the material (defaults to filename)"
    )
    
    # Finalize session command
    subparsers.add_parser(
        "finalize", 
        help="Finalize the session and generate summary feedback"
    )
    
    # Configure system command
    configure_parser = subparsers.add_parser(
        "configure", 
        help="Configure the system"
    )
    configure_parser.add_argument(
        "--df1", 
        type=str, 
        choices=["enable", "disable"],
        help="Enable/disable learner profiling (DF1)"
    )
    configure_parser.add_argument(
        "--df2", 
        type=str, 
        choices=["enable", "disable"],
        help="Enable/disable scaffolding (DF2)"
    )
    configure_parser.add_argument(
        "--df3", 
        type=str, 
        choices=["enable", "disable"],
        help="Enable/disable example map (DF3)"
    )
    configure_parser.add_argument(
        "--df4", 
        type=str, 
        choices=["enable", "disable"],
        help="Enable/disable content ingestion (DF4)"
    )
    configure_parser.add_argument(
        "--max-rounds", 
        type=int,
        help="Maximum number of rounds"
    )
    
    # Interactive mode command
    subparsers.add_parser(
        "interactive", 
        help="Start interactive mode"
    )
    
    return parser

def process_concept_map(system: MultiAgentScaffoldingSystem, pdf_path: str) -> None:
    """
    Process a concept map PDF.
    
    Args:
        system: The multi-agent scaffolding system
        pdf_path: Path to the concept map PDF
    """
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found: {pdf_path}")
        return
    
    print(f"Processing concept map: {pdf_path}")
    result = system.process_concept_map(pdf_path)
    
    if result.get("status") == "error":
        print(f"Error: {result.get('message')}")
        return
    
    # Print feedback from agents
    print("\n=== Feedback ===\n")
    
    responses = result.get("agent_responses", {})
    for agent_type, response in responses.items():
        if response:
            print(f"--- {agent_type.replace('_', ' ').title()} ---\n")
            print(response)
            print()
    
    # Print session state summary
    session_state = system.get_session_state()
    print(f"\nRound {session_state['current_round']} of {session_state['max_rounds']} completed.")
    
    if session_state["current_round"] >= session_state["max_rounds"]:
        print("\nAll rounds completed. Use 'finalize' command to generate summary feedback.")

def upload_material(system: MultiAgentScaffoldingSystem, 
                   file_path: str, 
                   material_type: str, 
                   material_name: Optional[str] = None) -> None:
    """
    Upload a learning material.
    
    Args:
        system: The multi-agent scaffolding system
        file_path: Path to the file to upload
        material_type: Type of material
        material_name: Name of the material
    """
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        return
    
    # Use filename if name not provided
    if not material_name:
        material_name = os.path.basename(file_path)
    
    print(f"Uploading material: {material_name} ({material_type})")
    result = system.process_material_upload(file_path, material_type, material_name)
    
    if result.get("status") == "error":
        print(f"Error: {result.get('message')}")
        return
    
    print(f"Material uploaded: {material_name}")
    
    # Print feedback from agents if any
    responses = result.get("agent_responses", {})
    if responses:
        print("\n=== Feedback ===\n")
        
        for agent_type, response in responses.items():
            if response:
                print(f"--- {agent_type.replace('_', ' ').title()} ---\n")
                print(response)
                print()

def finalize_session(system: MultiAgentScaffoldingSystem) -> None:
    """
    Finalize the session and generate summary feedback.
    
    Args:
        system: The multi-agent scaffolding system
    """
    print("Finalizing session...")
    result = system.finalize_session()
    
    if result.get("status") == "error":
        print(f"Error: {result.get('message')}")
        return
    
    # Print summary feedback from agents
    print("\n=== Summary Feedback ===\n")
    
    responses = result.get("agent_responses", {})
    for agent_type, response in responses.items():
        if response:
            print(f"--- {agent_type.replace('_', ' ').title()} ---\n")
            print(response)
            print()
    
    print("\nSession finalized. Log files and visualizations saved to output directory.")

def configure_system(args: argparse.Namespace) -> Dict[str, Any]:
    """
    Configure the system based on command-line arguments.
    
    Args:
        args: Command-line arguments
        
    Returns:
        Updated configuration
    """
    # Load existing configuration if available
    config_path = args.config
    config = {}
    
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
        except Exception as e:
            print(f"Error loading configuration: {e}")
    
    # Ensure design_features section exists
    if "design_features" not in config:
        config["design_features"] = {}
    
    # Update design features
    if args.df1:
        config["design_features"]["df1_learner_profiling"] = (args.df1 == "enable")
    
    if args.df2:
        config["design_features"]["df2_scaffolding"] = (args.df2 == "enable")
    
    if args.df3:
        config["design_features"]["df3_example_map"] = (args.df3 == "enable")
    
    if args.df4:
        config["design_features"]["df4_content_ingestion"] = (args.df4 == "enable")
    
    # Update max rounds
    if args.max_rounds:
        config["max_rounds"] = args.max_rounds
    
    # Set output directory
    config["output_dir"] = args.output_dir
    
    # Save configuration
    try:
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"Configuration saved to {config_path}")
    except Exception as e:
        print(f"Error saving configuration: {e}")
    
    return config

def interactive_mode(system: MultiAgentScaffoldingSystem) -> None:
    """
    Start interactive mode.
    
    Args:
        system: The multi-agent scaffolding system
    """
    print("Starting interactive mode. Type 'help' for available commands, 'exit' to quit.")
    
    # Check if there's a pending reflection
    session_state = system.get_session_state()
    if session_state.get("pending_reflection", False):
        print("\nYou have a pending reflection. Please provide your thoughts:")
        response = input("> ")
        
        # Process user response
        result = system.process_user_response(response)
        
        if result.get("status") == "error":
            print(f"Error: {result.get('message')}")
        else:
            print(result.get("response", "Thank you for your reflection."))
    
    while True:
        try:
            command = input("\nCommand: ").strip()
            
            if command == "exit":
                print("Exiting interactive mode.")
                break
            
            elif command == "help":
                print("\nAvailable commands:")
                print("  process <pdf_path>                - Process a concept map PDF")
                print("  upload <file_path> [type] [name]  - Upload a learning material")
                print("  respond <text>                    - Respond to a scaffolding prompt")
                print("  finalize                          - Finalize the session")
                print("  status                            - Show session status")
                print("  config                            - Show current configuration")
                print("  help                              - Show this help message")
                print("  exit                              - Exit interactive mode")
            
            elif command.startswith("process "):
                pdf_path = command[8:].strip()
                process_concept_map(system, pdf_path)
                
                # Check if there's a pending reflection
                session_state = system.get_session_state()
                if session_state.get("pending_reflection", False):
                    print("\nPlease provide your reflection on the feedback:")
                    response = input("> ")
                    
                    # Process user response
                    result = system.process_user_response(response)
                    
                    if result.get("status") == "error":
                        print(f"Error: {result.get('message')}")
                    else:
                        print(result.get("response", "Thank you for your reflection."))
            
            elif command.startswith("upload "):
                parts = command[7:].strip().split()
                file_path = parts[0] if parts else ""
                material_type = parts[1] if len(parts) > 1 else "pdf"
                material_name = parts[2] if len(parts) > 2 else None
                
                if file_path:
                    upload_material(system, file_path, material_type, material_name)
                else:
                    print("Error: File path required")
            
            elif command.startswith("respond "):
                response_text = command[8:].strip()
                
                if not response_text:
                    print("Error: Response text required")
                    continue
                
                # Process user response
                result = system.process_user_response(response_text)
                
                if result.get("status") == "error":
                    print(f"Error: {result.get('message')}")
                else:
                    print(result.get("response", "Thank you for your response."))
            
            elif command == "finalize":
                finalize_session(system)
            
            elif command == "status":
                session_state = system.get_session_state()
                print("\nSession Status:")
                print(f"  Current round: {session_state['current_round']} of {session_state['max_rounds']}")
                print(f"  Active design features: {session_state['active_design_features']}")
                print(f"  Uploaded materials: {len(session_state['uploaded_materials'])}")
                print(f"  Pending reflection: {session_state.get('pending_reflection', False)}")
                
                if session_state.get("learner_profile"):
                    print("\nLearner Profile:")
                    for key, value in session_state["learner_profile"].items():
                        print(f"  {key}: {value}")
                
                if session_state.get("zpd_estimate"):
                    print("\nZPD Estimate:")
                    for key, value in session_state["zpd_estimate"].items():
                        print(f"  {key}: {value}")
            
            elif command == "config":
                config = system.get_config()
                print("\nCurrent Configuration:")
                print(json.dumps(config, indent=2))
            
            else:
                print(f"Unknown command: {command}")
                print("Type 'help' for available commands.")
        
        except KeyboardInterrupt:
            print("\nExiting interactive mode.")
            break
        
        except Exception as e:
            print(f"Error: {e}")

def main() -> None:
    """
    Main entry point for the CLI.
    """
    parser = setup_argparse()
    args = parser.parse_args()
    
    # Configure system if requested
    if args.command == "configure":
        configure_system(args)
        return
    
    # Create system
    try:
        system = MultiAgentScaffoldingSystem(args.config)
        
        # Update output directory in system config
        system.config["output_dir"] = args.output_dir
        
    except Exception as e:
        print(f"Error initializing system: {e}")
        return
    
    # Process command
    if args.command == "process":
        process_concept_map(system, args.pdf_path)
    
    elif args.command == "upload":
        upload_material(system, args.file_path, args.type, args.name)
    
    elif args.command == "finalize":
        finalize_session(system)
    
    elif args.command == "interactive":
        interactive_mode(system)
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
