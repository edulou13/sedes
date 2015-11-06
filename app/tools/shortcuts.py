#-*- coding: utf-8 -*-
from time import sleep as _sleep
from datetime import (datetime as _datetime, timedelta as _timedelta)
from gammu import (StateMachine as _StateMachine, EncodeSMS as _EncodeSMS, ERR_EMPTY as _ERR_EMPTY, ERR_GETTING_SMSC as _ERR_GETTING_SMSC, ERR_UNKNOWNRESPONSE as _ERR_UNKNOWNRESPONSE)

class UTC(object):
	@classmethod
	def now(cls):
		return _datetime.utcnow() - _timedelta(hours=4)

class CustomDict(dict):
	def __getattr__(self, key):
		return self[key]
	def __setattr__(self, key, value):
		self[key] = value
	def __delattr__(self, key):
		del self[key]

def getLocals(obj, default='self'):
	check = lambda key: key.startswith('_') or key.startswith(default)
	return CustomDict([(k,v) for k,v in obj.iteritems() if not(check(k))])

class BaseHandler(object):
	def form2Dict(self):
		return CustomDict([(k, self.get_argument(k, None)) for k in self.request.arguments.iterkeys() if not(k.startswith('_'))])

class Modem(object):
	def __init__(self, cfg = '/etc/gammurc'):
		self.sm = _StateMachine()
		self.sm.ReadConfig(Filename = cfg)
		self.sm.Init()
	def erase(self, Folder, Location):
		"""
			Folder: 0 Inbox, 1 Outbox
			Location: 0-255, position of the sms in the memory
		"""
		try:
			self.sm.DeleteSMS(Folder = Folder, Location = Location)
		except _ERR_EMPTY:
			pass
	def get(self):
		while True:
			try:
				for pos in xrange(255):
					try:
						for msg in self.sm.GetSMS(Folder=0, Location=pos):
							yield CustomDict(number=msg['Number'], text=msg['Text'], location=pos)
					except _ERR_EMPTY:
						break
					except _ERR_UNKNOWNRESPONSE:
						print 'ERR_UNKNOWNRESPONSE'
				_sleep(5)
			except KeyboardInterrupt:
				break
	def send(self, phone, text):
		try:
			for msg in _EncodeSMS(dict(Class=1, Unicode=True, Entries=[dict(ID='ConcatenatedTextLong', Buffer=text)])):
				msg['SMSC'], msg['Number'] = dict(Location=1), '+591{phone}'.format(phone=int(phone))
				print self.sm.SendSMS(msg)
		except _ERR_GETTING_SMSC:
			pass