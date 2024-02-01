from flask import Blueprint, request, abort
from .config import RequestHeaders as rh

from playhouse.shortcuts import model_to_dict
from peewee import *

from .defaults import DefaultRestMethods, RestHelpers
from database.project import change as db, connect, gis
from database.project import base as project_base
from database import lib as db_lib
from helpers import table_mapper

bp = Blueprint('change', __name__, url_prefix='/change')

# Cal_parms_cal

@bp.route('/cal_parms', methods=['GET'])
def cal_parms():
	if request.method == 'GET':
		table = db.Cal_parms_cal
		filter_cols = [table.name, table.obj_typ, table.units]
		return DefaultRestMethods.get_paged_list(table, filter_cols)
	abort(405, 'HTTP Method not allowed.')

@bp.route('/cal_parms/<int:id>', methods=['GET', 'PUT'])
def cal_parmsId(id):
	if request.method == 'GET':
		return DefaultRestMethods.get(id, db.Cal_parms_cal, 'Calibration parameter')
	elif request.method == 'PUT':
		return DefaultRestMethods.put(id, db.Cal_parms_cal, 'Calibration parameter')

	abort(405, 'HTTP Method not allowed.')

@bp.route('/cal_parms/types', methods=['GET'])
def cal_parmsTypes():
	if request.method == 'GET':
		project_db = request.headers.get(rh.PROJECT_DB)
		has_db,error = rh.init(project_db)
		if not has_db: abort(400, error)

		table = db.Cal_parms_cal
		sol_types = table.select(table.name).where(table.obj_typ == 'sol').order_by(table.name)
		cli_types = table.select(table.name).where(table.obj_typ == 'cli').order_by(table.name)

		rh.close()
		return {
			'sol': [v.name for v in sol_types],
			'cli': [v.name for v in cli_types]
		}
	abort(405, 'HTTP Method not allowed.')

# Calibration_cal

@bp.route('/calibration', methods=['GET', 'POST'])
def calibration():
	if request.method == 'GET':
		table = db.Calibration_cal
		filter_cols = [table.chg_typ]
		items = DefaultRestMethods.get_paged_items(table, filter_cols)
		m = items['model']
		ml = []
		for v in m:
			d = model_to_dict(v, recurse=True)
			d['conditions'] = len(v.conditions)
			d['obj_tot'] = len(v.elements)
			ml.append(d)

		return {
			'total': items['total'],
			'matches': items['matches'],
			'items': ml
		}
	elif request.method == 'POST':
		return DefaultRestMethods.post(db.Calibration_cal, 'Calibration')
	abort(405, 'HTTP Method not allowed.')

