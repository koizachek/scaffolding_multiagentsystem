import json
import os
from logging import disable
from pandas._libs.tslibs.fields import round_nsint64
import streamlit as st
from conceptmap_component import conceptmap_component, parse_conceptmap
from application_session import ApplicationSession


# Session State Initialization
def init_session_state():
    defaults = {
        "session": ApplicationSession(),
        "submit_request": False,
        "followup": False,
        "roundn": 0,
        "contents": load_contents(),
        "cmdata": []
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
    
    if not st.session_state.cmdata:
        st.session_state.cmdata.append(defaults['contents']["initial_map"])
    
    if 'max_round' not in st.session_state:
        st.session_state.max_rounds = defaults['contents']["rounds"]


def load_contents():
    path = os.path.join(os.path.dirname(__file__), "contents.json")
    with open(path) as f:
        return json.load(f)


# UI Rendering
def render_summary_page():
    roundn = st.session_state.roundn
    
    st.header("Multiagent Scaffolding Experiment")
    st.markdown("---")
    st.write("Thank You for participating in the Multiagent Scaffolding Experiment!")
    st.balloons()
    st.subheader("Session Summary")
    
    st.write(f"Rounds completed: {st.session_state.max_rounds}")
    st.write(f"Agent order: {st.session_state.session._agent_sequence}")
    st.write(f"Final concept map:")
    conceptmap_component(cm_data=st.session_state.cmdata[roundn-1], key="cm_summary")


def render_agent_name():
    roundn = st.session_state.roundn
    agent_name = st.session_state.session.get_agent_name(roundn)
    st.markdown(f'<div style="font-size:20px;">🧙<b> {agent_name} Agent Follow-Up:</div>', unsafe_allow_html=True)

def render_header():
    st.header("Multiagent Scaffolding Experiment")
    st.markdown("---")
    st.subheader(f"Round {st.session_state.roundn + 1}/{st.session_state.max_rounds}")


@st.dialog("How to use a concept map creator?", width='large')
def render_help_dialog():
    st.subheader("Modifying nodes 🔵")
    st.markdown("""
                - Click with **Left Mouse Button** 🖱️ on any place to create a new node.
                    - Write the label and press **Enter** or click on the **OK** Button to confirm changes.
                    - Press **Escape** or drag the context map to discard changes.
                - You can move holding the **Left Mouse Button** 🖱️ on a node.
                    - You can also select multiple nodes by holding the **Shift** button. Selected nodes will be highlighted with the green color 🟢. 
                    - Selected nodes can be moved together.
                - Double Click with **Left Mouse Button** 🖱️ on a node to edit it's label.
                - Click with **Right Mouse Button** 🖱️ on a node to delete it.
                """)
    st.markdown("---")
    st.subheader("Modifying edges ↗️")
    st.markdown("""
                - Click and hold the **Left Mouse Button** 🖱️ on a node for one second to begin the edge creation. The source node will be highlighted with the red color 🔴.
                    - Click with **Left Mouse Button** 🖱️ on the other node to set it as the target node.
                    - Write the label and press **Enter** or click on the **OK** Button to confirm changes.
                    - Press **Escape** or drag the context map to discard changes.
                - Double Click with **Left Mouse Button** 🖱️ on an edge to edit it's label.
                - Click with **Right Mouse Button** 🖱️ on an edge to delete it.

                """)


def render_concept_map():
    roundn = st.session_state.roundn
    contents = st.session_state.contents
    cm_label = contents["labels"]["extend" if roundn else "initial"]["header"]
    
    _, middle,right = st.columns([1, 20, 1])
    with right:
        if st.button(label='❓', type='secondary'):
            render_help_dialog()
    with middle:
        st.write(cm_label)
        response = conceptmap_component(
            cm_data=st.session_state.cmdata[roundn],
            submit_request=st.session_state.submit_request,
            key=f"round_{roundn}"
        )
    return response


def render_cm_submit_button():
    with st.columns(5)[2]:
        if not st.session_state.followup:
            if st.button("Submit", type='primary'):
                if st.session_state.roundn == st.session_state.max_rounds - 1:
                    st.session_state.roundn += 1
                    
                st.session_state.submit_request = True
                st.rerun()
         

def render_followup():
    roundn = st.session_state.roundn
    with st.container(border=True):
        with st.spinner("Waiting for agent response..."):
            render_agent_name()
        with st.container(border=True):
            agent_msg = st.session_state.session.get_agent_response(roundn)
            st.write(agent_msg)
        st.text_area(label='label', label_visibility='hidden', placeholder="Please respond to the scaffolding above", height="stretch", key='followup_response')
        with st.columns([2,1,2])[1]: 
            if st.button("Submit", type='primary', disabled=len(st.session_state.followup_response) == 0):
                st.session_state.followup = False
                st.session_state.roundn += 1
                st.rerun()


# Handling of the concept map responses
def handle_response(response):
    if response and not st.session_state.followup:
        st.session_state.cmdata.append(response)
        st.session_state.submit_request = False
        st.session_state.followup = True
        st.rerun()
    elif st.session_state.submit_request:
        st.session_state.submit_request = False


# Main Logic
def main():
    init_session_state()
    
    roundn = st.session_state.roundn

    if roundn == st.session_state.max_rounds:
        render_summary_page()
    else:
        render_header()
        response = render_concept_map()
        handle_response(response)
        render_cm_submit_button()

        if st.session_state.followup:
            render_followup()



if __name__ == "__main__":
    main()

