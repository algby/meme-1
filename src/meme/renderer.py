import math, pango, cairo, random, time

from model import *

class GlobalStyle(object):
	def __init__(self):
		self.marginx = 20
		self.marginy = 20
		self.padx = 20
		self.pady = 10
		self.dimy = 20
		self.innerpad = 5

class NodePeer(object):
	def __init__(self, style, node, ctx, peers):
		self._style = style
		self._node = node
		self._peers = peers
		self._inner_height = style.dimy
		self._outer_height = style.pady + style.dimy
		self._child_height = 0
		self._total_height = self._outer_height
		self._inner_width = None
		self._outer_width = None

		self.make_layout(ctx)
		self._child_width = 0
		self._total_width = self._outer_width

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

	def make_layout(self, ctx):
		lo = ctx.create_layout()
		lo.set_font_description(pango.FontDescription("sans 8"))
		lo.set_text(self._node.title)
		tw, th = lo.get_pixel_size()
		self._inner_width = int(tw + self._style.innerpad * 2)
		self._outer_width = int(self._inner_width + self._style.padx)
		return lo

	def render(self, ctx, my_x, my_y, current):
		lo = self.make_layout(ctx)
		tw, th = lo.get_pixel_size()
		cy = my_y + self._total_height / 2.0
		dim = self._style.dimy / 2.0

		ctx.save()
		ctx.set_antialias(cairo.ANTIALIAS_NONE)
		ctx.rectangle(my_x + 1, cy - dim + 1, self._inner_width - 1, self._style.dimy - 1)
		ctx.set_source_rgb(*self._node.color[1])
		ctx.fill_preserve()
		ctx.set_line_width(1.0)
		if current:
			ctx.set_source_rgb(1, 0, 0)
		else:
			ctx.set_source_rgb(*self._node.color[0])
		ctx.stroke()
		
		ctx.move_to(my_x + self._style.innerpad, cy - dim + th / 3.0)
		ctx.show_layout(lo)
		ctx.new_path()
		ctx.restore()

#		ctx.save()
#		ctx.set_line_width(1.0)
#		if current:
#			ctx.set_source_rgb(0, 0, 1)
#		else:
#			ctx.set_source_rgb(0, 0.5, 0)
#		ctx.set_antialias(cairo.ANTIALIAS_NONE)
#		ctx.rectangle(my_x, my_y, self.total_width, self.total_height)
#		ctx.stroke()
#		ctx.restore()

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
			for c in p.children():
				if c == self._node:
					break
				cp = self._peers[c]
				pos += cp.total_height
			return px + pp.outer_width, py + pos
		else:
			return self._style.marginx, self._style.marginy

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

