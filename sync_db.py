#!/usr/bin/env python
#-*- coding: utf-8 -*-
import logging
import schedule as sc
from json import loads, dumps
from time import sleep
from sys import argv
from tornado.ioloop import IOLoop
from tornado.httpclient import AsyncHTTPClient
from tornado import gen
from functools import partial
from urllib import urlencode
from gammu import ERR_DEVICENOTEXIST, ERR_CANTOPENFILE, ERR_TIMEOUT
from app.tools import cdict, utc, Modem
from app.entities import db
from app.criterias import personsCtr, messagesCtr, agendasCrt

AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")

db.bind('postgres', host='127.0.0.1', database='sedes', user='postgres', password='master'); db.generate_mapping(create_tables=True)

apikey, _xsrf = 'NGM0NTRkNDIyZDRiNDg0MTU3NDE1ODNhNDU2YzYxNjM2NTcz', None

def show_status(str_log):
	now = utc.now()
	return u'{} {}: {}.'.format(now.date().isoformat(), now.time().isoformat()[:8], str_log)

def parse_datas(data, func):
	# print show_status(u'Successful sync')
	logging.info(show_status(u'Successful sync'))
	if type(data) == unicode:
		global _xsrf
		_xsrf = data
	elif type(data) == list:
		for params in data:
			func.save(**params)
	else:
		pass

def exec_fetch(**kwargs):
	@gen.coroutine
	def fetch_url(url, func, name=None):
		build_url = lambda: urlencode(dict(apikey=apikey, agendas=dumps([ag.to_dict() for ag in agendasCrt.getAll_Sent()]))) if(name and name=='feedback') else urlencode(dict(apikey=apikey))
		url = '{}?{}'.format(url, build_url())
		try:
			response = yield AsyncHTTPClient().fetch(url)
			parse_datas(data=loads(response.body), func=func)
		except Exception, e:
			#print show_status(u'Lost connection')
			print e
			logging.warning(show_status(u'Lost connection'))
	client, run_func = IOLoop.current(), partial(fetch_url, **kwargs)
	client.run_sync(run_func); sleep(1)

def sync_db(localhost=True):
	host = lambda: 'localhost' if localhost else 'enlaces-khawax.herokuapp.com'
	api_url = lambda lnk, func, name=None: cdict(url='http://{}/api/{}'.format(host(), lnk), func=func, name=name)
	params = [api_url('getsession',None), api_url('feedback', None, 'feedback'), api_url('getpersons', personsCtr), api_url('getmessages', messagesCtr), api_url('getagendas', agendasCrt)]
	for prs in params:
		exec_fetch(**prs)
	try:
		if utc.now().hour==14:
			print 'Hour: {}'.format(utc.now().hour)
			sync_status()
	except Exception, e:
		print 'Error at sync_db: {}'.format(e)

def sync_status():
	try:
		md = Modem()
		for number in [76180435]:
		# for number in [76180435, 70219542, 67370901, 70219848]:
			md.send(number, u'{}, última sincronización.'.format(utc.now().time().isoformat()[:8]))
	except ERR_DEVICENOTEXIST:
		# print 'without modem..!, please connect it'
		logging.error('without modem..!, please connect it')
	except ERR_CANTOPENFILE:
		# print 'usb-port has change!, please update the settings'
		logging.error('usb-port has change!, please update the settings')
	except ERR_TIMEOUT:
		# 'without network signal'
		logging.error('without network signal')

if __name__ == '__main__':
	localhost = argv[1]=='--localhost' if len(argv)==2 else False
	# sc.every(10).seconds.do(sync_db, localhost)
	sc.every(5).minutes.do(sync_db, localhost)
	# sc.every().day.at('11:08').do(sync_db, localhost)
	# sc.every().hours.do(sync_db, localhost)
	# sc.every().day.at('07:50').do(sync_db, localhost)
	# sc.every().day.at('08:50').do(sync_db, localhost)
	# sc.every().day.at('11:50').do(sync_db, localhost)
	# sc.every().day.at('12:50').do(sync_db, localhost)
	# sc.every().day.at('16:50').do(sync_db, localhost)
	# sc.every().day.at('17:50').do(sync_db, localhost)
	while True:
		try:
			sc.run_pending()
			sleep(.000000001)
		except KeyboardInterrupt:
			break