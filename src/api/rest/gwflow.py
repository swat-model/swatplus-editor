from flask import Blueprint, request, abort, Response
from playhouse.shortcuts import model_to_dict

from .defaults import DefaultRestMethods, RestHelpers
from .config import RequestHeaders as rh
from database.project import gwflow, config, connect, setup, reservoir
from database import lib
from fileio.connect import IndexHelper
import sys

bp = Blueprint('gwflow', __name__, url_prefix='/gwflow')

@bp.route('/enabled', methods=['GET'])
def enabled():
	project_db = request.headers.get(rh.PROJECT_DB)
	has_db,error = rh.init(project_db)
	if not has_db: abort(400, error)

	pc = config.Project_config.get()

	can_enable = False
	conn = lib.open_db(project_db)
	if lib.exists_table(conn, 'gwflow_base'):
		can_enable = True
	rh.close()
	return {
		'use_gwflow': pc.use_gwflow == 1,
		'can_enable': can_enable
	}		

@bp.route('/base', methods=['GET', 'PUT'])
def base():
	project_db = request.headers.get(rh.PROJECT_DB)
	has_db,error = rh.init(project_db)
	if not has_db: abort(400, error)

	table = gwflow.Gwflow_base
	item_description = 'Groundwater flow initialization'
	m = table.get_or_none()
	pc = config.Project_config.get()

	if request.method == 'GET':
		if m is None:
			rh.close()
			abort(400, '{} does not exist'.format(item_description))

		d = model_to_dict(m, recurse=False)

		rh.close()
		return {
			'use_gwflow': pc.use_gwflow == 1,
			'base': d,
		}
	elif request.method == 'PUT':
		try:
			result = RestHelpers.save_args(table, request.json['base'], id=0)

			pc.use_gwflow = request.json['use_gwflow']
			pc.save()

			rh.close()
			if result > 0:
				return '', 200

			abort(400, 'Unable to update {item}.'.format(item=item_description.lower()))
		except table.DoesNotExist:
			rh.close()
			abort(404, '{item} does not exist'.format(item=item_description))
		except Exception as ex:
			rh.close()
			abort(400, 'Unexpected error {ex}'.format(ex=ex))

	abort(405, 'HTTP Method not allowed.')

# Gwflow_zone

@bp.route('/zones', methods=['GET'])
def zones():
	if request.method == 'GET':
		table = gwflow.Gwflow_zone
		filter_cols = [table.zone_id]
		return DefaultRestMethods.get_paged_list(table, filter_cols)
	abort(405, 'HTTP Method not allowed.')

@bp.route('/zones/<int:id>', methods=['GET', 'PUT'])
def zonesId(id):
	project_db = request.headers.get(rh.PROJECT_DB)
	has_db,error = rh.init(project_db)
	if not has_db: abort(400, error)
	table = gwflow.Gwflow_zone

	if request.method == 'GET':
		m = table.get_or_none(table.zone_id == id)
		if m is None:
			rh.close()
			abort(400, '{} {} does not exist'.format('Zone', id))
		rh.close()
		return model_to_dict(m, recurse=False)
	elif request.method == 'PUT':
		return DefaultRestMethods.put(id, gwflow.Gwflow_zone, 'Zone', primary_key='zone_id')

	abort(405, 'HTTP Method not allowed.')


# Gwflow_fpcell

@bp.route('/fpcell', methods=['GET', 'POST', 'DELETE'])
def fpcell():
	table = gwflow.Gwflow_fpcell
	description = 'Floodplain cell'
	filter_cols = [table.cell_id]

	if request.method == 'GET':
		return get_cell_paged(table, filter_cols)
	elif request.method == 'POST':
		return post_cell(table, description)
	elif request.method == 'DELETE':
		return delete_all_cells(table, description)
	abort(405, 'HTTP Method not allowed.')

