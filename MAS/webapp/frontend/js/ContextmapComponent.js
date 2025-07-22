import { Streamlit, RenderData } from "streamlit-component-lib";
import cytoscape from 'cytoscape';
import { NodeCreationController, NodeOptionsBoxController } from './CanvasControllers.js';

let cy = null;
let ctx = {
	nodeCreationStarted: false	
};

function initCytoscape() {
	const container = document.getElementById('cy');
	if (!container) {
		console.error("Container #cy was not found!");
		return;
	}

	cy = cytoscape({
		container: document.getElementById('cy'),
		layout: { name: 'grid' },
		elements: [],
		zoomingEnabled: true,
		style: [
		{ selector: 'node', style: {
			'label': 'data(label)',
			'background-color': '#647CBF',
			'font-size': '16px',              
			'font-family': 'Comic Sans MS',           
			'color': '#FBF9F9',               
			'text-outline-color': '#000000',  
			'text-outline-width': 3,
			'text-valign': 'center',
			'text-halign': 'center',
			'border-width': 3,
			'border-color': '#392E8F',
			'width': 50,
			'height': 50 }},
			
		{ selector: 'edge', style: {
			'label': 'data(label)',
			'curve-style': 'bezier',
			'target-arrow-shape': 'triangle',
			'target-arrow-color': '#ccc',
			'line-color': '#ccc',
			'width': 3 }},

		{ selector: '.selectedNode', style: {
			'background-color': 'green',
			'border-color': 'orange',
			'border-width': 2 }}
	]});

	const nodeOptionsBox = new NodeOptionsBoxController(cy, ctx).init();
	const nodeCreation   = new NodeCreationController(cy, ctx).init();
}

function onRender(event) {
	if (!cy) {
		initCytoscape();
	}
};

Streamlit.events.addEventListener(Streamlit.RENDER_EVENT, onRender);
Streamlit.setComponentReady();
Streamlit.setFrameHeight();
