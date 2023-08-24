from flask import request, abort, Response
from .config import RequestHeaders as rh

from playhouse.shortcuts import model_to_dict
from playhouse.migrate import *

from helpers import table_mapper
from database import lib as db_lib
from database.project import base as project_base, climate

import ast

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

	@staticmethod
	def get_paged_items(table, filter_cols=[], table_lookups={}) -> Response:
		project_db = request.headers.get(rh.PROJECT_DB)
		has_db,error = rh.init(project_db)
		if not has_db: abort(400, error)

		args = request.args
		total = table.select().count()
		sort = RestHelpers.get_arg(args, 'sort', 'name')
		reverse = RestHelpers.get_arg(args, 'reverse', 'n')
		page = RestHelpers.get_arg(args, 'page', 1)
		per_page = RestHelpers.get_arg(args, 'per_page', 50)
		filter_val = RestHelpers.get_arg(args, 'filter', None)

		if filter_val is not None:
			w = None
			for f in filter_cols:
				lu = table_lookups.get(f, None)
				if lu is None:
					w = w | (f.contains(filter_val))
				else:
					sub = lu.select().where(lu.name.contains(filter_val))
					w = w | (f.in_(sub))
			s = table.select().where(w)
		else:
			s = table.select()

		matches = s.count()

		if sort == 'name':
			sort_val = table.name if reverse != 'y' else table.name.desc()
		else:
			sort_val = SQL('[{}]'.format(sort))
			if reverse == 'y':
				sort_val = SQL('[{}]'.format(sort)).desc()

		m = s.order_by(sort_val).paginate(int(page), int(per_page))

		rh.close()
		return {
			'model': m,
			'total': total,
			'matches': matches
		}
	
	@staticmethod
	def get_paged_list(table, filter_cols=[], back_refs=False, table_lookups={}) -> Response:
		items = DefaultRestMethods.get_paged_items(table, filter_cols, table_lookups)
		m = items['model']

		if back_refs:
			ml = [model_to_dict(v, backrefs=True, max_depth=1) for v in m]
			for d in ml:
				RestHelpers.get_obj_name(d)
		else:
			ml = [model_to_dict(v, recurse=False) for v in m]

		return {
			'total': items['total'],
			'matches': items['matches'],
			'items': ml
		}
	
	@staticmethod
	def get_list(table) -> Response:
		project_db = request.headers.get(rh.PROJECT_DB)
		has_db,error = rh.init(project_db)
		if not has_db: abort(400, error)

		m = table.select()
		rh.close()
		return [model_to_dict(v, recurse=False) for v in m]
	
	@staticmethod
	def get_name_id_list(table) -> Response:
		project_db = request.headers.get(rh.PROJECT_DB)
		has_db,error = rh.init(project_db)
		if not has_db: abort(400, error)

		m = table.select(table.id, table.name).order_by(table.name)
		rh.close()
		return [{'id': v.id, 'name': v.name} for v in m]

	@staticmethod
	def post(table, item_description, extra_args=[]) -> Response:
		project_db = request.headers.get(rh.PROJECT_DB)
		has_db,error = rh.init(project_db)
		if not has_db: abort(400, error)

		try:
			result = RestHelpers.save_args(table, request.json, is_new=True, extra_args=extra_args)

			rh.close()
			if result > 0:
				return {'id': result }, 201

			abort(400, 'Unable to create {item}.'.format(item=item_description.lower()))
		except IntegrityError as e:
			rh.close()
			abort(400, '{item} name must be unique. {ex}'.format(item=item_description, ex=str(e)))
		except Exception as ex:
			rh.close()
			abort(400, 'Unexpected error {ex}'.format(ex=ex))
	
	@staticmethod
	def put(id, table, item_description) -> Response:
		project_db = request.headers.get(rh.PROJECT_DB)
		has_db,error = rh.init(project_db)
		if not has_db: abort(400, error)

		try:
			result = RestHelpers.save_args(table, request.json, id=id)

			rh.close()
			if result > 0:
				return '', 201

			abort(400, 'Unable to update {item} {id}.'.format(item=item_description.lower(), id=id))
		except IntegrityError as e:
			rh.close()
			abort(400, '{item} name must be unique. '.format(item=item_description) + str(e))
		except table.DoesNotExist:
			rh.close()
			abort(404, '{item} {id} does not exist'.format(item=item_description, id=id))
		except Exception as ex:
			rh.close()
			abort(400, 'Unexpected error {ex}'.format(ex=ex))

	@staticmethod
	def put_many(table, item_description) -> Response:
		project_db = request.headers.get(rh.PROJECT_DB)
		has_db,error = rh.init(project_db)
		if not has_db: abort(400, error)

		try:
			args = request.json
			param_dict = {}
			for key in args.keys():
				if args[key] is not None and key != 'selected_ids':
					param_dict[key] = args[key]

			result = db_lib.bulk_update_ids(project_base.db, table, param_dict, args['selected_ids'])

			rh.close()
			if result > 0:
				return '', 200

			abort(400, 'Unable to update {item}.'.format(item=item_description.lower()))
		except Exception as ex:
			rh.close()
			abort(400, 'Unexpected error {ex}'.format(ex=ex))

	@staticmethod
	def get_paged_items_con(table, prop_table, filter_cols=[], table_lookups={}, props_lookups={}) -> Response:
		project_db = request.headers.get(rh.PROJECT_DB)
		has_db,error = rh.init(project_db)
		if not has_db: abort(400, error)

		args = request.args

		total = table.select().count()
		sort = RestHelpers.get_arg(args, 'sort', 'name')
		reverse = RestHelpers.get_arg(args, 'reverse', 'n')
		page = RestHelpers.get_arg(args, 'page', 1)
		per_page = RestHelpers.get_arg(args, 'per_page', 50)
		filter_val = RestHelpers.get_arg(args, 'filter', None)

		if filter_val is not None:
			w = None
			for f in filter_cols:
				lu = table_lookups.get(f, None)
				lu2 = props_lookups.get(f, None)
				if lu is None and lu2 is None:
					w = w | (f.contains(filter_val))
				elif lu2 is None:
					sub = lu.select().where(lu.name.contains(filter_val))
					w = w | (f.in_(sub))
				else:
					sub2 = lu2.select().where(lu2.name.contains(filter_val))
					w = w | (f.in_(sub2))
			s = table.select(table, prop_table).join(prop_table).where(w)
		else:
			s = table.select(table, prop_table).join(prop_table)

		matches = s.count()

		if sort == 'name':
			sort_val = table.name if reverse != 'y' else table.name.desc()
		else:
			sort_val = SQL('[{}]'.format(sort))
			if reverse == 'y':
				sort_val = SQL('[{}]'.format(sort)).desc()

		m = s.order_by(sort_val).paginate(int(page), int(per_page))

		rh.close()
		return {
			'model': m,
			'total': total,
			'matches': matches
		}

	@staticmethod
	def post_con(prop_name, con_table, prop_table) -> Response:
		project_db = request.headers.get(rh.PROJECT_DB)
		has_db,error = rh.init(project_db)
		if not has_db: abort(400, error)

		args = request.json
		e = con_table.get_or_none(con_table.name == args['name'])
		if e is not None:
			abort(400, 'Name must be unique. Object with the name, {}, already exists.'.format(args['name']))

		try:
			params = {
				'name': args['name'],
				'area': args['area'],
				'lat': args['lat'],
				'lon': args['lon'],
				'elev': args['elev'],
				'ovfl': 0,
				'rule': 0
			}

			params['{}_id'.format(prop_name)] = args['{}_id'.format(prop_name)]

			if args['wst_name'] is not None:
				params['wst_id'] = RestHelpers.get_id_from_name(climate.Weather_sta_cli, args['wst_name'])

			result = con_table.insert(params).execute()

			rh.close()
			if result > 0:
				return {'id': result }, 201

			abort(400, 'Unable to create object.')
		except IntegrityError:
			rh.close()
			abort(400, 'Name must be unique.')
		except prop_table.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['{}_name'.format(prop_name)]))
		except climate.Weather_sta_cli.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['wst_name']))
		except Exception as ex:
			rh.close()
			abort(400, "Unexpected error {ex}".format(ex=ex))

	@staticmethod
	def put_con(id, prop_name, con_table, prop_table) -> Response:
		project_db = request.headers.get(rh.PROJECT_DB)
		has_db,error = rh.init(project_db)
		if not has_db: abort(400, error)

		try:
			args = request.json
			params = {
				'name': args['name'],
				'area': args['area'],
				'lat': args['lat'],
				'lon': args['lon'],
				'elev': args['elev'],
			}

			params['{}_id'.format(prop_name)] = args['{}_id'.format(prop_name)]

			if 'wst_name' in args:
				params['wst_id'] = RestHelpers.get_id_from_name(climate.Weather_sta_cli, args['wst_name'])

			result = con_table.update(params).where(con_table.id == id).execute()

			rh.close()
			if result > 0:
				return '', 200

			abort(400, 'Unable to update item {}.'.format(id))
		except IntegrityError:
			rh.close()
			abort(400, 'Name must be unique.')
		except con_table.DoesNotExist:
			rh.close()
			abort(404, 'Object {id} does not exist'.format(id=id))
		except prop_table.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['{}_name'.format(prop_name)]))
		except climate.Weather_sta_cli.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['wst_name']))
		except Exception as ex:
			rh.close()
			abort(400, 'Unexpected error {ex}'.format(ex=ex))

	@staticmethod
	def put_many_con(args, param_dict, con_table, con_prop_field, prop_table):
		con_param_dict = {}
		if 'wst_name' in args:
			con_param_dict['wst_id'] = RestHelpers.get_id_from_name(climate.Weather_sta_cli, args['wst_name'])
		if 'elev' in args:
			con_param_dict['elev'] = args['elev']

		con_result = 1
		if (len(con_param_dict) > 0):
			con_result = db_lib.bulk_update_ids(project_base.db, con_table, con_param_dict, args['selected_ids'])

		if con_result > 0:
			result = 1
			if (len(param_dict) > 0):
				prop_ids = con_table.select(con_prop_field.alias('prop_id')).where(con_table.id.in_(args['selected_ids']))
				id_list = [v.prop_id for v in prop_ids]
				result = db_lib.bulk_update_ids(project_base.db, prop_table, param_dict, id_list)

			if result > 0:
				return 200

		return 0
	
	@staticmethod
	def put_con_out(id, prop_name, con_out_table) -> Response:
		project_db = request.headers.get(rh.PROJECT_DB)
		has_db,error = rh.init(project_db)
		if not has_db: abort(400, error)

		try:
			args = request.json

			params = {
				'order': args['order'],
				'obj_typ': args['obj_typ'],
				'obj_id': args['obj_id'],
				'hyd_typ': args['hyd_typ'],
				'frac': args['frac']
			}

			result = con_out_table.update(params).where(con_out_table.id == id).execute()

			rh.close()
			if result > 0:
				return '', 200

			abort(400, 'Unable to update outflow {id}.'.format(id=id))
		except con_out_table.DoesNotExist:
			rh.close()
			abort(404, 'Outflow {id} does not exist'.format(id=id))
		except Exception as ex:
			rh.close()
			abort(400, 'Unexpected error {ex}'.format(ex=ex))

	@staticmethod
	def post_con_out(prop_name, con_out_table) -> Response:
		project_db = request.headers.get(rh.PROJECT_DB)
		has_db,error = rh.init(project_db)
		if not has_db: abort(400, error)

		try:
			args = request.json

			params = {
				'order': args['order'],
				'obj_typ': args['obj_typ'],
				'obj_id': args['obj_id'],
				'hyd_typ': args['hyd_typ'],
				'frac': args['frac']
			}
			params['{}_id'.format(prop_name)] = args['{}_id'.format(prop_name)]

			result = con_out_table.insert(params).execute()

			rh.close()
			if result > 0:
				return '', 201

			abort(400, 'Unable to create outflow.')
		except Exception as ex:
			rh.close()
			abort(400, 'Unexpected error {ex}'.format(ex=ex))
		

