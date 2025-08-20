"""
AMG-Specific Scaffolding Configuration

This module provides scaffolding configuration specifically tailored for the 
Adaptive Market Gatekeeping (AMG) international market entry task.
"""

# AMG-specific scaffolding prompt templates
AMG_SCAFFOLDING_PROMPT_TEMPLATES = {
    "conceptual": {
        "high": [
            "I notice you've included {observation}. How do you think AMG's dynamic adaptation mechanism specifically relates to the entry barriers you've identified? What's the conceptual connection there?",
            "Looking at your map with {node_count} concepts, I'm curious about the relationship between AMG and your chosen entry strategy. What underlying principles connect these concepts?",
            "You've shown {concept} in your map. How might AMG's resource blocking mechanism conceptually relate to the start-up's resources? What's the nature of that interaction?",
            "I see you have market analysis and target markets in your map. How do these concepts relate to AMG's network control mechanism? What conceptual bridge connects them?",
            "Interesting placement of {concept}. How might the legal framework be influenced by AMG's rule-changing capability? What's the conceptual relationship there?",
            "Looking at your financing concepts, how might they be affected by AMG mechanisms? What underlying principles govern these relationships?"
        ],
        "medium": [
            "How do you think AMG relates to the entry barriers in your map?",
            "What's the connection between AMG and the entry strategies you've identified?",
            "How might AMG's mechanisms affect the start-up's resources?",
            "What relationship exists between market analysis and AMG in your understanding?",
            "How does the legal framework interact with AMG in your map?"
        ],
        "low": [
            "What concepts in your map are most affected by AMG?",
            "How does AMG connect to other concepts?",
            "Which AMG mechanism seems most important to you?",
            "What's the main relationship between AMG and market entry?"
        ]
    },
    "procedural": {
        "high": [
            "I see {observation}. When mapping AMG's impact, have you considered starting from each AMG mechanism (dynamic adaptation, rule-changing, network control, resource blocking) and tracing how each affects different aspects of market entry?",
            "Looking at your process, how do you identify which entry strategy concepts should connect to AMG? Have you tried using the Veyra example as a template for creating these relationships?",
            "When adding relationships between AMG and other concepts, what labeling approach do you use? Consider using action words like 'blocks', 'influences', 'counters' to show AMG's active role.",
            "I notice your map structure. Have you tried organizing concepts in layers - perhaps AMG mechanisms at one level, entry strategies at another, and resources at a third? This might help visualize the flow of influence.",
            "For showing how the start-up can navigate AMG, what process do you use to identify counter-strategies? Try working backwards from success factors to see what overcomes AMG barriers.",
            "When reviewing your map, do you systematically check if each AMG mechanism has at least one connection to other concepts? This ensures comprehensive coverage of AMG's impact."
        ],
        "medium": [
            "Have you tried starting from each AMG mechanism and tracing its effects?",
            "What process do you use to connect AMG to entry strategies?",
            "How do you decide on labels for AMG-related relationships?",
            "Have you considered organizing concepts in layers based on their role?",
            "What approach helps you identify how to navigate AMG?"
        ],
        "low": [
            "How do you decide which concepts to connect to AMG?",
            "What helps you label the relationships with AMG?",
            "Have you tried different ways to organize AMG in your map?",
            "What process helps you show AMG's impact?"
        ]
    },
    "strategic": {
        "high": [
            "I see {observation}. Strategically, how are you showing the start-up's response to AMG? What's your approach to demonstrating both the challenges AMG creates and the potential solutions?",
            "Your map has {node_count} concepts. What's your strategic thinking behind positioning AMG in relation to entry strategies? Should AMG be central, or would another arrangement better show its gatekeeping role?",
            "Looking at your organization, what strategy did you use to show how AMG affects multiple aspects simultaneously? Have you considered using different relationship types to show direct vs. indirect impacts?",
            "Interesting structure with {concept}. Strategically, how are you differentiating between AMG's preventive effects (blocking) and its adaptive effects (changing rules)? This distinction might strengthen your map.",
            "What's your strategic approach to showing the temporal aspect - how AMG adapts over time to new start-up strategies? This dynamic element is key to understanding AMG.",
            "How did you strategically decide which connections are most critical for showing how a start-up can successfully navigate AMG? What makes these relationships more important than others?"
        ],
        "medium": [
            "What's your strategy for showing both AMG's challenges and potential solutions?",
            "How did you decide where to position AMG in your map?",
            "What approach helps you show AMG's multiple impacts?",
            "How are you showing the difference between AMG's blocking and adapting functions?",
            "What's your strategy for showing the most critical AMG relationships?"
        ],
        "low": [
            "What's your overall strategy for organizing the AMG concept?",
            "How did you decide which AMG impacts to show first?",
            "What approach helps you structure AMG's relationships?",
            "Which AMG connections seem most important strategically?"
        ]
    },
    "metacognitive": {
        "high": [
            "As you look at your map now, which aspects of AMG do you feel you understand well, and which remain unclear? What makes the unclear parts challenging?",
            "How has your understanding of AMG's role in market entry evolved since you started? What specific insights about AMG have emerged through creating this map?",
            "Reflecting on the Veyra example, how well does your map capture similar dynamics? What aspects of AMG's impact might you be overlooking?",
            "If you had to explain AMG to another start-up founder, what key relationships from your map would you emphasize? What's still missing from that explanation?",
            "Looking at your map, how confident are you that you've captured how a start-up can successfully navigate AMG? What areas need more thought?",
            "What assumptions are you making about how AMG operates? How might challenging these assumptions change your concept map?"
        ],
        "medium": [
            "Which parts of AMG do you understand best? Which parts are still unclear?",
            "How has your understanding of AMG changed while creating this map?",
            "How well does your map explain the Veyra example?",
            "What AMG relationships would you emphasize to explain it to others?",
            "How confident are you about showing ways to navigate AMG?"
        ],
        "low": [
            "What do you understand best about AMG?",
            "What's still confusing about AMG's role?",
            "How has your thinking about AMG changed?",
            "What would you like to understand better about AMG?"
        ]
    }
}

