"""
Create Directories Script

This script creates the necessary directories for the Multi-Agent Scaffolding System.
"""

import os
from pathlib import Path

def create_directories():
    """
    Create the necessary directories for the project.
    """
    # Get the project root directory
    root_dir = Path(__file__).parent
    
    # Define directories to create
    directories = [
        "logs",
        "examples/output",
        "examples/output/sample_data",
        "examples/output/batch_processing",
        "examples/output/longitudinal_study",
        "examples/output/ablation_study"
    ]
    
    # Create directories
    for directory in directories:
        dir_path = root_dir / directory
        os.makedirs(dir_path, exist_ok=True)
        print(f"Created directory: {dir_path}")
    
    print("All directories created successfully.")

if __name__ == "__main__":
    create_directories()
