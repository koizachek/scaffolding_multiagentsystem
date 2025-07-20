class CanvasController {
	constructor(cy, ctx) {
		this.ctx = ctx;
		this.cy  = cy;
	}
}

export class NodeCreationController extends CanvasController {
	constructor(cy, ctx) {
		super(cy, ctx);
		
		this.labelBox    = document.getElementById("labelInputBox");
		this.labelInput  = document.getElementById("labelInputText");
		this.labelSubmit = document.getElementById("labelInputSubmit");

		this.ghostNodeId  = null;
	}

	init() {
		this.cy.on('tap', 'node', (evt) => {
			const node = evt.target;
			if (this.ctx.nodeCreationStarted && this.ghostNodeId == node.id()) {
				this.deleteGhost();
				return;
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

			this.labelBox.style.left = `${containerRect.left + renderPos.x - 120}px`;
			this.labelBox.style.top  = `${containerRect.top  + renderPos.y - 80}px`;
			this.labelBox.style.display = 'block';

			this.labelInput.value = '';
			this.labelInput.focus();

			this.ghostNodeId = id;
			this.ctx.nodeCreationStarted = true;
			this.cy.autoungrabify(true);
		});

		this.labelSubmit.onclick = () => {
			const label = this.labelInput.value.trim();
			if (!label) {
				this.deleteGhost();
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
			this.finish();
		};
	}

	finish() {
		this.cy.autoungrabify(false);
		this.ctx.nodeCreationStarted = false;
		this.labelBox.style.display = 'none';
		this.ghostNodeId = null;
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
