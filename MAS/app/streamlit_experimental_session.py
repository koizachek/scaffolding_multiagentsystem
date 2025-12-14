"""
Streamlit-adapted Experimental Session for Multi-Agent Scaffolding System

This module adapts the InteractiveExperimentalSession for use with Streamlit,
providing the same research-grade functionality through a web interface.
"""

import os
import sys
import json
import random
import logging
import hashlib
import streamlit as st
from datetime import datetime
from typing import Dict, List, Any, Optional

from streamlit.runtime.state import session_state

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    from MAS.mas_system import MultiAgentScaffoldingSystem
    from MAS.utils.ai_api import AIManager
    from MAS.utils.logging_utils import SessionLogger
    from MAS.utils.mermaid_parser import MermaidParser
    from MAS.database.mdbservice import *
except ImportError:
    # Fallback for when running from app directory
    import sys
    import os
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, parent_dir)
    
    from mas_system import MultiAgentScaffoldingSystem
    from utils.ai_api import AIManager
    from utils.logging_utils import SessionLogger
    from utils.mermaid_parser import MermaidParser
    from database.mdbservice import *

logger = logging.getLogger(__name__)

# Einzelne Experimentalbedingung mit fixer Sequenz (keine Randomisierung/Kontrollgruppe)
EXPERIMENTAL_CONDITIONS = ['EG_SEQ']

