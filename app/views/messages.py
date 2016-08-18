#-*- coding: utf-8 -*-
from json import (dumps, loads)
from tornado.gen import coroutine
from tornado.web import (RequestHandler, asynchronous)
# from ..tools import (route, BaseHandler, SendSMS as BulkSMS)
from ..tools import (route, BaseHandler, Modem)

@route('/sendsms')
class SendSMS(RequestHandler, BaseHandler):
	def set_default_headers(self):
		self.set_header('Access-Control-Allow-Origin', '*')
		self.set_header('Access-Control-Allow-Methods','POST')
	@asynchronous
	@coroutine
	def post(self):
		self.set_header('Content-type', 'application/json')
		x_real_ip = self.request.headers.get("X-Real-IP")
		remote_ip = self.request.remote_ip if not x_real_ip else x_real_ip
		print remote_ip
		form = self.form2Dict()
		phone_text =  lambda obj: dict(phone=obj['ctelf'], text=u'para: {}; {}'.format(obj['nombre'], form.msg)) if(not obj['telf']) else dict(phone=obj['telf'], text=form.msg)
		#sm = BulkSMS()
		sm = Modem()
		for pr in loads(form.personas):
			sm.send(**phone_text(pr))
		self.finish(dumps(True))