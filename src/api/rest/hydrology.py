from flask import Blueprint, request, abort
from .config import RequestHeaders as rh

from playhouse.shortcuts import model_to_dict
from peewee import *

from .defaults import DefaultRestMethods, RestHelpers
from database.project import hydrology as db

bp = Blueprint('hydrology', __name__, url_prefix='/hydrology')

hydrology_name = 'Hydrology'
topography_name = 'Topography'
field_name = 'Fields'

# Hydrology_hyd

@bp.route('/hydrology', methods=['GET', 'POST'])
def hydrology():
	if request.method == 'GET':
		table = db.Hydrology_hyd
		filter_cols = [table.name]
		return DefaultRestMethods.get_paged_list(table, filter_cols)
	elif request.method == 'POST':
		return DefaultRestMethods.post(db.Hydrology_hyd, hydrology_name)
	abort(405, 'HTTP Method not allowed.')

@bp.route('/hydrology/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def hydrologyId(id):
	if request.method == 'GET':
		return DefaultRestMethods.get(id, db.Hydrology_hyd, hydrology_name)
	elif request.method == 'DELETE':
		return DefaultRestMethods.delete(id, db.Hydrology_hyd, hydrology_name)
	elif request.method == 'PUT':
		return DefaultRestMethods.put(id, db.Hydrology_hyd, hydrology_name)

	abort(405, 'HTTP Method not allowed.')

@bp.route('/hydrology/many', methods=['GET', 'PUT'])
def hydrologyMany():
	if request.method == 'GET':
		return DefaultRestMethods.get_name_id_list(db.Hydrology_hyd)
	elif request.method == 'PUT':
		return DefaultRestMethods.put_many(db.Hydrology_hyd, hydrology_name)
	
	abort(405, 'HTTP Method not allowed.')

# Topography_hyd

@bp.route('/topography', methods=['GET', 'POST'])
def topography():
	if request.method == 'GET':
		table = db.Topography_hyd
		filter_cols = [table.name]
		return DefaultRestMethods.get_paged_list(table, filter_cols)
	elif request.method == 'POST':
		return DefaultRestMethods.post(db.Topography_hyd, topography_name)
	abort(405, 'HTTP Method not allowed.')

@bp.route('/topography/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def topographyId(id):
	if request.method == 'GET':
		return DefaultRestMethods.get(id, db.Topography_hyd, topography_name)
	elif request.method == 'DELETE':
		return DefaultRestMethods.delete(id, db.Topography_hyd, topography_name)
	elif request.method == 'PUT':
		return DefaultRestMethods.put(id, db.Topography_hyd, topography_name)

	abort(405, 'HTTP Method not allowed.')

@bp.route('/topography/many', methods=['GET', 'PUT'])
def topographyMany():
	if request.method == 'GET':
		return DefaultRestMethods.get_name_id_list(db.Topography_hyd)
	elif request.method == 'PUT':
		return DefaultRestMethods.put_many(db.Topography_hyd, topography_name)
	
	abort(405, 'HTTP Method not allowed.')

# Field_fld

@bp.route('/fields', methods=['GET', 'POST'])
def fields():
	if request.method == 'GET':
		table = db.Field_fld
		filter_cols = [table.name]
		return DefaultRestMethods.get_paged_list(table, filter_cols)
	elif request.method == 'POST':
		return DefaultRestMethods.post(db.Field_fld, field_name)
	abort(405, 'HTTP Method not allowed.')

@bp.route('/fields/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def fieldsId(id):
	if request.method == 'GET':
		return DefaultRestMethods.get(id, db.Field_fld, field_name)
	elif request.method == 'DELETE':
		return DefaultRestMethods.delete(id, db.Field_fld, field_name)
	elif request.method == 'PUT':
		return DefaultRestMethods.put(id, db.Field_fld, field_name)

	abort(405, 'HTTP Method not allowed.')

@bp.route('/fields/many', methods=['GET', 'PUT'])
def fieldsMany():
	if request.method == 'GET':
		return DefaultRestMethods.get_name_id_list(db.Field_fld)
	elif request.method == 'PUT':
		return DefaultRestMethods.put_many(db.Field_fld, field_name)
	
	abort(405, 'HTTP Method not allowed.')
