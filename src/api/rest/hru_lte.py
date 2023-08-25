from flask import Blueprint, request, abort
from .config import RequestHeaders as rh

from playhouse.shortcuts import model_to_dict
from peewee import *

from .defaults import DefaultRestMethods, RestHelpers
from database.project.climate import Weather_sta_cli
from database.project.connect import Hru_lte_con, Hru_lte_con_out
from database.project.hru import Hru_data_hru, Hru_lte_hru
from database.project.soils import Soils_lte_sol
from database.project.hru_parm_db import Plants_plt
from database.project.decision_table import D_table_dtl

bp = Blueprint('hru_lte', __name__, url_prefix='/hrus-lte')

@bp.route('/items', methods=['GET', 'POST'])
def con():
	if request.method == 'GET':
		table = Hru_lte_con
		prop_table = Hru_lte_hru
		filter_cols = [table.name, table.wst, prop_table.soil_text, prop_table.grow_start, prop_table.grow_end, prop_table.plnt_typ, prop_table.pet_flag, prop_table.irr_flag, prop_table.irr_src]
		table_lookups = {
			table.wst: Weather_sta_cli
		}
		props_lookups = {
			prop_table.soil_text: Soils_lte_sol,
			prop_table.grow_start: D_table_dtl,
			prop_table.grow_end: D_table_dtl,
			prop_table.plnt_typ: Plants_plt
		}

		items = DefaultRestMethods.get_paged_items_con(table, prop_table, filter_cols, table_lookups, props_lookups)
		ml = []
		for v in items['model']:
			d = RestHelpers.get_con_item_dict(v)
			d['soil_text'] = RestHelpers.get_prop_dict(v.lhru.soil_text)
			d['grow_start'] = RestHelpers.get_prop_dict(v.lhru.grow_start)
			d['grow_end'] = RestHelpers.get_prop_dict(v.lhru.grow_end)
			d['plnt_typ'] = RestHelpers.get_prop_dict(v.lhru.plnt_typ)
			ml.append(d)
		
		return {
			'total': items['total'],
			'matches': items['matches'],
			'items': ml
		}
	elif request.method == 'POST':
		return DefaultRestMethods.post_con('lhru', Hru_lte_con, Hru_lte_hru)
	abort(405, 'HTTP Method not allowed.')

@bp.route('/items/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def conId(id):
	if request.method == 'GET':
		return DefaultRestMethods.get(id, Hru_lte_con, 'Hru', True)
	elif request.method == 'PUT':
		return DefaultRestMethods.put_con(id, 'lhru', Hru_lte_con, Hru_lte_hru)
	elif request.method == 'DELETE':
		return DefaultRestMethods.delete(id, Hru_lte_con, 'Hru', 'lhru', Hru_lte_hru)
	abort(405, 'HTTP Method not allowed.')

@bp.route('/out', methods=['POST'])
def conOut():
	return DefaultRestMethods.post_con_out('hru_lte_con', Hru_lte_con_out)

@bp.route('/out/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def conOutId(id):
	if request.method == 'GET':
		return DefaultRestMethods.get(id, Hru_lte_con_out, 'Outflow', True)
	elif request.method == 'PUT':
		return DefaultRestMethods.put_con_out(id, 'hru_lte_con', Hru_lte_con_out)
	elif request.method == 'DELETE':
		return DefaultRestMethods.delete(id, Hru_lte_con_out, 'Outflow')
	abort(405, 'HTTP Method not allowed.')

# Hru-lte.hru

@bp.route('/properties', methods=['GET', 'POST'])
def properties():
	if request.method == 'GET':
		table = Hru_lte_hru
		filter_cols = [table.name]
		return DefaultRestMethods.get_paged_list(table, filter_cols, True)
	elif request.method == 'POST':
		project_db = request.headers.get(rh.PROJECT_DB)
		has_db,error = rh.init(project_db)
		if not has_db: abort(400, error)

		args = request.json
		try:
			args['grow_start_id'] = RestHelpers.get_id_from_name(D_table_dtl, args['grow_start'])
			args['grow_end_id'] = RestHelpers.get_id_from_name(D_table_dtl, args['grow_end'])

			args.pop('grow_start', None)
			args.pop('grow_end', None)

			result = RestHelpers.save_args(Hru_lte_hru, args, is_new=True, lookup_fields=['soil_text', 'plnt_typ'])

			rh.close()
			if result > 0:
				return {'id': result }, 201

			abort(400, 'Unable to update hru {id}.'.format(id=id))
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
		project_db = request.headers.get(rh.PROJECT_DB)
		has_db,error = rh.init(project_db)
		if not has_db: abort(400, error)

		table = Hru_lte_hru
		description = 'Hru'
		
		try:
			m = table.get(table.id == id)
			d = model_to_dict(m, backrefs=True, max_depth=1)
			d['grow_start'] = m.grow_start.name
			d['grow_end'] = m.grow_end.name
			rh.close()
			return d
		except table.DoesNotExist:
			rh.close()
			abort(404, '{description} {id} does not exist'.format(description=description, id=id))
	elif request.method == 'DELETE':
		return DefaultRestMethods.delete(id, Hru_lte_hru, 'Hru')
	elif request.method == 'PUT':
		project_db = request.headers.get(rh.PROJECT_DB)
		has_db,error = rh.init(project_db)
		if not has_db: abort(400, error)

		args = request.json
		try:
			args['grow_start_id'] = RestHelpers.get_id_from_name(D_table_dtl, args['grow_start'])
			args['grow_end_id'] = RestHelpers.get_id_from_name(D_table_dtl, args['grow_end'])

			args.pop('grow_start', None)
			args.pop('grow_end', None)

			result = RestHelpers.save_args(Hru_lte_hru, args, id=id, lookup_fields=['soil_text', 'plnt_typ'])

			rh.close()
			if result > 0:
				return '', 200

			abort(400, 'Unable to update hru {id}.'.format(id=id))
		except IntegrityError as e:
			rh.close()
			abort(400, 'Name must be unique.')
		except Hru_lte_hru.DoesNotExist:
			rh.close()
			abort(400, 'Hru-lte {id} does not exist'.format(id=id))
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
			if 'grow_start' in args:
				args['grow_start_id'] = RestHelpers.get_id_from_name(D_table_dtl, args['grow_start'])
				args.pop('grow_start', None)

			if 'grow_end' in args:
				args['grow_end_id'] = RestHelpers.get_id_from_name(D_table_dtl, args['grow_end'])
				args.pop('grow_end', None)

			lookup_fields = ['soil_text', 'plnt_typ']

			param_dict = {}
			for key in args.keys():
				if key in args and key != 'selected_ids':
					if key in lookup_fields:
						d = args[key]
						if int(d['id']) != 0:
							param_dict[key] = int(d['id'])
					else:
						param_dict[key] = args[key]

			con_table = Hru_lte_con
			con_prop_field = Hru_lte_con.lhru_id
			prop_table = Hru_lte_hru

			result = DefaultRestMethods.put_many_con(args, param_dict, con_table, con_prop_field, prop_table)
			rh.close()
			if result > 0:
				return '', 200

			abort(400, 'Unable to update channel HRUs.')
		except Exception as ex:
			rh.close()
			abort(400, 'Unexpected error {ex}'.format(ex=ex))
	
	abort(405, 'HTTP Method not allowed.')
