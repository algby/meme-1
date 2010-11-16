# Meme: a fast mind-mapping tool
# (c) 2010 Jamie Webb - MIT license

class GlobalStyle(object):
	def __init__(self):
		self.marginx = 20
		self.marginy = 20
		self.padx = 20
		self.pady = 5
		self.dimy = 20
		self.innerpad = 5
		self.background = (0.95, 0.93, 0.9)
		self.lines = (0.5, 0.5, 0.5)
		self.line_width = 2.0
		self.font = "sans 8"

		self.colors = [
			((0, 0, 0), (1, 1, 1)),
			((0.8, 0, 0), (1, 0.95, 0.95)),
			((0.7, 0.3, 0), (1, 0.95, 0.8)),
			((0, 0.5, 0), (0.9, 1, 0.9)),
			((0, 0, 1), (0.9, 0.9, 1))
		]

# vim:sw=4 ts=4
