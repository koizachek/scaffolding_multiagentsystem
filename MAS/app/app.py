import json
import os
import copy
import logging
from datetime import datetime
from typing import Dict, Optional
import streamlit as st
from conceptmap_component import conceptmap_component, parse_conceptmap
from streamlit.runtime.state import session_state
from streamlit_experimental_session import StreamlitExperimentalSession
from task_content import (
    STUDY_TITLE, STUDY_INTRODUCTION, TASK_DESCRIPTION,
    EXTRA_MATERIALS, INITIAL_CONCEPT_MAP
)
from text_to_image import render_protected_markdown
from streamlit_scroll_to_top import scroll_to_here

logger = logging.getLogger(__name__)


# Session State Initialization
def init_session_state():
    """Initialize session state with experimental session support."""
    if "contents" not in st.session_state:
        st.session_state.contents = load_contents()

    # Auto Scroll
    if 'scroll_to_top' not in st.session_state:
        st.session_state.scroll_to_top = False


    # Initialize other defaults
    defaults = {
        "experimental_session": None,
        "mode": None,
        "learner_profile": None,
        "agent_sequence": [],
        "submit_request": False,
        "followup": False,
        "roundn": 0,
        "consent_given": False,
        "consent_declined": False,
        "attention_check_failed": False,
        "profile_initialisation_started": False,
        "session_initialized": False,
        "profile_initialized": False,
        "pre_questionnaire_completed": False,
        "clt_completed": False,
        "post_questionnaire_completed": False,
        "session_finalized": False,
        "tutorial_completed": False,
        "conversation_turn": 0,
        "conversation_history": {},
        "agent_msg": None,
        "show_tutorial": False
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    # Initialize concept map data separately to avoid corruption
    if "cmdata" not in st.session_state or not isinstance(st.session_state.cmdata, list):
        initial_map = copy.deepcopy(st.session_state.contents["initial_map"])
        st.session_state.cmdata = [initial_map]

    # Set max rounds (now 5 total: round 1 + 4 scaffolding rounds)
    if 'max_rounds' not in st.session_state:
        st.session_state.max_rounds = 5  # Round 1 + 4 scaffolding rounds


def load_contents():
    """Load contents configuration."""
    path = os.path.join(os.path.dirname(__file__), "contents.json")
    with open(path) as f:
        return json.load(f)


def get_current_round_data(round_num):
    """Get current round data for concept map."""
    # Ensure we have enough slots in cmdata
    while len(st.session_state.cmdata) <= round_num:
        if len(st.session_state.cmdata) > 0:
            # Copy the previous round's data as starting point
            previous_map = copy.deepcopy(st.session_state.cmdata[-1])
            st.session_state.cmdata.append(previous_map)
        else:
            # First round uses initial map
            st.session_state.cmdata.append(st.session_state.contents["initial_map"])

    return st.session_state.cmdata[round_num]


def ensure_cm_slot(round_num):
    """Guarantee that cmdata[round_num] exists."""
    while len(st.session_state.cmdata) <= round_num:
        if len(st.session_state.cmdata) > 0:
            # Copy the previous round's data as starting point
            previous_map = copy.deepcopy(st.session_state.cmdata[-1])
            st.session_state.cmdata.append(previous_map)
        else:
            # First round uses initial map
            st.session_state.cmdata.append(st.session_state.contents["initial_map"])


def render_mode_selection():
    """Render mode selection page."""
    st.header(STUDY_TITLE)
    st.markdown("---")

    # Add page refresh warning at the top
    st.error("""
    🚫 **BITTE DIE SEITE NICHT AKTUALISIEREN**

    Ein Neuladen wuerde die Sitzung von vorne beginnen lassen und Fortschritt loeschen!
    Bitte das gesamte Experiment in einer Sitzung absolvieren.
    """)

    # Display the study introduction as regular text (not protected)
    st.markdown("### Studien-Einfuehrung")
    st.markdown(STUDY_INTRODUCTION)

    # Display topic as regular text (not protected)
    st.info(
        "**Thema:** Teilnahme von KMU an AI-CO2-Handelssystemen unter dem AI Carbon Credit Transfer Protocol (AICCTP).")

    # Task description and resources information
    st.success("""
    📋 **Aufgabenbeschreibung & Materialien:**

    Diese Studie untersucht die Nuetzlichkeit von Chatbot-Anweisungen beim Lernen. Im Experiment hast du durchgehend Zugriff auf:
    - **Aufgabenbeschreibung**: Das konkrete Problem, das du per Concept Map loesen sollst
    - **Zusatzmaterialien**: Weitere Ressourcen zum besseren Verstaendnis des Themas
    - **Hilfen und Anweisungen**: Ab Runde 1 kannst du mit einem Chatbot interagieren, der dir hilft, deine Map zu verbessern

    Diese Ressourcen findest du oben auf der Seite als Buttons. Der Chatbot ist unter der Concept Map positioniert.
    Deine Aufgabe: Erstelle und verfeinere eine Concept Map, die dein Verstaendnis des beschriebenen Problems widerspiegelt – mit Hilfe des Chatbots.
    """)

    # Add time information
    st.warning("""
    ⏱️ **Erwartete Dauer:**
    - Gesamtdauer: **ca. 30 Minuten**
    - 5 Runden Concept Mapping: **ca. 5 Minuten pro Runde**
    - Zusaetzliche Zeit fuer Frageboegen und Profil
    - Deine Zeit wird zu Forschungszwecken erfasst

    ⚠️ **Wichtig:** Bitte alle Schritte der Reihe nach abschliessen. Daten werden nur erfasst, wenn alle Pflichtangaben gemacht wurden.
    Deine sorgfaeltige Teilnahme sichert gueltige Forschungsdaten. Die besten 10 Prozent der Teilnehmenden erhalten einen Bonus.
    """)

    st.markdown("**Bereit, das Experiment zu starten?**")

    # Center the experimental mode button
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.subheader("🔬 Experimentelle Sitzung")
        st.markdown("""
        Diese Studie umfasst:
        - **KI-gestuetztes, personalisiertes Lernen**
        - **Fragebogen zur Lernendenprofilierung**
        - **5 Runden Concept Mapping**
        - **Datenerhebung fuer Forschungszwecke**
        """)

        if st.button("Experiment starten", type="primary", use_container_width=True):
            st.session_state.mode = "experimental"
            st.session_state.experimental_session = StreamlitExperimentalSession()

            # Initialize system
            if st.session_state.experimental_session.initialize_system("experimental"):
                st.session_state.session_initialized = True
                st.success("✅ Experiment initialisiert!")
                st.rerun()
            else:
                st.error("❌ Experiment konnte nicht initialisiert werden. Bitte Konfiguration pruefen.")


def render_consent_form():
    """Render research consent form."""
    st.header("📋 Einverstaendniserklaerung zur Studie")
    st.markdown("---")

    # Consent form content
    with st.container(border=True):
        st.markdown("""
        ### Einverstaendniserklaerung zur Studienteilnahme

        Du wirst eingeladen, an der Studie **"Agentic AI for Higher Education"** teilzunehmen.
        Die Studie wird von **Diana Kozachek** an der **Universitaet St. Gallen (Schweiz)** durchgefuehrt.

        **Zweck der Studie:**
        Wir untersuchen, wie KI-gestuetzte Agenten beim Lernen durch Concept Mapping unterstuetzen koennen.
        Wenn du zustimmst, bearbeitest du ein Online-Concept-Mapping mit KI-Unterstuetzung und anschliessenden Frageboegen.
        Dauer: ca. **30 Minuten**.

        **Nutzen:**
        Neben der Verguetung hilfst du, Lerntechnologien und KI-Lernhilfen zu verbessern.
        Die besten 10 Prozent der Teilnehmenden erhalten einen Bonus nach Auswertung.

        **Risiken & Vertraulichkeit:**
        Es sind keine besonderen Risiken bekannt; ein Restrisiko fuer Vertraulichkeit besteht immer online.
        Wir minimieren Risiken durch:
        - Sichere Speicherung mit Teilnehmer-IDs statt Klarnamen
        - Anonymisierte Veroeffentlichung
        - Loeschung der Daten nach Abschluss der Forschung

        **Freiwilligkeit:**
        Deine Teilnahme ist freiwillig, du kannst jederzeit abbrechen.

        **Kontakt:**
        Bei Fragen wende dich an **Diana Kozachek**, Universitaet St. Gallen.
        Bei Fragen zu Rechten als Proband: Ethikkommission der Universitaet St. Gallen.

        **Zustimmung:**
        Mit Klick auf „Ich stimme zu“ bestaetigst du, dass du mindestens 18 Jahre alt bist, die Informationen gelesen und verstanden hast und einverstanden bist teilzunehmen. Bewahre gern eine Kopie dieser Seite auf.
        """)

    st.markdown("---")

    # Consent buttons
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if st.button("❌ Nein, ich stimme nicht zu", type="secondary", use_container_width=True):
            st.session_state.consent_declined = True
            st.rerun()

    with col3:
        if st.button("✅ Ja, ich stimme zu", type="primary", use_container_width=True):
            st.session_state.consent_given = True

            # Log consent
            if st.session_state.experimental_session and st.session_state.experimental_session.session_logger:
                st.session_state.experimental_session.session_logger.log_event(
                    event_type="consent_given",
                    metadata={
                        "timestamp": datetime.now().isoformat(),
                        "consent": True
                    }
                )

            st.rerun()

    # Show message if consent was declined
    if st.session_state.consent_declined:
        st.error("""
        ### Vielen Dank fuer dein Interesse

        Du hast entschieden, nicht teilzunehmen. Das respektieren wir. Wenn du es dir anders ueberlegst, kannst du die Seite neu laden und neu starten.

        Danke, dass du eine Teilnahme in Betracht gezogen hast.
        """)
        st.stop()


def render_attention_check_failure():
    """Render attention check failure page."""
    st.header("❌ Aufmerksamkeitscheck nicht bestanden")
    st.markdown("---")

    st.error("""
    ### Danke fuer dein Interesse

    Du hast den Aufmerksamkeitscheck nicht bestanden und kannst an dieser Studie leider nicht teilnehmen.

    Wir brauchen, dass alle Fragen sorgfaeltig gelesen und beantwortet werden, um die Datenqualitaet sicherzustellen.

    Danke fuer deine Zeit und dein Interesse.
    """)
    st.stop()


def render_profile_login():
    with st.columns([1, 10, 1])[1]:
        st.header("Willkommen zum Experiment")
        st.write("Um an dieser Studie teilzunehmen, fuelle bitte den Profilfragebogen aus.")
        st.info("Deine Antworten helfen uns dabei, die Anpassung an deine Lernbeduerfnisse zu personalisieren.")

        if st.button("Profil einrichten", type='primary', use_container_width=True):
            st.session_state.profile_initialisation_started = True
            st.rerun()


def render_learner_profile():
    """Render learner profile creation page."""
    profile = st.session_state.experimental_session.create_learner_profile_form()

    if profile:
        st.session_state.learner_profile = profile
        st.session_state.profile_initialized = True

        # Initialize agent sequence
        st.session_state.agent_sequence = st.session_state.experimental_session.initialize_agent_sequence()

        st.info("📋 **Ablauf des Experiments:**")
        st.write("**Runde 0:** Erste Concept Map (ohne Agent) – Baseline")
        st.write("**Runden 1-4:** Agentengefuhrte Mapping-Runden")
        st.write("")
        st.write("Du erhaeltst in 4 Runden Hinweise von KI-Agenten, um deine Concept Map zu verbessern.")

        st.markdown("---")
        st.info("📝 Als naechstes folgt ein Fragebogen zu deinen Vorkenntnissen zu den Aufgabenmaterialien.")

        if st.button("Weiter zum Vorkenntnis-Fragebogen", type="primary"):
            st.rerun()


def render_tutorial():
    """Render interactive concept mapping tutorial."""
    st.header("📚 Concept-Mapping-Tutorial")
    st.markdown("---")

    st.markdown("""
    Willkommen! Bevor wir starten, schauen wir uns an, wie man Concept Maps effektiv erstellt.

    **Was ist eine Concept Map?**
    Eine Concept Map ist eine visuelle Darstellung von Wissen, die Beziehungen zwischen Konzepten ueber Knoten (Konzepte) und Kanten (Beziehungen) zeigt. Die Map ist responsiv, du kannst hinein- und herauszoomen, um sie an deinen Bildschirm anzupassen.
    """)

    tutorial_steps = [
        {
            "title": "Schritt 1: Knoten (Konzepte) erstellen",
            "content": """
            **So erstellst du einen Knoten:**
            - Klicke irgendwo auf die Map mit der **linken Maustaste** 🖱️
            - Gib den Konzeptnamen ein
            - Bestaetige mit **Enter** oder **OK**

            **Probiere es aus:** Erstelle unten einen Knoten mit der Beschriftung „Learning“.
            """,
            "demo_map": {
                "elements": [
                    {"data": {"id": "example1", "label": "Example Concept", "x": 200, "y": 100}}
                ]
            }
        },
        {
            "title": "Schritt 2: Kanten (Beziehungen) erstellen",
            "content": """
            **So erstellst du eine Kante:**
            - Klicke auf einen Knoten und **halte** fuer **1 Sekunde** 🖱️ (Quellknoten wird rot 🔴)
            - Klicke auf einen anderen Knoten, um zu verbinden
            - Beschrifte die Beziehung (z. B. „fuehrt zu“, „verursacht“, „enthaelt“)
            - Bestaetige mit **Enter** oder **OK**

            **Probiere es aus:** Verbinde zwei Konzepte mit einer sinnvollen Beziehung.
            """,
            "demo_map": {
                "elements": [
                    {"data": {"id": "a", "label": "Learning", "x": 150, "y": 100}},
                    {"data": {"id": "b", "label": "Understanding", "x": 350, "y": 100}},
                    {"data": {"source": "a", "target": "b", "label": "leads to"}}
                ]
            }
        },
        {
            "title": "Schritt 3: Bearbeiten und Loeschen",
            "content": """
            **Bearbeiten:**
            - **Doppelklick** auf einen Knoten oder eine Kante, um die Beschriftung zu aendern

            **Loeschen:**
            - **Rechtsklick** auf einen Knoten oder eine Kante, um ihn zu loeschen

            **Verschieben:**
            - **Ziehen**, um Knoten zu verschieben
            - **Shift** halten, um mehrere Knoten zu markieren

            **Probiere es aus:** Uebe das Bearbeiten und Verschieben in der Map unten.
            """,
            "demo_map": {
                "elements": [
                    {"data": {"id": "concept1", "label": "Practice", "x": 200, "y": 80}},
                    {"data": {"id": "concept2", "label": "Mastery", "x": 200, "y": 180}},
                    {"data": {"source": "concept1", "target": "concept2", "label": "leads to"}}
                ]
            }
        }
    ]

    # Tutorial navigation
    if "tutorial_step" not in st.session_state:
        st.session_state.tutorial_step = 0

    current_step = tutorial_steps[st.session_state.tutorial_step]

    # Progress indicator
    progress = (st.session_state.tutorial_step + 1) / len(tutorial_steps)
    st.progress(progress, text=f"Schritt {st.session_state.tutorial_step + 1} von {len(tutorial_steps)}")

    # Current step content
    st.subheader(current_step["title"])
    st.markdown(current_step["content"])

    # Practice area
    st.markdown("**Uebungsbereich:**")
    try:
        tutorial_response = conceptmap_component(
            cm_data=current_step["demo_map"]
        )
    except Exception as e:
        st.error(f"Tutorial map error: {e}")
        tutorial_response = None

    # Navigation buttons
    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        if st.session_state.tutorial_step > 0:
            if st.button("← Zurueck", type="secondary"):
                st.session_state.tutorial_step -= 1
                st.rerun()

    with col3:
        if st.session_state.tutorial_step < len(tutorial_steps) - 1:
            if st.button("Weiter →", type="primary"):
                st.session_state.tutorial_step += 1
                st.rerun()
        else:
            if st.button("Tutorial abschliessen", type="primary"):
                st.session_state.tutorial_completed = True
                st.session_state.show_tutorial = False
                st.success("🎉 Tutorial abgeschlossen! Du kannst mit dem Experiment starten.")
                st.session_state.scroll_to_top = True
                st.rerun()

    # Skip option
    st.markdown("---")
    if st.button("Tutorial ueberspringen", type="secondary"):
        st.session_state.tutorial_completed = True
        st.session_state.show_tutorial = False
        st.session_state.scroll_to_top = True
        st.rerun()


def render_agent_differentiation_question():
    """Render agent differentiation question before questionnaires."""
    st.header("🤖 Agenten-Differenzierung")
    st.markdown("---")

    st.info("""
    Bevor es mit den letzten Frageboegen weitergeht, wollen wir wissen, wie du die Agenten erlebt hast.
    """)

    with st.form("agent_differentiation"):
        st.markdown("**Konntest du die unterschiedlichen Agenten voneinander unterscheiden?**")

        differentiation = st.radio(
            "Waehle deine Antwort:",
            options=[
                "Ja, die Unterschiede waren klar",
                "Teils-teils – ich habe Unterschiede gemerkt, war mir aber unsicher",
                "Nein, alle Agenten wirkten gleich",
                "Ich weiss es nicht"
            ],
            index=None  # No default selection
        )

        # Optional text field for additional comments
        st.markdown("**Weitere Kommentare (optional):**")
        comments = st.text_area(
            "Wenn dir Unterschiede aufgefallen sind: Was genau? Falls nicht: Warum wirkten sie gleich?",
            height=100,
            placeholder="Deine Beobachtungen zu den Agenten..."
        )

        submitted = st.form_submit_button("Abschicken", type="primary")

        if submitted:
            if not differentiation:
                st.error("Bitte waehle eine Antwort aus, bevor du abschickst.")
                return

            # Store the response in session data
            if st.session_state.experimental_session:
                differentiation_data = {
                    "differentiation_response": differentiation,
                    "comments": comments,
                    "timestamp": datetime.now().isoformat(),
                    "participant_id": st.session_state.learner_profile.get('unique_id',
                                                                           'N/A') if st.session_state.learner_profile else 'N/A',
                    "participant_name": st.session_state.learner_profile.get('name',
                                                                             'Unknown') if st.session_state.learner_profile else 'Unknown'
                }

                # Add to session data
                st.session_state.experimental_session.session_data["agent_differentiation"] = differentiation_data

                # Log the response
                if st.session_state.experimental_session.session_logger:
                    st.session_state.experimental_session.session_logger.log_event(
                        event_type="agent_differentiation_response",
                        metadata=differentiation_data
                    )

            # Mark as completed
            st.session_state.agent_differentiation_completed = True

            st.success("✅ Danke fuer dein Feedback!")
            st.info("📊 Weiter geht es mit der Frage zur Map-Anpassung...")
            st.rerun()


def render_map_adaption_question():
    """Render self-assessment of concept map adaptation between rounds."""
    st.header("🗺️ Anpassung deiner Concept Map")
    st.markdown("---")

    st.info("""Wir moechten wissen, wie stark du deine Concept Map zwischen den Runden geaendert hast.""")

    with st.form("map_adaptation"):
        adaptation = st.radio(
            "Hast du deine Concept Map zwischen den Runden angepasst?",
            options=[
                "Ja, ich habe die Map aktiv veraendert oder erweitert",
                "Ein wenig – ein paar Anpassungen, sonst gleich geblieben",
                "Nein, ich habe kaum etwas geaendert",
                "Ich bin mir nicht sicher"
            ],
            index=None  # No default selection
        )

        comments = st.text_area(
            "Weitere Kommentare (optional):",
            height=100,
            placeholder="Welche Aenderungen (falls welche) hast du vorgenommen?"
        )

        submitted = st.form_submit_button("Abschicken", type="primary")

        if submitted:
            if not adaptation:
                st.error("Bitte waehle eine Antwort aus, bevor du abschickst.")
                return

            # Store response
            if st.session_state.experimental_session:
                adaptation_data = {
                    "adaptation_response": adaptation,
                    "comments": comments,
                    "timestamp": datetime.now().isoformat(),
                    "participant_id": st.session_state.learner_profile.get('unique_id',
                                                                           'N/A') if st.session_state.learner_profile else 'N/A',
                    "participant_name": st.session_state.learner_profile.get('name',
                                                                             'Unknown') if st.session_state.learner_profile else 'Unknown'
                }

                st.session_state.experimental_session.session_data["map_adaptation"] = adaptation_data

                if st.session_state.experimental_session.session_logger:
                    st.session_state.experimental_session.session_logger.log_event(
                        event_type="map_adaptation_response",
                        metadata=adaptation_data
                    )
            # Mark as completed and proceed
            st.session_state.map_adaptation_completed = True

            st.success("✅ Danke fuer dein Feedback!")
            st.info("📋 Weiter geht es mit dem Fragebogen zu deinem Lernerfolg...")
            st.rerun()


def render_summary_page():
    """Render session summary page."""
    st.header("Concept-Mapping-Experiment")
    st.markdown("---")
    st.write("Danke, dass du am Concept-Mapping-Experiment teilgenommen hast!")
    st.balloons()

    # Calculate map summary statistics
    final_nodes = 0
    final_edges = 0

    if st.session_state.experimental_session:
        final_map = st.session_state.experimental_session.session_data.get("current_concept_map", {})
        final_nodes = len(final_map.get("concepts", []))
        final_edges = len(final_map.get("relationships", []))

        # Log map summary for easy identification
        if st.session_state.experimental_session.session_logger:
            st.session_state.experimental_session.session_logger.log_event(
                event_type="map_summary",
                metadata={
                    "final_nodes": final_nodes,
                    "final_edges": final_edges,
                    "participant_id": st.session_state.learner_profile.get('unique_id',
                                                                           'N/A') if st.session_state.learner_profile else 'N/A',
                    "participant_name": st.session_state.learner_profile.get('name',
                                                                             'Unknown') if st.session_state.learner_profile else 'Unknown'
                }
            )

    # Finalize session if not already done
    if not st.session_state.session_finalized and st.session_state.experimental_session:
        with st.spinner("Sitzung wird abgeschlossen und Daten werden gespeichert..."):
            export_info = st.session_state.experimental_session.finalize_session()
            st.session_state.session_finalized = True

            if "error" not in export_info:
                st.success("✅ Sitzungsdaten erfolgreich gespeichert!")

    st.subheader("Sitzungsuebersicht")

    # Get session summary
    if st.session_state.experimental_session:
        summary = st.session_state.experimental_session.get_session_summary()

        # Get unique ID from learner profile
        unique_id = st.session_state.learner_profile.get('unique_id',
                                                         'N/A') if st.session_state.learner_profile else 'N/A'

        col1, col2 = st.columns(2)

        with col1:
            st.write(f"**Teilnehmername:** {summary.get('participant_name', 'Demo-Nutzer')}")
            st.write(f"**Prolific Experiment ID:** {unique_id}")
            st.write(f"**Modus:** {summary.get('mode', 'unknown').title()}")

        with col2:
            st.write(f"**Anzahl abgeschlossene Runden:** {st.session_state.max_rounds}")
            if st.session_state.mode == "experimental":
                st.write("**Ablauf:**")
                st.write("- Runde 0: Baseline (eigene Map)")
                st.write("- Runden 1-4: Agentengeleitete Map")

    # Display concept map statistics
    st.markdown("---")
    st.subheader("📊 Concept-Map-Statistiken")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(label="Erstellte Knoten gesamt", value=final_nodes)

    with col2:
        st.metric(label="Erstellte Kanten gesamt", value=final_edges)

    with col3:
        if final_nodes > 0:
            connectivity = round(final_edges / final_nodes, 2)
            st.metric(label="Verhaeltnis Kanten/Knoten", value=connectivity)
        else:
            st.metric(label="Verhaeltnis Kanten/Knoten", value="k.A.")

    # Thank you message
    st.markdown("---")
    st.info("""
    📊 Deine Antworten wurden fuer die Forschung gespeichert.

    Danke fuer deinen wertvollen Beitrag zu unserer Forschung ueber KI-gestuetztes Lernen!
    """)

    # Leading back to Prolific
#    st.markdown("---")
#    st.link_button("Bitte kehre zu Prolific zurueck", "https://app.prolific.com/submissions/complete?cc=C1EF9RLL", type="primary")


def render_agent_name():
    """Render agent name for current round."""
    roundn = st.session_state.roundn

    # In experimental mode, hide specific agent types from participants
    if st.session_state.mode == "experimental":
        if roundn == 0:
            agent_name = "Initiale Map-Erstellung"
        else:
            agent_name = "Agent"  # Generischer Name fuer alle Scaffolding-Agenten
    else:
        # In demo mode, show the actual agent type
        if st.session_state.experimental_session:
            agent_name = st.session_state.experimental_session.get_agent_name(roundn)
        else:
            agent_name = "Demo-Agent"

    st.markdown(f'<div style="font-size:20px;">🧙<b> {agent_name} Nachfrage:</b></div>', unsafe_allow_html=True)


def render_header():
    """Render page header."""
    st.header("Concept-Mapping-Experiment")
    st.markdown("---")

    # Add resource buttons in the header
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

    with col1:
        # Display Round 0 as "Baseline" and others as Round 1-4
        if st.session_state.roundn == 0:
            st.subheader(f"Runde 0 (Baseline) / {st.session_state.max_rounds - 1}")

        else:
            st.subheader(f"Runde {st.session_state.roundn}/{st.session_state.max_rounds - 1}")

    with col2:
        if st.button("📋 Aufgabenbeschreibung", type="secondary", use_container_width=True):
            render_task_dialog()

    with col3:
        if st.button("📚 Zusatzmaterialien", type="secondary", use_container_width=True):
            render_materials_dialog()

    with col4:
        if st.button("❓ Hilfe", type="secondary", use_container_width=True):
            render_help_dialog()

    # Show mode and participant info
    if st.session_state.mode:
        col1, col2 = st.columns([3, 1])
        with col1:
            if st.session_state.learner_profile:
                st.caption(f"Teilnehmer: {st.session_state.learner_profile['name']}")
        with col2:
            st.caption(f"Modus: {st.session_state.mode.title()}")


@st.dialog("Aufgabenbeschreibung", width='large')
def render_task_dialog():
    """Render task description dialog with copy protection."""
    st.markdown("📋 Aufgabenbeschreibung")
    st.caption("Dieser Inhalt ist geschuetzt und kann nicht kopiert werden.")

    # Render task description as protected image with larger font
    render_protected_markdown(TASK_DESCRIPTION, width=1100, font_size=20)


@st.dialog("Zusatzmaterialien", width='large')
def render_materials_dialog():
    """Render extra materials dialog with copy protection."""
    st.markdown("📚 Zusatzmaterialien")
    st.caption("Dieser Inhalt ist geschuetzt und kann nicht kopiert werden.")

    # Render extra materials as protected image with larger font
    render_protected_markdown(EXTRA_MATERIALS, width=1100, font_size=20)


@st.dialog("Anleitung Concept-Map-Editor", width='large')
def render_help_dialog():
    """Render help dialog for concept map editor."""
    st.subheader("Knoten bearbeiten 🔵")
    st.markdown("""
                - **Linksklick** 🖱️ irgendwo auf die Map, um einen neuen Knoten zu erstellen.
                    - Beschriftung eingeben und mit **Enter** oder **OK** bestaetigen.
                    - Mit **Escape** oder Ziehen der Map abbrechen.
                - Halte die **linke Maustaste** 🖱️ auf einem Knoten, um ihn zu bewegen.
                    - Mit **Shift** kannst du mehrere Knoten markieren (gruen hervorgehoben) und gemeinsam verschieben.
                - **Doppelklick** auf einen Knoten, um die Beschriftung zu bearbeiten.
                - **Rechtsklick** auf einen Knoten, um ihn zu loeschen.
                """)
    st.markdown("---")
    st.subheader("Kanten bearbeiten ↗️")
    st.markdown("""
                - **Linksklick halten** 🖱️ auf einem Knoten fuer eine Sekunde, um eine Kante zu starten (Quellknoten wird rot 🔴).
                    - Dann **Linksklick** auf den Zielknoten.
                    - Beschriftung eingeben und mit **Enter** oder **OK** bestaetigen.
                    - Mit **Escape** oder Ziehen der Map abbrechen.
                - **Doppelklick** auf eine Kante, um die Beschriftung zu bearbeiten.
                - **Rechtsklick** auf eine Kante, um sie zu loeschen.
                """)


def render_concept_map():
    """Render concept map editor."""
    roundn = st.session_state.roundn
    contents = st.session_state.contents
    cm_label = contents["labels"]["extend" if roundn else "initial"]["header"]

    _, middle, right = st.columns([1, 20, 1])
    with right:
        if st.button(label='❓', type='secondary'):
            render_help_dialog()
    with middle:
        st.write(cm_label)

        # example map
        if roundn == 0:
            st.markdown(
                "Bitte lies die Aufgabenbeschreibung und die Zusatzmaterialien sorgfaeltig. Fuege in dieser Runde mindestens 3 und bis zu 5 deiner wichtigsten Konzepte und deren Verbindungen hinzu. Unten ein Beispiel, wie eine Baseline-Concept-Map vor der Unterstuetzung aussehen koennte.")

            img_path = os.path.join(os.path.dirname(__file__), "..", "examples", "data", "examplemap.png")
            if os.path.exists(img_path):
                st.image(img_path, use_container_width=True)
            else:
                st.warning(f"⚠️ Example image not found at {img_path}")

        # Create a container for the concept map
        try:
            # Ensure we have valid concept map data
            if roundn < len(st.session_state.cmdata) and isinstance(st.session_state.cmdata[roundn], dict):
                cm_data = st.session_state.cmdata[roundn]
            else:
                # Use initial map if we don't have data for this round
                cm_data = st.session_state.contents["initial_map"]

            # Debug: Check data type before passing to component
            if not isinstance(cm_data, dict):
                st.error(f"Invalid concept map data type: {type(cm_data)}")
                cm_data = st.session_state.contents["initial_map"]

            response = conceptmap_component(
                cm_data=cm_data,
                submit_request=st.session_state.submit_request
            )
        except Exception as e:
            st.error(f"Error rendering concept map: {e}")
            response = None

    return response


def render_cm_submit_button():
    """Render concept map submit button."""
    st.markdown("---")  # Add a separator

    if st.session_state.followup:
        st.success("Danke!")
        return

    # Make the submit button more prominent
    st.markdown("### Concept Map einreichen")

    _, col2, _ = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Concept Map abschicken", type='primary', use_container_width=True,
                     disabled=st.session_state.submit_request):
            st.session_state.submit_request = True
            st.rerun()


