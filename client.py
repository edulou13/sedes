#!/usr/bin/env python
#-*- coding: utf-8 -*-
import sys, logging, signal, time
reload(sys)
sys.setdefaultencoding('utf-8')

from os import (environ as env, path)
from tornado.ioloop import IOLoop
from tornado.httpserver import HTTPServer
from tornado.options import (define, parse_command_line, options)
from tornado.web import (Application as _App,)
from app import views
from app.tools import url_handlers
from app.entities import db

define('debug', default=False, type=bool, help='Run in debug mode')
define('port', default=8000, type=int, help='Server port')

workingdir = path.dirname(path.realpath(__file__))

def shutdown(server):
	ioloop = IOLoop.current()
	logging.info('Stopping server.')
	server.stop()
	def finalinze():
		ioloop.stop()
		logging.info('Stopped.')
	ioloop.add_timeout(time.time() + .2, finalinze)

class Server(_App):
	def __init__(self):
		db.bind('postgres', host='127.0.0.1', database='sedes', user='postgres', password='master')
		db.generate_mapping(create_tables=True)
		settings = dict(
			static_path = path.join(workingdir, 'statics'),
			server_traceback = options.debug,
			debug = options.debug
		)
		super(Server, self).__init__(handlers=url_handlers, **settings)

if __name__ == '__main__':
	parse_command_line()
	server = HTTPServer(Server())
	signal.signal(signal.SIGINT, lambda sig, frame: shutdown(server))
	logging.info('Starting server on localhost:{}'.format(options.port))
	if not options.debug:
		server.bind(env.get('PORT', options.port))
		server.start(0)
	else:
		server.listen(env.get('PORT', options.port))
	IOLoop.current().start()