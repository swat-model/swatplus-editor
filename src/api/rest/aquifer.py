from flask import Blueprint, request, abort
from .config import RequestHeaders as rh

from playhouse.shortcuts import model_to_dict
from peewee import *

from .defaults import DefaultRestMethods, RestHelpers
from database.project.connect import Aquifer_con, Aquifer_con_out
from database.project.aquifer import Aquifer_aqu, Initial_aqu
from database.project.climate import Weather_sta_cli
from database.project.init import Om_water_ini, Pest_water_ini, Path_water_ini, Hmet_water_ini, Salt_water_ini

bp = Blueprint('aquifers', __name__, url_prefix='/aquifers')

@bp.route('/items', methods=['GET', 'POST'])
def con():
	if request.method == 'GET':
		table = Aquifer_con
		prop_table = Aquifer_aqu
		filter_cols = [table.name, table.wst, prop_table.init]
		table_lookups = {
			table.wst: Weather_sta_cli
		}
		props_lookups = {
			prop_table.init: Initial_aqu
		}

		items = DefaultRestMethods.get_paged_items_con(table, prop_table, filter_cols, table_lookups, props_lookups)
		ml = []
		for v in items['model']:
			d = RestHelpers.get_con_item_dict(v)
			d2 = model_to_dict(v.aqu, recurse=False)
			d3 = {**d, **d2}
			d3['init'] = RestHelpers.get_prop_dict(v.aqu.init)
			ml.append(d3)
		
		return {
			'total': items['total'],
			'matches': items['matches'],
			'items': ml
		}
	elif request.method == 'POST':
		return DefaultRestMethods.post_con('aqu', Aquifer_con, Aquifer_aqu)
	abort(405, 'HTTP Method not allowed.')

