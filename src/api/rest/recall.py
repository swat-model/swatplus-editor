from flask import Blueprint, request, abort
from .config import RequestHeaders as rh

from playhouse.shortcuts import model_to_dict
from peewee import *

from .defaults import DefaultRestMethods, RestHelpers
from database.project.connect import Recall_con, Recall_con_out
from database.project.recall import Recall_rec, Recall_dat
from database.project.climate import Weather_sta_cli
from database.project.simulation import Time_sim
from database.project import base as project_base
from database import lib as db_lib

import datetime

"""
In SWAT+, constant values for point sources and inlets are stored in the export coefficients properties file, exco.exc, while time series data 
are stored entirely in the recall section. However, in the editor, we keep both time series and constant recall and export coefficients in the same section. 
When the user writes input files, the editor will write to the appropriate files.
"""

bp = Blueprint('recall', __name__, url_prefix='/recall')

@bp.route('/items', methods=['GET', 'POST'])
def con():
	if request.method == 'GET':
		table = Recall_con
		prop_table = Recall_rec
		filter_cols = [table.name, table.wst]
		table_lookups = {
			table.wst: Weather_sta_cli
		}
		props_lookups = {}

		items = DefaultRestMethods.get_paged_items_con(table, prop_table, filter_cols, table_lookups, props_lookups)
		ml = []
		for v in items['model']:
			d = RestHelpers.get_con_item_dict(v)
			d['rec_typ'] = v.rec.rec_typ
			ml.append(d)
		
		return {
			'total': items['total'],
			'matches': items['matches'],
			'items': ml
		}
	elif request.method == 'POST':
		return DefaultRestMethods.post_con('rec', Recall_con, Recall_rec)
	abort(405, 'HTTP Method not allowed.')

