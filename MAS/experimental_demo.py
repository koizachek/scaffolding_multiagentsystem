#!/usr/bin/env python3
"""
Interactive Experimental Demo for Multi-Agent Scaffolding System

This script provides a fully interactive experimental platform where users:
1. Create their learner profile through guided questions
2. Experience 4 randomized, non-repeating scaffolding rounds
3. Build concept maps cumulatively across rounds
4. Have all interactions logged for research analysis
"""

import os
import sys
import json
import random
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from MAS.mas_system import MultiAgentScaffoldingSystem

class InteractiveExperimentalSession:
    """Manages a complete interactive experimental session."""
    
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
    
    def ask_user_question(self, question: str, required: bool = True) -> str:
        """Ask user a question and get their response."""
        while True:
            response = input(f"\n{question}\n> ").strip()
            if response or not required:
                return response
            print("This field is required. Please provide an answer.")
    
    def select_mode(self) -> str:
        """Ask user to select experimental mode or demo."""
        print("\n" + "="*60)
        print("🧪 Multi-Agent Scaffolding System")
        print("="*60)
        
        mode_response = input("\nDo you want to begin a live experimental session or run a demo? (experimental/demo) [experimental]: ").strip().lower()
        
        if mode_response in ['demo', 'd']:
            return 'demo'
        else:
            return 'experimental'
    
    def create_learner_profile(self) -> Dict[str, Any]:
        """Create learner profile through interactive questions."""
        print("\n" + "="*60)
        print("📋 LEARNER PROFILE CREATION")
        print("="*60)
        print("Please answer the following questions to create your learner profile.")
        
        profile = {
            "name": self.ask_user_question("What is your name?"),
            "background": self.ask_user_question("What is your educational/professional background?"),
            "prior_knowledge": self.ask_user_question("What prior knowledge do you have about the topic you'll be mapping?"),
            "confidence": self.ask_user_question("How confident do you feel about concept mapping? (1-10 scale or description)"),
            "interests": self.ask_user_question("What are your main interests or areas of focus?"),
            "goals": self.ask_user_question("What do you hope to achieve in this session?"),
            "zpd_level": "medium",  # Always initialize at medium level
            "created_at": datetime.now().isoformat()
        }
        
        print(f"\n✅ Profile created for {profile['name']}")
        print(f"📊 ZPD Level initialized: {profile['zpd_level']}")
        
        return profile
    
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
        
        print(f"\n🎲 Randomized agent sequence: {' → '.join([a.replace('_', ' ').title() for a in agents])}")
        
        return agents
    
    def get_concept_map_input(self, round_num: int, is_first_round: bool = False) -> Dict[str, Any]:
        """Get concept map input from user."""
        print(f"\n" + "="*60)
        print(f"📝 CONCEPT MAP INPUT - Round {round_num + 1}")
        print("="*60)
        
        if is_first_round:
            print("Please create your initial concept map using Mermaid.js syntax.")
            print("Example format:")
            print("  graph TD")
            print("    A[Learning] --> B[Understanding]")
            print("    B --> C[Application]")
            print("\nEnter your concept map (type 'DONE' on a new line when finished):")
        else:
            print("Please extend your concept map from the previous round.")
            print("Add new concepts and relationships to build upon your existing map.")
            print("\nCurrent concept map has:")
            print(f"  - {len(self.session_data['current_concept_map']['concepts'])} concepts")
            print(f"  - {len(self.session_data['current_concept_map']['relationships'])} relationships")
            print("\nEnter your extended concept map (type 'DONE' on a new line when finished):")
        
        mermaid_lines = []
        while True:
            line = input()
            if line.strip() == "DONE":
                break
            mermaid_lines.append(line)
        
        mermaid_text = "\n".join(mermaid_lines)
        
        # Parse Mermaid to internal format
        try:
            concept_map = self.system.mermaid_parser.parse_mermaid_to_concept_map(mermaid_text)
            concept_map["mermaid_source"] = mermaid_text
            concept_map["round"] = round_num
            concept_map["timestamp"] = datetime.now().isoformat()
            
            print(f"✅ Parsed concept map: {len(concept_map.get('concepts', []))} concepts, {len(concept_map.get('relationships', []))} relationships")
            
            return concept_map
        except Exception as e:
            print(f"⚠️  Error parsing concept map: {e}")
            # Return basic structure if parsing fails
            return {
                "concepts": [],
                "relationships": [],
                "mermaid_source": mermaid_text,
                "round": round_num,
                "timestamp": datetime.now().isoformat(),
                "parse_error": str(e)
            }
    
    def conduct_scaffolding_round(self, round_num: int, agent_type: str, concept_map: Dict[str, Any]) -> Dict[str, Any]:
        """Conduct a single scaffolding round with the specified agent."""
        print(f"\n" + "="*60)
        print(f"🤖 SCAFFOLDING ROUND {round_num + 1}: {agent_type.replace('_', ' ').title()}")
        print("="*60)
        
        round_data = {
            "round_number": round_num,
            "agent_type": agent_type,
            "start_time": datetime.now().isoformat(),
            "concept_map": concept_map,
            "interactions": [],
            "agent_responses": [],
            "user_responses": []
        }
        
        # Generate initial scaffolding prompt using OpenAI
        if self.session_data["mode"] == "experimental" and self.system.openai_manager:
            try:
                print("🔄 Generating scaffolding response...")
                
                context = {
                    "round_number": round_num,
                    "learner_profile": self.session_data["learner_profile"],
                    "previous_rounds": len(self.session_data["rounds"]),
                    "concept_map_evolution": self.session_data["concept_map_evolution"]
                }
                
                api_result = self.system.openai_manager.generate_scaffolding_response(
                    agent_type.replace("_scaffolding", ""), 
                    concept_map, 
                    context=context
                )
                
                initial_response = api_result["response"]
                round_data["agent_responses"].append({
                    "text": initial_response,
                    "timestamp": datetime.now().isoformat(),
                    "type": "initial_prompt",
                    "model_used": api_result.get("model_used"),
                    "tokens_used": api_result.get("tokens_used")
                })
                
                print(f"\n🤖 {agent_type.replace('_', ' ').title()} Agent:")
                print("-" * 40)
                print(initial_response)
                print("-" * 40)
                
                # Get user response
                user_response = self.ask_user_question(
                    f"\n💬 Please respond to the {agent_type.replace('_', ' ')} scaffolding above:",
                    required=True
                )
                
                round_data["user_responses"].append({
                    "text": user_response,
                    "timestamp": datetime.now().isoformat(),
                    "type": "response_to_initial"
                })
                
                # Generate follow-up if needed
                if len(user_response) > 10:  # Only if substantial response
                    print("\n🔄 Generating follow-up...")
                    
                    followup_result = self.system.openai_manager.generate_scaffolding_response(
                        agent_type.replace("_scaffolding", ""), 
                        concept_map, 
                        user_response=user_response,
                        context=context
                    )
                    
                    followup_response = followup_result["response"]
                    round_data["agent_responses"].append({
                        "text": followup_response,
                        "timestamp": datetime.now().isoformat(),
                        "type": "followup",
                        "model_used": followup_result.get("model_used"),
                        "tokens_used": followup_result.get("tokens_used")
                    })
                    
                    print(f"\n🤖 {agent_type.replace('_', ' ').title()} Agent Follow-up:")
                    print("-" * 40)
                    print(followup_response)
                    print("-" * 40)
                
            except Exception as e:
                print(f"⚠️  Error with OpenAI integration: {e}")
                # Fallback to demo response
                demo_responses = {
                    "conceptual": "Let's explore the conceptual relationships in your map. How do these concepts connect to form a coherent understanding?",
                    "strategic": "Consider the strategic organization of your concept map. What's the most effective way to structure these ideas?",
                    "metacognitive": "Reflect on your thinking process. How confident are you about these relationships? What might you be missing?",
                    "procedural": "Let's focus on the procedural aspects. What steps or processes are represented in your concept map?"
                }
                
                agent_key = agent_type.replace("_scaffolding", "")
                demo_response = demo_responses.get(agent_key, "How can we improve your concept map?")
                
                round_data["agent_responses"].append({
                    "text": demo_response,
                    "timestamp": datetime.now().isoformat(),
                    "type": "demo_fallback"
                })
                
                print(f"\n🤖 {agent_type.replace('_', ' ').title()} Agent (Demo Mode):")
                print("-" * 40)
                print(demo_response)
                print("-" * 40)
                
                user_response = self.ask_user_question(
                    f"\n💬 Please respond to the {agent_type.replace('_', ' ')} scaffolding above:",
                    required=True
                )
                
                round_data["user_responses"].append({
                    "text": user_response,
                    "timestamp": datetime.now().isoformat(),
                    "type": "response_to_demo"
                })
        
        else:
            # Demo mode responses
            demo_responses = {
                "conceptual": "Let's explore the conceptual relationships in your map. How do these concepts connect to form a coherent understanding?",
                "strategic": "Consider the strategic organization of your concept map. What's the most effective way to structure these ideas?",
                "metacognitive": "Reflect on your thinking process. How confident are you about these relationships? What might you be missing?",
                "procedural": "Let's focus on the procedural aspects. What steps or processes are represented in your concept map?"
            }
            
            agent_key = agent_type.replace("_scaffolding", "")
            demo_response = demo_responses.get(agent_key, "How can we improve your concept map?")
            
            round_data["agent_responses"].append({
                "text": demo_response,
                "timestamp": datetime.now().isoformat(),
                "type": "demo_response"
            })
            
            print(f"\n🤖 {agent_type.replace('_', ' ').title()} Agent (Demo Mode):")
            print("-" * 40)
            print(demo_response)
            print("-" * 40)
            
            user_response = self.ask_user_question(
                f"\n💬 Please respond to the {agent_type.replace('_', ' ')} scaffolding above:",
                required=True
            )
            
            round_data["user_responses"].append({
                "text": user_response,
                "timestamp": datetime.now().isoformat(),
                "type": "response_to_demo"
            })
        
        round_data["end_time"] = datetime.now().isoformat()
        round_data["duration_seconds"] = (
            datetime.fromisoformat(round_data["end_time"]) - 
            datetime.fromisoformat(round_data["start_time"])
        ).total_seconds()
        
        print(f"\n✅ Round {round_num + 1} completed with {agent_type.replace('_', ' ').title()} agent")
        
        return round_data
    
    def update_concept_map(self, new_concept_map: Dict[str, Any]) -> None:
        """Update the cumulative concept map."""
        # Store evolution
        self.session_data["concept_map_evolution"].append({
            "round": len(self.session_data["concept_map_evolution"]),
            "timestamp": datetime.now().isoformat(),
            "concept_map": new_concept_map.copy()
        })
        
        # Update current map (cumulative)
        if new_concept_map.get("concepts"):
            # Merge concepts (avoid duplicates by ID)
            existing_ids = {c.get("id") for c in self.session_data["current_concept_map"]["concepts"]}
            for concept in new_concept_map["concepts"]:
                if concept.get("id") not in existing_ids:
                    self.session_data["current_concept_map"]["concepts"].append(concept)
        
        if new_concept_map.get("relationships"):
            # Merge relationships (avoid duplicates)
            existing_rels = {(r.get("source"), r.get("target")) for r in self.session_data["current_concept_map"]["relationships"]}
            for rel in new_concept_map["relationships"]:
                rel_key = (rel.get("source"), rel.get("target"))
                if rel_key not in existing_rels:
                    self.session_data["current_concept_map"]["relationships"].append(rel)
    
    def save_session_data(self) -> str:
        """Save complete session data to JSON file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"experimental_session_{self.session_data['learner_profile'].get('name', 'unknown')}_{timestamp}.json"
        
        # Add final summary
        self.session_data["end_time"] = datetime.now().isoformat()
        self.session_data["total_duration_seconds"] = (
            datetime.fromisoformat(self.session_data["end_time"]) - 
            datetime.fromisoformat(self.session_data["start_time"])
        ).total_seconds()
        self.session_data["total_rounds"] = len(self.session_data["rounds"])
        self.session_data["final_concept_map"] = self.session_data["current_concept_map"]
        
        # Save to file
        os.makedirs("experimental_data", exist_ok=True)
        filepath = os.path.join("experimental_data", filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.session_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Session data saved to: {filepath}")
        return filepath
    
    def run_experimental_session(self) -> None:
        """Run the complete experimental session."""
        try:
            # 1. Mode Selection
            mode = self.select_mode()
            self.session_data["mode"] = mode
            
            print(f"\n🚀 Starting {mode} session...")
            
            # 2. Initialize System
            self.system = MultiAgentScaffoldingSystem(
                config_path="MAS/config.json",
                mode=mode,
                participant_id=f"participant_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )
            
            # 3. Create Learner Profile
            self.session_data["learner_profile"] = self.create_learner_profile()
            
            # 4. Initialize Agent Sequence
            self.session_data["agent_sequence"] = self.initialize_agent_sequence()
            
            # 5. Conduct 4 Rounds
            for round_num in range(4):
                agent_type = self.session_data["agent_sequence"][round_num]
                
                # Mark agent as used
                self.session_data["used_agents"].append(agent_type)
                
                # Get concept map input
                is_first_round = round_num == 0
                concept_map = self.get_concept_map_input(round_num, is_first_round)
                
                # Update cumulative concept map
                self.update_concept_map(concept_map)
                
                # Conduct scaffolding round
                round_data = self.conduct_scaffolding_round(round_num, agent_type, concept_map)
                
                # Store round data
                self.session_data["rounds"].append(round_data)
                
                # Show progress
                print(f"\n📊 Progress: {round_num + 1}/4 rounds completed")
                print(f"🎯 Agents used: {', '.join([a.replace('_', ' ').title() for a in self.session_data['used_agents']])}")
                
                if round_num < 3:
                    input("\nPress Enter to continue to the next round...")
            
            # 6. Session Summary
            print(f"\n" + "="*60)
            print("🎉 EXPERIMENTAL SESSION COMPLETED")
            print("="*60)
            print(f"Participant: {self.session_data['learner_profile']['name']}")
            print(f"Total rounds: {len(self.session_data['rounds'])}")
            print(f"Agents experienced: {', '.join([a.replace('_', ' ').title() for a in self.session_data['used_agents']])}")
            print(f"Final concept map: {len(self.session_data['current_concept_map']['concepts'])} concepts, {len(self.session_data['current_concept_map']['relationships'])} relationships")
            
            # 7. Save Data
            filepath = self.save_session_data()
            
            print(f"\n✅ Complete experimental data saved for research analysis")
            print(f"📁 File: {filepath}")
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Session interrupted by user")
            if self.session_data.get("rounds"):
                print("Saving partial session data...")
                self.save_session_data()
        except Exception as e:
            print(f"\n❌ Error during experimental session: {e}")
            import traceback
            traceback.print_exc()
            if self.session_data.get("rounds"):
                print("Saving partial session data...")
                self.save_session_data()

def main():
    """Main entry point for the experimental session."""
    print("🧪 Multi-Agent Scaffolding System - Interactive Experimental Platform")
    print("="*80)
    print("This platform provides a complete experimental research environment where:")
    print("• Users create personalized learner profiles")
    print("• Experience 4 randomized, non-repeating scaffolding agents")
    print("• Build concept maps cumulatively across rounds")
    print("• All interactions are logged for research analysis")
    print("="*80)
    
    session = InteractiveExperimentalSession()
    session.run_experimental_session()

if __name__ == "__main__":
    main()
