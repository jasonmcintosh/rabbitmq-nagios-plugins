import abc
import urllib2
import json
from pynagios import Plugin, make_option, Response, WARNING, CRITICAL, UNKNOWN
from urllib2 import Request, urlopen, URLError, HTTPError

import base_rabbit_check


class BaseRabbitCheck(Plugin):
	"""
	performs a nagios compliant check
	attempts to catch all errors. expected usage is with a critical threshold of 0
	"""

	username = make_option("--username", dest="username", help="RabbitMQ API username", type="string", default="guest")
	password = make_option("--password", dest="password", help="RabbitMQ API password", type="string", default="guest")
	port = make_option("--port", dest="port", help="RabbitMQ API port", type="string", default="15672")
        use_ssl =  make_option("--ssl", action="store_true", dest="use_ssl", default=False, help="Use SSL")

	def doApiGet(self):
		"""
		performs and returns content from an api get
		"""
		password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
		password_mgr.add_password(None, self.url, self.options.username, self.options.password)
		handler = urllib2.HTTPBasicAuthHandler(password_mgr)
		opener = urllib2.build_opener(handler)

		response = None
		try:
			request = opener.open(self.url)
			response = request.read()
			request.close()
		except Exception, e:
			response = False
			self.rabbit_error = 2
			self.rabbit_note = "problem with api get:" + str(e)

		return response

	def parseJson(self, response):
		"""
		parse test and return api json
		"""
		try:
			data = json.loads(response)
		except Exception, e:
			data = None
			self.rabbit_error = 4
			self.rabbit_note = "problem with json parse:", e
		return data

	@abc.abstractmethod
	def makeUrl(self):
		return

	@abc.abstractmethod
	def testOptions(self):
		return

	@abc.abstractmethod
	def setPerformanceData(self, data, result):
		return

	@abc.abstractmethod
	def parseResult(self, data):
		return Response(UNKNOWN, "No result set!")

	def check(self):
		"""
		returns a response and perf data for this check
		"""
		try:
			self.rabbit_error = 0
			self.rabbit_note = "action performed successfully"

			if not self.testOptions():
				return Response(UNKNOWN, "Incorrect check config" + self.rabbit_note)
			
			if not self.options.hostname or not self.options.port or not self.options.username or not self.options.password or not self.testOptions():
				return Response(UNKNOWN, "Incorrect missing options")

			if not self.makeUrl():
				return Response(UNKNOWN, "Error with URL")

			response = self.doApiGet()

			if self.rabbit_error > 0:
				return Response(CRITICAL, self.rabbit_note)

			data = self.parseJson(response)

			if self.rabbit_error > 0:
				return Response(CRITICAL, self.rabbit_note)

			result = self.parseResult(data)
			self.setPerformanceData(data, result)
			return result
		except Exception as e:
			return Response(UNKNOWN, "Error occurred:" + str(e))
