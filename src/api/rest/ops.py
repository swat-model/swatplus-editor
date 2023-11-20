from flask import Blueprint, request, abort
from .config import RequestHeaders as rh

from playhouse.shortcuts import model_to_dict
from peewee import *

from .defaults import DefaultRestMethods, RestHelpers
from database.project import ops as db
from database.datasets import ops as ds

bp = Blueprint('ops', __name__, url_prefix='/ops')

graze_name = 'Graze operation'
harvest_name = 'Harvest operation'
irrigation_name = 'Irrigation operation'
chemapp_name = 'Chemical application operation'
fire_name = 'Fire operation'
sweep_name = 'Sweep operation'

# Graze_ops

@bp.route('/graze', methods=['GET', 'POST'])
def graze():
	if request.method == 'GET':
		table = db.Graze_ops
		filter_cols = [table.name, table.description]
		return DefaultRestMethods.get_paged_list(table, filter_cols, back_refs=True)
	elif request.method == 'POST':
		return DefaultRestMethods.post(db.Graze_ops, graze_name, lookup_fields=['fert'])
	abort(405, 'HTTP Method not allowed.')

@bp.route('/graze/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def grazeId(id):
	if request.method == 'GET':
		return DefaultRestMethods.get(id, db.Graze_ops, graze_name, back_refs=True)
	elif request.method == 'DELETE':
		return DefaultRestMethods.delete(id, db.Graze_ops, graze_name)
	elif request.method == 'PUT':
		return DefaultRestMethods.put(id, db.Graze_ops, graze_name, lookup_fields=['fert'])

	abort(405, 'HTTP Method not allowed.')

@bp.route('/graze/many', methods=['GET', 'PUT'])
def grazeMany():
	if request.method == 'GET':
		return DefaultRestMethods.get_name_id_list(db.Graze_ops)
	elif request.method == 'PUT':
		return DefaultRestMethods.put_many(db.Graze_ops, graze_name, lookup_fields=['fert'])
	
	abort(405, 'HTTP Method not allowed.')

@bp.route('/graze/datasets/<name>', methods=['GET'])
def grazeDatasets(name):
	if request.method == 'GET':
		return DefaultRestMethods.get_datasets_name(name, ds.Graze_ops, graze_name, back_refs=True)

	abort(405, 'HTTP Method not allowed.')

# Harv_ops

@bp.route('/harvest', methods=['GET', 'POST'])
def harvest():
	if request.method == 'GET':
		table = db.Harv_ops
		filter_cols = [table.name]
		return DefaultRestMethods.get_paged_list(table, filter_cols)
	elif request.method == 'POST':
		return DefaultRestMethods.post(db.Harv_ops, harvest_name)
	abort(405, 'HTTP Method not allowed.')

@bp.route('/harvest/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def harvestId(id):
	if request.method == 'GET':
		return DefaultRestMethods.get(id, db.Harv_ops, harvest_name)
	elif request.method == 'DELETE':
		return DefaultRestMethods.delete(id, db.Harv_ops, harvest_name)
	elif request.method == 'PUT':
		return DefaultRestMethods.put(id, db.Harv_ops, harvest_name)

	abort(405, 'HTTP Method not allowed.')

@bp.route('/harvest/many', methods=['GET', 'PUT'])
def harvestMany():
	if request.method == 'GET':
		return DefaultRestMethods.get_name_id_list(db.Harv_ops)
	elif request.method == 'PUT':
		return DefaultRestMethods.put_many(db.Harv_ops, harvest_name)
	
	abort(405, 'HTTP Method not allowed.')

@bp.route('/harvest/datasets/<name>', methods=['GET'])
def harvestDatasets(name):
	if request.method == 'GET':
		return DefaultRestMethods.get_datasets_name(name, ds.Harv_ops, harvest_name)

	abort(405, 'HTTP Method not allowed.')

# Irr_ops

@bp.route('/irrigation', methods=['GET', 'POST'])
def irrigation():
	if request.method == 'GET':
		table = db.Irr_ops
		filter_cols = [table.name]
		return DefaultRestMethods.get_paged_list(table, filter_cols)
	elif request.method == 'POST':
		return DefaultRestMethods.post(db.Irr_ops, irrigation_name)
	abort(405, 'HTTP Method not allowed.')

@bp.route('/irrigation/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def irrigationId(id):
	if request.method == 'GET':
		return DefaultRestMethods.get(id, db.Irr_ops, irrigation_name)
	elif request.method == 'DELETE':
		return DefaultRestMethods.delete(id, db.Irr_ops, irrigation_name)
	elif request.method == 'PUT':
		return DefaultRestMethods.put(id, db.Irr_ops, irrigation_name)

	abort(405, 'HTTP Method not allowed.')

@bp.route('/irrigation/many', methods=['GET', 'PUT'])
def irrigationMany():
	if request.method == 'GET':
		return DefaultRestMethods.get_name_id_list(db.Irr_ops)
	elif request.method == 'PUT':
		return DefaultRestMethods.put_many(db.Irr_ops, irrigation_name)
	
	abort(405, 'HTTP Method not allowed.')

@bp.route('/irrigation/datasets/<name>', methods=['GET'])
def irrigationDatasets(name):
	if request.method == 'GET':
		return DefaultRestMethods.get_datasets_name(name, ds.Irr_ops, irrigation_name)

	abort(405, 'HTTP Method not allowed.')

# Chem_app_ops

@bp.route('/chemapp', methods=['GET', 'POST'])
def chemapp():
	if request.method == 'GET':
		table = db.Chem_app_ops
		filter_cols = [table.name]
		return DefaultRestMethods.get_paged_list(table, filter_cols)
	elif request.method == 'POST':
		return DefaultRestMethods.post(db.Chem_app_ops, chemapp_name)
	abort(405, 'HTTP Method not allowed.')

@bp.route('/chemapp/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def chemappId(id):
	if request.method == 'GET':
		return DefaultRestMethods.get(id, db.Chem_app_ops, chemapp_name)
	elif request.method == 'DELETE':
		return DefaultRestMethods.delete(id, db.Chem_app_ops, chemapp_name)
	elif request.method == 'PUT':
		return DefaultRestMethods.put(id, db.Chem_app_ops, chemapp_name)

	abort(405, 'HTTP Method not allowed.')

@bp.route('/chemapp/many', methods=['GET', 'PUT'])
def chemappMany():
	if request.method == 'GET':
		return DefaultRestMethods.get_name_id_list(db.Chem_app_ops)
	elif request.method == 'PUT':
		return DefaultRestMethods.put_many(db.Chem_app_ops, chemapp_name)
	
	abort(405, 'HTTP Method not allowed.')

@bp.route('/chemapp/datasets/<name>', methods=['GET'])
def chemappDatasets(name):
	if request.method == 'GET':
		return DefaultRestMethods.get_datasets_name(name, ds.Chem_app_ops, chemapp_name)

	abort(405, 'HTTP Method not allowed.')

# Fire_ops

@bp.route('/fire', methods=['GET', 'POST'])
def fire():
	if request.method == 'GET':
		table = db.Fire_ops
		filter_cols = [table.name]
		return DefaultRestMethods.get_paged_list(table, filter_cols)
	elif request.method == 'POST':
		return DefaultRestMethods.post(db.Fire_ops, fire_name)
	abort(405, 'HTTP Method not allowed.')

@bp.route('/fire/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def fireId(id):
	if request.method == 'GET':
		return DefaultRestMethods.get(id, db.Fire_ops, fire_name)
	elif request.method == 'DELETE':
		return DefaultRestMethods.delete(id, db.Fire_ops, fire_name)
	elif request.method == 'PUT':
		return DefaultRestMethods.put(id, db.Fire_ops, fire_name)

	abort(405, 'HTTP Method not allowed.')

@bp.route('/fire/many', methods=['GET', 'PUT'])
def fireMany():
	if request.method == 'GET':
		return DefaultRestMethods.get_name_id_list(db.Fire_ops)
	elif request.method == 'PUT':
		return DefaultRestMethods.put_many(db.Fire_ops, fire_name)
	
	abort(405, 'HTTP Method not allowed.')

@bp.route('/fire/datasets/<name>', methods=['GET'])
def fireDatasets(name):
	if request.method == 'GET':
		return DefaultRestMethods.get_datasets_name(name, ds.Fire_ops, fire_name)

	abort(405, 'HTTP Method not allowed.')

# Sweep_ops

@bp.route('/sweep', methods=['GET', 'POST'])
def sweep():
	if request.method == 'GET':
		table = db.Sweep_ops
		filter_cols = [table.name]
		return DefaultRestMethods.get_paged_list(table, filter_cols)
	elif request.method == 'POST':
		return DefaultRestMethods.post(db.Sweep_ops, sweep_name)
	abort(405, 'HTTP Method not allowed.')

@bp.route('/sweep/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def sweepId(id):
	if request.method == 'GET':
		return DefaultRestMethods.get(id, db.Sweep_ops, sweep_name)
	elif request.method == 'DELETE':
		return DefaultRestMethods.delete(id, db.Sweep_ops, sweep_name)
	elif request.method == 'PUT':
		return DefaultRestMethods.put(id, db.Sweep_ops, sweep_name)

	abort(405, 'HTTP Method not allowed.')

@bp.route('/sweep/many', methods=['GET', 'PUT'])
def sweepMany():
	if request.method == 'GET':
		return DefaultRestMethods.get_name_id_list(db.Sweep_ops)
	elif request.method == 'PUT':
		return DefaultRestMethods.put_many(db.Sweep_ops, sweep_name)
	
	abort(405, 'HTTP Method not allowed.')

@bp.route('/sweep/datasets/<name>', methods=['GET'])
def sweepDatasets(name):
	if request.method == 'GET':
		return DefaultRestMethods.get_datasets_name(name, ds.Sweep_ops, sweep_name)

	abort(405, 'HTTP Method not allowed.')
