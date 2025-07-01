"""
Conceptual Scaffolding Agent

This module provides the conceptual scaffolding agent that highlights key concepts
and relationships relevant to the learner's concept map.
"""

import logging
from typing import Dict, List, Any, Optional, Callable, Set

from MAS.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)

class ConceptualScaffoldingAgent(BaseAgent):
    """
    Conceptual scaffolding agent for the multi-agent scaffolding system.
    
    This agent highlights key concepts and relationships relevant to the learner's concept map,
    detects gaps, misconceptions, and missing domain links.
    """
    
    def __init__(self, 
                name: str,
                config: Dict[str, Any],
                logger_callback: Optional[Callable] = None):
        """
        Initialize the conceptual scaffolding agent.
        
        Args:
            name: Name of the agent
            config: Agent configuration
            logger_callback: Callback function for logging
        """
        super().__init__(name, "conceptual_scaffolding", config, logger_callback)
        
        # Initialize scaffolding level
        self.scaffolding_level = "medium"  # low, medium, high
        
        # Initialize domain concepts (these would typically be loaded from a knowledge base)
        # This is a simplified implementation for demonstration purposes
        self.domain_concepts = set()
        self.domain_relationships = []
        
        logger.info(f"Initialized conceptual scaffolding agent: {name}")
    
    def set_domain_knowledge(self, 
                            concepts: Set[str], 
                            relationships: List[Dict[str, str]]) -> None:
        """
        Set the domain knowledge for the agent.
        
        Args:
            concepts: Set of domain concepts
            relationships: List of relationships between concepts
        """
        self.domain_concepts = concepts
        self.domain_relationships = relationships
        logger.info(f"Set domain knowledge with {len(concepts)} concepts and {len(relationships)} relationships")
    
    def _process_impl(self, 
                     input_data: Dict[str, Any], 
                     context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input data and generate conceptual scaffolding.
        
        Args:
            input_data: Input data to process
            context: Context information
            
        Returns:
            Response data with conceptual scaffolding
        """
        # Extract input type
        input_type = input_data.get("type", "unknown")
        
        # Get session state
        session_state = context.get("session_state", {})
        
        # Update scaffolding level based on ZPD estimate if available
        zpd_estimate = session_state.get("zpd_estimate", {})
        if zpd_estimate and "scaffolding_needs" in zpd_estimate:
            conceptual_need = zpd_estimate["scaffolding_needs"].get("conceptual")
            if conceptual_need:
                self.scaffolding_level = conceptual_need
        
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
        Handle concept map submission by providing conceptual scaffolding.
        
        Args:
            input_data: Input data containing concept map
            context: Context information
            
        Returns:
            Response data with conceptual scaffolding
        """
        # Extract concept map data
        concept_map_data = input_data.get("concept_map_data")
        
        if not concept_map_data:
            return {
                "response": None,
                "agent_type": self.agent_type,
                "status": "error"
            }
        
        logger.info("Generating conceptual scaffolding for concept map")
        
        # Get session state
        session_state = context.get("session_state", {})
        
        # Get current round
        current_round = session_state.get("current_round", 0)
        
        # Generate conceptual scaffolding based on concept map and scaffolding level
        scaffolding = self._generate_conceptual_scaffolding(
            concept_map_data, 
            current_round,
            session_state
        )
        
        return {
            "response": scaffolding,
            "agent_type": self.agent_type,
            "status": "success",
            "scaffolding_level": self.scaffolding_level,
            "reasoning": f"Provided conceptual scaffolding at {self.scaffolding_level} level"
        }
    
    def _handle_final_round(self, 
                           input_data: Dict[str, Any], 
                           context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle final round by providing conceptual insights.
        
        Args:
            input_data: Input data
            context: Context information
            
        Returns:
            Response data with conceptual insights
        """
        logger.info("Generating conceptual insights for final round")
        
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
        
        # Generate conceptual insights
        insights = self._generate_conceptual_insights(concept_map_data, session_state)
        
        return {
            "response": insights,
            "agent_type": self.agent_type,
            "status": "success"
        }
    
    def _generate_conceptual_scaffolding(self, 
                                        concept_map_data: Dict[str, Any],
                                        current_round: int,
                                        session_state: Dict[str, Any]) -> str:
        """
        Generate conceptual scaffolding based on concept map and scaffolding level.
        
        Args:
            concept_map_data: Concept map data
            current_round: Current round number
            session_state: Current session state
            
        Returns:
            Conceptual scaffolding text
        """
        # Extract nodes and edges
        nodes = concept_map_data.get("nodes", [])
        edges = concept_map_data.get("edges", [])
        
        # Get previous concept map if available
        previous_maps = session_state.get("previous_concept_maps", [])
        previous_map = previous_maps[-1] if previous_maps else None
        
        # Analyze the concept map
        analysis = self._analyze_concept_map(nodes, edges, previous_map)
        
        # Generate scaffolding based on level
        if self.scaffolding_level == "high":
            return self._generate_high_level_conceptual_scaffolding(analysis, current_round)
        elif self.scaffolding_level == "medium":
            return self._generate_medium_level_conceptual_scaffolding(analysis, current_round)
        else:  # low
            return self._generate_low_level_conceptual_scaffolding(analysis, current_round)
    
    def _analyze_concept_map(self, 
                            nodes: List[str],
                            edges: List[Dict[str, str]],
                            previous_map: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze the concept map to identify strengths, gaps, and misconceptions.
        
        Args:
            nodes: List of concept nodes
            edges: List of edges between concepts
            previous_map: Previous concept map data
            
        Returns:
            Analysis results
        """
        # This is a simplified implementation
        # In a real implementation, this would use more sophisticated analysis
        
        # Initialize analysis results
        analysis = {
            "num_concepts": len(nodes),
            "num_relationships": len(edges),
            "central_concepts": [],
            "isolated_concepts": [],
            "missing_key_concepts": [],
            "missing_relationships": [],
            "potential_misconceptions": [],
            "strengths": [],
            "areas_for_improvement": []
        }
        
        # Identify central concepts (those with the most connections)
        concept_connections = {}
        for edge in edges:
            source = edge.get("source")
            target = edge.get("target")
            
            if source:
                concept_connections[source] = concept_connections.get(source, 0) + 1
            if target:
                concept_connections[target] = concept_connections.get(target, 0) + 1
        
        # Sort concepts by number of connections
        sorted_concepts = sorted(concept_connections.items(), key=lambda x: x[1], reverse=True)
        
        # Identify central concepts (top 3 or fewer)
        analysis["central_concepts"] = [concept for concept, count in sorted_concepts[:min(3, len(sorted_concepts))]]
        
        # Identify isolated concepts (those with no connections)
        connected_concepts = set(concept_connections.keys())
        analysis["isolated_concepts"] = [node for node in nodes if node not in connected_concepts]
        
        # Identify missing key concepts (if domain concepts are available)
        if self.domain_concepts:
            analysis["missing_key_concepts"] = list(self.domain_concepts - set(nodes))
        
        # Identify missing relationships (if domain relationships are available)
        if self.domain_relationships:
            # This is a simplified check
            # In a real implementation, this would be more sophisticated
            existing_relationships = set((edge.get("source"), edge.get("target")) for edge in edges)
            
            for rel in self.domain_relationships:
                source = rel.get("source")
                target = rel.get("target")
                
                if source in nodes and target in nodes and (source, target) not in existing_relationships:
                    analysis["missing_relationships"].append(rel)
        
        # Identify potential misconceptions (simplified)
        # In a real implementation, this would use more sophisticated analysis
        for edge in edges:
            source = edge.get("source")
            target = edge.get("target")
            relation = edge.get("relation", "")
            
            # Check for potential misconceptions in the relationships
            # This is a placeholder for more sophisticated analysis
            if relation and "not" in relation.lower():
                analysis["potential_misconceptions"].append({
                    "source": source,
                    "target": target,
                    "relation": relation,
                    "reason": "Negative relationships may indicate a misconception"
                })
        
        # Identify strengths
        if len(nodes) > 10:
            analysis["strengths"].append("Your map includes a good number of concepts")
        
        if len(edges) > len(nodes):
            analysis["strengths"].append("Your map shows good connectivity between concepts")
        
        if analysis["central_concepts"]:
            analysis["strengths"].append(f"Your map has clear central concepts: {', '.join(analysis['central_concepts'])}")
        
        # Identify areas for improvement
        if analysis["isolated_concepts"]:
            analysis["areas_for_improvement"].append("Some concepts are not connected to others")
        
        if len(edges) < len(nodes) - 1:
            analysis["areas_for_improvement"].append("Your map could benefit from more connections between concepts")
        
        if analysis["missing_key_concepts"]:
            analysis["areas_for_improvement"].append("Some key concepts are missing from your map")
        
        if analysis["missing_relationships"]:
            analysis["areas_for_improvement"].append("Some important relationships between concepts are missing")
        
        return analysis
    
    def _generate_high_level_conceptual_scaffolding(self, 
                                                  analysis: Dict[str, Any],
                                                  current_round: int) -> str:
        """
        Generate high-level conceptual scaffolding.
        
        Args:
            analysis: Analysis of the concept map
            current_round: Current round number
            
        Returns:
            High-level conceptual scaffolding text
        """
        # This is a simplified implementation
        # In a real implementation, this would provide more detailed and personalized scaffolding
        
        # Start with a supportive introduction
        scaffolding = "I've analyzed your concept map and have some specific suggestions to help you develop your understanding:\n\n"
        
        # Highlight strengths
        if analysis["strengths"]:
            scaffolding += "**Strengths:**\n"
            for strength in analysis["strengths"]:
                scaffolding += f"- {strength}\n"
            scaffolding += "\n"
        
        # Address areas for improvement
        scaffolding += "**Conceptual Development Opportunities:**\n"
        
        # Address isolated concepts
        if analysis["isolated_concepts"]:
            scaffolding += (
                f"- I notice that the following concepts are not connected to others: "
                f"{', '.join(analysis['isolated_concepts'])}. Consider how these concepts "
                f"relate to other concepts in your map. For example, how might "
                f"{analysis['isolated_concepts'][0]} connect to {analysis['central_concepts'][0] if analysis['central_concepts'] else 'other concepts'}?\n\n"
            )
        
        # Address missing key concepts
        if analysis["missing_key_concepts"] and len(analysis["missing_key_concepts"]) <= 5:
            scaffolding += (
                f"- Your map could be enhanced by including these key concepts: "
                f"{', '.join(analysis['missing_key_concepts'][:5])}. "
                f"Think about how these concepts fit into your current understanding of the topic.\n\n"
            )
        elif analysis["missing_key_concepts"]:
            scaffolding += (
                f"- Consider adding some of these key concepts to your map: "
                f"{', '.join(analysis['missing_key_concepts'][:3])}. "
                f"These concepts are important for understanding the topic more fully.\n\n"
            )
        
        # Address missing relationships
        if analysis["missing_relationships"] and len(analysis["missing_relationships"]) <= 3:
            for rel in analysis["missing_relationships"][:3]:
                scaffolding += (
                    f"- Consider the relationship between {rel.get('source')} and {rel.get('target')}. "
                    f"How might these concepts be connected? (Hint: Think about {rel.get('relation', 'how they influence each other')})\n\n"
                )
        elif analysis["missing_relationships"]:
            scaffolding += (
                f"- Look for additional relationships between concepts that are already in your map. "
                f"For example, how might {analysis['missing_relationships'][0].get('source')} relate to "
                f"{analysis['missing_relationships'][0].get('target')}?\n\n"
            )
        
        # Address potential misconceptions
        if analysis["potential_misconceptions"]:
            for misconception in analysis["potential_misconceptions"][:2]:
                scaffolding += (
                    f"- Review the relationship you've identified between {misconception.get('source')} and "
                    f"{misconception.get('target')} ({misconception.get('relation')}). "
                    f"Consider whether this accurately represents their relationship.\n\n"
                )
        
        # Provide specific guidance based on the map's development
        if analysis["num_concepts"] < 8:
            scaffolding += (
                "- Your map would benefit from including more concepts. Try brainstorming additional "
                "terms, ideas, or principles related to your topic. For each new concept, think about "
                "how it connects to your existing concepts.\n\n"
            )
        elif analysis["num_relationships"] < analysis["num_concepts"]:
            scaffolding += (
                "- Your map has a good number of concepts but could use more connections between them. "
                "Review each concept and ask yourself if it relates to other concepts in your map. "
                "Remember to label each connection to show the nature of the relationship.\n\n"
            )
        else:
            scaffolding += (
                "- Your map shows good connectivity. Now focus on the quality of your relationships. "
                "Make sure each connection has a clear, specific label that accurately describes "
                "the relationship between concepts.\n\n"
            )
        
        # Add a reflection prompt
        scaffolding += (
            "As you revise your map, think about the central theme or concept that ties everything together. "
            "How do the various concepts and relationships contribute to your understanding of this theme?"
        )
        
        return scaffolding
    
    def _generate_medium_level_conceptual_scaffolding(self, 
                                                    analysis: Dict[str, Any],
                                                    current_round: int) -> str:
        """
        Generate medium-level conceptual scaffolding.
        
        Args:
            analysis: Analysis of the concept map
            current_round: Current round number
            
        Returns:
            Medium-level conceptual scaffolding text
        """
        # This is a simplified implementation
        # In a real implementation, this would provide more detailed and personalized scaffolding
        
        # Start with a supportive introduction
        scaffolding = "Here are some observations and suggestions about the concepts in your map:\n\n"
        
        # Highlight strengths
        if analysis["strengths"]:
            scaffolding += "**Strengths:**\n"
            for strength in analysis["strengths"]:
                scaffolding += f"- {strength}\n"
            scaffolding += "\n"
        
        # Address areas for improvement
        if analysis["areas_for_improvement"]:
            scaffolding += "**Areas to Consider:**\n"
            for area in analysis["areas_for_improvement"]:
                scaffolding += f"- {area}\n"
            scaffolding += "\n"
        
        # Provide general guidance
        scaffolding += "**Conceptual Development Suggestions:**\n"
        
        # Address isolated concepts
        if analysis["isolated_concepts"]:
            scaffolding += (
                f"- Consider how concepts like {', '.join(analysis['isolated_concepts'][:2])} "
                f"might connect to other concepts in your map.\n\n"
            )
        
        # Address missing key concepts
        if analysis["missing_key_concepts"]:
            scaffolding += (
                f"- You might want to explore these concepts in relation to your topic: "
                f"{', '.join(analysis['missing_key_concepts'][:3])}.\n\n"
            )
        
        # Provide general guidance based on the map's development
        if analysis["num_concepts"] < 8:
            scaffolding += (
                "- Consider expanding your map with additional concepts related to your topic.\n\n"
            )
        elif analysis["num_relationships"] < analysis["num_concepts"]:
            scaffolding += (
                "- Look for additional relationships between the concepts in your map.\n\n"
            )
        else:
            scaffolding += (
                "- Focus on refining the relationship labels to be more specific and accurate.\n\n"
            )
        
        # Add a reflection prompt
        scaffolding += (
            "As you continue developing your map, think about how these concepts relate to each other "
            "and to the overall topic. What new insights do these relationships reveal?"
        )
        
        return scaffolding
    
    def _generate_low_level_conceptual_scaffolding(self, 
                                                 analysis: Dict[str, Any],
                                                 current_round: int) -> str:
        """
        Generate low-level conceptual scaffolding.
        
        Args:
            analysis: Analysis of the concept map
            current_round: Current round number
            
        Returns:
            Low-level conceptual scaffolding text
        """
        # This is a simplified implementation
        # In a real implementation, this would provide more detailed and personalized scaffolding
        
        # Start with a supportive introduction
        scaffolding = "Here are some thoughts about the concepts in your map:\n\n"
        
        # Highlight strengths
        if analysis["strengths"]:
            scaffolding += "I notice that:\n"
            for strength in analysis["strengths"]:
                scaffolding += f"- {strength}\n"
            scaffolding += "\n"
        
        # Provide gentle prompts for reflection
        scaffolding += "As you continue developing your map, consider:\n\n"
        
        # General conceptual prompts
        scaffolding += (
            "- What are the most important concepts related to this topic?\n\n"
            "- How do these concepts relate to each other?\n\n"
            "- Are there any concepts that might be missing from your current map?\n\n"
            "- How might you organize these concepts to show their relationships more clearly?\n\n"
        )
        
        # Add a reflection prompt
        scaffolding += (
            "Take some time to reflect on how these concepts fit together to form a complete picture "
            "of the topic. What does this organization reveal about your understanding?"
        )
        
        return scaffolding
    
    def _generate_conceptual_insights(self, 
                                     concept_map_data: Dict[str, Any],
                                     session_state: Dict[str, Any]) -> str:
        """
        Generate conceptual insights for the final round.
        
        Args:
            concept_map_data: Concept map data
            session_state: Current session state
            
        Returns:
            Conceptual insights text
        """
        # Extract nodes and edges
        nodes = concept_map_data.get("nodes", [])
        edges = concept_map_data.get("edges", [])
        
        # Get previous maps
        previous_maps = session_state.get("previous_concept_maps", [])
        
        # Analyze the final concept map
        analysis = self._analyze_concept_map(nodes, edges, previous_maps[-1] if previous_maps else None)
        
        # Generate insights based on the analysis
        insights = (
            "Looking at your concept map from a conceptual perspective, I notice the following:\n\n"
        )
        
        # Highlight conceptual strengths
        if analysis["strengths"]:
            insights += "**Conceptual Strengths:**\n"
            for strength in analysis["strengths"]:
                insights += f"- {strength}\n"
            insights += "\n"
        
        # Highlight central concepts
        if analysis["central_concepts"]:
            insights += (
                f"**Central Concepts:** Your map shows that {', '.join(analysis['central_concepts'])} "
                f"{'are' if len(analysis['central_concepts']) > 1 else 'is'} central to your understanding of this topic. "
                f"These concepts have the most connections to other ideas, suggesting they play a key role "
                f"in organizing your knowledge.\n\n"
            )
        
        # Discuss conceptual development over time
        if previous_maps:
            # Compare first and last maps
            first_map = previous_maps[0]
            first_nodes = first_map.get("nodes", [])
            first_edges = first_map.get("edges", [])
            
            # Calculate growth
            concept_growth = len(nodes) - len(first_nodes)
            relationship_growth = len(edges) - len(first_edges)
            
            if concept_growth > 0 or relationship_growth > 0:
                insights += (
                    f"**Conceptual Development:** Throughout this exercise, your concept map has evolved "
                    f"significantly. You've added {concept_growth} new concepts and {relationship_growth} "
                    f"new relationships since your first map. This growth demonstrates how your understanding "
                    f"of the topic has deepened and become more nuanced.\n\n"
                )
        
        # Provide suggestions for further conceptual development
        insights += (
            "**Further Conceptual Development:**\n"
            "As you continue to develop your understanding of this topic, consider:\n\n"
        )
        
        if analysis["missing_key_concepts"]:
            insights += (
                f"- Exploring these additional concepts: {', '.join(analysis['missing_key_concepts'][:3])}\n\n"
            )
        
        insights += (
            "- Deepening your understanding of the relationships between concepts by asking 'why' and 'how' questions\n\n"
            "- Looking for patterns and principles that connect multiple concepts\n\n"
            "- Connecting this knowledge to other topics or domains you're familiar with\n\n"
        )
        
        # Conclude with a positive note
        insights += (
            "Your concept map represents your current understanding of this topic, which will continue "
            "to evolve as you learn more. The connections you've identified between concepts provide a "
            "foundation for deeper understanding and application of this knowledge."
        )
        
        return insights
