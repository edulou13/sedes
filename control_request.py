#!/usr/bin/env python
#-*- coding: utf-8 -*-
import logging
from pony.orm import db_session
from gammu import ERR_DEVICENOTEXIST, ERR_CANTOPENFILE, ERR_TIMEOUT
from app.tools import utc, Modem
from app.entities import db
from app.criterias import personsCtr
import re as _re

db.bind('postgres', host='127.0.0.1', database='sedes', user='postgres', password='master')
db.generate_mapping(create_tables=True)

months = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
humanize = lambda strdt: u'{} de {} del {}'.format(strdt[2], months[int(strdt[1]) - 1], strdt[0])

pattern = "(?:(?:\\+591)?(6|7)[0-9]{7})"

@db_session
def listen():
	try:
		md = Modem(cfg = '/etc/gammurc1')
		sm = Modem()
		for msg in md.get():
			#pr = personsCtr.get_byCellphone(msg.number) if msg.number.isdigit() else None
			cellphone = _re.match(pattern, msg.number)
			if cellphone:
				cellphone = int(cellphone.group().replace('+591','')) if (len(cellphone.group()) == 12) else int(cellphone.group())
				pr = personsCtr.get_byCellphone(cellphone) if cellphone else None
				if pr and msg.text.lower()==u'c':
					print u'{}, agendas: {}, pregnants: {}\n'.format(pr, pr.agendas.count(), pr.embarazadas.count())
					today = utc.now().date()
					if pr.agendas.count() > 0 or pr.embarazadas.count() > 0:
						for ag in pr.agendas.select(lambda ag: ag.mensaje.tipo in [1,2] and ag.fecha_con >= today):
							sm.send(pr.telf, u'Fecha de control: {}'.format(humanize(ag.fecha_con.isoformat().split('-'))))
						for pregnant in pr.embarazadas:
							for ag in pregnant.agendas.select(lambda ag: ag.mensaje.tipo in [1,2] and ag.fecha_con >= today):
								sm.send(pr.telf, u'para: {}, fecha de control: {}'.format(pregnant.__str__(), humanize(ag.fecha_con.isoformat().split('-'))))
					else:
						sm.send(pr.telf, u'Usted no tiene controles próximos por ahora.')
			md.erase(Folder=0, Location=msg.location)
	except ERR_DEVICENOTEXIST:
		logging.error('without modem..!, please connect it')
	except ERR_CANTOPENFILE:
		logging.error('usb-port has change!, please update the settings')
	except ERR_TIMEOUT:
		logging.error('without network signal')
	except Exception, e:
		print e

if __name__ == '__main__':
	while True:
		try:
			listen()
		except KeyboardInterrupt:
			break