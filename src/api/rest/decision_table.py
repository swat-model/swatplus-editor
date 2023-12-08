from flask import Blueprint, request, abort
from .config import RequestHeaders as rh

from playhouse.shortcuts import model_to_dict
from peewee import *

from .defaults import DefaultRestMethods, RestHelpers
from database.project import decision_table as db
from database.datasets import decision_table as ds
from fileio import decision_table as fio

from database import lib
from helpers import table_mapper

bp = Blueprint('decision_table', __name__, url_prefix='/decision_table')

special_tables = ['pl_hv_summer1', 'pl_hv_summer2', 'pl_hv_winter1']

builder_tables = ['pl_hv_summer1', 'pl_hv_summer2', 'pl_hv_winter1', 'pl_hv_ccsws', 'fall_plow', 'spring_plow', 'mulch_till_1', 'mulch_till_2', 'no_till', 'fert_stess_test', 'fert_sprg_side', 'irr_opt_sw_unlim', 
	'graze_winter', 'graze_summer', 'hay_cutting', 'forest_cut', 'irr_str8_unlim', 'irr_str8_res', 'irr_str8_aqu', 'irr_str8_cha', 'irr_str8_r_a_u', 'irr_str8_a_r_u', 'irr_str8_res_aqu', 'irr_str8_aqu_res']

def get_dtable_list(table, table_type, sort, reverse, page, per_page, filter_val):
	filter_cols = [table.name]
	selected_table = table.select().where(table.file_name == table_type)
	total = selected_table.count()

	if filter_val is not None:
		w = None
		for f in filter_cols:
			w = w | (f.contains(filter_val))
		s = selected_table.where(w)
	else:
		s = selected_table

	matches = s.count()

	sort_val = SQL('[{}]'.format(sort))
	if reverse == 'y':
		sort_val = SQL('[{}]'.format(sort)).desc()

	m = s.order_by(sort_val).paginate(int(page), int(per_page))
	ml = [{'id': v.id, 'name': v.name, 'conditions': len(v.conditions), 'actions': len(v.actions)} for v in m]

	return {
		'total': total,
		'matches': matches,
		'items': ml
	}

def save_dtable(args, table_name):
	table, created = db.D_table_dtl.get_or_create(name=table_name, file_name=args['file_name'])

	if not created:
		cond_ids = db.D_table_dtl_cond.select(db.D_table_dtl_cond.id).where(db.D_table_dtl_cond.d_table_id == table.id)
		act_ids = db.D_table_dtl_act.select(db.D_table_dtl_act.id).where(db.D_table_dtl_act.d_table_id == table.id)
		db.D_table_dtl_cond_alt.delete().where(db.D_table_dtl_cond_alt.cond_id.in_(cond_ids)).execute()
		db.D_table_dtl_act_out.delete().where(db.D_table_dtl_act_out.act_id.in_(act_ids)).execute()

		db.D_table_dtl_cond.delete().where(db.D_table_dtl_cond.d_table_id == table.id).execute()
		db.D_table_dtl_act.delete().where(db.D_table_dtl_act.d_table_id == table.id).execute()

	table.description = None if 'description' not in args else args['description']
	table.save()

	if 'conditions' in args:
		for c in args['conditions']:
			cond = db.D_table_dtl_cond()
			cond.d_table = table
			cond.var = c['var']
			cond.obj = c['obj']
			cond.obj_num = int(c['obj_num'])
			cond.lim_var = c['lim_var']
			cond.lim_op = c['lim_op']
			cond.lim_const = float(c['lim_const'])
			cond.description = None if 'description' not in args else c['description']
			cond.save()

			if 'alts' in args:
				for l in c['alts']:
					alt = db.D_table_dtl_cond_alt()
					alt.cond = cond
					alt.alt = l['alt']
					alt.save()
	
	if 'actions' in args:
		for a in args['actions']:
			act = db.D_table_dtl_act()
			act.d_table = table
			act.act_typ = a['act_typ']
			act.obj = a['obj']
			act.obj_num = int(a['obj_num'])
			act.name = a['name']
			act.option = a['option']
			act.const = a['const']
			act.const2 = a['const2']
			act.fp = a['fp']
			act.save()

			if 'outcomes' in args:
				for o in a['outcomes']:
					oc = db.D_table_dtl_act_out()
					oc.act = act
					oc.outcome = o['outcome']
					oc.save()

	return table.id

