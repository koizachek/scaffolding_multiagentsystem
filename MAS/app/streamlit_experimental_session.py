"""
Streamlit-adapted Experimental Session for Multi-Agent Scaffolding System

This module adapts the InteractiveExperimentalSession for use with Streamlit,
providing the same research-grade functionality through a web interface.
"""

import os
import sys
import json
import random
import streamlit as st
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    from MAS.mas_system import MultiAgentScaffoldingSystem
    from MAS.utils.openai_api import OpenAIManager
    from MAS.utils.logging_utils import SessionLogger
    from MAS.utils.mermaid_parser import MermaidParser
except ImportError:
    # Fallback for when running from app directory
    import sys
    import os
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, parent_dir)
    
    from mas_system import MultiAgentScaffoldingSystem
    from utils.openai_api import OpenAIManager
    from utils.logging_utils import SessionLogger
    from utils.mermaid_parser import MermaidParser

class StreamlitExperimentalSession:
    """Manages a complete interactive experimental session through Streamlit."""
    
    def __init__(self):
        self.system = None
        self.session_data = {
            "session_id": f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "start_time": datetime.now().isoformat(),
            "learner_profile": {},
            "agent_sequence": [],
            "used_agents": [],
            "rounds": [],
            "concept_map_evolution": [],
            "current_concept_map": {"concepts": [], "relationships": []},
            "mode": None
        }
        self.openai_manager = None
        self.session_logger = None
        self.mermaid_parser = MermaidParser()
    
    def initialize_system(self, mode: str, participant_id: Optional[str] = None):
        """Initialize the MAS system with the specified mode."""
        try:
            self.session_data["mode"] = mode
            
            # Initialize system
            config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json")
            self.system = MultiAgentScaffoldingSystem(
                config_path=config_path,
                mode=mode,
                participant_id=participant_id or f"participant_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )
            
            # Initialize OpenAI manager for experimental mode
            if mode == "experimental":
                try:
                    openai_config = self.system.config.get("openai", {})
                    self.openai_manager = OpenAIManager(openai_config)
                    
                    # Initialize session logger
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    self.session_logger = SessionLogger(
                        log_dir="MAS/logs", 
                        session_id=f"streamlit_session_{timestamp}"
                    )
                    
                    # Log session start
                    self.session_logger.log_session_start({
                        "mode": mode,
                        "participant_id": participant_id,
                        "interface": "streamlit"
                    })
                    
                except Exception as e:
                    st.error(f"Failed to initialize OpenAI integration: {e}")
                    st.info("Falling back to demo mode")
                    self.session_data["mode"] = "demo"
                    self.openai_manager = None
                    self.session_logger = None
            
            return True
            
        except Exception as e:
            st.error(f"Failed to initialize system: {e}")
            return False
    
    def create_learner_profile_form(self) -> Dict[str, Any]:
        """Create learner profile through Streamlit form."""
        st.header("📋 Learner Profile Creation")
        st.markdown("Please complete your learner profile to personalize your scaffolding experience.")
        
        with st.form("learner_profile_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Name*", help="Your name or identifier")
                background = st.text_area(
                    "Educational/Professional Background*", 
                    help="Brief description of your educational or professional background"
                )
                prior_knowledge = st.text_area(
                    "Prior Knowledge*", 
                    help="What prior knowledge do you have about the topic you'll be mapping?"
                )
            
            with col2:
                confidence = st.selectbox(
                    "Confidence in Concept Mapping*",
                    options=["1 - Very Low", "2 - Low", "3 - Moderate", "4 - High", "5 - Very High"],
                    help="How confident do you feel about concept mapping?"
                )
                interests = st.text_area(
                    "Main Interests*", 
                    help="What are your main interests or areas of focus?"
                )
                goals = st.text_area(
                    "Learning Goals*", 
                    help="What do you hope to achieve in this session?"
                )
            
            submitted = st.form_submit_button("Create Profile", type="primary")
            
            if submitted:
                # Validate required fields
                if not all([name, background, prior_knowledge, confidence, interests, goals]):
                    st.error("Please fill in all required fields marked with *")
                    return None
                
                profile = {
                    "name": name.strip(),
                    "background": background.strip(),
                    "prior_knowledge": prior_knowledge.strip(),
                    "confidence": confidence,
                    "interests": interests.strip(),
                    "goals": goals.strip(),
                    "zpd_level": "medium",  # Always initialize at medium level
                    "created_at": datetime.now().isoformat()
                }
                
                # Store in session data
                self.session_data["learner_profile"] = profile
                
                # Log profile creation
                if self.session_logger:
                    self.session_logger.log_event(
                        event_type="learner_profile_created",
                        metadata={"profile": profile}
                    )
                
                st.success(f"✅ Profile created for {profile['name']}")
                st.info(f"📊 ZPD Level initialized: {profile['zpd_level']}")
                
                return profile
        
        return None
    
    def initialize_agent_sequence(self) -> List[str]:
        """Create randomized, non-repeating agent sequence."""
        agents = [
            "conceptual_scaffolding",
            "strategic_scaffolding", 
            "metacognitive_scaffolding",
            "procedural_scaffolding"
        ]
        
        # Randomize the order
        random.shuffle(agents)
        
        self.session_data["agent_sequence"] = agents
        
        # Log the randomized sequence
        if self.session_logger:
            self.session_logger.log_event(
                event_type="agent_sequence_initialized",
                metadata={
                    "agent_sequence": agents,
                    "participant_id": self.session_data["learner_profile"].get("name", "unknown")
                }
            )
        
        return agents
    
    def get_agent_name(self, roundn: int) -> str:
        """Get formatted agent name for display."""
        if roundn < len(self.session_data["agent_sequence"]):
            agent_type = self.session_data["agent_sequence"][roundn]
            return agent_type.replace('_', ' ').title()
        return "Unknown Agent"
    
    def convert_streamlit_to_internal_format(self, streamlit_cm_data) -> Dict[str, Any]:
        """Convert Streamlit concept map format to internal format."""
        concepts = []
        relationships = []
        
        # Handle different input types
        if streamlit_cm_data is None:
            # Return empty structure for None input
            pass
        elif isinstance(streamlit_cm_data, str):
            # Handle string input (might be JSON or initial map format)
            try:
                if streamlit_cm_data.strip():
                    parsed_data = json.loads(streamlit_cm_data)
                    if isinstance(parsed_data, dict):
                        streamlit_cm_data = parsed_data
                    else:
                        # If it's not a valid dict after parsing, treat as empty
                        streamlit_cm_data = {}
                else:
                    streamlit_cm_data = {}
            except (json.JSONDecodeError, AttributeError):
                # If JSON parsing fails, treat as empty concept map
                streamlit_cm_data = {}
        elif not isinstance(streamlit_cm_data, dict):
            # If it's not a dict, string, or None, treat as empty
            streamlit_cm_data = {}
        
        # Process the data if it's now a dictionary
        if isinstance(streamlit_cm_data, dict) and "elements" in streamlit_cm_data:
            for element in streamlit_cm_data["elements"]:
                data = element.get("data", {})
                
                # Check if it's a node (has id but no source/target)
                if "id" in data and "source" not in data and "target" not in data:
                    concepts.append({
                        "id": data["id"],
                        "text": data.get("label", ""),
                        "x": data.get("x", 0),
                        "y": data.get("y", 0)
                    })
                
                # Check if it's an edge (has source and target)
                elif "source" in data and "target" in data:
                    relationships.append({
                        "id": data.get("id", f"{data['source']}-{data['target']}"),
                        "source": data["source"],
                        "target": data["target"],
                        "text": data.get("label", "")
                    })
        
        return {
            "concepts": concepts,
            "relationships": relationships,
            "timestamp": datetime.now().isoformat(),
            "source_format": "streamlit"
        }
    
    def get_agent_response(self, roundn: int, concept_map_data: Optional[Dict[str, Any]] = None, user_response: Optional[str] = None, conversation_turn: int = 0) -> str:
        """Get agent response for the current round."""
        if roundn >= len(self.session_data["agent_sequence"]):
            return "Session completed. Thank you for participating!"
        
        agent_type = self.session_data["agent_sequence"][roundn]
        
        # Demo responses fallback
        demo_responses = {
            "conceptual_scaffolding": "Let's explore the conceptual relationships in your map. How do these concepts connect to form a coherent understanding?",
            "strategic_scaffolding": "Consider the strategic organization of your concept map. What's the most effective way to structure these ideas?",
            "metacognitive_scaffolding": "Reflect on your thinking process. How confident are you about these relationships? What might you be missing?",
            "procedural_scaffolding": "Let's focus on the procedural aspects. What steps or processes are represented in your concept map?"
        }
        
        # Try OpenAI integration for experimental mode
        if self.session_data["mode"] == "experimental" and self.openai_manager:
            try:
                # Safely convert concept map data to internal format with robust error handling
                internal_format = {"concepts": [], "relationships": []}
                
                if concept_map_data is not None:
                    try:
                        # Handle different data types safely
                        if isinstance(concept_map_data, dict):
                            if "elements" in concept_map_data:
                                internal_format = self.convert_streamlit_to_internal_format(concept_map_data)
                            elif "concepts" in concept_map_data and "relationships" in concept_map_data:
                                # Already in internal format
                                internal_format = concept_map_data
                            else:
                                # Unknown dict format, try conversion anyway
                                internal_format = self.convert_streamlit_to_internal_format(concept_map_data)
                        elif isinstance(concept_map_data, str):
                            # Try to parse string data
                            internal_format = self.convert_streamlit_to_internal_format(concept_map_data)
                        else:
                            # Unknown type, log and use empty format
                            if self.session_logger:
                                self.session_logger.log_event(
                                    event_type="concept_map_type_warning",
                                    metadata={
                                        "round_number": roundn,
                                        "data_type": type(concept_map_data).__name__,
                                        "data_preview": str(concept_map_data)[:100]
                                    }
                                )
                            internal_format = {"concepts": [], "relationships": []}
                    except Exception as conversion_error:
                        # Log conversion error but continue with empty format
                        if self.session_logger:
                            self.session_logger.log_event(
                                event_type="concept_map_conversion_error",
                                metadata={
                                    "round_number": roundn,
                                    "error": str(conversion_error),
                                    "data_type": type(concept_map_data).__name__
                                }
                            )
                        internal_format = {"concepts": [], "relationships": []}
                
                # Get conversation history for this round
                conversation_history = self.get_conversation_history(roundn)
                
                # Generate context
                context = {
                    "round_number": roundn,
                    "conversation_turn": conversation_turn,
                    "conversation_history": conversation_history,
                    "learner_profile": self.session_data.get("learner_profile", {}),
                    "previous_rounds": len(self.session_data.get("rounds", [])),
                    "concept_map_evolution": self.session_data.get("concept_map_evolution", [])
                }
                
                # Ensure internal_format is a proper dictionary
                if not isinstance(internal_format, dict):
                    internal_format = {"concepts": [], "relationships": []}
                
                # Generate scaffolding response
                api_result = self.openai_manager.generate_scaffolding_response(
                    agent_type.replace("_scaffolding", ""), 
                    internal_format, 
                    user_response=user_response,
                    context=context
                )
                
                # Safely extract response
                if isinstance(api_result, dict):
                    response = api_result.get("response", "I apologize, but I'm having trouble generating a response. Please continue with your concept map.")
                else:
                    response = str(api_result) if api_result else "I apologize, but I'm having trouble generating a response. Please continue with your concept map."
                
                # Log the interaction
                if self.session_logger:
                    self.session_logger.log_agent_response(
                        agent_type=agent_type,
                        response_text=response,
                        metadata={
                            "round_number": roundn,
                            "conversation_turn": conversation_turn,
                            "model_used": api_result.get("model_used") if isinstance(api_result, dict) else "unknown",
                            "tokens_used": api_result.get("tokens_used") if isinstance(api_result, dict) else 0,
                            "concept_map_nodes": len(internal_format.get("concepts", [])),
                            "concept_map_edges": len(internal_format.get("relationships", []))
                        }
                    )
                
                return response
                
            except Exception as e:
                # Log the specific error for debugging
                error_msg = f"OpenAI integration failed: {type(e).__name__}: {str(e)}"
                if self.session_logger:
                    self.session_logger.log_event(
                        event_type="openai_integration_error",
                        metadata={
                            "round_number": roundn,
                            "error_type": type(e).__name__,
                            "error_message": str(e),
                            "agent_type": agent_type
                        }
                    )
                st.warning(f"{error_msg}. Using demo response.")
                # Fall through to demo response
        
        # Use demo response with conversation awareness
        if conversation_turn > 0 and user_response:
            # Create contextual demo responses for follow-ups
            demo_followup_responses = {
                "conceptual_scaffolding": f"I see you mentioned '{user_response[:50]}...'. Let's explore how this connects to the broader conceptual framework in your map.",
                "strategic_scaffolding": f"Based on your response about '{user_response[:50]}...', have you considered alternative organizational strategies?",
                "metacognitive_scaffolding": f"Your reflection on '{user_response[:50]}...' is interesting. What does this tell you about your learning process?",
                "procedural_scaffolding": f"You mentioned '{user_response[:50]}...'. How does this procedural approach compare to other methods you could use?"
            }
            response = demo_followup_responses.get(agent_type, demo_responses.get(agent_type, "Thank you for your response. Can you elaborate further?"))
        else:
            response = demo_responses.get(agent_type, demo_responses["conceptual_scaffolding"])
        
        # Log demo response
        if self.session_logger:
            self.session_logger.log_agent_response(
                agent_type=agent_type,
                response_text=response,
                metadata={
                    "round_number": roundn,
                    "conversation_turn": conversation_turn,
                    "response_type": "demo",
                    "concept_map_nodes": len(concept_map_data.get("elements", [])) if isinstance(concept_map_data, dict) and concept_map_data else 0
                }
            )
        
        return response
    
    def log_user_response(self, roundn: int, user_response: str, concept_map_data: Optional[Dict[str, Any]] = None):
        """Log user response to scaffolding."""
        if self.session_logger:
            self.session_logger.log_user_input(
                input_text=user_response,
                metadata={
                    "round_number": roundn,
                    "agent_type": self.session_data["agent_sequence"][roundn] if roundn < len(self.session_data["agent_sequence"]) else None,
                    "concept_map_provided": concept_map_data is not None
                }
            )
    
    def update_concept_map_evolution(self, roundn: int, concept_map_data):
        """Update the concept map evolution tracking."""
        try:
            # Convert to internal format with robust error handling
            internal_format = self.convert_streamlit_to_internal_format(concept_map_data)
            
            # Add to evolution
            evolution_entry = {
                "round": roundn,
                "timestamp": datetime.now().isoformat(),
                "concept_map": internal_format,
                "agent_type": self.session_data["agent_sequence"][roundn] if roundn < len(self.session_data["agent_sequence"]) else None
            }
            
            self.session_data["concept_map_evolution"].append(evolution_entry)
            
            # Update current concept map (cumulative)
            self.session_data["current_concept_map"] = internal_format
            
            # Log concept map update
            if self.session_logger:
                self.session_logger.log_event(
                    event_type="concept_map_updated",
                    metadata={
                        "round_number": roundn,
                        "nodes_count": len(internal_format.get("concepts", [])),
                        "edges_count": len(internal_format.get("relationships", [])),
                        "evolution_length": len(self.session_data["concept_map_evolution"]),
                        "input_data_type": type(concept_map_data).__name__
                    }
                )
                
        except Exception as e:
            # Log the error but don't crash the session
            if self.session_logger:
                self.session_logger.log_event(
                    event_type="concept_map_update_error",
                    metadata={
                        "round_number": roundn,
                        "error": str(e),
                        "input_data_type": type(concept_map_data).__name__,
                        "input_data_preview": str(concept_map_data)[:200] if concept_map_data else "None"
                    }
                )
            
            # Create a minimal evolution entry to maintain session continuity
            evolution_entry = {
                "round": roundn,
                "timestamp": datetime.now().isoformat(),
                "concept_map": {"concepts": [], "relationships": [], "error": str(e)},
                "agent_type": self.session_data["agent_sequence"][roundn] if roundn < len(self.session_data["agent_sequence"]) else None
            }
            self.session_data["concept_map_evolution"].append(evolution_entry)
    
    def finalize_session(self) -> Dict[str, Any]:
        """Finalize the session and export data."""
        try:
            # Add final summary to session data
            self.session_data["end_time"] = datetime.now().isoformat()
            self.session_data["total_duration_seconds"] = (
                datetime.fromisoformat(self.session_data["end_time"]) - 
                datetime.fromisoformat(self.session_data["start_time"])
            ).total_seconds()
            self.session_data["total_rounds"] = len(self.session_data["rounds"])
            self.session_data["final_concept_map"] = self.session_data["current_concept_map"]
            
            # Save session data
            export_info = self.save_session_data()
            
            # Log session end
            if self.session_logger:
                self.session_logger.log_session_end({
                    "total_rounds": len(self.session_data["rounds"]),
                    "final_nodes": len(self.session_data["current_concept_map"].get("concepts", [])),
                    "final_edges": len(self.session_data["current_concept_map"].get("relationships", [])),
                    "export_files": export_info
                })
            
            return export_info
            
        except Exception as e:
            st.error(f"Error finalizing session: {e}")
            return {"error": str(e)}
    
    def save_session_data(self) -> Dict[str, str]:
        """Save complete session data to JSON and CSV files."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            participant_name = self.session_data['learner_profile'].get('name', 'unknown')
            
            # Create experimental_data directory
            os.makedirs("MAS/experimental_data", exist_ok=True)
            
            # JSON export (complete session data)
            json_filename = f"experimental_session_{participant_name}_{timestamp}.json"
            json_filepath = os.path.join("MAS/experimental_data", json_filename)
            
            with open(json_filepath, 'w', encoding='utf-8') as f:
                json.dump(self.session_data, f, indent=2, ensure_ascii=False)
            
            # CSV export (flattened for analysis)
            csv_filename = f"experimental_results_{participant_name}_{timestamp}.csv"
            csv_filepath = os.path.join("MAS/experimental_data", csv_filename)
            
            self._export_csv_data(csv_filepath)
            
            return {
                "json_file": json_filepath,
                "csv_file": csv_filepath,
                "participant_name": participant_name,
                "timestamp": timestamp
            }
            
        except Exception as e:
            st.error(f"Error saving session data: {e}")
            return {"error": str(e)}
    
    def _export_csv_data(self, filepath: str):
        """Export flattened data for statistical analysis."""
        import csv
        
        csv_data = []
        
        for round_data in self.session_data.get("rounds", []):
            round_num = round_data.get("round_number", 0)
            concept_map = round_data.get("concept_map", {})
            nodes = concept_map.get("concepts", [])
            edges = concept_map.get("relationships", [])
            
            # Create base row data
            base_row = {
                "participant_name": self.session_data["learner_profile"].get("name", "unknown"),
                "session_id": self.session_data["session_id"],
                "round_number": round_num,
                "agent_type": round_data.get("agent_type", ""),
                "agent_sequence": ",".join(self.session_data["agent_sequence"]),
                "node_count": len(nodes),
                "edge_count": len(edges),
                "mode": self.session_data.get("mode", "unknown")
            }
            
            # Add one row per round with summary data
            csv_data.append(base_row)
        
        # Write CSV file
        if csv_data:
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = csv_data[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(csv_data)
    
    def get_conversation_history(self, roundn: int) -> List[Dict[str, Any]]:
        """Get conversation history for a specific round."""
        # Initialize conversation history if not exists
        if "conversation_history" not in self.session_data:
            self.session_data["conversation_history"] = {}
        
        round_key = f"round_{roundn}"
        return self.session_data["conversation_history"].get(round_key, [])
    
    def add_to_conversation_history(self, roundn: int, speaker: str, message: str, metadata: Optional[Dict] = None):
        """Add a message to the conversation history for a specific round."""
        if "conversation_history" not in self.session_data:
            self.session_data["conversation_history"] = {}
        
        round_key = f"round_{roundn}"
        if round_key not in self.session_data["conversation_history"]:
            self.session_data["conversation_history"][round_key] = []
        
        conversation_entry = {
            "speaker": speaker,  # "agent" or "user"
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        self.session_data["conversation_history"][round_key].append(conversation_entry)
    
    def get_conversation_turn_count(self, roundn: int) -> int:
        """Get the number of conversation turns for a specific round."""
        history = self.get_conversation_history(roundn)
        return len(history)
    
    def can_continue_conversation(self, roundn: int) -> bool:
        """Check if more conversation turns are allowed for this round."""
        max_turns = 10  # 5 agent responses + 5 user responses
        return self.get_conversation_turn_count(roundn) < max_turns
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get session summary for display."""
        return {
            "participant_name": self.session_data["learner_profile"].get("name", "Unknown"),
            "total_rounds": len(self.session_data.get("rounds", [])),
            "agent_sequence": self.session_data.get("agent_sequence", []),
            "final_concept_map": self.session_data.get("current_concept_map", {}),
            "mode": self.session_data.get("mode", "unknown"),
            "start_time": self.session_data.get("start_time"),
            "end_time": self.session_data.get("end_time")
        }
