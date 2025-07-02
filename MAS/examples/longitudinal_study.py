"""
Longitudinal Study Example

This script demonstrates how to run a longitudinal study by tracking a learner's progress
over multiple sessions.
"""

import json
import os
import sys
from pathlib import Path
import time
import datetime
import copy

# Add the parent directory to the Python path to import the MAS package
sys.path.append(str(Path(__file__).parent.parent))

from MAS.mas_system import MultiAgentScaffoldingSystem
from utils.visualization import plot_concept_map

# Sample concept maps for longitudinal study (representing progression over time)
LEARNER_PROGRESSION = [
    {
        "session": 1,
        "date": "2025-01-15",
        "topic": "Climate Change - Initial Understanding",
        "data": {
            "nodes": [
                "Climate Change",
                "Global Warming",
                "Carbon Emissions",
                "Fossil Fuels"
            ],
            "edges": [
                {"source": "Fossil Fuels", "target": "Carbon Emissions", "relation": "produces"},
                {"source": "Carbon Emissions", "target": "Global Warming", "relation": "causes"},
                {"source": "Global Warming", "target": "Climate Change", "relation": "leads to"}
            ]
        }
    },
    {
        "session": 2,
        "date": "2025-01-22",
        "topic": "Climate Change - Week 2",
        "data": {
            "nodes": [
                "Climate Change",
                "Global Warming",
                "Carbon Emissions",
                "Fossil Fuels",
                "Renewable Energy",
                "Greenhouse Effect"
            ],
            "edges": [
                {"source": "Fossil Fuels", "target": "Carbon Emissions", "relation": "produces"},
                {"source": "Carbon Emissions", "target": "Greenhouse Effect", "relation": "enhances"},
                {"source": "Greenhouse Effect", "target": "Global Warming", "relation": "causes"},
                {"source": "Global Warming", "target": "Climate Change", "relation": "is part of"},
                {"source": "Renewable Energy", "target": "Carbon Emissions", "relation": "reduces"}
            ]
        }
    },
    {
        "session": 3,
        "date": "2025-01-29",
        "topic": "Climate Change - Week 3",
        "data": {
            "nodes": [
                "Climate Change",
                "Global Warming",
                "Carbon Emissions",
                "Fossil Fuels",
                "Renewable Energy",
                "Greenhouse Effect",
                "Sea Level Rise",
                "Extreme Weather"
            ],
            "edges": [
                {"source": "Fossil Fuels", "target": "Carbon Emissions", "relation": "produces"},
                {"source": "Carbon Emissions", "target": "Greenhouse Effect", "relation": "enhances"},
                {"source": "Greenhouse Effect", "target": "Global Warming", "relation": "causes"},
                {"source": "Global Warming", "target": "Climate Change", "relation": "is part of"},
                {"source": "Climate Change", "target": "Sea Level Rise", "relation": "causes"},
                {"source": "Climate Change", "target": "Extreme Weather", "relation": "increases"},
                {"source": "Renewable Energy", "target": "Carbon Emissions", "relation": "reduces"}
            ]
        }
    },
    {
        "session": 4,
        "date": "2025-02-05",
        "topic": "Climate Change - Week 4",
        "data": {
            "nodes": [
                "Climate Change",
                "Global Warming",
                "Carbon Emissions",
                "Fossil Fuels",
                "Renewable Energy",
                "Greenhouse Effect",
                "Sea Level Rise",
                "Extreme Weather",
                "Deforestation",
                "Ocean Acidification",
                "Biodiversity Loss"
            ],
            "edges": [
                {"source": "Fossil Fuels", "target": "Carbon Emissions", "relation": "produces"},
                {"source": "Carbon Emissions", "target": "Greenhouse Effect", "relation": "enhances"},
                {"source": "Greenhouse Effect", "target": "Global Warming", "relation": "causes"},
                {"source": "Global Warming", "target": "Climate Change", "relation": "is part of"},
                {"source": "Climate Change", "target": "Sea Level Rise", "relation": "causes"},
                {"source": "Climate Change", "target": "Extreme Weather", "relation": "increases"},
                {"source": "Climate Change", "target": "Ocean Acidification", "relation": "leads to"},
                {"source": "Deforestation", "target": "Carbon Emissions", "relation": "increases"},
                {"source": "Deforestation", "target": "Biodiversity Loss", "relation": "causes"},
                {"source": "Ocean Acidification", "target": "Biodiversity Loss", "relation": "contributes to"},
                {"source": "Renewable Energy", "target": "Carbon Emissions", "relation": "reduces"}
            ]
        }
    }
]

