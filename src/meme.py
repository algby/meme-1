#!/usr/bin/env python

import math, sys, pygtk, gtk, cairo, time
pygtk.require('2.0')

from meme.model import *
from meme.renderer import *

class MemeGui(object):
	def __init__(self):
		self._renderer = None
		self._builder = gtk.Builder()
		self._builder.add_from_file("ui/meme.xml")
		self._builder.connect_signals(self)

		self._main_win = self._builder.get_object("main_win")

		self._canvas = self._builder.get_object("canvas")

		self._model = Model("MyMap")
		root = self._model._root
		for i in xrange(0, 5):
			root.append_child(Node("Node %s" % ("x" * i)))
		for i in xrange(0, 2):
			root.child(1).append_child(Node("Node %d" % i))
		for i in xrange(0, 7):
			root.child(4).append_child(Node("Node %d" % i))
		root.child(1).child(1).append_child(Node("Longer node"))

		self._renderer = None
		self._main_win.show()

	def on_main_win_destroy(self, widget, data = None):
		gtk.main_quit()

	def on_file_quit_activate(self, widget, data = None):
		gtk.main_quit()

	def on_help_about_activate(self, widget, data = None):
		self._about = self._builder.get_object("about_dialog")
		self._about.run()
		self._about.hide()

	def on_canvas_configure_event(self, widget, data = None):
		if self._model:
			x, y, w, h = widget.get_allocation()
			if self._renderer:
				self._renderer.expand_pixmap(w, h, True)
			else:
				pixmapper = lambda w, h: gtk.gdk.Pixmap(widget.window, w, h)
				self._renderer = Renderer(self._model, self._canvas, pixmapper, w, h)
		return True

	def on_canvas_expose_event(self, widget, data = None):
		if self._renderer:
			x, y, w, h = data.area
			gc = widget.get_style().fg_gc[gtk.STATE_NORMAL]
			widget.window.draw_drawable(gc, self._renderer._pixmap, x, y, x, y, w, h)
			return False

	def on_canvas_button_press_event(self, widget, data = None):
		node = self._renderer.find(data.x, data.y)
		self._model.click(node)
		if node:
			a = time.time()
			self._model.append_child(node, Node("New"))
			print "Add took %fms" % ((time.time() - a) * 1000)
			pass

if __name__ == "__main__":
	gui = MemeGui()
	
	while gtk.events_pending():
		gtk.main_iteration(False)

	i = [0]
	def idle():
		node = gui._model._root
		node = node.child(i[0] % 5)
		gui._model.click(node)
		a = time.time()
		gui._model.append_child(node, Node("X %d" % i[0]))
		print "Add took %fms" % ((time.time() - a) * 1000)
		i[0] += 1
		if i[0] == 100:
			return False
		return True

	gtk.timeout_add(50, idle)
	gtk.main()

# vim:sw=4 ts=4
