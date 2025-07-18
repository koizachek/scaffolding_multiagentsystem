let cy = cytoscape({
	container: document.getElementById('cy'),
	layout: { name: 'grid' },
	elements: [],
	style: [{
		selector: 'node',
		style: {
			'label': 'data(label)',
			'background-color': '#3498db',
			'color': '#fff',
			'text-valign': 'center',
			'text-halign': 'center',
			'border-width': 2,
			'border-color': 'transparent',
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
	
	cy.autoungrabify(mode === Modes.AddNode || mode == Modes.AddEdge);
	edgeSource = null;
};

Object.values(Modes).forEach(mode => 
	document.getElementById(mode + "Button").onclick = () => setMode(mode));

const labelBox    = document.getElementById("labelInputBox");
const labelInput  = document.getElementById("labelInputText");
const labelSubmit = document.getElementById("labelInputSubmit");

const nodeCreationManager = {
	started: false,
	nodePos: null,
	nodeId:  null,

	begin: function(pos, id) {
		this.started = true;
		this.nodePos = pos;
		this.nodeId  = id;

	},

	finish: function() {
		this.started = false;
		this.nodePos = null;
		this.nodeId  = null;
		labelBox.style.display = 'none';
	},

	removeNode: function() {
		if (cy.getElementById(this.nodeId).nonempty())
			cy.remove(cy.getElementById(this.nodeId));
	}
};

cy.on('tap', function(evt) {
	if (evt.target != cy || currentMode != Modes.AddNode) return;
	
	if (nodeCreationManager.started) {
		nodeCreationManager.removeNode();
		nodeCreationManager.finish();
	}

	const pos = evt.position;
	const renderPos = cy.renderer().projectIntoViewport(pos.x, pos.y);

	labelBox.style.left = `${renderPos[0]-100}px`;
	labelBox.style.top  = `${renderPos[1]+25}px`;
	labelBox.style.display = 'block';
	
	const id = 'node_' + Date.now();
	const label = '';
	cy.add({
		group: 'nodes',
		data: { id, label },
		position: pos
	});
	
	labelInput.value = '';
	labelInput.focus();
	
	nodeCreationManager.begin(pos, id);
});

document.getElementById('labelInputSubmit').onclick = () => {
	if (!nodeCreationManager.started) return;

	const label = labelInput.value.trim();
	if (!label || !nodeCreationManager.nodePos) {
		nodeCreationManager.removeNode();
		nodeCreationManager.finish();
		return;
	}
				
	const node = cy.getElementById(nodeCreationManager.nodeId);
	const size = Math.max(50, label.length * 10);
	node.style({'width': size, 'height': size});
	node.data({ id: nodeCreationManager.nodeId, label });
	nodeCreationManager.finish();
};

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