def render_followup():
    """Render agent followup interaction with multi-turn conversation support."""
    roundn = st.session_state.roundn

    # Spezielle Behandlung fuer Runde 0 - direkt zu Runde 1 springen
    if roundn == 0:
        st.success("✅ Erste Concept Map erfolgreich eingereicht!")
        st.info("Das war deine Baseline-Concept-Map (Runde 0). Jetzt geht es mit agentengefuertem Scaffolding weiter.")

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("Weiter zu Runde 1", type="primary", use_container_width=True):
                # Log the round 0 completion
                if st.session_state.experimental_session:
                    current_cm_data = st.session_state.cmdata[0] if len(st.session_state.cmdata) > 0 else None
                # Log the round 0 completion with experimental session
                if st.session_state.experimental_session:
                    current_cm_data = st.session_state.cmdata[0] if len(st.session_state.cmdata) > 0 else None
                    st.session_state.experimental_session.update_concept_map_evolution(0, current_cm_data)
                    st.session_state.experimental_session.add_to_conversation_history(
                        0, "system", "Runde 0 abgeschlossen - Baseline-Concept-Map erstellt", {"final": True}
                    )

                # Move to round 1
                st.session_state.followup = False
                st.session_state.roundn = 1
                st.session_state.agent_msg = None
                st.session_state.scroll_to_top = True
                st.rerun()
        return

    # Initialize conversation state for this round
    round_key = f"round_{roundn}_conversation"
    if round_key not in st.session_state:
        st.session_state[round_key] = []

    conversation_history = st.session_state[round_key]

    # Initialize conversation turn counter
    conversation_turn_key = f"round_{roundn}_turn"
    if conversation_turn_key not in st.session_state:
        st.session_state[conversation_turn_key] = 0

    conversation_turn = st.session_state[conversation_turn_key]

    with st.container(border=True):
        render_agent_name()

        # Show conversation history
        if conversation_history:
            st.markdown("**Verlauf:**")
            for i, exchange in enumerate(conversation_history):
                with st.expander(f"Austausch {i + 1}", expanded=(i == len(conversation_history) - 1)):
                    st.markdown(f"**🧙 Agent:** {exchange['agent_message']}")
                    st.markdown(f"**👤 Du:** {exchange['user_response']}")

        # Current agent response
        with st.container(border=True):
            current_cm_data = st.session_state.cmdata[roundn] if roundn < len(st.session_state.cmdata) else None

            # Get previous user response for context
            previous_user_response = None
            if conversation_history:
                previous_user_response = conversation_history[-1]['user_response']

            # Get agent response
            if st.session_state.experimental_session:
                if not st.session_state.agent_msg:
                    st.session_state.agent_msg = st.session_state.experimental_session.get_agent_response(
                        roundn,
                        concept_map_data=current_cm_data,
                        user_response=previous_user_response,
                        conversation_turn=conversation_turn
                    )

                    # Add to conversation history in session
                    st.session_state.experimental_session.add_to_conversation_history(
                        roundn, "agent", st.session_state.agent_msg, {"conversation_turn": conversation_turn}
                    )
            else:
                # Demo mode with conversation awareness
                if conversation_turn == 0:
                    st.session_state.agent_msg = "Dies ist eine Demo-Antwort. Im Experiment erhaeltst du eine personalisierte KI-Antwort."
                else:
                    st.session_state.agent_msg = f"Danke fuer deine Antwort. Dies ist Demo-Nachfrage #{conversation_turn}. Im Experiment waere dies eine kontextuelle Antwort basierend auf deinem Input."

            st.markdown(f"**Aktuelle Antwort:**")
            st.write(st.session_state.agent_msg)

        # User response area - use unique key based on turn
        current_response_key = f'followup_response_r{roundn}_t{conversation_turn}'
        st.text_area(
            label='Deine Antwort',
            placeholder="Antworte hier auf die Ausgabe oben",
            height=100,
            key=current_response_key
        )

        # Action buttons
        col1, col2, col3 = st.columns([1, 1, 1])

        user_response = st.session_state.get(current_response_key, '')

        with col1:
            # Continue conversation button
            max_user_messages = 5
            can_continue = (st.session_state.experimental_session and
                            st.session_state.experimental_session.can_continue_conversation(roundn))

            if (len(user_response) > 0 and can_continue and
                    st.button("Gespräch fortsetzen", type='secondary', use_container_width=True,
                              key=f"continue_r{roundn}_t{conversation_turn}")):

                # Add current exchange to history
                conversation_history.append({
                    'agent_message': st.session_state.agent_msg,
                    'user_response': user_response,
                    'turn': conversation_turn
                })

                # Log user response
                if st.session_state.experimental_session:
                    st.session_state.experimental_session.log_user_response(
                        roundn, user_response, current_cm_data
                    )
                    st.session_state.experimental_session.add_to_conversation_history(
                        roundn, "user", user_response, {"conversation_turn": conversation_turn}
                    )

                # Increment turn counter for next iteration
                st.session_state[conversation_turn_key] += 1
                st.session_state.agent_msg = None
                st.rerun()

        with col2:
            # Finish round button
            if (len(user_response) > 0 and
                    st.button("Runde beenden", type='primary', use_container_width=True,
                              key=f"finish_r{roundn}_t{conversation_turn}")):

                # Add final exchange to history
                conversation_history.append({
                    'agent_message': st.session_state.agent_msg,
                    'user_response': user_response,
                    'turn': conversation_turn
                })

                # Log final user response
                if st.session_state.experimental_session:
                    st.session_state.experimental_session.log_user_response(
                        roundn, user_response, current_cm_data
                    )
                    st.session_state.experimental_session.add_to_conversation_history(
                        roundn, "user", user_response, {"conversation_turn": conversation_turn, "final": True}
                    )

                # Update concept map evolution
                if st.session_state.experimental_session and current_cm_data:
                    st.session_state.experimental_session.update_concept_map_evolution(
                        roundn, current_cm_data
                    )

                # Reset conversation state for next round
                st.session_state[conversation_turn_key] = 0

                # Move to next round
                st.session_state.followup = False
                st.session_state.roundn += 1
                st.session_state.agent_msg = None
                st.session_state.scroll_to_top = True
                st.rerun()

        with col3:
            # Show conversation limits
            if st.session_state.experimental_session:
                remaining_turns = max_user_messages - conversation_turn
                if remaining_turns > 0:
                    st.caption(f"Verbleibende Antworten: {remaining_turns}")
                else:
                    st.caption("Maximale Antworten erreicht")

        # Show instructions
        if conversation_turn == 0:
            st.info(
                "💡 **Tipp:** Du kannst bis zu 5 Austausche mit dem Agenten in dieser Runde fuehren. Nutze 'Gespraech fortsetzen' fuer weitere Fragen oder 'Runde beenden', wenn du fertig bist.")
        elif conversation_turn >= max_user_messages - 1:
            st.warning("⚠️ Dies ist dein letzter Austausch in dieser Runde. Klicke auf 'Runde beenden', um weiterzugehen.")