# Feste Agenten-Sequenz fuer alle Teilnehmenden
AGENT_SEQUENCES = {
    'EG_SEQ': ["metacognitive_scaffolding", "strategic_scaffolding", "procedural_scaffolding", "conceptual_scaffolding"]
}


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
        self.db_service = None
        self.ai_manager = None
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

            # Initialize AI manager for experimental mode
            if mode == "experimental":
                try:
                    ai_manager_config = self.system.config.get("ai_manager", {})
                    self.ai_manager = AIManager(ai_manager_config)
                    
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
                    self.demo_mode_fallback()
                    self.ai_manager = None
                    self.session_logger = None
                
                try: 
                    self.db_service = MDBService()
                    logger.info("    🗃️ Connection to the database established successfully")
                except DatabaseConnectionException as e:
                    logger.error("    ❌🗃️ Could not establish the connection to the database!")
                    st.error(f"Failed to connect to the database: {e}")
                    self.demo_mode_fallback()
                    self.db_service = None

            return True
            
        except Exception as e:
            st.error(f"Failed to initialize system: {e}")
            return False
   

    def demo_mode_fallback(self):
        st.info("Falling back to demo mode")
        self.session_data["mode"] = "demo"

            

    def render_pre_knowledge_questionnaire(self):
        """Render pre-knowledge questionnaire about task materials."""
        import streamlit as st
        
        st.header("📝 Vorkenntnis-Abfrage")
        st.markdown("---")
        
        st.info("""
        Bitte beantworte die folgenden Fragen. 
        Diese Informationen helfen uns, dein Vorwissen zu verstehen.
        
        **Notiz:** Deine Antworten werden nicht bewertet, sondern zu Forschungszwecken erhoben.
        """)
        
        # Define questions with correct answers (for logging only)
        questions = [
            {
                "id": "aicctp_role",
                "question": "AICCTP: Was beschreibt das AI Carbon Credit Transfer Protocol am besten?",
                "options": {
                    "A": "Ein technischer Standard zur CO2-Messung",
                    "B": "Ein Mechanismus dominanter Haendler, der Verifizierung/Transfer zu Ungunsten von KMU manipuliert",
                    "C": "Ein staatliches Lizenzsystem mit festen Regeln fuer alle"
                },
                "correct": "B"
            },
            {
                "id": "attention_check_pre",
                "question": "Aufmerksamkeitscheck: Welche Antwort steht in der Mitte?",
                "options": {
                    "A": "Diese Antwort steht zuerst",
                    "B": "In der Mitte findest du diese Antwort",
                    "C": "Die letzte moegliche Antwort"
                },
                "correct": "B"
            },
            {
                "id": "verification_complexity",
                "question": "Verifizierungskomplexitaet: Was bedeutet sie im Kontext von AICCTP?",
                "options": {
                    "A": "Einfache Selbstauskunft ohne Prufer",
                    "B": "Technische Standards, die grosse Compliance-Teams beguenstigen",
                    "C": "Sofortige automatische Freigabe von Zertifikaten"
                },
                "correct": "B"
            },
            {
                "id": "transfer_delays",
                "question": "Transferverzoegerungen: Wie wirken sie sich aus?",
                "options": {
                    "A": "Beschleunigen Transaktionen kleiner Haendler",
                    "B": "Verlangsamen Abwicklung und lassen KMU Preisfenster verpassen",
                    "C": "Haben keinen Einfluss auf Handelsabwicklung"
                },
                "correct": "B"
            },
            {
                "id": "price_signaling",
                "question": "Preissignalisierung im AICCTP-Kontext bedeutet…",
                "options": {
                    "A": "Koordinierte Infos, die kuenstliche Preisvolatilitaet erzeugen",
                    "B": "Staatlich fixierte CO2-Preise",
                    "C": "Zufaellige Marktschwankungen ohne Einflussnahme"
                },
                "correct": "A"
            },
            {
                "id": "access_control",
                "question": "Zugangssteuerung: Was umfasst sie?",
                "options": {
                    "A": "Offene Plattformen fuer alle",
                    "B": "Kontrolle ueber Pruefer, Auditoren und Plattformbetreiber durch dominante Haendler",
                    "C": "Rabattierte Handelsgebuehren fuer KMU"
                },
                "correct": "B"
            },
            {
                "id": "participation_strategy",
                "question": "Welche Teilnahmestrategie buendelt Ressourcen mehrerer KMU?",
                "options": {
                    "A": "Direkthandel",
                    "B": "Maklerpartnerschaft",
                    "C": "Handelskonsortium"
                },
                "correct": "C"
            },
            {
                "id": "regulatory_standards",
                "question": "Regulatorische Standards definieren…",
                "options": {
                    "A": "Wie Emissionen gemessen und Zertifikate verifiziert werden muessen",
                    "B": "Marketing- und Vertriebskanaele eines KMU",
                    "C": "Interne HR-Richtlinien"
                },
                "correct": "A"
            },
            {
                "id": "market_conditions",
                "question": "Marktbedingungen umfassen vor allem…",
                "options": {
                    "A": "Preisniveau, Liquiditaet, Handelsvolumen, Angebot/Nachfrage",
                    "B": "Teamgroesse des KMU",
                    "C": "Urlaubsplanung der Mitarbeitenden"
                },
                "correct": "A"
            }
        ]
        
        with st.form("pre_knowledge_questionnaire"):
            responses = {}
            
            # Display all questions
            for i, q in enumerate(questions, 1):
                st.markdown(f"**Question {i} of {len(questions)}**")
                
                # Use radio buttons for each question
                answer = st.radio(
                    q["question"],
                    options=["A", "B", "C"],
                    format_func=lambda x, opts=q["options"]: f"{x}) {opts[x]}",
                    key=f"q_{q['id']}",
                    index=None  # No default selection
                )
                
                if answer:
                    responses[q["id"]] = {
                        "question": q["question"],
                        "selected_answer": answer,
                        "answer_text": q["options"][answer],
                        "correct_answer": q["correct"],
                        "is_correct": answer == q["correct"]
                    }
                
                st.markdown("---")
            
            submitted = st.form_submit_button("Fragebogen abschicken", type="primary")
            
            if submitted:
                # Check if all questions are answered
                if len(responses) < len(questions):
                    st.error(f"Bitte beantworte alle {len(questions)} Fragen, bevor du absendest.")
                    return
                
                # Calculate score (for logging only, not shown to user)
                score = sum(1 for r in responses.values() if r["is_correct"])
                 
                
                # Attention check (all questions are answered at this point)
                attention_check_response = responses.get("attention_check_pre")
                attention_check_failed = not attention_check_response.get("is_correct", False)

                if attention_check_failed:
                    # Log the attention check failure
                    if self.session_logger:
                        self.session_logger.log_event(
                            event_type="attention_check_failed",
                            metadata={
                                "question_id": "attention_check_pre",
                                "selected_answer": attention_check_response.get("selected_answer", "N/A"),
                                "correct_answer": attention_check_response.get("correct_answer", "B"),
                                "participant_id": self.session_data.get("learner_profile", {}).get("unique_id", "N/A"),
                                "timestamp": datetime.now().isoformat()
                            }
                        )

                    # Critical: set BOTH flags so the app renders the failure page on next run
                    st.session_state.attention_check_failed = True
                    st.session_state.pre_questionnaire_completed = True
                    # Ensure we do NOT show the tutorial in failure case
                    st.session_state.show_tutorial = False

                    # Persist questionnaire data with explicit failure marker
                    self.session_data["pre_knowledge_questionnaire"] = {
                        "responses": responses,
                        "score": score,
                        "total_questions": len(questions),
                        "percentage": round((score / len(questions)) * 100, 2),
                        "completed_at": datetime.now().isoformat(),
                        "attention_check_passed": False
                    }

                    if self.session_logger:
                        self.session_logger.log_event(
                            event_type="pre_knowledge_questionnaire_completed",
                            metadata={
                                "score": score,
                                "total_questions": len(questions),
                                "percentage": round((score / len(questions)) * 100, 2),
                                "detailed_responses": responses,
                                "attention_check_passed": False
                            }
                        )

                    # Immediately re-render so the app-level routing shows the fail page
                    st.rerun()
                    return
                
                # Store questionnaire data in session
                questionnaire_data = {
                    "responses": responses,
                    "score": score,
                    "total_questions": len(questions),
                    "percentage": round((score / len(questions)) * 100, 2),
                    "completed_at": datetime.now().isoformat(),
                    "attention_check_passed": True
                }
                
                # Add to session data
                self.session_data["pre_knowledge_questionnaire"] = questionnaire_data
                
                # Log the questionnaire completion
                if self.session_logger:
                    self.session_logger.log_event(
                        event_type="pre_knowledge_questionnaire_completed",
                        metadata={
                            "score": score,
                            "total_questions": len(questions),
                            "percentage": questionnaire_data["percentage"],
                            "detailed_responses": responses,
                            "attention_check_passed": True
                        }
                    )
                
                # Update session state to mark questionnaire as completed
                st.session_state.pre_questionnaire_completed = True
                st.session_state.show_tutorial = True
                
                st.success("✅ Fragebogen abgeschlossen! Danke fur deine Antworten.")
                st.info("📚 Weiter zum Tutorial zum Concept Mapping...")
                
                # Automatically proceed to tutorial
                st.rerun()
    
    def render_clt_questionnaire(self):
        """Render Cognitive Load Theory questionnaire."""
        import streamlit as st
        
        st.header("📊 Erhebung der kognitiven Belastung")
        st.markdown("---")
        
        st.info("""
        Bitte bewerte die folgenden Aussagen zur soeben abgeschlossenen Lernaufgabe.
        
        Waehle fur jede Aussage eine Bewertung von 1 (trifft gar nicht zu) bis 9 (trifft voll zu).
        """)
        
        # Define CLT items (15 items total) – deutsche Originalformulierungen (Krieglstein et al., 2023)
        clt_items = [
            # Intrinsic Cognitive Load (ICL)
            {
                "construct": "ICL",
                "code": "ICL1",
                "statement": "Die Lerninhalte waren schwer zu verstehen."
            },
            {
                "construct": "ICL",
                "code": "ICL2",
                "statement": "Die Erklarungen des Lerninhalts waren schwer nachvollziehbar."
            },
            {
                "construct": "ICL",
                "code": "ICL3",
                "statement": "Die Lerninhalte waren komplex."
            },
            {
                "construct": "ICL",
                "code": "ICL4",
                "statement": "Die Lerninhalte enthielten viele komplexe Informationen."
            },
            {
                "construct": "ICL",
                "code": "ICL5",
                "statement": "Ohne Vorwissen waren die Informationen nicht verstandlich."
            },
            
            # Extraneous Cognitive Load (ECL)
            {
                "construct": "ECL",
                "code": "ECL1",
                "statement": "Es war schwierig, einen Ueberblick ueber den Aufbau des Lernmaterials zu erlangen."
            },
            {
                "construct": "ECL",
                "code": "ECL2",
                "statement": "Die Gestaltung des Lernmaterials machte es schwer, die Zusammenhaenge zwischen den einzelnen Informationen herzustellen."
            },
            {
                "construct": "ECL",
                "code": "ECL3",
                "statement": "Das Lernmaterial war unguenstig gestaltet."
            },
            {
                "construct": "ECL",
                "code": "ECL4",
                "statement": "Die Gestaltung des Lernmaterials machte es schwierig, wichtige Informationen zuegig zu finden."
            },
            {
                "construct": "ECL",
                "code": "ECL5",
                "statement": "Aufgrund der Gestaltung des Lernmaterials hatte ich das Gefuehl, mich nicht auf die Lerninhalte konzentrieren zu koennen."
            },
            
            # Germane Cognitive Load (GCL)
            {
                "construct": "GCL",
                "code": "GCL1",
                "statement": "Ich habe aktiv ueber die Lerninhalte nachgedacht."
            },
            {
                "construct": "GCL",
                "code": "GCL3",
                "statement": "Ich habe mich bemueht, die Lerninhalte zu verstehen."
            },
            {
                "construct": "GCL",
                "code": "GCL5",
                "statement": "Ich habe ein umfassendes Verstaendnis der Lerninhalte erlangt."
            },
            {
                "construct": "GCL",
                "code": "GCL6",
                "statement": "Ich konnte mein bestehendes Wissen mit den Lerninhalten erweitern."
            },
            {
                "construct": "GCL",
                "code": "GCL7",
                "statement": "Das Wissen, das ich durch das Lernmaterial erworben habe, kann ich schnell und sicher anwenden."
            }
        ]
        # Add random attention check item
        attention_check_item = {
            "construct": "ATTN",
            "code": "ATTN1",
            "statement": "Um zu zeigen, dass du noch Aufmerksamkeit spendest, waehle bitte die Zahl 4."
        }
        insert_position = random.randint(0, len(clt_items))
        clt_items.insert(insert_position, attention_check_item)
        
        # Randomize item order to reduce bias (but keep consistent within session)
        if "clt_item_order" not in st.session_state:
            st.session_state.clt_item_order = list(range(len(clt_items)))
            random.shuffle(st.session_state.clt_item_order)
        
        # Create form
        with st.form("clt_questionnaire"):
            responses = {}
            
            # Display items in randomized order
            for i, item_idx in enumerate(st.session_state.clt_item_order, 1):
                item = clt_items[item_idx]
                
                st.markdown(f"**Aussage {i} von {len(clt_items)}**")
                st.markdown(f"*{item['statement']}*")
                
                # Use radio buttons for 7-point Likert scale
                response = st.radio(
                    "Select your rating:",
                    options=list(range(1, 10)), 
                    format_func=str,
                    key=f"clt_{item['code']}",
                    index=None,  
                    horizontal=True  
                )
                st. caption ("1 = Not at all applicable     9 = Fully applicable")

                if response:
                    responses[item['code']] = {
                        "construct": item['construct'],
                        "code": item['code'],
                        "statement": item['statement'],
                        "response_value": response,
                        "item_order": i
                    }
                
                st.markdown("---")
            
            submitted = st.form_submit_button("Submit Questionnaire", type="primary")
            
            if submitted:
                # Check if all items are answered
                if len(responses) < len(clt_items):
                    st.error(f"Bitte beantworte alle {len(clt_items)} Aussagen, bevor du absendest.")
                    return
                
                # Calculate construct averages
                construct_scores = {}
                for construct in ["ICL", "ECL", "GCL"]:
                    construct_items = [r for r in responses.values() if r['construct'] == construct]
                    if construct_items:
                        avg_score = sum(item['response_value'] for item in construct_items) / len(construct_items)
                        construct_scores[construct] = round(avg_score, 2)
                
                # Store CLT data in session
                clt_data = {
                    "responses": responses,
                    "construct_scores": construct_scores,
                    "participant_id": self.session_data.get("learner_profile", {}).get("name", "unknown"),
                    "unique_id": self.session_data.get("learner_profile", {}).get("unique_id", "N/A"),
                    "timestamp": datetime.now().isoformat(),
                    "randomized_order": st.session_state.clt_item_order
                }
                
                # Check attention check
                attn_response = responses.get("ATTN1", {}).get("response_value")
                passed_attention_check = attn_response == 4
                clt_data["passed_attention_check"] = passed_attention_check


                
                # Add to session data
                self.session_data["clt_questionnaire"] = clt_data
                
                # Log the CLT completion with detailed item responses
                if self.session_logger:
                    # Log overall CLT completion
                    self.session_logger.log_event(
                        event_type="clt_questionnaire_completed",
                        metadata={
                            "construct_scores": construct_scores,
                            "total_items": len(responses),
                            "participant_id": clt_data["participant_id"],
                            "unique_id": clt_data["unique_id"],
                            "passed_attention_check": clt_data["passed_attention_check"]
                        }
                    )
                    
                    # Log individual item responses for detailed analysis
                    for code, response_data in responses.items():
                        self.session_logger.log_event(
                            event_type="clt_item_response",
                            metadata={
                                "participant_id": clt_data["participant_id"],
                                "unique_id": clt_data["unique_id"],
                                "timestamp": clt_data["timestamp"],
                                "construct_name": response_data["construct"],
                                "item_code": code,
                                "response_value": response_data["response_value"],
                                "statement": response_data["statement"],
                                "item_order": response_data["item_order"]
                            }
                        )
                
                # Update session state to mark CLT as completed
                st.session_state.clt_completed = True
                
                st.success("✅ Fragebogen zur kognitiven Belastung abgeschlossen!")
                st.info("📊 Weiter zum Post-Knowledge-Fragebogen...")
                
                # Automatically proceed to post knowledge
                st.rerun()
                

    def render_post_knowledge_questionnaire(self):
        """Render Post Knowledge questionnaire."""
        import streamlit as st

        st.header("📋 Deine Lernergebnisse")
        st.markdown("---")

        st.info(
            """
            Bitte beantworte die folgenden Fragen. Das hilft uns, deine Wissenszuwachse nach dem Experiment zu verstehen.
            """
        )

        # Define questions with correct answers (for logging only)
        questions = [
            {
                "id": "aicctp_role",
                "question": "AICCTP: Was beschreibt das AI Carbon Credit Transfer Protocol am besten?",
                "options": {
                    "A": "Ein technischer Standard zur CO2-Messung",
                    "B": "Ein Mechanismus dominanter Haendler, der Verifizierung/Transfer zu Ungunsten von KMU manipuliert",
                    "C": "Ein staatliches Lizenzsystem mit festen Regeln fuer alle"
                },
                "correct": "B"
            },
            {
                "id": "verification_complexity",
                "question": "Verifizierungskomplexitaet: Was bedeutet sie im Kontext von AICCTP?",
                "options": {
                    "A": "Einfache Selbstauskunft ohne Prufer",
                    "B": "Technische Standards, die grosse Compliance-Teams beguenstigen",
                    "C": "Sofortige automatische Freigabe von Zertifikaten"
                },
                "correct": "B"
            },
            {
                "id": "transfer_delays",
                "question": "Transferverzoegerungen: Wie wirken sie sich aus?",
                "options": {
                    "A": "Beschleunigen Transaktionen kleiner Haendler",
                    "B": "Verlangsamen Abwicklung und lassen KMU Preisfenster verpassen",
                    "C": "Haben keinen Einfluss auf Handelsabwicklung"
                },
                "correct": "B"
            },
            {
                "id": "price_signaling",
                "question": "Preissignalisierung im AICCTP-Kontext bedeutet…",
                "options": {
                    "A": "Koordinierte Infos, die kuenstliche Preisvolatilitaet erzeugen",
                    "B": "Staatlich fixierte CO2-Preise",
                    "C": "Zufaellige Marktschwankungen ohne Einflussnahme"
                },
                "correct": "A"
            },
            {
                "id": "attention_check_post",
                "question": "Aufmerksamkeitscheck: Welche Antwort steht in der Mitte?",
                "options": {
                    "A": "Diese Antwort steht zuerst",
                    "B": "In der Mitte findest du diese Antwort",
                    "C": "Die letzte moegliche Antwort"
                },
                "correct": "B"
            },
            {
                "id": "access_control",
                "question": "Zugangssteuerung: Was umfasst sie?",
                "options": {
                    "A": "Offene Plattformen fuer alle",
                    "B": "Kontrolle ueber Pruefer, Auditoren und Plattformbetreiber durch dominante Haendler",
                    "C": "Rabattierte Handelsgebuehren fuer KMU"
                },
                "correct": "B"
            },
            {
                "id": "participation_strategy",
                "question": "Welche Teilnahmestrategie buendelt Ressourcen mehrerer KMU?",
                "options": {
                    "A": "Direkthandel",
                    "B": "Maklerpartnerschaft",
                    "C": "Handelskonsortium"
                },
                "correct": "C"
            },
            {
                "id": "regulatory_standards",
                "question": "Regulatorische Standards definieren…",
                "options": {
                    "A": "Wie Emissionen gemessen und Zertifikate verifiziert werden muessen",
                    "B": "Marketing- und Vertriebskanaele eines KMU",
                    "C": "Interne HR-Richtlinien"
                },
                "correct": "A"
            },
            {
                "id": "market_conditions",
                "question": "Marktbedingungen umfassen vor allem…",
                "options": {
                    "A": "Preisniveau, Liquiditaet, Handelsvolumen, Angebot/Nachfrage",
                    "B": "Teamgroesse des KMU",
                    "C": "Urlaubsplanung der Mitarbeitenden"
                },
                "correct": "A"
            }
        ]

        with st.form("post_knowledge_questionnaire"):
            responses = {}

            # Display all questions
            for i, q in enumerate(questions, 1):
                st.markdown(f"**Question {i} of {len(questions)}**")

                # Use radio buttons for each question
                answer = st.radio(
                    q["question"],
                    options=["A", "B", "C"],
                    format_func=lambda x, opts=q["options"]: f"{x}) {opts[x]}",
                    key=f"post_q_{q['id']}",
                    index=None  # No default selection
                )

                if answer:
                    responses[q["id"]] = {
                        "question": q["question"],
                        "selected_answer": answer,
                        "answer_text": q["options"][answer],
                        "correct_answer": q["correct"],
                        "is_correct": answer == q["correct"]
                    }

                st.markdown("---")

            submitted = st.form_submit_button("Fragebogen abschicken", type="primary")

            if submitted:
                # Check if all questions are answered
                if len(responses) < len(questions):
                    st.error(f"Bitte beantworte alle {len(questions)} Fragen, bevor du absendest.")
                    return

                # Calculate score (for logging only, not shown to user)
                score = sum(1 for r in responses.values() if r["is_correct"])

                # Check attention check
                attention_check_response = responses.get("attention_check_post")
                attention_check_failed = not attention_check_response.get("is_correct", False)

                if attention_check_failed:
                    # Log the attention check failure
                    if self.session_logger:
                        self.session_logger.log_event(
                            event_type="attention_check_failed",
                            metadata={
                                "question_id": "attention_check_post",
                                "selected_answer": attention_check_response.get("selected_answer", "N/A"),
                                "correct_answer": attention_check_response.get("correct_answer", "B"),
                                "participant_id": self.session_data.get("learner_profile", {}).get("unique_id", "N/A"),
                                "timestamp": datetime.now().isoformat()
                            }
                        )

                # Store questionnaire data in session
                questionnaire_data = {
                    "responses": responses,
                    "score": score,
                    "total_questions": len(questions),
                    "percentage": round((score / len(questions)) * 100, 2),
                    "completed_at": datetime.now().isoformat(),
                    "attention_check_passed": not attention_check_failed
                }

                # Add to session data
                self.session_data["post_knowledge_questionnaire"] = questionnaire_data

                # Log the questionnaire completion
                if self.session_logger:
                    self.session_logger.log_event(
                        event_type="post_knowledge_questionnaire_completed",
                        metadata={
                            "score": score,
                            "total_questions": len(questions),
                            "percentage": questionnaire_data["percentage"],
                            "detailed_responses": responses,
                            "attention_check_passed": not attention_check_failed
                        }
                    )

                # Update session state to mark questionnaire as completed
                st.session_state.post_questionnaire_completed = True
                st.success("✅ Fragebogen abgeschlossen! Danke fur deine Antworten.")
                st.info("📊 Weiter zum Fragebogen zur kognitiven Belastung...")

                # Automatically proceed
                st.rerun()

    
    def create_learner_profile_form(self) -> Dict[str, Any]:
        """Create learner profile through Streamlit form."""
        st.header("Lernendenprofil erstellen")
        st.markdown("Bitte erstelle dein Lernendenprofil, um die Erfahrung zu personalisieren.")
        
        # Add disclaimer
        st.warning("""
        **Wichtiger Hinweis:**
        
        Alle Daten werden anonymisiert. Wir erfassen keinen Klarnamen – waehle ein Alias.
                   
        Fuer die Integritaet der Studie bitten wir dich:
        - Nutze nur deine eigenen kognitiven Faehigkeiten und die bereitgestellten Materialien.
        - Verzichte auf ChatGPT oder andere KI-Assistenten waehrend der Aufgaben.
        
        Deine Browser-Aktivitaet (inkl. Tab-Wechsel) kann zur Sicherung der Datenqualitaet beobachtet werden.
        
        Deine ehrliche Teilnahme hilft uns, bessere Lernmaterialien zu entwickeln. Danke fuer deine Unterstuetzung!
        """)
        
        # Define dropdown options
        nationality_options = [
            "Please select...",
            "Afghan", "Albanian", "Algerian", "American", "Andorran", "Angolan", "Argentine", 
            "Armenian", "Australian", "Austrian", "Azerbaijani", "Bahamian", "Bahraini", 
            "Bangladeshi", "Barbadian", "Belarusian", "Belgian", "Belizean", "Beninese", 
            "Bhutanese", "Bolivian", "Bosnian", "Brazilian", "British", "Bruneian", "Bulgarian", 
            "Burkinabe", "Burmese", "Burundian", "Cambodian", "Cameroonian", "Canadian", 
            "Cape Verdean", "Central African", "Chadian", "Chilean", "Chinese", "Colombian", 
            "Comoran", "Congolese", "Costa Rican", "Croatian", "Cuban", "Cypriot", "Czech", 
            "Danish", "Djiboutian", "Dominican", "Dutch", "East Timorese", "Ecuadorean", 
            "Egyptian", "Emirian", "Equatorial Guinean", "Eritrean", "Estonian", "Ethiopian", 
            "Fijian", "Filipino", "Finnish", "French", "Gabonese", "Gambian", "Georgian", 
            "German", "Ghanaian", "Greek", "Grenadian", "Guatemalan", "Guinea-Bissauan", 
            "Guinean", "Guyanese", "Haitian", "Herzegovinian", "Honduran", "Hungarian", 
            "Icelandic", "Indian", "Indonesian", "Iranian", "Iraqi", "Irish", "Israeli", 
            "Italian", "Ivorian", "Jamaican", "Japanese", "Jordanian", "Kazakhstani", 
            "Kenyan", "Kittian and Nevisian", "Kuwaiti", "Kyrgyz", "Laotian", "Latvian", 
            "Lebanese", "Liberian", "Libyan", "Liechtensteiner", "Lithuanian", "Luxembourgish", 
            "Macedonian", "Malagasy", "Malawian", "Malaysian", "Maldivan", "Malian", "Maltese", 
            "Marshallese", "Mauritanian", "Mauritian", "Mexican", "Micronesian", "Moldovan", 
            "Monacan", "Mongolian", "Montenegrin", "Moroccan", "Mosotho", "Motswana", 
            "Mozambican", "Namibian", "Nauruan", "Nepalese", "New Zealander", "Nicaraguan", 
            "Nigerian", "Nigerien", "North Korean", "Norwegian", "Omani", "Pakistani", 
            "Palauan", "Palestinian", "Panamanian", "Papua New Guinean", "Paraguayan", 
            "Peruvian", "Polish", "Portuguese", "Qatari", "Romanian", "Russian", "Rwandan", 
            "Saint Lucian", "Salvadoran", "Samoan", "San Marinese", "Sao Tomean", "Saudi", 
            "Scottish", "Senegalese", "Serbian", "Seychellois", "Sierra Leonean", "Singaporean", 
            "Slovakian", "Slovenian", "Solomon Islander", "Somali", "South African", 
            "South Korean", "South Sudanese", "Spanish", "Sri Lankan", "Sudanese", "Surinamer", 
            "Swazi", "Swedish", "Swiss", "Syrian", "Taiwanese", "Tajik", "Tanzanian", "Thai", 
            "Togolese", "Tongan", "Trinidadian or Tobagonian", "Tunisian", "Turkish", 
            "Turkmen", "Tuvaluan", "Ugandan", "Ukrainian", "Uruguayan", "Uzbekistani", 
            "Venezuelan", "Vietnamese", "Welsh", "Yemenite", "Zambian", "Zimbabwean",
            "Other", "Prefer not to say"
        ]
        
        education_options = [
            "Please select...",
            "High School Diploma/Secondary Education",
            "Some College/University (no degree)",
            "Associate Degree/Diploma",
            "Bachelor's Degree",
            "Master's Degree",
            "Doctoral Degree (PhD/MD/JD/etc.)",
            "Professional Certification",
            "Other"
        ]
        
        gender_options = [
            "Please select...",
            "Female",
            "Male",
            "Non-binary",
            "Other/Prefer not to tell"
        ]
        
        with st.form("learner_profile_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Alias*", help="Choose an alias or identifier")
                age = st.number_input("Age*", min_value=18, max_value=100, help="Your age")
                gender = st.selectbox(
                    "Gender*",
                    options=gender_options,
                    help="Select your gender"
                )
                nationality = st.selectbox(
                    "Nationality*", 
                    options=nationality_options,
                    help="Select your nationality"
                )
                background = st.selectbox(
                    "Highest Educational Level*", 
                    options=education_options,
                    help="Select your highest completed educational level"
                )
            
            with col2:
                confidence = st.selectbox(
                    "Confidence in Concept Mapping*",
                    options=["1 - Very Low", "2 - Low", "3 - Moderate", "4 - High", "5 - Very High"],
                    help="How confident do you feel about concept mapping?"
                )

                confidencechat = st.selectbox(
                    "Confidence in Chatbot Interactions*",
                    options=["1 - Very Low", "2 - Low", "3 - Moderate", "4 - High", "5 - Very High"],
                    help="How confident do you feel about interacting with a chatbot?"
                )
                # # Learning factors that could affect outcome
                # st.markdown("**Learning Factors**")
                # st.caption("Please select any factors that may affect your learning (optional):")
                
                # learning_factors = []
                # if st.checkbox("ADHD"):
                #     learning_factors.append("ADHD")
                # if st.checkbox("AuDHD"):
                #     learning_factors.append("AuDHD")
                # if st.checkbox("Autism Spectrum Disorder"):
                #     learning_factors.append("Autism Spectrum Disorder")
                # if st.checkbox("Visual Processing Disorder"):
                #     learning_factors.append("Visual Processing Disorder")
                # if st.checkbox("Dyslexia"):
                #     learning_factors.append("Dyslexia")
                # if st.checkbox("Dyscalculia"):
                #     learning_factors.append("Dyscalculia")
                
                # other_factors = st.text_input("Other factors (please specify)", help="Any other learning factors not listed above")
                # if other_factors:
                #     learning_factors.append(f"Other: {other_factors}")
            
            submitted = st.form_submit_button("Create Profile", type="primary")
            
            if submitted:
                # Validate required fields
                if not all([name, age, gender, nationality, background, confidence, confidencechat]):
                    st.error("Please fill in all required fields marked with *")
                    return None
                
                # Validate dropdown selections (ensure not default values)
                if gender == "Please select...":
                    st.error("Please select your gender from the dropdown menu")
                    return None
                
                if nationality == "Please select...":
                    st.error("Please select your nationality from the dropdown menu")
                    return None
                
                if background == "Please select...":
                    st.error("Please select your highest educational level from the dropdown menu")
                    return None
                
