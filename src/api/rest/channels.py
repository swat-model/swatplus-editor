from flask import Blueprint, request, abort
from .config import RequestHeaders as rh

from playhouse.shortcuts import model_to_dict
from peewee import *

from .defaults import DefaultRestMethods, RestHelpers
from database.project.connect import Channel_con, Chandeg_con, Chandeg_con_out
from database.project.channel import Channel_cha, Initial_cha, Hydrology_cha, Sediment_cha, Nutrients_cha, Channel_lte_cha, Hyd_sed_lte_cha
from database.project.climate import Weather_sta_cli
from database.project.init import Om_water_ini, Pest_water_ini, Path_water_ini, Hmet_water_ini, Salt_water_ini

bp = Blueprint('channels', __name__, url_prefix='/channels')

@bp.route('/type', methods=['GET'])
def getType():
	project_db = request.headers.get(rh.PROJECT_DB)
	has_db,error = rh.init(project_db)
	if not has_db: abort(400, error)

	cha_type = 'lte'
	if Channel_con.select().count() > 0:
		cha_type = 'regular'

	return { 'type': cha_type }

# Chandeg.con

@bp.route('/items', methods=['GET', 'POST'])
def con():
	if request.method == 'GET':
		table = Chandeg_con
		prop_table = Channel_lte_cha
		filter_cols = [table.name, table.wst, prop_table.init, prop_table.hyd, prop_table.nut]
		table_lookups = {
			table.wst: Weather_sta_cli
		}
		props_lookups = {
			prop_table.init: Initial_cha,
			prop_table.hyd: Hyd_sed_lte_cha,
			prop_table.nut: Nutrients_cha
		}

		items = DefaultRestMethods.get_paged_items_con(table, prop_table, filter_cols, table_lookups, props_lookups)
		ml = []
		for v in items['model']:
			d = RestHelpers.get_con_item_dict(v)
			d['init'] = RestHelpers.get_prop_dict(v.lcha.init)
			d['hyd'] = RestHelpers.get_prop_dict(v.lcha.hyd)
			d['nut'] = RestHelpers.get_prop_dict(v.lcha.nut)
			ml.append(d)
		
		return {
			'total': items['total'],
			'matches': items['matches'],
			'items': ml
		}
	elif request.method == 'POST':
		return DefaultRestMethods.post_con('lcha', Chandeg_con, Channel_lte_cha)
	abort(405, 'HTTP Method not allowed.')

