from dataclasses import dataclass, asdict, field
from typing import List, Dict, Optional
from datetime import datetime

"""
Contains declarations for the data classes for data transfer between dthe databank and the apllication.

Data transfer can be done via standard python dictionaries, so these dtos might be removed later.
"""

@dataclass 
class Profile:
    background: str 
    knowledge:  str 
    interests:  str 
    goals: str


@dataclass
class UserProfile:
    username: str  
    password: bytes
    profile:  Profile


@dataclass
class Concept:
    id: str
    text: str
    x: int
    y: int


@dataclass
class Relationship:
    id: str
    source: str
    target: str
    text: str


@dataclass
class ConceptMap:
    concepts: List[Concept]
    relationships: List[Relationship]
    action_history: List = field(default_factory=list)
    interaction_metrics: Dict = field(default_factory=dict)
    session_timing: Dict = field(default_factory=dict)
    timestamp: str = ""
    source_format: str = ""


@dataclass
class ConceptMapStep:
    round: int
    timestamp: str
    agent_type: str
    concept_map: ConceptMap
    action_history: List = field(default_factory=list)
    interaction_metrics: Dict = field(default_factory=dict)
    session_timing: Dict = field(default_factory=dict)


@dataclass
class Message:
    speaker: str
    agent_type: Optional[str]
    message: str
    timestamp: str
    metadata: Dict


@dataclass
class Session:
    session_id: str
    start_time: str
    end_time: str
    total_duration_seconds: float
    agent_sequence: List[str]
    used_agents: List[str]
    concept_map_evolution: List[ConceptMapStep]
    current_concept_map: ConceptMap
    final_concept_map: ConceptMap
    conversation_history: Dict[str, List[Message]]
    mode: str
    total_rounds: int
    rounds: list = field(default_factory=list)
    learner_profile: Dict = field(default_factory=dict)
    inserted_at: str = field(default_factory=lambda: 
                             datetime.utcnow().isoformat())


def deep_asdict(obj):
    if isinstance(obj, list):
        return [deep_asdict(i) for i in obj]
    elif hasattr(obj, "__dataclass_fields__"):
        return {k: deep_asdict(v) for k, v in asdict(obj).items()}
    else:
        return obj