class Renderer(Observer):
	def __init__(self, model, canvas, pixmapper, w, h):
		self._model = model
		self._style = GlobalStyle()
		self._zoom = 1
		self._peers = {}
		self._canvas = canvas
		self._pixmapper = pixmapper
		self._pixmap = pixmapper(w, h)
		self._ctx = self._pixmap.cairo_create()
		model.observe(self)

		self._top_arc = self._make_arc("top")
		self._middle_arc = self._make_arc("middle")
		self._bottom_arc = self._make_arc("bottom")

		def init_peers(n):
			self._peers[n] = NodePeer(self._style, n, self._ctx, self._peers)
			for c in n.children():
				init_peers(c)

		init_peers(model.root)
		self._peers[model.root].reflow()
		self.render(0, 0, w, h, True)
		canvas.set_size_request(*self.size)

	def _make_arc(self, t):
		pix = self._pixmapper(self._style.padx, self._style.dimy)
		ctx = pix.cairo_create()

		ctx.set_source_rgb(0.8, 0.8, 0.8)
		ctx.paint()

		ctx.set_source_rgb(0, 0, 0)
		rx = self._style.padx / 2.0
		ry = (self._style.pady + self._style.dimy) / 4.0
		r = rx if rx < ry else ry
		px2 = self._style.padx / 2.0
		cy = self._style.dimy / 2.0
		
		if t == "top":
			ctx.arc(px2 + r, cy + r, r, math.pi, math.pi * 1.5)
			ctx.stroke()
			ctx.move_to(px2 + r, cy)
			ctx.line_to(self._style.padx, cy)
			ctx.stroke()
			ctx.move_to(px2, cy + r)
			ctx.line_to(px2, self._style.dimy)
			ctx.stroke()
		if t == "middle":
			ctx.arc(px2 - r, cy - r, r, 0, math.pi * 0.5)
			ctx.stroke()
			ctx.arc(px2 - r, cy + r, r, -math.pi * 0.5, 0)
			ctx.stroke()
			ctx.move_to(0, cy)
			ctx.rel_line_to(px2 - r, 0)
			ctx.stroke()
			ctx.move_to(px2, cy + r)
			ctx.line_to(px2, self._style.dimy)
			ctx.stroke()
			ctx.move_to(px2, cy - r)
			ctx.line_to(px2, 0)
			ctx.stroke()
		if t == "bottom":
			ctx.arc(px2 + r, cy - r, r, math.pi * 0.5, math.pi)
			ctx.stroke()
			ctx.move_to(px2 + r, cy)
			ctx.line_to(self._style.padx, cy)
			ctx.stroke()
			ctx.move_to(px2, cy - r)
			ctx.line_to(px2, 0)
			ctx.stroke()

		return pix

	def clear(self, left, top, width, height):
		print "Clear %d" % (width * height)
		ctx = self._ctx
		ctx.save()
		ctx.rectangle(left, top, width, height)
		ctx.clip()
		ctx.set_source_rgb(0.8, 0.8, 0.8)
		ctx.paint()
		ctx.restore()

	def render(self, left, top, width, height, clip):
		print "Render %d" % (width * height)
		ctx = self._ctx
		ctx.save()
		if clip:
			ctx.rectangle(left, top, width, height)
			ctx.clip()
			ctx.set_source_rgb(0.8, 0.8, 0.8)
			ctx.paint()

		def traverse(node, x, y):
			p = self._peers[node]
			if p.hit_test_bounding(x, y, left, top, width, height):
				if x + p.outer_width > left:
					if not clip:
						self.clear(x, y, p.outer_width, p.total_height)
					self.draw_node(ctx, node, x, y)
				pos = y
				nx = x + p.outer_width
				for c in node.children():
					cp = traverse(c, nx, pos)
					pos += cp.total_height
			return p
		
		traverse(self._model.root, 20, 20)
		ctx.restore()
		self._canvas.queue_draw_area(left, top, width, height)

	def on_node_select(self, model, node, old):
		if old:
			self.redraw_node(old)
		if node:
			self.redraw_node(node)

	def on_node_add(self, model, node):
		ctx = self._ctx
		osw, osh = self.size
		peer = NodePeer(self._style, node, ctx, self._peers)
		self._peers[node] = peer
		delta = peer.total_height
		width = peer.total_width

		pnode = node.parent
		while pnode:
			ppeer = self._peers[pnode]
			old_height = ppeer.total_height
			ppeer.change_size(delta, width)
			width = ppeer.total_width
			delta = ppeer.total_height - old_height
			pnode = pnode.parent

		posx, posy = peer.find_pos()
		sw, sh = self.size
		self.expand_pixmap(sw, sh, False)
		self._pixmap.draw_drawable(self._pixmap.new_gc(), self._pixmap, 0, posy, 0, posy + delta, sw, osh - posy)
		ctx = self._ctx # It may have changed
		ctx.rectangle(0, posy, sw, max(delta - 1, 0))
		ctx.set_source_rgb(0.8, 0.8, 0.8)
		ctx.fill()
		self.render(0, posy, sw, max(delta - 1, self._style.dimy + self._style.pady), False)
		self._canvas.set_size_request(*self.size)

	def on_node_change(self, model, node):
		pass

	def redraw_node(self, node):
		peer = self._peers[node]
		x, y = peer.find_pos()
		w = peer.outer_width - 1
		h = peer.total_height
		self.clear(x, y, w, h)
		self.draw_node(self._ctx, node, x, y)
		self._canvas.queue_draw_area(x, y, w, h)

	def draw_node(self, ctx, node, x, y):
		#ctx.scale(self._zoom, self._zoom)
		ctx.set_line_width(2.0)
		gc = self._pixmap.new_gc()

		peer = self._peers[node]
		peer.render(ctx, x, y, node == self._model.current)

		n = node.count_children()
		if n == 0:
			return

		ctx.set_source_rgb(0, 0, 0)

		height = peer.total_height
		cy = y + height / 2.0
		dimx = peer.inner_width

		rx = self._style.padx / 2.0
		ry = (self._style.pady + self._style.dimy) / 4.0
		r = rx if rx < ry else ry
		px2 = self._style.padx / 2.0
		sp = self._style.dimy + self._style.pady

		if n == 1:
			ctx.move_to(x + dimx, cy)
			ctx.rel_line_to(px2 - r, 0)
			ctx.stroke()
		else:
			self._pixmap.draw_drawable(gc, self._middle_arc, 0, 0, x + dimx, int(cy - self._style.dimy / 2.0), *self._middle_arc.get_size())

		pos = 0
		i = 0
		topline = None
		bottomline = None
		for c in node.children():
			height = self._peers[c].total_height

			ccx = x + dimx + self._style.padx
			ccy = y + pos + height / 2.0
			cty = int(ccy - self._style.dimy / 2.0)

			if i == 0:
				topline = ccy - cy + r * 2.0
			elif i == n - 1:
				bottomline = ccy - cy - r * 2.0

			if ccy < cy:
				self._pixmap.draw_drawable(gc, self._top_arc, 0, 0, x + dimx, cty, *self._top_arc.get_size())
			elif ccy > cy:
				self._pixmap.draw_drawable(gc, self._bottom_arc, 0, 0, x + dimx, cty, *self._bottom_arc.get_size())
			else:
				ctx.move_to(x + dimx + px2 - r, cy)
				ctx.line_to(x + dimx + self._style.padx, cy)
				ctx.stroke()

			pos += height
			i += 1

		if n > 1:
			ctx.move_to(x + dimx + px2, cy - r)
			ctx.rel_line_to(0, topline)
			ctx.stroke()
			ctx.move_to(x + dimx + px2, cy + r)
			ctx.rel_line_to(0, bottomline)
			ctx.stroke()

	def find(self, x, y):
		found = [None]
		def traverse(node, nx, ny):
			p = self._peers[node]
			if p.hit_test_bounding(nx, ny, x, y, 0, 0):
				if p.hit_test_exact(nx, ny, x, y):
					found[0] = node
					return None
				qx = nx + p.outer_width
				pos = ny
				for c in node.children():
					p = traverse(c, qx, pos)
					if found[0]:
						return None
					pos += p.total_height
			return p

		traverse(self._model.root, self._style.marginx, self._style.marginy)
		return found[0]

	@property
	def size(self):
		peer = self._peers[self._model.root]
		return peer.total_width + self._style.marginx * 2 - self._style.padx, peer.total_height + self._style.marginy * 2

	def expand_pixmap(self, w, h, render):
		# Round up so we don't have to do this so often
		w = (w / 200 + 1) * 200
		h = (h / 200 + 1) * 200

		old = self._pixmap
		ow, oh = old.get_size()

		if w > ow or h > oh:
			self._pixmap = self._pixmapper(max(ow, w), max(oh, h))
			self._ctx = self._pixmap.cairo_create()
			self._pixmap.draw_drawable(self._pixmap.new_gc(), old, 0, 0, 0, 0, ow, oh)
			if render:
				if w > ow:
					self.render(ow, 0, w - ow, oh, True)
				if h > oh:
					self.render(0, oh, max(ow, w), h - oh, True)
			else:
				if w > ow:
					self.clear(ow, 0, w - ow, oh)
				if h > oh:
					self.clear(0, oh, max(ow, w), h - oh)
		
# vim:sw=4 ts=4
