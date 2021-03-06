# Meme: a fast mind-mapping tool
# (c) 2010 Jamie Webb - MIT license

import math, sys, pygtk, gtk, pango, cairo, random, time

class Renderer(object):
	def __init__(self, style, canvas, window, w, h):
		self._style = style
		self._canvas = canvas
		self._window = window
		self._zoom = 1
		self._pixmap = self._make_pixmap(w, h)
		self._ctx = self._pixmap.cairo_create()
		self.clear(0, 0, w, h)

		self._top_arc = self._make_arc("top")
		self._middle_arc = self._make_arc("middle")
		self._bottom_arc = self._make_arc("bottom")

	def _make_pixmap(self, w, h):
		return gtk.gdk.Pixmap(self._window, w, h)

	def _make_arc(self, t):
		style = self._style
		pix = self._make_pixmap(self._style.padx, self._style.dimy)
		ctx = pix.cairo_create()

		ctx.set_source_rgb(*style.background)
		ctx.paint()

		ctx.set_source_rgb(*style.lines)
		ctx.set_line_width(style.line_width)

		rx = style.padx / 2.0
		ry = (style.pady + style.dimy) / 4.0
		r = rx if rx < ry else ry
		px2 = style.padx / 2.0
		cy = style.dimy / 2.0

		if t == "top":
			ctx.arc(px2 + r, cy + r, r, math.pi, math.pi * 1.5)
			ctx.stroke()
			ctx.move_to(px2 + r, cy)
			ctx.line_to(style.padx, cy)
			ctx.stroke()
			ctx.move_to(px2, cy + r)
			ctx.line_to(px2, style.dimy)
			ctx.stroke()
		if t == "middle":
			ctx.arc(px2 - r, cy - r, r, 0, math.pi * 0.5)
			ctx.stroke()
			ctx.arc(px2 - r, cy + r, r, -math.pi * 0.5, 0)
			ctx.stroke()
			ctx.move_to(0, cy)
			ctx.rel_line_to(px2 - r, 0)
			ctx.stroke()
		if t == "bottom":
			ctx.arc(px2 + r, cy - r, r, math.pi * 0.5, math.pi)
			ctx.stroke()
			ctx.move_to(px2 + r, cy)
			ctx.line_to(style.padx, cy)
			ctx.stroke()
			ctx.move_to(px2, cy - r)
			ctx.line_to(px2, 0)
			ctx.stroke()

		return pix

	def clear_all(self, color = None):
		ctx = self._ctx
		ctx.set_source_rgb(*(color or self._style.background))
		ctx.paint()
		w, h = self._pixmap.get_size()
		self.redraw(0, 0, w, h)

	def clear(self, left, top, width, height, color = None):
		ctx = self._ctx
		ctx.set_source_rgb(*(color or self._style.background))
		ctx.rectangle(left, top, width, height)
		ctx.fill()

	def xgap(self, left, top, width, height, delta):
		self.resize(left + width + delta, 0)
		self._pixmap.draw_drawable(self._pixmap.new_gc(), self._pixmap, left, top, left + delta, top, width, height)
		if delta < 0:
			self.clear(left + width + delta, top, abs(delta), height)

	def ygap(self, width, height, top, delta):
		width += self._style.marginx * 2
		height += self._style.marginy
		self.resize(width, height)
		self._pixmap.draw_drawable(self._pixmap.new_gc(), self._pixmap, 0, top, 0, top + delta, width, height - delta)
		if delta > 0:
			self.clear(0, top, width, delta)
		elif delta < 0:
			self.clear(0, height + delta, width, -delta)

	def viewport(self, width, height):
		self._canvas.set_size_request(width + self._style.marginx * 2 - self._style.padx,
				height + self._style.marginy * 2)

	def draw_label(self, node, peer, x, y, cy, dimy2, style):
		lo = self._make_layout(node.title)
		tw, th = lo.get_pixel_size()
		ctx.set_antialias(cairo.ANTIALIAS_NONE)
		ctx.rectangle(x + 1, cy - dimy2 + 1, peer.inner_width - 1, style.dimy - 1)
		if current:
			ctx.set_source_rgb(1, 1, 0)
		else:
			ctx.set_source_rgb(*style.colors[node.color][1])
		ctx.fill_preserve()
		ctx.set_line_width(1.0)
		ctx.set_source_rgb(*style.colors[node.color][0])
		ctx.stroke()

		ctx.move_to(x + style.innerpad, cy - dimy2 + th / 3.0)
		ctx.show_layout(lo)

	def draw_label_alt(self, ctx, node, peer, x, y, cy, dimy2, style, current):
		lo = self._make_layout(node.title)
		tw, th = lo.get_pixel_size()
		if current:
			ctx.set_antialias(cairo.ANTIALIAS_NONE)
			ctx.rectangle(x + 1, cy - dimy2 + 1, peer.inner_width - 1, style.dimy - 1)
			ctx.set_source_rgb(*style.colors[0][1])
			ctx.fill_preserve()
			ctx.set_line_width(1.0)
			ctx.set_source_rgb(*style.colors[0][0])
			ctx.stroke()

		ctx.set_source_rgb(*style.colors[node.color][0])
		ctx.move_to(x + style.innerpad, cy - dimy2 + th / 3.0)
		ctx.show_layout(lo)

	def draw_node(self, node, peer, x, y, current):
		ctx = self._ctx
		style = self._style
		gc = self._pixmap.new_gc()

		#ctx.scale(self._zoom, self._zoom)

		width = peer.outer_width
		height = peer.total_height
		cy = int(y + height / 2.0 + 0.5)
		dimy2 = int(style.dimy / 2.0 + 0.5)
		dimx = peer.inner_width

		self.clear(x, y, width, height)
		self._canvas.queue_draw_area(x, y, width, height)

		ctx.save()
		self.draw_label_alt(ctx, node, peer, x, y, cy, dimy2, style, current)
		ctx.restore()

		n = node.count_children()
		if n == 0:
			return

		ctx.set_line_width(style.line_width)
		ctx.set_source_rgb(*style.lines)

		rx = style.padx / 2.0
		sp = style.dimy + style.pady
		ry = sp / 4.0
		r = rx if rx < ry else ry
		px2 = style.padx / 2.0

		pos = 0
		i = 0
		topline = None
		bottomline = None
		hline = False
		for cp in peer.children():
			height = cp.total_height

			ccx = x + dimx + style.padx
			ccy = int(y + pos + height / 2.0 + 0.5)

			if i == 0:
				topline = int(ccy - cy + 0.5)
			elif i == n - 1:
				bottomline = int(ccy - cy + 0.5)

			if ccy < cy:
				if i != 0:
					self._pixmap.draw_drawable(gc, self._top_arc, 0, int(dimy2 - r + 0.5), x + dimx, int(ccy - r + 0.5), style.padx, int(r * 2.0 - 0.5))
			elif ccy > cy:
				if i != n - 1:
					self._pixmap.draw_drawable(gc, self._bottom_arc, 0, int(dimy2 - r + 0.5), x + dimx, int(ccy - r + 0.5), style.padx, int(r * 2.0 - 0.5))
			else:
				hline = True

			pos += height
			i += 1

		if n > 1:
			ctx.move_to(x + dimx + px2, cy)
			ctx.rel_line_to(0, topline)
			ctx.stroke()
			ctx.move_to(x + dimx + px2, cy)
			ctx.rel_line_to(0, bottomline)
			ctx.stroke()

		if n == 1:
			ctx.move_to(x + dimx, cy)
			ctx.rel_line_to(px2 - r, 0)
			ctx.stroke()

		i = 0
		pos = 0
		for cp in peer.children():
			height = cp.total_height

			ccx = x + dimx + style.padx
			ccy = int(y + pos + height / 2.0 + 0.5)

			if i == 0 and ccy < cy:
				self._pixmap.draw_drawable(gc, self._top_arc, 0, int(dimy2 - r + 0.5), x + dimx, int(ccy - r + 0.5), style.padx, int(r * 2.0 - 0.5))
			elif i == n - 1 and ccy > cy:
				self._pixmap.draw_drawable(gc, self._bottom_arc, 0, int(dimy2 - r + 0.5), x + dimx, int(ccy - r + 0.5), style.padx, int(r * 2.0 - 0.5))

			pos += height
			i += 1

		if n != 1:
			self._pixmap.draw_drawable(gc, self._middle_arc, 0,
					int(dimy2 - r + 0.5), x + dimx, int(cy - r + 0.5),
					style.padx, int(r * 2.0 - 0.5))

		if hline:
				ctx.move_to(x + dimx + px2 - r, cy)
				ctx.line_to(x + dimx + style.padx, cy)
				ctx.stroke()

	def _make_layout(self, title):
		lo = self._ctx.create_layout()
		lo.set_font_description(pango.FontDescription(self._style.font))
		lo.set_text(title)
		return lo

	def text_width(self, title):
		lo = self._make_layout(title)
		tw, th = lo.get_pixel_size()
		return tw

	def resize(self, w, h):
		# Round up so we don't have to do this so often
		w = (w / 200 + 1) * 200
		h = (h / 200 + 1) * 200

		old = self._pixmap
		ow, oh = old.get_size()

		if w > ow or h > oh:
			self._pixmap = self._make_pixmap(max(ow, w), max(oh, h))
			self._ctx = self._pixmap.cairo_create()
			self._pixmap.draw_drawable(self._pixmap.new_gc(), old, 0, 0, 0, 0, ow, oh)
			if w > ow:
				self.clear(ow, 0, w - ow, oh)
			if h > oh:
				self.clear(0, oh, max(ow, w), h - oh)

	def redraw(self, left, top, width, height):
		gc = self._pixmap.new_gc()
		self._window.draw_drawable(gc, self._pixmap, left, top, left, top, width, height)

# vim:sw=4 ts=4
