from flask import Blueprint, request, abort
from .config import RequestHeaders as rh

from playhouse.shortcuts import model_to_dict
from peewee import *

from .defaults import DefaultRestMethods, RestHelpers
from database.project import base, lum, structural, init, hru_parm_db, decision_table
from database.datasets import lum as ds

from database import lib
from helpers import utils

bp = Blueprint('lum', __name__, url_prefix='/lum')

def save_landuse_args(m, args):
	m.name = args['name']
	m.description = None if 'description' not in args else args['description']
	m.cal_group = None if 'cal_group' not in args else utils.remove_space(args['cal_group'])
	m.urb_ro = None if 'urb_ro' not in args else args['urb_ro']

	if 'plnt_com_name' in args:
		m.plnt_com_id = RestHelpers.get_id_from_name(init.Plant_ini, args['plnt_com_name'])
	if 'mgt_name' in args:
		m.mgt_id = RestHelpers.get_id_from_name(lum.Management_sch, args['mgt_name'])
	if 'cn2_name' in args:
		m.cn2_id = RestHelpers.get_id_from_name(lum.Cntable_lum, args['cn2_name'])
	if 'cons_prac_name' in args:
		m.cons_prac_id = RestHelpers.get_id_from_name(lum.Cons_prac_lum, args['cons_prac_name'])
	if 'urban_name' in args:
		m.urban_id = RestHelpers.get_id_from_name(hru_parm_db.Urban_urb, args['urban_name'])
	if 'ov_mann_name' in args:
		m.ov_mann_id = RestHelpers.get_id_from_name(lum.Ovn_table_lum, args['ov_mann_name'])
	if 'tile_name' in args:
		m.tile_id = RestHelpers.get_id_from_name(structural.Tiledrain_str, args['tile_name'])
	if 'sep_name' in args:
		m.sep_id = RestHelpers.get_id_from_name(structural.Septic_str, args['sep_name'])
	if 'vfs_name' in args:
		m.vfs_id = RestHelpers.get_id_from_name(structural.Filterstrip_str, args['vfs_name'])
	if 'grww_name' in args:
		m.grww_id = RestHelpers.get_id_from_name(structural.Grassedww_str, args['grww_name'])
	if 'bmp_name' in args:
		m.bmp_id = RestHelpers.get_id_from_name(structural.Bmpuser_str, args['bmp_name'])

	return m.save()

# Landuse_lum

@bp.route('/landuse', methods=['GET', 'POST'])
def landuse():
	if request.method == 'GET':
		table = lum.Landuse_lum
		filter_cols = [table.name]
		return DefaultRestMethods.get_paged_list(table, filter_cols, True)
	elif request.method == 'POST':
		project_db = request.headers.get(rh.PROJECT_DB)
		has_db,error = rh.init(project_db)
		if not has_db: abort(400, error)

		args = request.json
		try:
			m = lum.Landuse_lum()
			result = save_landuse_args(m, args)

			rh.close()
			if result > 0:
				return {'id': m.id }, 200

			abort(400, 'Unable to create record.')
		except IntegrityError as e:
			rh.close()
			abort(400, 'Name must be unique.')
		except init.Plant_ini.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['plnt_com_name']))
		except lum.Management_sch.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['mgt_name']))
		except lum.Cntable_lum.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['cn2_name']))
		except lum.Cons_prac_lum.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['cons_prac_name']))
		except hru_parm_db.Urban_urb.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['urban_name']))
		except lum.Ovn_table_lum.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['ov_mann_name']))
		except structural.Tiledrain_str.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['tile_name']))
		except structural.Septic_str.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['sep_name']))
		except structural.Filterstrip_str.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['vfs_name']))
		except structural.Grassedww_str.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['grww_name']))
		except structural.Bmpuser_str.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['bmp_name']))
		except Exception as ex:
			rh.close()
			abort(400, 'Unexpected error {ex}'.format(ex=ex))
	
	abort(405, 'HTTP Method not allowed.')

