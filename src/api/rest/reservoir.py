from flask import Blueprint, request, abort
from .config import RequestHeaders as rh

from playhouse.shortcuts import model_to_dict
from peewee import *

from .defaults import DefaultRestMethods, RestHelpers
from database.project.connect import Reservoir_con, Reservoir_con_out
from database.project.reservoir import Reservoir_res, Initial_res, Hydrology_res, Sediment_res, Nutrients_res, Wetland_wet, Hydrology_wet
from database.project.climate import Weather_sta_cli
from database.project.init import Om_water_ini, Pest_water_ini, Path_water_ini, Hmet_water_ini
from database.project.decision_table import D_table_dtl
from database.project.salts import Salt_res_ini

bp = Blueprint('reservoirs', __name__, url_prefix='/reservoirs')

@bp.route('/items', methods=['GET', 'POST'])
def con():
	if request.method == 'GET':
		table = Reservoir_con
		prop_table = Reservoir_res
		filter_cols = [table.name, table.wst, prop_table.init, prop_table.hyd, prop_table.rel, prop_table.sed, prop_table.nut]
		table_lookups = {
			table.wst: Weather_sta_cli
		}
		props_lookups = {
			prop_table.init: Initial_res,
			prop_table.hyd: Hydrology_res,
			prop_table.rel: D_table_dtl,
			prop_table.sed: Sediment_res,
			prop_table.nut: Nutrients_res
		}

		items = DefaultRestMethods.get_paged_items_con(table, prop_table, filter_cols, table_lookups, props_lookups)
		ml = []
		for v in items['model']:
			d = RestHelpers.get_con_item_dict(v)
			d['init'] = RestHelpers.get_prop_dict(v.res.init)
			d['hyd'] = RestHelpers.get_prop_dict(v.res.hyd)
			d['rel'] = RestHelpers.get_prop_dict(v.res.rel)
			d['sed'] = RestHelpers.get_prop_dict(v.res.sed)
			d['nut'] = RestHelpers.get_prop_dict(v.res.nut)
			ml.append(d)
		
		return {
			'total': items['total'],
			'matches': items['matches'],
			'items': ml
		}
	elif request.method == 'POST':
		return DefaultRestMethods.post_con('res', Reservoir_con, Reservoir_res)
	abort(405, 'HTTP Method not allowed.')

@bp.route('/items/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def conId(id):
	if request.method == 'GET':
		return DefaultRestMethods.get(id, Reservoir_con, 'Reservoir', True)
	elif request.method == 'PUT':
		return DefaultRestMethods.put_con(id, 'res', Reservoir_con, Reservoir_res)
	elif request.method == 'DELETE':
		return DefaultRestMethods.delete(id, Reservoir_con, 'Reservoir', 'res', Reservoir_res)
	abort(405, 'HTTP Method not allowed.')

@bp.route('/out', methods=['POST'])
def conOut():
	return DefaultRestMethods.post_con_out('reservoir_con', Reservoir_con_out)

@bp.route('/out/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def conOutId(id):
	if request.method == 'GET':
		return DefaultRestMethods.get(id, Reservoir_con_out, 'Outflow', True)
	elif request.method == 'PUT':
		return DefaultRestMethods.put_con_out(id, 'reservoir_con', Reservoir_con_out)
	elif request.method == 'DELETE':
		return DefaultRestMethods.delete(id, Reservoir_con_out, 'Outflow')
	abort(405, 'HTTP Method not allowed.')

# Reservoir.res

@bp.route('/properties', methods=['GET', 'POST'])
def properties():
	if request.method == 'GET':
		table = Reservoir_res
		filter_cols = [table.name]
		return DefaultRestMethods.get_paged_list(table, filter_cols, True)
	elif request.method == 'POST':
		project_db = request.headers.get(rh.PROJECT_DB)
		has_db,error = rh.init(project_db)
		if not has_db: abort(400, error)

		args = request.json
		try:
			m = Reservoir_res()
			m.name = args['name']
			m.description = None if 'description' not in args else args['description']

			if 'init_name' in args:
				m.init_id = RestHelpers.get_id_from_name(Initial_res, args['init_name'])
			if 'rel_name' in args:
				m.rel_id = RestHelpers.get_id_from_name(D_table_dtl, args['rel_name'])
			if 'hyd_name' in args:
				m.hyd_id = RestHelpers.get_id_from_name(Hydrology_res, args['hyd_name'])
			if 'sed_name' in args:
				m.sed_id = RestHelpers.get_id_from_name(Sediment_res, args['sed_name'])
			if 'nut_name' in args:
				m.nut_id = RestHelpers.get_id_from_name(Nutrients_res, args['nut_name'])

			result = m.save()

			rh.close()
			if result > 0:
				return {'id': m.id }, 200

			abort(400, 'Unable to update properties {id}.'.format(id=id))
		except IntegrityError as e:
			rh.close()
			abort(400, 'Name must be unique.')
		except Initial_res.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['init_name']))
		except D_table_dtl.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['rel_name']))
		except Hydrology_res.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['hyd_name']))
		except Sediment_res.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['sed_name']))
		except Nutrients_res.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['nut_name']))
		except Exception as ex:
			rh.close()
			abort(400, 'Unexpected error {ex}'.format(ex=ex))
	
	abort(405, 'HTTP Method not allowed.')