@bp.route('/items/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def conId(id):
	if request.method == 'GET':
		return DefaultRestMethods.get(id, Chandeg_con, 'Channel', True)
	elif request.method == 'PUT':
		return DefaultRestMethods.put_con(id, 'lcha', Chandeg_con, Channel_lte_cha)
	elif request.method == 'DELETE':
		return DefaultRestMethods.delete(id, Chandeg_con, 'Channel', 'lcha', Channel_lte_cha)
	abort(405, 'HTTP Method not allowed.')

@bp.route('/out', methods=['POST'])
def conOut():
	return DefaultRestMethods.post_con_out('chandeg_con', Chandeg_con_out)

@bp.route('/out/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def conOutId(id):
	if request.method == 'GET':
		return DefaultRestMethods.get(id, Chandeg_con_out, 'Outflow', True)
	elif request.method == 'PUT':
		return DefaultRestMethods.put_con_out(id, 'chandeg_con', Chandeg_con_out)
	elif request.method == 'DELETE':
		return DefaultRestMethods.delete(id, Chandeg_con_out, 'Outflow')
	abort(405, 'HTTP Method not allowed.')

# Initial.cha

@bp.route('/initial', methods=['GET', 'POST'])
def init():
	if request.method == 'GET':
		table = Initial_cha
		filter_cols = [table.name]
		return DefaultRestMethods.get_paged_list(table, filter_cols, True)
	elif request.method == 'POST':
		project_db = request.headers.get(rh.PROJECT_DB)
		has_db,error = rh.init(project_db)
		if not has_db: abort(400, error)

		args = request.json
		try:
			m = Initial_cha()
			m.name = args['name']
			m.description = args['description']
			m.org_min_id = RestHelpers.get_id_from_name(Om_water_ini, args['org_min_name'])
			if args['pest_name']:
				m.pest_id = RestHelpers.get_id_from_name(Pest_water_ini, args['pest_name'])
			if args['path_name']:
				m.path_id = RestHelpers.get_id_from_name(Path_water_ini, args['path_name'])
			if args['hmet_name']:
				m.hmet_id = RestHelpers.get_id_from_name(Hmet_water_ini, args['hmet_name'])
			if args['salt_name']:
				m.salt_id = RestHelpers.get_id_from_name(Salt_water_ini, args['salt_name'])
			result = m.save()

			rh.close()
			if result > 0:
				return model_to_dict(m), 201

			abort(400, 'Unable to update initial channel properties {id}.'.format(id=id))
		except IntegrityError as e:
			rh.close()
			abort(400, 'Initial channel properties name must be unique.')
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
def initId(id):
	if request.method == 'GET':
		return DefaultRestMethods.get(id, Initial_cha, 'Channel', True)
	elif request.method == 'DELETE':
		return DefaultRestMethods.delete(id, Initial_cha, 'Channel')
	elif request.method == 'PUT':
		project_db = request.headers.get(rh.PROJECT_DB)
		has_db,error = rh.init(project_db)
		if not has_db: abort(400, error)

		args = request.json
		try:
			m = Initial_cha.get(Initial_cha.id == id)
			m.name = args['name']
			m.description = args['description']
			m.org_min_id = RestHelpers.get_id_from_name(Om_water_ini, args['org_min_name'])
			if args['pest_name']:
				m.pest_id = RestHelpers.get_id_from_name(Pest_water_ini, args['pest_name'])
			if args['path_name']:
				m.path_id = RestHelpers.get_id_from_name(Path_water_ini, args['path_name'])
			if args['hmet_name']:
				m.hmet_id = RestHelpers.get_id_from_name(Hmet_water_ini, args['hmet_name'])
			if args['salt_name']:
				m.salt_id = RestHelpers.get_id_from_name(Salt_water_ini, args['salt_name'])
			result = m.save()

			rh.close()
			if result > 0:
				return '', 200

			abort(400, 'Unable to update initial channel properties {id}.'.format(id=id))
		except IntegrityError as e:
			rh.close()
			abort(400, 'Initial channel properties name must be unique.')
		except Initial_cha.DoesNotExist:
			rh.close()
			abort(404, 'Initial channel properties {id} does not exist'.format(id=id))
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
def initMany():
	if request.method == 'GET':
		return DefaultRestMethods.get_name_id_list(Initial_cha)
	elif request.method == 'PUT':
		project_db = request.headers.get(rh.PROJECT_DB)
		has_db,error = rh.init(project_db)
		if not has_db: abort(400, error)

		args = request.json
		try:
			param_dict = {}

			if args['org_min_name'] is not None:
				param_dict['org_min_id'] = RestHelpers.get_id_from_name(Om_water_ini, args['org_min_name'])
			if args['pest_name'] is not None:
				param_dict['pest_id'] = RestHelpers.get_id_from_name(Pest_water_ini, args['pest_name'])
			if args['path_name'] is not None:
				param_dict['path_id'] = RestHelpers.get_id_from_name(Path_water_ini, args['path_name'])
			if args['hmet_name'] is not None:
				param_dict['hmet_id'] = RestHelpers.get_id_from_name(Hmet_water_ini, args['hmet_name'])
			if args['salt_name'] is not None:
				param_dict['salt_id'] = RestHelpers.get_id_from_name(Salt_water_ini, args['salt_name'])

			query = Initial_cha.update(param_dict).where(Initial_cha.id.in_(args['selected_ids']))
			result = query.execute()

			rh.close()
			if result > 0:
				return '', 200

			abort(400, 'Unable to update channel initial properties.')
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

# Nutrients.cha

@bp.route('/nutrients', methods=['GET', 'POST'])
def nutrients():
	if request.method == 'GET':
		table = Nutrients_cha
		filter_cols = [table.name]
		return DefaultRestMethods.get_paged_list(table, filter_cols, True)
	elif request.method == 'POST':
		return DefaultRestMethods.post(Nutrients_cha, 'Channel')
	abort(405, 'HTTP Method not allowed.')

@bp.route('/nutrients/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def nutrientsId(id):
	if request.method == 'GET':
		return DefaultRestMethods.get(id, Nutrients_cha, 'Channel')
	elif request.method == 'DELETE':
		return DefaultRestMethods.delete(id, Nutrients_cha, 'Channel')
	elif request.method == 'PUT':
		return DefaultRestMethods.put(id, Nutrients_cha, 'Channel')

	abort(405, 'HTTP Method not allowed.')

@bp.route('/nutrients/many', methods=['GET', 'PUT'])
def nutrientsMany():
	if request.method == 'GET':
		return DefaultRestMethods.get_name_id_list(Nutrients_cha)
	elif request.method == 'PUT':
		return DefaultRestMethods.put_many(Nutrients_cha, 'Channel')
	
	abort(405, 'HTTP Method not allowed.')

# Hyd-sed-lte.cha

@bp.route('/hydsed', methods=['GET', 'POST'])
def hydsed():
	if request.method == 'GET':
		table = Hyd_sed_lte_cha
		filter_cols = [table.name]
		return DefaultRestMethods.get_paged_list(table, filter_cols, True)
	elif request.method == 'POST':
		return DefaultRestMethods.post(Hyd_sed_lte_cha, 'Channel')
	abort(405, 'HTTP Method not allowed.')

@bp.route('/hydsed/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def hydsedId(id):
	if request.method == 'GET':
		return DefaultRestMethods.get(id, Hyd_sed_lte_cha, 'Channel')
	elif request.method == 'DELETE':
		return DefaultRestMethods.delete(id, Hyd_sed_lte_cha, 'Channel')
	elif request.method == 'PUT':
		return DefaultRestMethods.put(id, Hyd_sed_lte_cha, 'Channel')

	abort(405, 'HTTP Method not allowed.')

@bp.route('/hydsed/many', methods=['GET', 'PUT'])
def hydsedMany():
	if request.method == 'GET':
		return DefaultRestMethods.get_name_id_list(Hyd_sed_lte_cha)
	elif request.method == 'PUT':
		return DefaultRestMethods.put_many(Hyd_sed_lte_cha, 'Channel')
	
	abort(405, 'HTTP Method not allowed.')

# Channel-lte.cha

@bp.route('/properties', methods=['GET', 'POST'])
def properties():
	if request.method == 'GET':
		table = Channel_lte_cha
		filter_cols = [table.name]
		return DefaultRestMethods.get_paged_list(table, filter_cols, True)
	elif request.method == 'POST':
		project_db = request.headers.get(rh.PROJECT_DB)
		has_db,error = rh.init(project_db)
		if not has_db: abort(400, error)

		args = request.json
		try:
			m = Channel_lte_cha()
			m.name = args['name']
			m.description = args['description']
			m.init_id = RestHelpers.get_id_from_name(Initial_cha, args['init_name'])
			m.hyd_id = RestHelpers.get_id_from_name(Hyd_sed_lte_cha, args['hyd_name'])
			m.nut_id = RestHelpers.get_id_from_name(Nutrients_cha, args['nut_name'])

			result = m.save()

			rh.close()
			if result > 0:
				return {'id': m.id }, 200

			abort(400, 'Unable to update channel properties {id}.'.format(id=id))
		except IntegrityError as e:
			rh.close()
			abort(400, 'Channel properties name must be unique.')
		except Initial_cha.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['init_name']))
		except Hyd_sed_lte_cha.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['hyd_name']))
		except Nutrients_cha.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['nut_name']))
		except Exception as ex:
			rh.close()
			abort(400, 'Unexpected error {ex}'.format(ex=ex))
	
	abort(405, 'HTTP Method not allowed.')

