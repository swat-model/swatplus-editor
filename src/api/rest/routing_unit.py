from flask import Blueprint, request, abort
from .config import RequestHeaders as rh

from playhouse.shortcuts import model_to_dict
from peewee import *

from .defaults import DefaultRestMethods, RestHelpers
from database.project.climate import Weather_sta_cli
from database.project.routing_unit import Rout_unit_rtu, Rout_unit_dr
from database.project.connect import Rout_unit_con, Rout_unit_con_out, Rout_unit_ele, Chandeg_con
from database.project.dr import Delratio_del
from database.project.hydrology import Topography_hyd, Field_fld

bp = Blueprint('routing_units', __name__, url_prefix='/routing-units')

@bp.route('/items', methods=['GET', 'POST'])
def con():
	if request.method == 'GET':
		table = Rout_unit_con
		prop_table = Rout_unit_rtu
		filter_cols = [table.name, table.wst, prop_table.dlr, prop_table.topo, prop_table.field]
		table_lookups = {
			table.wst: Weather_sta_cli
		}
		props_lookups = {
			prop_table.dlr: Rout_unit_dr,
			prop_table.topo: Topography_hyd,
			prop_table.field: Field_fld
		}

		items = DefaultRestMethods.get_paged_items_con(table, prop_table, filter_cols, table_lookups, props_lookups)
		ml = []
		for v in items['model']:
			d = RestHelpers.get_con_item_dict(v)
			d['dlr'] = RestHelpers.get_prop_dict(v.rtu.dlr)
			d['topo'] = RestHelpers.get_prop_dict(v.rtu.topo)
			d['field'] = RestHelpers.get_prop_dict(v.rtu.field)
			ml.append(d)
		
		return {
			'total': items['total'],
			'matches': items['matches'],
			'items': ml
		}
	elif request.method == 'POST':
		return DefaultRestMethods.post_con('rtu', Rout_unit_con, Rout_unit_rtu)
	abort(405, 'HTTP Method not allowed.')

@bp.route('/items/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def conId(id):
	if request.method == 'GET':
		return DefaultRestMethods.get(id, Rout_unit_con, 'Rout_unit', True)
	elif request.method == 'PUT':
		return DefaultRestMethods.put_con(id, 'rtu', Rout_unit_con, Rout_unit_rtu)
	elif request.method == 'DELETE':
		return DefaultRestMethods.delete(id, Rout_unit_con, 'Rout_unit', 'rtu', Rout_unit_rtu)
	abort(405, 'HTTP Method not allowed.')

@bp.route('/out', methods=['POST'])
def conOut():
	return DefaultRestMethods.post_con_out('rtu_con', Rout_unit_con_out)

@bp.route('/out/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def conOutId(id):
	if request.method == 'GET':
		return DefaultRestMethods.get(id, Rout_unit_con_out, 'Outflow', True)
	elif request.method == 'PUT':
		return DefaultRestMethods.put_con_out(id, 'rtu_con', Rout_unit_con_out)
	elif request.method == 'DELETE':
		return DefaultRestMethods.delete(id, Rout_unit_con_out, 'Outflow')
	abort(405, 'HTTP Method not allowed.')

# Rounting-unit.rtu

@bp.route('/properties', methods=['GET', 'POST'])
def properties():
	if request.method == 'GET':
		table = Rout_unit_rtu
		filter_cols = [table.name]
		return DefaultRestMethods.get_paged_list(table, filter_cols, True)
	elif request.method == 'POST':
		project_db = request.headers.get(rh.PROJECT_DB)
		has_db,error = rh.init(project_db)
		if not has_db: abort(400, error)

		args = request.json
		try:
			m = Rout_unit_rtu()
			m.name = args['name']
			m.description = None if 'description' not in args else args['description']
			if 'dlr_name' in args:
				m.dlr_id = RestHelpers.get_id_from_name(Delratio_del, args['dlr_name'])

			m.topo_id = RestHelpers.get_id_from_name(Topography_hyd, args['topo_name'])
			m.field_id = RestHelpers.get_id_from_name(Field_fld, args['field_name'])

			result = m.save()

			rh.close()
			if result > 0:
				return {'id': m.id }, 200

			abort(400, 'Unable to update properties {id}.'.format(id=id))
		except IntegrityError as e:
			rh.close()
			abort(400, 'Name must be unique.')
		except Topography_hyd.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['topo_name']))
		except Delratio_del.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['dlr_name']))
		except Topography_hyd.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['topo_name']))
		except Field_fld.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['field_name']))
		except Exception as ex:
			rh.close()
			abort(400, 'Unexpected error {ex}'.format(ex=ex))
	
	abort(405, 'HTTP Method not allowed.')

