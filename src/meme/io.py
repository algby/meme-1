# Meme: a fast mind-mapping tool
# (c) 2010 Jamie Webb - MIT license

import json, gzip
from xml.etree import ElementTree

from model import *

def read_native(path):
	def read_tree(tree):
		title = tree["title"]
		color = tree["color"]
		node = Node(title)
		node.color = color
		for c in tree["children"]:
			node.add_child(read_tree(c))
		return node

	return read_tree(json.load(gzip.open(path, "r")))

def write_native(path, root):
	def write_node(node):
		return {
			"title": node.title,
			"color": node.color,
			"children": [write_node(c) for c in node.children()]
		}

	tree = write_node(root)
	json.dump(tree, gzip.open(path, "w"), indent = 4)

def read_freemind(path):
	def read_tree(tree):
		title = tree.get("TEXT")
		node = Node(title)
		for c in tree:
			if c.tag == "node":
				node.add_child(read_tree(c))
		return node

	return read_tree(list(ElementTree.parse(path).getroot())[0])

# vim:sw=4 ts=4
