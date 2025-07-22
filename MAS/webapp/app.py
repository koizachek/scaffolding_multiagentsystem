import os
import streamlit as st 
import streamlit.components.v1 as components

_RELEASE = False 

if not _RELEASE:
    _component_func = components.declare_component("cm_component", path="frontend")
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/build")
    _component_func = components.declare_component("cm_component", path=build_dir)

def cm_component(name, key=None):
    """Create a new instance of "cm_component"."""
    component_value = _component_func(name=name, key=key, default=0)
    return component_value

st.header("Scaffolding")
cm_component("scaff", key="cmap")
