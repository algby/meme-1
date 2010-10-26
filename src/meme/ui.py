import math, sys, pygtk, gtk, cairo, time
pygtk.require('2.0')

from meme.layout import *
from meme.model import *
from meme.renderer import *
from meme.style import *

class MemeGui(object):
	def __init__(self):
		self._layout = None
		self._renderer = None
		self._model = Model("MyMap")

		self._builder = gtk.Builder()
		self._builder.add_from_file("ui/meme.xml")
		self._builder.connect_signals(self)

		self._main_win = self._builder.get_object("main_win")
		self._canvas = self._builder.get_object("canvas")

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
		x, y, w, h = widget.get_allocation()
		if self._renderer:
			self._renderer.resize(w, h)
		else:
			style = GlobalStyle()
			self._renderer = Renderer(style, self._canvas, widget.window, w, h)
			self._layout = Layout(self._model, style, self._renderer)
		return True

	def on_canvas_expose_event(self, widget, data = None):
		if self._renderer:
			self._renderer.redraw(*data.area)
			return False

	def on_canvas_button_press_event(self, widget, data = None):
		node = self._layout.find(data.x, data.y)
		self._model.click(node)
		widget.grab_focus()
		if node:
			a = time.time()
			self._model.append_child(node, Node("New"))
			print "Add took %fms" % ((time.time() - a) * 1000)
			pass

# vim:sw=4 ts=4
