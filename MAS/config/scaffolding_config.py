"""
Scaffolding Configuration

This module provides configuration for scaffolding, including prompt templates.
"""

# Scaffolding prompt templates for different scaffolding types and intensities
SCAFFOLDING_PROMPT_TEMPLATES = {
    "strategic": {
        "high": [
            "I notice that {observation}. Could you walk me through your process for organizing the concepts in your map? What was your overall strategy?",
            "Looking at your concept map, I see that {observation}. What approach did you use to decide which concepts to include first and how to arrange them?",
            "Your map has {node_count} concepts and {edge_count} relationships. How did you decide on the overall structure? What might be a logical next step in expanding this area?",
            "I'm curious about how you approached the organization of your concept map. What was your thinking behind placing {concept} where you did?",
            "Have you considered organizing these concepts differently? What alternative structures might help show the relationships more clearly?",
            "What strategy did you use to determine which relationships to include in your map? Are there other important connections you considered but didn't include?"
        ],
        "medium": [
            "I see that {observation}. What was your approach to organizing the concepts in your map?",
            "Looking at your concept map, what strategy did you use to decide which concepts to include?",
            "How did you decide which relationships to show between concepts in your map?",
            "What might be your next step in developing this concept map further?",
            "Have you considered alternative ways to organize these concepts? What might work better?"
        ],
        "low": [
            "What was your overall approach to creating this concept map?",
            "How did you decide which concepts to include in your map?",
            "What might be a next step to improve the organization of your map?",
            "Is there a different way you could arrange these concepts to show their relationships more clearly?"
        ]
    },
    "metacognitive": {
        "high": [
            "As you look at your concept map now, which parts do you feel most confident about, and which parts are you less certain about? Why do you think that is?",
            "How has your understanding of {concept} changed since you started working on this concept map? What specific insights have you gained?",
            "What was the most challenging aspect of creating this concept map? How did you work through that challenge?",
            "If you were to explain what you've learned about this topic to someone else, what key points would you emphasize based on your concept map?",
            "What questions do you still have about this topic that aren't addressed in your current concept map?",
            "How would you assess your current understanding of the relationships between these concepts? What areas might need more exploration?"
        ],
        "medium": [
            "Which part of your concept map do you feel most confident about? Which part are you least confident about?",
            "How has your understanding of this topic changed as you've worked on this concept map?",
            "What was challenging about creating this concept map?",
            "What do you think is the most important relationship shown in your map? Why?",
            "What questions do you still have about this topic?"
        ],
        "low": [
            "How confident do you feel about your understanding of this topic?",
            "What did you learn while creating this concept map?",
            "What part of the concept map was most difficult to create?",
            "What's one thing you'd like to understand better about this topic?"
        ]
    },
    "procedural": {
        "high": [
            "I notice that {observation}. Would you like some guidance on how to add more complex relationships between concepts in your map? What specific aspects of the concept mapping process are you finding challenging?",
            "When creating relationships between concepts, what process do you follow to identify and label these connections? Are there any specific steps you find difficult?",
            "Let's talk about your concept mapping workflow. How do you typically approach the process of creating and revising your map? Are there specific techniques you'd like help with?",
            "When reviewing your concept map, what systematic approach do you use to identify areas for improvement? Have you tried starting from one concept and tracing all its possible connections?",
            "What specific features of your concept mapping tool are you comfortable using? Are there any features you're unsure about that might help improve your map?",
            "Could you describe your process for organizing concepts into hierarchical relationships? What techniques do you use to show different types of relationships?"
        ],
        "medium": [
            "I see that {observation}. Would you like some tips on how to add or label relationships between concepts?",
            "What process do you follow when creating your concept map?",
            "Have you tried reviewing your map systematically to identify missing connections?",
            "Are there any specific features of your concept mapping tool that you find challenging to use?",
            "How do you decide what type of relationship exists between two concepts?"
        ],
        "low": [
            "Would you like some tips on using your concept mapping tool more effectively?",
            "How do you typically create relationships between concepts in your map?",
            "Have you tried looking for missing connections in your map?",
            "Is there any part of the concept mapping process you find challenging?"
        ]
    },
    "conceptual": {
        "high": [
            "I notice that {observation}. Looking at the concepts '{concept}' and [another related concept], how might these two concepts be connected? What underlying mechanisms or principles link them?",
            "Your map includes {node_count} concepts. Can you explain your thinking behind the relationship between [concept A] and [concept B]? What evidence or reasoning supports this connection?",
            "I'm curious about the area of your map dealing with {concept}. This seems important but could be developed further. What additional concepts might be related to this area?",
            "Looking at your concept map, I notice that [concept X] isn't connected to [concept Y], though they seem related. How might these concepts be connected? What relationship might exist between them?",
            "What might be some underlying principles or mechanisms that connect multiple concepts in your map? How do these deeper connections help explain the relationships you've shown?",
            "If you were to add one more important concept to your map that would help connect several existing concepts, what would it be and why?"
        ],
        "medium": [
            "I see that {observation}. How might the concepts '{concept}' and [another concept] relate to each other?",
            "Can you explain your thinking behind the relationship between these two concepts?",
            "What additional concepts might be related to {concept} that aren't in your map yet?",
            "Are there any underlying principles that connect multiple concepts in your map?",
            "How does {concept} influence or affect other concepts in your map?"
        ],
        "low": [
            "How do you think these concepts relate to each other?",
            "What's the most important concept in your map? Why?",
            "Are there any key concepts missing from your map?",
            "How does {concept} connect to the overall topic?"
        ]
    }
}

