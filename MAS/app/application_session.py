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
        Create randomized, non-repeating agent sequence.
        """
        agents = [
            "conceptual_scaffolding",
            "strategic_scaffolding", 
            "metacognitive_scaffolding",
            "procedural_scaffolding"
        ]
        
        random.shuffle(agents)
        return agents
    

    def get_agent_name(self, roundn):
        return self._agent_sequence[roundn-1].replace('_', ' ').title()

    def get_agent_response(self, roundn):
        agent = self._agent_sequence[roundn-1]
        return _demo_responses[agent]
    