# Expert concept map for comparison
EXPERT_CONCEPT_MAP = {
    "nodes": [
        "Climate Change",
        "Global Warming",
        "Carbon Emissions",
        "Fossil Fuels",
        "Renewable Energy",
        "Greenhouse Effect",
        "Sea Level Rise",
        "Extreme Weather",
        "Deforestation",
        "Ocean Acidification",
        "Biodiversity Loss",
        "Carbon Sequestration",
        "Methane",
        "Permafrost Melting",
        "Feedback Loops",
        "Policy Interventions",
        "Climate Justice"
    ],
    "edges": [
        {"source": "Fossil Fuels", "target": "Carbon Emissions", "relation": "produces"},
        {"source": "Carbon Emissions", "target": "Greenhouse Effect", "relation": "enhances"},
        {"source": "Greenhouse Effect", "target": "Global Warming", "relation": "causes"},
        {"source": "Global Warming", "target": "Climate Change", "relation": "is part of"},
        {"source": "Climate Change", "target": "Sea Level Rise", "relation": "causes"},
        {"source": "Climate Change", "target": "Extreme Weather", "relation": "increases frequency of"},
        {"source": "Climate Change", "target": "Ocean Acidification", "relation": "leads to"},
        {"source": "Deforestation", "target": "Carbon Emissions", "relation": "increases"},
        {"source": "Deforestation", "target": "Biodiversity Loss", "relation": "causes"},
        {"source": "Ocean Acidification", "target": "Biodiversity Loss", "relation": "contributes to"},
        {"source": "Renewable Energy", "target": "Carbon Emissions", "relation": "reduces"},
        {"source": "Carbon Sequestration", "target": "Carbon Emissions", "relation": "reduces"},
        {"source": "Methane", "target": "Greenhouse Effect", "relation": "contributes to"},
        {"source": "Permafrost Melting", "target": "Methane", "relation": "releases"},
        {"source": "Global Warming", "target": "Permafrost Melting", "relation": "causes"},
        {"source": "Permafrost Melting", "target": "Feedback Loops", "relation": "creates"},
        {"source": "Feedback Loops", "target": "Climate Change", "relation": "accelerates"},
        {"source": "Policy Interventions", "target": "Carbon Emissions", "relation": "regulates"},
        {"source": "Climate Justice", "target": "Policy Interventions", "relation": "informs"}
    ]
}

# Learner profile
LEARNER_PROFILE = {
    "id": "learner123",
    "name": "Alex Johnson",
    "background": "Undergraduate student in Environmental Science",
    "prior_knowledge": "I have a basic understanding of climate change from high school science classes.",
    "experience": "I've read some news articles about climate change but haven't studied it formally.",
    "goals": "I want to understand the causes and effects of climate change more deeply.",
    "confidence": "I'm somewhat confident in my understanding of the basic concepts.",
    "interests": "I'm particularly interested in solutions to climate change and renewable energy."
}

