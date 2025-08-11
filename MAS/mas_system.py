"""
Multi-Agent Scaffolding System

This module provides the main system class for the multi-agent scaffolding system.
It initializes the system, creates the agents, and handles the interaction flow.
"""

import json
import logging
import os
import sys
import time
import random
import csv
import threading
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from MAS.agents.agent_factory import create_agents_from_config
from MAS.agents.base_agent import BaseAgent
from MAS.utils.logging_utils import setup_logging, SessionLogger
from MAS.utils.pdf_parser import parse_pdf_to_json
from MAS.utils.visualization import plot_concept_map
from MAS.utils.ai_api import AIManager
from MAS.utils.mermaid_parser import MermaidParser
from MAS.utils.session_timer import RoundManager
from MAS.core.scaffolding_engine import ScaffoldingEngine
from MAS.core.dialogue_manager import DialogueManager
from MAS.core.enhanced_io_manager import create_experimental_handlers, ExperimentalIOManager

logger = logging.getLogger(__name__)

class MultiAgentScaffoldingSystem:
    """
    Main system class for the multi-agent scaffolding system.
    
    This class initializes the system, creates the agents, and handles the interaction flow.
    """
    
    def __init__(self, config_path: str = "config.json", mode: str = "demo", participant_id: Optional[str] = None):
        """
        Initialize the multi-agent scaffolding system.
        
        Args:
            config_path: Path to the configuration file
            mode: "demo" for simulation or "experimental" for real user study
            participant_id: Unique participant identifier for experimental mode
        """
        # Load configuration
        self.config = self._load_config(config_path)
        
        # Setup logging
        log_config = self.config.get("logging", {})
        self.log_file = setup_logging(
            log_dir=log_config.get("log_dir", "logs"),
            log_level=log_config.get("log_level", "INFO")
        )
        
        logger.info("Initializing multi-agent scaffolding system")
        
        # Initialize session state
        self.session_state = {
            "current_round": 0,
            "max_rounds": self.config.get("max_rounds", 4),
            "learner_profile": {},
            "zpd_estimate": {},
            "previous_concept_maps": [],
            "current_concept_map": None,
            "uploaded_materials": [],
            "active_design_features": self._get_active_design_features(),
            "interactive_scaffolding": self.config.get("session", {}).get("interactive_scaffolding", True),
            "require_reflection": self.config.get("session", {}).get("require_reflection", True),
            "user_responses": [],
            "pending_reflection": False
        }
        
        # Create agents
        self.agents = create_agents_from_config(self.config, self._log_agent_action)
        
        # Get lead agent
        self.lead_agent = self._get_lead_agent()
        if not self.lead_agent:
            raise ValueError("No lead agent found in configuration")
        
        # Initialize enhanced I/O manager for experimental features
        self.experimental_io_manager = None
        self.enhanced_input_handler = None
        self.enhanced_output_handler = None
        
        # Initialize scaffolding engine and dialogue manager
        self.scaffolding_engine = ScaffoldingEngine(self.config, self.lead_agent)
        self.dialogue_manager = DialogueManager(
            self.config,
            self._handle_user_input,
            self._handle_system_output
        )
        
        # Register scaffolding engine and dialogue manager with lead agent
        if hasattr(self.lead_agent, 'scaffolding_engine') and hasattr(self.lead_agent, 'dialogue_manager'):
            self.lead_agent.scaffolding_engine = self.scaffolding_engine
            self.lead_agent.dialogue_manager = self.dialogue_manager
        
        # Initialize experimental mode
        self._init_experimental_mode(mode, participant_id)
        
        logger.info("Multi-agent scaffolding system initialized")
    
    def _init_experimental_mode(self, mode: str = "demo", participant_id: Optional[str] = None) -> None:
        """
        Initialize experimental mode with enhanced capabilities.
        
        Args:
            mode: "demo" for simulation or "experimental" for real user study
            participant_id: Unique participant identifier for experimental mode
        """
        self.mode = mode
        self.participant_id = participant_id
        
        # Initialize experimental components
        if mode == "experimental":
            # Initialize OpenAI manager
            ai_manager_config = self.config.get("ai_manager", {})
            self.ai_manager = AIManager(ai_manager_config)
            
            # Initialize Mermaid parser
            self.mermaid_parser = MermaidParser()
            
            # Initialize round manager
            experimental_config = self.config.get("experimental", {})
            self.round_manager = RoundManager(
                total_rounds=experimental_config.get("max_rounds", 4),
                round_duration_minutes=experimental_config.get("round_duration_minutes", 7),
                break_duration_minutes=experimental_config.get("break_duration_minutes", 2)
            )
            
            # Initialize session data
            self.session_rounds = []
            self.agent_sequence = []
            # Set up log file path and session logger
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            self.session_logger = SessionLogger(log_dir="logs", session_id=f"mas_{timestamp}")
            self.log_file = self.session_logger.log_path
