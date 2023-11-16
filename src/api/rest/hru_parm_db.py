from flask import Blueprint, request, abort
from .config import RequestHeaders as rh

from playhouse.shortcuts import model_to_dict
from peewee import *

from .defaults import DefaultRestMethods, RestHelpers
from database.project import hru_parm_db as db
from database.datasets import hru_parm_db as ds

bp = Blueprint('db', __name__, url_prefix='/db')

plant_name = 'Plant'
fertilizer_name = 'Fertilizer'
tillage_name = 'Tillage'
pesticide_name = 'Pesticide'
pathogen_name = 'Pathogen'
urban_name = 'Urban'
septic_name = 'Septic'
snow_name = 'Snow'

# Plants.plt

@bp.route('/plants', methods=['GET', 'POST'])
def plants():
	if request.method == 'GET':
		table = db.Plants_plt
		filter_cols = [table.name, table.plnt_typ, table.gro_trig, table.description]
		return DefaultRestMethods.get_paged_list(table, filter_cols)
	elif request.method == 'POST':
		return DefaultRestMethods.post(db.Plants_plt, plant_name)
	abort(405, 'HTTP Method not allowed.')

@bp.route('/plants/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def plantsId(id):
	if request.method == 'GET':
		return DefaultRestMethods.get(id, db.Plants_plt, plant_name)
	elif request.method == 'DELETE':
		return DefaultRestMethods.delete(id, db.Plants_plt, plant_name)
	elif request.method == 'PUT':
		return DefaultRestMethods.put(id, db.Plants_plt, plant_name)

	abort(405, 'HTTP Method not allowed.')

@bp.route('/plants/many', methods=['GET', 'PUT'])
def plantsMany():
	if request.method == 'GET':
		return DefaultRestMethods.get_name_id_list(db.Plants_plt)
	elif request.method == 'PUT':
		return DefaultRestMethods.put_many(db.Plants_plt, plant_name)
	
	abort(405, 'HTTP Method not allowed.')

@bp.route('/plants/datasets/<name>', methods=['GET'])
def plantsDatasets(name):
	if request.method == 'GET':
		return DefaultRestMethods.get_datasets_name(name, ds.Plants_plt, plant_name)

	abort(405, 'HTTP Method not allowed.')

# Fertilizer.frt

@bp.route('/fertilizer', methods=['GET', 'POST'])
def fertilizer():
	if request.method == 'GET':
		table = db.Fertilizer_frt
		filter_cols = [table.name, table.description]
		return DefaultRestMethods.get_paged_list(table, filter_cols)
	elif request.method == 'POST':
		return DefaultRestMethods.post(db.Fertilizer_frt, fertilizer_name)
	abort(405, 'HTTP Method not allowed.')

@bp.route('/fertilizer/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def fertilizerId(id):
	if request.method == 'GET':
		return DefaultRestMethods.get(id, db.Fertilizer_frt, fertilizer_name)
	elif request.method == 'DELETE':
		return DefaultRestMethods.delete(id, db.Fertilizer_frt, fertilizer_name)
	elif request.method == 'PUT':
		return DefaultRestMethods.put(id, db.Fertilizer_frt, fertilizer_name)

	abort(405, 'HTTP Method not allowed.')

@bp.route('/fertilizer/many', methods=['GET', 'PUT'])
def fertilizerMany():
	if request.method == 'GET':
		return DefaultRestMethods.get_name_id_list(db.Fertilizer_frt)
	elif request.method == 'PUT':
		return DefaultRestMethods.put_many(db.Fertilizer_frt, fertilizer_name)
	
	abort(405, 'HTTP Method not allowed.')

@bp.route('/fertilizer/datasets/<name>', methods=['GET'])
def fertilizerDatasets(name):
	if request.method == 'GET':
		return DefaultRestMethods.get_datasets_name(name, ds.Fertilizer_frt, fertilizer_name)

	abort(405, 'HTTP Method not allowed.')

# Tillage.til

@bp.route('/tillage', methods=['GET', 'POST'])
def tillage():
	if request.method == 'GET':
		table = db.Tillage_til
		filter_cols = [table.name, table.description]
		return DefaultRestMethods.get_paged_list(table, filter_cols)
	elif request.method == 'POST':
		return DefaultRestMethods.post(db.Tillage_til, tillage_name)
	abort(405, 'HTTP Method not allowed.')

@bp.route('/tillage/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def tillageId(id):
	if request.method == 'GET':
		return DefaultRestMethods.get(id, db.Tillage_til, tillage_name)
	elif request.method == 'DELETE':
		return DefaultRestMethods.delete(id, db.Tillage_til, tillage_name)
	elif request.method == 'PUT':
		return DefaultRestMethods.put(id, db.Tillage_til, tillage_name)

	abort(405, 'HTTP Method not allowed.')

@bp.route('/tillage/many', methods=['GET', 'PUT'])
def tillageMany():
	if request.method == 'GET':
		return DefaultRestMethods.get_name_id_list(db.Tillage_til)
	elif request.method == 'PUT':
		return DefaultRestMethods.put_many(db.Tillage_til, tillage_name)
	
	abort(405, 'HTTP Method not allowed.')

@bp.route('/tillage/datasets/<name>', methods=['GET'])
def tillageDatasets(name):
	if request.method == 'GET':
		return DefaultRestMethods.get_datasets_name(name, ds.Tillage_til, tillage_name)

	abort(405, 'HTTP Method not allowed.')

# Pesticide.pst

@bp.route('/pesticides', methods=['GET', 'POST'])
def pesticides():
	if request.method == 'GET':
		table = db.Pesticide_pst
		filter_cols = [table.name, table.description]
		return DefaultRestMethods.get_paged_list(table, filter_cols)
	elif request.method == 'POST':
		return DefaultRestMethods.post(db.Pesticide_pst, pesticide_name)
	abort(405, 'HTTP Method not allowed.')

@bp.route('/pesticides/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def pesticidesId(id):
	if request.method == 'GET':
		return DefaultRestMethods.get(id, db.Pesticide_pst, pesticide_name)
	elif request.method == 'DELETE':
		return DefaultRestMethods.delete(id, db.Pesticide_pst, pesticide_name)
	elif request.method == 'PUT':
		return DefaultRestMethods.put(id, db.Pesticide_pst, pesticide_name)

	abort(405, 'HTTP Method not allowed.')

@bp.route('/pesticides/many', methods=['GET', 'PUT'])
def pesticidesMany():
	if request.method == 'GET':
		return DefaultRestMethods.get_name_id_list(db.Pesticide_pst)
	elif request.method == 'PUT':
		return DefaultRestMethods.put_many(db.Pesticide_pst, pesticide_name)
	
	abort(405, 'HTTP Method not allowed.')

@bp.route('/pesticides/datasets/<name>', methods=['GET'])
def pesticidesDatasets(name):
	if request.method == 'GET':
		return DefaultRestMethods.get_datasets_name(name, ds.Pesticide_pst, pesticide_name)

	abort(405, 'HTTP Method not allowed.')

# Pathogens.pth

@bp.route('/pathogens', methods=['GET', 'POST'])
def pathogens():
	if request.method == 'GET':
		table = db.Pathogens_pth
		filter_cols = [table.name, table.description]
		return DefaultRestMethods.get_paged_list(table, filter_cols)
	elif request.method == 'POST':
		return DefaultRestMethods.post(db.Pathogens_pth, pathogen_name)
	abort(405, 'HTTP Method not allowed.')

@bp.route('/pathogens/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def pathogensId(id):
	if request.method == 'GET':
		return DefaultRestMethods.get(id, db.Pathogens_pth, pathogen_name)
	elif request.method == 'DELETE':
		return DefaultRestMethods.delete(id, db.Pathogens_pth, pathogen_name)
	elif request.method == 'PUT':
		return DefaultRestMethods.put(id, db.Pathogens_pth, pathogen_name)

	abort(405, 'HTTP Method not allowed.')

@bp.route('/pathogens/many', methods=['GET', 'PUT'])
def pathogensMany():
	if request.method == 'GET':
		return DefaultRestMethods.get_name_id_list(db.Pathogens_pth)
	elif request.method == 'PUT':
		return DefaultRestMethods.put_many(db.Pathogens_pth, pathogen_name)
	
	abort(405, 'HTTP Method not allowed.')

@bp.route('/pathogens/datasets/<name>', methods=['GET'])
def pathogensDatasets(name):
	if request.method == 'GET':
		return DefaultRestMethods.get_datasets_name(name, ds.Pathogens_pth, pathogen_name)

	abort(405, 'HTTP Method not allowed.')

# Urban.urb

@bp.route('/urban', methods=['GET', 'POST'])
def urban():
	if request.method == 'GET':
		table = db.Urban_urb
		filter_cols = [table.name, table.description]
		return DefaultRestMethods.get_paged_list(table, filter_cols)
	elif request.method == 'POST':
		return DefaultRestMethods.post(db.Urban_urb, urban_name)
	abort(405, 'HTTP Method not allowed.')

@bp.route('/urban/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def urbanId(id):
	if request.method == 'GET':
		return DefaultRestMethods.get(id, db.Urban_urb, urban_name)
	elif request.method == 'DELETE':
		return DefaultRestMethods.delete(id, db.Urban_urb, urban_name)
	elif request.method == 'PUT':
		return DefaultRestMethods.put(id, db.Urban_urb, urban_name)

	abort(405, 'HTTP Method not allowed.')

@bp.route('/urban/many', methods=['GET', 'PUT'])
def urbanMany():
	if request.method == 'GET':
		return DefaultRestMethods.get_name_id_list(db.Urban_urb)
	elif request.method == 'PUT':
		return DefaultRestMethods.put_many(db.Urban_urb, urban_name)
	
	abort(405, 'HTTP Method not allowed.')

@bp.route('/urban/datasets/<name>', methods=['GET'])
def urbanDatasets(name):
	if request.method == 'GET':
		return DefaultRestMethods.get_datasets_name(name, ds.Urban_urb, urban_name)

	abort(405, 'HTTP Method not allowed.')

# Septic.sep

@bp.route('/septic', methods=['GET', 'POST'])
def septic():
	if request.method == 'GET':
		table = db.Septic_sep
		filter_cols = [table.name, table.description]
		return DefaultRestMethods.get_paged_list(table, filter_cols)
	elif request.method == 'POST':
		return DefaultRestMethods.post(db.Septic_sep, septic_name)
	abort(405, 'HTTP Method not allowed.')

@bp.route('/septic/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def septicId(id):
	if request.method == 'GET':
		return DefaultRestMethods.get(id, db.Septic_sep, septic_name)
	elif request.method == 'DELETE':
		return DefaultRestMethods.delete(id, db.Septic_sep, septic_name)
	elif request.method == 'PUT':
		return DefaultRestMethods.put(id, db.Septic_sep, septic_name)

	abort(405, 'HTTP Method not allowed.')

@bp.route('/septic/many', methods=['GET', 'PUT'])
def septicMany():
	if request.method == 'GET':
		return DefaultRestMethods.get_name_id_list(db.Septic_sep)
	elif request.method == 'PUT':
		return DefaultRestMethods.put_many(db.Septic_sep, septic_name)
	
	abort(405, 'HTTP Method not allowed.')

@bp.route('/septic/datasets/<name>', methods=['GET'])
def septicDatasets(name):
	if request.method == 'GET':
		return DefaultRestMethods.get_datasets_name(name, ds.Septic_sep, septic_name)

	abort(405, 'HTTP Method not allowed.')

# Snow.sno

@bp.route('/snow', methods=['GET', 'POST'])
def snow():
	if request.method == 'GET':
		table = db.Snow_sno
		filter_cols = [table.name, table.description]
		return DefaultRestMethods.get_paged_list(table, filter_cols)
	elif request.method == 'POST':
		return DefaultRestMethods.post(db.Snow_sno, snow_name)
	abort(405, 'HTTP Method not allowed.')

@bp.route('/snow/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def snowId(id):
	if request.method == 'GET':
		return DefaultRestMethods.get(id, db.Snow_sno, snow_name)
	elif request.method == 'DELETE':
		return DefaultRestMethods.delete(id, db.Snow_sno, snow_name)
	elif request.method == 'PUT':
		return DefaultRestMethods.put(id, db.Snow_sno, snow_name)

	abort(405, 'HTTP Method not allowed.')

@bp.route('/snow/many', methods=['GET', 'PUT'])
def snowMany():
	if request.method == 'GET':
		return DefaultRestMethods.get_name_id_list(db.Snow_sno)
	elif request.method == 'PUT':
		return DefaultRestMethods.put_many(db.Snow_sno, snow_name)
	
	abort(405, 'HTTP Method not allowed.')

@bp.route('/snow/datasets/<name>', methods=['GET'])
def snowDatasets(name):
	if request.method == 'GET':
		return DefaultRestMethods.get_datasets_name(name, ds.Snow_sno, snow_name)

	abort(405, 'HTTP Method not allowed.')