def create_sample_config():
    """
    Create a sample configuration for the longitudinal study.
    
    Returns:
        Sample configuration
    """
    config = {
        "max_rounds": 1,  # Only one round per session in longitudinal study
        "agents": {
            "lead": {
                "type": "lead",
                "name": "Lead Agent",
                "enabled": True
            },
            "learner_profiling": {
                "type": "learner_profiling",
                "name": "Learner Profiling Agent",
                "enabled": True
            },
            "strategic_scaffolding": {
                "type": "strategic_scaffolding",
                "name": "Strategic Scaffolding Agent",
                "enabled": True
            },
            "conceptual_scaffolding": {
                "type": "conceptual_scaffolding",
                "name": "Conceptual Scaffolding Agent",
                "enabled": True
            },
            "metacognitive_scaffolding": {
                "type": "metacognitive_scaffolding",
                "name": "Metacognitive Scaffolding Agent",
                "enabled": True
            },
            "procedural_scaffolding": {
                "type": "procedural_scaffolding",
                "name": "Procedural Scaffolding Agent",
                "enabled": True
            },
            "example_map": {
                "type": "example_map",
                "name": "Example Map Agent",
                "enabled": True
            },
            "content_ingestion": {
                "type": "content_ingestion",
                "name": "Content Ingestion Agent",
                "enabled": True
            }
        },
        "design_features": {
            "df1_learner_profiling": True,
            "df2_scaffolding": True,
            "df3_example_map": True,
            "df4_content_ingestion": True
        },
        "logging": {
            "log_dir": "logs",
            "log_level": "INFO"
        },
        "output_dir": "output"
    }
    
    return config

def run_session(system, session_data, output_dir, previous_sessions=None):
    """
    Run a session in the longitudinal study.
    
    Args:
        system: The multi-agent scaffolding system
        session_data: Data for the current session
        output_dir: Output directory
        previous_sessions: Data from previous sessions
        
    Returns:
        Session result and analysis
    """
    session_num = session_data["session"]
    session_date = session_data["date"]
    concept_map = session_data["data"]
    
    print(f"\n=== Session {session_num} ({session_date}) ===\n")
    
    # Save concept map as JSON
    json_path = os.path.join(output_dir, f"session_{session_num}_map.json")
    with open(json_path, 'w') as f:
        json.dump(concept_map, f, indent=2)
    
    # Plot concept map
    plot_path = os.path.join(output_dir, f"session_{session_num}_map.png")
    plot_concept_map(concept_map, plot_path)
    
    print(f"Processing concept map for session {session_num}")
    print(f"Nodes: {len(concept_map['nodes'])}, Edges: {len(concept_map['edges'])}")
    
    # Reset session state for new session
    system.session_state["current_round"] = 0
    
    # If this is not the first session, add previous maps to session state
    if previous_sessions:
        system.session_state["previous_concept_maps"] = [s["data"] for s in previous_sessions]
    else:
        system.session_state["previous_concept_maps"] = []
    
    # Directly update system's session state with the concept map
    system.session_state["current_concept_map"] = concept_map
    
    # Create input data for agents
    input_data = {
        "type": "concept_map_submission",
        "concept_map_data": concept_map,
        "pdf_path": json_path,  # Using JSON path as a stand-in for PDF path
        "round": system.session_state["current_round"],
        "session": session_num,
        "date": session_date
    }
    
    # Process with lead agent
    context = {"session_state": system.session_state}
    result = system.lead_agent.process(input_data, context)
    
    # Update session state
    if "session_state_updates" in result:
        system.session_state.update(result["session_state_updates"])
    
    # Save agent responses
    responses_path = os.path.join(output_dir, f"session_{session_num}_responses.json")
    with open(responses_path, 'w') as f:
        json.dump(result.get("agent_responses", {}), f, indent=2)
    
    # Save session summary
    summary_path = os.path.join(output_dir, f"session_{session_num}_summary.txt")
    with open(summary_path, 'w') as f:
        f.write(f"Session {session_num} ({session_date})\n")
        f.write(f"Topic: {session_data['topic']}\n")
        f.write(f"Nodes: {len(concept_map['nodes'])}, Edges: {len(concept_map['edges'])}\n\n")
        
        f.write("Agent Feedback:\n\n")
        
        responses = result.get("agent_responses", {})
        for agent_type, response in responses.items():
            if response:
                f.write(f"[{agent_type.replace('_', ' ').title()}]\n\n")
                f.write(response)
                f.write("\n\n" + "-" * 80 + "\n\n")
    
    # Analyze progress compared to previous sessions
    progress_analysis = analyze_progress(session_data, previous_sessions)
    
    # Save progress analysis
    analysis_path = os.path.join(output_dir, f"session_{session_num}_progress_analysis.json")
    with open(analysis_path, 'w') as f:
        json.dump(progress_analysis, f, indent=2)
    
    print(f"Session {session_num} completed")
    print(f"Results saved to {output_dir}")
    
    return result, progress_analysis