@bp.route('/properties/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def propertiesId(id):
	if request.method == 'GET':
		return DefaultRestMethods.get(id, Rout_unit_rtu, 'Rout_unit', True)
	elif request.method == 'DELETE':
		return DefaultRestMethods.delete(id, Rout_unit_rtu, 'Rout_unit')
	elif request.method == 'PUT':
		project_db = request.headers.get(rh.PROJECT_DB)
		has_db,error = rh.init(project_db)
		if not has_db: abort(400, error)

		args = request.json
		try:
			m = Rout_unit_rtu.get(Rout_unit_rtu.id == id)
			m.name = args['name']
			m.description = None if 'description' not in args else args['description']
			if 'dlr_name' in args:
				m.dlr_id = RestHelpers.get_id_from_name(Delratio_del, args['dlr_name'])
			if 'topo_name' in args:
				m.topo_id = RestHelpers.get_id_from_name(Topography_hyd, args['topo_name'])
			if 'field_name' in args:
				m.field_id = RestHelpers.get_id_from_name(Field_fld, args['field_name'])

			result = m.save()

			rh.close()
			if result > 0:
				return '', 200

			abort(400, 'Unable to update properties {id}.'.format(id=id))
		except IntegrityError as e:
			rh.close()
			abort(400, 'Name must be unique.')
		except Topography_hyd.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['topo_name']))
		except Delratio_del.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['dlr_name']))
		except Topography_hyd.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['topo_name']))
		except Field_fld.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['field_name']))
		except Exception as ex:
			rh.close()
			abort(400, 'Unexpected error {ex}'.format(ex=ex))

	abort(405, 'HTTP Method not allowed.')

@bp.route('/properties/many', methods=['GET', 'PUT'])
def propertiesMany():
	if request.method == 'GET':
		return DefaultRestMethods.get_name_id_list(Rout_unit_rtu)
	elif request.method == 'PUT':
		project_db = request.headers.get(rh.PROJECT_DB)
		has_db,error = rh.init(project_db)
		if not has_db: abort(400, error)

		args = request.json
		try:
			param_dict = {}

			if 'dlr_name' in args:
				param_dict['dlr_id'] = RestHelpers.get_id_from_name(Delratio_del, args['dlr_name'])
			if 'topo_name' in args:
				param_dict['topo_id'] = RestHelpers.get_id_from_name(Topography_hyd, args['topo_name'])			
			if 'field_name' in args:
				param_dict['field_id'] = RestHelpers.get_id_from_name(Field_fld, args['field_name'])

			con_table = Rout_unit_con
			con_prop_field = Rout_unit_con.rtu_id
			prop_table = Rout_unit_rtu

			result = DefaultRestMethods.put_many_con(args, param_dict, con_table, con_prop_field, prop_table)
			rh.close()
			if result > 0:
				return '', 200

			abort(400, 'Unable to update hru properties.')
		except Topography_hyd.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['topo_name']))
		except Delratio_del.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['dlr_name']))
		except Topography_hyd.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['topo_name']))
		except Field_fld.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['field_name']))
		except Weather_sta_cli.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['wst_name']))
		except Exception as ex:
			rh.close()
			abort(400, 'Unexpected error {ex}'.format(ex=ex))
	
	abort(405, 'HTTP Method not allowed.')

# Rounting-unit.ele

@bp.route('/elements', methods=['GET', 'POST'])
def elements():
	if request.method == 'GET':
		table = Rout_unit_ele
		filter_cols = [table.name, table.rtu, table.obj_typ, table.dlr]
		return DefaultRestMethods.get_paged_list(table, filter_cols, True)
	elif request.method == 'POST':
		return DefaultRestMethods.post(Rout_unit_ele, 'Routing unit element')
	abort(405, 'HTTP Method not allowed.')

@bp.route('/elements/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def elementsId(id):
	if request.method == 'GET':
		return DefaultRestMethods.get(id, Rout_unit_ele, 'Routing unit element', back_refs=True)
	elif request.method == 'DELETE':
		return DefaultRestMethods.delete(id, Rout_unit_ele, 'Routing unit element')
	elif request.method == 'PUT':
		return DefaultRestMethods.put(id, Rout_unit_ele, 'Routing unit element')

	abort(405, 'HTTP Method not allowed.')