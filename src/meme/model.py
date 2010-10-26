COLOR_PLAIN = ((0, 0, 0), (1, 1, 1))
COLOR_RED = ((1, 0, 0), (1, 0.9, 0.9))
COLOR_AMBER = ((0.8, 0.6, 0), (1, 0.9, 0.8))
COLOR_GREEN = ((0, 1, 0), (0.9, 1, 0.9))
COLOR_BLUE = ((0, 0, 1), (0.9, 0.9, 1))

class Model(object):
	def __init__(self, name):
		self._root = Node(name)
		self._current = self._root
		self._undo = []
		self._redo = []
		self._observers = []

	def do(self, cmd):
		self.undo.append(cmd)
		self.redo = []
		cmd.do(self)

	def undo(self):
		cmd = self._undo.pop()
		self._redo.append(cmd)
		cmd.undo(self)

	def redo(self):
		cmd = self._redo.pop()
		self._undo.append(cmd)
		cmd.do(self)

	def click(self, node):
		if node:
			print "Clicked: %s" % node.title
		else:
			print "Clicked away"
		old = self._current
		if node == old:
			return
		self._current = node
		for o in self._observers:
			o.on_node_select(self, node, old)

	def observe(self, observer):
		self._observers.append(observer)

	@property
	def root(self):
		return self._root
	
	@property
	def current(self):
		return self._current

	def append_child(self, node, child):
		node.append_child(child)
		for o in self._observers:
			o.on_node_add(self, child)

class Observer(object):
	def on_node_select(self, model, node, old):
		pass

	def on_node_change(self, model, node):
		pass

	def on_node_add(self, model, node):
		pass

	def on_node_remove(self, model, node):
		pass


class EditCommand(object):
	def __init__(self, new):
		self._new = new
		
	def do(self, model):
		self._old = model.current.title
		self._node = model.current
		self._node.title = self._new
		for o in model._observers:
			o.on_node_change(model, self._node)

	def undo(self, model):
		self._node.title = self._old
		for o in model._observers:
			o.on_node_change(model, self._node)


class ColorCommand(object):
	def __init__(self, new):
		self._new = new
		
	def do(self, model):
		self._old = model.current.color
		self._node = model.current
		self._node.color = self._new
		for o in model._observers:
			o.on_node_change(model, self._node)

	def undo(self, model):
		self._node.color = self._old
		for o in model._observers:
			o.on_node_change(model, self._node)


class Node(object):
	def __init__(self, title):
		self.title = title
		self.color = COLOR_PLAIN
		self._children = []
		self._parent = None
		self.open = True

	def child(self, n):
		return self._children[n]

	def append_child(self, c):
		self._children.append(c)
		c._parent = self

	def children(self):
		for c in self._children:
			yield c

	def count_children(self):
		return len(self._children)

	@property
	def parent(self):
		return self._parent

	def __str__(self):
		return "Node(%s)" % self.title

# vim:sw=4 ts=4
