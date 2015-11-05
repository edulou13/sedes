#-*- coding: utf-8 -*-
from pony.orm import db_session as _db_session, commit as _commit, select as _select
from ..entities import Persona as _Persona
from ..tools import getLocals as _getLocals

class PersonasCriteria(object):
	def exists(self, id_per):
		return _select(pr for pr in _Persona if int(id_per)==pr.id_per).exists()
	@classmethod
	def get_person(cls, id_per):
		with _db_session:
			return _Persona.get(id_per=id_per)
	@classmethod
	def get_byCellphone(cls, number):
		return _Persona.get(telf=number)
	@classmethod
	def save(cls, id_per, nombres, apellidos, telf, cobertura, contacto):
		params = _getLocals(locals(), default='cls')
		with _db_session:
			if not cls().exists(id_per=id_per):
				params.contacto = cls.get_person(id_per=contacto) if contacto else None
				_Persona(**params)
				_commit()
			else:
				cls.update(**params)
	@classmethod
	def update(cls, id_per, nombres, apellidos, telf, cobertura, contacto):
		params = _getLocals(locals(), default='cls'); del params.id_per
		with _db_session:
			params.contacto = cls.get_person(id_per=contacto) if contacto else None
			cls.get_person(id_per=id_per).set(**params)
			_commit()