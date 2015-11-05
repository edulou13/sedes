#-*- coding: utf-8 -*-
from ..tools import (route, BaseHandler)
from tornado.gen import coroutine
from tornado.web import (RequestHandler, asynchronous)
from json import dumps
from fabric.api import (env, put)

@route('/getaudiofile')
class GetAudioFile(RequestHandler, BaseHandler):
	def set_default_headers(self):
		self.set_header('Access-Control-Allow-Origin', '*')
		self.set_header('Access-Control-Allow-Methods','POST')
	def to_asterisk(self, pathfile):
		try:
			env.user, env.password, env.host_string = 'root', 'S1nclave', '172.16.80.13'
			put(pathfile, '/var/lib/asterisk/sounds')
		except Exception:
			pass
		self.finish(dumps(True))
	@asynchronous
	@coroutine
	def post(self):
		self.set_header('Content-type', 'application/json')
		form = self.form2Dict()
		fl_audio = self.request.files['audio'][0]['body']
		path_audio = '{}/audio/{}'.format(self.settings['static_path'], form.audioname)
		print path_audio
		with open(path_audio, 'wb') as fl:
			fl.write(fl_audio)
		self.to_asterisk(path_audio)