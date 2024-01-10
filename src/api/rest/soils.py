from flask import Blueprint, request, abort
from .config import RequestHeaders as rh

from playhouse.shortcuts import model_to_dict
from peewee import *

from .defaults import DefaultRestMethods, RestHelpers
from database.project import soils as db

bp = Blueprint('soils', __name__, url_prefix='/soils')

# Soils_sol
soils_name = 'Soil'

@bp.route('/items', methods=['GET', 'POST'])
def items():
	if request.method == 'GET':
		table = db.Soils_sol
		filter_cols = [table.name, table.description, table.hyd_grp, table.texture]
		return DefaultRestMethods.get_paged_list(table, filter_cols)
	elif request.method == 'POST':
		return DefaultRestMethods.post(db.Soils_sol, soils_name)
	abort(405, 'HTTP Method not allowed.')

@bp.route('/items/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def itemsId(id):
	if request.method == 'GET':
		return DefaultRestMethods.get(id, db.Soils_sol, soils_name, back_refs=True)
	elif request.method == 'DELETE':
		return DefaultRestMethods.delete(id, db.Soils_sol, soils_name)
	elif request.method == 'PUT':
		return DefaultRestMethods.put(id, db.Soils_sol, soils_name)

	abort(405, 'HTTP Method not allowed.')

# Soils_sol_layer
soil_layer_name = 'Soil layer'

@bp.route('/layer', methods=['POST'])
def layer():
	if request.method == 'POST':
		return DefaultRestMethods.post(db.Soils_sol_layer, soil_layer_name, extra_args=[{'name': 'soil_id', 'type': int}])
	abort(405, 'HTTP Method not allowed.')

@bp.route('/layer/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def layerId(id):
	if request.method == 'GET':
		return DefaultRestMethods.get(id, db.Soils_sol_layer, soil_layer_name)
	elif request.method == 'DELETE':
		return DefaultRestMethods.delete(id, db.Soils_sol_layer, soil_layer_name)
	elif request.method == 'PUT':
		return DefaultRestMethods.put(id, db.Soils_sol_layer, soil_layer_name)

	abort(405, 'HTTP Method not allowed.')

# Nutrients_sol
soil_nutrients_name = 'Soil nutrients'

@bp.route('/nutrients', methods=['GET', 'POST'])
def nutrients():
	if request.method == 'GET':
		table = db.Nutrients_sol
		filter_cols = [table.name, table.description]
		return DefaultRestMethods.get_paged_list(table, filter_cols)
	elif request.method == 'POST':
		return DefaultRestMethods.post(db.Nutrients_sol, soil_nutrients_name)
	abort(405, 'HTTP Method not allowed.')

@bp.route('/nutrients/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def nutrientsId(id):
	if request.method == 'GET':
		return DefaultRestMethods.get(id, db.Nutrients_sol, soil_nutrients_name)
	elif request.method == 'DELETE':
		return DefaultRestMethods.delete(id, db.Nutrients_sol, soil_nutrients_name)
	elif request.method == 'PUT':
		return DefaultRestMethods.put(id, db.Nutrients_sol, soil_nutrients_name)

	abort(405, 'HTTP Method not allowed.')

@bp.route('/nutrients-many', methods=['GET', 'PUT'])
def nutrientsMany():
	if request.method == 'GET':
		return DefaultRestMethods.get_name_id_list(db.Nutrients_sol)
	elif request.method == 'PUT':
		return DefaultRestMethods.put_many(db.Nutrients_sol, soil_nutrients_name)
	
	abort(405, 'HTTP Method not allowed.')

# Soils_lte_sol

@bp.route('/lte', methods=['GET', 'POST'])
def lte():
	if request.method == 'GET':
		table = db.Soils_lte_sol
		filter_cols = [table.name]
		return DefaultRestMethods.get_paged_list(table, filter_cols)
	elif request.method == 'POST':
		return DefaultRestMethods.post(db.Soils_lte_sol, soils_name)
	abort(405, 'HTTP Method not allowed.')

@bp.route('/lte/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def lteId(id):
	if request.method == 'GET':
		return DefaultRestMethods.get(id, db.Soils_lte_sol, soils_name)
	elif request.method == 'DELETE':
		return DefaultRestMethods.delete(id, db.Soils_lte_sol, soils_name)
	elif request.method == 'PUT':
		return DefaultRestMethods.put(id, db.Soils_lte_sol, soils_name)

	abort(405, 'HTTP Method not allowed.')

@bp.route('/lte-many', methods=['GET', 'PUT'])
def lteMany():
	if request.method == 'GET':
		return DefaultRestMethods.get_name_id_list(db.Soils_lte_sol)
	elif request.method == 'PUT':
		return DefaultRestMethods.put_many(db.Soils_lte_sol, soils_name)
	
	abort(405, 'HTTP Method not allowed.')
