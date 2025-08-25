"""
Scaffolding Configuration

    Conceptual → Focus on the conceptual connections and their correctness in terms of content: what is it about? is this correct?
    Procedural → Focus on tool and resource handling, process orientation: which tools can I use? what steps can I take?
    Strategic → Focus on planing, order, structure and solution strategies and approaches: how can I solve this?
    Metacognitive → Focus on self-assessment, regulation, learning process on a meta-level: how can I improve this further? 

This module provides configuration for scaffolding, including prompt templates.
"""

# Scaffolding prompt templates for different scaffolding types and intensities
SCAFFOLDING_PROMPT_TEMPLATES = {
    "strategic": {
        "high": [
            "I notice that {observation}. Could you walk me through your process for organizing the concepts in your map? What was your overall strategy to solve the challenges that AMG imposes?",
            "Looking at your concept map, I see that {observation}. What approach did you use to decide which concepts to include first and how to arrange them?",
            "Your map has {node_count} concepts and {edge_count} relationships. What might be a logical next step in expanding this area?",
            "What strategy did you use to determine which relationships to include in your map? Are there other important connections you considered but didn't include?",
            # LÖSUNGSSTRATEGIEN & PROBLEMANSÄTZE
            "Looking at your challenge with {observation}, what strategy would be most effective here? Have you considered breaking this down into smaller, manageable problems?",
            "I see that {observation}. What approach would you take to tackle this systematically? Which problem-solving method fits best for this type of challenge?",
            "Your map shows {node_count} concepts. What's your strategy for prioritizing which areas to develop first? Which approach would give you the biggest impact?",
            "What problem-solving strategy did you use when deciding how to organize these relationships? Would an alternative approach work better?",
            "Looking at this complexity, what systematic approach could help you organize these concepts more effectively?",
            "How would you strategically approach integrating AMG across all these concepts? What's your game plan for ensuring comprehensive coverage?",
            # STRATEGISCHE PLANUNG & PRIORISIERUNG
            "What's your roadmap for expanding this concept map? Which areas deserve priority and why?",
            "Since you have only limited time, which strategic approach would you take to maximize the conceptual coverage?",
            "Looking at competing priorities in your map, how do you strategically balance depth versus breadth? What decision criteria are you using?",
            "What's your strategy for identifying the most critical relationships first? How do you prioritize connection-building?",
            "If you were to add one more important concept to your map that would help connect several existing concepts, what would it be and why?",
            "What additional concepts might be related to {concept} that aren't in your map yet?"
        ],
        "medium": [
            "I see that {observation}. What was your approach to organizing the concepts in your map?",
            "Looking at your concept map, what strategy did you use to decide which concepts to include?",
            "How did you decide which relationships to show between concepts in your map?",
            "What might be your next step in developing this concept map further?",
            "Have you considered alternative ways to organize these concepts? What might work better?"
        ]
    },
    "metacognitive": {
        "high": [
            # alt
            "As you look at your concept map now, which parts do you feel most confident about, and which parts are you less certain about?",
            "How has your understanding of {concept} changed since you started working on this concept map? What specific insights have you gained?",
            "If you were to explain what you've learned about this topic to someone else, what key points would you emphasize based on your concept map?",
            "What questions do you still have about this topic that aren't addressed in your current concept map?",
            "How would you assess your current understanding of the relationships between {concept} and {another_concept}? What areas might need more exploration?",
            # SELBSTMONITORING & VERSTÄNDNISKONTROLLE
            "How did you approach the organization of your concept map? What was your idea behind re-placing {concept}?",
            "As you review {observation}, how well do you understand the connections you've made?",
            "What's your internal gauge telling you about {concept}? Where do you feel solid versus uncertain?",
            "How are you monitoring whether your understanding of AMG is complete? What internal checks are you running?",
            "When you look at this relationship between {concept} and {another_concept}, how confident are you in your reasoning?",
            "What's your self-assessment of how well you understand the mechanisms behind these connections?",
            # LERNPROZESS-REFLEXION
            "How has your thinking evolved while working on this concept map? What mental shifts have you noticed?",
            "What strategies were you using to check your understanding as you build these relationships?",
            # SELBSTEVALUATION & ZIELSETZUNG
            "What criteria are you using to judge the quality of the concept map? How does it differ from the beginning?",
            "How do you monitor whether you're integrating new insights effectively into your existing understanding?"
        ],
        "medium": [
            "Which part of your concept map do you feel most confident about? Which part are you least confident about?",
            "How has your understanding of this topic changed as you've worked on this concept map?",
            "What was challenging about creating this concept map?",
            "What do you think is the most important relationship shown in your map? Why?",
            "What questions do you still have about this topic?"
        ]
    },
    "procedural": {
        "high": [
            # KONKRETE ARBEITSSCHRITTE & METHODEN
            "I notice that {observation}. Let me walk you through a systematic method for adding complex relationships: First identify the concepts, then determine the relationship type, then create the linking phrase.",
            "When creating relationships between concepts, follow this procedure: 1) Select your starting concept, 2) Brainstorm all possible connections, 3) Evaluate each connection's validity, 4) Create precise linking phrases. Which concept do you find challenging?",
            "Let's talk about your mapping flow. Did you start from AMG, trace each pathway, check for missing links, verify relationship labels? You managed to do that already with {concept}, can you think of another concept, that could fit in?",
            "To ensure AMG integration, follow these steps: 1) List all AMG mechanisms, 2) Check each concept for AMG relevance, 3) Create explicit AMG connections, 4) Verify comprehensive coverage. Which step needs attention?",
            # TOOL-NUTZUNG & TECHNISCHE SCHRITTE
            "Here's the step-by-step process for {concept} categorization: Identify themes, group it with related concepts, create category labels, organize spatially. Which step requires guidance?",
            "To check map completeness systematically: 1) List key course concepts, 2) Verify each appears in your map, 3) Check for adequate connections, 4) Identify gaps. Let's work through this process.",
            # alt
            "I notice that {observation}. Would you like some guidance on how to add more complex relationships between concepts in your map? What specific aspects of the concept mapping process are you finding challenging?",
            "Let's talk about your concept mapping workflow. How do you typically approach the process of creating and revising your map? Are there specific techniques you'd like help with?",
            "When reviewing your concept map, what systematic approach do you use to identify areas for improvement? Have you tried starting from one concept and tracing all its possible connections?",
            "What procedure do you follow to make sure each key factor is represented in your map?",
            "Have you tried grouping your concepts by categories (e.g., financial resources, environment, strategies)?",
            "When you revise your map, what steps do you take to check whether AMG is fully integrated?",
        ],
        "medium": [
            "I see that {observation}. Would you like some tips on how to add or label relationships between concepts?",
            "What process do you follow when creating your concept map?",
            "Have you tried reviewing your map systematically to identify missing connections?",
            "Are there any specific features of your concept mapping tool that you find challenging to use?",
            "How do you decide what type of relationship exists between two concepts?"
        ]
    },
    "conceptual": {
        "high": [
            # FACHINHALT & THEORETISCHES VERSTÄNDNIS
            "I notice that {observation}. The theoretical connection between '{concept}' and market entry barriers might relate to AMG's mechanism of resource blocking. How does this framework help explain what you're seeing?",
            "Your map shows {concept} but doesn't capture all underlying principles that AMG operates through dynamic adaptation yet. How might this core concept influence the relationships you've mapped?",
            "The concept of {concept} could relate to competitive advantages in international markets. How does this theoretical understanding change how you see these relationships?",
            "AMG as a theoretical construct involves four core mechanisms: dynamic adaptation, rule-changing, network control, and resource blocking. How does {concept} relate to any of these theoretical foundations?",
            "The relationship between {concept} and market success relates to established internationalization theory. What theoretical principles are underlying the connections you've made?",
            # PRINZIPIEN & MECHANISMEN
            "What fundamental business principle explains why {concept} and {another_concept} are connected in international market entry?",
            "Looking at your map, what core mechanism of market dynamics explains the relationship pattern you've created around {concept}?",
            "The concept of {concept} operates according to specific business principles. How do these principles manifest in your other mapped relationships?",
            "What underlying economic principle governs how {concept} influences market entry success under AMG conditions?",
            "The theoretical mechanism behind {concept} involves stakeholder dynamics. How does this principle connect to other concepts in your domain?",
            # alt
            "Your map includes {node_count} concepts. Can you explain your thinking behind the relationship between [concept A] and [concept B]? What meta-concept supports their connection?",
            "I'm curious about the area of your map dealing with {concept}. This seems important but could be developed further. What additional concepts might be related to this area?",
            "What might be some underlying principles or mechanisms that connect '{concept}' in your map? How do these deeper connections help explain the relationships you've shown?",
            "Looking at your map, how does AMG influence the relationship between {concept} and another factor (e.g., Financing or Legal Framework)?",
            "How does {concept} connect with the mechanisms of AMG (dynamic adaptation, rule-changing, network control, resource blocking)?",
            "What role does {concept} play in shaping international market entry under AMG?",
            "If you had to explain {concept} to someone new, what would be the three most important aspects to mention?",
            "What’s the link between {concept} and the success factors of international expansion?"
        ],
        "medium": [
            "I see that {observation}. How might the concepts '{concept}' and [another concept] relate to each other?",
            "Can you explain your thinking behind the relationship between these two concepts?",
            "Are there any underlying principles that connect multiple concepts in your map?",
            "How does {concept} influence or affect other concepts in your map?",
            "What does {concept} mean in the context of entering a new market?",
            "How is {concept} connected to AMG?",
            "Can you explain the difference between {concept} and one of the entry strategies?",
            "What underlying principle explains the relationship between {concept} and {another_concept}?",
            "How would you summarize the importance of {concept} for internationalization?"
        ]
    }
}

