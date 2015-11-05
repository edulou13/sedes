#-*- coding: utf-8 -*-
from pony.orm import (db_session as _db_session, commit as _commit, select as _select)
from ..entities import Mensaje as _Mensaje
from ..tools import getLocals as _getLocals

class MessagesCriteria(object):
	def exists(self, id_msj):
		return _select(msg for msg in _Mensaje if int(id_msj)==msg.id_msj).exists()
	@classmethod
	def get_message(cls, id_msj):
		with _db_session:
			return _Mensaje.get(id_msj=id_msj)
	@classmethod
	def save(cls, id_msj, tenor, tipo, audio, nro_control):
		params = _getLocals(locals(), default='cls')
		with _db_session:
			if not cls().exists(id_msj=id_msj):
				_Mensaje(**params)
				_commit()
			else:
				cls.update(**params)
	@classmethod
	def update(cls, id_msj, tenor, tipo, audio, nro_control):
		params = _getLocals(locals(), default='cls'); del params.id_msj
		with _db_session:
			cls.get_message(id_msj=id_msj).set(**params)
			_commit()