@bp.route('/calibration/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def calibrationId(id):
	if request.method == 'GET':
		project_db = request.headers.get(rh.PROJECT_DB)
		has_db,error = rh.init(project_db)
		if not has_db: abort(400, error)

		table = db.Calibration_cal
		description = 'Calibration'
		try:
			m = table.get(table.id == id)
			item = model_to_dict(m, recurse=True, backrefs=True, max_depth=1)

			initial_selection = {
				'subbasins': [],
				'landuse': [],
				'soils': [],
				'objects': [v.obj_id for v in m.elements]
			}

			parm_type = m.cal_parm.obj_typ

			if parm_type in ['hru', 'sol', 'hlt']:
				if parm_type in ['hru', 'sol']:
					gis_hru_ids = connect.Hru_con.select(connect.Hru_con.gis_id).where(connect.Hru_con.id.in_(initial_selection['objects']))
				if parm_type == 'hlt':
					gis_hru_ids = connect.Hru_lte_con.select(connect.Hru_lte_con.gis_id).where(connect.Hru_lte_con.id.in_(initial_selection['objects']))
				gis_hrus = gis.Gis_hrus.select().where(gis.Gis_hrus.id.in_(gis_hru_ids))
				initial_selection['soils'] = list(dict.fromkeys([v.soil for v in gis_hrus]))
				initial_selection['landuse'] = list(dict.fromkeys([v.landuse for v in gis_hrus]))

				gis_lsus_ids = list(dict.fromkeys([v.lsu for v in gis_hrus]))
				gis_lsus = gis.Gis_lsus.select().where(gis.Gis_lsus.id.in_(gis_lsus_ids))

				gis_channel_ids = list(dict.fromkeys([v.channel for v in gis_lsus]))
				gis_channels = gis.Gis_channels.select().where(gis.Gis_channels.id.in_(gis_channel_ids))
				initial_selection['subbasins'] = list(dict.fromkeys([v.subbasin for v in gis_channels]))
			else:
				obj_to_gis = {
					'swq': gis.Gis_channels,
					'rte': gis.Gis_channels,
					'gw': gis.Gis_aquifers,
					'res': gis.Gis_water
				}
				gis_table = obj_to_gis.get(parm_type, None)
				if gis_table is not None:
					gis_items = gis_table.select().where(gis_table.id.in_(initial_selection['objects']))
					initial_selection['subbasins'] = list(dict.fromkeys([v.subbasin for v in gis_items]))

			"""obj_options = []
			parm_type = m.cal_parm.obj_typ
			obj_typ = table_mapper.cal_to_obj.get(parm_type, None)
			if obj_typ is not None:
				obj_table = table_mapper.obj_typs.get(obj_typ, None)
				if obj_table is not None:
					t = obj_table.select(obj_table.id, obj_table.name).order_by(obj_table.name)
					obj_options = [{'value': v.id, 'text': v.name} for v in t]"""

			rh.close()
			return {'item': item, 'initialSelection': initial_selection } #{'item': item, 'obj_options': obj_options}
		except table.DoesNotExist:
			rh.close()
			abort(404, '{description} {id} does not exist'.format(description=description, id=id))
	elif request.method == 'DELETE':
		return DefaultRestMethods.delete(id, db.Calibration_cal, 'Calibration')
	elif request.method == 'PUT':
		project_db = request.headers.get(rh.PROJECT_DB)
		has_db,error = rh.init(project_db)
		if not has_db: abort(400, error)

		table = db.Calibration_cal
		description = 'Calibration'
		args = request.json

		try:
			result = RestHelpers.save_args(table, args, id=id)

			if 'elements' in args:
				cal_parm = db.Cal_parms_cal.get(db.Cal_parms_cal.id == args['cal_parm_id'])
				obj_typ = table_mapper.cal_to_obj.get(cal_parm.obj_typ, None)
				if obj_typ is not None:
					obj_table = table_mapper.obj_typs.get(obj_typ, None)
					if obj_table is not None:
						elements = []
						for e in args['elements']:
							elements.append({
								'calibration_cal_id': id,
								'obj_typ': obj_typ,
								'obj_id': int(e)
							})
						
						db.Calibration_cal_elem.delete().where(db.Calibration_cal_elem.calibration_cal_id == id).execute()
						db_lib.bulk_insert(project_base.db, db.Calibration_cal_elem, elements)

			if 'conditions' in args:
				conditions = []
				for c in args['conditions']:
					conditions.append({
						'calibration_cal_id': id,
						'cond_typ': c['cond_typ'],
						'cond_op': c['cond_op'],
						'cond_val': c['cond_val'],
						'cond_val_text': c['cond_val_text']
					})
				
				db.Calibration_cal_cond.delete().where(db.Calibration_cal_cond.calibration_cal_id == id).execute()
				db_lib.bulk_insert(project_base.db, db.Calibration_cal_cond, conditions)

			rh.close()
			return '', 200
		except IntegrityError as e:
			rh.close()
			abort(400, '{item} save error. '.format(item=description) + str(e))
		except table.DoesNotExist:
			rh.close()
			abort(404, '{item} {id} does not exist'.format(item=description, id=id))
		except db.Cal_parms_cal.DoesNotExist:
			rh.close()
			abort(404, '{item} {id} does not exist'.format(item='Calibration parameter', id=args['cal_parm_id']))
		except Exception as ex:
			rh.close()
			abort(400, message="Unexpected error {ex}".format(ex=ex))

	abort(405, 'HTTP Method not allowed.')

@bp.route('/water_balance', methods=['GET', 'PUT'])
def water_balance():
	project_db = request.headers.get(rh.PROJECT_DB)
	has_db,error = rh.init(project_db)
	if not has_db: abort(400, error)
	
	if request.method == 'GET':
		codes = db.Codes_sft.get_or_none()
		if codes is None:
			codes = db.Codes_sft.create()

		# Reset tables
		if db.Wb_parms_sft.select().count() != 10:
			db.Wb_parms_sft.delete().execute()
			db.Wb_parms_sft.create_defaults()
		if db.Water_balance_sft.select().count() != 1 or db.Water_balance_sft_item.select().count() != 1:
			db.Water_balance_sft_item.delete().execute()
			db.Water_balance_sft.delete().execute()
			wb = db.Water_balance_sft.create(name='basin')
			db.Water_balance_sft_item.create(water_balance_sft=wb, name='basin')

		enabled = codes.hyd
		params = [model_to_dict(v, recurse=False) for v in db.Wb_parms_sft.select()]
		balance = model_to_dict(db.Water_balance_sft_item.get(), recurse=False)

		rh.close()
		return {
			'enabled': enabled,
			'params': params,
			'balance': balance
		}
	elif request.method == 'PUT':
		args = request.json
		codes = db.Codes_sft.get_or_none()
		if codes is None:
			codes = db.Codes_sft.create()

		balance = db.Water_balance_sft_item.get_or_none()
		if balance is None:
			db.Water_balance_sft.delete().execute()
			wb = db.Water_balance_sft.create(name='basin')
			balance = db.Water_balance_sft_item.create(water_balance_sft=wb, name='basin')

		if 'enabled' not in args or 'balance' not in args:
			rh.close()
			abort(400, 'Invalid request.')

		if args['enabled'] == 'n':				
			codes.hyd = 'n'
			codes.save()
		elif args['enabled'] == 'a':
			codes.hyd = 'a'
			codes.save()
			balance.surq_rto = args['balance']['surq_rto'];
			balance.latq_rto = args['balance']['latq_rto'];
			balance.perc_rto = args['balance']['perc_rto'];
			balance.et_rto = args['balance']['et_rto'];
			balance.tileq_rto = args['balance']['tileq_rto'];
			balance.pet = args['balance']['pet'];
			balance.sed = 0;
			balance.wyr = 0;
			balance.bfr = 0;
			balance.solp = 0;
			balance.save()
		elif args['enabled'] == 'b':
			codes.hyd = 'b'
			codes.save()
			balance.surq_rto = 0;
			balance.latq_rto = 0;
			balance.perc_rto = 0;
			balance.et_rto = 0;
			balance.tileq_rto = 0;
			balance.pet = 0;
			balance.sed = 0;
			balance.wyr = args['balance']['wyr'];
			balance.bfr = args['balance']['bfr'];
			balance.solp = 0;
			balance.save()
		
		rh.close()
		return '', 200
			
	abort(405, 'HTTP Method not allowed.')

@bp.route('/water_balance/parms/<int:id>', methods=['PUT'])
def waterBalanceParmsId(id):
	if request.method == 'PUT':
		return DefaultRestMethods.put(id, db.Wb_parms_sft, 'Water balance parameter')

	abort(405, 'HTTP Method not allowed.')

@bp.route('/plant_growth', methods=['GET', 'PUT'])
def plant_growth():
	project_db = request.headers.get(rh.PROJECT_DB)
	has_db,error = rh.init(project_db)
	if not has_db: abort(400, error)
	
	if request.method == 'GET':
		codes = db.Codes_sft.get_or_none()
		if codes is None:
			codes = db.Codes_sft.create()

		# Reset tables
		if db.Plant_parms_sft.select().count() != 1 or db.Plant_gro_sft.select().count() != 1:
			db.Plant_parms_sft_item.delete().execute()
			db.Plant_parms_sft.delete().execute()
			db.Plant_parms_sft.create(name='basin')
			db.Plant_gro_sft_item.delete().execute()
			db.Plant_gro_sft.delete().execute()
			db.Plant_gro_sft.create(name='basin')

		enabled = codes.plnt
		plants = db.Plant_gro_sft_item.select()
		req_pvars = ['pest_stress', 'epco', 'lai_pot', 'harv_idx']

		param_parent = db.Plant_parms_sft.get()

		plant_data = []
		for p in plants:
			params = db.Plant_parms_sft_item.select().where(db.Plant_parms_sft_item.name == p.name)
			pvars = [v.var for v in params]
			if set(pvars) != set(req_pvars):
				params.delete().execute()
				db.Plant_parms_sft_item.create(plant_parms_sft=param_parent, name=p.name, var='pest_stress', init=0, chg_typ='abschg', neg=0, pos=0, lo=0, up=0)
				db.Plant_parms_sft_item.create(plant_parms_sft=param_parent, name=p.name, var='epco', init=0, chg_typ='abschg', neg=0, pos=0, lo=0, up=0)
				db.Plant_parms_sft_item.create(plant_parms_sft=param_parent, name=p.name, var='lai_pot', init=0, chg_typ='abschg', neg=0, pos=0, lo=0, up=0)
				db.Plant_parms_sft_item.create(plant_parms_sft=param_parent, name=p.name, var='harv_idx', init=0, chg_typ='abschg', neg=0, pos=0, lo=0, up=0)
				params = db.Plant_parms_sft_item.select().where(db.Plant_parms_sft_item.name == p.name)
			
			param_data = [{ 'var': v.var, 'init': v.init, 'chg_typ': v.chg_typ, 'neg': v.neg, 'pos': v.pos, 'lo': v.lo, 'up': v.up } for v in params]
			plant_data.append({ 'name': p.name, 'yld': p.yld, 'params': param_data })

		rh.close()
		return {
			'enabled': enabled,
			'plants': plant_data
		}
	elif request.method == 'PUT':
		args = request.json
		codes = db.Codes_sft.get_or_none()
		if codes is None:
			codes = db.Codes_sft.create()

		codes.plnt = args['enabled']
		codes.save()

		db.Plant_gro_sft_item.delete().execute()
		db.Plant_parms_sft_item.delete().execute()

		gro_parent = db.Plant_gro_sft.get()
		param_parent = db.Plant_parms_sft.get()

		for p in args['plants']:
			db.Plant_gro_sft_item.create(plant_gro_sft=gro_parent, name=p['name'], yld=p['yld'])
			for param in p['params']:
				db.Plant_parms_sft_item.create(plant_parms_sft=param_parent, name=p['name'], var=param['var'], init=param['init'], chg_typ=param['chg_typ'], neg=param['neg'], pos=param['pos'], lo=param['lo'], up=param['up'])	
		
		rh.close()
		return '', 200
			
	abort(405, 'HTTP Method not allowed.')