class RestHelpers:
	__invalid_name_msg = 'Invalid name {name}. Please ensure the value exists in your database.'

	@staticmethod
	def has_arg(args, name):
		missing = name not in args or args[name] is None or args[name] == ''
		return not missing

	@staticmethod
	def get_arg(args, name, default):
		return default if not RestHelpers.has_arg(args, name) else args[name]
	
	@staticmethod
	def save_args(table, args, id=0, is_new=False, lookup_fields=[], extra_args=[]):
		params = {}
		for field in table._meta.sorted_fields:
			if field.column_name in args or field.name in args:
				if field.name in lookup_fields:
					d = ast.literal_eval(args[field.name])
					params[field.name] = int(d['id'])
				elif field.column_name in lookup_fields:
					d = ast.literal_eval(args[field.column_name])
					params[field.column_name] = int(d['id'])
				else:
					params[field.column_name] = args[field.column_name]

		for extra in extra_args:
			params[extra['name']] = args[extra['name']]

		if is_new:
			query = table.insert(params)
		else:
			query = table.update(params).where(table.id == id)
		
		return query.execute()
	
	@staticmethod
	def get_id_from_name(table, value):
		if value is None or value == '':
			return None
			
		i = table.get(table.name == value)
		return i.id
	
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

	@staticmethod
	def get_con_item_dict(v):
		return {
			'id': v.id, 
			'name': v.name, 
			'area': v.area,  
			'lat': v.lat, 
			'lon': v.lon, 
			'elev': v.elev, 
			'wst':  None if v.wst is None else { 'id': v.wst.id, 'name': v.wst.name }, 
			'outflow': len(v.con_outs)
		}
	
	@staticmethod
	def get_prop_dict(item):
		return None if item is None else { 'id' : item.id, 'name': item.name }