# Scaffolding follow-up templates for different scaffolding types
SCAFFOLDING_FOLLOWUP_TEMPLATES = {
    "strategic": [
        "That's interesting. Have you considered how this approach might be applied to other parts of your map?",
        "Based on what you've shared, how might you reorganize your map to better reflect these connections?",
        "Given your strategy, what might be the next logical step in developing your concept map?",
        "How might a different organizational approach change the way you understand these relationships?"
    ],
    "metacognitive": [
        "That's a thoughtful reflection. How has your thinking about this topic evolved since you started?",
        "Interesting insight. How might this new understanding influence your approach to learning about related topics?",
        "Based on what you've learned, what questions would you want to explore next?",
        "How would you assess your current understanding compared to when you started this exercise?"
    ],
    "procedural": [
        "That's helpful to know. Would a step-by-step approach to reviewing your map help identify additional connections?",
        "Have you tried using specific features of your concept mapping tool to help with this process?",
        "Would it be useful to discuss specific techniques for organizing hierarchical relationships in your map?",
        "Based on your process, what specific aspect of concept mapping would you like to improve?"
    ],
    "conceptual": [
        "That's an interesting connection. How might this relationship influence other parts of your map?",
        "Given this understanding, are there other concepts that might be connected in similar ways?",
        "How does this relationship contribute to your overall understanding of the topic?",
        "What evidence or reasoning supports this connection between concepts?"
    ]
}

# Scaffolding conclusion templates for different scaffolding types
SCAFFOLDING_CONCLUSION_TEMPLATES = {
    "strategic": [
        "Thank you for sharing your strategic approach to concept mapping. Consider how organizing concepts by {specific_approach} might help clarify the relationships in your next revision.",
        "Your strategy for concept mapping reveals thoughtful planning. As you revise, consider how grouping related concepts might make the structure even clearer.",
        "Based on our discussion, focusing on the hierarchical relationships between concepts could strengthen your map's organization in your next revision."
    ],
    "metacognitive": [
        "Your reflections show deep engagement with this topic. As you continue, regularly assessing your understanding of key relationships will help identify areas for growth.",
        "This self-assessment of your understanding is valuable. Continue to question which parts feel most solid and which need more exploration as you revise.",
        "Your awareness of your learning process is impressive. Keep tracking how your understanding evolves as you develop your concept map further."
    ],
    "procedural": [
        "Thank you for discussing your concept mapping process. Try the systematic review approach we discussed to identify additional connections in your next revision.",
        "The step-by-step approach we discussed should help make your concept mapping process more effective. Remember to save your work regularly as you implement these techniques.",
        "As you apply these procedural techniques to your next revision, focus particularly on clearly labeling the relationships between concepts."
    ],
    "conceptual": [
        "Your understanding of the relationships between concepts shows depth. In your next revision, consider exploring the connection between {concept_1} and {concept_2} further.",
        "The conceptual links you've identified are meaningful. Consider adding some of the underlying mechanisms we discussed to show deeper relationships in your next map.",
        "Your grasp of how these concepts interconnect is developing well. As you revise, focus on showing how {key_concept} influences multiple other concepts in your map."
    ]
}

# Scaffolding selection weights for different factors
SCAFFOLDING_SELECTION_WEIGHTS = {
    "zpd_estimate": 3.0,
    "map_analysis": 2.0,
    "map_comparison": 1.5,
    "round_number": 1.0,
    "interaction_history": 2.0
}

# Default scaffolding intensity for each scaffolding type
DEFAULT_SCAFFOLDING_INTENSITY = {
    "strategic": "medium",
    "metacognitive": "medium",
    "procedural": "medium",
    "conceptual": "medium"
}

# Scaffolding intensity adaptation thresholds
INTENSITY_ADAPTATION_THRESHOLDS = {
    "understanding_indicators": 3,  # Number of understanding indicators to decrease intensity
    "confusion_indicators": 2,      # Number of confusion indicators to increase intensity
    "question_count": 2,            # Number of questions to increase intensity
    "response_length": 100          # Minimum response length to consider for adaptation
}

# Default scaffolding configuration
DEFAULT_SCAFFOLDING_CONFIG = {
    "prompt_templates": SCAFFOLDING_PROMPT_TEMPLATES,
    "followup_templates": SCAFFOLDING_FOLLOWUP_TEMPLATES,
    "conclusion_templates": SCAFFOLDING_CONCLUSION_TEMPLATES,
    "selection_weights": SCAFFOLDING_SELECTION_WEIGHTS,
    "default_intensity": DEFAULT_SCAFFOLDING_INTENSITY,
    "intensity_thresholds": INTENSITY_ADAPTATION_THRESHOLDS,
    "scaffolding_types": ["strategic", "metacognitive", "procedural", "conceptual"],
    "intensity_levels": ["low", "medium", "high"],
    "max_prompts_per_interaction": 3,
    "require_response": True,
    "enable_follow_ups": True,
    "enable_conclusions": True
}
