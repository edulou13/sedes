#-*- coding: utf-8 -*-
from tornado.gen import coroutine
from tornado.web import (RequestHandler, asynchronous)
from json import dumps, loads
from ..tools import (route, BaseHandler)
from ..criterias import agendasCrt

@route('/delete_agendas')
class DeleteAgendas(RequestHandler, BaseHandler):
	def set_default_headers(self):
		self.set_header('Access-Control-Allow-Origin', '*')
		self.set_header('Access-Control-Allow-Methods','POST')
	@asynchronous
	@coroutine
	def post(self):
		self.set_header('Content-type', 'application/json')
		form = self.form2Dict()
		if form.has_key('agendas'):
			print form.agendas
			for id_agd in loads(form.agendas):
				agendasCrt.delete(id_agd=id_agd)
		self.finish(dumps(True))