@bp.route('/fpcell/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def fpcellId(id):
	table = gwflow.Gwflow_fpcell
	description = 'Floodplain cell'

	if request.method == 'GET':
		return get_cell(table, id, description)
	elif request.method == 'DELETE':
		return delete_cell(table, id, description)
	elif request.method == 'PUT':
		return put_cell(id, table, description)

	abort(405, 'HTTP Method not allowed.')

# Gwflow_rescell

@bp.route('/rescell', methods=['GET', 'POST', 'DELETE'])
def rescell():
	table = gwflow.Gwflow_rescell
	description = 'Reservoir cell'
	filter_cols = [table.cell_id]

	if request.method == 'GET':
		return get_cell_paged(table, filter_cols)
	elif request.method == 'POST':
		return post_cell(table, description)
	elif request.method == 'DELETE':
		return delete_all_cells(table, description)
	abort(405, 'HTTP Method not allowed.')

@bp.route('/rescell/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def rescellId(id):
	table = gwflow.Gwflow_rescell
	description = 'Reservoir cell'

	if request.method == 'GET':
		return get_cell(table, id, description)
	elif request.method == 'DELETE':
		return delete_cell(table, id, description)
	elif request.method == 'PUT':
		return put_cell(id, table, description)

	abort(405, 'HTTP Method not allowed.')

@bp.route('/rescell-default', methods=['GET', 'PUT'])
def rescellDefault():
	project_db = request.headers.get(rh.PROJECT_DB)
	has_db,error = rh.init(project_db)
	if not has_db: abort(400, error)

	if request.method == 'GET':
		m = gwflow.Gwflow_base.get_or_none()
		if m is None:
			rh.close()
			abort(400, 'Gwflow setup does not exist')

		rh.close()
		return {
			'resbed_thickness': m.resbed_thickness,
			'resbed_k': m.resbed_k
		}
	elif request.method == 'PUT':
		args = request.json
		try:
			resbed_thickness = 0 if 'resbed_thickness' not in args else args['resbed_thickness']
			resbed_k = 0 if 'resbed_k' not in args else args['resbed_k']

			result = gwflow.Gwflow_base.update(resbed_thickness=resbed_thickness, resbed_k=resbed_k).execute()
			rh.close()
			if result > 0:
				return '', 200

			abort(400, 'Unable to update properties {id}.'.format(id=id))
		except gwflow.Gwflow_base.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name='Gwflow setup'))
		except Exception as ex:
			rh.close()
			abort(400, 'Unexpected error {ex}'.format(ex=ex))

# Gwflow_wetland

@bp.route('/wetland', methods=['GET', 'POST', 'DELETE'])
def wetland():
	table = gwflow.Gwflow_wetland
	description = 'Wetland'
	filter_cols = []

	project_db = request.headers.get(rh.PROJECT_DB)
	has_db,error = rh.init(project_db)
	if not has_db: abort(400, error)

	if request.method == 'GET':
		setup.SetupProjectDatabase.create_these_tables([gwflow.Gwflow_wetland])
		items = DefaultRestMethods.get_paged_items(table, filter_cols)
		m = items['model']

		gis_col = 'wet_id'

		ml = [model_to_dict(v, recurse=False) for v in m]
		cons = reservoir.Wetland_wet.select().order_by(reservoir.Wetland_wet.id)
		gis_to_con = {}
		for con in cons:
			gis_to_con[con.id] = con.name

		for d in ml:
			id = d[gis_col]
			d['wetland'] = {
				'id': id,
				'name': gis_to_con.get(id, None)
			}

		return {
			'total': items['total'],
			'matches': items['matches'],
			'items': ml
		}
	elif request.method == 'POST':
		args = request.json
		try:
			m = gwflow.Gwflow_wetland()
			m.thickness = 0 if 'thickness' not in args else args['thickness']
			if 'wet_name' in args:
				m.wet_id = RestHelpers.get_id_from_name(reservoir.Wetland_wet, args['wet_name'])

			result = m.save()
			rh.close()
			if result > 0:
				return {'id': result }, 201

			abort(400, 'Unable to create {item}.'.format(item=description.lower()))
		except Exception as ex:
			rh.close()
			abort(400, 'Unexpected error {ex}'.format(ex=ex))
	elif request.method == 'DELETE':
		return delete_all_cells(table, description)
	abort(405, 'HTTP Method not allowed.')

@bp.route('/wetland/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def wetlandId(id):
	table = gwflow.Gwflow_wetland
	description = 'Wetland'

	project_db = request.headers.get(rh.PROJECT_DB)
	has_db,error = rh.init(project_db)
	if not has_db: abort(400, error)

	if request.method == 'GET':
		m = table.get_or_none(table.wet_id == id)
		if m is None:
			rh.close()
			abort(400, '{} {} does not exist'.format(description, id))

		d = model_to_dict(m, recurse=False)
		con = reservoir.Wetland_wet.get_or_none(reservoir.Wetland_wet.id == d['wet_id'])
		d['wet_name'] = con.name if con is not None else None
		rh.close()
		return d
	elif request.method == 'DELETE':
		query = table.delete().where(table.wet_id == id)
		result = query.execute()
		rh.close()
		if result > 0:
			return '', 204
		
		abort(400, 'Error deleting {item} {id}.'.format(item=description.lower(), id=id))
	elif request.method == 'PUT':
		args = request.json
		try:
			thickness = 0 if 'thickness' not in args else args['thickness']

			result = gwflow.Gwflow_wetland.update(thickness=thickness).where(gwflow.Gwflow_wetland.wet_id == id).execute()
			rh.close()
			if result > 0:
				return '', 200

			abort(400, 'Unable to update properties {id}.'.format(id=id))
		except gwflow.Gwflow_wetland.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=args['wet_name']))
		except Exception as ex:
			rh.close()
			abort(400, 'Unexpected error {ex}'.format(ex=ex))

	abort(405, 'HTTP Method not allowed.')

