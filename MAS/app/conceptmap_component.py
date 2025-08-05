"""
Streamlit concept map component wrapper.

This module exposes a helper function that renders the custom concept map
component built with Cytoscape.js and returns its state to Python. The
returned value can be logged and analysed. A small parser is also provided
that converts the raw component data into a simplified structure.
"""

from __future__ import annotations

import os
from typing import Any, Dict, Optional

import streamlit.components.v1 as components

# Locate the frontend build for the component. The build directory is vendored
# under ``conceptmap_frontend_build`` within this package.
_BUILD_DIR = os.path.join(os.path.dirname(__file__), "conceptmap_frontend_build")

# Declare the Streamlit component using the local build directory so that it can
# exchange data with the Python backend.
_conceptmap = components.declare_component(
    "conceptmap_component", path=_BUILD_DIR
)


def conceptmap_component(
    cm_data: Optional[Dict[str, Any]] = None,
    submit_request: bool = False,
    key: str | None = "conceptmap",
) -> Optional[Dict[str, Any]]:
    """Render the concept map component and return its state.

    Parameters
    ----------
    cm_data:
        Initial data to populate the component. If ``None`` an empty map is
        shown.
    submit_request:
        Flag forwarded to the frontend to indicate a submission request.
    key:
        Unique Streamlit key for the component instance.

    Returns
    -------
    dict or ``None``
        The concept map data returned by the frontend component.
    """

    cm_data = cm_data or {}
    return _conceptmap(
        cm_data=cm_data, submit_request=submit_request, key=key, default=None
    )


def parse_conceptmap(cm_data: Dict[str, Any]) -> Dict[str, Any]:
    """Parse raw component data into a simplified concept map representation."""
    if not cm_data or "elements" not in cm_data:
        return {
            "concepts": [],
            "relationships": [],
            "action_history": [],
            "interaction_metrics": {},
            "session_timing": {},
        }

    elements = cm_data.get("elements", {})
    nodes: list[Dict[str, Any]] = []
    edges: list[Dict[str, Any]] = []

    # The frontend may return elements as a dict with ``nodes`` and ``edges`` or
    # as a flat list. Handle both cases for robustness.
    if isinstance(elements, dict) and ("nodes" in elements or "edges" in elements):
        raw_nodes = elements.get("nodes", [])
        raw_edges = elements.get("edges", [])
        for node in raw_nodes:
            data = node.get("data", {})
            nodes.append(
                {
                    "id": data.get("id", ""),
                    "label": data.get("label", ""),
                    "x": data.get("x", 0),
                    "y": data.get("y", 0),
                }
            )
        for edge in raw_edges:
            data = edge.get("data", {})
            edges.append(
                {
                    "id": data.get("id", ""),
                    "source": data.get("source", ""),
                    "target": data.get("target", ""),
                    "label": data.get("label", ""),
                }
            )
    else:
        # Elements delivered as a flat list
        for element in elements:
            data = element.get("data", {})
            if "source" not in data:
                nodes.append(
                    {
                        "id": data.get("id", ""),
                        "label": data.get("label", ""),
                        "x": data.get("x", 0),
                        "y": data.get("y", 0),
                    }
                )
            else:
                edges.append(
                    {
                        "id": data.get("id", ""),
                        "source": data.get("source", ""),
                        "target": data.get("target", ""),
                        "label": data.get("label", ""),
                    }
                )

    return {
        "concepts": nodes,
        "relationships": edges,
        "action_history": cm_data.get("action_history", []),
        "interaction_metrics": cm_data.get("interaction_metrics", {}),
        "session_timing": cm_data.get("session_timing", {}),
    }
