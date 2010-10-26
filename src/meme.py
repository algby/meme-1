#!/usr/bin/env python

import sys, pygtk, gtk
pygtk.require('2.0')

from meme.ui import *

if __name__ == "__main__":
	gui = MemeGui()

	while gtk.events_pending():
		gtk.main_iteration(False)

	model = gui._model
	root = model._root
	for i in xrange(0, 5):
		model.append_child(root, Node("Node %s" % ("x" * i)))
	for i in xrange(0, 2):
		model.append_child(root.child(1), Node("Node %d" % i))
	for i in xrange(0, 7):
		model.append_child(root.child(4), Node("Node %d" % i))
	model.append_child(root.child(1).child(1), Node("Longer node"))

	i = [0]
	def idle():
		import time
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

	#gtk.timeout_add(50, idle)
	gtk.main()

# vim:sw=4 ts=4
