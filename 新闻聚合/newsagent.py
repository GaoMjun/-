
from nntplib import NNTP
from time import strftime, time, localtime
from email import message_from_string
from urllib import urlopen
import re

day = 24 * 60 * 60

def wrap(string, max = 70):
	return '\n'.join(textwrap.wrap(string)) + '\n'

class NewsAgent:
	def __init__(self):
		self.source = []
		self.destinations = []

	def addSource(self, source):
		self.source.append(source)

	def addDestination(self, dest):
		self.destinations.append(dest)

	def distribute(self):
		items = []
		for source in self.source:
			items.extend(source.getItems())
		for dest in self.destinations:
			dest.receiveItems(items)

class NewsItem:
	def __init__(self, title, body):
		self.title = title
		self.body = body

class NNTPSource:
	def __init__(self, servername, group, window):
		self.servername = servername
		self.group = group
		self.window = window

	def getItems(self):
		start = localtime(time() - self.window * day)
		date = strftime('%y%m%d', start)
		hour = strftime('%H%M%S', start)

		server = NNTP(self.servername)

		ids = server.newnews(self.group, date, hour)[1]

		for  id in ids:
			lines = server.article(id)[3]
			message = message_from_string('\n'.join(lines))

			title = message['subject']
			body = message.get_payload()
			if message.is_multipart():
				body = body[0]

			yield NewsItem(title, body)

		server.quit()

class SimpleWebSource:
	def __init__(self, url, titlePattern, bodyPattern):
		self.url = url
		self.titlePattern = re.compile(titlePattern)
		self.bodyPattern = re.compile(bodyPattern)

	def getItems(self):
		text = urlopen(self.url).read()
		titles = self.titlePattern.findall(text)
		bodies = self.bodyPattern.findall(text)
		for title, body in zip(titles, bodies):
			yield NewsItem(title, wrap(body))

class plainDestination:
	def reciveItems(self, items):
		for item in items:
			print item.title
			print '_'*len(item.title)
			print item.body

class HTMLDestination:
	def __init__(self, filename):
		self.filename = filename

	def reciveItems(self, items):
		out = open(self.filename, 'w')
		print >> out, """
		<html>
			<head>
				<title>Today's News</title>
			</head>
			<body>
			<h1>Today's News</h1>
		"""

		print >> out, '<ul>'
		id = 0
		for item in items:
			id += 1
			print >> out, '<li><a href="#%i">%s</li>' % (id, item.title)
		print >> out, '</ul>'

		id = 0
		for item in items:
			id += 1
			print >> out, '<h2><a name="%i">%s</a></h2>' % (id, item.title)

		print >>out, """
			</body>
		</html>
		"""

	def runDefultSetup():
		agent = NewsAgent()

		bbc_url = 'http://news.bbc.co.uk/text_only.stm'
		bbc_title = r'(?s)</a>\s*<br />\s*<b>\s*(.*?)\s*</b>'
		bbc_body = r'(?s)</a>\s*<br />\s*(.*?)\s*<'
		bbc = SimpleWebSource(bbc_url, bbc_title, bbc_body)

		agent.addSource(bbc)

		clpa_server = '' #input real server address
		clpa_group = '' #inpout real group
		clpa_window = 1
		clpa = NNTPSource(clpa_server, clpa_group, clpa_window)

		agent.addSource(clpa)

		agent.addDestination(PlainDestination())
		agent.addDestination(HTMLDestination('new.html'))

		agent.distribute()

if __name__ == '__main__':
	runDefultSetup()



