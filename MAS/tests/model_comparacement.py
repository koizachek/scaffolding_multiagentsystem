"""
Upon calling the script generates scaffolding responses using different clients/models for future comparacement.
The agent sequence as well as the concept maps for each round are pregenerated.
Exports response data into a JSON file.
"""

import json, os, sys
from time import perf_counter
from textwrap import indent
from datetime import datetime
from typing import Any, Dict, List


# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    from MAS.utils.ai_api import AIManager
except ImportError as e:
    import sys, os
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, parent_dir)

    from utils.ai_api import AIManager


agent_sequence = [
    "conceptual_scaffolding",
    "strategic_scaffolding", 
    "metacognitive_scaffolding",
    "procedural_scaffolding"
]

cmdatas = [
    { "concepts": [{"text": "Vulcanic Erruption"}, {"text": "Temperature Rising"}],
      "relationships": [{"source": "Vulcanic Erruption", "target": "Temperature Rising", "text": "leads to"}] },
    
    { "concepts": [{"text": "Vulcanic Erruption"}, {"text": "Temperature Rising"}, {"text": "Carbon Gas Emissions"}],
      "relationships": [{"source": "Vulcanic Erruption",   "target": "Carbon Gas Emissions", "text": "leads to"},
                        {"source": "Carbon Gas Emissions", "target": "Temperature Rising", "text": "result in" }] },

    { "concepts": [{"text": "Vulcanic Erruption"},   {"text": "Temperature Rising"}, {"text": "Carbon Gas Emissions"}, 
                   {"text": "Icebergs Melting Down"}, {"text": "Animal Species Dying"}],
      "relationships": [{"source": "Vulcanic Erruption",   "target": "Carbon Gas Emissions",  "text": "leads to"},
                        {"source": "Carbon Gas Emissions", "target": "Temperature Rising",    "text": "result in" },
                        {"source": "Carbon Gas Emissions", "target": "Animal Species Dying",  "text": "harden living conditions for animals"},
                        {"source": "Temperature Rising",   "target": "Animal Species Dying",  "text": "creates impossible living conditions"},
                        {"source": "Temperature Rising",   "target": "Icebergs Melting Donw", "text": "correlates directly with"}] },

    { "concepts": [{"text": "Vulcanic Erruption"},   {"text": "Temperature Rising"}, {"text": "Carbon Gas Emissions"}, 
                   {"text": "Icebergs Melting Down"}, {"text": "Animal Species Dying"}, {"text": "Metallurgic Industries"},
                   {"text": "Industrial Animal Farms"}, {"text": "Terraforming"}, {"text": "Falling Down Big Forests"}],
      "relationships": [{"source": "Vulcanic Erruption",   "target": "Carbon Gas Emissions",  "text": "leads to"},
                        {"source": "Carbon Gas Emissions", "target": "Temperature Rising",    "text": "result in" },
                        {"source": "Carbon Gas Emissions", "target": "Animal Species Dying",  "text": "harden living conditions for animals"},
                        {"source": "Temperature Rising",   "target": "Animal Species Dying",  "text": "creates impossible living conditions"},
                        {"source": "Temperature Rising",   "target": "Icebergs Melting Donw", "text": "correlates directly with"}] },
]

# Insert models supported by Groq client that need to be analyzed into this list
# Supported models: https://console.groq.com/settings/limits
groq_models = [
    "deepseek-r1-distill-llama-70b",
    "gemma2-9b-it",
    "llama-3.1-8b-instant",
    "llama-3.3-70b-versatile",
    "compound-beta",
    "openai/gpt-oss-120b",
    "qwen/qwen3-32b"
]

# Insert models supported by Open Router client that need to be analyzed into this list
# Supported models: https://openrouter.ai/models?fmt=table&input_modalities=text&order=pricing-low-to-high
open_router_models = [
    "openai/gpt-oss-20b:free",
    "qwen/qwen3-30b-a3b:free",
    "moonshotai/kimi-k2:free",
    "google/gemma-3n-e2b-it:free",
    "rekaai/reka-flash-3:free"
]

groq_configs = [{ "client": "groq", "primary_model": model } for model in groq_models]
open_router_configs = [{ "client": "open_router", "primary_model": model } for model in open_router_models ]


def generate_model_responses() -> List[Dict[Any, Any]]:
    """
    Simulates experimental scaffolding sessions for all requested models.
    Collects response data provided by the AIManager.

    Returns:
        List containig responses for scaffolding session for each requested ai model.
    """
    model_responses = []
    configs = groq_configs + open_router_configs
    for config in configs:
        model_response_sequence = {
                "client": config['client'], 
                "model": config['primary_model'],
                "rounds": [] }
        manager = AIManager(config)
        context = { "round_number": 0 }
        start_time = perf_counter()
        
        for agent, cmdata in zip(agent_sequence, cmdatas):
            response = manager.generate_scaffolding_response(
                    scaffolding_type=agent, 
                    concept_map=cmdata,
                    context=context) 
            
            model_response_sequence["rounds"].append({
                "agent": agent,
                "fallback_occured": response['fallback_occurred'], 
                "message": response['response'] })
            context["round_number"] += 1
        
        model_response_sequence["total_tokens"] = manager.total_tokens
        model_response_sequence["time_taken"]   = perf_counter() - start_time
        model_responses.append(model_response_sequence)
        
    return model_responses


def main() -> None:
    """
    Performs sessions generation and saves the results into a new JSON file.
    """
    responses = generate_model_responses()
    with open(f'comparacement_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json', 'w') as f:
        try: json.dump(responses, f, indent=1)
        except Exception as e:
            raise Exception(e)


if __name__ == "__main__":
    main()
