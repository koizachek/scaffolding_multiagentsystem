"""
Example Map Agent (DF3)

This module provides the example map agent that holds a domain-expert "gold standard"
concept map for comparison with the learner's submission.
"""

import logging
from typing import Dict, List, Any, Optional, Callable, Set

from .base_agent import BaseAgent

logger = logging.getLogger(__name__)

class ExampleMapAgent(BaseAgent):
    """
    Example map agent for the multi-agent scaffolding system.
    
    This agent holds a domain-expert "gold standard" concept map for comparison
    with the learner's submission, providing feedback on divergences without
    revealing the ideal map directly.
    """
    
    def __init__(self, 
                name: str,
                config: Dict[str, Any],
                logger_callback: Optional[Callable] = None):
        """
        Initialize the example map agent.
        
        Args:
            name: Name of the agent
            config: Agent configuration
            logger_callback: Callback function for logging
        """
        super().__init__(name, "example_map", config, logger_callback)
        
        # Initialize example map
        self.example_map = {
            "nodes": [],
            "edges": []
        }
        
        # Initialize feedback level
        self.feedback_level = "medium"  # low, medium, high
        
        logger.info(f"Initialized example map agent: {name}")
    
    def set_example_map(self, example_map: Dict[str, Any]) -> None:
        """
        Set the example map.
        
        Args:
            example_map: Example map data
        """
        self.example_map = example_map
        logger.info(f"Set example map with {len(example_map.get('nodes', []))} nodes and {len(example_map.get('edges', []))} edges")
    
    def _process_impl(self, 
                     input_data: Dict[str, Any], 
                     context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input data and generate feedback based on comparison with the example map.
        
        Args:
            input_data: Input data to process
            context: Context information
            
        Returns:
            Response data with feedback
        """
        # Extract input type
        input_type = input_data.get("type", "unknown")
        
        # Get session state
        session_state = context.get("session_state", {})
        
        # Update feedback level based on ZPD estimate if available
        zpd_estimate = session_state.get("zpd_estimate", {})
        if zpd_estimate:
            conceptual_understanding = zpd_estimate.get("conceptual_understanding")
            if conceptual_understanding == "high":
                self.feedback_level = "high"
            elif conceptual_understanding == "low":
                self.feedback_level = "low"
            else:
                self.feedback_level = "medium"
        
        # Process based on input type
        if input_type == "concept_map_submission":
            return self._handle_concept_map_submission(input_data, context)
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
        Handle concept map submission by comparing with the example map.
        
        Args:
            input_data: Input data containing concept map
            context: Context information
            
        Returns:
            Response data with feedback
        """
        # Extract concept map data
        concept_map_data = input_data.get("concept_map_data")
        
        if not concept_map_data:
            return {
                "response": None,
                "agent_type": self.agent_type,
                "status": "error"
            }
        
        logger.info("Comparing submitted concept map with example map")
        
        # Get session state
        session_state = context.get("session_state", {})
        
        # Get current round
        current_round = session_state.get("current_round", 0)
        
        # Compare with example map and generate feedback
        feedback = self._generate_comparison_feedback(
            concept_map_data, 
            current_round,
            session_state
        )
        
        return {
            "response": feedback,
            "agent_type": self.agent_type,
            "status": "success",
            "feedback_level": self.feedback_level,
            "reasoning": f"Provided comparison feedback at {self.feedback_level} level"
        }
    
    def _handle_final_round(self, 
                           input_data: Dict[str, Any], 
                           context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle final round by providing a summary comparison.
        
        Args:
            input_data: Input data
            context: Context information
            
        Returns:
            Response data with summary comparison
        """
        logger.info("Generating summary comparison for final round")
        
        # Get session state
        session_state = context.get("session_state", {})
        
        # Extract concept map data
        concept_map_data = input_data.get("concept_map_data")
        
        if not concept_map_data:
            return {
                "response": None,
                "agent_type": self.agent_type,
                "status": "error"
            }
        
        # Generate summary comparison
        summary = self._generate_summary_comparison(concept_map_data, session_state)
        
        return {
            "response": summary,
            "agent_type": self.agent_type,
            "status": "success"
        }
    
    def _generate_comparison_feedback(self, 
                                     concept_map_data: Dict[str, Any],
                                     current_round: int,
                                     session_state: Dict[str, Any]) -> str:
        """
        Generate feedback based on comparison with the example map.
        
        Args:
            concept_map_data: Concept map data
            current_round: Current round number
            session_state: Current session state
            
        Returns:
            Comparison feedback text
        """
        # Check if example map is set
        if not self.example_map or not self.example_map.get("nodes"):
            return (
                "I'm looking at your concept map and considering how it represents the key concepts "
                "and relationships in this topic. As you continue to develop your map, think about "
                "what concepts are most central to understanding this topic and how they relate to each other."
            )
        
        # Compare the submitted map with the example map
        comparison = self._compare_maps(concept_map_data, self.example_map)
        
        # Generate feedback based on comparison and feedback level
        if self.feedback_level == "high":
            return self._generate_high_level_comparison_feedback(comparison, current_round)
        elif self.feedback_level == "medium":
            return self._generate_medium_level_comparison_feedback(comparison, current_round)
        else:  # low
            return self._generate_low_level_comparison_feedback(comparison, current_round)
    
    def _compare_maps(self, 
                     student_map: Dict[str, Any],
                     example_map: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare the student's map with the example map.
        
        Args:
            student_map: Student's concept map
            example_map: Example concept map
            
        Returns:
            Comparison results
        """
        # Extract nodes and edges
        student_nodes = set(student_map.get("nodes", []))
        example_nodes = set(example_map.get("nodes", []))
        
        student_edges = student_map.get("edges", [])
        example_edges = example_map.get("edges", [])
        
        # Convert edges to a comparable format
        student_edge_tuples = {(edge.get("source", ""), edge.get("target", ""), edge.get("relation", "")) 
                              for edge in student_edges if edge.get("source") and edge.get("target")}
        
        example_edge_tuples = {(edge.get("source", ""), edge.get("target", ""), edge.get("relation", "")) 
                              for edge in example_edges if edge.get("source") and edge.get("target")}
        
        # Find matching and missing elements
        matching_nodes = student_nodes.intersection(example_nodes)
        missing_nodes = example_nodes - student_nodes
        extra_nodes = student_nodes - example_nodes
        
        matching_edges = student_edge_tuples.intersection(example_edge_tuples)
        missing_edges = example_edge_tuples - student_edge_tuples
        extra_edges = student_edge_tuples - example_edge_tuples
        
        # Check for similar but not exact matches in relationships
        similar_edges = set()
        for s_edge in student_edge_tuples:
            for e_edge in example_edge_tuples:
                # If source and target match but relation is different
                if s_edge[0] == e_edge[0] and s_edge[1] == e_edge[1] and s_edge[2] != e_edge[2]:
                    similar_edges.add((s_edge, e_edge))
        
        # Calculate coverage percentages
        node_coverage = len(matching_nodes) / len(example_nodes) if example_nodes else 0
        edge_coverage = len(matching_edges) / len(example_edge_tuples) if example_edge_tuples else 0
        
        # Create comparison result
        comparison = {
            "matching_nodes": matching_nodes,
            "missing_nodes": missing_nodes,
            "extra_nodes": extra_nodes,
            "matching_edges": matching_edges,
            "missing_edges": missing_edges,
            "extra_edges": extra_edges,
            "similar_edges": similar_edges,
            "node_coverage": node_coverage,
            "edge_coverage": edge_coverage
        }
        
        return comparison
    
    def _generate_high_level_comparison_feedback(self, 
                                               comparison: Dict[str, Any],
                                               current_round: int) -> str:
        """
        Generate high-level comparison feedback.
        
        Args:
            comparison: Comparison results
            current_round: Current round number
            
        Returns:
            High-level comparison feedback text
        """
        # This is a simplified implementation
        # In a real implementation, this would provide more detailed and personalized feedback
        
        # Start with a supportive introduction
        feedback = "I've compared your concept map with an expert's understanding of this topic. Here's what I notice:\n\n"
        
        # Add feedback on concept coverage
        node_coverage = comparison["node_coverage"]
        if node_coverage > 0.8:
            feedback += (
                "**Concept Coverage**: Excellent! Your map includes most of the key concepts for this topic. "
                f"You've included {len(comparison['matching_nodes'])} important concepts that align with expert understanding.\n\n"
            )
        elif node_coverage > 0.5:
            feedback += (
                "**Concept Coverage**: Good progress! Your map includes many important concepts, but there are still "
                f"some key concepts that could enhance your understanding. You've included {len(comparison['matching_nodes'])} "
                "important concepts that align with expert understanding.\n\n"
            )
        else:
            feedback += (
                "**Concept Coverage**: Your map includes some important concepts, but there are several key concepts "
                f"that would help develop a more complete understanding. Currently, you've included {len(comparison['matching_nodes'])} "
                "concepts that align with expert understanding.\n\n"
            )
        
        # Add feedback on relationship coverage
        edge_coverage = comparison["edge_coverage"]
        if edge_coverage > 0.7:
            feedback += (
                "**Relationship Coverage**: Excellent! Your map shows strong understanding of how concepts relate to each other. "
                f"You've identified {len(comparison['matching_edges'])} relationships that align with expert understanding.\n\n"
            )
        elif edge_coverage > 0.4:
            feedback += (
                "**Relationship Coverage**: Good progress! You've identified some important relationships between concepts, "
                f"but there are more connections to explore. You've included {len(comparison['matching_edges'])} relationships "
                "that align with expert understanding.\n\n"
            )
        else:
            feedback += (
                "**Relationship Coverage**: Your map shows some relationships between concepts, but there are many more "
                f"important connections to explore. Currently, you've included {len(comparison['matching_edges'])} relationships "
                "that align with expert understanding.\n\n"
            )
        
        # Provide specific guidance on missing concepts (without revealing the entire example map)
        if comparison["missing_nodes"] and len(comparison["missing_nodes"]) <= 5:
            # Select up to 3 missing concepts to hint at
            missing_sample = list(comparison["missing_nodes"])[:3]
            
            feedback += (
                "**Concepts to Consider**: Based on expert understanding, consider exploring these additional concepts "
                f"and how they might fit into your map: {', '.join(missing_sample)}.\n\n"
            )
        elif comparison["missing_nodes"]:
            # Give a more general hint about missing concept areas
            feedback += (
                "**Concepts to Consider**: There are several important concepts missing from your map. "
                "Consider what additional concepts might be central to understanding this topic, particularly "
                "those that might connect to the concepts you've already included.\n\n"
            )
        
        # Provide guidance on relationship quality
        if comparison["similar_edges"]:
            # Select one example to provide specific feedback on
            example = next(iter(comparison["similar_edges"]))
            student_rel = example[0][2]
            expert_rel = example[1][2]
            
            feedback += (
                "**Relationship Quality**: Some of your relationships could be refined. For example, "
                f"you've described the relationship between '{example[0][0]}' and '{example[0][1]}' as '{student_rel}'. "
                f"Consider whether there might be a more precise or accurate way to describe this relationship.\n\n"
            )
        
        # Add a reflection prompt
        feedback += (
            "**Reflection Questions**:\n\n"
            "1. What are the most central concepts in your map? How do they connect to other concepts?\n"
            "2. Are there any areas of your map that feel incomplete or could benefit from more development?\n"
            "3. How might you refine the relationships between concepts to more accurately represent their connections?\n\n"
            
            "Continue developing your map based on these reflections, focusing on both adding any missing key concepts "
            "and refining the relationships between concepts."
        )
        
        return feedback
    
    def _generate_medium_level_comparison_feedback(self, 
                                                 comparison: Dict[str, Any],
                                                 current_round: int) -> str:
        """
        Generate medium-level comparison feedback.
        
        Args:
            comparison: Comparison results
            current_round: Current round number
            
        Returns:
            Medium-level comparison feedback text
        """
        # This is a simplified implementation
        # In a real implementation, this would provide more detailed and personalized feedback
        
        # Start with a supportive introduction
        feedback = "I've compared your concept map with expert understanding of this topic. Here's some feedback:\n\n"
        
        # Add feedback on concept coverage
        node_coverage = comparison["node_coverage"]
        if node_coverage > 0.7:
            feedback += (
                "**Concept Coverage**: Your map includes many of the key concepts for this topic. "
                "This shows a good understanding of the important elements.\n\n"
            )
        elif node_coverage > 0.4:
            feedback += (
                "**Concept Coverage**: Your map includes some important concepts, but there are others "
                "that would help develop a more complete understanding.\n\n"
            )
        else:
            feedback += (
                "**Concept Coverage**: Consider expanding your map to include more key concepts related to this topic. "
                "There are several important concepts that would enhance your understanding.\n\n"
            )
        
        # Add feedback on relationship coverage
        edge_coverage = comparison["edge_coverage"]
        if edge_coverage > 0.6:
            feedback += (
                "**Relationship Coverage**: Your map shows good understanding of how concepts relate to each other. "
                "The connections you've made align well with expert understanding.\n\n"
            )
        elif edge_coverage > 0.3:
            feedback += (
                "**Relationship Coverage**: You've identified some important relationships between concepts, "
                "but there are more connections to explore.\n\n"
            )
        else:
            feedback += (
                "**Relationship Coverage**: Focus on developing more connections between the concepts in your map. "
                "Understanding how concepts relate to each other is key to mastering this topic.\n\n"
            )
        
        # Provide general guidance on missing concepts
        if comparison["missing_nodes"]:
            feedback += (
                "**Areas to Explore**: There are some concept areas that could be further developed in your map. "
                "Consider what additional concepts might be important for understanding this topic, particularly "
                "those that might connect to the concepts you've already included.\n\n"
            )
        
        # Add a reflection prompt
        feedback += (
            "As you continue to develop your map, consider:\n\n"
            "- What are the most important concepts in this topic?\n"
            "- How do these concepts relate to each other?\n"
            "- Are there any areas of your map that could be expanded or refined?\n\n"
            
            "Use these questions to guide your next revision."
        )
        
        return feedback
    
    def _generate_low_level_comparison_feedback(self, 
                                              comparison: Dict[str, Any],
                                              current_round: int) -> str:
        """
        Generate low-level comparison feedback.
        
        Args:
            comparison: Comparison results
            current_round: Current round number
            
        Returns:
            Low-level comparison feedback text
        """
        # This is a simplified implementation
        # In a real implementation, this would provide more detailed and personalized feedback
        
        # Start with a supportive introduction
        feedback = "I've looked at your concept map and have some thoughts to share:\n\n"
        
        # Add general feedback on the map
        feedback += (
            "Your map shows your current understanding of this topic. As you continue to develop it, "
            "consider whether there are additional concepts or relationships that might be important "
            "to include.\n\n"
        )
        
        # Add a reflection prompt
        feedback += (
            "Here are some questions to consider as you revise your map:\n\n"
            "- What do you think are the most important concepts in this topic?\n"
            "- How do these concepts connect to each other?\n"
            "- Are there any areas where you could add more detail or connections?\n\n"
            
            "Use these questions to guide your thinking as you continue to develop your understanding."
        )
        
        return feedback
    
    def _generate_summary_comparison(self, 
                                    concept_map_data: Dict[str, Any],
                                    session_state: Dict[str, Any]) -> str:
        """
        Generate a summary comparison for the final round.
        
        Args:
            concept_map_data: Concept map data
            session_state: Current session state
            
        Returns:
            Summary comparison text
        """
        # Check if example map is set
        if not self.example_map or not self.example_map.get("nodes"):
            return (
                "Your final concept map represents your understanding of this topic. As you continue "
                "to learn and explore this area, your understanding will continue to develop and evolve."
            )
        
        # Compare the final map with the example map
        comparison = self._compare_maps(concept_map_data, self.example_map)
        
        # Get previous maps
        previous_maps = session_state.get("previous_concept_maps", [])
        
        # Generate summary based on comparison and progress
        summary = (
            "**Final Concept Map Analysis:**\n\n"
        )
        
        # Add feedback on overall coverage
        node_coverage = comparison["node_coverage"]
        edge_coverage = comparison["edge_coverage"]
        
        overall_score = (node_coverage + edge_coverage) / 2
        
        if overall_score > 0.75:
            summary += (
                "Your final concept map demonstrates an excellent understanding of this topic. "
                f"You've included {len(comparison['matching_nodes'])} key concepts and {len(comparison['matching_edges'])} "
                "important relationships that align with expert understanding. This shows a comprehensive grasp "
                "of both the individual concepts and how they relate to each other.\n\n"
            )
        elif overall_score > 0.5:
            summary += (
                "Your final concept map demonstrates a good understanding of this topic. "
                f"You've included {len(comparison['matching_nodes'])} key concepts and {len(comparison['matching_edges'])} "
                "important relationships that align with expert understanding. This shows a solid grasp "
                "of many important aspects of the topic.\n\n"
            )
        else:
            summary += (
                "Your final concept map demonstrates a developing understanding of this topic. "
                f"You've included {len(comparison['matching_nodes'])} concepts and {len(comparison['matching_edges'])} "
                "relationships that align with expert understanding. This provides a foundation for "
                "further learning and exploration.\n\n"
            )
        
        # Add feedback on progress if there are previous maps
        if previous_maps:
            # Compare first map with final map to show progress
            first_map = previous_maps[0]
            first_comparison = self._compare_maps(first_map, self.example_map)
            
            node_improvement = node_coverage - first_comparison["node_coverage"]
            edge_improvement = edge_coverage - first_comparison["edge_coverage"]
            
            if node_improvement > 0.2 or edge_improvement > 0.2:
                summary += (
                    "**Progress**: Your concept map has shown significant improvement throughout this exercise. "
                    "You've expanded your understanding by adding key concepts and developing important relationships "
                    "between them. This demonstrates effective learning and engagement with the material.\n\n"
                )
            elif node_improvement > 0 or edge_improvement > 0:
                summary += (
                    "**Progress**: Your concept map has shown improvement throughout this exercise. "
                    "You've built upon your initial understanding by adding concepts and developing relationships "
                    "between them. This shows engagement with the learning process.\n\n"
                )
            else:
                summary += (
                    "**Progress**: Throughout this exercise, you've worked to develop your concept map and "
                    "explore your understanding of the topic. Concept mapping is an iterative process, and "
                    "each revision provides an opportunity to refine your thinking.\n\n"
                )
        
        # Add suggestions for further development
        summary += (
            "**Further Development:**\n\n"
            "As you continue to learn about this topic, consider:\n\n"
        )
        
        if comparison["missing_nodes"] and len(comparison["missing_nodes"]) <= 5:
            # Select up to 3 missing concepts to suggest
            missing_sample = list(comparison["missing_nodes"])[:3]
            
            summary += (
                f"- Exploring these additional concepts: {', '.join(missing_sample)}\n"
                "- How these concepts might connect to your existing understanding\n\n"
            )
        else:
            summary += (
                "- Continuing to expand your understanding with additional concepts\n"
                "- Developing more nuanced relationships between concepts\n\n"
            )
        
        summary += (
            "Remember that concept maps are tools for learning and organizing knowledge. "
            "Your map will continue to evolve as your understanding deepens, and the process "
            "of creating and revising concept maps itself contributes to your learning."
        )
        
        return summary
    
    def get_example_map(self) -> Dict[str, Any]:
        """
        Get the example map.
        
        Returns:
            The example map
        """
        return self.example_map
    
    def get_feedback_level(self) -> str:
        """
        Get the current feedback level.
        
        Returns:
            The current feedback level
        """
        return self.feedback_level