@bp.route('/landuse/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def landuseId(id):
	if request.method == 'GET':
		return DefaultRestMethods.get(id, lum.Landuse_lum, 'Landuse', True)
	elif request.method == 'DELETE':
		return DefaultRestMethods.delete(id, lum.Landuse_lum, 'Landuse')
	elif request.method == 'PUT':
		project_db = request.headers.get(rh.PROJECT_DB)
		has_db,error = rh.init(project_db)
		if not has_db: abort(400, error)

		args = request.json
		try:
			m = lum.Landuse_lum.get(lum.Landuse_lum.id == id)
			result = save_landuse_args(m, args)

			rh.close()
			if result > 0:
				return '', 200

			abort(400, 'Unable to update properties {id}.'.format(id=id))
		except IntegrityError as e:
			rh.close()
			abort(400, 'Name must be unique.')
		except lum.Landuse_lum.DoesNotExist:
			rh.close()
			abort(404, 'Land use properties {id} does not exist'.format(id=id))
		except init.Plant_ini.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['plnt_com_name']))
		except lum.Management_sch.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['mgt_name']))
		except lum.Cntable_lum.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['cn2_name']))
		except lum.Cons_prac_lum.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['cons_prac_name']))
		except hru_parm_db.Urban_urb.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['urban_name']))
		except lum.Ovn_table_lum.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['ov_mann_name']))
		except structural.Tiledrain_str.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['tile_name']))
		except structural.Septic_str.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['sep_name']))
		except structural.Filterstrip_str.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['vfs_name']))
		except structural.Grassedww_str.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['grww_name']))
		except structural.Bmpuser_str.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['bmp_name']))
		except Exception as ex:
			rh.close()
			abort(400, 'Unexpected error {ex}'.format(ex=ex))

	abort(405, 'HTTP Method not allowed.')

@bp.route('/landuse/many', methods=['GET', 'PUT'])
def landuseMany():
	if request.method == 'GET':
		return DefaultRestMethods.get_name_id_list(lum.Landuse_lum)
	elif request.method == 'PUT':
		project_db = request.headers.get(rh.PROJECT_DB)
		has_db,error = rh.init(project_db)
		if not has_db: abort(400, error)

		args = request.json
		try:
			param_dict = {}

			if 'plnt_com_name' in args:
				param_dict['plnt_com_id'] = RestHelpers.get_id_from_name(init.Plant_ini, args['plnt_com_name'])
			if 'mgt_name' in args:
				param_dict['mgt_id'] = RestHelpers.get_id_from_name(lum.Management_sch, args['mgt_name'])
			if 'cn2_name' in args:
				param_dict['cn2_id'] = RestHelpers.get_id_from_name(lum.Cntable_lum, args['cn2_name'])
			if 'cons_prac_name' in args:
				param_dict['cons_prac_id'] = RestHelpers.get_id_from_name(lum.Cons_prac_lum, args['cons_prac_name'])
			if 'urban_name' in args:
				param_dict['urban_id'] = RestHelpers.get_id_from_name(hru_parm_db.Urban_urb, args['urban_name'])
			if 'ov_mann_name' in args:
				param_dict['ov_mann_id'] = RestHelpers.get_id_from_name(lum.Ovn_table_lum, args['ov_mann_name'])
			if 'tile_name' in args:
				param_dict['tile_id'] = RestHelpers.get_id_from_name(structural.Tiledrain_str, args['tile_name'])
			if 'sep_name' in args:
				param_dict['sep_id'] = RestHelpers.get_id_from_name(structural.Septic_str, args['sep_name'])
			if 'vfs_name' in args:
				param_dict['vfs_id'] = RestHelpers.get_id_from_name(structural.Filterstrip_str, args['vfs_name'])
			if 'grww_name' in args:
				param_dict['grww_id'] = RestHelpers.get_id_from_name(structural.Grassedww_str, args['grww_name'])
			if 'bmp_name' in args:
				param_dict['bmp_id'] = RestHelpers.get_id_from_name(structural.Bmpuser_str, args['bmp_name'])

			query = lum.Landuse_lum.update(param_dict).where(lum.Landuse_lum.id.in_(args['selected_ids']))
			result = query.execute()

			rh.close()
			if result > 0:
				return '', 200

			abort(400, 'Unable to update properties.')
		except init.Plant_ini.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['plnt_com_name']))
		except lum.Management_sch.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['mgt_name']))
		except lum.Cntable_lum.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['cn2_name']))
		except lum.Cons_prac_lum.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['cons_prac_name']))
		except hru_parm_db.Urban_urb.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['urban_name']))
		except lum.Ovn_table_lum.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['ov_mann_name']))
		except structural.Tiledrain_str.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['tile_name']))
		except structural.Septic_str.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['sep_name']))
		except structural.Filterstrip_str.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['vfs_name']))
		except structural.Grassedww_str.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['grww_name']))
		except structural.Bmpuser_str.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['bmp_name']))
		except Exception as ex:
			rh.close()
			abort(400, 'Unexpected error {ex}'.format(ex=ex))
	
	abort(405, 'HTTP Method not allowed.')

# Cntable_lum
cntable_remove_spaces = ['description', 'treat', 'cond_cov']

@bp.route('/cntable', methods=['GET', 'POST'])
def cntable():
	if request.method == 'GET':
		table = lum.Cntable_lum
		filter_cols = [table.name, table.description, table.treat, table.cond_cov]
		return DefaultRestMethods.get_paged_list(table, filter_cols)
	elif request.method == 'POST':
		return DefaultRestMethods.post(lum.Cntable_lum, 'Curve number', remove_spaces = cntable_remove_spaces)
	abort(405, 'HTTP Method not allowed.')