# AMG-specific follow-up templates
AMG_SCAFFOLDING_FOLLOWUP_TEMPLATES = {
    "conceptual": [
        "That's an interesting connection. Given that understanding, how might AMG's other mechanisms (like network control or rule-changing) create similar conceptual relationships?",
        "Based on what you've identified, are there other concepts in your map that AMG might influence through the same principle?",
        "How does this AMG relationship you've described affect the start-up's strategic options? What conceptual implications follow?",
        "Interesting insight about AMG. How might this understanding help identify ways for the start-up to counter or adapt to AMG's effects?"
    ],
    "procedural": [
        "Good approach. Have you tried applying this same process to map out each of AMG's four mechanisms systematically?",
        "That's helpful. Would it be useful to create a checklist of AMG impacts to ensure you've covered all major areas?",
        "Based on your process, how might you systematically identify counter-strategies for each AMG mechanism?",
        "Interesting technique. How could you use this approach to show the temporal sequence of AMG's adaptive responses?"
    ],
    "strategic": [
        "That's a thoughtful strategy. How might reorganizing to highlight AMG's central gatekeeping role change the overall message of your map?",
        "Good strategic thinking. Given this approach, what would be the most effective way to show successful navigation paths through AMG barriers?",
        "Based on your strategy, how might grouping concepts by whether they're affected by AMG vs. those that counter AMG improve clarity?",
        "Interesting approach. How could your strategy better emphasize the dynamic, adaptive nature of AMG over time?"
    ],
    "metacognitive": [
        "That's valuable self-reflection. Based on this awareness, which aspect of AMG would benefit most from deeper exploration?",
        "Good insight into your learning. How might this understanding of AMG influence your approach to similar complex business concepts?",
        "Thoughtful assessment. Given what you've learned about AMG, what questions about market entry are you now able to answer?",
        "Interesting realization. How has understanding AMG changed your perspective on why start-ups fail in international expansion?"
    ]
}

# AMG-specific conclusion templates
AMG_SCAFFOLDING_CONCLUSION_TEMPLATES = {
    "conceptual": [
        "Your understanding of AMG's conceptual relationships shows good depth. In your next revision, consider exploring how AMG's {specific_mechanism} mechanism creates cascading effects across multiple concepts.",
        "The conceptual links between AMG and market entry factors are developing well. Focus next on showing how these relationships create feedback loops in the system.",
        "You've identified key AMG relationships. As you revise, consider adding concepts that show how start-ups can leverage their resources to counter specific AMG mechanisms."
    ],
    "procedural": [
        "The systematic approach to mapping AMG's impacts we discussed should help. Try starting with AMG's four mechanisms and methodically trace each one's effects in your next revision.",
        "Good progress on your mapping process. Remember to check that each AMG mechanism connects to relevant entry strategies and resources as you continue.",
        "The procedural techniques for showing AMG's influence are coming together. Focus on using consistent relationship labels that clearly indicate AMG's active role."
    ],
    "strategic": [
        "Your strategic approach to organizing AMG relationships shows thoughtful planning. Consider restructuring to emphasize paths through AMG barriers in your next iteration.",
        "The strategy for showing AMG's dual role (blocking and adapting) is developing. Next, focus on highlighting which relationships are most critical for successful market entry.",
        "Good strategic thinking about AMG's position in your map. As you revise, consider how to better show the temporal dynamics of AMG's adaptive responses."
    ],
    "metacognitive": [
        "Your reflection on understanding AMG shows strong metacognitive awareness. Use this insight to identify which AMG mechanisms need more exploration in your next revision.",
        "This self-assessment of your AMG understanding is valuable. Continue questioning your assumptions about how AMG operates as you develop your map further.",
        "Your evolving understanding of AMG's role is impressive. Keep tracking how your perspective on market entry challenges changes as you deepen your analysis."
    ]
}

# Configuration for AMG task
AMG_SCAFFOLDING_CONFIG = {
    "prompt_templates": AMG_SCAFFOLDING_PROMPT_TEMPLATES,
    "followup_templates": AMG_SCAFFOLDING_FOLLOWUP_TEMPLATES,
    "conclusion_templates": AMG_SCAFFOLDING_CONCLUSION_TEMPLATES,
    "task_context": {
        "main_concept": "Adaptive Market Gatekeeping (AMG)",
        "key_mechanisms": ["dynamic adaptation", "rule-changing", "network control", "resource blocking"],
        "example_company": "Veyra",
        "example_market": "Japanese market",
        "core_challenge": "navigating AMG barriers for successful market entry"
    },
    "concept_priorities": {
        "essential": ["AMG", "Entry Strategies", "Entry Barriers", "Start-up Resources"],
        "important": ["Market Analysis", "Target Markets", "Competitive Environment", "Legal Framework"],
        "supporting": ["Financing", "Marketing Strategy", "Success Factors"]
    },
    "relationship_suggestions": {
        "AMG_impacts": ["blocks", "restricts", "influences", "challenges", "prevents", "increases"],
        "counter_strategies": ["overcomes", "bypasses", "adapts to", "mitigates", "leverages"],
        "enabling": ["enables", "facilitates", "supports", "strengthens"],
        "causal": ["causes", "leads to", "results in", "triggers"]
    }
}
