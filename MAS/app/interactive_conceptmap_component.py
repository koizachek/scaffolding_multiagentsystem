"""
Interactive Concept Map Component for Streamlit using Cytoscape.js

This module provides a true interactive concept map component that integrates
Cytoscape.js with Streamlit for drag-and-drop, click-to-create functionality.
"""

import streamlit as st
import streamlit.components.v1 as components
import json
from typing import Dict, Any, Optional


def interactive_conceptmap_component(cm_data: Optional[Dict[str, Any]] = None, 
                                   submit_request: bool = False, 
                                   key: str = "interactive_conceptmap") -> Optional[Dict[str, Any]]:
    """
    Render an interactive concept map component using Cytoscape.js.
    
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
    
    # Convert to Cytoscape format
    cytoscape_elements = []
    for element in cm_data.get("elements", []):
        data = element.get("data", {})
        if "source" not in data:  # It's a node
            cytoscape_elements.append({
                "data": {
                    "id": data.get("id", ""),
                    "label": data.get("label", "")
                },
                "position": {
                    "x": data.get("x", 200),
                    "y": data.get("y", 150)
                }
            })
        else:  # It's an edge
            cytoscape_elements.append({
                "data": {
                    "id": data.get("id", ""),
                    "source": data.get("source", ""),
                    "target": data.get("target", ""),
                    "label": data.get("label", "")
                }
            })
    
    # HTML template with Cytoscape.js
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
        </div>
        
        <div class="toolbar">
            <button id="resetBtn">🔄 Reset View</button>
            <button id="fitBtn">📐 Fit to Screen</button>
            <button id="exportBtn">💾 Export Data</button>
            <span style="margin-left: auto; font-size: 14px; color: #6c757d;">
                Nodes: <span id="nodeCount">0</span> | Edges: <span id="edgeCount">0</span>
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
            
            // Initialize Cytoscape
            document.addEventListener('DOMContentLoaded', function() {{
                cy = cytoscape({{
                    container: document.getElementById('cy'),
                    
                    elements: {json.dumps(cytoscape_elements)},
                    
                    // Zoom and pan settings to prevent map from disappearing
                    minZoom: 0.2,      // Prevents zooming out too far (20% minimum)
                    maxZoom: 3,        // Prevents zooming in too much (300% maximum)
                    wheelSensitivity: 0.1,  // Makes scroll wheel zooming smoother
                    
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
                
                // Event handlers
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
                        evt.target.remove();
                        updateCounts();
                        sendDataToStreamlit();
                    }}
                }});
                
                cy.on('dbltap', function(evt) {{
                    // Double click - edit label
                    if (evt.target !== cy) {{
                        editLabel(evt.target, evt.renderedPosition || evt.position);
                    }}
                }});
                
                cy.on('dragfree', 'node', function(evt) {{
                    // Node moved - update data
                    sendDataToStreamlit();
                }});
                
                // Toolbar buttons with enhanced reset/fit functionality
                document.getElementById('resetBtn').onclick = function() {{
                    cy.zoom(1);  // Reset to 100% zoom
                    cy.center(); // Center the viewport
                    cy.fit(50);  // Fit all elements with 50px padding
                }};
                
                document.getElementById('fitBtn').onclick = function() {{
                    cy.fit(50);  // Fit all elements to screen with padding
                    // Ensure zoom stays within bounds
                    if (cy.zoom() < 0.2) cy.zoom(0.2);
                    if (cy.zoom() > 3) cy.zoom(3);
                }};
                
                document.getElementById('exportBtn').onclick = function() {{
                    sendDataToStreamlit();
                }};
                
                // Escape key cancels edge creation
                document.addEventListener('keydown', function(e) {{
                    if (e.key === 'Escape') {{
                        resetEdgeCreation();
                        cancelLabel();
                    }}
                }});
            }});
            
            function createNode(x, y) {{
                showLabelInput(x, y, function(label) {{
                    if (label.trim()) {{
                        let nodeId = 'node_' + nodeIdCounter++;
                        cy.add({{
                            data: {{ id: nodeId, label: label }},
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
                        updateCounts();
                        sendDataToStreamlit();
                    }}
                }});
            }}
            
            function editLabel(element, pos) {{
                showLabelInput(pos.x, pos.y, function(label) {{
                    if (label.trim()) {{
                        element.data('label', label);
                        sendDataToStreamlit();
                    }}
                }}, element.data('label'));
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
                
                // Send to Streamlit
                window.parent.postMessage({{
                    type: 'streamlit:componentValue',
                    value: {{ elements: elements }}
                }}, '*');
            }}
            
            // Send initial data
            setTimeout(sendDataToStreamlit, 100);
        </script>
    </body>
    </html>
    """
    
    # Render the component
    component_value = components.html(
        html_template,
        height=700
    )
    
    # Return the component value (concept map data)
    return component_value


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
    st.title("Interactive Concept Map Component Test")
    
    # Test the component
    result = interactive_conceptmap_component(key="test")
    
    if result:
        st.write("**Component Output:**")
        st.json(result)
        
        st.write("**Parsed Output:**")
        parsed = parse_conceptmap(result)
        st.json(parsed)