@bp.route('/properties/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def propertiesId(id):
	if request.method == 'GET':
		return DefaultRestMethods.get(id, Reservoir_res, 'Reservoir', True)
	elif request.method == 'DELETE':
		return DefaultRestMethods.delete(id, Reservoir_res, 'Reservoir')
	elif request.method == 'PUT':
		project_db = request.headers.get(rh.PROJECT_DB)
		has_db,error = rh.init(project_db)
		if not has_db: abort(400, error)

		args = request.json
		try:
			m = Reservoir_res.get(Reservoir_res.id == id)
			m.name = args['name']
			m.description = None if 'description' not in args else args['description']

			if 'init_name' in args:
				m.init_id = RestHelpers.get_id_from_name(Initial_res, args['init_name'])
			if 'rel_name' in args:
				m.rel_id = RestHelpers.get_id_from_name(D_table_dtl, args['rel_name'])
			if 'hyd_name' in args:
				m.hyd_id = RestHelpers.get_id_from_name(Hydrology_res, args['hyd_name'])
			if 'sed_name' in args:
				m.sed_id = RestHelpers.get_id_from_name(Sediment_res, args['sed_name'])
			if 'nut_name' in args:
				m.nut_id = RestHelpers.get_id_from_name(Nutrients_res, args['nut_name'])

			result = m.save()

			rh.close()
			if result > 0:
				return '', 200

			abort(400, 'Unable to update properties {id}.'.format(id=id))
		except IntegrityError as e:
			rh.close()
			abort(400, 'Name must be unique.')
		except Reservoir_res.DoesNotExist:
			rh.close()
			abort(400, 'Reservoir properties {id} does not exist'.format(id=id))
		except Initial_res.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['init_name']))
		except D_table_dtl.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['rel_name']))
		except Hydrology_res.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['hyd_name']))
		except Sediment_res.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['sed_name']))
		except Nutrients_res.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['nut_name']))
		except Exception as ex:
			rh.close()
			abort(400, 'Unexpected error {ex}'.format(ex=ex))

	abort(405, 'HTTP Method not allowed.')

@bp.route('/properties/many', methods=['GET', 'PUT'])
def propertiesMany():
	if request.method == 'GET':
		return DefaultRestMethods.get_name_id_list(Reservoir_res)
	elif request.method == 'PUT':
		project_db = request.headers.get(rh.PROJECT_DB)
		has_db,error = rh.init(project_db)
		if not has_db: abort(400, error)

		args = request.json
		try:
			param_dict = {}

			if 'init_name' in args:
				param_dict['init_id'] = RestHelpers.get_id_from_name(Initial_res, args['init_name'])
			if 'rel_name' in args:
				param_dict['rel_id'] = RestHelpers.get_id_from_name(D_table_dtl, args['rel_name'])
			if 'hyd_name' in args:
				param_dict['hyd_id'] = RestHelpers.get_id_from_name(Hydrology_res, args['hyd_name'])
			if 'sed_name' in args:
				param_dict['sed_id'] = RestHelpers.get_id_from_name(Sediment_res, args['sed_name'])
			if 'nut_name' in args:
				param_dict['nut_id'] = RestHelpers.get_id_from_name(Nutrients_res, args['nut_name'])

			con_table = Reservoir_con
			con_prop_field = Reservoir_con.res_id
			prop_table = Reservoir_res

			result = DefaultRestMethods.put_many_con(args, param_dict, con_table, con_prop_field, prop_table)
			rh.close()
			if result > 0:
				return '', 200

			abort(400, 'Unable to update hru properties.')
		except Initial_res.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['init_name']))
		except D_table_dtl.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['rel_name']))
		except Hydrology_res.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['hyd_name']))
		except Sediment_res.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['sed_name']))
		except Nutrients_res.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['nut_name']))
		except Exception as ex:
			rh.close()
			abort(400, 'Unexpected error {ex}'.format(ex=ex))
	
	abort(405, 'HTTP Method not allowed.')

