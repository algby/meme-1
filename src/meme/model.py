import time

class Model(object):
	def __init__(self, root = None):
		if root:
			self._root = root
			self._clean = 0
		else:
			self._root = Node("Meme")
			self._clean = -1
		self._current = None
		self._undo = []
		self._redo = []
		self._observers = []

	def do(self, cmd):
		if cmd:
			if len(self._undo) < self._clean:
				self._clean = -1
			self._undo.append(cmd)
			self._redo = []
			cmd.do(self)

	def undo(self):
		if self._undo:
			cmd = self._undo.pop()
			self._redo.append(cmd)
			cmd.undo(self)

	def redo(self):
		if self._redo:
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

	def mark_clean(self):
		self._clean = len(self._undo)

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

	@property
	def has_undo(self):
		return len(self._undo) > 0

	@property
	def has_redo(self):
		return len(self._redo) > 0

	@property
	def is_clean(self):
		return len(self._undo) == self._clean

	def direct_add_child(self, node, child, pos = None):
		a = time.time()
		node.add_child(child, pos)
		for o in self._observers:
			o.on_node_add(self, child, pos)
		print "Add took %fms" % ((time.time() - a) * 1000)


class Observer(object):
	def on_node_select(self, model, node, old):
		pass

	def on_node_change(self, model, node):
		pass

	def on_node_add(self, model, node, pos):
		pass

	def on_node_delete(self, model, node, pos):
		pass


class AddCommand(object):
	def __init__(self, parent, node, pos = None):
		self._parent = parent
		self._node = node
		self._pos = pos

	def do(self, model):
		model.direct_add_child(self._parent, self._node, self._pos)
		self._pos = self._node.index
		model.click(self._node)
	
	def undo(self, model):
		pos = self._pos
		model.click(None)
		self._node.delete()
		for o in model._observers:
			o.on_node_delete(model, self._node, pos)
		p = self._node.parent
		n = p.count_children()
		if n > pos:
			model.click(p.child(pos))
		elif n > 0:
			model.click(p.child(pos - 1))
		else:
			model.click(p)


class DeleteCommand(object):
	def __init__(self, node):
		self._node = node

	def do(self, model):
		model.click(None)
		pos = self._node.index
		self._pos = pos
		self._node.delete()
		for o in model._observers:
			o.on_node_delete(model, self._node, pos)
		p = self._node.parent
		n = p.count_children()
		if n > pos:
			model.click(p.child(pos))
		elif n > 0:
			model.click(p.child(pos - 1))
		else:
			model.click(p)
	
	def undo(self, model):
		model.direct_add_child(self._node._parent, self._node, self._pos)
		model.click(self._node)


class EditCommand(object):
	def __init__(self, node, new):
		self._node = node
		self._new = new

	def do(self, model):
		self._old = self._node.title
		self._node.title = self._new
		for o in model._observers:
			o.on_node_change(model, self._node)

	def undo(self, model):
		self._node.title = self._old
		for o in model._observers:
			o.on_node_change(model, self._node)


class ColorCommand(object):
	def __init__(self, node, new):
		self._node = node
		self._new = new

	def do(self, model):
		self._old = self._node.color
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

	def add_child(self, c, pos = None):
		if pos is None:
			self._children.append(c)
		else:
			self._children.insert(pos, c)
		c._parent = self

	def delete(self):
		if self._parent:
			self._parent._children.remove(self)

	def children(self):
		for c in self._children:
			yield c

	def count_children(self):
		return len(self._children)

	def find_sibling(self, d, depth = 0):
		p = self._parent
		if p:
			pos = self.index
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
	def index(self):
		if not self._parent:
			return None

		pos = 0
		for n in self._parent._children:
			if n is self:
				return pos
			pos += 1

		return None

	@property
	def parent(self):
		return self._parent

	def __str__(self):
		return "Node(%s)" % self.title

# vim:sw=4 ts=4
