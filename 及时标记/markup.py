import sys
import re
from handler import *
from rules import *
from util import *

class Parase:
	def __init__(self, handler):
		self.handler = handler
		self.rules = []
		self.filter = []

	def addRule(self, rule):
		self.rules.append(rule)

	def addFilter(self, pattern, name):
		def filter(block, handler):
			return re.sub(pattern, handler.sub(name), block)
		self.filter.append(filter)

	def parse(self, file):
		self.handler.start('document')
		for block in blocks(file):
			for filter in self.filters:
				block = filter(block, self.handler)
			for rule in self.rules:
				if rule.condition(block):
					last = rule.action(block, self.handler)
					if last:
						break
		self.handler.end('document')

class BasicTextParse(Parase):
	def __init__(self, handler):
		Parase.__init__(self, handler)
		self.addRule(ListRule())
		self.addRule(ListItemRule())
		self.addRule(TitleRule())
		self.addRule(HeadingRule())
		self.addRule(ParagraphRule())

		self.addFilter(r'\*(.+?)\*', 'emphasis')
		self.addFilter(r'(http://[\.a-zA-Z/]+)', 'url')
		self.addFilter(r'([\.a-zA-Z]+@[\.a-zA-Z]+[a-zA-Z]+)', 'mail')

handler = HTMLRenderer()
parse = BasicTextParse(handler)

parse.parse(sys.stdin)