# Initial.res

@bp.route('/initial', methods=['GET', 'POST'])
def initial():
	if request.method == 'GET':
		table = Initial_res
		filter_cols = [table.name]
		return DefaultRestMethods.get_paged_list(table, filter_cols, True)
	elif request.method == 'POST':
		project_db = request.headers.get(rh.PROJECT_DB)
		has_db,error = rh.init(project_db)
		if not has_db: abort(400, error)

		args = request.json
		try:
			m = Initial_res()
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
				m.salt_cs_id = RestHelpers.get_id_from_name(Salt_res_ini, args['salt_name'])
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
		except Salt_res_ini.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['salt_name']))
		except Exception as ex:
			rh.close()
			abort(400, 'Unexpected error {ex}'.format(ex=ex))
	abort(405, 'HTTP Method not allowed.')

@bp.route('/initial/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def initialId(id):
	if request.method == 'GET':
		return DefaultRestMethods.get(id, Initial_res, 'Reservoir', back_refs=True)
	elif request.method == 'DELETE':
		return DefaultRestMethods.delete(id, Initial_res, 'Reservoir')
	elif request.method == 'PUT':
		project_db = request.headers.get(rh.PROJECT_DB)
		has_db,error = rh.init(project_db)
		if not has_db: abort(400, error)

		args = request.json
		try:
			m = Initial_res.get(Initial_res.id == id)
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
				m.salt_cs_id = RestHelpers.get_id_from_name(Salt_res_ini, args['salt_name'])

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
		except Salt_res_ini.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['salt_name']))
		except Exception as ex:
			rh.close()
			abort(400, 'Unexpected error {ex}'.format(ex=ex))

	abort(405, 'HTTP Method not allowed.')

@bp.route('/initial/many', methods=['GET', 'PUT'])
def initialMany():
	if request.method == 'GET':
		return DefaultRestMethods.get_name_id_list(Initial_res)
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
				param_dict['salt_cs_id'] = RestHelpers.get_id_from_name(Salt_res_ini, args['salt_name'])

			query = Initial_res.update(param_dict).where(Initial_res.id.in_(args['selected_ids']))
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
		except Salt_res_ini.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['salt_name']))
		except Exception as ex:
			rh.close()
			abort(400, 'Unexpected error {ex}'.format(ex=ex))
	
	abort(405, 'HTTP Method not allowed.')

# Hydrology.res

@bp.route('/hydrology', methods=['GET', 'POST'])
def hyd():
	if request.method == 'GET':
		table = Hydrology_res
		filter_cols = [table.name]
		return DefaultRestMethods.get_paged_list(table, filter_cols)
	elif request.method == 'POST':
		return DefaultRestMethods.post(Hydrology_res, 'Reservoir')
	abort(405, 'HTTP Method not allowed.')