@bp.route('/items/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def conId(id):
	if request.method == 'GET':
		return DefaultRestMethods.get(id, Aquifer_con, 'Aquifer', True)
	elif request.method == 'PUT':
		return DefaultRestMethods.put_con(id, 'aqu', Aquifer_con, Aquifer_aqu)
	elif request.method == 'DELETE':
		return DefaultRestMethods.delete(id, Aquifer_con, 'Aquifer', 'aqu', Aquifer_aqu)
	abort(405, 'HTTP Method not allowed.')

@bp.route('/out', methods=['POST'])
def conOut():
	return DefaultRestMethods.post_con_out('aquifer_con', Aquifer_con_out)

@bp.route('/out/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def conOutId(id):
	if request.method == 'GET':
		return DefaultRestMethods.get(id, Aquifer_con_out, 'Outflow', True)
	elif request.method == 'PUT':
		return DefaultRestMethods.put_con_out(id, 'aquifer_con', Aquifer_con_out)
	elif request.method == 'DELETE':
		return DefaultRestMethods.delete(id, Aquifer_con_out, 'Outflow')
	abort(405, 'HTTP Method not allowed.')

# Aquifer.aqu

@bp.route('/properties', methods=['GET', 'POST'])
def properties():
	if request.method == 'GET':
		table = Aquifer_aqu
		filter_cols = [table.name]
		return DefaultRestMethods.get_paged_list(table, filter_cols, True)
	elif request.method == 'POST':
		project_db = request.headers.get(rh.PROJECT_DB)
		has_db,error = rh.init(project_db)
		if not has_db: abort(400, error)

		args = request.json
		try:
			result = RestHelpers.save_args(Aquifer_aqu, args, is_new=True, lookup_fields=['init'])

			rh.close()
			if result > 0:
				return {'id': result }, 200

			abort(400, 'Unable to update properties {id}.'.format(id=id))
		except IntegrityError as e:
			rh.close()
			abort(400, 'Name must be unique.')
		except Exception as ex:
			rh.close()
			abort(400, 'Unexpected error {ex}'.format(ex=ex))
	
	abort(405, 'HTTP Method not allowed.')

@bp.route('/properties/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def propertiesId(id):
	if request.method == 'GET':
		return DefaultRestMethods.get(id, Aquifer_aqu, 'Aquifer', True)
	elif request.method == 'DELETE':
		return DefaultRestMethods.delete(id, Aquifer_aqu, 'Aquifer')
	elif request.method == 'PUT':
		project_db = request.headers.get(rh.PROJECT_DB)
		has_db,error = rh.init(project_db)
		if not has_db: abort(400, error)

		args = request.json
		try:
			result = RestHelpers.save_args(Aquifer_aqu, args, id=id, lookup_fields=['init'])

			rh.close()
			if result > 0:
				return '', 200

			abort(400, 'Unable to update properties {id}.'.format(id=id))
		except IntegrityError as e:
			rh.close()
			abort(400, 'Name must be unique.')
		except Aquifer_aqu.DoesNotExist:
			rh.close()
			abort(400, 'Aquifer properties {id} does not exist'.format(id=id))
		except Exception as ex:
			rh.close()
			abort(400, 'Unexpected error {ex}'.format(ex=ex))

	abort(405, 'HTTP Method not allowed.')

@bp.route('/properties/many', methods=['GET', 'PUT'])
def propertiesMany():
	if request.method == 'GET':
		return DefaultRestMethods.get_name_id_list(Aquifer_aqu)
	elif request.method == 'PUT':
		project_db = request.headers.get(rh.PROJECT_DB)
		has_db,error = rh.init(project_db)
		if not has_db: abort(400, error)

		args = request.json
		try:
			lookup_fields = ['init']

			param_dict = {}
			for key in args.keys():
				if key in args and key != 'selected_ids':
					if key in lookup_fields:
						d = args[key]
						if int(d['id']) != 0:
							param_dict[key] = int(d['id'])
					else:
						param_dict[key] = args[key]

			con_table = Aquifer_con
			con_prop_field = Aquifer_con.aqu_id
			prop_table = Aquifer_aqu

			result = DefaultRestMethods.put_many_con(args, param_dict, con_table, con_prop_field, prop_table)
			rh.close()
			if result > 0:
				return '', 200

			abort(400, 'Unable to update hru properties.')
		except Exception as ex:
			rh.close()
			abort(400, 'Unexpected error {ex}'.format(ex=ex))
	
	abort(405, 'HTTP Method not allowed.')

# Initial.aqu

@bp.route('/initial', methods=['GET', 'POST'])
def initial():
	if request.method == 'GET':
		table = Initial_aqu
		filter_cols = [table.name, table.rtu, table.obj_typ, table.dlr]
		return DefaultRestMethods.get_paged_list(table, filter_cols, True)
	elif request.method == 'POST':
		project_db = request.headers.get(rh.PROJECT_DB)
		has_db,error = rh.init(project_db)
		if not has_db: abort(400, error)

		args = request.json
		try:
			m = Initial_aqu()
			m.name = args['name']
			m.description = None if 'description' not in args else args['description']
			if 'org_min_name' in args:
				m.org_min_id = RestHelpers.get_id_from_name(Om_water_ini, args['org_min_name'])
			if 'pest_name' in args:
				m.pest_id = RestHelpers.get_id_from_name(Pest_water_ini, args['pest_name'])
			if 'path_name' in args:
				m.path_id = RestHelpers.get_id_from_name(Path_water_ini, args['path_name'])
			if 'hmet_name' in args:
				m.hmet_id = RestHelpers.get_id_from_name(Hmet_water_ini, args['hmet_name'])
			if 'salt_name' in args:
				m.salt_id = RestHelpers.get_id_from_name(Salt_water_ini, args['salt_name'])
			result = m.save()

			rh.close()
			if result > 0:
				return model_to_dict(m), 201

			abort(400, 'Unable to update properties {id}.'.format(id=id))
		except IntegrityError as e:
			rh.close()
			abort(400, 'Name must be unique.')
		except Om_water_ini.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['org_min_name']))
		except Pest_water_ini.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['pest_name']))
		except Path_water_ini.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['path_name']))
		except Hmet_water_ini.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['hmet_name']))
		except Salt_water_ini.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['salt_name']))
		except Exception as ex:
			rh.close()
			abort(400, 'Unexpected error {ex}'.format(ex=ex))
	abort(405, 'HTTP Method not allowed.')

