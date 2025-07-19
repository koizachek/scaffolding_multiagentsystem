"""
Mermaid.js Parser

This module provides functionality to parse Mermaid.js graph syntax
into the internal concept map format used by the scaffolding system.
"""

import re
import logging
from typing import Dict, List, Any, Tuple, Optional

logger = logging.getLogger(__name__)

class MermaidParser:
    """
    Parser for converting Mermaid.js graph syntax to internal concept map format.
    """
    
    def __init__(self):
        """Initialize the Mermaid parser."""
        # Regular expressions for parsing Mermaid syntax
        self.node_pattern = re.compile(r'([A-Za-z0-9_]+)\[([^\]]+)\]')
        self.edge_pattern = re.compile(r'([A-Za-z0-9_]+)\s*-->\s*([A-Za-z0-9_]+)')
        self.edge_with_label_pattern = re.compile(r'([A-Za-z0-9_]+)\s*--\s*([^-]+)\s*-->\s*([A-Za-z0-9_]+)')
        self.edge_with_pipe_label_pattern = re.compile(r'([A-Za-z0-9_]+)\s*-->\s*\|([^|]+)\|\s*([A-Za-z0-9_]+)')
        
        logger.info("Mermaid parser initialized")
    
    def parse_mermaid_to_concept_map(self, mermaid_text: str) -> Dict[str, Any]:
        """
        Parse Mermaid.js graph syntax to internal concept map format.
        
        Args:
            mermaid_text: Mermaid.js graph syntax
            
        Returns:
            Concept map in internal format
        """
        logger.info("Parsing Mermaid.js syntax to concept map")
        
        try:
            # Clean and normalize the input
            cleaned_text = self._clean_mermaid_text(mermaid_text)
            
            # Extract nodes and edges
            nodes = self._extract_nodes(cleaned_text)
            edges = self._extract_edges(cleaned_text)
            
            # Convert to internal format
            concepts = self._nodes_to_concepts(nodes)
            relationships = self._edges_to_relationships(edges, nodes)
            
            concept_map = {
                "concepts": concepts,
                "relationships": relationships,
                "mermaid_source": mermaid_text,
                "parser_metadata": {
                    "nodes_found": len(nodes),
                    "edges_found": len(edges),
                    "concepts_created": len(concepts),
                    "relationships_created": len(relationships)
                }
            }
            
            logger.info(f"Successfully parsed Mermaid: {len(concepts)} concepts, {len(relationships)} relationships")
            return concept_map
            
        except Exception as e:
            logger.error(f"Error parsing Mermaid syntax: {e}")
            # Return minimal concept map with error info
            return {
                "concepts": [],
                "relationships": [],
                "mermaid_source": mermaid_text,
                "parser_metadata": {
                    "error": str(e),
                    "nodes_found": 0,
                    "edges_found": 0,
                    "concepts_created": 0,
                    "relationships_created": 0
                }
            }
    
    def _clean_mermaid_text(self, text: str) -> str:
        """Clean and normalize Mermaid text."""
        # Remove graph declaration line
        lines = text.strip().split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            # Skip empty lines and graph declaration
            if line and not line.startswith('graph ') and not line.startswith('flowchart '):
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def _extract_nodes(self, text: str) -> Dict[str, str]:
        """
        Extract nodes from Mermaid text.
        
        Returns:
            Dictionary mapping node IDs to node labels
        """
        nodes = {}
        
        # Find explicit node definitions like A[Label]
        for match in self.node_pattern.finditer(text):
            node_id = match.group(1)
            node_label = match.group(2)
            nodes[node_id] = node_label
        
        # Also find nodes referenced in edges but not explicitly defined
        edge_matches = list(self.edge_pattern.finditer(text))
        edge_matches.extend(self.edge_with_label_pattern.finditer(text))
        edge_matches.extend(self.edge_with_pipe_label_pattern.finditer(text))
        
        for match in edge_matches:
            if len(match.groups()) >= 2:
                source_id = match.group(1)
                target_id = match.group(-1)  # Last group is always target
                
                # Add nodes if not already defined
                if source_id not in nodes:
                    nodes[source_id] = source_id  # Use ID as label if no explicit label
                if target_id not in nodes:
                    nodes[target_id] = target_id
        
        return nodes
    
    def _extract_edges(self, text: str) -> List[Dict[str, str]]:
        """
        Extract edges from Mermaid text.
        
        Returns:
            List of edge dictionaries with source, target, and optional label
        """
        edges = []
        
        # Pattern 1: A --> |label| B
        for match in self.edge_with_pipe_label_pattern.finditer(text):
            edges.append({
                "source": match.group(1),
                "target": match.group(3),
                "label": match.group(2).strip()
            })
        
        # Pattern 2: A -- label --> B
        for match in self.edge_with_label_pattern.finditer(text):
            edges.append({
                "source": match.group(1),
                "target": match.group(3),
                "label": match.group(2).strip()
            })
        
        # Pattern 3: A --> B (no label)
        for match in self.edge_pattern.finditer(text):
            # Skip if this edge was already captured with a label
            edge_text = match.group(0)
            if '|' not in edge_text and '--' not in edge_text.replace('-->', ''):
                edges.append({
                    "source": match.group(1),
                    "target": match.group(2),
                    "label": "relates to"  # Default label
                })
        
        return edges
    
    def _nodes_to_concepts(self, nodes: Dict[str, str]) -> List[Dict[str, Any]]:
        """
        Convert nodes to concept format.
        
        Args:
            nodes: Dictionary mapping node IDs to labels
            
        Returns:
            List of concept dictionaries
        """
        concepts = []
        
        # Calculate positions in a simple grid layout
        node_count = len(nodes)
        cols = max(1, int(node_count ** 0.5))
        rows = (node_count + cols - 1) // cols
        
        x_spacing = 200
        y_spacing = 150
        start_x = 100
        start_y = 100
        
        for i, (node_id, node_label) in enumerate(nodes.items()):
            row = i // cols
            col = i % cols
            
            x = start_x + col * x_spacing
            y = start_y + row * y_spacing
            
            concept = {
                "id": node_id,
                "text": node_label,
                "x": x,
                "y": y
            }
            concepts.append(concept)
        
        return concepts
    
    def _edges_to_relationships(self, edges: List[Dict[str, str]], nodes: Dict[str, str]) -> List[Dict[str, Any]]:
        """
        Convert edges to relationship format.
        
        Args:
            edges: List of edge dictionaries
            nodes: Dictionary of nodes for validation
            
        Returns:
            List of relationship dictionaries
        """
        relationships = []
        
        for i, edge in enumerate(edges):
            source_id = edge["source"]
            target_id = edge["target"]
            label = edge.get("label", "relates to")
            
            # Validate that source and target nodes exist
            if source_id in nodes and target_id in nodes:
                relationship = {
                    "id": f"r{i+1}",
                    "source": source_id,
                    "target": target_id,
                    "text": label
                }
                relationships.append(relationship)
            else:
                logger.warning(f"Skipping edge with invalid nodes: {source_id} -> {target_id}")
        
        return relationships
    
    def concept_map_to_mermaid(self, concept_map: Dict[str, Any]) -> str:
        """
        Convert internal concept map format back to Mermaid.js syntax.
        
        Args:
            concept_map: Concept map in internal format
            
        Returns:
            Mermaid.js graph syntax
        """
        concepts = concept_map.get("concepts", [])
        relationships = concept_map.get("relationships", [])
        
        mermaid_lines = ["graph TD"]
        
        # Add node definitions
        for concept in concepts:
            node_id = concept.get("id", "")
            node_text = concept.get("text", "")
            if node_id and node_text:
                mermaid_lines.append(f"    {node_id}[{node_text}]")
        
        # Add edges
        for relationship in relationships:
            source = relationship.get("source", "")
            target = relationship.get("target", "")
            text = relationship.get("text", "relates to")
            
            if source and target:
                if text and text != "relates to":
                    mermaid_lines.append(f"    {source} --> |{text}| {target}")
                else:
                    mermaid_lines.append(f"    {source} --> {target}")
        
        return "\n".join(mermaid_lines)
    
    def validate_mermaid_syntax(self, mermaid_text: str) -> Tuple[bool, List[str]]:
        """
        Validate Mermaid.js syntax and return any errors.
        
        Args:
            mermaid_text: Mermaid.js graph syntax
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        try:
            # Check for graph declaration
            if not re.search(r'graph\s+(TD|TB|BT|RL|LR)', mermaid_text) and not re.search(r'flowchart\s+(TD|TB|BT|RL|LR)', mermaid_text):
                errors.append("Missing graph declaration (e.g., 'graph TD')")
            
            # Try to parse
            concept_map = self.parse_mermaid_to_concept_map(mermaid_text)
            
            # Check if parsing was successful
            if concept_map.get("parser_metadata", {}).get("error"):
                errors.append(f"Parsing error: {concept_map['parser_metadata']['error']}")
            
            # Check for minimum content
            if len(concept_map.get("concepts", [])) == 0:
                errors.append("No concepts found in the graph")
            
            return len(errors) == 0, errors
            
        except Exception as e:
            errors.append(f"Validation error: {str(e)}")
            return False, errors

# Convenience function for easy import
def parse_mermaid(mermaid_text: str) -> Dict[str, Any]:
    """
    Convenience function to parse Mermaid.js syntax.
    
    Args:
        mermaid_text: Mermaid.js graph syntax
        
    Returns:
        Concept map in internal format
    """
    parser = MermaidParser()
    return parser.parse_mermaid_to_concept_map(mermaid_text)
