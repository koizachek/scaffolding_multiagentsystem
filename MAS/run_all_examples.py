"""
Run All Examples Script

This script runs all the example scripts in sequence.
"""

import os
import sys
import time
import importlib.util
from pathlib import Path

def import_module_from_path(module_name, file_path):
    """
    Import a module from a file path.
    
    Args:
        module_name: Name to give the module
        file_path: Path to the module file
        
    Returns:
        Imported module
    """
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

def run_example(example_name, file_path):
    """
    Run an example script.
    
    Args:
        example_name: Name of the example
        file_path: Path to the example script
    """
    print("\n" + "=" * 80)
    print(f"Running example: {example_name}")
    print("=" * 80 + "\n")
    
    # Import and run the example
    module = import_module_from_path(f"example_{example_name}", file_path)
    module.main()
    
    print("\n" + "-" * 80)
    print(f"Example {example_name} completed.")
    print("-" * 80 + "\n")
    
    # Add a small delay between examples
    time.sleep(1)

def main():
    """
    Main function to run all examples.
    """
    print("Multi-Agent Scaffolding System - Run All Examples")
    
    # Get the project root directory
    root_dir = Path(__file__).parent
    
    # Create necessary directories
    create_dirs_script = root_dir / "create_directories.py"
    create_dirs_module = import_module_from_path("create_directories", create_dirs_script)
    create_dirs_module.create_directories()
    
    # Define examples to run
    examples = [
        ("load_sample_data", "examples/load_sample_data.py"),
        ("programmatic_usage", "examples/programmatic_usage.py"),
        ("ablation_study", "examples/ablation_study.py"),
        ("batch_processing", "examples/batch_processing.py"),
        ("longitudinal_study", "examples/longitudinal_study.py")
    ]
    
    # Run each example
    for example_name, example_path in examples:
        example_script = root_dir / example_path
        run_example(example_name, example_script)
    
    print("\nAll examples completed successfully.")

if __name__ == "__main__":
    main()