@bp.route('/initial/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def initialId(id):
	if request.method == 'GET':
		return DefaultRestMethods.get(id, Initial_aqu, 'Aquifer', back_refs=True)
	elif request.method == 'DELETE':
		return DefaultRestMethods.delete(id, Initial_aqu, 'Aquifer')
	elif request.method == 'PUT':
		project_db = request.headers.get(rh.PROJECT_DB)
		has_db,error = rh.init(project_db)
		if not has_db: abort(400, error)

		args = request.json
		try:
			m = Initial_aqu.get(Initial_aqu.id == id)
			m.name = args['name']
			m.description = None if 'description' not in args else args['description']
			if 'org_min_name' in args:
				m.org_min_id = RestHelpers.get_id_from_name(Om_water_ini, args['org_min_name'])
			if 'pest_name' in args:
				m.pest_id = RestHelpers.get_id_from_name(Pest_water_ini, args['pest_name'])
			if 'path_name' in args:
				m.path_id = RestHelpers.get_id_from_name(Path_water_ini, args['path_name'])
			if 'hmet_name' in args:
				m.hmet_id = RestHelpers.get_id_from_name(Hmet_water_ini, args['hmet_name'])
			if 'salt_name' in args:
				m.salt_id = RestHelpers.get_id_from_name(Salt_water_ini, args['salt_name'])

			result = m.save()

			rh.close()
			if result > 0:
				return '', 200

			abort(400, 'Unable to update properties {id}.'.format(id=id))
		except IntegrityError as e:
			rh.close()
			abort(400, 'Name must be unique.')
		except Om_water_ini.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['org_min_name']))
		except Pest_water_ini.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['pest_name']))
		except Path_water_ini.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['path_name']))
		except Hmet_water_ini.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['hmet_name']))
		except Salt_water_ini.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['salt_name']))
		except Exception as ex:
			rh.close()
			abort(400, 'Unexpected error {ex}'.format(ex=ex))

	abort(405, 'HTTP Method not allowed.')

@bp.route('/initial/many', methods=['GET', 'PUT'])
def initialMany():
	if request.method == 'GET':
		return DefaultRestMethods.get_name_id_list(Initial_aqu)
	elif request.method == 'PUT':
		project_db = request.headers.get(rh.PROJECT_DB)
		has_db,error = rh.init(project_db)
		if not has_db: abort(400, error)

		args = request.json
		try:
			param_dict = {}

			if 'org_min_name' in args:
				param_dict['org_min_id'] = RestHelpers.get_id_from_name(Om_water_ini, args['org_min_name'])
			if 'pest_name' in args:
				param_dict['pest_id'] = RestHelpers.get_id_from_name(Pest_water_ini, args['pest_name'])
			if 'path_name' in args:
				param_dict['path_id'] = RestHelpers.get_id_from_name(Path_water_ini, args['path_name'])
			if 'hmet_name' in args:
				param_dict['hmet_id'] = RestHelpers.get_id_from_name(Hmet_water_ini, args['hmet_name'])
			if 'salt_name' in args:
				param_dict['salt_id'] = RestHelpers.get_id_from_name(Salt_water_ini, args['salt_name'])

			query = Initial_aqu.update(param_dict).where(Initial_aqu.id.in_(args['selected_ids']))
			result = query.execute()

			rh.close()
			if result > 0:
				return '', 200

			abort(400, 'Unable to update properties.')
		except Om_water_ini.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['org_min_name']))
		except Pest_water_ini.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['pest_name']))
		except Path_water_ini.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['path_name']))
		except Hmet_water_ini.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['hmet_name']))
		except Salt_water_ini.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['salt_name']))
		except Exception as ex:
			rh.close()
			abort(400, 'Unexpected error {ex}'.format(ex=ex))
	
	abort(405, 'HTTP Method not allowed.')