def capture_concept_map_data(roundn: int, concept_map_response: Dict) -> None:
    """Capture concept map data for experimental analysis with comprehensive logging."""

    # 1. Store in session state for UI persistence
    ensure_cm_slot(roundn)
    st.session_state.cmdata[roundn] = concept_map_response

    # 2. Log to experimental session for research data
    if st.session_state.experimental_session:
        st.session_state.experimental_session.update_concept_map_evolution(
            roundn, concept_map_response
        )

    # 3. Log detailed interaction data for research analysis
    if st.session_state.experimental_session and st.session_state.experimental_session.session_logger:
        # Extract element counts for research metrics
        elements = concept_map_response.get("elements", [])
        if isinstance(elements, dict):
            dict_elements = []
            dict_elements.extend(elements.get("nodes", []))
            dict_elements.extend(elements.get("edges", []))
        else:
            dict_elements = [e for e in elements if isinstance(e, dict)]

        nodes = [e for e in dict_elements if "source" not in e.get("data", {})]
        edges = [e for e in dict_elements if "source" in e.get("data", {})]

        st.session_state.experimental_session.session_logger.log_event(
            event_type="concept_map_captured",
            metadata={
                "round_number": roundn,
                "nodes_count": len(nodes),
                "edges_count": len(edges),
                "total_elements": len(dict_elements),
                "participant_id": st.session_state.learner_profile.get(
                    "unique_id") if st.session_state.learner_profile else "unknown",
                "agent_type": get_current_agent_type(roundn),
                "capture_timestamp": datetime.now().isoformat(),
                "experimental_data": {
                    "concept_map_data": concept_map_response,
                    "session_id": st.session_state.experimental_session.session_data["session_id"]
                }
            }
        )


