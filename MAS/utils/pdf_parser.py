"""
PDF Parser Utility

This module provides functionality to parse PDF concept maps and convert them to a JSON graph format.
"""

import os
import json
import logging
from typing import Dict, List, Optional, Tuple, Any

import pdfplumber  # type: ignore
import PyPDF2  # type: ignore

logger = logging.getLogger(__name__)

def parse_pdf_to_json(pdf_path: str, output_json_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Parse a PDF file containing a concept map and convert to JSON graph format.
    
    This is a convenience function that uses the PDFParser class.
    
    Args:
        pdf_path: Path to the PDF file
        output_json_path: Optional path to save the JSON output
        
    Returns:
        Dict containing nodes and edges in the format:
        {
            "nodes": ["ConceptA", "ConceptB", ...],
            "edges": [
                {"source": "ConceptA", "target": "ConceptB", "relation": "causes"},
                ...
            ]
        }
    """
    parser = PDFParser()
    graph_data = parser.parse_pdf(pdf_path)
    
    if output_json_path:
        parser.save_to_json(output_json_path, graph_data)
    
    return graph_data

class PDFParser:
    """
    Parser for extracting concept map data from PDF files and converting to JSON graph format.
    """
    
    def __init__(self):
        """Initialize the PDF parser."""
        self.last_parsed_file = None
        self.last_parsed_data = None
    
    def parse_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """
        Parse a PDF file containing a concept map and convert to JSON graph format.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dict containing nodes and edges in the format:
            {
                "nodes": ["ConceptA", "ConceptB", ...],
                "edges": [
                    {"source": "ConceptA", "target": "ConceptB", "relation": "causes"},
                    ...
                ]
            }
        """
        if not os.path.exists(pdf_path):
            logger.error(f"PDF file not found: {pdf_path}")
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        logger.info(f"Parsing PDF file: {pdf_path}")
        
        # This is a simplified implementation
        # In a real implementation, this would use OCR or other techniques to extract
        # concept map elements from the PDF
        
        try:
            # Extract text from PDF
            text = self._extract_text(pdf_path)
            
            # Parse text to identify concepts and relationships
            # This is a placeholder for the actual parsing logic
            nodes, edges = self._identify_concepts_and_relationships(text)
            
            # Create graph representation
            graph_data = {
                "nodes": nodes,
                "edges": edges
            }
            
            self.last_parsed_file = pdf_path
            self.last_parsed_data = graph_data
            
            logger.info(f"Successfully parsed PDF: {pdf_path}")
            logger.debug(f"Extracted graph data: {json.dumps(graph_data)}")
            
            return graph_data
            
        except Exception as e:
            logger.error(f"Error parsing PDF {pdf_path}: {str(e)}")
            raise
    
    def _extract_text(self, pdf_path: str) -> str:
        """
        Extract text content from a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text content
        """
        text = ""
        
        # Try with pdfplumber first
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""
        except Exception as e:
            logger.warning(f"pdfplumber extraction failed: {str(e)}. Trying PyPDF2...")
            
            # Fallback to PyPDF2
            try:
                with open(pdf_path, "rb") as file:
                    reader = PyPDF2.PdfReader(file)
                    for page in reader.pages:
                        text += page.extract_text() or ""
            except Exception as e2:
                logger.error(f"PyPDF2 extraction also failed: {str(e2)}")
                raise Exception(f"Failed to extract text from PDF: {str(e2)}")
        
        return text
    
    def _identify_concepts_and_relationships(self, text: str) -> Tuple[List[str], List[Dict[str, str]]]:
        """
        Parse extracted text to identify concepts and relationships.
        
        Args:
            text: Extracted text from PDF
            
        Returns:
            Tuple of (nodes, edges) where:
            - nodes is a list of concept names
            - edges is a list of dictionaries with source, target, and relation
        """
        # This is a placeholder implementation
        # In a real implementation, this would use NLP or other techniques to
        # identify concepts and relationships from the text
        
        # For demonstration purposes, we'll extract words that might be concepts
        # and create some placeholder relationships
        
        # Simple word extraction (excluding common words)
        common_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "with", "by", "of"}
        words = [word.strip(".,;:()[]{}\"'") for word in text.split()]
        potential_concepts = list(set([word for word in words if len(word) > 3 and word.lower() not in common_words]))
        
        # Limit to a reasonable number of concepts for demonstration
        nodes = potential_concepts[:min(len(potential_concepts), 10)]
        
        # Create some placeholder relationships
        edges = []
        if len(nodes) > 1:
            # Create a simple chain of relationships
            for i in range(len(nodes) - 1):
                relation_type = "relates to"  # Placeholder
                edges.append({
                    "source": nodes[i],
                    "target": nodes[i + 1],
                    "relation": relation_type
                })
        
        return nodes, edges
    
    def save_to_json(self, output_path: str, graph_data: Optional[Dict[str, Any]] = None) -> str:
        """
        Save the parsed graph data to a JSON file.
        
        Args:
            output_path: Path to save the JSON file
            graph_data: Graph data to save. If None, uses the last parsed data.
            
        Returns:
            Path to the saved JSON file
        """
        if graph_data is None:
            if self.last_parsed_data is None:
                raise ValueError("No graph data available to save")
            graph_data = self.last_parsed_data
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(graph_data, f, indent=2)
        
        logger.info(f"Saved graph data to {output_path}")
        return output_path
    
    @staticmethod
    def load_from_json(json_path: str) -> Dict[str, Any]:
        """
        Load graph data from a JSON file.
        
        Args:
            json_path: Path to the JSON file
            
        Returns:
            Graph data dictionary
        """
        if not os.path.exists(json_path):
            logger.error(f"JSON file not found: {json_path}")
            raise FileNotFoundError(f"JSON file not found: {json_path}")
        
        with open(json_path, 'r') as f:
            graph_data = json.load(f)
        
        logger.info(f"Loaded graph data from {json_path}")
        return graph_data
