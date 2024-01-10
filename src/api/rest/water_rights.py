from flask import Blueprint, request, abort
from .config import RequestHeaders as rh

from playhouse.shortcuts import model_to_dict
from peewee import *

from .defaults import DefaultRestMethods, RestHelpers
from database.project import water_rights as db

bp = Blueprint('water_rights', __name__, url_prefix='/water_rights')

# Water_allocation_wro
wa_table_name = 'Water allocation table'

@bp.route('/allocation', methods=['GET', 'POST'])
def allocation():
	if request.method == 'GET':
		table = db.Water_allocation_wro
		filter_cols = [table.name]
		return DefaultRestMethods.get_paged_list(table, filter_cols)
	elif request.method == 'POST':
		return DefaultRestMethods.post(db.Water_allocation_wro, wa_table_name)
	abort(405, 'HTTP Method not allowed.')

@bp.route('/allocation/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def allocationId(id):
	if request.method == 'GET':
		return DefaultRestMethods.get(id, db.Water_allocation_wro, wa_table_name, back_refs=True, max_depth=3)
	elif request.method == 'DELETE':
		return DefaultRestMethods.delete(id, db.Water_allocation_wro, wa_table_name)
	elif request.method == 'PUT':
		return DefaultRestMethods.put(id, db.Water_allocation_wro, wa_table_name)

	abort(405, 'HTTP Method not allowed.')

# Water_allocation_src_ob
wa_src_name = 'Water allocation source'

@bp.route('/source', methods=['GET', 'POST'])
def source():
	if request.method == 'GET':
		table = db.Water_allocation_src_ob
		filter_cols = [table.name]
		return DefaultRestMethods.get_paged_list(table, filter_cols)
	elif request.method == 'POST':
		return DefaultRestMethods.post(db.Water_allocation_src_ob, wa_src_name, extra_args=[{'name': 'water_allocation_id', 'type': int}])
	abort(405, 'HTTP Method not allowed.')

@bp.route('/source/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def sourceId(id):
	if request.method == 'GET':
		return DefaultRestMethods.get(id, db.Water_allocation_src_ob, wa_src_name)
	elif request.method == 'DELETE':
		return DefaultRestMethods.delete(id, db.Water_allocation_src_ob, wa_src_name)
	elif request.method == 'PUT':
		return DefaultRestMethods.put(id, db.Water_allocation_src_ob, wa_src_name)

	abort(405, 'HTTP Method not allowed.')

# Water_allocation_dmd_ob
wa_dmd_name = 'Water allocation demand object'

@bp.route('/demand', methods=['GET', 'POST'])
def demand():
	if request.method == 'GET':
		table = db.Water_allocation_dmd_ob
		filter_cols = [table.name]
		return DefaultRestMethods.get_paged_list(table, filter_cols)
	elif request.method == 'POST':
		return DefaultRestMethods.post(db.Water_allocation_dmd_ob, wa_dmd_name, extra_args=[{'name': 'water_allocation_id', 'type': int}])
	abort(405, 'HTTP Method not allowed.')

@bp.route('/demand/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def demandId(id):
	if request.method == 'GET':
		return DefaultRestMethods.get(id, db.Water_allocation_dmd_ob, wa_dmd_name)
	elif request.method == 'DELETE':
		return DefaultRestMethods.delete(id, db.Water_allocation_dmd_ob, wa_dmd_name)
	elif request.method == 'PUT':
		return DefaultRestMethods.put(id, db.Water_allocation_dmd_ob, wa_dmd_name)

	abort(405, 'HTTP Method not allowed.')

# Water_allocation_dmd_ob_src
wa_dmd_src_name = 'Water allocation demand source'

@bp.route('/demand-source', methods=['GET', 'POST'])
def demandSource():
	if request.method == 'GET':
		table = db.Water_allocation_dmd_ob_src
		filter_cols = [table.name]
		return DefaultRestMethods.get_paged_list(table, filter_cols)
	elif request.method == 'POST':
		return DefaultRestMethods.post(db.Water_allocation_dmd_ob_src, wa_dmd_src_name, extra_args=[{'name': 'water_allocation_dmd_ob_id', 'type': int}])
	abort(405, 'HTTP Method not allowed.')

@bp.route('/demand-source/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def demandSourceId(id):
	if request.method == 'GET':
		return DefaultRestMethods.get(id, db.Water_allocation_dmd_ob_src, wa_dmd_src_name)
	elif request.method == 'DELETE':
		return DefaultRestMethods.delete(id, db.Water_allocation_dmd_ob_src, wa_dmd_src_name)
	elif request.method == 'PUT':
		return DefaultRestMethods.put(id, db.Water_allocation_dmd_ob_src, wa_dmd_src_name)

	abort(405, 'HTTP Method not allowed.')