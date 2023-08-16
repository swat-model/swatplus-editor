from flask import jsonify, request, abort, Response
from .config import RequestHeaders as rh

from playhouse.shortcuts import model_to_dict
from playhouse.migrate import *

from helpers import utils, table_mapper
from database.project import base as project_base

class DefaultRestMethods:
	@staticmethod
	def get(id, table, description, back_refs=False, max_depth=1) -> Response:
		project_db = request.headers.get(rh.PROJECT_DB)
		has_db,error = rh.init(project_db)
		if not has_db: abort(400, error)

		m = table.get(table.id == id)
		if m is None:
			rh.close()
			abort(400, '{} {} does not exist'.format(description, id))

		if back_refs:
			d = model_to_dict(m, backrefs=True, max_depth=max_depth)
			RestHelpers.get_obj_name(d)
			rh.close()
			return d
		else:
			rh.close()
			return model_to_dict(m, recurse=False)
		
	@staticmethod
	def get_by_name(name, table, description, back_refs=False, max_depth=1) -> Response:
		project_db = request.headers.get(rh.PROJECT_DB)
		has_db,error = rh.init(project_db)
		if not has_db: abort(400, error)

		m = table.get(table.name == name)
		if m is None:
			rh.close()
			abort(400, '{} {} does not exist'.format(description, name))

		if back_refs:
			d = model_to_dict(m, backrefs=True, max_depth=max_depth)
			RestHelpers.get_obj_name(d)
			rh.close()
			return d
		else:
			rh.close()
			return model_to_dict(m, recurse=False)
		
	@staticmethod
	def get_datasets(id, table, description, back_refs=False, max_depth=1) -> Response:
		project_db = request.headers.get(rh.PROJECT_DB)
		datasets_db = request.headers.get(rh.DATASETS_DB)
		has_db,error = rh.init(project_db, datasets_db)
		if not has_db: abort(400, error)

		m = table.get(table.id == id)
		if m is None:
			rh.close()
			abort(400, '{} {} does not exist'.format(description, id))

		if back_refs:
			d = model_to_dict(m, backrefs=True, max_depth=max_depth)
			RestHelpers.get_obj_name(d)
			rh.close()
			return d
		else:
			rh.close()
			return model_to_dict(m, recurse=False)
		
	@staticmethod
	def get_datasets_name(name, table, description, back_refs=False, max_depth=1) -> Response:
		project_db = request.headers.get(rh.PROJECT_DB)
		datasets_db = request.headers.get(rh.DATASETS_DB)
		has_db,error = rh.init(project_db, datasets_db)
		if not has_db: abort(400, error)

		m = table.get(table.name == name)
		if m is None:
			rh.close()
			abort(400, '{} {} does not exist'.format(description, name))

		if back_refs:
			d = model_to_dict(m, backrefs=True, max_depth=max_depth)
			RestHelpers.get_obj_name(d)
			rh.close()
			return d
		else:
			rh.close()
			return model_to_dict(m, recurse=False)
		
	@staticmethod
	def delete(id, table, description, related_col=None, related_table=None) -> Response:
		project_db = request.headers.get(rh.PROJECT_DB)
		has_db,error = rh.init(project_db)
		if not has_db: abort(400, error)

		project_base.db.execute_sql("PRAGMA foreign_keys = ON")
		m = table.get(table.id == id)
		if m is None:
			rh.close()
			abort(400, '{} {} does not exist'.format(description, id))

		if related_col is not None and related_table is not None:
			d = model_to_dict(m, recurse=False)
			rid = d[related_col]
			m2 = related_table.get(related_table.id == rid)
			m2.delete_instance()
		
		result = m.delete_instance()
		rh.close()
		if result > 0:
			return '', 204
		
		abort(400, 'Unable to delete {} {}.'.format(description, id))
		

class RestHelpers:
	@staticmethod
	def get_obj_name(d):
		if 'con_outs' in d:
			for o in d['con_outs']:
				c_table = table_mapper.obj_typs.get(o['obj_typ'], None)
				o['obj_name'] = c_table.get(c_table.id == o['obj_id']).name
		if 'src_obs' in d:
			for o in d['src_obs']:
				obj_typ = o['obj_typ'] if o['obj_typ'] != 'cha' else 'sdc'
				c_table = table_mapper.obj_typs.get(obj_typ, None)
				if c_table is None: o['obj_name'] = None
				else: o['obj_name'] = c_table.get(c_table.id == o['obj_id']).name
		if 'dmd_obs' in d:
			for o in d['dmd_obs']:
				c_table = table_mapper.obj_typs.get(o['obj_typ'], None)
				if c_table is None: o['obj_name'] = None
				else: o['obj_name'] = c_table.get(c_table.id == o['obj_id']).name

				r_table = table_mapper.obj_typs.get(o['rcv_obj'], None)
				if r_table is None: o['rcv_obj_name'] = None
				else: o['rcv_obj_name'] = r_table.get(r_table.id == o['rcv_obj_id']).name
		if 'elements' in d:
			for o in d['elements']:
				c_table = table_mapper.obj_typs.get(o['obj_typ'], None)
				key = 'obj_id' if 'obj_id' in o else 'obj_typ_no'
				o['obj_name'] = c_table.get(c_table.id == o[key]).name
		if 'obj_typ' in d and ('obj_id' in d or 'obj_typ_no' in d):
			c_table = table_mapper.obj_typs.get(d['obj_typ'], None)
			key = 'obj_id' if 'obj_id' in d else 'obj_typ_no'
			if c_table is None: d['obj_name'] = None
			else: d['obj_name'] = c_table.get(c_table.id == d[key]).name