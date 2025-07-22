const nameInputBox =  {
	box:          document.getElementById("labelInputBox"),
	input:        document.getElementById("labelInputText"),
	submitButton: document.getElementById("labelInputSubmit"),
	
	position: function(posX, posY) {	
			nameInputBox.box.style.left = `${posX}px`;
			nameInputBox.box.style.top  = `${posY}px`;
			nameInputBox.box.style.display = 'block';	
	},

	focus: function() {	
		this.input.value = '';
		this.input.focus();
	},

	hide: function() {
		this.box.style.display = 'none';
	},

	getValue: function() {
		return this.input.value.trim();
	}
};

class CanvasController {
	constructor(cy, ctx) {
		this.ctx = ctx;
		this.cy  = cy;
	}
}

export class EdgeCreationController extends CanvasController {
	constructor(cy, ctx) {
		super(cy, ctx);
		
		this.ghostNodeId = 'edge_ghost';
	}

	init() {
		this.cy.on('taphold', 'node', (evt) => {
			if (this.ctx.nodeCreationStarted) return;
			
			const edgeStart = evt.target;

			this.cy.add({
				group: 'nodes',
				data: { id: this.ghostNodeId },
				style: {
					'background-color': 'transparent'
				},
				grabbable: false,
				selectable: false
			});
			

			this.ctx.edgeCreationStarted = true;
		});
	}
}

export class NodeCreationController extends CanvasController {
	constructor(cy, ctx) {
		super(cy, ctx);
		this.ghostNodeId = null;
	}

	init() {
		this.cy.on('tap', 'node', (evt) => {
			const node = evt.target;
			if (this.ctx.nodeCreationStarted && this.ghostNodeId == node.id()) {
				this.deleteGhost();
				this.finish();
			}
		});

		this.cy.on('tap', (evt) => {
			if (evt.target != this.cy) return;
			if (this.ctx.nodeCreationStarted) this.deleteGhost();

			const pos = evt.position;
			
			const id = 'node_' + Date.now();
			

			this.cy.add({
				group: 'nodes',
				data: { id, label: ''},
				position: pos
			});
			
			const renderPos = this.cy.getElementById(id).renderedPosition();
			const containerRect = this.cy.container().getBoundingClientRect();

			nameInputBox.position(containerRect.left + renderPos.x - 12,
					      containerRect.top  + renderPos.y - 80);
			nameInputBox.focus();

			this.ghostNodeId = id;
			this.ctx.nodeCreationStarted = true;
			this.cy.autoungrabify(true);
		});

		nameInputBox.submitButton.onclick = () => {
			const label = nameInputBox.getValue();
			if (!label) {
				this.deleteGhost();
				this.finish();
				return;
			}
						
			const node = this.cy.getElementById(this.ghostNodeId);
			const size = Math.max(50, label.length * 10);
			node.style({'width': size, 'height': size});
			node.data({ id: this.ghostNodeId, label: label});
			
			this.finish();
		};

		return this;
	}

	deleteGhost() {
		if (this.cy.getElementById(this.ghostNodeId).nonempty()) {
			this.cy.remove(this.cy.getElementById(this.ghostNodeId));
		};
	}

	finish() {
		this.cy.autoungrabify(false);
		this.ctx.nodeCreationStarted = false;
		this.ghostNodeId = null;

		nameInputBox.hide();
	}

	
}

export class NodeOptionsBoxController extends CanvasController {
	constructor(cy, ctx) {
		super(cy, ctx);

		this.box = document.getElementById("nodeOptionsBox");
		this.editButton     = document.getElementById("nodeOptionEdit");
		this.deleteButton   = document.getElementById("nodeOptionDelete");
		this.selectedNodeId = null;
	}
	
	init() {
		this.cy.on('mouseover', 'node', (evt) => { if (!this.ctx.nodeCreationStarted) this.show(evt.target); });
		this.cy.on('mouseout',  'node', (evt) => this.hide());

		this.deleteButton.onclick = () => {
		if (this.cy.getElementById(this.selectedNodeId).nonempty()) {
			this.cy.remove(this.cy.getElementById(this.selectedNodeId));
			this.hide();
		}};

		return this;
	}

	show(node) {
		this.selectedNodeId = node.id();
		const renderPos = node.renderedPosition();
		const offsetX   = node.width()/2 - 5;
		const offsetY   = node.width()/2 + 5;
		const containerRect = this.cy.container().getBoundingClientRect();
		
		const pageX = containerRect.left + renderPos.x + offsetX;
		const pageY = containerRect.top  + renderPos.y - offsetY;

		this.box.style.left = `${pageX}px`;
		this.box.style.top  = `${pageY}px`;
		this.box.style.display = 'flex';
	}

	hide() {
		this.selectedNodeId = null;
		this.box.style.display = 'none';
	}
}
