from flask import Blueprint, request, abort
from .config import RequestHeaders as rh

from playhouse.shortcuts import model_to_dict
from peewee import *

from .defaults import DefaultRestMethods, RestHelpers
from database.project.climate import Weather_sta_cli
from database.project.connect import Hru_con, Hru_con_out
from database.project.hru import Hru_data_hru
from database.project.hydrology import Hydrology_hyd, Topography_hyd, Field_fld
from database.project.soils import Soils_sol
from database.project.lum import Landuse_lum
from database.project.hru_parm_db import Snow_sno
from database.project.init import Soil_plant_ini
from database.project.reservoir import Wetland_wet

bp = Blueprint('hrus', __name__, url_prefix='/hrus')

@bp.route('/items', methods=['GET', 'POST'])
def con():
	if request.method == 'GET':
		table = Hru_con
		prop_table = Hru_data_hru
		filter_cols = [table.name, table.wst, prop_table.topo, prop_table.hydro, prop_table.soil, prop_table.lu_mgt, prop_table.soil_plant_init, prop_table.surf_stor, prop_table.snow, prop_table.field]
		table_lookups = {
			table.wst: Weather_sta_cli
		}
		props_lookups = {
			prop_table.topo: Topography_hyd,
			prop_table.hydro: Hydrology_hyd,
			prop_table.soil: Soils_sol,
			prop_table.lu_mgt: Landuse_lum,
			prop_table.soil_plant_init: Soil_plant_ini,
			prop_table.surf_stor: Wetland_wet,
			prop_table.snow: Snow_sno,
			prop_table.field: Field_fld
		}

		items = DefaultRestMethods.get_paged_items_con(table, prop_table, filter_cols, table_lookups, props_lookups)
		ml = []
		for v in items['model']:
			d = RestHelpers.get_con_item_dict(v)
			d['topo'] = RestHelpers.get_prop_dict(v.hru.topo)
			d['hydro'] = RestHelpers.get_prop_dict(v.hru.hydro)
			d['soil'] = RestHelpers.get_prop_dict(v.hru.soil)
			d['lu_mgt'] = RestHelpers.get_prop_dict(v.hru.lu_mgt)
			d['soil_plant_init'] = RestHelpers.get_prop_dict(v.hru.soil_plant_init)
			d['surf_stor'] = RestHelpers.get_prop_dict(v.hru.surf_stor)
			d['snow'] = RestHelpers.get_prop_dict(v.hru.snow)
			d['field'] = RestHelpers.get_prop_dict(v.hru.field)
			ml.append(d)
		
		return {
			'total': items['total'],
			'matches': items['matches'],
			'items': ml
		}
	elif request.method == 'POST':
		return DefaultRestMethods.post_con('hru', Hru_con, Hru_data_hru)
	abort(405, 'HTTP Method not allowed.')

