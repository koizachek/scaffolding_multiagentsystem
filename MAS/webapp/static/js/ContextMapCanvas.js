import { 
	NodeCreationController, 
	NodeOptionsBoxController } 
from './CanvasControllers.js';

const cy = cytoscape({
	container: document.getElementById('cy'),
	layout: { name: 'grid' },
	elements: [],
	zoomingEnabled: true,
	style: [{
		selector: 'node',
		style: {
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
			'height': 50
		}
	}, {
		selector: 'edge',
		style: {
			'label': 'data(label)',
			'curve-style': 'bezier',
			'target-arrow-shape': 'triangle',
			'target-arrow-color': '#ccc',
			'line-color': '#ccc',
			'width': 3
		}
	}]});

cy.style()
	.selector('.selectedNode')
	.style({
		'background-color': 'green',
		'border-color': 'orange',
		'border-width': 2
	}).update();

let ctx = {
	nodeCreationStarted: false	
};

const nodeOptionsBox = new NodeOptionsBoxController(cy, ctx).init();
const nodeCreation   = new NodeCreationController(cy, ctx).init();

const Modes = { AddNode: "addNode", AddEdge: "addEdge", Move: "moveMode" };

let selectedButton = document.getElementById(Modes.Move + "Button");
let currentMode = Modes.Move;

let edgeSource = null;

const setMode = (mode) => {
	console.log("mode change from " + currentMode + " to " + mode);
	selectedButton.classList.remove('active');
	selectedButton = document.getElementById(mode + 'Button');
	
	selectedButton.classList.add('active');
	currentMode = mode;
	
	edgeSource = null;
};

Object.values(Modes).forEach(mode => 
	document.getElementById(mode + "Button").onclick = () => setMode(mode));

cy.on('tap', 'node', function(evt) {
	if (currentMode != Modes.AddEdge) return;
	
	const node = evt.target;
	if (!edgeSource) {
		edgeSource = node;
		edgeSource.addClass('selectedNode');
		return;
	}

	if (edgeSource.id() == node.id()) {
		edgeSource.removeClass('selectedNode');
		edgeSource = null;
		return;
	}

	const label = prompt('Enter edge label:');
	cy.add({
		group: 'edges',
		data: {
			id: 'edge_' + Date.now(),
			source: edgeSource.id(),
			target: node.id(),
			label
		}
	});
	edgeSource.removeClass('selectedNode');
	edgeSource = null;
});