@bp.route('/cntable/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def cntableId(id):
	if request.method == 'GET':
		return DefaultRestMethods.get(id, lum.Cntable_lum, 'Curve number')
	elif request.method == 'DELETE':
		return DefaultRestMethods.delete(id, lum.Cntable_lum, 'Curve number')
	elif request.method == 'PUT':
		return DefaultRestMethods.put(id, lum.Cntable_lum, 'Curve number', remove_spaces = cntable_remove_spaces)

	abort(405, 'HTTP Method not allowed.')

@bp.route('/cntable/many', methods=['GET', 'PUT'])
def cntableMany():
	if request.method == 'GET':
		return DefaultRestMethods.get_name_id_list(lum.Cntable_lum)
	elif request.method == 'PUT':
		return DefaultRestMethods.put_many(lum.Cntable_lum, 'Curve number', remove_spaces = cntable_remove_spaces)
	
	abort(405, 'HTTP Method not allowed.')

@bp.route('/cntable/datasets/<name>', methods=['GET'])
def cntableDatasets(name):
	if request.method == 'GET':
		return DefaultRestMethods.get_datasets_name(name, ds.Cntable_lum, 'Curve number')

	abort(405, 'HTTP Method not allowed.')

# Ovn_table_lum

@bp.route('/ovntable', methods=['GET', 'POST'])
def ovntable():
	if request.method == 'GET':
		table = lum.Ovn_table_lum
		filter_cols = [table.name, table.description]
		return DefaultRestMethods.get_paged_list(table, filter_cols)
	elif request.method == 'POST':
		return DefaultRestMethods.post(lum.Ovn_table_lum, 'Mannings n')
	abort(405, 'HTTP Method not allowed.')

@bp.route('/ovntable/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def ovntableId(id):
	if request.method == 'GET':
		return DefaultRestMethods.get(id, lum.Ovn_table_lum, 'Mannings n')
	elif request.method == 'DELETE':
		return DefaultRestMethods.delete(id, lum.Ovn_table_lum, 'Mannings n')
	elif request.method == 'PUT':
		return DefaultRestMethods.put(id, lum.Ovn_table_lum, 'Mannings n')

	abort(405, 'HTTP Method not allowed.')

@bp.route('/ovntable/many', methods=['GET', 'PUT'])
def ovntableMany():
	if request.method == 'GET':
		return DefaultRestMethods.get_name_id_list(lum.Ovn_table_lum)
	elif request.method == 'PUT':
		return DefaultRestMethods.put_many(lum.Ovn_table_lum, 'Mannings n')
	
	abort(405, 'HTTP Method not allowed.')

@bp.route('/ovntable/datasets/<name>', methods=['GET'])
def ovntableDatasets(name):
	if request.method == 'GET':
		return DefaultRestMethods.get_datasets_name(name, ds.Ovn_table_lum, 'Mannings n')

	abort(405, 'HTTP Method not allowed.')

# Cons_prac_lum

@bp.route('/cons_prac', methods=['GET', 'POST'])
def cons_prac():
	if request.method == 'GET':
		table = lum.Cons_prac_lum
		filter_cols = [table.name, table.description]
		return DefaultRestMethods.get_paged_list(table, filter_cols)
	elif request.method == 'POST':
		return DefaultRestMethods.post(lum.Cons_prac_lum, 'Conservation practice')
	abort(405, 'HTTP Method not allowed.')

@bp.route('/cons_prac/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def cons_pracId(id):
	if request.method == 'GET':
		return DefaultRestMethods.get(id, lum.Cons_prac_lum, 'Conservation practice')
	elif request.method == 'DELETE':
		return DefaultRestMethods.delete(id, lum.Cons_prac_lum, 'Conservation practice')
	elif request.method == 'PUT':
		return DefaultRestMethods.put(id, lum.Cons_prac_lum, 'Conservation practice')

	abort(405, 'HTTP Method not allowed.')

@bp.route('/cons_prac/many', methods=['GET', 'PUT'])
def cons_pracMany():
	if request.method == 'GET':
		return DefaultRestMethods.get_name_id_list(lum.Cons_prac_lum)
	elif request.method == 'PUT':
		return DefaultRestMethods.put_many(lum.Cons_prac_lum, 'Conservation practice')
	
	abort(405, 'HTTP Method not allowed.')

@bp.route('/cons_prac/datasets/<name>', methods=['GET'])
def cons_pracDatasets(name):
	if request.method == 'GET':
		return DefaultRestMethods.get_datasets_name(name, ds.Cons_prac_lum, 'Conservation practice')

	abort(405, 'HTTP Method not allowed.')

# Management_sch

@bp.route('/mgt_sch', methods=['GET', 'POST'])
def mgt_sch():
	if request.method == 'GET':
		table = lum.Management_sch
		filter_cols = [table.name]
		
		items = DefaultRestMethods.get_paged_items(table, filter_cols)
		m = items['model']
		ml = [{'id': v.id, 'name': v.name, 'num_ops': len(v.operations), 'num_auto': len(v.auto_ops)} for v in m]

		return {
			'total': items['total'],
			'matches': items['matches'],
			'items': ml
		}
	elif request.method == 'POST':
		project_db = request.headers.get(rh.PROJECT_DB)
		has_db,error = rh.init(project_db)
		if not has_db: abort(400, error)

		args = request.json
		try:
			m = lum.Management_sch()
			m.name = args['name']
			m.save()

			new_auto = []
			for a in args['auto_ops']:
				try:
					dt = decision_table.D_table_dtl.get((decision_table.D_table_dtl.file_name == 'lum.dtl') & (decision_table.D_table_dtl.name == a['name']))
					new_auto.append({'management_sch_id': m.id, 'd_table_id': dt.id, 'plant1': a['plant1'], 'plant2': a['plant2']})
				except decision_table.D_table_dtl.DoesNotExist:
					abort(404, message='Decision table {name} does not exist'.format(name=a['name']))

			new_ops = []
			order = 1
			for o in args['operations']:
				new_ops.append({
					'management_sch_id': m.id,
					'op_typ': o['op_typ'],
					'mon': o['mon'],
					'day': o['day'],
					'op_data1': o['op_data1'],
					'op_data2': o['op_data2'],
					'op_data3': o['op_data3'],
					'order': o['order'],
					'hu_sch': o['hu_sch']
				})
				order += 1

			lib.bulk_insert(base.db, lum.Management_sch_auto, new_auto)
			lib.bulk_insert(base.db, lum.Management_sch_op, new_ops)

			rh.close()
			return {'id': m.id }, 201
		except IntegrityError as e:
			rh.close()
			abort(400, 'Name must be unique.')
		except Exception as ex:
			rh.close()
			abort(400, 'Unexpected error {ex}'.format(ex=ex))

	abort(405, 'HTTP Method not allowed.')

@bp.route('/mgt_sch/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def mgt_schId(id):
	if request.method == 'GET':
		return DefaultRestMethods.get(id, lum.Management_sch, 'Management schedule', back_refs=True, max_depth=2)
	elif request.method == 'DELETE':
		return DefaultRestMethods.delete(id, lum.Management_sch, 'Management schedule')
	elif request.method == 'PUT':
		project_db = request.headers.get(rh.PROJECT_DB)
		has_db,error = rh.init(project_db)
		if not has_db: abort(400, error)

		args = request.json
		try:
			m = lum.Management_sch.get(lum.Management_sch.id == id)
			m.name = args['name']
			m.save()

			new_auto = []
			for a in args['auto_ops']:
				try:
					dt = decision_table.D_table_dtl.get((decision_table.D_table_dtl.file_name == 'lum.dtl') & (decision_table.D_table_dtl.name == a['name']))
					new_auto.append({'management_sch_id': m.id, 'd_table_id': dt.id, 'plant1': a['plant1'], 'plant2': a['plant2']})
				except decision_table.D_table_dtl.DoesNotExist:
					abort(404, message='Decision table {name} does not exist'.format(name=a['name']))

			new_ops = []
			order = 1
			for o in args['operations']:
				new_ops.append({
					'management_sch_id': m.id,
					'op_typ': o['op_typ'],
					'mon': o['mon'],
					'day': o['day'],
					'op_data1': o['op_data1'],
					'op_data2': o['op_data2'],
					'op_data3': o['op_data3'],
					'order': o['order'],
					'hu_sch': o['hu_sch']
				})
				order += 1

			lum.Management_sch_auto.delete().where(lum.Management_sch_auto.management_sch_id == m.id).execute()
			lib.bulk_insert(base.db, lum.Management_sch_auto, new_auto)

			lum.Management_sch_op.delete().where(lum.Management_sch_op.management_sch_id == m.id).execute()
			lib.bulk_insert(base.db, lum.Management_sch_op, new_ops)

			rh.close()
			return '', 200
		except IntegrityError as e:
			rh.close()
			abort(400, 'Name must be unique.')
		except lum.Management_sch.DoesNotExist:
			rh.close()
			abort(404, 'Management schedule {id} does not exist'.format(id=id))
		except Exception as ex:
			rh.close()
			abort(400, 'Unexpected error {ex}'.format(ex=ex))

	abort(405, 'HTTP Method not allowed.')