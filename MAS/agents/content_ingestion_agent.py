"""
Content Ingestion / Knowledge State Agent (DF4)

This module provides the content ingestion agent that parses and stores
the learner's current concept map and uploaded materials.
"""

import logging
from typing import Dict, List, Any, Optional, Callable

from .base_agent import BaseAgent

logger = logging.getLogger(__name__)

class ContentIngestionAgent(BaseAgent):
    """
    Content ingestion agent for the multi-agent scaffolding system.
    
    This agent continuously parses and stores the learner's current concept map
    and uploaded materials, providing context-awareness to other agents.
    """
    
    def __init__(self, 
                name: str,
                config: Dict[str, Any],
                logger_callback: Optional[Callable] = None):
        """
        Initialize the content ingestion agent.
        
        Args:
            name: Name of the agent
            config: Agent configuration
            logger_callback: Callback function for logging
        """
        super().__init__(name, "content_ingestion", config, logger_callback)
        
        # Initialize content storage
        self.current_concept_map = None
        self.previous_concept_maps = []
        self.uploaded_materials = []
        
        # Initialize content analysis
        self.content_analysis = {
            "concept_map_history": [],
            "key_concepts": set(),
            "concept_relationships": [],
            "changes_over_time": []
        }
        
        logger.info(f"Initialized content ingestion agent: {name}")
    
    def _process_impl(self, 
                     input_data: Dict[str, Any], 
                     context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input data and store/analyze content.
        
        Args:
            input_data: Input data to process
            context: Context information
            
        Returns:
            Response data with content analysis
        """
        # Extract input type
        input_type = input_data.get("type", "unknown")
        
        # Process based on input type
        if input_type == "concept_map_submission":
            return self._handle_concept_map_submission(input_data, context)
        elif input_type == "material_upload":
            return self._handle_material_upload(input_data, context)
        elif input_type == "final_round":
            return self._handle_final_round(input_data, context)
        else:
            logger.warning(f"Unknown input type: {input_type}")
            return {
                "response": None,
                "agent_type": self.agent_type,
                "status": "error"
            }
    
    def _handle_concept_map_submission(self, 
                                      input_data: Dict[str, Any], 
                                      context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle concept map submission by storing and analyzing it.
        
        Args:
            input_data: Input data containing concept map
            context: Context information
            
        Returns:
            Response data with content analysis
        """
        # Extract concept map data
        concept_map_data = input_data.get("concept_map_data")
        
        if not concept_map_data:
            return {
                "response": None,
                "agent_type": self.agent_type,
                "status": "error"
            }
        
        logger.info("Processing concept map submission")
        
        # Get session state
        session_state = context.get("session_state", {})
        
        # Get current round
        current_round = session_state.get("current_round", 0)
        
        # Store previous concept map if exists
        if self.current_concept_map:
            self.previous_concept_maps.append(self.current_concept_map)
        
        # Update current concept map
        self.current_concept_map = concept_map_data
        
        # Analyze concept map
        self._analyze_concept_map(concept_map_data, current_round)
        
        # No direct response to the user from this agent
        return {
            "response": None,
            "agent_type": self.agent_type,
            "status": "success",
            "content_analysis": self.content_analysis
        }
    
    def _handle_material_upload(self, 
                               input_data: Dict[str, Any], 
                               context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle material upload by storing and analyzing it.
        
        Args:
            input_data: Input data containing uploaded material
            context: Context information
            
        Returns:
            Response data with content analysis
        """
        # Extract material data
        material_data = input_data.get("material_data")
        material_type = input_data.get("material_type")
        material_name = input_data.get("material_name")
        
        if not material_data or not material_type:
            return {
                "response": None,
                "agent_type": self.agent_type,
                "status": "error"
            }
        
        logger.info(f"Processing material upload: {material_name} ({material_type})")
        
        # Store uploaded material
        material = {
            "name": material_name,
            "type": material_type,
            "data": material_data,
            "timestamp": input_data.get("timestamp")
        }
        
        self.uploaded_materials.append(material)
        
        # Analyze material
        self._analyze_material(material)
        
        # No direct response to the user from this agent
        return {
            "response": None,
            "agent_type": self.agent_type,
            "status": "success",
            "content_analysis": self.content_analysis
        }
    
    def _handle_final_round(self, 
                           input_data: Dict[str, Any], 
                           context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle final round by providing a summary of content changes.
        
        Args:
            input_data: Input data
            context: Context information
            
        Returns:
            Response data with content summary
        """
        logger.info("Generating content summary for final round")
        
        # Get session state
        session_state = context.get("session_state", {})
        
        # Generate content summary
        summary = self._generate_content_summary(session_state)
        
        return {
            "response": summary,
            "agent_type": self.agent_type,
            "status": "success",
            "content_analysis": self.content_analysis
        }
    
    def _analyze_concept_map(self, 
                            concept_map_data: Dict[str, Any],
                            current_round: int) -> None:
        """
        Analyze a concept map and update content analysis.
        
        Args:
            concept_map_data: Concept map data
            current_round: Current round number
        """
        # Extract nodes and edges
        nodes = concept_map_data.get("nodes", [])
        edges = concept_map_data.get("edges", [])
        
        # Update key concepts
        self.content_analysis["key_concepts"].update(nodes)
        
        # Update concept relationships
        for edge in edges:
            source = edge.get("source")
            target = edge.get("target")
            relation = edge.get("relation")
            
            if source and target:
                relationship = {
                    "source": source,
                    "target": target,
                    "relation": relation,
                    "round": current_round
                }
                
                self.content_analysis["concept_relationships"].append(relationship)
        
        # Add to concept map history
        map_snapshot = {
            "round": current_round,
            "num_concepts": len(nodes),
            "num_relationships": len(edges),
            "concepts": nodes,
            "relationships": edges
        }
        
        self.content_analysis["concept_map_history"].append(map_snapshot)
        
        # Analyze changes if not the first map
        if len(self.content_analysis["concept_map_history"]) > 1:
            self._analyze_changes(map_snapshot)
    
    def _analyze_material(self, material: Dict[str, Any]) -> None:
        """
        Analyze uploaded material and update content analysis.
        
        Args:
            material: Uploaded material data
        """
        # This is a simplified implementation
        # In a real implementation, this would extract concepts and relationships from the material
        
        # For now, just log that the material was processed
        logger.info(f"Processed material: {material.get('name')}")
    
    def _analyze_changes(self, current_map_snapshot: Dict[str, Any]) -> None:
        """
        Analyze changes between the current map and the previous map.
        
        Args:
            current_map_snapshot: Current map snapshot
        """
        # Get previous map snapshot
        previous_map_snapshot = self.content_analysis["concept_map_history"][-2]
        
        # Calculate changes
        added_concepts = set(current_map_snapshot["concepts"]) - set(previous_map_snapshot["concepts"])
        removed_concepts = set(previous_map_snapshot["concepts"]) - set(current_map_snapshot["concepts"])
        
        # Convert relationships to comparable format
        current_rels = {(rel.get("source", ""), rel.get("target", ""), rel.get("relation", "")) 
                       for rel in current_map_snapshot["relationships"] 
                       if rel.get("source") and rel.get("target")}
        
        previous_rels = {(rel.get("source", ""), rel.get("target", ""), rel.get("relation", "")) 
                        for rel in previous_map_snapshot["relationships"] 
                        if rel.get("source") and rel.get("target")}
        
        added_relationships = current_rels - previous_rels
        removed_relationships = previous_rels - current_rels
        
        # Record changes
        changes = {
            "round": current_map_snapshot["round"],
            "added_concepts": list(added_concepts),
            "removed_concepts": list(removed_concepts),
            "added_relationships": [{"source": rel[0], "target": rel[1], "relation": rel[2]} for rel in added_relationships],
            "removed_relationships": [{"source": rel[0], "target": rel[1], "relation": rel[2]} for rel in removed_relationships],
            "concept_count_change": current_map_snapshot["num_concepts"] - previous_map_snapshot["num_concepts"],
            "relationship_count_change": current_map_snapshot["num_relationships"] - previous_map_snapshot["num_relationships"]
        }
        
        self.content_analysis["changes_over_time"].append(changes)
    
    def _generate_content_summary(self, session_state: Dict[str, Any]) -> str:
        """
        Generate a summary of content changes over time.
        
        Args:
            session_state: Current session state
            
        Returns:
            Content summary text
        """
        # This is a simplified implementation
        # In a real implementation, this would provide a more detailed and personalized summary
        
        # Check if we have enough data for a meaningful summary
        if len(self.content_analysis["concept_map_history"]) <= 1:
            return (
                "Thank you for participating in this concept mapping exercise. "
                "Your concept map represents your current understanding of the topic."
            )
        
        # Get first and last map snapshots
        first_map = self.content_analysis["concept_map_history"][0]
        last_map = self.content_analysis["concept_map_history"][-1]
        
        # Calculate overall changes
        concept_growth = last_map["num_concepts"] - first_map["num_concepts"]
        relationship_growth = last_map["num_relationships"] - first_map["num_relationships"]
        
        # Generate summary
        summary = (
            "**Content Development Summary:**\n\n"
            
            f"Throughout this exercise, your concept map has evolved from {first_map['num_concepts']} concepts "
            f"and {first_map['num_relationships']} relationships to {last_map['num_concepts']} concepts and "
            f"{last_map['num_relationships']} relationships.\n\n"
        )
        
        # Add details about growth
        if concept_growth > 0 and relationship_growth > 0:
            summary += (
                f"You've added {concept_growth} new concepts and {relationship_growth} new relationships, "
                "demonstrating significant development in your understanding of the topic.\n\n"
            )
        elif concept_growth > 0:
            summary += (
                f"You've added {concept_growth} new concepts, expanding the breadth of your understanding, "
                "though you might consider developing more connections between these concepts.\n\n"
            )
        elif relationship_growth > 0:
            summary += (
                f"You've added {relationship_growth} new relationships between concepts, "
                "deepening your understanding of how these concepts connect to each other.\n\n"
            )
        else:
            summary += (
                "While the overall number of concepts and relationships hasn't increased, "
                "you've refined your map through revisions, which is an important part of the learning process.\n\n"
            )
        
        # Add details about key changes if available
        if self.content_analysis["changes_over_time"]:
            # Find the round with the most significant changes
            max_changes_round = max(
                self.content_analysis["changes_over_time"],
                key=lambda x: len(x["added_concepts"]) + len(x["added_relationships"])
            )
            
            round_num = max_changes_round["round"]
            
            summary += (
                f"The most significant development in your concept map occurred in round {round_num}, "
                f"where you added {len(max_changes_round['added_concepts'])} new concepts and "
                f"{len(max_changes_round['added_relationships'])} new relationships.\n\n"
            )
        
        # Conclude with a positive note
        summary += (
            "This progression reflects your engagement with the material and the development of your "
            "understanding through the concept mapping process. Each revision has contributed to a "
            "more comprehensive and interconnected representation of your knowledge."
        )
        
        return summary
    
    def get_current_concept_map(self) -> Dict[str, Any]:
        """
        Get the current concept map.
        
        Returns:
            The current concept map
        """
        return self.current_concept_map
    
    def get_previous_concept_maps(self) -> List[Dict[str, Any]]:
        """
        Get the previous concept maps.
        
        Returns:
            The previous concept maps
        """
        return self.previous_concept_maps
    
    def get_uploaded_materials(self) -> List[Dict[str, Any]]:
        """
        Get the uploaded materials.
        
        Returns:
            The uploaded materials
        """
        return self.uploaded_materials
    
    def get_content_analysis(self) -> Dict[str, Any]:
        """
        Get the content analysis.
        
        Returns:
            The content analysis
        """
        return self.content_analysis