def get_current_agent_type(roundn: int) -> Optional[str]:
    """Get the current agent type for the given round."""
    if roundn == 0:
        return None  # Round 0 has no agent

    agent_index = roundn - 1
    if (st.session_state.experimental_session and
            agent_index < len(st.session_state.experimental_session.session_data.get("agent_sequence", []))):
        return st.session_state.experimental_session.session_data["agent_sequence"][agent_index]

    return None


def ensure_round_transition_data_integrity(from_round: int, to_round: int):
    """Ensure data integrity during round transitions for experimental analysis."""

    # 1. Capture final state of current round
    if from_round < len(st.session_state.cmdata):
        current_map_data = st.session_state.cmdata[from_round]
    else:
        current_map_data = st.session_state.contents["initial_map"]

    # 2. Log round transition for research analysis
    if st.session_state.experimental_session and st.session_state.experimental_session.session_logger:
        st.session_state.experimental_session.session_logger.log_event(
            event_type="round_transition",
            metadata={
                "from_round": from_round,
                "to_round": to_round,
                "final_map_data": current_map_data,
                "transition_timestamp": datetime.now().isoformat(),
                "participant_id": st.session_state.learner_profile.get(
                    "unique_id") if st.session_state.learner_profile else "unknown",
                "experimental_session_id": st.session_state.experimental_session.session_data["session_id"]
            }
        )

    # 3. Initialize next round with proper baseline for experimental continuity
    if to_round == 1:  # Special handling for Round 0 → Round 1 (baseline → scaffolding)
        # Copy baseline map as starting point for scaffolding rounds
        ensure_cm_slot(to_round)
        st.session_state.cmdata[to_round] = copy.deepcopy(current_map_data)

        # Log baseline preservation for research analysis
        if st.session_state.experimental_session and st.session_state.experimental_session.session_logger:
            st.session_state.experimental_session.session_logger.log_event(
                event_type="baseline_map_preserved",
                metadata={
                    "baseline_round": from_round,
                    "scaffolding_round": to_round,
                    "baseline_data": current_map_data,
                    "preservation_timestamp": datetime.now().isoformat()
                }
            )


