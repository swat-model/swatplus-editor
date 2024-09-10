from flask import Blueprint, request, abort
from .config import RequestHeaders as rh

from playhouse.shortcuts import model_to_dict
from peewee import *

from .defaults import DefaultRestMethods, RestHelpers
from database.project import regions as db

bp = Blueprint('regions', __name__, url_prefix='/regions')

# Ls_unit_def

@bp.route('/ls_units', methods=['GET', 'POST'])
def lsunits():
	if request.method == 'GET':
		table = db.Ls_unit_def
		filter_cols = [table.name]
		items = DefaultRestMethods.get_paged_items(table, filter_cols)
		m = items['model']
		ml = [{'id': v.id, 'name': v.name, 'area': v.area, 'num_elements': len(v.elements)} for v in m]

		return {
			'total': items['total'],
			'matches': items['matches'],
			'items': ml
		}
	elif request.method == 'POST':
		return DefaultRestMethods.post(db.Ls_unit_def, 'Landscape unit')
	abort(405, 'HTTP Method not allowed.')

@bp.route('/ls_units/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def lsunitsId(id):
	if request.method == 'GET':
		return DefaultRestMethods.get(id, db.Ls_unit_def, 'Landscape unit', back_refs=True)
	elif request.method == 'DELETE':
		return DefaultRestMethods.delete(id, db.Ls_unit_def, 'Landscape unit')
	elif request.method == 'PUT':
		return DefaultRestMethods.put(id, db.Ls_unit_def, 'Landscape unit')

	abort(405, 'HTTP Method not allowed.')

@bp.route('/ls_units/elements-table/<int:id>', methods=['GET'])
def lsunitsElementsTable(id):
	if request.method == 'GET':
		table = db.Ls_unit_ele
		filter_cols = [table.name]
		back_refs=False
		table_lookups={}
		recurse=False
		
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
			s = table.select().where((table.ls_unit_def_id == id) & (w))
		else:
			s = table.select().where(table.ls_unit_def_id == id)

		matches = s.count()

		if sort == 'name':
			sort_val = table.name if reverse != 'y' else table.name.desc()
		else:
			sort_val = SQL('[{}]'.format(sort))
			if reverse == 'y':
				sort_val = SQL('[{}]'.format(sort)).desc()

		m = s.order_by(sort_val).paginate(int(page), int(per_page))

		rh.close()
		items = {
			'model': m,
			'total': total,
			'matches': matches
		}

		m = items['model']

		if back_refs:
			ml = [model_to_dict(v, backrefs=True, max_depth=1) for v in m]
			for d in ml:
				RestHelpers.get_obj_name(d)
		else:
			ml = [model_to_dict(v, recurse=recurse) for v in m]

		return {
			'total': items['total'],
			'matches': items['matches'],
			'items': ml
		}
	abort(405, 'HTTP Method not allowed.')

# Ls_unit_ele

@bp.route('/ls_units/elements', methods=['GET', 'POST'])
def lsunitsElements():
	if request.method == 'GET':
		table = db.Ls_unit_ele
		filter_cols = [table.name]
		return DefaultRestMethods.get_paged_list(table, filter_cols, back_refs=True)
	elif request.method == 'POST':
		return DefaultRestMethods.post(db.Ls_unit_ele, 'Landscape unit element', extra_args=[{'name': 'ls_unit_def_id', 'type': int}])
	abort(405, 'HTTP Method not allowed.')

@bp.route('/ls_units/elements/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def lsunitsElementsId(id):
	if request.method == 'GET':
		return DefaultRestMethods.get(id, db.Ls_unit_ele, 'Landscape unit element', back_refs=True)
	elif request.method == 'DELETE':
		return DefaultRestMethods.delete(id, db.Ls_unit_ele, 'Landscape unit element')
	elif request.method == 'PUT':
		return DefaultRestMethods.put(id, db.Ls_unit_ele, 'Landscape unit element')

	abort(405, 'HTTP Method not allowed.')	
