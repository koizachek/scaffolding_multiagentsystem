"""
Procedural Scaffolding Agent

This module provides the procedural scaffolding agent that guides learners
in using external tools and interfaces.
"""

import logging
from typing import Dict, List, Any, Optional, Callable

from MAS.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)

class ProceduralScaffoldingAgent(BaseAgent):
    """
    Procedural scaffolding agent for the multi-agent scaffolding system.
    
    This agent guides learners in using external tools and interfaces,
    providing process-oriented hints and step-by-step support.
    """
    
    def __init__(self, 
                name: str,
                config: Dict[str, Any],
                logger_callback: Optional[Callable] = None):
        """
        Initialize the procedural scaffolding agent.
        
        Args:
            name: Name of the agent
            config: Agent configuration
            logger_callback: Callback function for logging
        """
        super().__init__(name, "procedural_scaffolding", config, logger_callback)
        
        # Initialize scaffolding level
        self.scaffolding_level = "medium"  # low, medium, high
        
        # Initialize scaffolding history
        self.scaffolding_history = []
        
        # Initialize common procedural issues
        self.common_issues = {
            "pdf_upload": "Having trouble uploading your PDF concept map? Make sure your file is in PDF format and not too large.",
            "concept_creation": "To add new concepts to your map, you typically need to use the 'Add Concept' or '+' button in your concept mapping tool.",
            "relationship_creation": "To create relationships between concepts, you usually need to select one concept, then drag to another concept to create a connecting line.",
            "relationship_labeling": "Don't forget to label your relationships to show how concepts are connected. Most tools allow you to double-click on a line to add a label.",
            "map_organization": "You can usually rearrange your concept map by dragging concepts to new positions. This can help make the structure clearer.",
            "saving_exporting": "Remember to save your work regularly. Most concept mapping tools allow you to export your map as a PDF for submission."
        }
        
        logger.info(f"Initialized procedural scaffolding agent: {name}")
    
    def _process_impl(self, 
                     input_data: Dict[str, Any], 
                     context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input data and generate procedural scaffolding.
        
        Args:
            input_data: Input data to process
            context: Context information
            
        Returns:
            Response data with procedural scaffolding
        """
        # Extract input type
        input_type = input_data.get("type", "unknown")
        
        # Get session state
        session_state = context.get("session_state", {})
        
        # Update scaffolding level based on ZPD estimate if available
        zpd_estimate = session_state.get("zpd_estimate", {})
        if zpd_estimate and "scaffolding_needs" in zpd_estimate:
            procedural_need = zpd_estimate["scaffolding_needs"].get("procedural")
            if procedural_need:
                self.scaffolding_level = procedural_need
        
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
        Handle concept map submission by providing procedural scaffolding.
        
        Args:
            input_data: Input data containing concept map
            context: Context information
            
        Returns:
            Response data with procedural scaffolding
        """
        # Extract concept map data
        concept_map_data = input_data.get("concept_map_data")
        
        if not concept_map_data:
            return {
                "response": None,
                "agent_type": self.agent_type,
                "status": "error"
            }
        
        logger.info("Generating procedural scaffolding for concept map")
        
        # Get session state
        session_state = context.get("session_state", {})
        
        # Get current round
        current_round = session_state.get("current_round", 0)
        
        # Generate procedural scaffolding based on concept map and scaffolding level
        scaffolding = self._generate_procedural_scaffolding(
            concept_map_data, 
            current_round,
            session_state
        )
        
        # Record scaffolding provided
        self.scaffolding_history.append({
            "round": current_round,
            "scaffolding_level": self.scaffolding_level,
            "scaffolding_provided": scaffolding
        })
        
        # Adjust scaffolding level for next round (fade scaffolding)
        self._adjust_scaffolding_level(session_state)
        
        return {
            "response": scaffolding,
            "agent_type": self.agent_type,
            "status": "success",
            "scaffolding_level": self.scaffolding_level,
            "reasoning": f"Provided procedural scaffolding at {self.scaffolding_level} level"
        }
    
    def _handle_final_round(self, 
                           input_data: Dict[str, Any], 
                           context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle final round by providing procedural tips for future concept mapping.
        
        Args:
            input_data: Input data
            context: Context information
            
        Returns:
            Response data with procedural tips
        """
        logger.info("Generating procedural tips for final round")
        
        # Get session state
        session_state = context.get("session_state", {})
        
        # Generate procedural tips
        tips = self._generate_procedural_tips(session_state)
        
        return {
            "response": tips,
            "agent_type": self.agent_type,
            "status": "success"
        }
    
    def _generate_procedural_scaffolding(self, 
                                        concept_map_data: Dict[str, Any],
                                        current_round: int,
                                        session_state: Dict[str, Any]) -> str:
        """
        Generate procedural scaffolding based on concept map and scaffolding level.
        
        Args:
            concept_map_data: Concept map data
            current_round: Current round number
            session_state: Current session state
            
        Returns:
            Procedural scaffolding text
        """
        # Extract nodes and edges
        nodes = concept_map_data.get("nodes", [])
        edges = concept_map_data.get("edges", [])
        
        # Analyze the concept map for potential procedural issues
        issues = self._identify_procedural_issues(nodes, edges, current_round)
        
        # Generate scaffolding based on level
        if self.scaffolding_level == "high":
            return self._generate_high_level_procedural_scaffolding(issues, current_round)
        elif self.scaffolding_level == "medium":
            return self._generate_medium_level_procedural_scaffolding(issues, current_round)
        else:  # low
            return self._generate_low_level_procedural_scaffolding(issues, current_round)
    
    def _identify_procedural_issues(self, 
                                   nodes: List[str],
                                   edges: List[Dict[str, str]],
                                   current_round: int) -> List[str]:
        """
        Identify potential procedural issues based on the concept map.
        
        Args:
            nodes: List of concept nodes
            edges: List of edges between concepts
            current_round: Current round number
            
        Returns:
            List of identified issues
        """
        issues = []
        
        # Check for empty or very small maps
        if len(nodes) < 3:
            issues.append("concept_creation")
        
        # Check for maps with concepts but few relationships
        if len(nodes) > 3 and len(edges) < len(nodes) / 2:
            issues.append("relationship_creation")
        
        # Check for relationships without labels
        unlabeled_edges = [edge for edge in edges if not edge.get("relation")]
        if unlabeled_edges:
            issues.append("relationship_labeling")
        
        # Add general issues based on round
        if current_round == 0:
            # First round, add upload help
            issues.append("pdf_upload")
        elif current_round == 1:
            # Second round, add organization help
            issues.append("map_organization")
        elif current_round >= 2:
            # Later rounds, add saving/exporting help
            issues.append("saving_exporting")
        
        return issues
    
    def _generate_high_level_procedural_scaffolding(self, 
                                                  issues: List[str],
                                                  current_round: int) -> str:
        """
        Generate high-level procedural scaffolding.
        
        Args:
            issues: List of identified procedural issues
            current_round: Current round number
            
        Returns:
            High-level procedural scaffolding text
        """
        # This is a simplified implementation
        # In a real implementation, this would provide more detailed and personalized scaffolding
        
        # Start with a supportive introduction
        scaffolding = "Here are some specific tips to help you with the concept mapping process:\n\n"
        
        # Add detailed guidance for each identified issue
        if "concept_creation" in issues:
            scaffolding += (
                "**Adding Concepts to Your Map:**\n\n"
                "1. Look for the 'Add Concept' or '+' button in your concept mapping tool\n"
                "2. Click the button to create a new concept node\n"
                "3. Type the name of your concept\n"
                "4. Position the concept in an appropriate location on your map\n"
                "5. Repeat for each new concept you want to add\n\n"
            )
        
        if "relationship_creation" in issues:
            scaffolding += (
                "**Creating Relationships Between Concepts:**\n\n"
                "1. Select the first concept you want to connect\n"
                "2. Look for a connection tool or handle (often appears when you hover over or select a concept)\n"
                "3. Drag from the first concept to the second concept to create a connecting line\n"
                "4. Some tools require you to select both concepts and then click a 'Connect' button\n"
                "5. After creating the connection, add a label to describe the relationship\n\n"
            )
        
        if "relationship_labeling" in issues:
            scaffolding += (
                "**Labeling Relationships:**\n\n"
                "1. Select or double-click on the connecting line between two concepts\n"
                "2. A text field should appear, allowing you to add a label\n"
                "3. Type a brief phrase that describes how the concepts are related (e.g., 'causes', 'is part of', 'influences')\n"
                "4. Press Enter or click away to save the label\n"
                "5. Make sure all your relationships have meaningful labels\n\n"
            )
        
        if "map_organization" in issues:
            scaffolding += (
                "**Organizing Your Concept Map:**\n\n"
                "1. You can rearrange your map by dragging concepts to new positions\n"
                "2. Try to position related concepts near each other\n"
                "3. Consider using a hierarchical structure with the main concept at the top or center\n"
                "4. Some tools allow you to color-code or group concepts to show different categories\n"
                "5. Aim for a clear, readable layout with minimal crossing lines\n\n"
            )
        
        if "saving_exporting" in issues:
            scaffolding += (
                "**Saving and Exporting Your Map:**\n\n"
                "1. Save your work regularly using the 'Save' option in your tool\n"
                "2. To submit your map, look for an 'Export' or 'Download' option\n"
                "3. Select PDF as the export format\n"
                "4. Choose a filename and location for your exported file\n"
                "5. Review the PDF to ensure it shows your complete map before submitting\n\n"
            )
        
        if "pdf_upload" in issues:
            scaffolding += (
                "**Uploading Your Concept Map:**\n\n"
                "1. Ensure your concept map is saved as a PDF file\n"
                "2. Check that the file size is not too large (typically under 10MB)\n"
                "3. Use the upload button or drag-and-drop area to select your file\n"
                "4. Wait for the upload to complete\n"
                "5. If you encounter errors, try reducing the file size or using a different browser\n\n"
            )
        
        # Add general tool tips if no specific issues were identified
        if not issues:
            scaffolding += (
                "**General Concept Mapping Tool Tips:**\n\n"
                "1. Most concept mapping tools allow you to zoom in and out to focus on different parts of your map\n"
                "2. Use the undo/redo functions if you make a mistake\n"
                "3. Consider using different shapes or colors for different types of concepts if your tool supports this\n"
                "4. Some tools allow you to add images or attachments to concepts for additional context\n"
                "5. Remember to save your work regularly to avoid losing progress\n\n"
            )
        
        # Add a note about focusing on content
        scaffolding += (
            "While these technical tips can help you create your concept map, remember that the most important "
            "aspect is the content: the concepts you include and how you connect them to show your understanding "
            "of the topic."
        )
        
        return scaffolding
    
    def _generate_medium_level_procedural_scaffolding(self, 
                                                    issues: List[str],
                                                    current_round: int) -> str:
        """
        Generate medium-level procedural scaffolding.
        
        Args:
            issues: List of identified procedural issues
            current_round: Current round number
            
        Returns:
            Medium-level procedural scaffolding text
        """
        # This is a simplified implementation
        # In a real implementation, this would provide more detailed and personalized scaffolding
        
        # Start with a supportive introduction
        scaffolding = "Here are some helpful tips for working with your concept mapping tool:\n\n"
        
        # Add guidance for each identified issue
        for issue in issues:
            if issue in self.common_issues:
                scaffolding += f"**{issue.replace('_', ' ').title()}**: {self.common_issues[issue]}\n\n"
        
        # Add general tool tips if few specific issues were identified
        if len(issues) <= 2:
            scaffolding += (
                "**Additional Tips:**\n\n"
                "- Most concept mapping tools allow you to undo recent actions if you make a mistake\n"
                "- You can usually zoom in and out to see different levels of detail in your map\n"
                "- Remember to save your work regularly to avoid losing progress\n\n"
            )
        
        # Add a note about focusing on content
        scaffolding += (
            "While the technical aspects of creating your concept map are important, remember to focus "
            "on the content and connections that demonstrate your understanding of the topic."
        )
        
        return scaffolding
    
    def _generate_low_level_procedural_scaffolding(self, 
                                                 issues: List[str],
                                                 current_round: int) -> str:
        """
        Generate low-level procedural scaffolding.
        
        Args:
            issues: List of identified procedural issues
            current_round: Current round number
            
        Returns:
            Low-level procedural scaffolding text
        """
        # This is a simplified implementation
        # In a real implementation, this would provide more detailed and personalized scaffolding
        
        # Start with a supportive introduction
        scaffolding = "Here's a quick reminder about the concept mapping process:\n\n"
        
        # Add brief guidance for the most important identified issue
        if issues:
            primary_issue = issues[0]
            if primary_issue in self.common_issues:
                scaffolding += f"- {self.common_issues[primary_issue]}\n\n"
        
        # Add a general tip
        scaffolding += (
            "Remember that concept maps should show both the important concepts and the relationships "
            "between them. The connections are just as important as the concepts themselves."
        )
        
        return scaffolding
    
    def _generate_procedural_tips(self, session_state: Dict[str, Any]) -> str:
        """
        Generate procedural tips for future concept mapping.
        
        Args:
            session_state: Current session state
            
        Returns:
            Procedural tips text
        """
        # This is a simplified implementation
        # In a real implementation, this would provide more personalized tips
        
        tips = (
            "**Tips for Future Concept Mapping:**\n\n"
            
            "Now that you've completed this concept mapping exercise, here are some procedural tips "
            "that may help you with future concept mapping activities:\n\n"
            
            "1. **Tool Selection**: There are many concept mapping tools available, both online and offline. "
            "Some popular options include CmapTools, MindMeister, Lucidchart, and Coggle. Choose one that "
            "fits your needs and become familiar with its features.\n\n"
            
            "2. **Starting Structure**: Begin with a central concept and branch outward. This helps organize "
            "your thoughts and creates a clear hierarchy or network of ideas.\n\n"
            
            "3. **Iterative Process**: Concept mapping works best as an iterative process. Start with a rough "
            "draft, then refine and expand it as your understanding develops.\n\n"
            
            "4. **Relationship Labels**: Always label the relationships between concepts. These labels are "
            "crucial for showing how concepts are connected and demonstrating your understanding.\n\n"
            
            "5. **Visual Organization**: Use the spatial layout of your map to convey meaning. Related concepts "
            "should be positioned near each other, and the overall structure should be easy to follow.\n\n"
            
            "6. **Regular Saving**: Save your work frequently to avoid losing progress. Most tools offer "
            "auto-save features, but it's good practice to manually save at key points.\n\n"
            
            "7. **Exporting Options**: Familiarize yourself with the exporting options of your chosen tool. "
            "Being able to export in different formats (PDF, image, etc.) can be useful for sharing or submitting "
            "your work.\n\n"
            
            "8. **Collaboration Features**: If you're working with others, look for tools that support "
            "real-time collaboration or easy sharing of concept maps.\n\n"
            
            "These procedural skills will become more natural with practice, allowing you to focus more on "
            "the content and connections in your concept maps rather than the technical aspects of creating them."
        )
        
        return tips
    
    def _adjust_scaffolding_level(self, session_state: Dict[str, Any]) -> None:
        """
        Adjust scaffolding level based on learner progress (fading).
        
        Args:
            session_state: Current session state
        """
        # This is a simplified implementation of scaffolding fading
        # In a real implementation, this would use more sophisticated analysis
        
        # Get current round
        current_round = session_state.get("current_round", 0)
        
        # Get ZPD estimate
        zpd_estimate = session_state.get("zpd_estimate", {})
        
        # If we have a ZPD estimate with scaffolding needs, use that
        if zpd_estimate and "scaffolding_needs" in zpd_estimate:
            procedural_need = zpd_estimate["scaffolding_needs"].get("procedural")
            if procedural_need:
                # Only reduce scaffolding if current level is higher than the estimated need
                if self._scaffolding_level_value(self.scaffolding_level) > self._scaffolding_level_value(procedural_need):
                    self.scaffolding_level = procedural_need
                return
        
        # Otherwise, gradually reduce scaffolding level based on round
        if current_round >= 2 and self.scaffolding_level == "high":
            self.scaffolding_level = "medium"
            logger.info("Reduced scaffolding level from high to medium")
        elif current_round >= 3 and self.scaffolding_level == "medium":
            self.scaffolding_level = "low"
            logger.info("Reduced scaffolding level from medium to low")
    
    def _scaffolding_level_value(self, level: str) -> int:
        """
        Convert scaffolding level string to numeric value for comparison.
        
        Args:
            level: Scaffolding level string
            
        Returns:
            Numeric value (1 for low, 2 for medium, 3 for high)
        """
        if level == "high":
            return 3
        elif level == "medium":
            return 2
        else:  # low
            return 1
    
    def get_scaffolding_level(self) -> str:
        """
        Get the current scaffolding level.
        
        Returns:
            The current scaffolding level
        """
        return self.scaffolding_level
    
    def get_scaffolding_history(self) -> List[Dict[str, Any]]:
        """
        Get the scaffolding history.
        
        Returns:
            The scaffolding history
        """
        return self.scaffolding_history
