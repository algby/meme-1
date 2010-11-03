#!/usr/bin/env python

import sys, pygtk, gtk
pygtk.require('2.0')

from meme.ui import *

if __name__ == "__main__":
	gui = MemeGui()
	gtk.main()

# vim:sw=4 ts=4