@bp.route('/hydrology/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def hydId(id):
	if request.method == 'GET':
		return DefaultRestMethods.get(id, Hydrology_res, 'Reservoir')
	elif request.method == 'DELETE':
		return DefaultRestMethods.delete(id, Hydrology_res, 'Reservoir')
	elif request.method == 'PUT':
		return DefaultRestMethods.put(id, Hydrology_res, 'Reservoir')

	abort(405, 'HTTP Method not allowed.')

@bp.route('/hydrology/many', methods=['GET', 'PUT'])
def hydMany():
	if request.method == 'GET':
		return DefaultRestMethods.get_name_id_list(Hydrology_res)
	elif request.method == 'PUT':
		return DefaultRestMethods.put_many(Hydrology_res, 'Reservoir')
	
	abort(405, 'HTTP Method not allowed.')

# Sediment.res

@bp.route('/sediment', methods=['GET', 'POST'])
def sediment():
	if request.method == 'GET':
		table = Sediment_res
		filter_cols = [table.name]
		return DefaultRestMethods.get_paged_list(table, filter_cols)
	elif request.method == 'POST':
		return DefaultRestMethods.post(Sediment_res, 'Reservoir')
	abort(405, 'HTTP Method not allowed.')

@bp.route('/sediment/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def sedimentId(id):
	if request.method == 'GET':
		return DefaultRestMethods.get(id, Sediment_res, 'Reservoir')
	elif request.method == 'DELETE':
		return DefaultRestMethods.delete(id, Sediment_res, 'Reservoir')
	elif request.method == 'PUT':
		return DefaultRestMethods.put(id, Sediment_res, 'Reservoir')

	abort(405, 'HTTP Method not allowed.')

@bp.route('/sediment/many', methods=['GET', 'PUT'])
def sedimentMany():
	if request.method == 'GET':
		return DefaultRestMethods.get_name_id_list(Sediment_res)
	elif request.method == 'PUT':
		return DefaultRestMethods.put_many(Sediment_res, 'Reservoir')
	
	abort(405, 'HTTP Method not allowed.')

# Nutrients.res

@bp.route('/nutrients', methods=['GET', 'POST'])
def nutrients():
	if request.method == 'GET':
		table = Nutrients_res
		filter_cols = [table.name]
		return DefaultRestMethods.get_paged_list(table, filter_cols)
	elif request.method == 'POST':
		return DefaultRestMethods.post(Nutrients_res, 'Reservoir')
	abort(405, 'HTTP Method not allowed.')

@bp.route('/nutrients/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def nutrientsId(id):
	if request.method == 'GET':
		return DefaultRestMethods.get(id, Nutrients_res, 'Reservoir')
	elif request.method == 'DELETE':
		return DefaultRestMethods.delete(id, Nutrients_res, 'Reservoir')
	elif request.method == 'PUT':
		return DefaultRestMethods.put(id, Nutrients_res, 'Reservoir')

	abort(405, 'HTTP Method not allowed.')

@bp.route('/nutrients/many', methods=['GET', 'PUT'])
def nutrientsMany():
	if request.method == 'GET':
		return DefaultRestMethods.get_name_id_list(Nutrients_res)
	elif request.method == 'PUT':
		return DefaultRestMethods.put_many(Nutrients_res, 'Reservoir')
	
	abort(405, 'HTTP Method not allowed.')

# Wetland.wet

@bp.route('/wetlands', methods=['GET', 'POST'])
def wetlands():
	if request.method == 'GET':
		table = Wetland_wet
		filter_cols = [table.name]
		return DefaultRestMethods.get_paged_list(table, filter_cols, True)
	elif request.method == 'POST':
		project_db = request.headers.get(rh.PROJECT_DB)
		has_db,error = rh.init(project_db)
		if not has_db: abort(400, error)

		args = request.json
		try:
			m = Wetland_wet()
			m.name = args['name']
			m.description = None if 'description' not in args else args['description']
			if 'init_name' in args:
				m.init_id = RestHelpers.get_id_from_name(Initial_res, args['init_name'])
			if 'rel_name' in args:
				m.rel_id = RestHelpers.get_id_from_name(D_table_dtl, args['rel_name'])
			if 'hyd_name' in args:
				m.hyd_id = RestHelpers.get_id_from_name(Hydrology_wet, args['hyd_name'])
			if 'sed_name' in args:
				m.sed_id = RestHelpers.get_id_from_name(Sediment_res, args['sed_name'])
			if 'nut_name' in args:
				m.nut_id = RestHelpers.get_id_from_name(Nutrients_res, args['nut_name'])
			result = m.save()

			rh.close()
			if result > 0:
				return model_to_dict(m), 201

			abort(400, 'Unable to update properties {id}.'.format(id=id))
		except IntegrityError as e:
			rh.close()
			abort(400, 'Name must be unique.')
		except Initial_res.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['init_name']))
		except D_table_dtl.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['rel_name']))
		except Hydrology_wet.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['hyd_name']))
		except Sediment_res.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['sed_name']))
		except Nutrients_res.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['nut_name']))
		except Exception as ex:
			rh.close()
			abort(400, 'Unexpected error {ex}'.format(ex=ex))
	abort(405, 'HTTP Method not allowed.')

