from flask import Blueprint, request, abort
from .config import RequestHeaders as rh

from playhouse.shortcuts import model_to_dict
from peewee import *

from .defaults import DefaultRestMethods, RestHelpers
from database.project import salts as db
from database.project import base as project_base, recall
from database.project.simulation import Time_sim
from database.project.climate import Atmo_cli_sta
from database.project.hru_parm_db import Fertilizer_frt, Urban_urb, Plants_plt
from database import lib as db_lib

import datetime

bp = Blueprint('salts', __name__, url_prefix='/salts')

@bp.route('/salt_aqu_ini', methods=['GET', 'POST'])
def salt_aqu_ini():
	if request.method == 'GET':
		table = db.Salt_aqu_ini
		filter_cols = [table.name]
		return DefaultRestMethods.get_paged_list(table, filter_cols)
	elif request.method == 'POST':
		return DefaultRestMethods.post(db.Salt_aqu_ini, 'Value')
	abort(405, 'HTTP Method not allowed.')

@bp.route('/salt_aqu_ini/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def salt_aqu_iniId(id):
	if request.method == 'GET':
		return DefaultRestMethods.get(id, db.Salt_aqu_ini, 'Value')
	elif request.method == 'DELETE':
		return DefaultRestMethods.delete(id, db.Salt_aqu_ini, 'Value')
	elif request.method == 'PUT':
		return DefaultRestMethods.put(id, db.Salt_aqu_ini, 'Value')

	abort(405, 'HTTP Method not allowed.')

@bp.route('/salt_channel_ini', methods=['GET', 'POST'])
def salt_channel_ini():
	if request.method == 'GET':
		table = db.Salt_channel_ini
		filter_cols = [table.name]
		return DefaultRestMethods.get_paged_list(table, filter_cols)
	elif request.method == 'POST':
		return DefaultRestMethods.post(db.Salt_channel_ini, 'Value')
	abort(405, 'HTTP Method not allowed.')

@bp.route('/salt_channel_ini/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def salt_channel_iniId(id):
	if request.method == 'GET':
		return DefaultRestMethods.get(id, db.Salt_channel_ini, 'Value')
	elif request.method == 'DELETE':
		return DefaultRestMethods.delete(id, db.Salt_channel_ini, 'Value')
	elif request.method == 'PUT':
		return DefaultRestMethods.put(id, db.Salt_channel_ini, 'Value')

	abort(405, 'HTTP Method not allowed.')

@bp.route('/salt_res_ini', methods=['GET', 'POST'])
def salt_res_ini():
	if request.method == 'GET':
		table = db.Salt_res_ini
		filter_cols = [table.name]
		return DefaultRestMethods.get_paged_list(table, filter_cols)
	elif request.method == 'POST':
		return DefaultRestMethods.post(db.Salt_res_ini, 'Value')
	abort(405, 'HTTP Method not allowed.')

@bp.route('/salt_res_ini/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def salt_res_iniId(id):
	if request.method == 'GET':
		return DefaultRestMethods.get(id, db.Salt_res_ini, 'Value')
	elif request.method == 'DELETE':
		return DefaultRestMethods.delete(id, db.Salt_res_ini, 'Value')
	elif request.method == 'PUT':
		return DefaultRestMethods.put(id, db.Salt_res_ini, 'Value')

	abort(405, 'HTTP Method not allowed.')

@bp.route('/salt_hru_ini_cs', methods=['GET', 'POST'])
def salt_hru_ini_cs():
	if request.method == 'GET':
		table = db.Salt_hru_ini_cs
		filter_cols = [table.name]
		return DefaultRestMethods.get_paged_list(table, filter_cols)
	elif request.method == 'POST':
		return DefaultRestMethods.post(db.Salt_hru_ini_cs, 'Value')
	abort(405, 'HTTP Method not allowed.')

@bp.route('/salt_hru_ini_cs/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def salt_hru_ini_csId(id):
	if request.method == 'GET':
		return DefaultRestMethods.get(id, db.Salt_hru_ini_cs, 'Value')
	elif request.method == 'DELETE':
		return DefaultRestMethods.delete(id, db.Salt_hru_ini_cs, 'Value')
	elif request.method == 'PUT':
		return DefaultRestMethods.put(id, db.Salt_hru_ini_cs, 'Value')

	abort(405, 'HTTP Method not allowed.')

@bp.route('/enable-plants', methods=['GET','PUT'])
def enablePlants():
	project_db = request.headers.get(rh.PROJECT_DB)
	has_db,error = rh.init(project_db)
	if not has_db: abort(400, error)

	module, created = db.Salt_module.get_or_create(id=1)
	flags, created2 = db.Salt_plants_flags.get_or_create(id=1)
	
	if request.method == 'GET':
		rh.close()
		return {
			'plants_uptake': module.plants_uptake,
			'enabled': flags.enabled,
			'soil': flags.soil,
			'stress': flags.stress,
			'conversion_factor': flags.conversion_factor
		}
	elif request.method == 'PUT':
		args = request.json
		result = db.Salt_module.update(plants_uptake=args['plants_uptake']).execute()
		result2 = db.Salt_plants_flags.update(enabled=args['enabled'], soil=args['soil'], stress=args['stress'], conversion_factor=args['conversion_factor']).execute()
		
		if result > 0 and result2 > 0:
			rh.close()
			return '', 200

		rh.close()
		abort(400, 'Unable to update salts module.')

@bp.route('/plants/<int:id>', methods=['GET','PUT'])
def plants(id):
	if request.method == 'GET':
		project_db = request.headers.get(rh.PROJECT_DB)
		has_db,error = rh.init(project_db)
		if not has_db: abort(400, error)

		item = Plants_plt.get_or_none(Plants_plt.id == id)
		
		if item is None:
			rh.close()
			abort(404, 'Urban not found.')

		if item.salts is None or len(item.salts) == 0:
			defaults = db.Salt_plants.get_a_b_defaults()
			a = 0
			b = 0
			if item.name in defaults:
				a = defaults[item.name][0]
				b = defaults[item.name][1]
			v = db.Salt_plants.create(name_id=id, a=a, b=b, so4=0.1, ca=0.1, mg=0.1, na=0.1, k=0.1, cl=0.1, co3=0.1, hco3=0.1)
		else:
			v = item.salts[0]

		d = model_to_dict(v, recurse=False)
		for k in d:
			if k == 'name':
				d['name_id'] = d[k]
				d.pop(k)
				break

		rh.close()
		return {
			'name': item.name,
			'item': d
		}
	elif request.method == 'PUT':
		return DefaultRestMethods.put(id, db.Salt_plants, 'Value')
	
@bp.route('/enable-irrigation', methods=['GET','PUT'])
def enableIrrigation():
	project_db = request.headers.get(rh.PROJECT_DB)
	has_db,error = rh.init(project_db)
	if not has_db: abort(400, error)

	module, created = db.Salt_module.get_or_create(id=1)
	
	if request.method == 'GET':
		rh.close()
		return {
			'irrigation': module.irrigation,
			'has_hru_ini': db.Salt_hru_ini_cs.select().count() > 0
		}
	elif request.method == 'PUT':
		args = request.json
		result = db.Salt_module.update(irrigation=args['irrigation']).execute()
		
		if result > 0:
			rh.close()
			return '', 200

		rh.close()
		abort(400, 'Unable to update salts module.')

@bp.route('/irrigation/<int:id>', methods=['GET','PUT'])
def irrigation(id):
	if request.method == 'GET':
		project_db = request.headers.get(rh.PROJECT_DB)
		has_db,error = rh.init(project_db)
		if not has_db: abort(400, error)

		item = db.Salt_hru_ini_cs.get_or_none(db.Salt_hru_ini_cs.id == id)
		
		if item is None:
			rh.close()
			abort(404, 'Urban not found.')

		if item.salts is None or len(item.salts) == 0:
			v = db.Salt_irrigation.create(name_id=id, so4=0, ca=0, mg=0, na=0, k=0, cl=0, co3=0, hco3=0)
		else:
			v = item.salts[0]

		d = model_to_dict(v, recurse=False)
		for k in d:
			if k == 'name':
				d['name_id'] = d[k]
				d.pop(k)
				break

		rh.close()
		return {
			'name': item.name,
			'item': d
		}
	elif request.method == 'PUT':
		return DefaultRestMethods.put(id, db.Salt_irrigation, 'Value')

@bp.route('/enable-urban', methods=['GET','PUT'])
def enableUrban():
	project_db = request.headers.get(rh.PROJECT_DB)
	has_db,error = rh.init(project_db)
	if not has_db: abort(400, error)

	module, created = db.Salt_module.get_or_create(id=1)
	
	if request.method == 'GET':
		rh.close()
		return {
			'urban': module.urban
		}
	elif request.method == 'PUT':
		args = request.json
		result = db.Salt_module.update(urban=args['urban']).execute()
		
		if result > 0:
			rh.close()
			return '', 200

		rh.close()
		abort(400, 'Unable to update salts module.')

@bp.route('/urban/<int:id>', methods=['GET','PUT'])
def urban(id):
	if request.method == 'GET':
		project_db = request.headers.get(rh.PROJECT_DB)
		has_db,error = rh.init(project_db)
		if not has_db: abort(400, error)

		item = Urban_urb.get_or_none(Urban_urb.id == id)
		
		if item is None:
			rh.close()
			abort(404, 'Urban not found.')

		if item.salts is None or len(item.salts) == 0:
			v = db.Salt_urban.create(name_id=id, so4=250, ca=150, mg=60, na=45, k=2, cl=55, co3=1, hco3=200)
		else:
			v = item.salts[0]

		d = model_to_dict(v, recurse=False)
		for k in d:
			if k == 'name':
				d['name_id'] = d[k]
				d.pop(k)
				break

		rh.close()
		return {
			'name': item.name,
			'item': d
		}
	elif request.method == 'PUT':
		return DefaultRestMethods.put(id, db.Salt_urban, 'Value')

@bp.route('/enable-fert', methods=['GET','PUT'])
def enableFert():
	project_db = request.headers.get(rh.PROJECT_DB)
	has_db,error = rh.init(project_db)
	if not has_db: abort(400, error)

	module, created = db.Salt_module.get_or_create(id=1)
	
	if request.method == 'GET':
		rh.close()
		return {
			'fert': module.fert
		}
	elif request.method == 'PUT':
		args = request.json
		result = db.Salt_module.update(fert=args['fert']).execute()
		
		if result > 0:
			rh.close()
			return '', 200

		rh.close()
		abort(400, 'Unable to update salts module.')

@bp.route('/fert/<int:id>', methods=['GET','PUT'])
def fert(id):
	if request.method == 'GET':
		project_db = request.headers.get(rh.PROJECT_DB)
		has_db,error = rh.init(project_db)
		if not has_db: abort(400, error)

		item = Fertilizer_frt.get_or_none(Fertilizer_frt.id == id)
		
		if item is None:
			rh.close()
			abort(404, 'Fertilizer not found.')

		if item.salts is None or len(item.salts) == 0:
			v = db.Salt_fertilizer_frt.create(name_id=id, so4=0, ca=0, mg=0, na=0, k=0, cl=0, co3=0, hco3=0)
		else:
			v = item.salts[0]

		d = model_to_dict(v, recurse=False)
		for k in d:
			if k == 'name':
				d['name_id'] = d[k]
				d.pop(k)
				break

		rh.close()
		return {
			'name': item.name,
			'item': d
		}
	elif request.method == 'PUT':
		return DefaultRestMethods.put(id, db.Salt_fertilizer_frt, 'Value')

@bp.route('/enable-road', methods=['GET','PUT','POST','DELETE'])
def enableRoad():
	project_db = request.headers.get(rh.PROJECT_DB)
	has_db,error = rh.init(project_db)
	if not has_db: abort(400, error)

	module, created = db.Salt_module.get_or_create(id=1)
	if module.road_timestep is None or module.road_timestep == '':
		module.road_timestep = 'aa'
		module.save()
	
	if request.method == 'GET':
		rh.close()
		return {
			'road': module.road,
			'road_timestep': module.road_timestep,
			'has_atmo': Atmo_cli_sta.select().count() > 0
		}
	elif request.method == 'PUT':
		args = request.json
		result = db.Salt_module.update(road=args['road'], road_timestep=args['road_timestep']).execute()
		
		if result > 0:
			rh.close()
			return '', 200

		rh.close()
		abort(400, 'Unable to update salts module.')
	elif request.method == 'DELETE':
		project_base.db.execute_sql("PRAGMA foreign_keys = ON")
		db.Salt_road.delete().execute()
		rh.close()
		return '', 200
	elif request.method == 'POST':
		args = request.json
		time_step = args['time_step']	
		sim = Time_sim.get_or_create_default()	

		mod_updated = db.Salt_module.update(road_timestep=args['time_step']).execute()
		
		items = []
		for sta in Atmo_cli_sta.select().order_by(Atmo_cli_sta.name):
			if time_step == 'aa':
				items.append({
					'sta_id': sta.id,
					'timestep': 0,
					'so4': 0,
					'ca': 0,
					'mg': 0,
					'na': 1,
					'k': 0,
					'cl': 1.55,
					'co3': 0,
					'hco3': 0
				})
			elif time_step == 'yr':
				for yr in range(sim.yrc_start, sim.yrc_end + 1):
					items.append({
						'sta_id': sta.id,
						'timestep': yr,
						'so4': 0,
						'ca': 0,
						'mg': 0,
						'na': 1,
						'k': 0,
						'cl': 1.55,
						'co3': 0,
						'hco3': 0
					})
			elif time_step == 'mo':
				start_date = datetime.datetime(sim.yrc_start, 1, 1) + datetime.timedelta(sim.day_start)
				start_month = start_date.month
				for yr in range(sim.yrc_start, sim.yrc_end + 1):
					write_month = start_month if yr == sim.yrc_start else 1
					for mo in range(write_month, 13):
						items.append({
							'sta_id': sta.id,
							'timestep': yr * 100 + mo,
							'so4': 0,
							'ca': 0,
							'mg': 0,
							'na': 1,
							'k': 0,
							'cl': 1.55,
							'co3': 0,
							'hco3': 0
						})
			
		db.Salt_road.delete().execute()
		db_lib.bulk_insert(project_base.db, db.Salt_road, items)

		rh.close()
		return '', 200

	abort(405, 'HTTP Method not allowed.')

@bp.route('/road/<int:id>', methods=['GET','POST'])
def roadValues(id):
	if request.method == 'GET':
		project_db = request.headers.get(rh.PROJECT_DB)
		has_db,error = rh.init(project_db)
		if not has_db: abort(400, error)

		sta = Atmo_cli_sta.get_or_none(Atmo_cli_sta.id == id)
		
		if sta is None:
			rh.close()
			abort(404, 'Atmospheric station not found.')

		values = [model_to_dict(v, recurse=False) for v in sta.salt_road_values.order_by(db.Salt_road.timestep)]
		for v in values:
			for k in v:
				if k == 'sta':
					v['sta_id'] = v[k]
					v.pop(k)
					break

		rh.close()
		return {
			'name': sta.name,
			'values': values
		}
	elif request.method == 'POST':
		return DefaultRestMethods.post(db.Salt_road, 'Value')

@bp.route('/road-values/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def roadValuesId(id):
	if request.method == 'GET':
		return DefaultRestMethods.get(id, db.Salt_road, 'Value')
	elif request.method == 'DELETE':
		return DefaultRestMethods.delete(id, db.Salt_road, 'Value')
	elif request.method == 'PUT':
		return DefaultRestMethods.put(id, db.Salt_road, 'Value')

	abort(405, 'HTTP Method not allowed.')

@bp.route('/enable-atmo', methods=['GET','PUT','POST','DELETE'])
def enableAtmo():
	project_db = request.headers.get(rh.PROJECT_DB)
	has_db,error = rh.init(project_db)
	if not has_db: abort(400, error)

	module, created = db.Salt_module.get_or_create(id=1)
	if module.atmo_timestep is None or module.atmo_timestep == '':
		module.atmo_timestep = 'aa'
		module.save()
	
	if request.method == 'GET':
		rh.close()
		return {
			'atmo': module.atmo,
			'atmo_timestep': module.atmo_timestep,
			'has_atmo': Atmo_cli_sta.select().count() > 0
		}
	elif request.method == 'PUT':
		args = request.json
		result = db.Salt_module.update(atmo=args['atmo'], atmo_timestep=args['atmo_timestep']).execute()
		
		if result > 0:
			rh.close()
			return '', 200

		rh.close()
		abort(400, 'Unable to update salts recall module.')
	elif request.method == 'DELETE':
		project_base.db.execute_sql("PRAGMA foreign_keys = ON")
		db.Salt_atmo_cli.delete().execute()
		rh.close()
		return '', 200
	elif request.method == 'POST':
		args = request.json
		time_step = args['time_step']	
		sim = Time_sim.get_or_create_default()	

		mod_updated = db.Salt_module.update(atmo_timestep=args['time_step']).execute()
		
		items = []
		for sta in Atmo_cli_sta.select().order_by(Atmo_cli_sta.name):
			if time_step == 'aa':
				items.append({
					'sta_id': sta.id,
					'timestep': 0,
					'so4_wet': 5,
					'ca_wet': 2,
					'mg_wet': 0.5,
					'na_wet': 0.75,
					'k_wet': 0.1,
					'cl_wet': 1,
					'co3_wet': 0,
					'hco3_wet': 3,
					'so4_dry': 0,
					'ca_dry': 0,
					'mg_dry': 0,
					'na_dry': 0,
					'k_dry': 0,
					'cl_dry': 0,
					'co3_dry': 0,
					'hco3_dry': 0
				})
			elif time_step == 'yr':
				for yr in range(sim.yrc_start, sim.yrc_end + 1):
					items.append({
						'sta_id': sta.id,
						'timestep': yr,
						'so4_wet': 5,
						'ca_wet': 2,
						'mg_wet': 0.5,
						'na_wet': 0.75,
						'k_wet': 0.1,
						'cl_wet': 1,
						'co3_wet': 0,
						'hco3_wet': 3,
						'so4_dry': 0,
						'ca_dry': 0,
						'mg_dry': 0,
						'na_dry': 0,
						'k_dry': 0,
						'cl_dry': 0,
						'co3_dry': 0,
						'hco3_dry': 0
					})
			elif time_step == 'mo':
				start_date = datetime.datetime(sim.yrc_start, 1, 1) + datetime.timedelta(sim.day_start)
				start_month = start_date.month
				for yr in range(sim.yrc_start, sim.yrc_end + 1):
					write_month = start_month if yr == sim.yrc_start else 1
					for mo in range(write_month, 13):
						items.append({
							'sta_id': sta.id,
							'timestep': yr * 100 + mo,
							'so4_wet': 5,
							'ca_wet': 2,
							'mg_wet': 0.5,
							'na_wet': 0.75,
							'k_wet': 0.1,
							'cl_wet': 1,
							'co3_wet': 0,
							'hco3_wet': 3,
							'so4_dry': 0,
							'ca_dry': 0,
							'mg_dry': 0,
							'na_dry': 0,
							'k_dry': 0,
							'cl_dry': 0,
							'co3_dry': 0,
							'hco3_dry': 0
						})
			
		db.Salt_atmo_cli.delete().execute()
		db_lib.bulk_insert(project_base.db, db.Salt_atmo_cli, items)

		rh.close()
		return '', 200

	abort(405, 'HTTP Method not allowed.')

@bp.route('/atmo/<int:id>', methods=['GET','POST'])
def atmoValues(id):
	if request.method == 'GET':
		project_db = request.headers.get(rh.PROJECT_DB)
		has_db,error = rh.init(project_db)
		if not has_db: abort(400, error)

		sta = Atmo_cli_sta.get_or_none(Atmo_cli_sta.id == id)
		if sta is None:
			rh.close()
			abort(404, 'Atmospheric station not found.')

		values = [model_to_dict(v, recurse=False) for v in sta.salt_values.order_by(db.Salt_atmo_cli.timestep)]
		for v in values:
			for k in v:
				if k == 'sta':
					v['sta_id'] = v[k]
					v.pop(k)
					break
		
		rh.close()
		return {
			'name': sta.name,
			'values': values
		}
	elif request.method == 'POST':
		return DefaultRestMethods.post(db.Salt_atmo_cli, 'Value')

@bp.route('/atmo-values/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def atmoValuesId(id):
	if request.method == 'GET':
		return DefaultRestMethods.get(id, db.Salt_atmo_cli, 'Value')
	elif request.method == 'DELETE':
		return DefaultRestMethods.delete(id, db.Salt_atmo_cli, 'Value')
	elif request.method == 'PUT':
		return DefaultRestMethods.put(id, db.Salt_atmo_cli, 'Value')

	abort(405, 'HTTP Method not allowed.')

@bp.route('/enable-recall', methods=['GET','PUT','POST'])
def enableRecall():
	project_db = request.headers.get(rh.PROJECT_DB)
	has_db,error = rh.init(project_db)
	if not has_db: abort(400, error)

	module, created = db.Salt_module.get_or_create(id=1)
	
	if request.method == 'GET':
		rh.close()
		return {
			'recall': module.recall
		}
	elif request.method == 'PUT':
		args = request.json
		result = db.Salt_module.update(recall=args['recall']).execute()
		
		if result > 0:
			rh.close()
			return '', 200

		rh.close()
		abort(400, 'Unable to update salts recall module.')
	elif request.method == 'POST':
		args = request.json
		time_step = args['time_step']
		if time_step < 1 or time_step > 3:
			rh.close()
			abort(400, 'Invalid time step value.')
		
		if db.Salt_recall_rec.select().count() == 0:
			items = []
			for rec in recall.Recall_rec.select():
				items.append({
					'name': rec.name,
					'rec_typ': time_step
				})

			db_lib.bulk_insert(project_base.db, db.Salt_recall_rec, items)

			for rec in db.Salt_recall_rec.select():
				update_recall_rec(rec, rec.id, Time_sim.get_or_create_default(), time_step, True)

		rh.close()
		return '', 200

	abort(405, 'HTTP Method not allowed.')

@bp.route('/recall', methods=['GET', 'POST', 'DELETE'])
def recallTable():
	if request.method == 'GET':
		table = db.Salt_recall_rec
		filter_cols = [table.name]
		return DefaultRestMethods.get_paged_list(table, filter_cols, True)
	elif request.method == 'POST':
		return DefaultRestMethods.post(db.Salt_recall_rec, 'Recall')
	elif request.method == 'DELETE':
		project_db = request.headers.get(rh.PROJECT_DB)
		has_db,error = rh.init(project_db)
		if not has_db: abort(400, error)
		project_base.db.execute_sql("PRAGMA foreign_keys = ON")
		db.Salt_recall_dat.delete().execute()
		db.Salt_recall_rec.delete().execute()
		rh.close()
		return '', 200
	
	abort(405, 'HTTP Method not allowed.')

@bp.route('/recall/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def recallId(id):
	if request.method == 'GET':
		return DefaultRestMethods.get(id, db.Salt_recall_rec, 'Salt recall', back_refs=False)
	elif request.method == 'DELETE':
		return DefaultRestMethods.delete(id, db.Salt_recall_rec, 'Salt recall')
	elif request.method == 'PUT':
		project_db = request.headers.get(rh.PROJECT_DB)
		has_db,error = rh.init(project_db)
		if not has_db: abort(400, error)

		table = db.Salt_recall_rec
		item_description = 'Salt recall'
		args = request.json
		try:
			sim = Time_sim.get_or_create_default()
			m = table.get(table.id==id)
			update_recall_rec(m, id, sim, args['rec_typ'])

			result = RestHelpers.save_args(table, args, id=id)

			rh.close()
			if result > 0:
				return '', 200

			abort(400, 'Unable to update salt recall {id}.'.format(id=id))
		except IntegrityError as e:
			rh.close()
			abort(400, 'Name must be unique.')
		except table.DoesNotExist:
			rh.close()
			abort(404, '{item} {id} does not exist'.format(item=item_description, id=id))
		except Exception as ex:
			rh.close()
			abort(400, 'Unexpected error {ex}'.format(ex=ex))

	abort(405, 'HTTP Method not allowed.')

@bp.route('/recall-data-list/<int:id>', methods=['GET'])
def dataList(id):
	project_db = request.headers.get(rh.PROJECT_DB)
	has_db,error = rh.init(project_db)
	if not has_db: abort(400, error)

	table = db.Salt_recall_dat
	args = request.args
	sort = RestHelpers.get_arg(args, 'sort', 'name')
	reverse = RestHelpers.get_arg(args, 'reverse', 'n')
	page = RestHelpers.get_arg(args, 'page', 1)
	per_page = RestHelpers.get_arg(args, 'per_page', 50)
	
	s = table.select().where(table.recall_rec_id == id)
	total = s.count()

	if sort == 'name':
		sort_val = table.name if reverse != 'y' else table.name.desc()
	else:
		sort_val = SQL('[{}]'.format(sort))
		if reverse == 'y':
			sort_val = SQL('[{}]'.format(sort)).desc()

	m = s.order_by(sort_val).paginate(int(page), int(per_page))

	rh.close()
	return {
		'total': total,
		'matches': total,
		'items': [model_to_dict(v, recurse=False) for v in m]
	}

@bp.route('/recall-data', methods=['POST'])
def data():
	return DefaultRestMethods.post(db.Salt_recall_dat, 'Recall')

@bp.route('/recall-data/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def dataItem(id):
	if request.method == 'GET':
		return DefaultRestMethods.get(id, db.Salt_recall_dat, 'Recall')
	elif request.method == 'DELETE':
		return DefaultRestMethods.delete(id, db.Salt_recall_dat, 'Recall')
	elif request.method == 'PUT':
		return DefaultRestMethods.put(id, db.Salt_recall_dat, 'Recall')

	abort(405, 'HTTP Method not allowed.')

def update_recall_rec(m, id, sim, new_rec_typ, no_compare = False):
	if (m.rec_typ != new_rec_typ) or no_compare:
		db.Salt_recall_dat.delete().where(db.Salt_recall_dat.recall_rec_id==id).execute()
		rec = db.Salt_recall_rec.get_or_none(db.Salt_recall_rec.id == id)
		name = '' if rec is None else rec.name

		ob_typs = {
			1: 'pt_day',
			2: 'pt_mon',
			3: 'pt_yr'
		}
		ob_typ = ob_typs.get(new_rec_typ, 'ptsrc')

		years = 0
		months = 1
		start_month = 1
		insert_daily = False

		if new_rec_typ != 4:
			years = sim.yrc_end - sim.yrc_start
			if new_rec_typ != 3:
				start_date = datetime.datetime(sim.yrc_start, 1, 1) + datetime.timedelta(sim.day_start)
				end_date = datetime.datetime(sim.yrc_end, 1, 1) + datetime.timedelta(sim.day_end)
				if sim.day_end == 0:
					end_date = datetime.datetime(sim.yrc_end, 12, 31)

				start_month = start_date.month
				months = end_date.month
				
				if new_rec_typ != 2:
					insert_daily = True

		rec_data = []
		if not insert_daily:
			for x in range(years + 1):
				for y in range(start_month, months + 1):
					t_step = x + 1 if months == 1 else y
					data = {
						'recall_rec_id': id,
						'jday': 1,
						'mo': t_step if new_rec_typ == 1 or new_rec_typ == 2 else 1,
						'day_mo': 1,
						'yr': x + sim.yrc_start if new_rec_typ != 4 else 1,
						'ob_typ': ob_typ,
						'ob_name': name,
						'so4': 0,
						'ca': 0,
						'mg': 0,
						'na': 0,
						'k': 0,
						'cl': 0,
						'co3': 0,
						'hco3': 0
					}
					rec_data.append(data)
		else:
			current_date = start_date
			while current_date <= end_date:
				curent_tt = current_date.timetuple()
				data = {
					'recall_rec_id': id,
					'jday': curent_tt.tm_yday,
					'mo': curent_tt.tm_mon,
					'day_mo': curent_tt.tm_mday,
					'yr': current_date.year,
					'ob_typ': ob_typ,
					'ob_name': name,
					'so4': 0,
					'ca': 0,
					'mg': 0,
					'na': 0,
					'k': 0,
					'cl': 0,
					'co3': 0,
					'hco3': 0
				}
				rec_data.append(data)
				current_date = current_date + datetime.timedelta(1) 

		db_lib.bulk_insert(project_base.db, db.Salt_recall_dat, rec_data)