@bp.route('/wetland-default', methods=['GET', 'PUT'])
def wetlandDefault():
	project_db = request.headers.get(rh.PROJECT_DB)
	has_db,error = rh.init(project_db)
	if not has_db: abort(400, error)

	if request.method == 'GET':
		setup.SetupProjectDatabase.create_these_tables([gwflow.Gwflow_wetland])
		m = gwflow.Gwflow_base.get_or_none()
		if m is None:
			rh.close()
			abort(400, 'Gwflow setup does not exist')

		rh.close()
		return {
			'wet_thickness': m.wet_thickness
		}
	elif request.method == 'PUT':
		args = request.json
		try:
			wet_thickness = 0 if 'wet_thickness' not in args else args['wet_thickness']

			result = gwflow.Gwflow_base.update(wet_thickness=wet_thickness).execute()
			rh.close()
			if result > 0:
				return '', 200

			abort(400, 'Unable to update properties {id}.'.format(id=id))
		except gwflow.Gwflow_base.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name='Gwflow setup'))
		except Exception as ex:
			rh.close()
			abort(400, 'Unexpected error {ex}'.format(ex=ex))

# Gwflow_solutes

@bp.route('/solutes', methods=['GET'])
def solutes():
	if request.method == 'GET':
		table = gwflow.Gwflow_solutes
		filter_cols = [table.solute_name]
		return DefaultRestMethods.get_paged_list(table, filter_cols)
	abort(405, 'HTTP Method not allowed.')

@bp.route('/solutes/<name>', methods=['GET', 'PUT'])
def solutesId(name):
	table = gwflow.Gwflow_solutes
	description = 'Solute'

	project_db = request.headers.get(rh.PROJECT_DB)
	has_db,error = rh.init(project_db)
	if not has_db: abort(400, error)

	if request.method == 'GET':
		m = table.get_or_none(table.solute_name == name)
		if m is None:
			rh.close()
			abort(400, '{} {} does not exist'.format(description, name))

		d = model_to_dict(m, recurse=False)
		rh.close()
		return d
	elif request.method == 'PUT':
		args = request.json
		try:
			sorption = 0 if 'sorption' not in args else args['sorption']
			rate_const = 0 if 'rate_const' not in args else args['rate_const']
			canal_irr = 0 if 'canal_irr' not in args else args['canal_irr']
			init_data = 'single' if 'init_data' not in args else args['init_data']
			init_conc = 0 if 'init_conc' not in args else args['init_conc']

			result = table.update(sorption=sorption,rate_const=rate_const,canal_irr=canal_irr,init_data=init_data,init_conc=init_conc).where(table.solute_name == name).execute()
			rh.close()
			if result > 0:
				return '', 200

			abort(400, 'Unable to update properties {}.'.format(name))
		except table.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name=name))
		except Exception as ex:
			rh.close()
			abort(400, 'Unexpected error {ex}'.format(ex=ex))

	abort(405, 'HTTP Method not allowed.')

@bp.route('/solutes-default', methods=['GET', 'PUT'])
def solutesDefault():
	project_db = request.headers.get(rh.PROJECT_DB)
	has_db,error = rh.init(project_db)
	if not has_db: abort(400, error)

	if request.method == 'GET':
		m = gwflow.Gwflow_base.get_or_none()
		if m is None:
			rh.close()
			abort(400, 'Gwflow setup does not exist')

		rh.close()
		return {
			'transport_steps': m.transport_steps,
			'disp_coef': m.disp_coef
		}
	elif request.method == 'PUT':
		args = request.json
		try:
			transport_steps = 0 if 'transport_steps' not in args else args['transport_steps']
			disp_coef = 0 if 'disp_coef' not in args else args['disp_coef']

			result = gwflow.Gwflow_base.update(transport_steps=transport_steps, disp_coef=disp_coef).execute()
			rh.close()
			if result > 0:
				return '', 200

			abort(400, 'Unable to update properties {id}.'.format(id=id))
		except gwflow.Gwflow_base.DoesNotExist:
			rh.close()
			abort(400, RestHelpers.__invalid_name_msg.format(name='Gwflow setup'))
		except Exception as ex:
			rh.close()
			abort(400, 'Unexpected error {ex}'.format(ex=ex))

