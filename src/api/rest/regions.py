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
