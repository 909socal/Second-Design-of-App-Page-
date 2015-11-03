import os
import webapp2
import jinja2
from datetime import datetime
from google.appengine.ext import ndb


template_dir = os.path.join(os.path.dirname(__file__), 'templates')
template_loader = jinja2.FileSystemLoader(template_dir)
template_env = jinja2.Environment(loader = template_loader, autoescape = True)


class Handler(webapp2.RequestHandler):
	def write(self, *arguments, **kw_arguments):
		self.response.out.write(*arguments, **kw_arguments)

	def render_str(self, template, **kw_arguments):
		t = template_env.get_template(template)
		return t.render(kw_arguments)

	def render(self, template, **kw_arguments):
		self.write(self.render_str(template, **kw_arguments))


class FormPage(Handler):
	def get(self):
		topics = ["Add your Comments:"]
		self.render('data_page.html', topics = topics)


class UserPage(Handler):
	def get(self):
		query = Page.query().order(Page.post_date)
		for i in query:
			topics = i.topics
			content = i.content
			name = i.name
			date = i.date
		self.render('commented_page.html', topics = topics, content = content, name = name,
			date = date)

	def post(self):
		name = self.request.get("name")
		date = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M') + " (PT)"
		topics = ["Add your Comments:"]
		paragraphs = self.request.get_all("content")
		content = {}
		for index, topic in enumerate(topics):
			content[topic] = paragraphs[index]
		blank = False
		if name.isspace():
			blank = True
			self.render('data_page.html', topics = topics, blank = blank)
		elif name and date and topics and content :
			input_page = Page(name = name, date = date, topics = topics, content = content)
			input_page.put()
			import time
			delay_time = .1
			time.sleep(delay_time)
			self.redirect('/userpage')
		else:
			self.redirect('/error')


class Collection(Handler):
	def get(self):
	   pages = Page.query().order(-Page.post_date)
	   self.render('total_comments.html', pages = pages)


class ErrorHandler(Handler):
	def get(self):
		self.render('error_page.html')


class Page(ndb.Model):
	topics = ndb.StringProperty(repeated=True)
	content = ndb.PickleProperty()
	name = ndb.StringProperty()
	date = ndb.StringProperty()
	post_date = ndb.DateTimeProperty(auto_now_add = True)

class NotesPage(Handler):
	def get(self):
		self.render("notes.html")

class FinalStage(Handler):
	def get(self):
		self.render("stage5.html")

app = webapp2.WSGIApplication([
	('/', FormPage),
	('/stage5', FinalStage),
	('/notes', NotesPage),
	('/userpage', UserPage),
	('/collection', Collection),
	('/error', ErrorHandler)
], debug=True)
