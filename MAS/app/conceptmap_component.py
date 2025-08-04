"""
Interactive Concept Map Component for Streamlit using Cytoscape.js

This module provides a true interactive concept map component that integrates
Cytoscape.js with Streamlit for drag-and-drop, click-to-create functionality.
Enhanced with detailed action logging for research purposes.
"""

import streamlit as st
import streamlit.components.v1 as components
import json
from typing import Dict, Any, Optional


def conceptmap_component(cm_data: Optional[Dict[str, Any]] = None, 
                        submit_request: bool = False, 
                        key: str = "conceptmap") -> Optional[Dict[str, Any]]:
    """
    Render an interactive concept map component using Cytoscape.js with enhanced action tracking.
    
    Args:
        cm_data: Initial concept map data
        submit_request: Whether a submit was requested
        key: Unique key for the component
        
    Returns:
        Updated concept map data with action history or None
    """
    
    # Initialize concept map data
    if cm_data is None:
        cm_data = {
            "elements": [
                {"data": {"id": "start", "label": "Start Here", "x": 200, "y": 150}}
            ]
        }
    
    # Convert to Cytoscape format
    cytoscape_elements = []
    elements = cm_data.get("elements", []) if cm_data else []
    
    node_counter = 1
    edge_counter = 1
    
    for element in elements:
        if not element or "data" not in element:
            continue
            
        data = element["data"]
        if "source" not in data:  # It's a node
            # Ensure valid ID
            node_id = data.get("id", "")
            if not node_id or node_id.strip() == "":
                node_id = f"node_{node_counter}"
                node_counter += 1
                
            cytoscape_elements.append({
                "data": {
                    "id": node_id,
                    "label": data.get("label", "Untitled")
                },
                "position": {
                    "x": data.get("x", 200),
                    "y": data.get("y", 150)
                }
            })
        else:  # It's an edge
            # Ensure valid ID
            edge_id = data.get("id", "")
            if not edge_id or edge_id.strip() == "":
                edge_id = f"edge_{edge_counter}"
                edge_counter += 1
                
            # Ensure valid source and target
            source_id = data.get("source", "")
            target_id = data.get("target", "")
            
            if source_id and target_id:  # Only add edge if both source and target exist
                cytoscape_elements.append({
                    "data": {
                        "id": edge_id,
                        "source": source_id,
                        "target": target_id,
                        "label": data.get("label", "")
                    }
                })
    
    # HTML template with enhanced Cytoscape.js and action tracking
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://unpkg.com/cytoscape@3.24.0/dist/cytoscape.min.js"></script>
        <style>
            #cy {{
                width: 100%;
                height: 600px;
                border: 2px solid #ddd;
                border-radius: 8px;
                background: #fafafa;
                cursor: crosshair;
            }}
            
            .toolbar {{
                display: flex;
                gap: 10px;
                padding: 10px;
                background: #f8f9fa;
                border-bottom: 1px solid #dee2e6;
                border-radius: 8px 8px 0 0;
                margin-bottom: 0;
            }}
            
            .toolbar button {{
                padding: 8px 16px;
                border: 1px solid #ced4da;
                background: white;
                border-radius: 4px;
                cursor: pointer;
                font-size: 14px;
                transition: all 0.2s;
            }}
            
            .toolbar button:hover {{
                background: #e9ecef;
            }}
            
            .toolbar button.active {{
                background: #28a745;
                color: white;
                border-color: #28a745;
            }}
            
            #labelInputBox {{
                position: absolute;
                display: none;
                background: white;
                border: 2px solid #007bff;
                border-radius: 4px;
                padding: 8px;
                z-index: 1000;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                min-width: 200px;
            }}
            
            #labelInput {{
                width: 100%;
                padding: 6px;
                border: 1px solid #ced4da;
                border-radius: 3px;
                font-size: 14px;
            }}
            
            .input-buttons {{
                margin-top: 8px;
                display: flex;
                gap: 8px;
            }}
            
            .input-buttons button {{
                padding: 4px 12px;
                border: 1px solid #ced4da;
                border-radius: 3px;
                cursor: pointer;
                font-size: 12px;
            }}
            
            .btn-ok {{
                background: #28a745;
                color: white;
                border-color: #28a745;
            }}
            
            .btn-cancel {{
                background: #6c757d;
                color: white;
                border-color: #6c757d;
            }}
            
            .instructions {{
                padding: 10px;
                background: #e7f3ff;
                border: 1px solid #b3d9ff;
                border-radius: 4px;
                margin-bottom: 10px;
                font-size: 14px;
            }}
        </style>
    </head>
    <body>
        <div class="instructions">
            <strong>🗺️ Interactive Concept Map:</strong>
            <strong>Left-click</strong> empty space to add concepts • 
            <strong>Click & hold</strong> a node for 1 second, then click another to connect • 
            <strong>Double-click</strong> to edit • 
            <strong>Right-click</strong> to delete • 
            <strong>Drag</strong> to move
            <br><small>📊 All actions are being tracked for research purposes</small>
        </div>
        
        <div class="toolbar">
            <button id="resetBtn">🔄 Reset View</button>
            <button id="fitBtn">📐 Fit to Screen</button>
            <button id="exportBtn">💾 Export Data</button>
            <span style="margin-left: auto; font-size: 14px; color: #6c757d;">
                Nodes: <span id="nodeCount">0</span> | Edges: <span id="edgeCount">0</span> | Actions: <span id="actionCount">0</span>
            </span>
        </div>
        
        <div id="cy"></div>
        
        <div id="labelInputBox">
            <input type="text" id="labelInput" placeholder="Enter label..." />
            <div class="input-buttons">
                <button class="btn-ok" onclick="confirmLabel()">✓ OK</button>
                <button class="btn-cancel" onclick="cancelLabel()">✗ Cancel</button>
            </div>
        </div>

        <script>
            let cy;
            let currentElement = null;
            let isCreatingEdge = false;
            let sourceNode = null;
            let nodeIdCounter = 1;
            let edgeIdCounter = 1;
            
            // Enhanced action tracking variables
            let actionHistory = [];
            let sessionStartTime = new Date();
            let roundStartTime = new Date();
            let interactionMetrics = {{
                total_actions: 0,
                nodes_created: 0,
                edges_created: 0,
                nodes_deleted: 0,
                edges_deleted: 0,
                labels_edited: 0,
                nodes_moved: 0
            }};
            
            // Action logging function
            function logAction(actionType, elementId, details = {{}}) {{
                const timestamp = new Date().toISOString();
                const sessionTimeMs = new Date() - sessionStartTime;
                const roundTimeMs = new Date() - roundStartTime;
                
                const action = {{
                    timestamp: timestamp,
                    action_type: actionType,
                    element_id: elementId,
                    details: details,
                    session_time_ms: sessionTimeMs,
                    round_time_ms: roundTimeMs
                }};
                
                actionHistory.push(action);
                interactionMetrics.total_actions++;
                
                // Update specific metrics
                switch(actionType) {{
                    case 'add_node':
                        interactionMetrics.nodes_created++;
                        break;
                    case 'add_edge':
                        interactionMetrics.edges_created++;
                        break;
                    case 'delete_node':
                        interactionMetrics.nodes_deleted++;
                        break;
                    case 'delete_edge':
                        interactionMetrics.edges_deleted++;
                        break;
                    case 'edit_label':
                        interactionMetrics.labels_edited++;
                        break;
                    case 'move_node':
                        interactionMetrics.nodes_moved++;
                        break;
                }}
                
                updateActionCount();
                console.log('Action logged:', action);
            }}
            
            function updateActionCount() {{
                document.getElementById('actionCount').textContent = actionHistory.length;
            }}
            
            // Initialize Cytoscape with enhanced tracking
            function initializeCytoscape() {{
                const container = document.getElementById('cy');
                if (!container) {{
                    setTimeout(initializeCytoscape, 50);
                    return;
                }}
                
                if (window.cytoscapeInitialized) {{
                    return;
                }}
                window.cytoscapeInitialized = true;
                
                cy = cytoscape({{
                    container: document.getElementById('cy'),
                    
                    elements: {json.dumps(cytoscape_elements)},
                    
                    style: [
                        {{
                            selector: 'node',
                            style: {{
                                'background-color': '#3498db',
                                'label': 'data(label)',
                                'text-valign': 'center',
                                'text-halign': 'center',
                                'color': 'white',
                                'text-outline-width': 2,
                                'text-outline-color': '#3498db',
                                'width': 'label',
                                'height': 'label',
                                'padding': '8px',
                                'shape': 'round-rectangle',
                                'font-size': '14px',
                                'font-weight': 'bold'
                            }}
                        }},
                        {{
                            selector: 'node:selected',
                            style: {{
                                'background-color': '#e74c3c',
                                'text-outline-color': '#e74c3c'
                            }}
                        }},
                        {{
                            selector: 'node.source-node',
                            style: {{
                                'background-color': '#e74c3c',
                                'text-outline-color': '#e74c3c'
                            }}
                        }},
                        {{
                            selector: 'edge',
                            style: {{
                                'width': 3,
                                'line-color': '#95a5a6',
                                'target-arrow-color': '#95a5a6',
                                'target-arrow-shape': 'triangle',
                                'curve-style': 'bezier',
                                'label': 'data(label)',
                                'font-size': '12px',
                                'text-rotation': 'autorotate',
                                'text-margin-y': -10,
                                'color': '#2c3e50',
                                'text-background-color': 'white',
                                'text-background-opacity': 0.8,
                                'text-background-padding': '2px'
                            }}
                        }},
                        {{
                            selector: 'edge:selected',
                            style: {{
                                'line-color': '#e74c3c',
                                'target-arrow-color': '#e74c3c'
                            }}
                        }}
                    ],
                    
                    layout: {{
                        name: 'preset'
                    }},
                    
                    userZoomingEnabled: true,
                    userPanningEnabled: true,
                    boxSelectionEnabled: true,
                    selectionType: 'single'
                }});
                
                updateCounts();
                updateActionCount();
                
                // Enhanced event handlers with action logging
                cy.on('tap', function(evt) {{
                    if (evt.target === cy) {{
                        // Clicked on background - create new node
                        let pos = evt.position || evt.cyPosition;
                        createNode(pos.x, pos.y);
                    }}
                }});
                
                cy.on('taphold', 'node', function(evt) {{
                    // Start edge creation
                    if (!isCreatingEdge) {{
                        isCreatingEdge = true;
                        sourceNode = evt.target;
                        sourceNode.addClass('source-node');
                        cy.container().style.cursor = 'crosshair';
                        
                        logAction('start_edge_creation', sourceNode.id(), {{
                            source_label: sourceNode.data('label'),
                            position: sourceNode.position()
                        }});
                    }}
                }});
                
                cy.on('tap', 'node', function(evt) {{
                    if (isCreatingEdge && sourceNode && evt.target !== sourceNode) {{
                        // Complete edge creation
                        createEdge(sourceNode, evt.target);
                        resetEdgeCreation();
                    }}
                }});
                
                cy.on('cxttap', function(evt) {{
                    // Right click - delete element
                    if (evt.target !== cy) {{
                        const elementType = evt.target.isNode() ? 'node' : 'edge';
                        const elementId = evt.target.id();
                        const elementData = {{
                            id: elementId,
                            label: evt.target.data('label')
                        }};
                        
                        if (elementType === 'edge') {{
                            elementData.source = evt.target.source().id();
                            elementData.target = evt.target.target().id();
                        }} else {{
                            elementData.position = evt.target.position();
                        }}
                        
                        logAction(`delete_${{elementType}}`, elementId, elementData);
                        
                        evt.target.remove();
                        updateCounts();
                        sendDataToStreamlit();
                    }}
                }});
                
                cy.on('dbltap', function(evt) {{
                    // Double click - edit label
                    if (evt.target !== cy) {{
                        const oldLabel = evt.target.data('label');
                        editLabel(evt.target, evt.renderedPosition || evt.position, oldLabel);
                    }}
                }});
                
                cy.on('dragfree', 'node', function(evt) {{
                    // Node moved - log and update data
                    const newPos = evt.target.position();
                    logAction('move_node', evt.target.id(), {{
                        label: evt.target.data('label'),
                        new_position: newPos
                    }});
                    sendDataToStreamlit();
                }});
                
                // Toolbar buttons
                document.getElementById('resetBtn').onclick = function() {{
                    logAction('reset_view', null, {{
                        zoom_before: cy.zoom(),
                        pan_before: cy.pan()
                    }});
                    cy.zoom(1);
                    cy.center();
                }};
                
                document.getElementById('fitBtn').onclick = function() {{
                    logAction('fit_to_screen', null, {{
                        zoom_before: cy.zoom(),
                        pan_before: cy.pan()
                    }});
                    cy.fit();
                }};
                
                document.getElementById('exportBtn').onclick = function() {{
                    logAction('manual_export', null, {{
                        nodes_count: cy.nodes().length,
                        edges_count: cy.edges().length
                    }});
                    sendDataToStreamlit();
                }};
                
                // Escape key cancels edge creation
                document.addEventListener('keydown', function(e) {{
                    if (e.key === 'Escape') {{
                        if (isCreatingEdge) {{
                            logAction('cancel_edge_creation', sourceNode ? sourceNode.id() : null);
                        }}
                        resetEdgeCreation();
                        cancelLabel();
                    }}
                }});
                
                // Log initial state
                logAction('component_initialized', null, {{
                    initial_nodes: cy.nodes().length,
                    initial_edges: cy.edges().length
                }});
                
                // Send initial data after a short delay
                setTimeout(sendDataToStreamlit, 100);
            }}
            
            // Initialize immediately and also on DOMContentLoaded as fallback
            initializeCytoscape();
            document.addEventListener('DOMContentLoaded', initializeCytoscape);
            
            // Additional fallback for Streamlit components
            setTimeout(initializeCytoscape, 100);
            
            function createNode(x, y) {{
                showLabelInput(x, y, function(label) {{
                    if (label.trim()) {{
                        let nodeId = 'node_' + nodeIdCounter++;
                        cy.add({{
                            data: {{ id: nodeId, label: label }},
                            position: {{ x: x, y: y }}
                        }});
                        
                        logAction('add_node', nodeId, {{
                            label: label,
                            position: {{ x: x, y: y }}
                        }});
                        
                        updateCounts();
                        sendDataToStreamlit();
                    }}
                }});
            }}
            
            function createEdge(sourceNode, targetNode) {{
                let pos = sourceNode.renderedPosition();
                showLabelInput(pos.x, pos.y, function(label) {{
                    if (label.trim()) {{
                        let edgeId = 'edge_' + edgeIdCounter++;
                        cy.add({{
                            data: {{
                                id: edgeId,
                                source: sourceNode.id(),
                                target: targetNode.id(),
                                label: label
                            }}
                        }});
                        
                        logAction('add_edge', edgeId, {{
                            label: label,
                            source: sourceNode.id(),
                            target: targetNode.id(),
                            source_label: sourceNode.data('label'),
                            target_label: targetNode.data('label')
                        }});
                        
                        updateCounts();
                        sendDataToStreamlit();
                    }}
                }});
            }}
            
            function editLabel(element, pos, oldLabel) {{
                showLabelInput(pos.x, pos.y, function(label) {{
                    if (label.trim() && label !== oldLabel) {{
                        element.data('label', label);
                        
                        logAction('edit_label', element.id(), {{
                            old_label: oldLabel,
                            new_label: label,
                            element_type: element.isNode() ? 'node' : 'edge'
                        }});
                        
                        sendDataToStreamlit();
                    }}
                }}, oldLabel);
            }}
            
            function showLabelInput(x, y, callback, currentLabel = '') {{
                currentElement = {{ callback: callback }};
                let inputBox = document.getElementById('labelInputBox');
                let input = document.getElementById('labelInput');
                
                input.value = currentLabel;
                inputBox.style.left = x + 'px';
                inputBox.style.top = y + 'px';
                inputBox.style.display = 'block';
                input.focus();
                input.select();
                
                input.onkeydown = function(e) {{
                    if (e.key === 'Enter') {{
                        confirmLabel();
                    }} else if (e.key === 'Escape') {{
                        cancelLabel();
                    }}
                }};
            }}
            
            function confirmLabel() {{
                if (currentElement && currentElement.callback) {{
                    let label = document.getElementById('labelInput').value;
                    currentElement.callback(label);
                }}
                cancelLabel();
            }}
            
            function cancelLabel() {{
                document.getElementById('labelInputBox').style.display = 'none';
                currentElement = null;
                resetEdgeCreation();
            }}
            
            function resetEdgeCreation() {{
                if (sourceNode) {{
                    sourceNode.removeClass('source-node');
                }}
                isCreatingEdge = false;
                sourceNode = null;
                cy.container().style.cursor = 'default';
            }}
            
            function updateCounts() {{
                let nodeCount = cy.nodes().length;
                let edgeCount = cy.edges().length;
                document.getElementById('nodeCount').textContent = nodeCount;
                document.getElementById('edgeCount').textContent = edgeCount;
            }}
            
            function sendDataToStreamlit() {{
                let elements = [];
                
                // Add nodes
                cy.nodes().forEach(function(node) {{
                    let pos = node.position();
                    elements.push({{
                        data: {{
                            id: node.id(),
                            label: node.data('label'),
                            x: pos.x,
                            y: pos.y
                        }}
                    }});
                }});
                
                // Add edges
                cy.edges().forEach(function(edge) {{
                    elements.push({{
                        data: {{
                            id: edge.id(),
                            source: edge.source().id(),
                            target: edge.target().id(),
                            label: edge.data('label')
                        }}
                    }});
                }});
                
                // Calculate session duration
                const sessionDurationMs = new Date() - sessionStartTime;
                const roundDurationMs = new Date() - roundStartTime;
                
                // Send enhanced data to Streamlit
                window.parent.postMessage({{
                    type: 'streamlit:componentValue',
                    value: {{
                        elements: elements,
                        action_history: actionHistory,
                        interaction_metrics: interactionMetrics,
                        session_timing: {{
                            session_duration_ms: sessionDurationMs,
                            round_duration_ms: roundDurationMs,
                            session_start: sessionStartTime.toISOString(),
                            round_start: roundStartTime.toISOString()
                        }}
                    }}
                }}, '*');
            }}
            
        </script>
    </body>
    </html>
    """
    
    # Render the component without key parameter for compatibility
    component_value = components.html(
        html_template,
        height=700
    )
    
    # Debug: Log what the component is returning
    if component_value is not None:
        print(f"🔍 COMPONENT DEBUG: Received data from component")
        print(f"   Type: {type(component_value)}")
        print(f"   Content: {str(component_value)[:200]}")
    else:
        print(f"🔍 COMPONENT DEBUG: Component returned None")
    
    # Return the component value (concept map data with action history)
    return component_value


def parse_conceptmap(cm_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse concept map data into a standardized format with enhanced action tracking.
    
    Args:
        cm_data: Raw concept map data with action history
        
    Returns:
        Parsed concept map data with action analytics
    """
    if not cm_data or "elements" not in cm_data:
        return {"concepts": [], "relationships": [], "action_history": [], "interaction_metrics": {}}
    
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
        "relationships": relationships,
        "action_history": cm_data.get("action_history", []),
        "interaction_metrics": cm_data.get("interaction_metrics", {}),
        "session_timing": cm_data.get("session_timing", {})
    }


# Example usage and testing
if __name__ == "__main__":
    st.title("Enhanced Interactive Concept Map Component Test")
    
    # Test the component
    result = conceptmap_component(key="test")
    
    if result:
        st.write("**Component Output:**")
        st.json(result)
        
        st.write("**Parsed Output:**")
        parsed = parse_conceptmap(result)
        st.json(parsed)
        
        # Display action analytics if available
        if result.get("action_history"):
            st.write("**Action Analytics:**")
            st.write(f"Total Actions: {len(result['action_history'])}")
            if result.get("interaction_metrics"):
                metrics = result["interaction_metrics"]
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Nodes Created", metrics.get("nodes_created", 0))
                    st.metric("Nodes Deleted", metrics.get("nodes_deleted", 0))
                with col2:
                    st.metric("Edges Created", metrics.get("edges_created", 0))
                    st.metric("Edges Deleted", metrics.get("edges_deleted", 0))
                with col3:
                    st.metric("Labels Edited", metrics.get("labels_edited", 0))
                    st.metric("Nodes Moved", metrics.get("nodes_moved", 0))
