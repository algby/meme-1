from model import Observer

class Layout(Observer):
	def __init__(self, model, style, renderer):
		self._model = model
		self._style = style
		self._renderer = renderer
		self._peers = {}
		model.observe(self)

		def init_peers(n):
			self._peers[n] = NodePeer(n, style, renderer, self._peers)
			for c in n.children():
				init_peers(c)

		init_peers(model.root)

		self._peers[model.root].reflow()
		renderer.resize(*self.size)
		self.render(0, 0, *self.size)

	def on_node_select(self, model, node, old):
		if old:
			self.render_node(old)
		if node:
			self.render_node(node)

	def on_node_add(self, model, node, pos):
		# Peer may already exist if we are re-adding a deleted node
		peer = self._peers.get(node)
		if not peer:
			peer = NodePeer(node, self._style, self._renderer, self._peers)
			self._peers[node] = peer

		osw, osh = self.size

		width = peer.total_width
		height = peer.total_height
		delta = height
		pnode = node.parent
		while pnode:
			ppeer = self._peers[pnode]
			old_height = ppeer.total_height
			ppeer.change_size(delta, width)
			width = ppeer.total_width
			height = ppeer.total_height
			delta = height - old_height
			pnode = pnode.parent

		posx, posy = peer.find_pos()

		self._renderer.ygap(width, height, posy, delta)
		self._renderer.viewport(*self.size)
		self.render(0, posy, width, max(delta - 1, self._style.dimy + self._style.pady))

	def on_node_delete(self, model, node, pos):
		peer = self._peers[node]

		osw, osh = self.size

		width = peer.total_width
		height = peer.total_height
		delta = -height
		pnode = node.parent
		while pnode:
			ppeer = self._peers[pnode]
			old_height = ppeer.total_height
			ppeer.change_size(delta, width)
			width = ppeer.total_width
			height = ppeer.total_height
			delta = height - old_height
			pnode = pnode.parent

		pnode = node.parent
		ppeer = self._peers[pnode]
		posx, posy = ppeer.find_pos()
		posx += ppeer.outer_width
		for i in xrange(0, pos):
			posy += self._peers[pnode.child(i)].total_height

		self._renderer.ygap(width, height - delta, posy - delta, delta)
		self._renderer.clear(posx, posy, peer.total_width, peer.total_height)
		self._renderer.viewport(*self.size)
		self.render(0, posy - 1, posx + peer.total_width, peer.total_height)

	def on_node_change(self, model, node):
		if node:
			peer = self._peers[node]
			ow = peer.outer_width
			peer.recalc_width()
			nw = peer.outer_width
			if ow != nw:
				tw = peer.total_width
				pnode = node.parent
				while pnode:
					ppeer = self._peers[pnode]
					ppeer.change_size(0, tw)
					tw = ppeer.total_width
					pnode = pnode.parent

				x, y = peer.find_pos()
				self._renderer.clear(x, y, ow, peer.total_height)
				self._renderer.xgap(x + ow, y, peer.child_width, peer.total_height, nw - ow)
				self._renderer.viewport(*self.size)

			self.render_node(node)

	def walk(self, left, top, width, height):
		def subtree(node, peer, x, y):
			if peer.hit_test_bounding(x, y, left, top, width, height):
				if x + peer.outer_width > left:
					yield (node, peer, x, y)
				cx = x + peer.outer_width
				cy = y
				for c in node.children():
					cp = self._peers[c]
					for r in subtree(c, cp, cx, cy):
						yield r
					cy += cp.total_height

		root = self._model.root
		return subtree(root, self._peers[root], self._style.marginx, self._style.marginy)

	def find(self, x, y):
		for node, peer, nx, ny in self.walk(x, y, 0, 0):
			if peer.hit_test_exact(nx, ny, x, y):
				return node
		return None

	def render(self, left, top, width, height):
		r = self._renderer
		c = self._model.current
		for node, peer, x, y in self.walk(left, top, width, height):
			r.draw_node(node, peer, x, y, node is c)

	def render_node(self, node):
		peer = self._peers[node]
		x, y = peer.find_pos()
		w = peer.outer_width - 1
		h = peer.total_height
		self._renderer.draw_node(node, peer, x, y, node is self._model.current)

	@property
	def size(self):
		peer = self._peers[self._model.root]
		return (peer.total_width + self._style.marginx * 2 - self._style.padx,
				peer.total_height + self._style.marginy * 2)


class NodePeer(object):
	def __init__(self, node, style, renderer, peers):
		self._node = node
		self._style = style
		self._renderer = renderer
		self._peers = peers

		self._inner_height = style.dimy
		self._outer_height = style.pady + style.dimy
		self._child_height = 0
		self._total_height = self._outer_height
		self._inner_width = 0
		self._outer_width = 0
		self._child_width = 0
		self._total_width = 0
		self.recalc_width()

	def recalc_width(self):
		self._inner_width = self._renderer.text_width(self._node.title) + self._style.innerpad * 2
		self._outer_width = self._inner_width + self._style.padx
		self._total_width = self._outer_width + self._child_width

	def hit_test_bounding(self, my_x, my_y, left, top, width, height):
		return (left < my_x + self._total_width
				and left + width >= my_x
				and top < my_y + self._total_height
				and top + height >= my_y)

	def hit_test_exact(self, my_x, my_y, p_x, p_y):
		mid = my_y + self._total_height / 2.0
		dim = self._inner_height / 2.0
		return (p_x >= my_x
				and p_x < my_x + self._inner_width
				and p_y >= mid - dim
				and p_y < mid + dim)

	def reflow(self):
		pos = 0
		tw = 0
		for c in self._node.children():
			p = self._peers[c]
			pos += p.reflow()
			tw = max(tw, p._total_width)

		self._child_height = pos
		self._total_height = max(self._outer_height, self._child_height)
		self._child_width = tw
		self._total_width = self._outer_width + tw
		return self._total_height

	def change_size(self, delta, width):
		self._child_height += delta
		self._total_height = max(self._outer_height, self._child_height)
		self._child_width = max(self._child_width, width)
		self._total_width = self._outer_width + self._child_width

	def find_pos(self):
		p = self._node._parent
		if p:
			pp = self._peers[p]
			px, py = pp.find_pos()
			pos = 0
			for cp in pp.children():
				if cp is self:
					break
				pos += cp.total_height
			return px + pp.outer_width, py + pos
		else:
			return self._style.marginx, self._style.marginy

	def children(self):
		for c in self._node.children():
			yield self._peers[c]

	@property
	def total_height(self):
		return self._total_height

	@property
	def inner_height(self):
		return self._inner_height

	@property
	def outer_height(self):
		return self._outer_height

	@property
	def total_width(self):
		return self._total_width

	@property
	def inner_width(self):
		return self._inner_width

	@property
	def outer_width(self):
		return self._outer_width

	@property
	def child_width(self):
		return self._child_width

# vim:sw=4 ts=4