# Scaffolding follow-up templates for different scaffolding types
SCAFFOLDING_FOLLOWUP_TEMPLATES = {
    "strategic": [
        # STRATEGY REFINEMENT & ALTERNATIVE APPROACHES
        "That's an interesting strategy. Have you considered how this approach might work for tackling other complex areas in your map?",
        "Based on your approach, what alternative strategy might give you even better results here?",
        "Given this strategy worked well, how might you adapt it to prioritize the most impactful connections first?",
        "That's a solid approach. What would be your backup strategy if this method doesn't yield the connections you're looking for?",
        "Interesting problem-solving approach. How might you scale this strategy to handle the entire AMG integration systematically?",
        # STRATEGIC PLANNING & NEXT STEPS
        "Given your current strategy, what's your game plan for the next phase of development?",
        "That approach makes sense. How would you strategically sequence your next moves to maximize impact?",
        "Based on this strategy, which area deserves your immediate attention and which can wait?",
        "That's a thoughtful approach. How might you strategically balance expanding breadth versus deepening specific areas?",
        "Given your strategic thinking here, what criteria will you use to decide when you've achieved comprehensive coverage?",
        # STRATEGIC DECISION-MAKING
        "That's a logical approach. How did you decide this strategy would be more effective than alternative methods?",
        "Interesting strategic choice. What trade-offs are you making with this approach, and are you comfortable with them?",
        "Given competing priorities, how are you strategically deciding what to focus on first?"
    ],
    "metacognitive": [
        # SELF-MONITORING & CONFIDENCE ASSESSMENT
        "That's a thoughtful self-assessment. What internal signals are you using to gauge whether your understanding is solid or needs more work?",
        "Interesting reflection. How are you monitoring your comprehension as you build these complex relationships?",
        "Based on your self-evaluation, what specific indicators tell you when you truly understand a concept versus just surface-level familiarity?",
        "That's valuable self-awareness. How do you catch yourself when your confidence might be overriding actual understanding?",
        "Good reflection. What's your internal checkpoint system for verifying you really grasp these connections?",
        # LEARNING PROCESS REFLECTION
        "That's insightful about your learning process. What study strategies have you discovered work best for you in concept mapping?",
        "Interesting learning insight. How has your approach to processing complex information evolved through this exercise?",
        "That's a valuable realization. What mental strategies help you most when you encounter confusing or contradictory information?",
        "Good self-reflection. How do you regulate your learning when you notice your attention or understanding starting to fade?",
        "That's thoughtful self-analysis. What adjustments have you made to your learning approach based on what's working or not working?",      
        # GOAL-SETTING & PROGRESS EVALUATION
        "Based on your self-assessment, how would you revise your learning goals for the remaining work?",
        "That's honest self-evaluation. What criteria are you using to measure whether you're meeting your own learning standards?",
        "Given your reflection on progress, how do you decide when you're ready to move to more advanced relationships?",
        "That's good self-awareness. How do you balance pushing yourself versus recognizing when you need to consolidate your current understanding?"
    ],
    "procedural": [
        # SPECIFIC TECHNIQUES & METHODS
        "That makes sense. Let me walk you through a systematic technique for expanding that area - would that be helpful?",
        "Good point. There's a specific method for checking relationship completeness systematically. Want to try that approach?",
        "I understand. Here's a step-by-step process for that exact challenge: First..., then..., finally... Which step would you like to practice?",
        "That's a common issue. There's a particular workflow that helps with this - shall we go through it together?",
        "Makes sense. Let me show you the specific procedure for organizing hierarchical relationships more effectively.",
        # TOOL USAGE & TECHNICAL STEPS
        "Understood. Have you tried using the grouping features in your concept mapping tool to organize similar concepts together?",
        "That's helpful feedback. Are there specific tool functions that might streamline this process for you?",
        "I see. Would learning the keyboard shortcuts for quick relationship creation help speed up your workflow?",
        "Good to know. There are some advanced features that might help - want me to walk you through them step-by-step?",
        "That's useful information. Let's go through the specific steps for using templates or pre-made structures to organize your concepts.",
        # WORKFLOW OPTIMIZATION
        "Based on your experience, would a checklist approach help you systematically verify completeness?",
        "That's valuable input. Let's create a standard operating procedure for your concept map reviews - what steps should we include?",
        "Given that challenge, would a specific routine for adding and checking connections help streamline your process?",
        "I understand. There's a particular sequence that makes relationship-building more efficient. Want to try that method?"
    ],
    "conceptual": [
        # THEORETICAL UNDERSTANDING & PRINCIPLES
        "That's an insightful connection. How does this relationship fit with the core theoretical framework of internationalization theory?",
        "Interesting insight. What underlying business principle do you think explains why these concepts connect this way?",
        "That's a valuable understanding. How does this connect to the fundamental mechanisms of how AMG operates in markets?",
        "Good conceptual thinking. What theoretical foundation supports this relationship you've identified?",
        "That makes sense conceptually. How does this connection relate to established theories about market entry barriers?",
        # CONCEPT RELATIONSHIPS & MECHANISMS
        "That's a solid conceptual understanding. How might this same principle apply to other concept relationships in international business?",
        "Interesting conceptual insight. What core mechanism explains how these different factors influence each other?",
        "That's thoughtful analysis. How does understanding this concept change your grasp of the overall AMG framework?",
        "Good conceptual reasoning. What evidence from business theory or practice supports this particular relationship?",
        "That's a strong conceptual connection. How do the underlying dynamics here mirror other market phenomena you know?",
        # MEANING & SIGNIFICANCE
        "That's a nuanced understanding. How would you explain the significance of this concept to someone new to international business?",
        "Interesting conceptual grasp. What's the essential meaning that makes this concept so important for market entry success?",
        "That's insightful. How does mastering this concept enhance your overall understanding of the AMG challenge?",
        "Good conceptual analysis. What makes this particular relationship between concepts so crucial for practical application?",
        "That's thoughtful interpretation. How does this conceptual understanding illuminate the broader patterns in your map?"
    ]
}

# Scaffolding conclusion templates for different scaffolding types
SCAFFOLDING_CONCLUSION_TEMPLATES = {
    "strategic": [
        "Thank you for sharing your strategic approach to concept mapping. Consider how organizing concepts by {specific_approach} might help clarify the relationships in your next revision.",
        "Your strategy for concept mapping reveals thoughtful planning. As you revise, consider how grouping related concepts might make the process even clearer.",
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