#            log_filename = f"logs/mas_{timestamp}.log"
#            self.log_file = log_filename  
#            self.session_logger = SessionLogger(self.log_file)

            logger.info(f"Experimental mode initialized for participant: {participant_id}")
            
        else:
            # Demo mode - no real API calls
            self.ai_manager = None
            self.mermaid_parser = MermaidParser()  # Still need parser for demo
            self.round_manager = None
            self.session_logger = None
            self.session_rounds = []
            self.agent_sequence = []
            
            logger.info("Demo mode initialized")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """
        Load the configuration from a JSON file.
        
        Args:
            config_path: Path to the configuration file
            
        Returns:
            The loaded configuration
        """
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            logger.info(f"Loaded configuration from {config_path}")
            return config
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            # Return default configuration
            return {
                "max_rounds": 4,
                "agents": {
                    "lead": {
                        "type": "lead",
                        "name": "Lead Agent",
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
                }
            }
    
    def _get_active_design_features(self) -> Dict[str, bool]:
        """
        Get the active design features from the configuration.
        
        Returns:
            Dictionary of design features and their activation status
        """
        design_features = self.config.get("design_features", {})
        
        # Ensure all design features have a value
        default_features = {
            "df1_learner_profiling": True,
            "df2_scaffolding": True,
            "df3_example_map": True,
            "df4_content_ingestion": True
        }
        
        # Update default features with configured values
        for feature, enabled in design_features.items():
            default_features[feature] = enabled
        
        return default_features
    
    def _get_lead_agent(self) -> Optional[BaseAgent]:
        """
        Get the lead agent from the created agents.
        
        Returns:
            The lead agent, or None if not found
        """
        for agent_id, agent in self.agents.items():
            if agent.agent_type == "lead":
                return agent
        return None
    
    def _log_agent_action(self, 
                         agent_id: str, 
                         action_type: str, 
                         details: Dict[str, Any]) -> None:
        """
        Log an agent action.
        
        Args:
            agent_id: ID of the agent
            action_type: Type of action
            details: Action details
        """
        log_entry = {
            "timestamp": details.get("timestamp"),
            "agent_id": agent_id,
            "agent_type": details.get("agent_type"),
            "action_type": action_type,
            "input": details.get("input"),
            "output": details.get("output"),
            "reasoning": details.get("reasoning"),
            "zpd_estimate": details.get("zpd_estimate"),
            "active_design_features": self.session_state.get("active_design_features")
        }
        
        logger.info(f"Agent action: {agent_id} - {action_type}")
        
        # In a real implementation, this would write to a structured log file
    
    def process_concept_map(self, pdf_path: str) -> Dict[str, Any]:
        """
        Process a concept map PDF.
        
        Args:
            pdf_path: Path to the concept map PDF
            
        Returns:
            Processing result
        """
        logger.info(f"Processing concept map: {pdf_path}")
        
        try:
            # Parse PDF to JSON
            concept_map_data = parse_pdf_to_json(pdf_path)
            
            # Visualize concept map
            output_dir = self.config.get("output_dir", "output")
            os.makedirs(output_dir, exist_ok=True)
            
            output_path = os.path.join(
                output_dir, 
                f"concept_map_round_{self.session_state['current_round']}.png"
            )
            
            plot_concept_map(concept_map_data, output_path)
            
            # Store concept map in session state
            if self.session_state.get("current_concept_map"):
                self.session_state["previous_concept_maps"].append(
                    self.session_state["current_concept_map"]
                )
            
            # Update current concept map
            self.session_state["current_concept_map"] = concept_map_data
            
            # Save concept map as JSON
            json_output_path = os.path.join(
                output_dir, 
                f"concept_map_round_{self.session_state['current_round']}.json"
            )
            
            with open(json_output_path, 'w') as f:
                json.dump(concept_map_data, f, indent=2)
            
            # Create input data for agents
            input_data = {
                "type": "concept_map_submission",
                "concept_map_data": concept_map_data,
                "pdf_path": pdf_path,
                "round": self.session_state["current_round"]
            }
            
            # Process with lead agent
            context = {"session_state": self.session_state}
            result = self.lead_agent.process(input_data, context)
            
            # Update session state
            if "session_state" in result:
                self.session_state = result["session_state"]
            elif "session_state_updates" in result:
                self.session_state.update(result["session_state_updates"])
            
            # Increment round counter if not already incremented by lead agent
            if "current_round" not in result.get("session_state_updates", {}) and "session_state" not in result:
                self.session_state["current_round"] += 1
            
            return result
        
        except Exception as e:
            logger.error(f"Error processing concept map: {e}")
            return {
                "status": "error",
                "message": f"Error processing concept map: {str(e)}"
            }
    
    def initialize_agent_sequence(self, participant_id: Optional[str] = None) -> List[str]:
        """
        Generate randomized agent sequence for experimental validity.
        
        Args:
            participant_id: Participant identifier for logging
            
        Returns:
            Randomized list of agent types
        """
        scaffolding_agents = [
            "conceptual_scaffolding",
            "strategic_scaffolding", 
            "metacognitive_scaffolding",
            "procedural_scaffolding"
        ]
        
        # Randomize order per participant
        random.shuffle(scaffolding_agents)
        
        self.agent_sequence = scaffolding_agents
        self.session_state["agent_sequence"] = scaffolding_agents
        
        # Log the randomized sequence
        logger.info(f"Agent sequence for participant {participant_id}: {scaffolding_agents}")
        
        if self.session_logger:
            self.session_logger.log_agent_sequence(participant_id, scaffolding_agents)
        
        return scaffolding_agents
    
    def set_active_agent(self, agent_type: str) -> None:
        """
        Set the active agent for the current round.
        
        Args:
            agent_type: Type of agent to activate
        """
        if agent_type in self.agents:
            self.active_agent = self.agents[agent_type]
            self.session_state["active_agent"] = agent_type
            logger.info(f"Active agent set to: {agent_type}")
        else:
            logger.error(f"Agent type not found: {agent_type}")
            raise ValueError(f"Agent type not found: {agent_type}")
    
    def conduct_scaffolding_interaction(self, 
                                      concept_map: Dict[str, Any], 
                                      round_number: int) -> Dict[str, Any]:
        """
        Conduct time-limited scaffolding interaction.
        
        Args:
            concept_map: Current concept map
            round_number: Round number (0-based)
            
        Returns:
            Interaction results
        """
        if self.mode == "demo":
            return self._simulate_interaction(concept_map, round_number)
        else:
            return self._real_interaction(concept_map, round_number)
    
    def _simulate_interaction(self, 
                            concept_map: Dict[str, Any], 
                            round_number: int) -> Dict[str, Any]:
        """
        Simulate scaffolding interaction for demo mode.
        
        Args:
            concept_map: Current concept map
            round_number: Round number
            
        Returns:
            Simulated interaction results
        """
        # Get active agent for this round
        if round_number < len(self.agent_sequence):
            agent_type = self.agent_sequence[round_number]
        else:
            agent_type = "conceptual_scaffolding"  # Default fallback
        
        # Simulate agent response
        simulated_responses = {
            "conceptual_scaffolding": "I notice your concept map shows some interesting connections. Can you tell me more about how these concepts relate to each other?",
            "strategic_scaffolding": "Let's think about how to organize your concept map more effectively. What's the main theme you're trying to represent?",
            "metacognitive_scaffolding": "How confident do you feel about the relationships you've drawn? What areas might need more thought?",
            "procedural_scaffolding": "Let me help you with the technical aspects of concept mapping. Have you considered using different types of connections?"
        }
        
        response = simulated_responses.get(agent_type, "How can I help you improve your concept map?")
        
        return {
            "agent_type": agent_type,
            "response": response,
            "round_number": round_number,
            "concept_map_nodes": len(concept_map.get("concepts", [])),
            "concept_map_edges": len(concept_map.get("relationships", [])),
            "simulation": True
        }
    
    def _real_interaction(self, 
                        concept_map: Dict[str, Any], 
                        round_number: int) -> Dict[str, Any]:
        """
        Conduct real scaffolding interaction with OpenAI.
        
        Args:
            concept_map: Current concept map
            round_number: Round number
            
        Returns:
            Real interaction results
        """
        # Set active agent for this round
        agent_type = self.agent_sequence[round_number]
        self.set_active_agent(agent_type)
        
        # Start round timer
        round_start_time = time.time()
        
        if self.round_manager:
            self.round_manager.timer.start_round(round_number, self._handle_round_timeout)
        
        print(f"\n=== Round {round_number + 1} ===")
        print(f"Active Agent: {agent_type.replace('_', ' ').title()}")
        print(f"Time Limit: 7 minutes")
        
        # Initialize round data
        round_data = {
            "round_number": round_number,
            "agent_type": agent_type,
            "start_time": datetime.now().isoformat(),
            "concept_map": concept_map,
            "exchanges": [],
            "agent_outputs": [],
            "user_responses": []
        }
        
        # Generate initial scaffolding prompt
        context = {"round_number": round_number}
        api_result = self.ai_manager.generate_scaffolding_response(
            agent_type.replace("_scaffolding", ""), concept_map, context=context
        )
        
        initial_response = api_result["response"]
        round_data["agent_outputs"].append({
            "text": initial_response,
            "timestamp": datetime.now().isoformat(),
            "type": "initial_prompt",
            "model_used": api_result.get("model_used"),
            "tokens_used": api_result.get("tokens_used")
        })
        
        print(f"\n🤖 {agent_type.replace('_', ' ').title()} Agent:")
        print(initial_response)
        
        # Interaction loop
        exchange_count = 0
        while (self.round_manager and self.round_manager.timer.is_round_active()):
            exchange_count += 1
            
            # Get user response
            user_response = input(f"\n💬 Your response (Exchange {exchange_count}): ")
            
            if not user_response.strip():
                continue
            
            round_data["user_responses"].append({
                "text": user_response,
                "timestamp": datetime.now().isoformat(),
                "exchange_number": exchange_count
            })
            
            # Generate agent follow-up
            api_result = self.ai_manager.generate_scaffolding_response(
                agent_type.replace("_scaffolding", ""), 
                concept_map, 
                user_response=user_response,
                context=context
            )
            
            agent_followup = api_result["response"]
            round_data["agent_outputs"].append({
                "text": agent_followup,
                "timestamp": datetime.now().isoformat(),
                "type": "followup",
                "exchange_number": exchange_count,
                "model_used": api_result.get("model_used"),
                "tokens_used": api_result.get("tokens_used")
            })
            
            print(f"\n🤖 {agent_type.replace('_', ' ').title()} Agent:")
            print(agent_followup)
            
            # Check for time remaining
            if self.round_manager:
                remaining = self.round_manager.timer.get_round_time_remaining()
                if remaining <= 60:  # Last minute warning
                    print(f"\n⚠️  Only {remaining} seconds remaining!")
        
        # End round
        if self.round_manager:
            timing_data = self.round_manager.timer.stop_round()
            round_data.update(timing_data)
        
        round_data["end_time"] = datetime.now().isoformat()
        round_data["exchange_count"] = exchange_count
        
        # Store round data
        self.session_rounds.append(round_data)
        
        # Log round completion
        if self.session_logger:
            self.session_logger.log_round_completion(round_number, round_data)
        
        return round_data
    
    def _handle_round_timeout(self):
        """Handle round timeout."""
        if self.round_manager:
            print(f"\n⏰ Time's up! Round {self.round_manager.current_round_number + 1} has ended.")
    
    def conduct_experimental_session(self, participant_id: str) -> Dict[str, Any]:
        """
        Conduct complete experimental session with breaks and timing.
        
        Args:
            participant_id: Unique participant identifier
            
        Returns:
            Complete session results
        """
        if self.mode != "experimental":
            raise ValueError("Experimental session requires experimental mode")
        
        print(f"🧪 Starting experimental session for participant: {participant_id}")
        
        # Initialize session
        self.participant_id = participant_id
        self.initialize_agent_sequence(participant_id)
        
        if self.round_manager:
            self.round_manager.start_session()
        
        # Conduct 4 rounds
        for round_num in range(4):
            print(f"\n=== Round {round_num + 1} ===")
            print(f"Active Agent: {self.agent_sequence[round_num]}")
            
            # Get concept map input
            concept_map = self._get_concept_map_input(round_num)
            
            # Conduct scaffolding interaction
            round_result = self.conduct_scaffolding_interaction(concept_map, round_num)
            
            # 2-minute break (except after last round)
            if round_num < 3:
                self._conduct_break_period()
        
        # Generate final exports
        session_summary = self._export_session_data(participant_id)
        
        print(f"\n✅ Session completed for participant: {participant_id}")
        return session_summary
    
    def _get_concept_map_input(self, round_num: int) -> Dict[str, Any]:
        """
        Get concept map from participant via Mermaid syntax.
        
        Args:
            round_num: Round number
            
        Returns:
            Parsed concept map
        """
        print(f"\n📝 Please enter your concept map for Round {round_num + 1}")
        print("Use Mermaid.js syntax (e.g., 'graph TD\\n    A[Concept] --> B[Another]')")
        print("Enter 'DONE' on a new line when finished:")
        
        mermaid_lines = []
        while True:
            line = input()
            if line.strip() == "DONE":
                break
            mermaid_lines.append(line)
        
        mermaid_text = "\n".join(mermaid_lines)
        
        # Parse Mermaid to internal format
        concept_map = self.mermaid_parser.parse_mermaid_to_concept_map(mermaid_text)
        
        return concept_map
    
    def _conduct_break_period(self):
        """2-minute break with countdown."""
        if self.round_manager:
            self.round_manager.timer.start_break()
            
            # Wait for break to complete
            while self.round_manager.timer.is_break_active():
                time.sleep(1)
    
    def _export_session_data(self, participant_id: str) -> Dict[str, Any]:
        """
        Export session data in both JSON and CSV formats.
        
        Args:
            participant_id: Participant identifier
            
        Returns:
            Export summary
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # JSON Export (complete session data)
        json_filename = f"experimental_data_{participant_id}_{timestamp}.json"
        self._export_json_data(json_filename)
        
        # CSV Export (flattened for analysis)
        csv_filename = f"experimental_results_{participant_id}_{timestamp}.csv"
        self._export_csv_data(csv_filename)
        
        print(f"📊 Data exported:")
        print(f"   JSON: {json_filename}")
        print(f"   CSV: {csv_filename}")
        
        return {
            "participant_id": participant_id,
            "json_file": json_filename,
            "csv_file": csv_filename,
            "total_rounds": len(self.session_rounds),
            "session_completed": True
        }
    
    def _export_json_data(self, filename: str):
        """Export complete session data as JSON."""
        session_data = {
            "participant_id": self.participant_id,
            "agent_sequence": self.agent_sequence,
            "session_start": self.round_manager.timer.session_start_time.isoformat() if self.round_manager and self.round_manager.timer.session_start_time else None,
            "rounds": self.session_rounds,
            "ai_usage": self.ai_manager.get_usage_stats() if self.ai_manager else None,
            "export_timestamp": datetime.now().isoformat()
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False)
    
    def _export_csv_data(self, filename: str):
        """Export flattened data for statistical analysis."""
        csv_data = []
        
        for round_data in self.session_rounds:
            round_num = round_data["round_number"]
            concept_map = round_data["concept_map"]
            nodes = concept_map.get("concepts", [])
            edges = concept_map.get("relationships", [])
            
            # Create base row data
            base_row = {
                "participant_id": self.participant_id,
                "round_number": round_num,
                "agent_type": round_data["agent_type"],
                "agent_sequence": ",".join(self.agent_sequence),
                "round_duration_seconds": round_data.get("duration_seconds", 0),
                "exchange_count": round_data.get("exchange_count", 0),
                "node_count": len(nodes),
                "edge_count": len(edges),
                "mermaid_source": concept_map.get("mermaid_source", "")
            }
            
            # Add node data
            for i, node in enumerate(nodes):
                row = base_row.copy()
                row.update({
                    "element_type": "node",
                    "element_index": i,
                    "element_id": node.get("id", ""),
                    "element_text": node.get("text", ""),
                    "element_x": node.get("x", ""),
                    "element_y": node.get("y", "")
                })
                csv_data.append(row)
            
            # Add edge data
            for i, edge in enumerate(edges):
                row = base_row.copy()
                row.update({
                    "element_type": "edge",
                    "element_index": i,
                    "element_id": edge.get("id", ""),
                    "element_text": edge.get("text", ""),
                    "source_id": edge.get("source", ""),
                    "target_id": edge.get("target", "")
                })
                csv_data.append(row)
            
            # Add agent output data
            for i, output in enumerate(round_data.get("agent_outputs", [])):
                row = base_row.copy()
                row.update({
                    "element_type": "agent_output",
                    "element_index": i,
                    "element_text": output.get("text", ""),
                    "output_type": output.get("type", ""),
                    "model_used": output.get("model_used", ""),
                    "tokens_used": output.get("tokens_used", 0)
                })
                csv_data.append(row)
        
        # Write CSV file
        if csv_data:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = csv_data[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(csv_data)
    
    def process_scaffolding_response(self, 
                                   agent_response: str, 
                                   user_feedback: Optional[str] = None) -> Dict[str, Any]:
        """
        Process scaffolding response and user feedback.
        
        Args:
            agent_response: Agent's scaffolding response
            user_feedback: Optional user feedback
            
        Returns:
            Processing results
        """
        logger.info("Processing scaffolding response")
        
        # Store the interaction
        interaction_data = {
            "timestamp": datetime.now().isoformat(),
            "agent_response": agent_response,
            "user_feedback": user_feedback,
            "round": self.session_state.get("current_round", 0)
        }
        
        # Add to session state
        if "scaffolding_interactions" not in self.session_state:
            self.session_state["scaffolding_interactions"] = []
        
        self.session_state["scaffolding_interactions"].append(interaction_data)
        
        return {
            "status": "success",
            "interaction_logged": True,
            "total_interactions": len(self.session_state.get("scaffolding_interactions", []))
        }
    
    def process_material_upload(self, 
                               file_path: str, 
                               material_type: str, 
                               material_name: str) -> Dict[str, Any]:
        """
        Process an uploaded material.
        
        Args:
            file_path: Path to the uploaded file
            material_type: Type of material
            material_name: Name of the material
            
        Returns:
            Processing result
        """
        logger.info(f"Processing material upload: {material_name} ({material_type})")
        
        try:
            # Read file data
            with open(file_path, 'rb') as f:
                material_data = f.read()
            
            # Create input data for agents
            input_data = {
                "type": "material_upload",
                "material_data": material_data,
                "material_type": material_type,
                "material_name": material_name,
                "file_path": file_path,
                "timestamp": None  # In a real implementation, this would be a timestamp
            }
            
            # Process with lead agent
            context = {"session_state": self.session_state}
            result = self.lead_agent.process(input_data, context)
            
            # Update session state
            if "session_state_updates" in result:
                self.session_state.update(result["session_state_updates"])
            
            # Store material in session state
            self.session_state["uploaded_materials"].append({
                "name": material_name,
                "type": material_type,
                "path": file_path
            })
            
            return result
        
        except Exception as e:
            logger.error(f"Error processing material upload: {e}")
            return {
                "status": "error",
                "message": f"Error processing material upload: {str(e)}"
            }
    
    def finalize_session(self) -> Dict[str, Any]:
        """
        Finalize the session and generate summary feedback.
        
        Returns:
            Finalization result
        """
        logger.info("Finalizing session")
        
        try:
            # Create input data for agents
            input_data = {
                "type": "final_round",
                "concept_map_data": self.session_state.get("current_concept_map")
            }
            
            # Process with lead agent
            context = {"session_state": self.session_state}
            result = self.lead_agent.process(input_data, context)
            
            # Generate session log
            self._generate_session_log()
            
            return result
        
        except Exception as e:
            logger.error(f"Error finalizing session: {e}")
            return {
                "status": "error",
                "message": f"Error finalizing session: {str(e)}"
            }
    
    def _generate_session_log(self) -> None:
        """Generate a comprehensive session log."""
        logger.info("Generating session log")
        
        # In a real implementation, this would generate a structured log file
        logger.info(f"Session completed: {self.session_state['current_round']} rounds")
        logger.info(f"Active design features: {self.session_state['active_design_features']}")
    
    def _handle_user_input(self, prompt: str) -> str:
        """Handle user input."""
        return input(prompt)
    
    def _handle_system_output(self, text: str) -> None:
        """Handle system output."""
        print(text)
    
    def get_session_state(self) -> Dict[str, Any]:
        """Get the current session state."""
        return self.session_state
    
    def get_agents(self) -> Dict[str, BaseAgent]:
        """Get all agents in the system."""
        return self.agents
    
    def get_config(self) -> Dict[str, Any]:
        """Get the system configuration."""
        return self.config