def handle_response(response):
    """Handle concept map response with cumulative logic and enhanced debugging."""
    # Always log what we receive, even if None
    logger.debug("🔍 HANDLE_RESPONSE DEBUG:")
    logger.debug(f"   Response received: {response is not None}")
    logger.debug(f"   Response type: {type(response).__name__}")
    logger.debug(f"   Followup state: {st.session_state.followup}")
    logger.debug(f"   Submit request: {st.session_state.submit_request}")

    if response is not None:
        logger.debug(f"   Response content: {str(response)[:300]}")
        if isinstance(response, dict):
            logger.debug(f"   Has elements: {'elements' in response}")
            if "elements" in response:
                logger.debug(f"   Elements count: {len(response['elements'])}")

    # --- Real-time logging of node and edge creations ---
    if response and isinstance(response, dict) and "elements" in response:
        elements = response["elements"]
        if isinstance(elements, dict):
            dict_elements = []
            dict_elements.extend(elements.get("nodes", []))
            dict_elements.extend(elements.get("edges", []))
        else:
            dict_elements = [e for e in elements if isinstance(e, dict)]
        current_nodes = {
            e["data"]["id"] for e in dict_elements if "source" not in e.get("data", {})
        }
        current_edges = {
            e["data"]["id"] for e in dict_elements if "source" in e.get("data", {})
        }

        prev_nodes = st.session_state.get("_prev_cm_nodes")
        prev_edges = st.session_state.get("_prev_cm_edges")

        if prev_nodes is None or prev_edges is None:
            # Initialize tracking on first run without logging existing elements
            st.session_state._prev_cm_nodes = current_nodes
            st.session_state._prev_cm_edges = current_edges
        else:
            new_nodes = current_nodes - prev_nodes
            new_edges = current_edges - prev_edges

            # Prepare a parsed snapshot for logging if needed
            parsed_snapshot = parse_conceptmap(response)

            for node_id in new_nodes:
                node_data = next(
                    e["data"]
                    for e in dict_elements
                    if e.get("data", {}).get("id") == node_id
                )
                logger.info(
                    f"🆕 Node created: {node_data.get('label', '')} (id: {node_id}, x: {node_data.get('x')}, y: {node_data.get('y')})"
                )
                if (
                        st.session_state.experimental_session
                        and st.session_state.experimental_session.session_logger
                ):
                    st.session_state.experimental_session.session_logger.log_event(
                        event_type="concept_map_node_created",
                        metadata={
                            "node": node_data,
                            "nodes_count": len(parsed_snapshot.get("concepts", [])),
                            "edges_count": len(parsed_snapshot.get("relationships", [])),
                            "concept_map_snapshot": parsed_snapshot,
                        },
                    )

            for edge_id in new_edges:
                edge_data = next(
                    e["data"]
                    for e in dict_elements
                    if e.get("data", {}).get("id") == edge_id
                )
                logger.info(
                    f"🆕 Edge created: {edge_data.get('source')} -> {edge_data.get('target')} "
                    f"(label: {edge_data.get('label', '')}, id: {edge_id})"
                )
                if (
                        st.session_state.experimental_session
                        and st.session_state.experimental_session.session_logger
                ):
                    st.session_state.experimental_session.session_logger.log_event(
                        event_type="concept_map_edge_created",
                        metadata={
                            "edge": edge_data,
                            "nodes_count": len(parsed_snapshot.get("concepts", [])),
                            "edges_count": len(parsed_snapshot.get("relationships", [])),
                            "concept_map_snapshot": parsed_snapshot,
                        },
                    )

            # Update tracked state
            st.session_state._prev_cm_nodes = current_nodes
            st.session_state._prev_cm_edges = current_edges

    if st.session_state.submit_request and response and not st.session_state.followup:
        logger.info("   ✅ Processing response...")

        # Debug: Log what we received
        if st.session_state.experimental_session and st.session_state.experimental_session.session_logger:
            st.session_state.experimental_session.session_logger.log_event(
                event_type="handle_response_debug",
                metadata={
                    "response_type": type(response).__name__,
                    "response_preview": str(response)[:300] if response else "None",
                    "has_elements": "elements" in response if isinstance(response, dict) else False,
                    "has_action_history": "action_history" in response if isinstance(response, dict) else False
                }
            )

        # Update the current round's concept map instead of appending
        roundn = st.session_state.roundn

        # Ensure we have enough slots in cmdata
        while len(st.session_state.cmdata) <= roundn:
            # For rounds after 0, copy the previous round's data as starting point
            if len(st.session_state.cmdata) > 0:
                # Copy the previous round's concept map as the base for the new round
                previous_map = copy.deepcopy(st.session_state.cmdata[-1])
                st.session_state.cmdata.append(previous_map)
            else:
                # First round uses initial map
                st.session_state.cmdata.append(st.session_state.contents["initial_map"])

        # Update the current round's concept map with the new data
        st.session_state.cmdata[roundn] = response
        logger.info(f"   📝 Stored response in cmdata[{roundn}]")

        # Debug: Show what we're storing
        if isinstance(response, dict) and "elements" in response:
            dict_elements = [e for e in response["elements"] if isinstance(e, dict)]
            element_count = len(dict_elements)
            st.success(f"✅ Concept map data captured: {element_count} elements")

            # Show element breakdown
            nodes = [e for e in dict_elements if "source" not in e.get("data", {})]
            edges = [e for e in dict_elements if "source" in e.get("data", {})]
            st.write(f"**Elements breakdown:** {len(nodes)} nodes, {len(edges)} edges")

            # Show first few elements for verification
            if len(dict_elements) > 0:
                st.write("**Sample elements:**")
                for i, elem in enumerate(dict_elements[:3]):
                    st.write(f"  {i + 1}. {elem}")
        else:
            st.warning("⚠️ Response received but no elements found")

        # Log the concept map update for debugging
        if st.session_state.experimental_session:
            st.session_state.experimental_session.update_concept_map_evolution(roundn, response)

        st.session_state.submit_request = False
        st.session_state.followup = True
        st.rerun()
    elif st.session_state.submit_request:
        logger.warning("   ⚠️ Submit request but no response - resetting submit_request")
        st.session_state.submit_request = False
    else:
        logger.info(
            f"   ℹ️ No action taken (response: {response is not None}, submit_request: {st.session_state.submit_request}, followup: {st.session_state.followup})"
        )


