from flask import Blueprint, request, abort
from .config import RequestHeaders as rh

from playhouse.shortcuts import model_to_dict
from peewee import *

from .defaults import DefaultRestMethods, RestHelpers
from database.project import init as db
from database.project.soils import Nutrients_sol
from database.project.simulation import Constituents_cs
from database.project.hru_parm_db import Pesticide_pst, Pathogens_pth
from database.project.salts import Salt_hru_ini_cs, Salt_module
from database.project import base as project_base
from database import lib as db_lib

bp = Blueprint('init', __name__, url_prefix='/init')

soil_plant_name = 'Soil/plant'

# Soil_plant_ini

def save_soil_plant_args(m, args):
	m.name = args['name']
	m.sw_frac = None if 'sw_frac' not in args else args['sw_frac']

	if 'nutrients_name' in args:
		m.nutrients_id = RestHelpers.get_id_from_name(Nutrients_sol, args['nutrients_name'])
	if 'pest_name' in args:
		m.pest_id = RestHelpers.get_id_from_name(db.Pest_hru_ini, args['pest_name'])
	if 'path_name' in args:
		m.path_id = RestHelpers.get_id_from_name(db.Path_hru_ini, args['path_name'])
	if 'hmet_name' in args:
		m.hmet_id = RestHelpers.get_id_from_name(db.Hmet_hru_ini, args['hmet_name'])
	if 'salt_name' in args:
		m.salt_cs_id = RestHelpers.get_id_from_name(Salt_hru_ini_cs, args['salt_name'])

	return m.save()

@bp.route('/soil_plant', methods=['GET', 'POST'])
def soil_plant():
	if request.method == 'GET':
		table = db.Soil_plant_ini
		filter_cols = [table.name]
		return DefaultRestMethods.get_paged_list(table, filter_cols, back_refs=True)
	elif request.method == 'POST':
		project_db = request.headers.get(rh.PROJECT_DB)
		has_db,error = rh.init(project_db)
		if not has_db: abort(400, error)

		args = request.json
		try:
			m = db.Soil_plant_ini()
			result = save_soil_plant_args(m, args)

			rh.close()
			if result > 0:
				return {'id': m.id }, 200

			abort(400, 'Unable to create record.')
		except IntegrityError as e:
			rh.close()
			abort(400, 'Name must be unique.')
		except Nutrients_sol.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['nutrients_name']))
		except db.Pest_hru_ini.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['pest_name']))
		except db.Path_hru_ini.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['path_name']))
		except db.Hmet_hru_ini.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['hmet_name']))
		except Salt_hru_ini_cs.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['salt_name']))
		except Exception as ex:
			rh.close()
			abort(400, 'Unexpected error {ex}'.format(ex=ex))
	abort(405, 'HTTP Method not allowed.')

@bp.route('/soil_plant/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def soil_plantId(id):
	if request.method == 'GET':
		return DefaultRestMethods.get(id, db.Soil_plant_ini, soil_plant_name, back_refs=True)
	elif request.method == 'DELETE':
		return DefaultRestMethods.delete(id, db.Soil_plant_ini, soil_plant_name)
	elif request.method == 'PUT':
		project_db = request.headers.get(rh.PROJECT_DB)
		has_db,error = rh.init(project_db)
		if not has_db: abort(400, error)

		args = request.json
		try:
			m = db.Soil_plant_ini.get(db.Soil_plant_ini.id == id)
			result = save_soil_plant_args(m, args)

			rh.close()
			if result > 0:
				return {'id': m.id }, 200

			abort(400, 'Unable to create record.')
		except IntegrityError as e:
			rh.close()
			abort(400, 'Name must be unique.')
		except db.Soil_plant_ini.DoesNotExist:
			rh.close()
			abort(404, 'Soil plant properties {id} does not exist'.format(id=id))
		except Nutrients_sol.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['nutrients_name']))
		except db.Pest_hru_ini.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['pest_name']))
		except db.Path_hru_ini.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['path_name']))
		except db.Hmet_hru_ini.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['hmet_name']))
		except Salt_hru_ini_cs.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['salt_name']))
		except Exception as ex:
			rh.close()
			abort(400, 'Unexpected error {ex}'.format(ex=ex))

	abort(405, 'HTTP Method not allowed.')

