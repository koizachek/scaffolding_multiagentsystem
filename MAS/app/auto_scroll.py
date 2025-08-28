"""
Auto-scroll functionality for Streamlit app.

This module provides JavaScript-based auto-scrolling to ensure smooth
transitions between rounds and important page changes.
"""

import streamlit as st
import streamlit.components.v1 as components


def scroll_to_top():
    """Scroll to the top of the page."""
    components.html(
        """
        <script>
            window.parent.document.querySelector('.main').scrollTo(0, 0);
        </script>
        """,
        height=0
    )


def scroll_to_element(element_id: str, offset: int = 100):
    """
    Scroll to a specific element on the page.
    
    Args:
        element_id: The HTML element ID to scroll to
        offset: Pixel offset from the top (default 100)
    """
    components.html(
        f"""
        <script>
            const element = window.parent.document.getElementById('{element_id}');
            if (element) {{
                const yOffset = -{offset};
                const y = element.getBoundingClientRect().top + window.parent.pageYOffset + yOffset;
                window.parent.scrollTo({{top: y, behavior: 'smooth'}});
            }}
        </script>
        """,
        height=0
    )


def smooth_scroll_to_position(position: int):
    """
    Smoothly scroll to a specific vertical position.
    
    Args:
        position: The vertical position in pixels to scroll to
    """
    components.html(
        f"""
        <script>
            window.parent.scrollTo({{
                top: {position},
                behavior: 'smooth'
            }});
        </script>
        """,
        height=0
    )


def auto_scroll_on_round_change():
    """
    Automatically scroll to appropriate position when round changes.
    This ensures users see the new content immediately.
    """
    # Check if we've changed rounds
    if 'previous_round' not in st.session_state:
        st.session_state.previous_round = st.session_state.get('roundn', 0)
    
    current_round = st.session_state.get('roundn', 0)
    
    if current_round != st.session_state.previous_round:
        # Round has changed, scroll to top
        scroll_to_top()
        st.session_state.previous_round = current_round
        return True
    
    return False


def auto_scroll_on_page_transition():
    """
    Automatically scroll when transitioning between major page sections.
    """
    # Track page state transitions
    page_state_keys = [
        'consent_given',
        'profile_initialized', 
        'pre_questionnaire_completed',
        'tutorial_completed',
        'clt_completed',
        'agent_differentiation_completed',
        'map_adaptation_completed',
        'session_finalized'
    ]
    
    # Create a composite state string
    current_state = ''.join([
        '1' if st.session_state.get(key, False) else '0' 
        for key in page_state_keys
    ])
    
    # Check if state has changed
    if 'previous_page_state' not in st.session_state:
        st.session_state.previous_page_state = current_state
    
    if current_state != st.session_state.previous_page_state:
        # Page state has changed, scroll to top
        scroll_to_top()
        st.session_state.previous_page_state = current_state
        return True
    
    return False


def auto_scroll_to_agent_response():
    """
    Scroll to agent response area when a new response is generated.
    """
    if st.session_state.get('agent_msg') and st.session_state.get('followup'):
        # Scroll down a bit to show the agent response
        smooth_scroll_to_position(400)


def inject_auto_scroll_styles():
    """
    Inject CSS to improve scrolling behavior and visual feedback.
    """
    st.markdown(
        """
        <style>
        /* Smooth scrolling for the entire app */
        html {
            scroll-behavior: smooth;
        }
        
        /* Visual indicator for scroll position */
        .scroll-indicator {
            position: fixed;
            top: 0;
            left: 0;
            height: 3px;
            background: linear-gradient(to right, #4CAF50, #2196F3);
            transition: width 0.3s ease;
            z-index: 9999;
        }
        
        /* Ensure main content area is scrollable */
        .main .block-container {
            scroll-behavior: smooth;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
