#!/usr/bin/env python

# Meme: a fast mind-mapping tool
# (c) 2010 Jamie Webb - MIT license

import sys, pygtk, gtk, os
pygtk.require('2.0')

from meme.ui import MemeGui
from meme.model import Model
from meme.io import read_native

ROOT = os.path.dirname(os.path.realpath(__file__))
UI = ROOT + "/ui/meme.xml"

if __name__ == "__main__":
	if len(sys.argv) == 1:
		gui = MemeGui(UI)
	elif len(sys.argv) == 2:
		model = Model(read_native(sys.argv[1]))
		gui = MemeGui(UI, model)
	else:
		print "Usage: %s [file]" % sys.argv[0]
	gtk.main()

# vim:sw=4 ts=4