def analyze_progress(current_session, previous_sessions):
    """
    Analyze progress between sessions.
    
    Args:
        current_session: Current session data
        previous_sessions: Previous session data
        
    Returns:
        Progress analysis
    """
    if not previous_sessions:
        # First session, no progress to analyze
        return {
            "session": current_session["session"],
            "date": current_session["date"],
            "nodes": len(current_session["data"]["nodes"]),
            "edges": len(current_session["data"]["edges"]),
            "expert_coverage": {
                "nodes": len(current_session["data"]["nodes"]) / len(EXPERT_CONCEPT_MAP["nodes"]),
                "edges": len(current_session["data"]["edges"]) / len(EXPERT_CONCEPT_MAP["edges"])
            }
        }
    
    # Get previous session
    previous_session = previous_sessions[-1]
    
    # Calculate changes
    new_nodes = set(current_session["data"]["nodes"]) - set(previous_session["data"]["nodes"])
    removed_nodes = set(previous_session["data"]["nodes"]) - set(current_session["data"]["nodes"])
    
    # Convert edges to comparable format
    current_edges = {(edge["source"], edge["target"], edge.get("relation", "")) 
                    for edge in current_session["data"]["edges"]}
    previous_edges = {(edge["source"], edge["target"], edge.get("relation", "")) 
                     for edge in previous_session["data"]["edges"]}
    
    new_edges = current_edges - previous_edges
    removed_edges = previous_edges - current_edges
    
    # Calculate coverage of expert map
    expert_nodes = set(EXPERT_CONCEPT_MAP["nodes"])
    expert_edges = {(edge["source"], edge["target"], edge.get("relation", "")) 
                   for edge in EXPERT_CONCEPT_MAP["edges"]}
    
    node_coverage = len(set(current_session["data"]["nodes"]) & expert_nodes) / len(expert_nodes)
    edge_coverage = len(current_edges & expert_edges) / len(expert_edges)
    
    # Create analysis
    analysis = {
        "session": current_session["session"],
        "date": current_session["date"],
        "nodes": len(current_session["data"]["nodes"]),
        "edges": len(current_session["data"]["edges"]),
        "changes_since_previous": {
            "new_nodes": list(new_nodes),
            "removed_nodes": list(removed_nodes),
            "new_edges": [{"source": e[0], "target": e[1], "relation": e[2]} for e in new_edges],
            "removed_edges": [{"source": e[0], "target": e[1], "relation": e[2]} for e in removed_edges],
            "node_change": len(current_session["data"]["nodes"]) - len(previous_session["data"]["nodes"]),
            "edge_change": len(current_session["data"]["edges"]) - len(previous_session["data"]["edges"])
        },
        "expert_coverage": {
            "nodes": node_coverage,
            "edges": edge_coverage
        }
    }
    
    return analysis