#helpers
	
gis_cols = {
	gwflow.Gwflow_hrucell: ['hru', connect.Hru_con, 'many', False],
	gwflow.Gwflow_fpcell: ['channel', connect.Chandeg_con, 'single', True],
	gwflow.Gwflow_rivcell: ['channel', connect.Chandeg_con, 'single', False],
	gwflow.Gwflow_lsucell: ['lsu', connect.Rout_unit_con, 'many', False],
	gwflow.Gwflow_rescell: ['res', connect.Reservoir_con, 'single', True],
}
	
def get_cell_paged(table, filter_cols) -> Response:
	items = DefaultRestMethods.get_paged_items(table, filter_cols)
	m = items['model']

	gis_col = gis_cols.get(table, None)

	ml = [model_to_dict(v, recurse=False) for v in m]
	gis_to_con_name = IndexHelper(gis_col[1]).get_names()
	for d in ml:
		id = d[gis_col[0]]
		d[gis_col[0]] = {
			'id': id,
			'name': gis_to_con_name.get(id, None)
		}

	return {
		'total': items['total'],
		'matches': items['matches'],
		'items': ml
	}

def get_cell(table, id, description) -> Response:
	project_db = request.headers.get(rh.PROJECT_DB)
	has_db,error = rh.init(project_db)
	if not has_db: abort(400, error)

	gis_col = gis_cols.get(table, None)

	m = table.get_or_none(table.cell_id == id)
	if m is None:
		rh.close()
		abort(400, '{} {} does not exist'.format(description, id))

	d = model_to_dict(m, recurse=False)
	con = gis_col[1].get_or_none(gis_col[1].gis_id == d[gis_col[0]])
	d['{}_name'.format(gis_col[0])] = con.name if con is not None else None
	d.pop(gis_col[0], None)
	rh.close()
	return d

def delete_all_cells(table, description) -> Response:
	project_db = request.headers.get(rh.PROJECT_DB)
	has_db,error = rh.init(project_db)
	if not has_db: abort(400, error)

	query = table.delete()
	result = query.execute()
	rh.close()
	if result > 0:
		return '', 204
	
	abort(400, 'Error deleting {item}.'.format(item=description.lower()))

def delete_cell(table, id, description) -> Response:
	project_db = request.headers.get(rh.PROJECT_DB)
	has_db,error = rh.init(project_db)
	if not has_db: abort(400, error)

	query = table.delete().where(table.cell_id == id)
	result = query.execute()
	rh.close()
	if result > 0:
		return '', 204
	
	abort(400, 'Error deleting {item} {id}.'.format(item=description.lower(), id=id))
		
def post_cell(table, item_description) -> Response:
	project_db = request.headers.get(rh.PROJECT_DB)
	has_db,error = rh.init(project_db)
	if not has_db: abort(400, error)

	try:
		result = save_cell_args(table, request.json, is_new=True)

		rh.close()
		if result > 0:
			return {'id': result }, 201

		abort(400, 'Unable to create {item}.'.format(item=item_description.lower()))
	except Exception as ex:
		rh.close()
		abort(400, 'Unexpected error {ex}'.format(ex=ex))
		
def put_cell(id, table, item_description) -> Response:
	project_db = request.headers.get(rh.PROJECT_DB)
	has_db,error = rh.init(project_db)
	if not has_db: abort(400, error)

	try:
		result = save_cell_args(table, request.json, id=id)

		rh.close()
		if result > 0:
			return '', 200

		abort(400, 'Unable to update {item} {id}.'.format(item=item_description.lower(), id=id))
	except table.DoesNotExist:
		rh.close()
		abort(404, '{item} {id} does not exist'.format(item=item_description, id=id))
	except Exception as ex:
		rh.close()
		abort(400, 'Unexpected error {ex}'.format(ex=ex))

def save_cell_args(table, args, id=0, is_new=False):
	gis_col = gis_cols.get(table, None)
	gis_name_to_con = IndexHelper(gis_col[1]).get_id_from_name()
	gis_name = '{}_name'.format(gis_col[0])

	params = {}
	table_gis_field = None
	for field in table._meta.sorted_fields:
		if field.name in args or '{}_name'.format(field.name) in args:
			if field.name == gis_col[0]:
				table_gis_field = field
				params[field.name] = gis_name_to_con.get(args[gis_name], None)
			else:
				params[field.name] = args[field.name]

	if is_new:
		query = table.insert(params)
	elif gis_col[2] == 'single':
		query = table.update(params).where(table.cell_id == id)
	else:
		query = table.update(params).where((table.cell_id == id) & (table_gis_field == params[gis_col[0]]))
	
	return query.execute()