@bp.route('/soil_plant/many', methods=['GET', 'PUT'])
def soil_plantMany():
	if request.method == 'GET':
		return DefaultRestMethods.get_name_id_list(db.Soil_plant_ini)
	elif request.method == 'PUT':
		project_db = request.headers.get(rh.PROJECT_DB)
		has_db,error = rh.init(project_db)
		if not has_db: abort(400, error)

		args = request.json
		try:
			param_dict = {}

			if 'sw_frac' in args:
				param_dict['sw_frac'] = args['sw_frac']
			if 'nutrients_name' in args:
				param_dict['nutrients_id'] = RestHelpers.get_id_from_name(Nutrients_sol, args['nutrients_name'])
			if 'pest_name' in args:
				param_dict['pest_id'] = RestHelpers.get_id_from_name(db.Pest_hru_ini, args['pest_name'])
			if 'path_name' in args:
				param_dict['path_id'] = RestHelpers.get_id_from_name(db.Path_hru_ini, args['path_name'])
			if 'hmet_name' in args:
				param_dict['hmet_id'] = RestHelpers.get_id_from_name(db.Hmet_hru_ini, args['hmet_name'])
			if 'salt_name' in args:
				param_dict['salt_cs_id'] = RestHelpers.get_id_from_name(Salt_hru_ini_cs, args['salt_name'])

			query = db.Soil_plant_ini.update(param_dict).where(db.Soil_plant_ini.id.in_(args['selected_ids']))
			result = query.execute()

			rh.close()
			if result > 0:
				return '', 200

			abort(400, 'Unable to update properties.')
		except db.Soil_plant_ini.DoesNotExist:
			rh.close()
			abort(404, 'Soil plant properties {id} does not exist'.format(id=id))
		except Nutrients_sol.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['nutrients_name']))
		except db.Pest_hru_ini.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['pest_name']))
		except db.Path_hru_ini.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['path_name']))
		except db.Hmet_hru_ini.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['hmet_name']))
		except Salt_hru_ini_cs.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['salt_name']))
		except Exception as ex:
			rh.close()
			abort(400, 'Unexpected error {ex}'.format(ex=ex))
	
	abort(405, 'HTTP Method not allowed.')

# Om_water_ini

om_water_name = 'Organic mineral water'

@bp.route('/om_water', methods=['GET', 'POST'])
def om_water():
	if request.method == 'GET':
		table = db.Om_water_ini
		filter_cols = [table.name]
		return DefaultRestMethods.get_paged_list(table, filter_cols)
	elif request.method == 'POST':
		return DefaultRestMethods.post(db.Om_water_ini, om_water_name)
	abort(405, 'HTTP Method not allowed.')