@bp.route('/wetlands/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def wetlandsId(id):
	if request.method == 'GET':
		return DefaultRestMethods.get(id, Wetland_wet, 'Reservoir', back_refs=True)
	elif request.method == 'DELETE':
		return DefaultRestMethods.delete(id, Wetland_wet, 'Reservoir')
	elif request.method == 'PUT':
		project_db = request.headers.get(rh.PROJECT_DB)
		has_db,error = rh.init(project_db)
		if not has_db: abort(400, error)

		args = request.json
		try:
			m = Wetland_wet.get(Wetland_wet.id == id)
			m.name = args['name']
			m.description = None if 'description' not in args else args['description']
			if 'init_name' in args:
				m.init_id = RestHelpers.get_id_from_name(Initial_res, args['init_name'])
			if 'rel_name' in args:
				m.rel_id = RestHelpers.get_id_from_name(D_table_dtl, args['rel_name'])
			if 'hyd_name' in args:
				m.hyd_id = RestHelpers.get_id_from_name(Hydrology_wet, args['hyd_name'])
			if 'sed_name' in args:
				m.sed_id = RestHelpers.get_id_from_name(Sediment_res, args['sed_name'])
			if 'nut_name' in args:
				m.nut_id = RestHelpers.get_id_from_name(Nutrients_res, args['nut_name'])

			result = m.save()

			rh.close()
			if result > 0:
				return '', 200

			abort(400, 'Unable to update properties {id}.'.format(id=id))
		except IntegrityError as e:
			rh.close()
			abort(400, 'Name must be unique.')
		except Initial_res.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['init_name']))
		except D_table_dtl.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['rel_name']))
		except Hydrology_wet.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['hyd_name']))
		except Sediment_res.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['sed_name']))
		except Nutrients_res.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['nut_name']))
		except Exception as ex:
			rh.close()
			abort(400, 'Unexpected error {ex}'.format(ex=ex))

	abort(405, 'HTTP Method not allowed.')

@bp.route('/wetlands/many', methods=['GET', 'PUT'])
def wetlandsMany():
	if request.method == 'GET':
		return DefaultRestMethods.get_name_id_list(Initial_res)
	elif request.method == 'PUT':
		project_db = request.headers.get(rh.PROJECT_DB)
		has_db,error = rh.init(project_db)
		if not has_db: abort(400, error)

		args = request.json
		try:
			param_dict = {}

			if 'init_name' in args:
				param_dict['init_id'] = RestHelpers.get_id_from_name(Initial_res, args['init_name'])
			if 'rel_name' in args:
				param_dict['rel_id'] = RestHelpers.get_id_from_name(D_table_dtl, args['rel_name'])
			if 'hyd_name' in args:
				param_dict['hyd_id'] = RestHelpers.get_id_from_name(Hydrology_wet, args['hyd_name'])
			if 'sed_name' in args:
				param_dict['sed_id'] = RestHelpers.get_id_from_name(Sediment_res, args['sed_name'])
			if 'nut_name' in args:
				param_dict['nut_id'] = RestHelpers.get_id_from_name(Nutrients_res, args['nut_name'])

			query = Wetland_wet.update(param_dict).where(Wetland_wet.id.in_(args['selected_ids']))
			result = query.execute()

			rh.close()
			if result > 0:
				return '', 200

			abort(400, 'Unable to update properties.')
		except Initial_res.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['init_name']))
		except D_table_dtl.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['rel_name']))
		except Hydrology_wet.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['hyd_name']))
		except Sediment_res.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['sed_name']))
		except Nutrients_res.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['nut_name']))
		except Exception as ex:
			rh.close()
			abort(400, 'Unexpected error {ex}'.format(ex=ex))
	
	abort(405, 'HTTP Method not allowed.')

# Hydrology.wet

@bp.route('/wetlands-hydrology', methods=['GET', 'POST'])
def wethyd():
	if request.method == 'GET':
		table = Hydrology_wet
		filter_cols = [table.name]
		return DefaultRestMethods.get_paged_list(table, filter_cols)
	elif request.method == 'POST':
		return DefaultRestMethods.post(Hydrology_wet, 'Reservoir')
	abort(405, 'HTTP Method not allowed.')

@bp.route('/wetlands-hydrology/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def wethydId(id):
	if request.method == 'GET':
		return DefaultRestMethods.get(id, Hydrology_wet, 'Reservoir')
	elif request.method == 'DELETE':
		return DefaultRestMethods.delete(id, Hydrology_wet, 'Reservoir')
	elif request.method == 'PUT':
		return DefaultRestMethods.put(id, Hydrology_wet, 'Reservoir')

	abort(405, 'HTTP Method not allowed.')

@bp.route('/wetlands-hydrology/many', methods=['GET', 'PUT'])
def wethydMany():
	if request.method == 'GET':
		return DefaultRestMethods.get_name_id_list(Hydrology_wet)
	elif request.method == 'PUT':
		return DefaultRestMethods.put_many(Hydrology_wet, 'Reservoir')
	
	abort(405, 'HTTP Method not allowed.')