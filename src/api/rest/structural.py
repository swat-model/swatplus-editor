from flask import Blueprint, request, abort
from .config import RequestHeaders as rh

from playhouse.shortcuts import model_to_dict
from peewee import *

from .defaults import DefaultRestMethods, RestHelpers
from database.project import structural as db
from database.datasets import structural as ds

bp = Blueprint('structural', __name__, url_prefix='/structural')

bmpuser_name = 'Best management practice'
tiledrain_name = 'Tile drains'
septic_name = 'Septic Systems'
filter_name = 'Filter Strip'
grassedww_name = 'Grassed Waterways'

# Tiledrain_str

@bp.route('/tiledrain', methods=['GET', 'POST'])
def tiledrain():
	if request.method == 'GET':
		table = db.Tiledrain_str
		filter_cols = [table.name]
		return DefaultRestMethods.get_paged_list(table, filter_cols)
	elif request.method == 'POST':
		return DefaultRestMethods.post(db.Tiledrain_str, tiledrain_name)
	abort(405, 'HTTP Method not allowed.')

@bp.route('/tiledrain/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def tiledrainId(id):
	if request.method == 'GET':
		return DefaultRestMethods.get(id, db.Tiledrain_str, tiledrain_name)
	elif request.method == 'DELETE':
		return DefaultRestMethods.delete(id, db.Tiledrain_str, tiledrain_name)
	elif request.method == 'PUT':
		return DefaultRestMethods.put(id, db.Tiledrain_str, tiledrain_name)

	abort(405, 'HTTP Method not allowed.')

@bp.route('/tiledrain/many', methods=['GET', 'PUT'])
def tiledrainMany():
	if request.method == 'GET':
		return DefaultRestMethods.get_name_id_list(db.Tiledrain_str)
	elif request.method == 'PUT':
		return DefaultRestMethods.put_many(db.Tiledrain_str, tiledrain_name)
	
	abort(405, 'HTTP Method not allowed.')

@bp.route('/tiledrain/datasets/<name>', methods=['GET'])
def tiledrainDatasets(name):
	if request.method == 'GET':
		return DefaultRestMethods.get_datasets_name(name, ds.Tiledrain_str, tiledrain_name)

	abort(405, 'HTTP Method not allowed.')

# Septic_str

@bp.route('/septic', methods=['GET', 'POST'])
def septic():
	if request.method == 'GET':
		table = db.Septic_str
		filter_cols = [table.name]
		return DefaultRestMethods.get_paged_list(table, filter_cols)
	elif request.method == 'POST':
		return DefaultRestMethods.post(db.Septic_str, septic_name)
	abort(405, 'HTTP Method not allowed.')

@bp.route('/septic/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def septicId(id):
	if request.method == 'GET':
		return DefaultRestMethods.get(id, db.Septic_str, septic_name)
	elif request.method == 'DELETE':
		return DefaultRestMethods.delete(id, db.Septic_str, septic_name)
	elif request.method == 'PUT':
		return DefaultRestMethods.put(id, db.Septic_str, septic_name)

	abort(405, 'HTTP Method not allowed.')

@bp.route('/septic/many', methods=['GET', 'PUT'])
def septicMany():
	if request.method == 'GET':
		return DefaultRestMethods.get_name_id_list(db.Septic_str)
	elif request.method == 'PUT':
		return DefaultRestMethods.put_many(db.Septic_str, septic_name)
	
	abort(405, 'HTTP Method not allowed.')

@bp.route('/septic/datasets/<name>', methods=['GET'])
def septicDatasets(name):
	if request.method == 'GET':
		return DefaultRestMethods.get_datasets_name(name, ds.Septic_str, septic_name)

	abort(405, 'HTTP Method not allowed.')

# Filterstrip_str

@bp.route('/filterstrip', methods=['GET', 'POST'])
def filterstrip():
	if request.method == 'GET':
		table = db.Filterstrip_str
		filter_cols = [table.name]
		return DefaultRestMethods.get_paged_list(table, filter_cols)
	elif request.method == 'POST':
		return DefaultRestMethods.post(db.Filterstrip_str, filter_name)
	abort(405, 'HTTP Method not allowed.')

@bp.route('/filterstrip/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def filterstripId(id):
	if request.method == 'GET':
		return DefaultRestMethods.get(id, db.Filterstrip_str, filter_name)
	elif request.method == 'DELETE':
		return DefaultRestMethods.delete(id, db.Filterstrip_str, filter_name)
	elif request.method == 'PUT':
		return DefaultRestMethods.put(id, db.Filterstrip_str, filter_name)

	abort(405, 'HTTP Method not allowed.')

@bp.route('/filterstrip/many', methods=['GET', 'PUT'])
def filterstripMany():
	if request.method == 'GET':
		return DefaultRestMethods.get_name_id_list(db.Filterstrip_str)
	elif request.method == 'PUT':
		return DefaultRestMethods.put_many(db.Filterstrip_str, filter_name)
	
	abort(405, 'HTTP Method not allowed.')

@bp.route('/filterstrip/datasets/<name>', methods=['GET'])
def filterstripDatasets(name):
	if request.method == 'GET':
		return DefaultRestMethods.get_datasets_name(name, ds.Filterstrip_str, filter_name)

	abort(405, 'HTTP Method not allowed.')

# Grassedww_str

@bp.route('/grassedww', methods=['GET', 'POST'])
def grassedww():
	if request.method == 'GET':
		table = db.Grassedww_str
		filter_cols = [table.name]
		return DefaultRestMethods.get_paged_list(table, filter_cols)
	elif request.method == 'POST':
		return DefaultRestMethods.post(db.Grassedww_str, grassedww_name)
	abort(405, 'HTTP Method not allowed.')

@bp.route('/grassedww/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def grassedwwId(id):
	if request.method == 'GET':
		return DefaultRestMethods.get(id, db.Grassedww_str, grassedww_name)
	elif request.method == 'DELETE':
		return DefaultRestMethods.delete(id, db.Grassedww_str, grassedww_name)
	elif request.method == 'PUT':
		return DefaultRestMethods.put(id, db.Grassedww_str, grassedww_name)

	abort(405, 'HTTP Method not allowed.')

@bp.route('/grassedww/many', methods=['GET', 'PUT'])
def grassedwwMany():
	if request.method == 'GET':
		return DefaultRestMethods.get_name_id_list(db.Grassedww_str)
	elif request.method == 'PUT':
		return DefaultRestMethods.put_many(db.Grassedww_str, grassedww_name)
	
	abort(405, 'HTTP Method not allowed.')

@bp.route('/grassedww/datasets/<name>', methods=['GET'])
def grassedwwDatasets(name):
	if request.method == 'GET':
		return DefaultRestMethods.get_datasets_name(name, ds.Grassedww_str, grassedww_name)

	abort(405, 'HTTP Method not allowed.')

# Bmpuser_str

@bp.route('/bmpuser', methods=['GET', 'POST'])
def bmpuser():
	if request.method == 'GET':
		table = db.Bmpuser_str
		filter_cols = [table.name]
		return DefaultRestMethods.get_paged_list(table, filter_cols)
	elif request.method == 'POST':
		return DefaultRestMethods.post(db.Bmpuser_str, bmpuser_name)
	abort(405, 'HTTP Method not allowed.')

@bp.route('/bmpuser/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def bmpuserId(id):
	if request.method == 'GET':
		return DefaultRestMethods.get(id, db.Bmpuser_str, bmpuser_name)
	elif request.method == 'DELETE':
		return DefaultRestMethods.delete(id, db.Bmpuser_str, bmpuser_name)
	elif request.method == 'PUT':
		return DefaultRestMethods.put(id, db.Bmpuser_str, bmpuser_name)

	abort(405, 'HTTP Method not allowed.')

@bp.route('/bmpuser/many', methods=['GET', 'PUT'])
def bmpuserMany():
	if request.method == 'GET':
		return DefaultRestMethods.get_name_id_list(db.Bmpuser_str)
	elif request.method == 'PUT':
		return DefaultRestMethods.put_many(db.Bmpuser_str, bmpuser_name)
	
	abort(405, 'HTTP Method not allowed.')

@bp.route('/bmpuser/datasets/<name>', methods=['GET'])
def bmpuserDatasets(name):
	if request.method == 'GET':
		return DefaultRestMethods.get_datasets_name(name, ds.Bmpuser_str, bmpuser_name)

	abort(405, 'HTTP Method not allowed.')
