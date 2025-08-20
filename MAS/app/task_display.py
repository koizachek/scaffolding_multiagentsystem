"""
Task Display Module with Copy Protection
This module handles the secure display of task content with anti-copy measures.
"""

import streamlit as st
import streamlit.components.v1 as components
from MAS.app.task_content import (
    STUDY_TITLE, STUDY_INTRODUCTION, TASK_DESCRIPTION, 
    EXTRA_MATERIALS, INITIAL_CONCEPT_MAP
)

def display_task_with_protection():
    """Display task content with copy protection measures."""
    
    # Add CSS for copy protection
    copy_protection_css = """
    <style>
    /* Disable text selection */
    .no-select {
        -webkit-user-select: none !important;
        -moz-user-select: none !important;
        -ms-user-select: none !important;
        user-select: none !important;
        -webkit-touch-callout: none !important;
    }
    
    /* Disable right-click context menu on task content */
    .task-content {
        position: relative;
        -webkit-user-select: none !important;
        -moz-user-select: none !important;
        -ms-user-select: none !important;
        user-select: none !important;
    }
    
    /* Override selection for all task elements */
    .task-content * {
        -webkit-user-select: none !important;
        -moz-user-select: none !important;
        -ms-user-select: none !important;
        user-select: none !important;
    }
    
    /* Disable highlighting */
    .task-content::selection,
    .task-content *::selection {
        background: transparent !important;
    }
    
    .task-content::-moz-selection,
    .task-content *::-moz-selection {
        background: transparent !important;
    }
    
    /* Disable drag */
    .task-content img,
    .task-content a {
        -webkit-user-drag: none !important;
        -khtml-user-drag: none !important;
        -moz-user-drag: none !important;
        -o-user-drag: none !important;
        user-drag: none !important;
    }
    
    /* Disable print */
    @media print {
        .task-content {
            display: none !important;
        }
    }
    </style>
    """
    
    # JavaScript for additional protection
    copy_protection_js = """
    <script>
    // Disable right-click context menu
    document.addEventListener('contextmenu', function(e) {
        var taskElements = document.querySelectorAll('.task-content, .task-content *');
        for (var i = 0; i < taskElements.length; i++) {
            if (taskElements[i].contains(e.target)) {
                e.preventDefault();
                return false;
            }
        }
    });
    
    // Disable text selection with mouse
    document.addEventListener('selectstart', function(e) {
        var taskElements = document.querySelectorAll('.task-content, .task-content *');
        for (var i = 0; i < taskElements.length; i++) {
            if (taskElements[i].contains(e.target)) {
                e.preventDefault();
                return false;
            }
        }
    });
    
    // Disable copy keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        var taskElements = document.querySelectorAll('.task-content, .task-content *');
        var isInTaskContent = false;
        
        for (var i = 0; i < taskElements.length; i++) {
            if (taskElements[i].contains(document.activeElement)) {
                isInTaskContent = true;
                break;
            }
        }
        
        if (isInTaskContent) {
            // Disable Ctrl+A, Ctrl+C, Ctrl+X
            if ((e.ctrlKey || e.metaKey) && (e.keyCode == 65 || e.keyCode == 67 || e.keyCode == 88)) {
                e.preventDefault();
                return false;
            }
            // Disable F12 (Developer Tools)
            if (e.keyCode == 123) {
                e.preventDefault();
                return false;
            }
            // Disable Ctrl+Shift+I (Developer Tools)
            if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.keyCode == 73) {
                e.preventDefault();
                return false;
            }
            // Disable Ctrl+Shift+J (Console)
            if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.keyCode == 74) {
                e.preventDefault();
                return false;
            }
        }
    });
    
    // Disable drag and drop
    document.addEventListener('dragstart', function(e) {
        var taskElements = document.querySelectorAll('.task-content, .task-content *');
        for (var i = 0; i < taskElements.length; i++) {
            if (taskElements[i].contains(e.target)) {
                e.preventDefault();
                return false;
            }
        }
    });
    
    // Clear clipboard if copy attempt is made
    document.addEventListener('copy', function(e) {
        var taskElements = document.querySelectorAll('.task-content, .task-content *');
        for (var i = 0; i < taskElements.length; i++) {
            if (taskElements[i].contains(e.target)) {
                e.clipboardData.setData('text/plain', 'Copying task content is not allowed.');
                e.preventDefault();
                return false;
            }
        }
    });
    
    // Disable print
    window.addEventListener('beforeprint', function(e) {
        alert('Printing task content is not allowed.');
        return false;
    });
    </script>
    """
    
    # Inject CSS and JavaScript
    st.markdown(copy_protection_css, unsafe_allow_html=True)
    components.html(copy_protection_js, height=0)
    
    # Display task content with protection wrapper
    st.markdown('<div class="task-content no-select">', unsafe_allow_html=True)
    
    # Title
    st.markdown(f"## {STUDY_TITLE}")
    
    # Introduction
    st.markdown("### Introduction")
    st.markdown(STUDY_INTRODUCTION)
    
    # Task Description
    st.markdown("### Task Description")
    st.markdown(TASK_DESCRIPTION)
    
    # Extra Materials in Expander
    with st.expander("📚 Additional Resources (Protected Content)", expanded=False):
        st.markdown('<div class="task-content no-select">', unsafe_allow_html=True)
        st.markdown(EXTRA_MATERIALS)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Close protection wrapper
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Warning message
    st.warning("⚠️ **Note:** Task content is protected and cannot be copied. Please read carefully and create your concept map based on your understanding.")
    
    # Additional protection notice
    st.info("💡 **Tip:** Focus on understanding the relationships between concepts rather than memorizing the exact text. The goal is to demonstrate your analytical thinking, not reproduction of the instructions.")


def display_task_simple():
    """Fallback display without protection for testing."""
    st.markdown(f"## {STUDY_TITLE}")
    st.markdown("### Introduction")
    st.markdown(STUDY_INTRODUCTION)
    st.markdown("### Task Description")
    st.markdown(TASK_DESCRIPTION)
    
    with st.expander("📚 Additional Resources", expanded=False):
        st.markdown(EXTRA_MATERIALS)
