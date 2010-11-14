#!/usr/bin/env python

import sys, pygtk, gtk
pygtk.require('2.0')

import sys
from meme.ui import MemeGui
from meme.model import Model
from meme.io import read_native

if __name__ == "__main__":
	if len(sys.argv) == 1:
		gui = MemeGui()
	elif len(sys.argv) == 2:
		model = Model(read_native(sys.argv[1]))
		gui = MemeGui(model)
	else:
		print "Usage: %s [file]" % sys.argv[0]
	gtk.main()

# vim:sw=4 ts=4
