import time

class Model(object):
	def __init__(self, name):
		self._root = Node(name)
		self._current = None
		self._undo = []
		self._redo = []
		self._observers = []

	def do(self, cmd):
		self._undo.append(cmd)
		self._redo = []
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

	def move(self, fn):
		if self._current:
			n = fn(self.current)
			if n:
				self.click(n)
		else:
			self.click(self._root)

	def observe(self, observer):
		self._observers.append(observer)

	@property
	def root(self):
		return self._root

	@property
	def current(self):
		return self._current

	@property
	def title(self):
		if self._current:
			return self._current.title
		else:
			return None

	def direct_append_child(self, node, child):
		a = time.time()
		node.append_child(child)
		for o in self._observers:
			o.on_node_add(self, child)
		print "Add took %fms" % ((time.time() - a) * 1000)


class Observer(object):
	def on_node_select(self, model, node, old):
		pass

	def on_node_change(self, model, node):
		pass

	def on_node_add(self, model, node):
		pass

	def on_node_remove(self, model, node):
		pass

class AddCommand(object):
	def __init__(self, parent, node):
		self._parent = parent
		self._node = node

	def do(self, model):
		model.direct_append_child(self._parent, self._node)
		model.click(self._node)
	
	def undo(self, model):
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
	def __init__(self, title = ""):
		self.title = title
		self.color = 0
		self._children = []
		self._parent = None
		self.open = True

	def child(self, n):
		if n < 0 or n >= len(self._children):
			return None
		else:
			return self._children[n]

	def append_child(self, c):
		self._children.append(c)
		c._parent = self

	def children(self):
		for c in self._children:
			yield c

	def count_children(self):
		return len(self._children)

	def find_sibling(self, d, depth = 0):
		p = self._parent
		if p:
			pos = 0
			for c in p._children:
				if c is self:
					if d < 0:
						if pos == 0:
							return p.find_sibling(-1, depth + 1)
						elif depth == 0:
							return p._children[pos - 1]
						else:
							return p._children[pos - 1].find_child(-1, depth - 1)
					elif d > 0:
						if pos == len(p._children) - 1:
							return p.find_sibling(1, depth + 1)
						elif depth == 0:
							return p._children[pos + 1]
						else:
							return p._children[pos + 1].find_child(1, depth - 1)
				pos += 1
		return None

	def find_child(self, d, depth):
		if self._children:
			if d < 0:
				c = self._children[-1]
			elif d > 0:
				c = self._children[0]
			if depth == 0:
				return c
			else:
				return c.find_child(d, depth - 1)
		else:
			return self.find_sibling(d, depth + 1)

	@property
	def parent(self):
		return self._parent

	def __str__(self):
		return "Node(%s)" % self.title

# vim:sw=4 ts=4
