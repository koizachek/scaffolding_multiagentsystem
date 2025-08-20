import random
from typing import List

_demo_responses = {
    "conceptual_scaffolding": "Let's explore the conceptual relationships in your map. How do these concepts connect to form a coherent understanding?",
    "strategic_scaffolding": "Consider the strategic organization of your concept map. What's the most effective way to structure these ideas?",
    "metacognitive_scaffolding": "Reflect on your thinking process. How confident are you about these relationships? What might you be missing?",
    "procedural_scaffolding": "Let's focus on the procedural aspects. What steps or processes are represented in your concept map?"
}


class ApplicationSession:
    """
    Manages a complete interactive session through the scaffoldding web application.
    """

    def __init__(self) -> None:
        self._agent_sequence = self.initialize_agent_sequence() 


    @staticmethod 
    def initialize_agent_sequence() -> List[str]:
        """
        Create hardcoded agent sequence for experimental consistency.
        """
        # ideal order (no randomization)
        agents = [
            "conceptual_scaffolding",    # Round 1 - always first
            "procedural_scaffolding",     # Round 2 - always second
            "strategic_scaffolding",      # Round 3 - always third
            "metacognitive_scaffolding"   # Round 4 - always fourth
        ]
        
        # Note: Round 0 is handled separately (no scaffolding agent)
        # No shuffling - hardcoded order for experimental consistency
        return agents
    

    def get_agent_name(self, roundn):
        # Round 0 is special - no scaffolding agent
        if roundn == 0:
            return "Initial Map Creation (No Scaffolding)"
        
        # Adjust for 0-based indexing after round 0
        agent_index = roundn - 1
        if agent_index < len(self._agent_sequence):
            return self._agent_sequence[agent_index].replace('_', ' ').title()
        return "Unknown Agent"

    def get_agent_response(self, roundn):
        # Handle round 0 specially - no scaffolding
        if roundn == 0:
            return "Please create your initial concept map on the topic. Take your time to include all the concepts and relationships you think are relevant. When you're ready, submit your concept map to proceed."
        
        # Adjust for agent sequence after round 0
        agent_index = roundn - 1
        if agent_index >= len(self._agent_sequence):
            return "Session completed. Thank you for participating!"
        
        agent = self._agent_sequence[agent_index]
        return _demo_responses[agent]