def get_selectlist_index(type):
	table = table_mapper.types.get(type, None)

	items = []
	i = 1
	for v in table.select(table.id, table.name).order_by(table.id):
		items.append({'value': i, 'title': v.name})
		i += 1
	return items

def get_selectlist_text(type):
	table = table_mapper.types.get(type, None)

	items = table.select().order_by(table.name)
	return [{'value': m.name, 'title': m.name} for m in items]

@bp.route('/tables/<table_type>', methods=['GET'])
def tables(table_type):
	project_db = request.headers.get(rh.PROJECT_DB)
	has_db,error = rh.init(project_db)
	if not has_db: abort(400, error)

	args = request.args
	sort = RestHelpers.get_arg(args, 'sort', 'name')
	reverse = RestHelpers.get_arg(args, 'reverse', 'n')
	page = RestHelpers.get_arg(args, 'page', 1)
	per_page = RestHelpers.get_arg(args, 'per_page', 50)
	filter_val = RestHelpers.get_arg(args, 'filter', None)
	data = get_dtable_list(db.D_table_dtl, table_type, sort, reverse, page, per_page, filter_val)
	rh.close()
	return data

@bp.route('/dataset-tables/<table_type>', methods=['GET'])
def datasetTables(table_type):
	project_db = request.headers.get(rh.PROJECT_DB)
	datasets_db = request.headers.get(rh.DATASETS_DB)
	has_db,error = rh.init(project_db, datasets_db)
	if not has_db: abort(400, error)

	args = request.args
	sort = RestHelpers.get_arg(args, 'sort', 'name')
	reverse = RestHelpers.get_arg(args, 'reverse', 'n')
	page = RestHelpers.get_arg(args, 'page', 1)
	per_page = RestHelpers.get_arg(args, 'per_page', 50)
	filter_val = RestHelpers.get_arg(args, 'filter', None)
	data = get_dtable_list(ds.D_table_dtl, table_type, sort, reverse, page, per_page, filter_val)
	rh.close()
	return data

@bp.route('/table', methods=['POST'])
def table():
	project_db = request.headers.get(rh.PROJECT_DB)
	has_db,error = rh.init(project_db)
	if not has_db: abort(400, error)

	args = request.json
	try:
		if args['name'] in special_tables:
			abort(400, 'Decision table {} is reserved and cannot be modified or replaced. Please make a copy instead.'.format(args['name']))
		id = save_dtable(args, args['name'])

		rh.close()
		return {'id': id }, 201
	except IntegrityError as e:
		rh.close()
		abort(400, 'Decision table name must be unique.')
	except Exception as ex:
		rh.close()
		abort(400, 'Unexpected error {}'.format(ex))