@bp.route('/om_water/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def om_waterId(id):
	if request.method == 'GET':
		return DefaultRestMethods.get(id, db.Om_water_ini, om_water_name)
	elif request.method == 'DELETE':
		return DefaultRestMethods.delete(id, db.Om_water_ini, om_water_name)
	elif request.method == 'PUT':
		return DefaultRestMethods.put(id, db.Om_water_ini, om_water_name)

	abort(405, 'HTTP Method not allowed.')

@bp.route('/om_water/many', methods=['GET', 'PUT'])
def om_waterMany():
	if request.method == 'GET':
		return DefaultRestMethods.get_name_id_list(db.Om_water_ini)
	elif request.method == 'PUT':
		return DefaultRestMethods.put_many(db.Om_water_ini, om_water_name)
	
	abort(405, 'HTTP Method not allowed.')

# Plant_ini

plant_ini_name = 'Plant community'

@bp.route('/plant_ini', methods=['GET', 'POST'])
def plant_ini():
	if request.method == 'GET':
		table = db.Plant_ini
		filter_cols = [table.name]
		items = DefaultRestMethods.get_paged_items(table, filter_cols)
		m = items['model']
		ml = [{'id': v.id, 'name': v.name, 'rot_yr_ini': v.rot_yr_ini, 'description': v.description, 'num_plants': len(v.plants)} for v in m]

		return {
			'total': items['total'],
			'matches': items['matches'],
			'items': ml
		}
	elif request.method == 'POST':
		return DefaultRestMethods.post(db.Plant_ini, plant_ini_name)
	abort(405, 'HTTP Method not allowed.')

@bp.route('/plant_ini/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def plant_iniId(id):
	if request.method == 'GET':
		return DefaultRestMethods.get(id, db.Plant_ini, plant_ini_name, back_refs=True, max_depth=2)
	elif request.method == 'DELETE':
		return DefaultRestMethods.delete(id, db.Plant_ini, plant_ini_name)
	elif request.method == 'PUT':
		return DefaultRestMethods.put(id, db.Plant_ini, plant_ini_name)

	abort(405, 'HTTP Method not allowed.')

# Plant_ini_item

plant_ini_item_name = 'Plant'

@bp.route('/plant_ini_item', methods=['POST'])
def plant_ini_item():
	if request.method == 'POST':
		return DefaultRestMethods.post(db.Plant_ini_item, plant_ini_item_name)
	abort(405, 'HTTP Method not allowed.')

@bp.route('/plant_ini_item/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def plant_ini_itemId(id):
	if request.method == 'GET':
		return DefaultRestMethods.get(id, db.Plant_ini_item, plant_ini_item_name)
	elif request.method == 'DELETE':
		return DefaultRestMethods.delete(id, db.Plant_ini_item, plant_ini_item_name)
	elif request.method == 'PUT':
		return DefaultRestMethods.put(id, db.Plant_ini_item, plant_ini_item_name)

	abort(405, 'HTTP Method not allowed.')

#Constituents_cs

constituents_name = 'Constituents'

def create_constit_ini_tables():
	project_base.db.create_tables([db.Pest_hru_ini, db.Pest_hru_ini_item, db.Pest_water_ini, db.Pest_water_ini_item, 
		db.Path_hru_ini, db.Path_hru_ini_item, db.Path_water_ini, db.Path_water_ini_item, 
		db.Hmet_hru_ini, db.Hmet_hru_ini_item, db.Hmet_water_ini, db.Hmet_water_ini_item, 
		db.Salt_hru_ini, db.Salt_hru_ini_item, db.Salt_water_ini, db.Salt_water_ini_item,
		Salt_module])
	
@bp.route('/constituents', methods=['GET','DELETE','PUT'])
def constituents():
	project_db = request.headers.get(rh.PROJECT_DB)
	has_db,error = rh.init(project_db)
	if not has_db: abort(400, error)
	
	if request.method == 'GET':
		create_constit_ini_tables()

		if Constituents_cs.select().count() > 0:
			m = Constituents_cs.get()
			rh.close()
			return {
				'using': True,
				'pests': [] if m.pest_coms is None else sorted(m.pest_coms.split(',')),
				'paths': [] if m.path_coms is None else sorted(m.path_coms.split(',')),
				'hmets': [] if m.hmet_coms is None else sorted(m.hmet_coms.split(',')),
				'salts': [] if m.salt_coms is None else sorted(m.salt_coms.split(','))
			}

		rh.close()
		return {
			'using': False,
			'pests': [],
			'paths': [],
			'hmets': [],
			'salts': []
		}
	if request.method == 'DELETE':
		if Constituents_cs.select().count() > 0:
			project_base.db.execute_sql('PRAGMA foreign_keys = ON')
			db.Pest_hru_ini.delete().execute()
			db.Pest_water_ini.delete().execute()
			db.Path_hru_ini.delete().execute()
			db.Path_water_ini.delete().execute()
			db.Hmet_hru_ini.delete().execute()
			db.Hmet_water_ini.delete().execute()
			Constituents_cs.delete().execute()

		rh.close()
		return '', 204
	if request.method == 'PUT':
		args = request.json
		try:
			result = 1
			if Constituents_cs.select().count() < 1:
				Constituents_cs.create(id=1, name='Constituents')
			if Salt_module.select().count() < 1:
				Salt_module.create(id=1)

			if 'pests' in args:
				if len(args['pests']) < 1:
					db.Pest_hru_ini_item.delete().execute()
					db.Pest_water_ini_item.delete().execute()
					result = Constituents_cs.update(pest_coms=None).execute()
				else:
					pest_coms = None if len(args['pests']) < 1 else ','.join(args['pests'])
					pest_ids = Pesticide_pst.select().where(Pesticide_pst.name.in_(args['pests']))
					db.Pest_hru_ini_item.delete().where(db.Pest_hru_ini_item.name.not_in(pest_ids)).execute()
					db.Pest_water_ini_item.delete().where(db.Pest_water_ini_item.name.not_in(pest_ids)).execute()
					result = Constituents_cs.update(pest_coms=pest_coms).execute()
			if 'paths' in args:
				if len(args['paths']) < 1:
					db.Path_hru_ini_item.delete().execute()
					db.Path_water_ini_item.delete().execute()
					result = Constituents_cs.update(path_coms=None).execute()
				else:
					path_coms = None if 'paths' not in args or len(args['paths']) < 1 else ','.join(args['paths'])
					path_ids = Pathogens_pth.select().where(Pathogens_pth.name.in_(args['paths']))
					db.Path_hru_ini_item.delete().where(db.Path_hru_ini_item.name.not_in(path_ids)).execute()
					db.Path_water_ini_item.delete().where(db.Path_water_ini_item.name.not_in(path_ids)).execute()
					result = Constituents_cs.update(path_coms=path_coms).execute()
			if 'enable_salts' in args:
				salt_coms = 'so4,ca,mg,na,k,cl,co3,hco3' if args['enable_salts'] == 1 else None
				result = Constituents_cs.update(salt_coms=salt_coms).execute()
				result = Salt_module.update(enable=args['enable_salts']==1).execute()

			rh.close()
			if result > 0:
				return '', 200

			abort(400, 'Unable to update save changes to constituents.')
		except Exception as ex:
			rh.close()
			abort(400, 'Unexpected error {ex}'.format(ex=ex))
	abort(405, 'HTTP Method not allowed.')

def get_constituents_ini(ini_table, db_table, col_name):
	project_db = request.headers.get(rh.PROJECT_DB)
	has_db,error = rh.init(project_db)
	if not has_db: abort(400, error)
	
	items = [model_to_dict(v, backrefs=True, max_depth=1) for v in ini_table.select()]
	constituents = []
	if Constituents_cs.select().count() > 0:
		c = model_to_dict(Constituents_cs.get())[col_name]
		names = [] if c is None else sorted(c.split(','))
		constituents = [{'id': v.id, 'name': v.name} for v in db_table.select().where(db_table.name.in_(names))]

	rh.close()
	return {
		'items': items,
		'constituents': constituents
	}

def save_constituents_ini(ini_table, ini_item_table, rel_col_name, row1='plant', row2='soil'):
	project_db = request.headers.get(rh.PROJECT_DB)
	has_db,error = rh.init(project_db)
	if not has_db: abort(400, error)
	
	args = request.json
	
	ini_item_table.delete().execute()
	ini_table.delete().execute()

	if 'items' in args and len(args['items']) > 0:
		for item in args['items']:
			m = ini_table(name = item['name'])
			m.save()

			rows = []
			for row in item['rows']:
				rows.append({
					rel_col_name: m.id,
					'name_id': row['name_id'],
					row1: row[row1],
					row2: row[row2]
				})

			db_lib.bulk_insert(project_base.db, ini_item_table, rows)
	rh.close()

@bp.route('/constituents/pest-hru', methods=['GET','PUT'])
def constituentsPestHru():
	if request.method == 'GET':
		create_constit_ini_tables()
		return get_constituents_ini(db.Pest_hru_ini, Pesticide_pst, 'pest_coms')
	if request.method == 'PUT':
		try:
			save_constituents_ini(db.Pest_hru_ini, db.Pest_hru_ini_item, 'pest_hru_ini_id')
			return '',200
		except Exception as ex:
			abort(400, 'Unexpected error {}'.format(ex))
		
	abort(405, 'HTTP Method not allowed.')

@bp.route('/constituents/pest-water', methods=['GET','PUT'])
def constituentsPestWater():
	if request.method == 'GET':
		create_constit_ini_tables()
		return get_constituents_ini(db.Pest_water_ini, Pesticide_pst, 'pest_coms')
	if request.method == 'PUT':
		try:
			save_constituents_ini(db.Pest_water_ini, db.Pest_water_ini_item, 'pest_water_ini_id', row1='water', row2='benthic')
			return '',200
		except Exception as ex:
			abort(400, 'Unexpected error {}'.format(ex))
		
	abort(405, 'HTTP Method not allowed.')

@bp.route('/constituents/path-hru', methods=['GET','PUT'])
def constituentsPathHru():
	if request.method == 'GET':
		create_constit_ini_tables()
		return get_constituents_ini(db.Path_hru_ini, Pathogens_pth, 'path_coms')
	if request.method == 'PUT':
		try:
			save_constituents_ini(db.Path_hru_ini, db.Path_hru_ini_item, 'path_hru_ini_id')
			return '',200
		except Exception as ex:
			abort(400, 'Unexpected error {}'.format(ex))
		
	abort(405, 'HTTP Method not allowed.')

@bp.route('/constituents/path-water', methods=['GET','PUT'])
def constituentsPathWater():
	if request.method == 'GET':
		create_constit_ini_tables()
		return get_constituents_ini(db.Path_water_ini, Pathogens_pth, 'path_coms')
	if request.method == 'PUT':
		try:
			save_constituents_ini(db.Path_water_ini, db.Path_water_ini_item, 'path_water_ini_id', row1='water', row2='benthic')
			return '',200
		except Exception as ex:
			abort(400, 'Unexpected error {}'.format(ex))
		
	abort(405, 'HTTP Method not allowed.')
