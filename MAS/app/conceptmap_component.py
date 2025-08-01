"""
Concept Map Component for Streamlit

This module provides a Streamlit component for interactive concept map creation and editing.
It serves as a placeholder/mock implementation for the actual concept map component.
"""

import streamlit as st
import json
from typing import Dict, Any, Optional


def conceptmap_component(cm_data: Optional[Dict[str, Any]] = None, 
                        submit_request: bool = False, 
                        key: str = "conceptmap") -> Optional[Dict[str, Any]]:
    """
    Render an interactive concept map component.
    
    This is a simplified implementation that provides basic concept map functionality
    through Streamlit's native components until a full interactive component is available.
    
    Args:
        cm_data: Initial concept map data
        submit_request: Whether a submit was requested
        key: Unique key for the component
        
    Returns:
        Updated concept map data or None
    """
    
    # Initialize concept map data
    if cm_data is None:
        cm_data = {
            "elements": [
                {"data": {"id": "start", "label": "Start Here", "x": 200, "y": 150}}
            ]
        }
    
    # Create a container for the concept map editor
    with st.container():
        st.markdown("### 🗺️ Concept Map Editor")
        
        # Show current concept map structure
        if cm_data and "elements" in cm_data:
            nodes = [elem for elem in cm_data["elements"] if "source" not in elem.get("data", {})]
            edges = [elem for elem in cm_data["elements"] if "source" in elem.get("data", {})]
            
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Nodes:** {len(nodes)}")
                for node in nodes[:5]:  # Show first 5 nodes
                    label = node.get("data", {}).get("label", "Unlabeled")
                    st.write(f"• {label}")
                if len(nodes) > 5:
                    st.write(f"... and {len(nodes) - 5} more")
            
            with col2:
                st.write(f"**Connections:** {len(edges)}")
                for edge in edges[:5]:  # Show first 5 edges
                    label = edge.get("data", {}).get("label", "unlabeled")
                    source = edge.get("data", {}).get("source", "?")
                    target = edge.get("data", {}).get("target", "?")
                    st.write(f"• {source} → {target} ({label})")
                if len(edges) > 5:
                    st.write(f"... and {len(edges) - 5} more")
        
        # Simplified editing interface
        st.markdown("---")
        st.markdown("**Quick Edit Interface:**")
        
        # Add new node
        with st.expander("➕ Add New Concept", expanded=False):
            new_concept = st.text_input("Concept name:", key=f"{key}_new_concept")
            if st.button("Add Concept", key=f"{key}_add_concept") and new_concept:
                # Add new node to concept map
                new_id = f"concept_{len([e for e in cm_data['elements'] if 'source' not in e.get('data', {})])}"
                new_node = {
                    "data": {
                        "id": new_id,
                        "label": new_concept,
                        "x": 200 + len([e for e in cm_data['elements'] if 'source' not in e.get('data', {})]) * 50,
                        "y": 150 + (len([e for e in cm_data['elements'] if 'source' not in e.get('data', {})]) % 3) * 100
                    }
                }
                cm_data["elements"].append(new_node)
                st.success(f"Added concept: {new_concept}")
                st.rerun()
        
        # Add new connection
        with st.expander("🔗 Add New Connection", expanded=False):
            nodes = [elem for elem in cm_data["elements"] if "source" not in elem.get("data", {})]
            if len(nodes) >= 2:
                node_options = [f"{node['data']['id']}: {node['data']['label']}" for node in nodes]
                
                source_node = st.selectbox("From concept:", node_options, key=f"{key}_source")
                target_node = st.selectbox("To concept:", node_options, key=f"{key}_target")
                relationship = st.text_input("Relationship label:", key=f"{key}_relationship")
                
                if st.button("Add Connection", key=f"{key}_add_connection") and relationship:
                    source_id = source_node.split(":")[0]
                    target_id = target_node.split(":")[0]
                    
                    if source_id != target_id:
                        new_edge = {
                            "data": {
                                "id": f"edge_{source_id}_{target_id}",
                                "source": source_id,
                                "target": target_id,
                                "label": relationship
                            }
                        }
                        cm_data["elements"].append(new_edge)
                        st.success(f"Added connection: {relationship}")
                        st.rerun()
                    else:
                        st.error("Cannot connect a concept to itself")
            else:
                st.info("Add at least 2 concepts before creating connections")
        
        # Visual representation (simplified)
        st.markdown("---")
        st.markdown("**Current Map Structure:**")
        
        # Create a simple text-based visualization
        nodes = [elem for elem in cm_data["elements"] if "source" not in elem.get("data", {})]
        edges = [elem for elem in cm_data["elements"] if "source" in elem.get("data", {})]
        
        if nodes:
            # Create a simple network diagram using text
            diagram_text = "```\n"
            for edge in edges:
                source_id = edge["data"]["source"]
                target_id = edge["data"]["target"]
                label = edge["data"]["label"]
                
                # Find node labels
                source_label = next((n["data"]["label"] for n in nodes if n["data"]["id"] == source_id), source_id)
                target_label = next((n["data"]["label"] for n in nodes if n["data"]["id"] == target_id), target_id)
                
                diagram_text += f"{source_label} --[{label}]--> {target_label}\n"
            
            if not edges:
                diagram_text += "Isolated concepts:\n"
                for node in nodes:
                    diagram_text += f"• {node['data']['label']}\n"
            
            diagram_text += "```"
            st.markdown(diagram_text)
        
        # Instructions
        st.info("""
        💡 **Instructions:**
        - Use the expandable sections above to add concepts and connections
        - In a full implementation, you would click directly on the map to add concepts
        - This simplified interface allows you to build your concept map step by step
        """)
    
    # Return the updated concept map data
    return cm_data


def parse_conceptmap(cm_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse concept map data into a standardized format.
    
    Args:
        cm_data: Raw concept map data
        
    Returns:
        Parsed concept map data
    """
    if not cm_data or "elements" not in cm_data:
        return {"concepts": [], "relationships": []}
    
    concepts = []
    relationships = []
    
    for element in cm_data["elements"]:
        data = element.get("data", {})
        
        if "source" not in data:  # It's a node
            concepts.append({
                "id": data.get("id", ""),
                "label": data.get("label", ""),
                "x": data.get("x", 0),
                "y": data.get("y", 0)
            })
        else:  # It's an edge
            relationships.append({
                "id": data.get("id", ""),
                "source": data.get("source", ""),
                "target": data.get("target", ""),
                "label": data.get("label", "")
            })
    
    return {
        "concepts": concepts,
        "relationships": relationships
    }


# Example usage and testing
if __name__ == "__main__":
    st.title("Concept Map Component Test")
    
    # Test the component
    result = conceptmap_component(key="test")
    
    if result:
        st.write("**Component Output:**")
        st.json(result)
        
        st.write("**Parsed Output:**")
        parsed = parse_conceptmap(result)
        st.json(parsed)