#                # Use fixed Prolific completion code as unique ID
#                unique_id = "C1EF9RLL"
                
                # Assess background knowledge and determine scaffolding level
                background_score = self.assess_background_knowledge(background, "")  # No prior knowledge field anymore
                scaffolding_level = self.determine_scaffolding_level(background_score)
                
                profile = {
                    "name": name.strip(),
                    "unique_id": unique_id,
                    "age": age,
                    "gender": gender.strip(),
                    "nationality": nationality.strip(),
                    "background": background.strip(),
                    "confidence": confidence,
                    "confidencechat": confidencechat,
#                    "learning_factors": learning_factors,
                    "background_knowledge_score": background_score,
                    "scaffolding_level": scaffolding_level,
                    "zpd_level": scaffolding_level,  # For compatibility
                    "created_at": datetime.now().isoformat()
                }
                
                # Store in session data
                self.session_data["learner_profile"] = profile
                
                # Log profile creation
                if self.session_logger:
                    self.session_logger.log_event(
                        event_type="learner_profile_created",
                        metadata={
                            "profile": profile,
                            "background_assessment": {
                                "score": background_score,
                                "scaffolding_level": scaffolding_level,
                                "reasoning": f"Background knowledge score {background_score} → {scaffolding_level} assistance"
                            }
                        }
                    )
                
                st.success(f"Profil angelegt für {profile['name']}")
