from flask import Blueprint, request, abort
from .config import RequestHeaders as rh

from playhouse.shortcuts import model_to_dict
from peewee import *

from .defaults import DefaultRestMethods, RestHelpers
from database.project import salts as db
from database.project import base as project_base, recall
from database.project.simulation import Time_sim
from database import lib as db_lib

import datetime

bp = Blueprint('salts', __name__, url_prefix='/salts')

@bp.route('/enable-recall', methods=['GET','PUT','POST'])
def enableRecall():
	project_db = request.headers.get(rh.PROJECT_DB)
	has_db,error = rh.init(project_db)
	if not has_db: abort(400, error)

	module, created = db.Salt_module.get_or_create(id=1)
	
	if request.method == 'GET':
		rh.close()
		return {
			'recall': module.recall
		}
	elif request.method == 'PUT':
		args = request.json
		result = db.Salt_module.update(recall=args['recall']).execute()
		
		if result > 0:
			rh.close()
			return '', 200

		rh.close()
		abort(400, 'Unable to update salts recall module.')
	elif request.method == 'POST':
		args = request.json
		time_step = args['time_step']
		if time_step < 1 or time_step > 3:
			rh.close()
			abort(400, 'Invalid time step value.')
		
		if db.Salt_recall_rec.select().count() == 0:
			items = []
			for rec in recall.Recall_rec.select():
				items.append({
					'name': rec.name,
					'rec_typ': time_step
				})

			db_lib.bulk_insert(project_base.db, db.Salt_recall_rec, items)

			for rec in db.Salt_recall_rec.select():
				update_recall_rec(rec, rec.id, Time_sim.get_or_create_default(), time_step, True)

		rh.close()
		return '', 200

	abort(405, 'HTTP Method not allowed.')

@bp.route('/recall', methods=['GET', 'POST', 'DELETE'])
def recallTable():
	if request.method == 'GET':
		table = db.Salt_recall_rec
		filter_cols = [table.name]
		return DefaultRestMethods.get_paged_list(table, filter_cols, True)
	elif request.method == 'POST':
		return DefaultRestMethods.post(db.Salt_recall_rec, 'Recall')
	elif request.method == 'DELETE':
		project_db = request.headers.get(rh.PROJECT_DB)
		has_db,error = rh.init(project_db)
		if not has_db: abort(400, error)
		project_base.db.execute_sql("PRAGMA foreign_keys = ON")
		db.Salt_recall_dat.delete().execute()
		db.Salt_recall_rec.delete().execute()
		rh.close()
		return '', 200
	
	abort(405, 'HTTP Method not allowed.')

@bp.route('/recall/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def recallId(id):
	if request.method == 'GET':
		return DefaultRestMethods.get(id, db.Salt_recall_rec, 'Salt recall', back_refs=False)
	elif request.method == 'DELETE':
		return DefaultRestMethods.delete(id, db.Salt_recall_rec, 'Salt recall')
	elif request.method == 'PUT':
		project_db = request.headers.get(rh.PROJECT_DB)
		has_db,error = rh.init(project_db)
		if not has_db: abort(400, error)

		table = db.Salt_recall_rec
		item_description = 'Salt recall'
		args = request.json
		try:
			sim = Time_sim.get_or_create_default()
			m = table.get(table.id==id)
			update_recall_rec(m, id, sim, args['rec_typ'])

			result = RestHelpers.save_args(table, args, id=id)

			rh.close()
			if result > 0:
				return '', 200

			abort(400, 'Unable to update salt recall {id}.'.format(id=id))
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

@bp.route('/recall-data-list/<int:id>', methods=['GET'])
def dataList(id):
	project_db = request.headers.get(rh.PROJECT_DB)
	has_db,error = rh.init(project_db)
	if not has_db: abort(400, error)

	table = db.Salt_recall_dat
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

@bp.route('/recall-data', methods=['POST'])
def data():
	return DefaultRestMethods.post(db.Salt_recall_dat, 'Recall')

@bp.route('/recall-data/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def dataItem(id):
	if request.method == 'GET':
		return DefaultRestMethods.get(id, db.Salt_recall_dat, 'Recall')
	elif request.method == 'DELETE':
		return DefaultRestMethods.delete(id, db.Salt_recall_dat, 'Recall')
	elif request.method == 'PUT':
		return DefaultRestMethods.put(id, db.Salt_recall_dat, 'Recall')

	abort(405, 'HTTP Method not allowed.')

def update_recall_rec(m, id, sim, new_rec_typ, no_compare = False):
	if (m.rec_typ != new_rec_typ) or no_compare:
		db.Salt_recall_dat.delete().where(db.Salt_recall_dat.recall_rec_id==id).execute()
		rec = db.Salt_recall_rec.get_or_none(db.Salt_recall_rec.id == id)
		name = '' if rec is None else rec.name

		ob_typs = {
			1: 'pt_day',
			2: 'pt_mon',
			3: 'pt_yr'
		}
		ob_typ = ob_typs.get(new_rec_typ, 'ptsrc')

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
						'so4': 0,
						'ca': 0,
						'mg': 0,
						'na': 0,
						'k': 0,
						'cl': 0,
						'co3': 0,
						'hco3': 0
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
					'so4': 0,
					'ca': 0,
					'mg': 0,
					'na': 0,
					'k': 0,
					'cl': 0,
					'co3': 0,
					'hco3': 0
				}
				rec_data.append(data)
				current_date = current_date + datetime.timedelta(1) 

		db_lib.bulk_insert(project_base.db, db.Salt_recall_dat, rec_data)