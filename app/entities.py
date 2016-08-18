#-*- coding: utf-8 -*-
from datetime import (date as _date,)
from pony.orm import (Database as _Database, PrimaryKey as _PrimaryKey, Required as _Required, Optional as _Optional, Set as _Set)

db = _Database()

class Persona(db.Entity):
	id_per = _PrimaryKey(int, auto=False)
	nombres = _Required(unicode)
	apellidos = _Required(unicode)
	telf = _Optional(str, 8, nullable=True)
	cobertura = _Optional(int, default=0)
	contacto = _Optional(lambda: Persona, reverse='embarazadas', nullable=True)
	embarazadas = _Set(lambda: Persona, reverse='contacto')
	agendas = _Set(lambda: Agenda, reverse='persona')
	def __str__(self):
		return u'{} {}'.format(self.nombres, self.apellidos)

class Mensaje(db.Entity):
	id_msj = _PrimaryKey(int, auto=False)
	tenor = _Required(unicode)
	tipo = _Required(int)
	# titulo = _Optional(unicode, nullable=True)
	audio = _Optional(unicode, nullable=True)
	nro_control = _Optional(int, nullable=True)
	agendas = _Set(lambda: Agenda, reverse='mensaje')

class Agenda(db.Entity):
	id_agd = _PrimaryKey(int, auto=False)
	fecha_msj = _Optional(_date, nullable=True)
	fecha_con = _Optional(_date, nullable=True)
	persona = _Required(Persona, reverse='agendas')
	mensaje = _Required(Mensaje, reverse='agendas')
	sms_estado = _Optional(bool, default=False)
	lmd_estado = _Optional(bool, default=False)
	def to_dict(self):
		return dict(id_agd=self.id_agd, sms_estado=self.sms_estado, lmd_estado=self.lmd_estado)