@bp.route('/items/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def conId(id):
	if request.method == 'GET':
		return DefaultRestMethods.get(id, Recall_con, 'Recall', True)
	elif request.method == 'PUT':
		return DefaultRestMethods.put_con(id, 'rec', Recall_con, Recall_rec)
	elif request.method == 'DELETE':
		return DefaultRestMethods.delete(id, Recall_con, 'Recall', 'rec', Recall_rec)
	abort(405, 'HTTP Method not allowed.')

@bp.route('/out', methods=['POST'])
def conOut():
	return DefaultRestMethods.post_con_out('recall_con', Recall_con_out)

@bp.route('/out/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def conOutId(id):
	if request.method == 'GET':
		return DefaultRestMethods.get(id, Recall_con_out, 'Outflow', True)
	elif request.method == 'PUT':
		return DefaultRestMethods.put_con_out(id, 'recall_con', Recall_con_out)
	elif request.method == 'DELETE':
		return DefaultRestMethods.delete(id, Recall_con_out, 'Outflow')
	abort(405, 'HTTP Method not allowed.')

# Recall.rec

def update_recall_rec(m, id, sim, new_rec_typ):
	if m.rec_typ != new_rec_typ:
		Recall_dat.delete().where(Recall_dat.recall_rec_id==id).execute()
		rec = Recall_rec.get_or_none(Recall_rec.id == id)
		name = '' if rec is None else rec.name

		ob_typs = {
			1: 'pt_day',
			2: 'pt_mon',
			3: 'pt_yr',
			4: 'pt_const'
		}
		ob_typ = ob_typs.get(new_rec_typ, 'pt')

		years = 0
		months = 1
		start_month = 1
		insert_daily = False

		if new_rec_typ != 4:
			years = sim.yrc_end - sim.yrc_start
			if new_rec_typ != 3:
				start_date = datetime.datetime(sim.yrc_start, 1, 1) + datetime.timedelta(sim.day_start)
				end_date = datetime.datetime(sim.yrc_end, 1, 1) + datetime.timedelta(sim.day_end)
				if sim.day_end == 0:
					end_date = datetime.datetime(sim.yrc_end, 12, 31)

				start_month = start_date.month
				months = end_date.month
				
				if new_rec_typ != 2:
					insert_daily = True

		rec_data = []
		if not insert_daily:
			for x in range(years + 1):
				for y in range(start_month, months + 1):
					t_step = x + 1 if months == 1 else y
					data = {
						'recall_rec_id': id,
						'jday': 1,
						'mo': t_step if new_rec_typ == 1 or new_rec_typ == 2 else 1,
						'day_mo': 1,
						'yr': x + sim.yrc_start if new_rec_typ != 4 else 1,
						'ob_typ': ob_typ,
						'ob_name': name,
						'flo': 0,
						'sed': 0,
						'orgn': 0,
						'sedp': 0,
						'no3': 0,
						'solp': 0,
						'chla': 0,
						'nh3': 0,
						'no2': 0,
						'cbod': 0,
						'dox': 0,
						'sand': 0,
						'silt': 0,
						'clay': 0,
						'sag': 0,
						'lag': 0,
						'gravel': 0,
						'tmp': 0
					}
					rec_data.append(data)
		else:
			current_date = start_date
			while current_date <= end_date:
				curent_tt = current_date.timetuple()
				data = {
					'recall_rec_id': id,
					'jday': curent_tt.tm_yday,
					'mo': curent_tt.tm_mon,
					'day_mo': curent_tt.tm_mday,
					'yr': current_date.year,
					'ob_typ': ob_typ,
					'ob_name': name,
					'flo': 0,
					'sed': 0,
					'orgn': 0,
					'sedp': 0,
					'no3': 0,
					'solp': 0,
					'chla': 0,
					'nh3': 0,
					'no2': 0,
					'cbod': 0,
					'dox': 0,
					'sand': 0,
					'silt': 0,
					'clay': 0,
					'sag': 0,
					'lag': 0,
					'gravel': 0,
					'tmp': 0
				}
				rec_data.append(data)
				current_date = current_date + datetime.timedelta(1) 

		db_lib.bulk_insert(project_base.db, Recall_dat, rec_data)

@bp.route('/properties', methods=['GET', 'POST'])
def properties():
	if request.method == 'GET':
		table = Recall_rec
		filter_cols = [table.name]
		return DefaultRestMethods.get_paged_list(table, filter_cols, True)
	elif request.method == 'POST':
		return DefaultRestMethods.post(Recall_rec, 'Recall')
	
	abort(405, 'HTTP Method not allowed.')

@bp.route('/properties/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def propertiesId(id):
	if request.method == 'GET':
		return DefaultRestMethods.get(id, Recall_rec, 'Recall', back_refs=False)
	elif request.method == 'DELETE':
		return DefaultRestMethods.delete(id, Recall_rec, 'Recall')
	elif request.method == 'PUT':
		project_db = request.headers.get(rh.PROJECT_DB)
		has_db,error = rh.init(project_db)
		if not has_db: abort(400, error)

		table = Recall_rec
		item_description = 'Recall'
		args = request.json
		try:
			sim = Time_sim.get_or_create_default()
			m = table.get(table.id==id)
			update_recall_rec(m, id, sim, args['rec_typ'])

			result = RestHelpers.save_args(table, args, id=id)

			rh.close()
			if result > 0:
				return '', 200

			abort(400, 'Unable to update properties {id}.'.format(id=id))
		except IntegrityError as e:
			rh.close()
			abort(400, 'Name must be unique.')
		except table.DoesNotExist:
			rh.close()
			abort(404, '{item} {id} does not exist'.format(item=item_description, id=id))
		except Exception as ex:
			rh.close()
			abort(400, 'Unexpected error {ex}'.format(ex=ex))

	abort(405, 'HTTP Method not allowed.')

@bp.route('/properties/many', methods=['GET', 'PUT'])
def propertiesMany():
	if request.method == 'GET':
		return DefaultRestMethods.get_name_id_list(Recall_rec)
	elif request.method == 'PUT':
		project_db = request.headers.get(rh.PROJECT_DB)
		has_db,error = rh.init(project_db)
		if not has_db: abort(400, error)

		args = request.json
		try:
			param_dict = {}

			if 'rec_typ' in args:
				param_dict['rec_typ'] = args['rec_typ']

			con_table = Recall_con
			con_prop_field = Recall_con.rec_id
			prop_table = Recall_rec

			con_param_dict = {}
			if 'wst_name' in args:
				con_param_dict['wst_id'] = RestHelpers.get_id_from_name(Weather_sta_cli, args['wst_name'])
			if 'elev' in args:
				con_param_dict['elev'] = args['elev']

			con_result = 1
			if (len(con_param_dict) > 0):
				con_query = con_table.update(con_param_dict).where(con_table.id.in_(args['selected_ids']))
				con_result = con_query.execute()

			if con_result > 0:
				result = 1
				if (len(param_dict) > 0):
					prop_ids = con_table.select(con_prop_field).where(con_table.id.in_(args['selected_ids']))
					query = prop_table.select().where(prop_table.id.in_(prop_ids))
					sim = Time_sim.get_or_create_default()
					for m in query:
						update_recall_rec(project_base.db, m, m.id, sim, args['rec_typ'])

					query2 = prop_table.update(param_dict).where(prop_table.id.in_(prop_ids))
					result = query2.execute()

				rh.close()
				if result > 0:
					return '', 200

			rh.close()
			abort(400, 'Unable to update properties.')
		except Exception as ex:
			rh.close()
			abort(400, 'Unexpected error {ex}'.format(ex=ex))
	
	abort(405, 'HTTP Method not allowed.')

# Recall.dat

@bp.route('/data-list/<int:id>', methods=['GET'])
def dataList(id):
	project_db = request.headers.get(rh.PROJECT_DB)
	has_db,error = rh.init(project_db)
	if not has_db: abort(400, error)

	table = Recall_dat
	args = request.args
	sort = RestHelpers.get_arg(args, 'sort', 'name')
	reverse = RestHelpers.get_arg(args, 'reverse', 'n')
	page = RestHelpers.get_arg(args, 'page', 1)
	per_page = RestHelpers.get_arg(args, 'per_page', 50)
	
	s = table.select().where(table.recall_rec_id == id)
	total = s.count()

	if sort == 'name':
		sort_val = table.name if reverse != 'y' else table.name.desc()
	else:
		sort_val = SQL('[{}]'.format(sort))
		if reverse == 'y':
			sort_val = SQL('[{}]'.format(sort)).desc()

	m = s.order_by(sort_val).paginate(int(page), int(per_page))

	rh.close()
	return {
		'total': total,
		'matches': total,
		'items': [model_to_dict(v, recurse=False) for v in m]
	}

@bp.route('/data', methods=['POST'])
def data():
	return DefaultRestMethods.post(Recall_dat, 'Recall')

@bp.route('/data/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def dataItem(id):
	if request.method == 'GET':
		return DefaultRestMethods.get(id, Recall_dat, 'Recall')
	elif request.method == 'DELETE':
		return DefaultRestMethods.delete(id, Recall_dat, 'Recall')
	elif request.method == 'PUT':
		return DefaultRestMethods.put(id, Recall_dat, 'Recall')

	abort(405, 'HTTP Method not allowed.')