@bp.route('/items/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def conId(id):
	if request.method == 'GET':
		return DefaultRestMethods.get(id, Hru_con, 'Hru', True)
	elif request.method == 'PUT':
		return DefaultRestMethods.put_con(id, 'hru', Hru_con, Hru_data_hru)
	elif request.method == 'DELETE':
		return DefaultRestMethods.delete(id, Hru_con, 'Hru', 'hru', Hru_data_hru)
	abort(405, 'HTTP Method not allowed.')

@bp.route('/out', methods=['POST'])
def conOut():
	return DefaultRestMethods.post_con_out('hru_con', Hru_con_out)

@bp.route('/out/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def conOutId(id):
	if request.method == 'GET':
		return DefaultRestMethods.get(id, Hru_con_out, 'Outflow', True)
	elif request.method == 'PUT':
		return DefaultRestMethods.put_con_out(id, 'hru_con', Hru_con_out)
	elif request.method == 'DELETE':
		return DefaultRestMethods.delete(id, Hru_con_out, 'Outflow')
	abort(405, 'HTTP Method not allowed.')

# Hru-data.hru

@bp.route('/properties', methods=['GET', 'POST'])
def properties():
	if request.method == 'GET':
		table = Hru_data_hru
		filter_cols = [table.name]
		return DefaultRestMethods.get_paged_list(table, filter_cols, True)
	elif request.method == 'POST':
		project_db = request.headers.get(rh.PROJECT_DB)
		has_db,error = rh.init(project_db)
		if not has_db: abort(400, error)

		args = request.json
		try:
			m = Hru_data_hru()
			m.name = args['name']
			m.description = None if 'description' not in args else args['description']
			m.topo_id = RestHelpers.get_id_from_name(Topography_hyd, args['topo_name'])
			m.hydro_id = RestHelpers.get_id_from_name(Hydrology_hyd, args['hyd_name'])
			m.soil_id = RestHelpers.get_id_from_name(Soils_sol, args['soil_name'])
			m.lu_mgt_id = RestHelpers.get_id_from_name(Landuse_lum, args['lu_mgt_name'])
			m.soil_plant_init_id = RestHelpers.get_id_from_name(Soil_plant_ini, args['soil_plant_init_name'])
			m.surf_stor_id = RestHelpers.get_id_from_name(Wetland_wet, args['surf_stor'])
			m.snow_id = RestHelpers.get_id_from_name(Snow_sno, args['snow_name'])
			m.field_id = RestHelpers.get_id_from_name(Field_fld, args['field_name'])

			result = m.save()

			rh.close()
			if result > 0:
				return {'id': m.id }, 200

			abort(400, 'Unable to update hru properties {id}.'.format(id=id))
		except IntegrityError as e:
			rh.close()
			abort(400, 'Hru properties name must be unique.')
		except Topography_hyd.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['topo_name']))
		except Hydrology_hyd.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['hyd_name']))
		except Soils_sol.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['soil_name']))
		except Landuse_lum.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['lu_mgt_name']))
		except Soil_plant_ini.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['soil_plant_init_name']))
		except Wetland_wet.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['surf_stor']))
		except Snow_sno.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['snow_name']))
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
		return DefaultRestMethods.get(id, Hru_data_hru, 'Hru', True)
	elif request.method == 'DELETE':
		return DefaultRestMethods.delete(id, Hru_data_hru, 'Hru')
	elif request.method == 'PUT':
		project_db = request.headers.get(rh.PROJECT_DB)
		has_db,error = rh.init(project_db)
		if not has_db: abort(400, error)

		args = request.json
		try:
			m = Hru_data_hru.get(Hru_data_hru.id == id)
			m.name = args['name']
			m.description = None if 'description' not in args else args['description']
			if 'topo_name' in args:
				m.topo_id = RestHelpers.get_id_from_name(Topography_hyd, args['topo_name'])
			if 'hyd_name' in args:
				m.hydro_id = RestHelpers.get_id_from_name(Hydrology_hyd, args['hyd_name'])
			if 'soil_name' in args:
				m.soil_id = RestHelpers.get_id_from_name(Soils_sol, args['soil_name'])
			if 'lu_mgt_name' in args:
				m.lu_mgt_id = RestHelpers.get_id_from_name(Landuse_lum, args['lu_mgt_name'])
			if 'soil_plant_init_name' in args:
				m.soil_plant_init_id = RestHelpers.get_id_from_name(Soil_plant_ini, args['soil_plant_init_name'])
			if 'surf_stor' in args:
				m.surf_stor_id = RestHelpers.get_id_from_name(Wetland_wet, args['surf_stor'])
			if 'snow_name' in args:
				m.snow_id = RestHelpers.get_id_from_name(Snow_sno, args['snow_name'])
			if 'field_name' in args:
				m.field_id = RestHelpers.get_id_from_name(Field_fld, args['field_name'])

			result = m.save()

			rh.close()
			if result > 0:
				return '', 200

			abort(400, 'Unable to update hru properties {id}.'.format(id=id))
		except IntegrityError as e:
			rh.close()
			abort(400, 'Hru properties name must be unique.')
		except Topography_hyd.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['topo_name']))
		except Hydrology_hyd.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['hyd_name']))
		except Soils_sol.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['soil_name']))
		except Landuse_lum.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['lu_mgt_name']))
		except Soil_plant_ini.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['soil_plant_init_name']))
		except Wetland_wet.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['surf_stor']))
		except Snow_sno.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['snow_name']))
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
		return DefaultRestMethods.get_name_id_list(Hru_data_hru)
	elif request.method == 'PUT':
		project_db = request.headers.get(rh.PROJECT_DB)
		has_db,error = rh.init(project_db)
		if not has_db: abort(400, error)

		args = request.json
		try:
			param_dict = {}

			if 'topo_name' in args:
				param_dict['topo_id'] = RestHelpers.get_id_from_name(Topography_hyd, args['topo_name'])
			if 'hyd_name' in args:
				param_dict['hydro_id'] = RestHelpers.get_id_from_name(Hydrology_hyd, args['hyd_name'])
			if 'soil_name' in args:
				param_dict['soil_id'] = RestHelpers.get_id_from_name(Soils_sol, args['soil_name'])
			if 'lu_mgt_name' in args:
				param_dict['lu_mgt_id'] = RestHelpers.get_id_from_name(Landuse_lum, args['lu_mgt_name'])
			if 'soil_plant_init_name' in args is not None:
				param_dict['soil_plant_init_id'] = RestHelpers.get_id_from_name(Soil_plant_ini, args['soil_plant_init_name'])
			if 'surf_stor' in args:
				param_dict['surf_stor_id'] = RestHelpers.get_id_from_name(Wetland_wet, args['surf_stor'])
			if 'snow_name' in args:
				param_dict['snow_id'] = RestHelpers.get_id_from_name(Snow_sno, args['snow_name'])
			if 'field_name' in args:
				param_dict['field_id'] = RestHelpers.get_id_from_name(Field_fld, args['field_name'])

			con_table = Hru_con
			con_prop_field = Hru_con.hru_id
			prop_table = Hru_data_hru

			result = DefaultRestMethods.put_many_con(args, param_dict, con_table, con_prop_field, prop_table)
			rh.close()
			if result > 0:
				return '', 200

			abort(400, 'Unable to update hru properties.')
		except Topography_hyd.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['topo_name']))
		except Hydrology_hyd.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['hyd_name']))
		except Soils_sol.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['soil_name']))
		except Landuse_lum.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['lu_mgt_name']))
		except Soil_plant_ini.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['soil_plant_init_name']))
		except Wetland_wet.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['surf_stor']))
		except Snow_sno.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['snow_name']))
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