def generate_longitudinal_report(session_analyses, output_dir):
    """
    Generate a longitudinal report based on session analyses.
    
    Args:
        session_analyses: List of session analyses
        output_dir: Output directory
    """
    # Create report data
    report_data = {
        "learner": LEARNER_PROFILE,
        "sessions": session_analyses,
        "progress_over_time": {
            "nodes": [analysis["nodes"] for analysis in session_analyses],
            "edges": [analysis["edges"] for analysis in session_analyses],
            "node_coverage": [analysis["expert_coverage"]["nodes"] for analysis in session_analyses],
            "edge_coverage": [analysis["expert_coverage"]["edges"] for analysis in session_analyses]
        }
    }
    
    # Save report data
    report_data_path = os.path.join(output_dir, "longitudinal_report_data.json")
    with open(report_data_path, 'w') as f:
        json.dump(report_data, f, indent=2)
    
    # Generate text report
    report_path = os.path.join(output_dir, "longitudinal_report.txt")
    with open(report_path, 'w') as f:
        f.write("Multi-Agent Scaffolding System - Longitudinal Study Report\n")
        f.write("=" * 80 + "\n\n")
        
        f.write("Learner Profile:\n")
        f.write(f"  ID: {LEARNER_PROFILE['id']}\n")
        f.write(f"  Name: {LEARNER_PROFILE['name']}\n")
        f.write(f"  Background: {LEARNER_PROFILE['background']}\n\n")
        
        f.write("Session Summary:\n\n")
        
        for i, analysis in enumerate(session_analyses):
            session_num = analysis["session"]
            session_date = analysis["date"]
            
            f.write(f"Session {session_num} ({session_date}):\n")
            f.write(f"  Nodes: {analysis['nodes']}, Edges: {analysis['edges']}\n")
            f.write(f"  Expert Coverage: {analysis['expert_coverage']['nodes']:.2%} of nodes, {analysis['expert_coverage']['edges']:.2%} of edges\n")
            
            if i > 0:
                changes = analysis["changes_since_previous"]
                f.write(f"  Changes since previous session:\n")
                f.write(f"    Added nodes: {len(changes['new_nodes'])}\n")
                f.write(f"    Removed nodes: {len(changes['removed_nodes'])}\n")
                f.write(f"    Added edges: {len(changes['new_edges'])}\n")
                f.write(f"    Removed edges: {len(changes['removed_edges'])}\n")
            
            f.write("\n")
        
        f.write("\nLearning Progression Analysis:\n\n")
        
        # Calculate overall growth
        first_session = session_analyses[0]
        last_session = session_analyses[-1]
        
        node_growth = last_session["nodes"] - first_session["nodes"]
        edge_growth = last_session["edges"] - first_session["edges"]
        node_coverage_growth = last_session["expert_coverage"]["nodes"] - first_session["expert_coverage"]["nodes"]
        edge_coverage_growth = last_session["expert_coverage"]["edges"] - first_session["expert_coverage"]["edges"]
        
        f.write(f"Overall Growth:\n")
        f.write(f"  Nodes: {node_growth} ({node_growth / first_session['nodes']:.2%} increase)\n")
        f.write(f"  Edges: {edge_growth} ({edge_growth / first_session['edges']:.2%} increase)\n")
        f.write(f"  Expert Node Coverage: {node_coverage_growth:.2%} increase\n")
        f.write(f"  Expert Edge Coverage: {edge_coverage_growth:.2%} increase\n\n")
        
        # Identify key learning moments
        if len(session_analyses) > 1:
            max_node_growth_session = max(range(1, len(session_analyses)), 
                                         key=lambda i: session_analyses[i]["nodes"] - session_analyses[i-1]["nodes"])
            max_edge_growth_session = max(range(1, len(session_analyses)), 
                                         key=lambda i: session_analyses[i]["edges"] - session_analyses[i-1]["edges"])
            
            f.write(f"Key Learning Moments:\n")
            f.write(f"  Most significant concept growth occurred in Session {session_analyses[max_node_growth_session]['session']}\n")
            f.write(f"  Most significant relationship growth occurred in Session {session_analyses[max_edge_growth_session]['session']}\n\n")
        
        f.write("\nConclusion:\n\n")
        
        if node_growth > 0 and edge_growth > 0:
            f.write("The learner has shown significant progress throughout the longitudinal study, ")
            f.write("demonstrating an expanding understanding of both concepts and relationships in the domain. ")
            
            if last_session["expert_coverage"]["nodes"] > 0.7 and last_session["expert_coverage"]["edges"] > 0.6:
                f.write("By the final session, the learner has developed a comprehensive understanding that closely aligns with expert knowledge.")
            elif last_session["expert_coverage"]["nodes"] > 0.5 and last_session["expert_coverage"]["edges"] > 0.4:
                f.write("By the final session, the learner has developed a good understanding of the domain, though there are still areas for further development.")
            else:
                f.write("While progress has been made, there are still significant opportunities for the learner to develop a more comprehensive understanding of the domain.")
        else:
            f.write("The learner's concept map has not shown significant growth in terms of quantity, ")
            
            if last_session["expert_coverage"]["nodes"] > first_session["expert_coverage"]["nodes"]:
                f.write("but there has been improvement in the quality and alignment with expert understanding.")
            else:
                f.write("and alignment with expert understanding remains an area for improvement.")
    
    print(f"Longitudinal report generated at {report_path}")

