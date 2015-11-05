#-*- coding: utf-8 -*-
from datetime import timedelta as _timedelta
from pony.orm import (db_session as _db_session, commit as _commit, select as _select)
from ..tools import (getLocals as _getLocals, utc as _utc)
from ..entities import Agenda as _Agenda
from .persons_ctr import PersonasCriteria as _personsCtr
from .messages_ctr import MessagesCriteria as _messagesCtr

class AgendasCriteria(object):
	def exists(self, id_agd):
		with _db_session:
			return _select(agd for agd in _Agenda if agd.id_agd==id_agd).exists()
	@classmethod
	def get_agenda(cls, id_agd):
		with _db_session:
			return _Agenda.get(id_agd=id_agd)
	@classmethod
	def getAll_Unsent(cls):
		with _db_session:
			today = _utc.now().date()
			backward = today - _timedelta(days=4)
			for ag in _Agenda.select(lambda ag: (ag.fecha_con >= backward and ag.fecha_con <= today) and not ag.sms_estado):
				yield ag
	@classmethod
	def getAll_Sent(cls):
		cls.delete_outdated()
		with _db_session:
			today = _utc.now().date()
			backward = today - _timedelta(days=15)
			for ag in _Agenda.select(lambda ag: (ag.fecha_con >= backward and ag.fecha_con <= today) and (ag.sms_estado or ag.lmd_estado)):
				yield ag
	@classmethod
	def save(cls, id_agd, persona, mensaje, fecha_msj=None, fecha_con=None, sms_estado=False, lmd_estado=False):
		params = _getLocals(locals(), default='cls')
		if not cls().exists(id_agd=id_agd):
			with _db_session:
				params.persona, params.mensaje = _personsCtr.get_person(id_per=persona), _messagesCtr.get_message(id_msj=mensaje)
				_Agenda(**params)
				_commit()
			return True
		else:
			cls.update(**params)
			return False
	@classmethod
	def update(cls, id_agd, persona=None, mensaje=None, fecha_msj=None, fecha_con=None, sms_estado=None, lmd_estado=None):
		params = _getLocals(locals(), default='cls'); del params.id_agd
		with _db_session:
			params.persona, params.mensaje = _personsCtr.get_person(id_per=persona), _messagesCtr.get_message(id_msj=mensaje)
			cls.get_agenda(id_agd=id_agd).set(**params)
			_commit()
		return True
	@classmethod
	def update_status(cls, id_agd, sms_estado=None, lmd_estado=None):
		with _db_session:
			ag = cls.get_agenda(id_agd=id_agd)
			if not(sms_estado is None):
				ag.sms_estado = sms_estado
			if not(lmd_estado is None):
				ag.lmd_estado = lmd_estado
			_commit()
	@classmethod
	def delete(cls, id_agd):
		with _db_session:
			ag = cls.get_agenda(id_agd=id_agd)
			if ag:
				ag.delete()
			_commit()

	@classmethod
	def delete_outdated(cls):
		backward = _utc.now().date() - _timedelta(days=16)
		with _db_session:
			for ag in _Agenda.select(lambda ag: ag.fecha_con <= backward):
				ag.delete()
			_commit()