#                st.info("Your profile has been created successfully. Let's continue with the experiment.")
                
                return profile
        
        return None
    
    def assess_background_knowledge(self, background: str, prior_knowledge: str = "") -> int:
        """Assess background knowledge by comparing against AMG task concepts."""
        # AMG-related expert concepts for the market entry task
        expert_concepts = [
            "market entry", "market analysis", "target market", "competitive environment",
            "entry barriers", "legal framework", "startup resources", "entry strategy",
            "export", "joint venture", "direct investment", "financing",
            "marketing strategy", "success factors", "international expansion",
            "market research", "business strategy", "competition", "regulation",
            "capital", "partnership", "subsidiary", "distribution", "pricing"
        ]
        
        # Use background text (prior_knowledge parameter kept for compatibility but not used)
        combined_text = background.lower()
        
        # Count matches with expert concepts
        matches = 0
        for concept in expert_concepts:
            if concept in combined_text:
                matches += 1
        
        return matches
    
    def determine_scaffolding_level(self, background_score: int) -> str:
        """Determine assistance level based on background knowledge score."""
        # Higher background knowledge = lower scaffolding needed
        if background_score >= 8:  # High knowledge (8+ concepts mentioned)
            return "low"     # Low scaffolding needed
        elif background_score >= 4:  # Medium knowledge (4-7 concepts)
            return "medium"  # Medium scaffolding
        else:  # Low knowledge (0-3 concepts)
            return "high"    # High scaffolding needed
    
    def assign_experimental_condition(self) -> str:
        """
        Assign the single experimental condition (no randomization).
        
        Returns:
            Assigned experimental condition (fixed: EG_SEQ)
        """
        # Check if condition already assigned
        if "experimental_condition" in self.session_data:
            return self.session_data["experimental_condition"]
        
        assigned_condition = "EG_SEQ"
        
        # Store in session data
        self.session_data["experimental_condition"] = assigned_condition
        
        # Log the assignment
        if self.session_logger:
            self.session_logger.log_event(
                event_type="experimental_condition_assigned",
                metadata={
                    "experimental_condition": assigned_condition,
                    "session_id": self.session_data["session_id"],
                    "assignment_method": "fixed_single_condition",
                    "condition_index": 0,
                    "timestamp": datetime.now().isoformat()
                }
            )
        
        logger.info(f"Assigned experimental condition: {assigned_condition}")
        return assigned_condition
    
    def load_expert_map(self) -> Dict[str, Any]:
        """Load the expert concept map for comparison."""
        try:
            expert_map_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "examples", "data", "expert_concept_map.json"
            )
            with open(expert_map_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            # Return empty map if loading fails
            return {"nodes": [], "edges": []}
    
    def initialize_agent_sequence(self) -> List[str]:
        """Create agent sequence based on assigned experimental condition."""
        # Assign experimental condition for this session
        experimental_condition = self.assign_experimental_condition()
        
        # Get agent sequence based on experimental condition
        agents = AGENT_SEQUENCES.get(experimental_condition, AGENT_SEQUENCES['EG_SEQ'])
        
        # Note: Round 0 is handled separately (no scaffolding agent)
        
        self.session_data["agent_sequence"] = agents
        
        # Log the condition-based sequence
        if self.session_logger:
            self.session_logger.log_event(
                event_type="agent_sequence_initialized",
                metadata={
                    "agent_sequence": agents,
                    "experimental_condition": experimental_condition,
                    "participant_id": self.session_data["learner_profile"].get("name", "unknown"),
                    "sequence_type": "experimental_condition_based",
                    "total_rounds": 5,  # Including round 0
                    "note": f"Round 0 is baseline (no scaffolding), followed by 4 rounds with {experimental_condition} condition"
                }
            )
        
        return agents
    
    def get_agent_name(self, roundn: int) -> str:
        """Get formatted agent name for display."""
        # Round 0 is special - no scaffolding agent
        if roundn == 0:
            return "Initial Map Creation"
        
        # Adjust for 0-based indexing after round 0
        agent_index = roundn - 1
        if agent_index < len(self.session_data["agent_sequence"]):
            agent_type = self.session_data["agent_sequence"][agent_index]
            return agent_type.replace('_', ' ').title()
        return "Unknown Agent"
    
    def _clamp_followup_response(self, response: str, max_paragraphs: int = 2) -> str:
        """
        Clamp follow-up response to first 2 paragraphs (preserves scaffolding content).
        
        Splits by paragraph breaks (double newlines) and keeps only the first max_paragraphs.
        This preserves all scaffolding semantics, multiple sentences, and questions within those paragraphs.
        Rationale: We've had to do it for the german version only, as this language extends the text lenght significantly, thus, potentially causing cognitive overload.
        
        Args:
            response: The response text to clamp
            max_paragraphs: Maximum number of paragraphs to keep (default: 2)
            
        Returns:
            Clamped response with at most max_paragraphs
        """
        if not response:
            return response
        
        # Split by paragraph breaks (double newlines or single newlines followed by blank lines)
        paragraphs = [p.strip() for p in response.split('\n\n') if p.strip()]
        
        # Keep only first max_paragraphs
        if len(paragraphs) > max_paragraphs:
            clamped = '\n\n'.join(paragraphs[:max_paragraphs])
            logger.info(f"Clamped response from {len(paragraphs)} to {max_paragraphs} paragraphs")
            return clamped
        
        return response
    
    def convert_streamlit_to_internal_format(self, streamlit_cm_data) -> Dict[str, Any]:
        """Convert Streamlit concept map format to internal format with enhanced action tracking."""
        concepts = []
        relationships = []
        action_history = []
        interaction_metrics = {}
        session_timing = {}
        
        # Debug logging - always log for troubleshooting
        logger.info("🔍 DEBUG: Converting concept map data")
        logger.info(f"   Input type: {type(streamlit_cm_data).__name__}")
        logger.info(f"   Input data: {str(streamlit_cm_data)[:200] if streamlit_cm_data else 'None'}")
        
        if self.session_logger:
            self.session_logger.log_event(
                event_type="concept_map_conversion_debug",
                metadata={
                    "input_type": type(streamlit_cm_data).__name__,
                    "input_data": str(streamlit_cm_data)[:500] if streamlit_cm_data else "None",
                    "has_elements": "elements" in streamlit_cm_data if isinstance(streamlit_cm_data, dict) else False,
                    "has_action_history": "action_history" in streamlit_cm_data if isinstance(streamlit_cm_data, dict) else False
                }
            )
        
        # Handle different input types
        if streamlit_cm_data is None:
            logger.warning("   ⚠️  Input is None - returning empty structure")
            # Return empty structure for None input
            pass
        elif isinstance(streamlit_cm_data, str):
            logger.info("   📝 Input is string - attempting JSON parse")
            # Handle string input (might be JSON or initial map format)
            try:
                if streamlit_cm_data.strip():
                    parsed_data = json.loads(streamlit_cm_data)
                    if isinstance(parsed_data, dict):
                        streamlit_cm_data = parsed_data
                        logger.info(f"   ✅ Successfully parsed JSON: {len(parsed_data)} keys")
                    else:
                        # If it's not a valid dict after parsing, treat as empty
                        streamlit_cm_data = {}
                        logger.warning("   ⚠️  Parsed data is not a dict")
                else:
                    streamlit_cm_data = {}
                    logger.warning("   ⚠️  Empty string input")
            except (json.JSONDecodeError, AttributeError) as e:
                # If JSON parsing fails, treat as empty concept map
                streamlit_cm_data = {}
                logger.error(f"   ❌ JSON parsing failed: {e}")
        elif not isinstance(streamlit_cm_data, dict):
            logger.warning(f"   ⚠️  Input is not dict, string, or None: {type(streamlit_cm_data)}")
            # If it's not a dict, string, or None, treat as empty
            streamlit_cm_data = {}
        
        # Process the data if it's now a dictionary
        if isinstance(streamlit_cm_data, dict):
            logger.info(f"   📊 Processing dict with keys: {list(streamlit_cm_data.keys())}")
            
            # Extract action history and metrics if available (enhanced format)
            action_history = streamlit_cm_data.get("action_history", [])
            interaction_metrics = streamlit_cm_data.get("interaction_metrics", {})
            session_timing = streamlit_cm_data.get("session_timing", {})
            
            logger.info(f"   📈 Found {len(action_history)} actions, metrics: {bool(interaction_metrics)}")
            
            # Process concept map elements
            if "elements" in streamlit_cm_data:
                elements = streamlit_cm_data["elements"]
                if isinstance(elements, dict):
                    elements_list = []
                    elements_list.extend(elements.get("nodes", []))
                    elements_list.extend(elements.get("edges", []))
                else:
                    elements_list = elements
                logger.info(f"   🗺️  Processing {len(elements_list)} elements")

                if self.session_logger:
                    self.session_logger.log_event(
                        event_type="processing_elements",
                        metadata={
                            "element_count": len(elements_list),
                            "elements_preview": str(elements_list)[:300]
                        }
                    )

                for i, element in enumerate(elements_list):
                    if not isinstance(element, dict):
                        logger.warning(f"   ⚠️  Element {i} is not a dict: {type(element)}")
                        continue

                    if "data" not in element:
                        logger.warning(f"   ⚠️  Element {i} has no 'data' key: {list(element.keys())}")
                        continue

                    data = element.get("data", {})
                    logger.info(f"   🔍 Element {i} data: {data}")

                    if "id" in data and "source" not in data and "target" not in data:
                        concept = {
                            "id": data["id"],
                            "text": data.get("label", ""),
                            "x": data.get("x", 0),
                            "y": data.get("y", 0)
                        }
                        concepts.append(concept)
                        logger.info(f"   ✅ Added node: {concept}")

                        if self.session_logger:
                            self.session_logger.log_event(
                                event_type="node_processed",
                                metadata={"node": concept}
                            )

                    elif "source" in data and "target" in data:
                        relationship = {
                            "id": data.get("id", f"{data['source']}-{data['target']}"),
                            "source": data["source"],
                            "target": data["target"],
                            "text": data.get("label", "")
                        }
                        relationships.append(relationship)
                        logger.info(f"   ✅ Added edge: {relationship}")

                        if self.session_logger:
                            self.session_logger.log_event(
                                event_type="edge_processed",
                                metadata={"edge": relationship}
                            )
                    else:
                        logger.warning(f"   ⚠️  Element {i} is neither node nor edge: {data}")
            else:
                logger.warning("   ⚠️  No 'elements' key found in data")
        
        result = {
            "concepts": concepts,
            "relationships": relationships,
            "action_history": action_history,
            "interaction_metrics": interaction_metrics,
            "session_timing": session_timing,
            "timestamp": datetime.now().isoformat(),
            "source_format": "streamlit_enhanced"
        }
        
        logger.info(f"   🎯 Final result: {len(concepts)} concepts, {len(relationships)} relationships")
        
        # Final debug log
        if self.session_logger:
            self.session_logger.log_event(
                event_type="concept_map_conversion_result",
                metadata={
                    "concepts_count": len(concepts),
                    "relationships_count": len(relationships),
                    "action_history_count": len(action_history),
                    "has_interaction_metrics": bool(interaction_metrics),
                    "result_preview": str(result)[:500]
                }
            )
        
        return result
    
    def get_agent_response(self, roundn: int, concept_map_data: Optional[Dict[str, Any]] = None, user_response: Optional[str] = None, conversation_turn: int = 0) -> str:
        """Get agent response for the current round with pattern detection."""
        # Handle round 0 specially - no scaffolding
        if roundn == 0:
            return "Bitte erstelle deine erste Concept Map zum Thema. Nimm dir Zeit, alle relevanten Konzepte und Beziehungen einzutragen. Wenn du bereit bist, reiche die Concept Map ein, um fortzufahren."
        
        # Adjust for agent sequence after round 0
        agent_index = roundn - 1
        if agent_index >= len(self.session_data["agent_sequence"]):
            return "Session abgeschlossen. Vielen Dank fur deine Teilnahme!"
        
        agent_type = self.session_data["agent_sequence"][agent_index]
        
        # Apply pattern detection to ALL agents including neutral agent
        if user_response is not None and agent_type != "neutral":
            try:
                # Import pattern detection utilities
                from MAS.utils.scaffolding_utils import analyze_user_response_type
            except ImportError:
                from utils.scaffolding_utils import analyze_user_response_type
            
            # Analyze user response for patterns
            response_analysis = analyze_user_response_type(user_response)
            
            # Check if a pattern was detected that needs special handling
            if response_analysis.get("requires_pattern_response", False):
                # Generate pattern-specific response while maintaining agent context
                pattern_response = self._generate_pattern_response(
                    agent_type=agent_type,
                    response_analysis=response_analysis,
                    user_response=user_response,
                    concept_map_data=concept_map_data,
                    roundn=roundn,
                    conversation_turn=conversation_turn
                )
                
                if pattern_response:
                    # Apply post-filter for follow-ups (conversation_turn > 0)
                    if conversation_turn > 0:
                        pattern_response = self._clamp_followup_response(pattern_response)
                    
                    # Log the pattern-based response
                    if self.session_logger:
                        self.session_logger.log_agent_response(
                            agent_type=agent_type,
                            response_text=pattern_response,
                            metadata={
                                "round_number": roundn,
                                "conversation_turn": conversation_turn,
                                "response_type": "pattern_based",
                                "pattern_detected": response_analysis.get("response_type", "unknown"),
                                "experimental_condition": self.session_data.get("experimental_condition", "unknown"),
                                "concept_map_nodes": len(concept_map_data.get("elements", [])) if isinstance(concept_map_data, dict) and concept_map_data else 0
                            }
                        )
                    return pattern_response
        
        # Handle neutral agent - ALWAYS route to neutral agent, bypass pattern detection for domain questions
        if agent_type == "neutral":
            try:
                # Import and use NeutralAgent for ALL responses
                from MAS.agents.neutral_agent import NeutralAgent
            except ImportError:
                from agents.neutral_agent import NeutralAgent
            
            neutral_agent = NeutralAgent()
            
            # Convert concept map data to internal format for neutral agent
            internal_format = {"concepts": [], "relationships": []}
            if concept_map_data is not None:
                try:
                    internal_format = self.convert_streamlit_to_internal_format(concept_map_data)
                except Exception as e:
                    logger.warning(f"Failed to convert concept map for neutral agent: {e}")
            
            # CRITICAL FIX: Always use neutral agent for ALL responses, including domain questions
            neutral_response = neutral_agent.generate_response(
                user_message=user_response,
                concept_map=internal_format,
                context={"round_number": roundn, "conversation_turn": conversation_turn}
            )
            
            # Apply post-filter for follow-ups (conversation_turn > 0)
            if conversation_turn > 0:
                neutral_response = self._clamp_followup_response(neutral_response)
            
            # Log neutral response
            if self.session_logger:
                self.session_logger.log_agent_response(
                    agent_type=agent_type,
                    response_text=neutral_response,
                    metadata={
                        "round_number": roundn,
                        "conversation_turn": conversation_turn,
                        "response_type": "neutral_direct",
                        "experimental_condition": self.session_data.get("experimental_condition", "unknown"),
                        "concept_map_nodes": len(internal_format.get("concepts", [])),
                        "concept_map_edges": len(internal_format.get("relationships", []))
                    }
                )
            
            return neutral_response
        
        # Demo responses fallback
        demo_responses = {
            "conceptual_scaffolding": "Lass uns die konzeptuellen Beziehungen in deiner Map erkunden. Wie fugen sich diese Konzepte zu einem stimmigen Verstandnis zusammen?",
            "strategic_scaffolding": "Uberlege die strategische Struktur deiner Concept Map. Wie ordnest du die Ideen am effektivsten?",
            "metacognitive_scaffolding": "Reflektiere deinen Denkprozess. Wie sicher bist du dir bei diesen Beziehungen? Was konnte noch fehlen?",
            "procedural_scaffolding": "Schau auf die praktischen Schritte. Welche Vorgehensweise oder Tools hast du beim Erstellen der Map genutzt?"
        }
        
        # Try OpenAI integration for experimental mode (only for scaffolding agents)
        if self.session_data["mode"] == "experimental" and self.ai_manager and agent_type != "neutral":
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
                
                # CRITICAL FIX: Enhance the concept map with resolved labels
                # Build ID to text lookup dictionary
                id_to_text = {}
                for concept in internal_format.get("concepts", []):
                    concept_id = concept.get("id")
                    concept_text = concept.get("text", concept.get("label", concept_id))
                    if concept_id:
                        id_to_text[concept_id] = concept_text
                
                # Enhance relationships with resolved text labels
                enhanced_relationships = []
                for rel in internal_format.get("relationships", []):
                    enhanced_rel = rel.copy()
                    # Add resolved text labels
                    enhanced_rel["source_text"] = id_to_text.get(rel.get("source"), rel.get("source"))
                    enhanced_rel["target_text"] = id_to_text.get(rel.get("target"), rel.get("target"))
                    enhanced_relationships.append(enhanced_rel)
                
                # Update internal format with enhanced relationships
                internal_format["relationships"] = enhanced_relationships
                
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
                
                # Analyze concept map performance
                map_analysis = self.analyze_concept_map_performance(internal_format, roundn)
                
                # Get scaffolding level from learner profile
                scaffolding_level = self.session_data.get("learner_profile", {}).get("scaffolding_level", "medium")
                
                # Generate scaffolding response with level
                api_result = self.ai_manager.generate_scaffolding_response(
                    agent_type.replace("_scaffolding", ""), 
                    internal_format, 
                    user_response=user_response,
                    context=context,
                    scaffolding_level=scaffolding_level
                )
                
                # Log performance-scaffolding relationship
                self.log_scaffolding_decision(roundn, agent_type, scaffolding_level, map_analysis, api_result.get("response", ""))
                
                # Safely extract response
                if isinstance(api_result, dict):
                    response = api_result.get("response", "Entschuldige, ich habe Schwierigkeiten, eine Antwort zu erzeugen. Bitte arbeite an deiner Concept Map weiter oder springe zur nachsten Runde.")
                else:
                    response = str(api_result) if api_result else "Entschuldige, ich habe Schwierigkeiten, eine Antwort zu erzeugen. Bitte arbeite an deiner Concept Map weiter oder springe zur nachsten Runde."
                
                # Apply post-filter for follow-ups (conversation_turn > 0)
                if conversation_turn > 0:
                    response = self._clamp_followup_response(response)
                
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
                            "concept_map_edges": len(internal_format.get("relationships", [])),
                            "experimental_condition": self.session_data.get("experimental_condition", "unknown")
                        }
                    )
                
                return response
                
            except Exception as e:
                # Log the specific error for debugging
                error_msg = f"OpenAI integration failed: {type(e).__name__}: {str(e)}"
                if self.session_logger:
                    self.session_logger.log_event(
                        event_type="ai_integration_error",
                        metadata={
                            "round_number": roundn,
                            "error_type": type(e).__name__,
                            "error_message": str(e),
                            "agent_type": agent_type
                        }
                    )
                st.warning(f"{error_msg}. Ich nutze eine Demo-Antwort.")
                # Fall through to demo response
        
        # Use demo response with conversation awareness
        if conversation_turn > 0 and user_response:
            # Create contextual demo responses for follow-ups
            demo_followup_responses = {
                "conceptual_scaffolding": f"Du hast '{user_response[:50]}...' erwahnt. Wie passt das in den konzeptuellen Rahmen deiner Map?",
                "strategic_scaffolding": f"Ausgehend von '{user_response[:50]}...' – hast du alternative Organisationsstrategien bedacht?",
                "metacognitive_scaffolding": f"Deine Reflexion zu '{user_response[:50]}...' ist interessant. Was sagt dir das uber deinen Lernprozess?",
                "procedural_scaffolding": f"Du hast '{user_response[:50]}...' erwahnt. Wie lasst sich dieser Schritt mit anderen Methoden oder Tools vergleichen?"
            }
            response = demo_followup_responses.get(agent_type, demo_responses.get(agent_type, "Danke fur deine Antwort. Kannst du das noch etwas ausfuhrlicher erlautern?"))
        else:
            response = demo_responses.get(agent_type, demo_responses["conceptual_scaffolding"])
        
        # Apply post-filter for follow-ups (conversation_turn > 0)
        if conversation_turn > 0:
            response = self._clamp_followup_response(response)
        
        # Log demo response
        if self.session_logger:
            self.session_logger.log_agent_response(
                agent_type=agent_type,
                response_text=response,
                metadata={
                    "round_number": roundn,
                    "conversation_turn": conversation_turn,
                    "response_type": "demo",
                    "experimental_condition": self.session_data.get("experimental_condition", "unknown"),
                    "concept_map_nodes": len(concept_map_data.get("elements", [])) if isinstance(concept_map_data, dict) and concept_map_data else 0
                }
            )
        
        return response
    
    def _generate_pattern_response(self, agent_type: str, response_analysis: Dict[str, Any], 
                                  user_response: str, concept_map_data: Optional[Dict[str, Any]], 
                                  roundn: int, conversation_turn: int) -> Optional[str]:
        """Generate pattern-specific response while maintaining agent scaffolding context."""
        
        # Import handler functions from scaffolding_utils
        try:
            from MAS.utils.scaffolding_utils import (
                handle_help_seeking, handle_gibberish, handle_intention_without_action,
                handle_domain_question, handle_system_question, handle_disagreement,
                handle_empty_input, handle_inappropriate_language, handle_off_topic,
                handle_frustration, handle_premature_ending, generate_concrete_idea_followup,
                handle_greeting, handle_minimal_input, handle_reassurance_seeking
            )
        except ImportError:
            from utils.scaffolding_utils import (
                handle_help_seeking, handle_gibberish, handle_intention_without_action,
                handle_domain_question, handle_system_question, handle_disagreement,
                handle_empty_input, handle_inappropriate_language, handle_off_topic,
                handle_frustration, handle_premature_ending, generate_concrete_idea_followup,
                handle_greeting, handle_minimal_input, handle_reassurance_seeking
            )
        
        # Get the pattern type detected
        pattern_type = response_analysis.get("response_type", "unknown")
        
        # Handle neutral agent patterns with neutral responses
        if agent_type == "neutral":
            # Convert concept map data for neutral agent
            internal_format = {"concepts": [], "relationships": []}
            if concept_map_data is not None:
                try:
                    internal_format = self.convert_streamlit_to_internal_format(concept_map_data)
                except Exception as e:
                    logger.warning(f"Failed to convert concept map for neutral pattern: {e}")
            
            # Load expert map for comparison
            expert_map = self.load_expert_map()
            
            # Handle patterns with neutral responses
            if pattern_type == "interface_help":
                # CRITICAL FIX: Neutral agent should also use universal interface help
                try:
                    from MAS.utils.scaffolding_utils import handle_interface_help
                except ImportError:
                    from utils.scaffolding_utils import handle_interface_help
                return handle_interface_help(user_response)
            elif pattern_type == "reassurance_seeking":
                return handle_reassurance_seeking(user_response, internal_format, expert_map)
            elif pattern_type == "help_seeking":
                return "Bitte nutze die Buttons 'Task Description' und 'Extra Materials' fur Hinweise. Arbeite an deiner Concept Map wie beschrieben weiter."
            elif pattern_type == "empty_input":
                return "Bitte gib deine Antwort ein oder klicke auf 'Finish Round', um zur nachsten Runde zu gehen."
            elif pattern_type == "gibberish":
                return "Das habe ich nicht verstanden. Bitte arbeite an deiner Concept Map wie beschrieben weiter."
            elif pattern_type == "greeting":
                return "Hallo! Bitte arbeite an deiner Concept Map wie in den Anweisungen beschrieben weiter."
            elif pattern_type == "minimal_input":
                return "Bitte entwickle deine Concept Map weiter wie in der Aufgabe vorgesehen."
            elif pattern_type == "system_question":
                return "Das entscheidest du anhand der Aufgabenbeschreibung. Arbeite weiter, wie du es fur richtig haltst."
            elif pattern_type == "disagreement":
                return "Verstanden, dass du es anders siehst. Bitte arbeite an deiner Concept Map weiter, wie du es fur richtig haltst."
            elif pattern_type == "inappropriate_language":
                return "Lass uns beim Thema Concept Mapping bleiben. Bitte arbeite wie angewiesen weiter."
            elif pattern_type == "off_topic":
                return "Bitte konzentriere dich auf die Concept-Mapping-Aufgabe. Baue deine Map wie beschrieben weiter aus."
            elif pattern_type == "frustration":
                return "Nimm dir Zeit fur die Concept-Mapping-Aufgabe. Arbeite nach den bereitgestellten Anweisungen weiter."
            elif pattern_type == "premature_ending":
                return "Dein Beitrag ist wichtig fur die Studie. Bitte fahre mit der Concept-Mapping-Aufgabe wie vorgesehen fort."
            elif pattern_type in ["concrete_idea", "conversational", "intention_without_action"]:
                # Acknowledge without scaffolding
                idea_snippet = user_response[:30] + "..." if len(user_response) > 30 else user_response
                return f"Ich sehe, du hast '{idea_snippet}' erwahnt. Fahre fort, deine Concept Map nach deinen Vorstellungen auszubauen."
            else:
                # Default neutral response
                node_count = len(internal_format.get("concepts", []))
                if node_count > 0:
                    return f"Deine Map hat bisher {node_count} Konzepte - bitte arbeite wie angewiesen weiter."
                else:
                    return "Bitte arbeite an deiner Concept Map wie beschrieben weiter."
        
        # Extract scaffolding type without "_scaffolding" suffix for handlers
        scaffolding_type_clean = agent_type.replace("_scaffolding", "")
        
        # Route to appropriate handler based on pattern type for scaffolding agents
        pattern_response = None
        
        # CRITICAL FIX: Interface help pattern - UNIVERSAL for ALL agents (highest priority)
        if pattern_type == "interface_help":
            # Import the universal interface help handler
            try:
                from MAS.utils.scaffolding_utils import handle_interface_help
            except ImportError:
                from utils.scaffolding_utils import handle_interface_help
            pattern_response = handle_interface_help(user_response)
        
        # NEW PATTERNS - Priority handling
        elif pattern_type == "greeting":
            pattern_response = handle_greeting(scaffolding_type_clean)
        elif pattern_type == "minimal_input":
            pattern_response = handle_minimal_input(scaffolding_type_clean)
        elif pattern_type == "help_seeking":
            pattern_response = handle_help_seeking(user_response, scaffolding_type_clean)
        elif pattern_type == "gibberish":
            pattern_response = handle_gibberish(scaffolding_type_clean)
        elif pattern_type == "intention_without_action":
            pattern_response = handle_intention_without_action(user_response, scaffolding_type_clean)
        elif pattern_type == "reassurance_seeking":
            # Convert concept map for scaffolding agents too
            internal_format = {"concepts": [], "relationships": []}
            if concept_map_data is not None:
                try:
                    internal_format = self.convert_streamlit_to_internal_format(concept_map_data)
                except Exception as e:
                    logger.warning(f"Failed to convert concept map for reassurance pattern: {e}")
            expert_map = self.load_expert_map()
            pattern_response = handle_reassurance_seeking(user_response, internal_format, expert_map)
        
        # EXISTING PATTERNS
        elif pattern_type == "empty_input":
            pattern_response = handle_empty_input(scaffolding_type_clean)
        elif pattern_type == "inappropriate_language":
            pattern_response = handle_inappropriate_language(scaffolding_type_clean)
        elif pattern_type == "disagreement":
            disagreement_type = response_analysis.get("disagreement_type", "general")
            pattern_response = handle_disagreement(user_response, scaffolding_type_clean, disagreement_type)
        elif pattern_type == "question":
            # Differentiate between domain and system questions
            if response_analysis.get("is_domain_question"):
                key_phrases = response_analysis.get("key_phrases", [])
                pattern_response = handle_domain_question(user_response, scaffolding_type_clean, key_phrases)
            elif response_analysis.get("is_system_question"):
                pattern_response = handle_system_question(user_response, scaffolding_type_clean)
            else:
                # Generic question handling - let AI handle it
                pattern_response = None
        elif pattern_type == "frustration":
            pattern_response = handle_frustration(user_response, scaffolding_type_clean)
        elif pattern_type == "off_topic":
            pattern_response = handle_off_topic(scaffolding_type_clean)
        elif pattern_type == "premature_ending":
            pattern_response = handle_premature_ending(scaffolding_type_clean)
        
        # Pattern 5: Concrete Ideas (Critical Fix)
        elif pattern_type == "concrete_idea" and response_analysis.get("contains_idea", False):
            # Only affirm if user actually shared an idea
            mentions_concepts = response_analysis.get("mentions_concepts", [])
            pattern_response = generate_concrete_idea_followup(user_response, scaffolding_type_clean, mentions_concepts)
        
        # For conversational engagement pattern (Pattern 5 critical fix)
        elif pattern_type == "conversational" and response_analysis.get("contains_idea", False):
            # Only affirm if user actually shared an idea
            pattern_response = self._generate_idea_affirmation_response(
                agent_type, user_response, concept_map_data
            )
        
        return pattern_response
    
    def _generate_idea_affirmation_response(self, agent_type: str, user_response: str, 
                                           concept_map_data: Optional[Dict[str, Any]]) -> str:
        """Generate appropriate affirmation when user shares actual ideas (Pattern 5 fix)."""
        
        # Extract the user's idea (first 50 chars for context)
        idea_snippet = user_response[:50] + "..." if len(user_response) > 50 else user_response
        
        # Agent-specific idea affirmations with call to action
        idea_responses = {
            "conceptual_scaffolding": f"Spiegelt deine Concept Map '{idea_snippet}' wider? Fuge ggf. einen Knoten oder eine Beziehung hinzu.",
            "procedural_scaffolding": f"Wie kannst du '{idea_snippet}' in deinen Mapping-Prozess einbauen? Versuche es als beschriftete Beziehung einzutragen.",
            "strategic_scaffolding": f"Wie passt '{idea_snippet}' in deine Gesamtstruktur? Ordne verwandte Konzepte ggf. um, um das hervorzuheben.",
            "metacognitive_scaffolding": f"Was sagt dir '{idea_snippet}' uber dein Verstandnis? Wie sicher kannst du das in der Map darstellen?"
        }
        
        return idea_responses.get(agent_type, f"Ich sehe, du hast '{idea_snippet}' erwahnt. Wie hangt das mit deiner Concept Map zusammen?")
    
    def log_user_response(self, roundn: int, user_response: str, concept_map_data: Optional[Dict[str, Any]] = None):
        """Log user response to scaffolding."""
        if self.session_logger:
            # Determine agent type (None for round 0)
            if roundn == 0:
                agent_type = None
            else:
                agent_index = roundn - 1
                agent_type = self.session_data["agent_sequence"][agent_index] if agent_index < len(self.session_data["agent_sequence"]) else None
            
            self.session_logger.log_user_input(
                input_text=user_response,
                metadata={
                    "round_number": roundn,
                    "agent_type": agent_type,
                    "concept_map_provided": concept_map_data is not None
                }
            )
    
    def update_concept_map_evolution(self, roundn: int, concept_map_data):
        """Update the concept map evolution tracking with enhanced action logging."""
        try:
            # Convert to internal format with robust error handling
            internal_format = self.convert_streamlit_to_internal_format(concept_map_data)
            
            # Extract action history and metrics if available
            action_history = internal_format.get("action_history", [])
            interaction_metrics = internal_format.get("interaction_metrics", {})
            session_timing = internal_format.get("session_timing", {})
            
            # Determine agent type (None for round 0)
            if roundn == 0:
                agent_type = None
            else:
                agent_index = roundn - 1
                agent_type = self.session_data["agent_sequence"][agent_index] if agent_index < len(self.session_data["agent_sequence"]) else None
            
            # Add to evolution with enhanced data
            evolution_entry = {
                "round": roundn,
                "timestamp": datetime.now().isoformat(),
                "concept_map": internal_format,
                "agent_type": agent_type,
                "action_history": action_history,
                "interaction_metrics": interaction_metrics,
                "session_timing": session_timing
            }
            
            self.session_data["concept_map_evolution"].append(evolution_entry)
            
            # Update current concept map (cumulative)
            self.session_data["current_concept_map"] = internal_format
            
            # Log detailed concept map actions if available
            if action_history and self.session_logger:
                self.log_detailed_concept_map_actions(roundn, action_history, interaction_metrics)
            
            # Log concept map update
            if self.session_logger:
                self.session_logger.log_event(
                    event_type="concept_map_updated",
                    metadata={
                        "round_number": roundn,
                        "nodes_count": len(internal_format.get("concepts", [])),
                        "edges_count": len(internal_format.get("relationships", [])),
                        "evolution_length": len(self.session_data["concept_map_evolution"]),
                        "input_data_type": type(concept_map_data).__name__,
                        "action_count": len(action_history),
                        "interaction_metrics": interaction_metrics
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
            
            # Determine agent type (None for round 0)
            if roundn == 0:
                agent_type = None
            else:
                agent_index = roundn - 1
                agent_type = self.session_data["agent_sequence"][agent_index] if agent_index < len(self.session_data["agent_sequence"]) else None
            
            # Create a minimal evolution entry to maintain session continuity
            evolution_entry = {
                "round": roundn,
                "timestamp": datetime.now().isoformat(),
                "concept_map": {"concepts": [], "relationships": [], "error": str(e)},
                "agent_type": agent_type,
                "action_history": [],
                "interaction_metrics": {},
                "session_timing": {}
            }
            self.session_data["concept_map_evolution"].append(evolution_entry)
    
    def log_detailed_concept_map_actions(self, roundn: int, action_history: List[Dict], interaction_metrics: Dict):
        """Log detailed concept map actions for research analysis."""
        if not self.session_logger:
            return
        
        # Analyze action patterns
        action_patterns = self.analyze_action_patterns(action_history)
        
        # Log comprehensive action data
        self.session_logger.log_event(
            event_type="detailed_concept_map_actions",
            metadata={
                "round_number": roundn,
                "agent_type": self.session_data["agent_sequence"][roundn] if roundn < len(self.session_data["agent_sequence"]) else None,
                "total_actions": len(action_history),
                "action_breakdown": {
                    "nodes_created": interaction_metrics.get("nodes_created", 0),
                    "edges_created": interaction_metrics.get("edges_created", 0),
                    "nodes_deleted": interaction_metrics.get("nodes_deleted", 0),
                    "edges_deleted": interaction_metrics.get("edges_deleted", 0),
                    "labels_edited": interaction_metrics.get("labels_edited", 0),
                    "nodes_moved": interaction_metrics.get("nodes_moved", 0)
                },
                "action_patterns": action_patterns,
                "detailed_actions": action_history[-10:] if len(action_history) > 10 else action_history,  # Last 10 actions for detail
                "interaction_metrics": interaction_metrics
            }
        )
    
    def analyze_action_patterns(self, action_history: List[Dict]) -> Dict[str, Any]:
        """Analyze patterns in user concept map actions."""
        if not action_history:
            return {}
        
        # Count action types
        action_counts = {}
        action_sequences = []
        time_intervals = []
        
        for i, action in enumerate(action_history):
            action_type = action.get("action_type", "unknown")
            action_counts[action_type] = action_counts.get(action_type, 0) + 1
            action_sequences.append(action_type)
            
            # Calculate time intervals between actions
            if i > 0:
                try:
                    current_time = datetime.fromisoformat(action["timestamp"].replace('Z', '+00:00'))
                    prev_time = datetime.fromisoformat(action_history[i-1]["timestamp"].replace('Z', '+00:00'))
                    interval = (current_time - prev_time).total_seconds()
                    time_intervals.append(interval)
                except:
                    pass
        
        # Analyze patterns
        patterns = {
            "action_counts": action_counts,
            "total_actions": len(action_history),
            "most_common_action": max(action_counts.items(), key=lambda x: x[1])[0] if action_counts else None,
            "action_diversity": len(action_counts),
            "average_time_between_actions": sum(time_intervals) / len(time_intervals) if time_intervals else 0,
            "building_strategy": self.determine_building_strategy(action_sequences),
            "editing_behavior": self.analyze_editing_behavior(action_history)
        }
        
        return patterns
    
    def determine_building_strategy(self, action_sequences: List[str]) -> str:
        """Determine the user's concept map building strategy."""
        if not action_sequences:
            return "unknown"
        
        # Count consecutive node vs edge additions
        node_streaks = 0
        edge_streaks = 0
        current_streak = 1
        current_type = None
        
        for action in action_sequences:
            if action in ["add_node", "add_edge"]:
                if action == current_type:
                    current_streak += 1
                else:
                    if current_type == "add_node" and current_streak >= 3:
                        node_streaks += 1
                    elif current_type == "add_edge" and current_streak >= 2:
                        edge_streaks += 1
                    current_type = action
                    current_streak = 1
        
        # Determine strategy
        if node_streaks > edge_streaks:
            return "node_first"  # Adds many nodes then connects
        elif edge_streaks > node_streaks:
            return "incremental"  # Builds incrementally (node-edge-node-edge)
        else:
            return "mixed"  # Mixed approach
    
    def analyze_editing_behavior(self, action_history: List[Dict]) -> Dict[str, Any]:
        """Analyze editing and revision behavior."""
        edit_actions = [a for a in action_history if a.get("action_type") in ["edit_label", "delete_node", "delete_edge", "move_node"]]
        creation_actions = [a for a in action_history if a.get("action_type") in ["add_node", "add_edge"]]
        
        return {
            "total_edits": len(edit_actions),
            "total_creations": len(creation_actions),
            "edit_ratio": len(edit_actions) / max(1, len(creation_actions)),
            "revision_frequency": len(edit_actions) / max(1, len(action_history)),
            "most_edited_elements": self.find_most_edited_elements(edit_actions)
        }
    
    def find_most_edited_elements(self, edit_actions: List[Dict]) -> Dict[str, int]:
        """Find which elements were edited most frequently."""
        element_edit_counts = {}
        
        for action in edit_actions:
            element_id = action.get("element_id")
            if element_id:
                element_edit_counts[element_id] = element_edit_counts.get(element_id, 0) + 1
        
        # Return top 5 most edited elements
        sorted_elements = sorted(element_edit_counts.items(), key=lambda x: x[1], reverse=True)
        return dict(sorted_elements[:5])
    
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
            
            # Calculate and add map summary statistics
            final_nodes = len(self.session_data["current_concept_map"].get("concepts", []))
            final_edges = len(self.session_data["current_concept_map"].get("relationships", []))
            
            # Add map_summary to session data for easy identification
            self.session_data["map_summary"] = {
                "final_nodes": final_nodes,
                "final_edges": final_edges,
                "connectivity_ratio": round(final_edges / max(1, final_nodes), 2),
                "participant_id": self.session_data.get("learner_profile", {}).get("unique_id", "N/A"),
                "participant_name": self.session_data.get("learner_profile", {}).get("name", "Unknown")
            }
            
            # Save session data
            export_info = self.save_session_data()
            
            # Log session end with map summary
            if self.session_logger:
                # Log map summary event for easy identification
                self.session_logger.log_event(
                    event_type="map_summary",
                    metadata=self.session_data["map_summary"]
                )
                
                self.session_logger.log_session_end({
                    "total_rounds": len(self.session_data["rounds"]),
                    "final_nodes": final_nodes,
                    "final_edges": final_edges,
                    "export_files": export_info
                })
            
            # Export session log to the database
            if self.db_service:
                self.db_service.insert_session_log(self.session_logger.log_entries)

            logger.info("Session was finalized successfully") 
            return export_info
            
        except Exception as e:
            st.error(f"Error finalizing session: {e}")
            return {"error": str(e)}
    
    def save_session_data(self) -> Dict[str, str]:
        """Save complete session data to JSON and CSV files."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            participant_name = self.session_data['learner_profile'].get('name', 'unknown')
            
            # Create experimental_data directory - use correct path relative to project root
            experimental_data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "experimental_data")
            os.makedirs(experimental_data_dir, exist_ok=True)
            
            # JSON export (complete session data)
            json_filename = f"experimental_session_{participant_name}_{timestamp}.json"
            json_filepath = os.path.join(experimental_data_dir, json_filename)
            
            with open(json_filepath, 'w', encoding='utf-8') as f:
                json.dump(self.session_data, f, indent=2, ensure_ascii=False)
            
            # CSV export (flattened for analysis)
            csv_filename = f"experimental_results_{participant_name}_{timestamp}.csv"
            csv_filepath = os.path.join(experimental_data_dir, csv_filename)
            
            self._export_csv_data(csv_filepath)

            # Export session data to the database
            if self.db_service:
                self.db_service.insert_session(self.session_data)

            return {
                "json_file": json_filepath,
                "csv_file": csv_filepath,
                "participant_name": participant_name,
                "timestamp": timestamp
            }
            
        except Exception as e:
            st.error(f"Error saving session data: {e}")
            return {"error": str(e)}
    

    def _save_session_to_database(self):
        """
        Converts the generated json file into the Session DTO and stores the session in 
        the database sessions collection.
        """    
        


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
                "experimental_condition": self.session_data.get("experimental_condition", "unknown"),
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
        
        # Determine agent type and speaker ID
        if speaker == "agent":
            if roundn == 0:
                # Round 0 has no agent
                speaker_id = "system"
                agent_type = None
            else:
                # Get specific agent type for rounds 1-4
                agent_index = roundn - 1
                if agent_index < len(self.session_data["agent_sequence"]):
                    agent_type = self.session_data["agent_sequence"][agent_index]
                    speaker_id = agent_type
                else:
                    speaker_id = speaker
                    agent_type = None
        else:
            speaker_id = speaker
            agent_type = None
        
        conversation_entry = {
            "speaker": speaker_id,
            "agent_type": agent_type,
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
        # Count only user messages to limit to 5 user interactions
        history = self.get_conversation_history(roundn)
        user_message_count = len([msg for msg in history if msg.get("speaker") == "user"])
        max_user_messages = 5
        return user_message_count < max_user_messages
    
    def analyze_concept_map_performance(self, concept_map: Dict[str, Any], roundn: int) -> Dict[str, Any]:
        """Analyze concept map performance for scaffolding decisions."""
        try:
            # Import scaffolding utilities
            from MAS.utils.scaffolding_utils import analyze_concept_map
        except ImportError:
            # Fallback implementation
            return self._basic_concept_map_analysis(concept_map, roundn)
        
        # Get previous map for comparison
        previous_map = None
        if roundn > 0 and len(self.session_data["concept_map_evolution"]) > 0:
            previous_entry = self.session_data["concept_map_evolution"][-1]
            previous_map = previous_entry.get("concept_map", {})
        
        # Load expert map
        expert_map = self.load_expert_map()
        
        # Convert expert map format if needed
        if expert_map and "nodes" in expert_map:
            # Convert expert map to internal format
            expert_internal = {
                "concepts": [{"text": node, "id": node} for node in expert_map["nodes"]],
                "relationships": [
                    {"source": edge["source"], "target": edge["target"], "text": edge.get("relation", "")}
                    for edge in expert_map.get("edges", [])
                ]
            }
        else:
            expert_internal = {"concepts": [], "relationships": []}
        
        # Perform analysis
        analysis = analyze_concept_map(concept_map, previous_map, expert_internal)
        
        # Add round-specific information
        analysis["round_number"] = roundn
        analysis["timestamp"] = datetime.now().isoformat()
        
        return analysis
    
    def _basic_concept_map_analysis(self, concept_map: Dict[str, Any], roundn: int) -> Dict[str, Any]:
        """Basic concept map analysis fallback."""
        concepts = concept_map.get("concepts", [])
        relationships = concept_map.get("relationships", [])
        
        # Basic metrics
        node_count = len(concepts)
        edge_count = len(relationships)
        connectivity_ratio = edge_count / max(1, node_count)
        
        # Simple ZPD estimation
        zpd_estimate = {
            "strategic": 0.5,
            "metacognitive": 0.5,
            "procedural": 0.5,
            "conceptual": 0.5
        }
        
        # Adjust based on basic metrics
        if node_count < 3:
            zpd_estimate["conceptual"] = 0.8
        elif node_count > 10:
            zpd_estimate["conceptual"] = 0.2
        
        if connectivity_ratio < 0.5:
            zpd_estimate["strategic"] = 0.8
        elif connectivity_ratio > 1.5:
            zpd_estimate["strategic"] = 0.2
        
        return {
            "node_count": node_count,
            "edge_count": edge_count,
            "connectivity_ratio": connectivity_ratio,
            "isolated_nodes": [],
            "central_nodes": [],
            "missing_nodes": [],
            "missing_edges": [],
            "zpd_estimate": zpd_estimate,
            "round_number": roundn,
            "timestamp": datetime.now().isoformat()
        }
    
    def log_scaffolding_decision(self, roundn: int, agent_type: str, scaffolding_level: str, 
                                map_analysis: Dict[str, Any], agent_response: str):
        """Log the complete performance-scaffolding relationship."""
        if self.session_logger:
            # Calculate expert similarity if possible
            expert_similarity = self.calculate_expert_similarity(map_analysis)
            
            # Calculate improvement from previous round
            improvement = self.calculate_improvement_from_previous(roundn)
            
            self.session_logger.log_event(
                event_type="scaffolding_decision",
                metadata={
                    "round_number": roundn,
                    "agent_type": agent_type,
                    "scaffolding_level": scaffolding_level,
                    "background_knowledge_score": self.session_data.get("learner_profile", {}).get("background_knowledge_score", 0),
                    "concept_map_performance": {
                        "nodes": map_analysis.get("node_count", 0),
                        "edges": map_analysis.get("edge_count", 0),
                        "connectivity": map_analysis.get("connectivity_ratio", 0),
                        "isolated_nodes": len(map_analysis.get("isolated_nodes", [])),
                        "expert_similarity": expert_similarity,
                        "improvement_from_previous": improvement
                    },
                    "zpd_estimates": map_analysis.get("zpd_estimate", {}),
                    "agent_response": agent_response,
                    "scaffolding_reasoning": f"Background knowledge score {self.session_data.get('learner_profile', {}).get('background_knowledge_score', 0)} → {scaffolding_level} scaffolding",
                    "performance_indicators": {
                        "map_complexity": map_analysis.get("node_count", 0) + map_analysis.get("edge_count", 0),
                        "organization_quality": map_analysis.get("connectivity_ratio", 0),
                        "conceptual_coverage": len(map_analysis.get("central_nodes", []))
                    }
                }
            )
    
    def calculate_expert_similarity(self, map_analysis: Dict[str, Any]) -> float:
        """Calculate similarity to expert concept map."""
        try:
            expert_map = self.load_expert_map()
            if not expert_map or not expert_map.get("nodes"):
                return 0.0
            
            expert_node_count = len(expert_map["nodes"])
            expert_edge_count = len(expert_map.get("edges", []))
            
            current_node_count = map_analysis.get("node_count", 0)
            current_edge_count = map_analysis.get("edge_count", 0)
            
            # Simple similarity based on coverage
            node_similarity = min(current_node_count / max(1, expert_node_count), 1.0)
            edge_similarity = min(current_edge_count / max(1, expert_edge_count), 1.0)
            
            # Weighted average
            similarity = (node_similarity * 0.6) + (edge_similarity * 0.4)
            return round(similarity, 3)
            
        except Exception:
            return 0.0
    
    def calculate_improvement_from_previous(self, roundn: int) -> Dict[str, Any]:
        """Calculate improvement from previous round."""
        if roundn == 0 or len(self.session_data["concept_map_evolution"]) < 2:
            return {"node_growth": 0, "edge_growth": 0, "connectivity_change": 0.0}
        
        try:
            current_map = self.session_data["concept_map_evolution"][-1]["concept_map"]
            previous_map = self.session_data["concept_map_evolution"][-2]["concept_map"]
            
            current_nodes = len(current_map.get("concepts", []))
            current_edges = len(current_map.get("relationships", []))
            current_connectivity = current_edges / max(1, current_nodes)
            
            previous_nodes = len(previous_map.get("concepts", []))
            previous_edges = len(previous_map.get("relationships", []))
            previous_connectivity = previous_edges / max(1, previous_nodes)
            
            return {
                "node_growth": current_nodes - previous_nodes,
                "edge_growth": current_edges - previous_edges,
                "connectivity_change": round(current_connectivity - previous_connectivity, 3)
            }
            
        except Exception:
            return {"node_growth": 0, "edge_growth": 0, "connectivity_change": 0.0}
    
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
