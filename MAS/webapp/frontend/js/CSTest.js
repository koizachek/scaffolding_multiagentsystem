import { Streamlit } from "streamlit-component-lib";
import cytoscape from "cytoscape";


function waitForContainerInitialization(callback) {
	const cydiv = document.getElementById('cy');

	if (cydiv && cydiv.offsetWidth > 0) {
		callback(cydiv);
	} else {
		setTimeout(() => waitForContainerInitialization(callback), 100);
	}
}

function initializeCytoscape(container) {
	const cy = cytoscape({
	    container: container,
	    elements: [
	      { data: { id: "a", label: "Node A" } },
	      { data: { id: "b", label: "Node B" } },
	      { data: { source: "a", target: "b", label: "A to B" } },
	    ],
	    layout: { name: "grid" },
	    style: [
	      { selector: "node", style: { label: "data(label)", "background-color": "#0074D9" } },
	      { selector: "edge", style: { label: "data(label)", "line-color": "#ccc" } },
	    ],
	  });

	  Streamlit.setComponentReady();
	  Streamlit.setFrameHeight();
}

window.addEventListener("DOMContentLoaded", () =>
	waitForContainerInitialization((container) => initializeCytoscape(container)));
