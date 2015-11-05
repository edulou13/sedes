#!/usr/bin/env python
#-*- coding: utf-8 -*-
import logging
import schedule as sc
from time import sleep
from gammu import ERR_DEVICENOTEXIST, ERR_CANTOPENFILE, ERR_TIMEOUT
from pony.orm import db_session
from app.tools import Modem
from app.entities import db
from app.criterias import agendasCrt

db.bind('postgres', host='127.0.0.1', database='sedes', user='postgres', password='master')
db.generate_mapping(create_tables=True)

def send_sms():
	contact_sms = lambda person, message: dict(phone=person.contacto.telf, text=u'para: {}; {}'.format(person.__str__(), message.tenor))
	try:
		sm = Modem()
		with db_session:
			for ag in agendasCrt.getAll_Unsent():
				if ag.persona.telf and ag.persona.cobertura==1:
					sm.send(phone=ag.persona.telf, text=ag.mensaje.tenor)
					if ag.persona.contacto and ag.persona.contacto.cobertura==1:
						sm.send(**contact_sms(ag.persona, ag.mensaje))
						# sm.send(phone=ag.persona.contacto.telf, text=u'para: {}; {}'.format(ag.persona.__str__(), ag.mensaje.tenor))
					agendasCrt.update_status(id_agd=ag.id_agd, sms_estado=True)
					continue
				if ag.persona.contacto and ag.persona.contacto.cobertura==1:
					sm.send(**contact_sms(ag.persona, ag.mensaje))
					agendasCrt.update_status(id_agd=ag.id_agd, sms_estado=True)
					continue
					# sm.send(phone=ag.persona.contacto.telf, text=u'para: {}; {}'.format(ag.persona.__str__(), ag.mensaje.tenor))
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
	sc.every(1).minutes.do(send_sms)
	# sc.every().day.at('09:00').do(send_sms)
	# sc.every().day.at('13:00').do(send_sms)
	# sc.every().day.at('18:00').do(send_sms)
	while True:
		try:
			sc.run_pending()
			sleep(.000001)
		except KeyboardInterrupt:
			break