@bp.route('/properties/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def propertiesId(id):
	if request.method == 'GET':
		return DefaultRestMethods.get(id, Channel_lte_cha, 'Channel', True)
	elif request.method == 'DELETE':
		return DefaultRestMethods.delete(id, Channel_lte_cha, 'Channel')
	elif request.method == 'PUT':
		project_db = request.headers.get(rh.PROJECT_DB)
		has_db,error = rh.init(project_db)
		if not has_db: abort(400, error)

		args = request.json
		try:
			m = Channel_lte_cha.get(Channel_lte_cha.id == id)
			m.name = args['name']
			m.description = args['description']
			m.init_id = RestHelpers.get_id_from_name(Initial_cha, args['init_name'])
			m.hyd_id = RestHelpers.get_id_from_name(Hyd_sed_lte_cha, args['hyd_name'])
			m.nut_id = RestHelpers.get_id_from_name(Nutrients_cha, args['nut_name'])

			result = m.save()

			rh.close()
			if result > 0:
				return '', 200

			abort(400, 'Unable to update channel properties {id}.'.format(id=id))
		except IntegrityError as e:
			rh.close()
			abort(400, 'Channel properties name must be unique.')
		except Channel_lte_cha.DoesNotExist:
			rh.close()
			abort(404, 'Channel properties {id} does not exist'.format(id=id))
		except Initial_cha.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['init_name']))
		except Hyd_sed_lte_cha.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['hyd_name']))
		except Nutrients_cha.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['nut_name']))
		except Exception as ex:
			rh.close()
			abort(400, 'Unexpected error {ex}'.format(ex=ex))

	abort(405, 'HTTP Method not allowed.')

@bp.route('/properties/many', methods=['GET', 'PUT'])
def propertiesMany():
	if request.method == 'GET':
		return DefaultRestMethods.get_name_id_list(Channel_lte_cha)
	elif request.method == 'PUT':
		project_db = request.headers.get(rh.PROJECT_DB)
		has_db,error = rh.init(project_db)
		if not has_db: abort(400, error)

		args = request.json
		try:
			param_dict = {}

			if args['init_name'] is not None:
				param_dict['init_id'] = RestHelpers.get_id_from_name(Initial_cha, args['init_name'])
			if args['hyd_name'] is not None:
				param_dict['hyd_id'] = RestHelpers.get_id_from_name(Hyd_sed_lte_cha, args['hyd_name'])
			if args['nut_name'] is not None:
				param_dict['nut_id'] = RestHelpers.get_id_from_name(Nutrients_cha, args['nut_name'])

			con_table = Chandeg_con
			con_prop_field = Chandeg_con.lcha_id
			prop_table = Channel_lte_cha

			result = RestHelpers.put_many_con(args, param_dict, con_table, con_prop_field, prop_table)
			rh.close()
			if result > 0:
				return '', 200

			abort(400, 'Unable to update channel properties.')
		except Initial_cha.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['init_name']))
		except Hyd_sed_lte_cha.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['hyd_name']))
		except Nutrients_cha.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['nut_name']))
		except Weather_sta_cli.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['wst_name']))
		except Exception as ex:
			rh.close()
			abort(400, 'Unexpected error {ex}'.format(ex=ex))
	
	abort(405, 'HTTP Method not allowed.')