@bp.route('/table/<int:id>', methods=['GET', 'DELETE', 'PUT'])
def tableId(id):
	if request.method == 'GET':
		return DefaultRestMethods.get(id, db.D_table_dtl, 'Decision table', back_refs=True, max_depth=2)
	elif request.method == 'DELETE':
		return DefaultRestMethods.delete(id, db.D_table_dtl, 'Decision table')
	elif request.method == 'PUT':
		project_db = request.headers.get(rh.PROJECT_DB)
		has_db,error = rh.init(project_db)
		if not has_db: abort(400, error)

		args = request.json
		try:
			file_processor = fio.D_table_dtl(args['file_name'])
			file_processor.set_tables('project')
			i, new_table = file_processor.read_table(args['text'].splitlines(), 0, id)
			new_table.name = args['name']
			new_table.description = None if 'description' not in args else args['description']
			new_table.save()

			rh.close()
			return {'id': new_table.id }, 201
		except db.D_table_dtl.DoesNotExist:
			rh.close()
			abort(404, 'Decision table {id} does not exist'.format(id=id))
		except IndexError as e:
			rh.close()
			abort(400, 'Error parsing decision table. {}'.format(e))
		except IntegrityError as e:
			rh.close()
			abort(400, 'Decision table name must be unique.')
		except Exception as ex:
			rh.close()
			abort(400, 'Unexpected error {}'.format(ex))

	abort(405, 'HTTP Method not allowed.')

@bp.route('/dataset-table/<int:id>', methods=['GET'])
def datasetTableId(id):
	return DefaultRestMethods.get(id, ds.D_table_dtl, 'Decision table', back_refs=True, max_depth=2)

@bp.route('/name/<file_name>/<name>', methods=['GET'])
def name(file_name, name):
	project_db = request.headers.get(rh.PROJECT_DB)
	has_db,error = rh.init(project_db)
	if not has_db: abort(400, error)

	table = db.D_table_dtl
	try:
		m = table.get((table.name == name) & (table.file_name == file_name))
		d = model_to_dict(m, backrefs=True, max_depth=2)
		RestHelpers.get_obj_name(d)
		rh.close()
		return d
	except table.DoesNotExist:
		rh.close()
		abort(404, '{description} {id} does not exist'.format(description='Decision table', name=name))

@bp.route('/dataset-builder', methods=['GET'])
def datasetBuilder():
	project_db = request.headers.get(rh.PROJECT_DB)
	datasets_db = request.headers.get(rh.DATASETS_DB)
	has_db,error = rh.init(project_db, datasets_db)
	if not has_db: abort(400, error)

	m = ds.D_table_dtl.select().where(ds.D_table_dtl.name.in_(builder_tables))
	ml = [model_to_dict(v, backrefs=True, max_depth=2) for v in m]
	md = { v['name']: v for v in ml }
	warning = None
	if len(m) < len(builder_tables):
		warning = 'The schedule builder is dependent on decision tables added in the 2.1.0 release. Please update your swatplus_datasets.sqlite to version 2.1.0 or later to use the builder tool.'

	data = {
		'tables': md, 
		'warning': warning,
		'fertilizers': get_selectlist_text('fert'),
		'chem_apps': get_selectlist_text('chem_app_ops'),
		'reservoirs': get_selectlist_index('res_con'),
		'aquifers': get_selectlist_index('aqu_con'),
		'channels': get_selectlist_index('chandeg_con')
	}

	rh.close()
	return data

@bp.route('/builder', methods=['POST'])
def builder():
	project_db = request.headers.get(rh.PROJECT_DB)
	has_db,error = rh.init(project_db)
	if not has_db: abort(400, error)

	args = request.json
	try:
		if args['name'] in special_tables:
			rh.close()
			abort(400, 'Decision table {} is reserved and cannot be modified or replaced. Please make a copy instead.'.format(args['name']))
		
		name = args['name']
		if not args['overwrite']:
			matches = db.D_table_dtl.select().where(db.D_table_dtl.name.startswith(args['name']))				
			existing_count = matches.count()
			if existing_count > 0:
				existing_names = [v.name for v in matches]
				condition = True
				while condition:
					name = '{name}{count}'.format(name=name,count=existing_count+1)
					existing_count += 1
					condition = name in existing_names

		id = save_dtable(args, name)

		rh.close()
		return {'name': name }, 201
	except IntegrityError as e:
		rh.close()
		abort(400, 'Decision table name must be unique.')
	except Exception as ex:
		rh.close()
		abort(400, 'Unexpected error {}'.format(ex))