def main():
    """
    Main function for the longitudinal study example.
    """
    print("Multi-Agent Scaffolding System - Longitudinal Study Example")
    
    # Create output directory
    output_dir = "examples/output/longitudinal_study"
    os.makedirs(output_dir, exist_ok=True)
    
    # Create and save sample configuration
    config = create_sample_config()
    config["output_dir"] = output_dir
    
    config_path = os.path.join(output_dir, "config.json")
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"Created sample configuration at {config_path}")
    
    # Save learner profile
    profile_path = os.path.join(output_dir, "learner_profile.json")
    with open(profile_path, 'w') as f:
        json.dump(LEARNER_PROFILE, f, indent=2)
    
    # Initialize system
    system = MultiAgentScaffoldingSystem(config_path)
    print("Initialized multi-agent scaffolding system")
    
    # Set expert concept map for the example map agent
    for agent_id, agent in system.agents.items():
        if agent.agent_type == "example_map":
            agent.set_example_map(EXPERT_CONCEPT_MAP)
            print("Set expert concept map for comparison")
    
    # Simulate learner profile input
    print("Collecting learner profile information...")
    
    # Create input data for agents
    input_data = {
        "type": "learner_profile",
        "learner_responses": {
            "prior_knowledge": LEARNER_PROFILE["prior_knowledge"],
            "experience": LEARNER_PROFILE["experience"],
            "goals": LEARNER_PROFILE["goals"],
            "confidence": LEARNER_PROFILE["confidence"],
            "interests": LEARNER_PROFILE["interests"]
        }
    }
    
    # Process with lead agent
    context = {"session_state": system.session_state}
    result = system.lead_agent.process(input_data, context)
    
    # Update session state
    if "session_state_updates" in result:
        system.session_state.update(result["session_state_updates"])
    
    print("Learner profile collected and ZPD estimated.")
    
    # Run each session
    previous_sessions = []
    session_analyses = []
    
    for session_data in LEARNER_PROGRESSION:
        # Create session-specific output directory
        session_output_dir = os.path.join(output_dir, f"session_{session_data['session']}")
        os.makedirs(session_output_dir, exist_ok=True)
        
        # Run session
        result, analysis = run_session(system, session_data, session_output_dir, previous_sessions)
        
        # Add to previous sessions for next iteration
        previous_sessions.append(session_data)
        session_analyses.append(analysis)
        
        # Add a small delay between sessions
        time.sleep(1)
    
    # Generate longitudinal report
    generate_longitudinal_report(session_analyses, output_dir)
    
    print("\nLongitudinal study completed. Check the output directory for results.")

if __name__ == "__main__":
    main()