def main():
    """Main application logic."""
    init_session_state()
    st.markdown('<a id="top"></a>', unsafe_allow_html=True)
    scroll_js = """
           <script>
               const topAnchor = parent.document.getElementById('top');
               if (topAnchor) {
                   topAnchor.scrollIntoView({behavior: 'smooth'});
               }
           </script>
           """

    # Mode selection
    if not st.session_state.mode:
        render_mode_selection()
        return

    # Consent form (experimental mode only, after mode selection)
    if (st.session_state.mode == "experimental" and
            st.session_state.session_initialized and
            not st.session_state.consent_given):
        render_consent_form()
        st.components.v1.html(scroll_js)
        return

    # Learner profile login page (experimental mode only, after consent)
    if (st.session_state.mode == "experimental" and
            st.session_state.session_initialized and
            st.session_state.consent_given and
            not st.session_state.profile_initialisation_started and
            not st.session_state.profile_initialized):
        render_profile_login()
        return

    # Learner profile creation (experimental mode only)
    if (st.session_state.mode == "experimental" and
            st.session_state.session_initialized and
            st.session_state.profile_initialisation_started and
            not st.session_state.profile_initialized):
        render_learner_profile()
        return

    # Pre-knowledge questionnaire (experimental mode only)
    if (st.session_state.mode == "experimental" and
            st.session_state.profile_initialized and
            not st.session_state.pre_questionnaire_completed):
        if st.session_state.experimental_session:
            st.session_state.experimental_session.render_pre_knowledge_questionnaire()
        st.components.v1.html(scroll_js)
        return

    # Attention check failure page (experimental mode only, after pre-questionnaire)
    if (st.session_state.mode == "experimental" and
            st.session_state.attention_check_failed):
        render_attention_check_failure()
        return

    # Tutorial flow (experimental mode only)
    if (st.session_state.mode == "experimental" and
            st.session_state.profile_initialized and
            st.session_state.pre_questionnaire_completed and
            st.session_state.show_tutorial):
        render_tutorial()
        st.components.v1.html(scroll_js)
        return

    # Check if tutorial is required but not completed (experimental mode)
    if (st.session_state.mode == "experimental" and
            st.session_state.profile_initialized and
            st.session_state.pre_questionnaire_completed and
            not st.session_state.tutorial_completed and
            not st.session_state.show_tutorial):
        st.session_state.show_tutorial = True
        st.rerun()

    # Main session logic
    roundn = st.session_state.roundn

    # Check if all rounds are completed and post-task questionnaires are needed
    if roundn == st.session_state.max_rounds:
        # Agent differentiation question (experimental mode only)
        if (st.session_state.mode == "experimental" and
                not st.session_state.get('agent_differentiation_completed', False)):
            render_agent_differentiation_question()
            return
        # Map adaptation question (after differentiation)
        if (st.session_state.mode == "experimental" and
                st.session_state.get('agent_differentiation_completed', False) and
                not st.session_state.get('map_adaptation_completed', False)):
            render_map_adaption_question()
            return

        # Post-knowledge questionnaire (experimental mode only, after map adaptation - measure learning gains immediately)
        if (st.session_state.mode == "experimental" and
             st.session_state.get('map_adaptation_completed', False) and
             not st.session_state.get('post_questionnaire_completed', False)):
             if st.session_state.experimental_session:
                 st.session_state.experimental_session.render_post_knowledge_questionnaire()
             st.components.v1.html(scroll_js)
             return

        # CLT questionnaire (experimental mode only, after post-knowledge questionnaire)
        if (st.session_state.mode == "experimental" and
                st.session_state.get('post_questionnaire_completed', False) and
                not st.session_state.get('clt_completed', False)):
            if st.session_state.experimental_session:
                st.session_state.experimental_session.render_clt_questionnaire()
            st.components.v1.html(scroll_js)
            return

        # Show summary page after all questionnaires are completed (or immediately in demo mode)
        render_summary_page()
    else:
        render_header()

        # Render concept map first
        response = render_concept_map()


        # Then render submit button
        render_cm_submit_button()

        handle_response(response)

        if st.session_state.followup:
            render_followup()

    if st.session_state.scroll_to_top:
        st.components.v1.html(scroll_js)
        st.session_state.scroll_to_top = False


if __name__ == "__main__":
    main()
