import math, sys, pygtk, gtk, cairo, time
pygtk.require('2.0')

from meme.layout import Layout
from meme.model import *
from meme.renderer import Renderer
from meme.style import GlobalStyle

class MemeGui(Observer):
	def __init__(self):
		self._layout = None
		self._renderer = None
		self._model = Model("MyMap")
		self._model.observe(self)

		self._builder = gtk.Builder()
		self._builder.add_from_file("ui/meme.xml")
		self._builder.connect_signals(self)

		self._main_win = self._builder.get_object("main_win")
		self._canvas = self._builder.get_object("canvas")
		self._text = self._builder.get_object("text")
		self._undo = self._builder.get_object("undo_action")
		self._redo = self._builder.get_object("redo_action")

		self._main_win.show()
		self._canvas.grab_focus()

		def on_return(m):
			n = Node()
			sib = m.current
			if not sib or not sib.parent:
				return
			m.do(AddCommand(sib.parent, n, sib.index + 1))
			self._text.grab_focus()
			self._text.set_text("")

		def on_tab(m):
			n = Node()
			m.do(AddCommand(m.current or m.root, n))
			self._text.grab_focus()
			self._text.set_text("")

		def on_delete(m):
			n = self._model.current
			if n and n.parent:
				m.do(DeleteCommand(n))

		self._key_dispatch = {
			gtk.keysyms.Return: on_return,
			gtk.keysyms.Tab: on_tab,
			gtk.keysyms.Left: lambda m: m.move(lambda n: n.parent),
			gtk.keysyms.Right: lambda m: m.move(lambda n: n.child(0)),
			gtk.keysyms.Up: lambda m: m.move(lambda n: n.find_sibling(-1)),
			gtk.keysyms.Down: lambda m: m.move(lambda n: n.find_sibling(1)),
			gtk.keysyms.F4: lambda m: m.do(m.current and ColorCommand(m.current, 0)),
			gtk.keysyms.F5: lambda m: m.do(m.current and ColorCommand(m.current, 1)),
			gtk.keysyms.F6: lambda m: m.do(m.current and ColorCommand(m.current, 2)),
			gtk.keysyms.F7: lambda m: m.do(m.current and ColorCommand(m.current, 3)),
			gtk.keysyms.F8: lambda m: m.do(m.current and ColorCommand(m.current, 4)),
			gtk.keysyms.Insert: lambda m: self._text.grab_focus(),
			gtk.keysyms.Escape: lambda m: m.click(m.root),
			gtk.keysyms.Delete: on_delete
		}

		self._update_tools()

	def _update_tools(self):
		print self._model.has_undo
		self._undo.set_sensitive(self._model.has_undo)
		self._redo.set_sensitive(self._model.has_redo)

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
		widget.grab_focus()
		node = self._layout.find(data.x, data.y)
		self._model.click(node)

	def on_canvas_key_press_event(self, widget, data = None):
		k = data.keyval
		model = self._model
		if k == gtk.keysyms.space:
			model.toggle_expand()
		elif k < 255:
			if not model.current:
				model.new_child()
			self._text.grab_focus()
			self._text.set_text(chr(k))
			self._text.set_position(1)
		elif k in self._key_dispatch:
			self._key_dispatch[k](model)
		else:
			print "No binding for %d / %s" % (k, data)
		return True

	def on_text_key_press_event(self, widget, data = None):
		if data.keyval == gtk.keysyms.Return:
			self._canvas.grab_focus()
		elif data.keyval == gtk.keysyms.Escape:
			widget.set_text(self._model.title or "")
			self._canvas.grab_focus()
		elif data.keyval in [gtk.keysyms.Up, gtk.keysyms.Down]:
			self._canvas.grab_focus()
			self.on_canvas_key_press_event(self._canvas, data)

	def on_text_focus_out_event(self, widget, data = None):
		if self._model.current:
			self._model.do(EditCommand(self._model.current, widget.get_text()))
			widget.set_text(self._model.title or "")

	def on_undo_action_activate(self, widget, data = None):
		self._model.undo()

	def on_redo_action_activate(self, widget, data = None):
		self._model.redo()

	def on_node_select(self, model, node, old):
		self._text.set_text(node.title if node else "")
		self._update_tools()

	def on_node_change(self, model, node):
		self._update_tools()

	def on_node_add(self, model, node, pos):
		self._update_tools()

	def on_node_delete(self, model, node, pos):
		self._update_tools()

# vim:sw=4 ts=4
