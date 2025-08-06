"""
Standalone test for the concept map component to verify data flow.
"""

import streamlit as st
from .conceptmap_component import conceptmap_component

st.title("🧪 Concept Map Component Test")
st.markdown("This is a standalone test to verify the component is working properly.")

# Test the component
st.subheader("Test Component")
result = conceptmap_component(key="test_component")

st.subheader("Debug Information")
st.write(f"**Component returned:** {result is not None}")
st.write(f"**Type:** {type(result).__name__}")

if result:
    st.subheader("Raw Component Output")
    st.json(result)
    
    if isinstance(result, dict) and "elements" in result:
        elements = result["elements"]
        st.write(f"**Elements found:** {len(elements)}")
        
        nodes = [e for e in elements if "source" not in e.get("data", {})]
        edges = [e for e in elements if "source" in e.get("data", {})]
        
        st.write(f"**Nodes:** {len(nodes)}")
        st.write(f"**Edges:** {len(edges)}")
        
        if elements:
            st.subheader("Sample Elements")
            for i, elem in enumerate(elements[:3]):
                st.write(f"{i+1}. {elem}")
else:
    st.warning("⚠️ Component returned None - this indicates a communication issue")

st.markdown("---")
st.markdown("**Instructions:**")
st.markdown("1. Click on the map to add nodes")
st.markdown("2. Hold click on a node for 1 second, then click another to connect")
st.markdown("3. Check if the debug information updates")
