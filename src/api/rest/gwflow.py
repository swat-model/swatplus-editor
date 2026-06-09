from flask import Blueprint, request, abort, Response
from playhouse.shortcuts import model_to_dict

from .defaults import DefaultRestMethods, RestHelpers
from .config import RequestHeaders as rh
from database.project import gwflow, config, connect, setup, reservoir
from database import lib
from fileio.connect import IndexHelper

bp = Blueprint('gwflow', __name__, url_prefix='/gwflow')

@bp.route('/enabled', methods=['GET'])
def enabled():
	project_db = request.headers.get(rh.PROJECT_DB)
	has_db,error = rh.init(project_db)
	if not has_db: abort(400, error)

	pc = config.Project_config.get()

	can_enable = False
	conn = lib.open_db(project_db)
	if lib.exists_table(conn, 'codes_gw'):
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

	table = gwflow.Gwflow_config
	m = table.get_or_none()
	pc = config.Project_config.get()

	if request.method == 'GET':
		if m is None:
			rh.close()
			abort(400, 'Gwflow configuration does not exist')

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

			abort(400, 'Unable to update gwflow configuration.')
		except table.DoesNotExist:
			rh.close()
			abort(404, 'Gwflow configuration does not exist')
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

# Gwflow_cell

@bp.route('/cells', methods=['GET'])
def cells():
	if request.method == 'GET':
		table = gwflow.Gwflow_cell
		filter_cols = [table.cell_id]
		return DefaultRestMethods.get_paged_list(table, filter_cols)
	abort(405, 'HTTP Method not allowed.')

@bp.route('/cells/<int:id>', methods=['GET', 'PUT'])
def cellsId(id):
	project_db = request.headers.get(rh.PROJECT_DB)
	has_db,error = rh.init(project_db)
	if not has_db: abort(400, error)
	table = gwflow.Gwflow_cell

	if request.method == 'GET':
		m = table.get_or_none(table.cell_id == id)
		if m is None:
			rh.close()
			abort(400, '{} {} does not exist'.format('Cell', id))
		rh.close()
		return model_to_dict(m, recurse=False)
	elif request.method == 'PUT':
		return DefaultRestMethods.put(id, gwflow.Gwflow_cell, 'Cell', primary_key='cell_id')

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

@bp.route('/fpcell/<int:id>', methods=['PUT'])
def fpcellIdPut(id):
	table = gwflow.Gwflow_fpcell
	description = 'Floodplain cell'

	if request.method == 'PUT':
		return put_cell(id, table, description) # Note, they are allowed to change the channel in the form, so don't include the original channel id in this method

	abort(405, 'HTTP Method not allowed.')

@bp.route('/fpcell/<int:id>/<int:channel_id>', methods=['GET', 'DELETE'])
def fpcellId(id, channel_id):
	table = gwflow.Gwflow_fpcell
	composite_key_part2_field = gwflow.Gwflow_fpcell.channel_id
	composite_key_part2_value = channel_id
	description = 'Floodplain cell'

	if request.method == 'GET':
		return get_cell(table, id, description, composite_key_part2_field, composite_key_part2_value)
	elif request.method == 'DELETE':
		return delete_cell(table, id, description, composite_key_part2_field, composite_key_part2_value)

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

@bp.route('/rescell/<int:id>', methods=['PUT'])
def rescellIdPut(id):
	table = gwflow.Gwflow_rescell
	description = 'Reservoir cell'

	if request.method == 'PUT':
		return put_cell(id, table, description) # Note, they are allowed to change the reservoir in the form, so don't include the original reservoir id in this method

	abort(405, 'HTTP Method not allowed.')

@bp.route('/rescell/<int:id>/<int:reservoir_id>', methods=['GET', 'DELETE'])
def rescellId(id, reservoir_id):
	table = gwflow.Gwflow_rescell
	composite_key_part2_field = gwflow.Gwflow_rescell.reservoir_id
	composite_key_part2_value = reservoir_id
	description = 'Reservoir cell'

	if request.method == 'GET':
		return get_cell(table, id, description, composite_key_part2_field, composite_key_part2_value)
	elif request.method == 'DELETE':
		return delete_cell(table, id, description, composite_key_part2_field, composite_key_part2_value)

	abort(405, 'HTTP Method not allowed.')

@bp.route('/rescell-default', methods=['GET', 'PUT'])
def rescellDefault():
	project_db = request.headers.get(rh.PROJECT_DB)
	has_db,error = rh.init(project_db)
	if not has_db: abort(400, error)

	if request.method == 'GET':
		m = gwflow.Gwflow_config.get_or_none()
		if m is None:
			rh.close()
			abort(400, 'Gwflow configuration does not exist')

		rh.close()
		return {
			'resbed_thickness': m.resbed_thickness,
			'resbed_k': m.resbed_k
		}
	elif request.method == 'PUT':
		args = request.json
		try:
			resbed_thickness = args.get('resbed_thickness', 0)
			resbed_k = args.get('resbed_k', 0)

			result = gwflow.Gwflow_config.update(resbed_thickness=resbed_thickness, resbed_k=resbed_k).execute()
			rh.close()
			if result > 0:
				return '', 200

			abort(400, 'Unable to update properties.')
		except gwflow.Gwflow_config.DoesNotExist:
			rh.close()
			abort(400, 'Gwflow configuration does not exist')
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

		ml = [model_to_dict(v, recurse=False) for v in m]
		cons = reservoir.Wetland_wet.select().order_by(reservoir.Wetland_wet.id)
		gis_to_con = {con.id: con.name for con in cons}

		for d in ml:
			wid = d['wet_id']
			d['wetland'] = {'id': wid, 'name': gis_to_con.get(wid, None)}

		return {
			'total': items['total'],
			'matches': items['matches'],
			'items': ml
		}
	elif request.method == 'POST':
		args = request.json
		try:
			m = gwflow.Gwflow_wetland()
			m.thickness = args.get('thickness', 0)
			if 'wet_name' in args:
				m.wet_id = RestHelpers.get_id_from_name(reservoir.Wetland_wet, args['wet_name'])

			result = m.save()
			rh.close()
			if result > 0:
				return {'id': result}, 201

			abort(400, 'Unable to create {}.'.format(description.lower()))
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
		result = table.delete().where(table.wet_id == id).execute()
		rh.close()
		if result > 0:
			return '', 204
		abort(400, 'Error deleting {} {}.'.format(description.lower(), id))
	elif request.method == 'PUT':
		args = request.json
		try:
			result = gwflow.Gwflow_wetland.update(
				thickness=args.get('thickness', 0)
			).where(gwflow.Gwflow_wetland.wet_id == id).execute()
			rh.close()
			if result > 0:
				return '', 200
			abort(400, 'Unable to update {} {}.'.format(description.lower(), id))
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
		m = gwflow.Gwflow_config.get_or_none()
		if m is None:
			rh.close()
			abort(400, 'Gwflow configuration does not exist')
		rh.close()
		return {'wet_thickness': m.wet_thickness}
	elif request.method == 'PUT':
		args = request.json
		try:
			result = gwflow.Gwflow_config.update(
				wet_thickness=args.get('wet_thickness', 0)
			).execute()
			rh.close()
			if result > 0:
				return '', 200
			abort(400, 'Unable to update properties.')
		except gwflow.Gwflow_config.DoesNotExist:
			rh.close()
			abort(400, 'Gwflow configuration does not exist')
		except Exception as ex:
			rh.close()
			abort(400, 'Unexpected error {ex}'.format(ex=ex))

# Gwflow_solute

@bp.route('/solutes', methods=['GET'])
def solutes():
	if request.method == 'GET':
		table = gwflow.Gwflow_solute
		filter_cols = [table.name]
		return DefaultRestMethods.get_paged_list(table, filter_cols)
	abort(405, 'HTTP Method not allowed.')

@bp.route('/solutes/<int:id>', methods=['GET', 'PUT'])
def solutesId(id):
	table = gwflow.Gwflow_solute
	description = 'Solute'

	project_db = request.headers.get(rh.PROJECT_DB)
	has_db,error = rh.init(project_db)
	if not has_db: abort(400, error)

	if request.method == 'GET':
		m = table.get_or_none(table.id == id)
		if m is None:
			rh.close()
			abort(400, '{} {} does not exist'.format(description, id))
		rh.close()
		return model_to_dict(m, recurse=False)
	elif request.method == 'PUT':
		args = request.json
		try:
			result = table.update(
				sorption_coef=args.get('sorption_coef', 0),
				rate_const=args.get('rate_const', 0),
				canal_irr=args.get('canal_irr', 0),
				init_conc=args.get('init_conc', 0),
			).where(table.id == id).execute()
			rh.close()
			if result > 0:
				return '', 200
			abort(400, 'Unable to update {}.'.format(id))
		except table.DoesNotExist:
			rh.close()
			abort(400, '{} {} does not exist'.format(description, id))
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
		m = gwflow.Gwflow_config.get_or_none()
		if m is None:
			rh.close()
			abort(400, 'Gwflow configuration does not exist')
		rh.close()
		return {
			'transport_steps': m.transport_steps,
			'disp_coef': m.disp_coef
		}
	elif request.method == 'PUT':
		args = request.json
		try:
			result = gwflow.Gwflow_config.update(
				transport_steps=args.get('transport_steps', 0),
				disp_coef=args.get('disp_coef', 0)
			).execute()
			rh.close()
			if result > 0:
				return '', 200
			abort(400, 'Unable to update properties.')
		except gwflow.Gwflow_config.DoesNotExist:
			rh.close()
			abort(400, 'Gwflow configuration does not exist')
		except Exception as ex:
			rh.close()
			abort(400, 'Unexpected error {ex}'.format(ex=ex))

# Helpers

gis_cols = {
	gwflow.Gwflow_hrucell: ['hru_id', connect.Hru_con, 'many', False],
	gwflow.Gwflow_fpcell: ['channel_id', connect.Chandeg_con, 'many', True],
	gwflow.Gwflow_chancell: ['channel_id', connect.Chandeg_con, 'single', False],
	gwflow.Gwflow_lsucell: ['lsu_id', connect.Rout_unit_con, 'many', False],
	gwflow.Gwflow_rescell: ['reservoir_id', connect.Reservoir_con, 'many', True],
}

def get_cell_paged(table, filter_cols) -> Response:
	items = DefaultRestMethods.get_paged_items(table, filter_cols)
	m = items['model']

	gis_col = gis_cols.get(table, None)

	ml = [model_to_dict(v, recurse=False) for v in m]

	if gis_col is not None:
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

def get_cell_model(table, id, composite_key_part2_field = None, composite_key_part2_value = None):
	if composite_key_part2_field is not None and composite_key_part2_value is not None:
		return table.get_or_none((table.cell_id == id) & (composite_key_part2_field == composite_key_part2_value))
	else:
		return table.get_or_none(table.cell_id == id)

def get_cell(table, id, description, composite_key_part2_field = None, composite_key_part2_value = None) -> Response:
	project_db = request.headers.get(rh.PROJECT_DB)
	has_db,error = rh.init(project_db)
	if not has_db: abort(400, error)

	m = get_cell_model(table, id, composite_key_part2_field, composite_key_part2_value)
	if m is None:
		rh.close()
		abort(400, '{} {} does not exist'.format(description, id))

	gis_col = gis_cols.get(table, None)
	d = model_to_dict(m, recurse=False)
	con = gis_col[1].get_or_none(gis_col[1].gis_id == d[gis_col[0]])
	d['{}_name'.format(gis_col[0])] = con.name if con is not None else None
	d.pop(gis_col[0], None)
	rh.close()
	return d

def post_cell(table, description) -> Response:
	project_db = request.headers.get(rh.PROJECT_DB)
	has_db,error = rh.init(project_db)
	if not has_db: abort(400, error)

	args = request.json
	gis_col = gis_cols.get(table, None)

	try:
		result = save_cell_args(table, request.json, is_new=True)

		rh.close()
		if result > 0:
			return {'id': result}, 201

		abort(400, 'Unable to create {}.'.format(description.lower()))
	except Exception as ex:
		rh.close()
		abort(400, 'Unexpected error {ex}'.format(ex=ex))

def put_cell(id, table, description) -> Response:
	project_db = request.headers.get(rh.PROJECT_DB)
	has_db,error = rh.init(project_db)
	if not has_db: abort(400, error)

	try:
		result = save_cell_args(table, request.json, id=id)

		rh.close()
		if result > 0:
			return '', 200
		abort(400, 'Unable to update {} {}.'.format(description.lower(), id))
	except table.DoesNotExist:
		rh.close()
		abort(404, '{} {} does not exist'.format(description, id))
	except Exception as ex:
		rh.close()
		abort(400, 'Unexpected error {ex}'.format(ex=ex))

def delete_cell(table, id, description, composite_key_part2_field = None, composite_key_part2_value = None) -> Response:
	project_db = request.headers.get(rh.PROJECT_DB)
	has_db,error = rh.init(project_db)
	if not has_db: abort(400, error)

	if composite_key_part2_field is not None and composite_key_part2_value is not None:
		result = table.delete().where((table.cell_id == id) & (composite_key_part2_field == composite_key_part2_value)).execute()
	else:
		result = table.delete().where(table.cell_id == id).execute()
	rh.close()
	if result > 0:
		return '', 204
	abort(400, 'Error deleting {} {}.'.format(description.lower(), id))

def delete_all_cells(table, description) -> Response:
	project_db = request.headers.get(rh.PROJECT_DB)
	has_db,error = rh.init(project_db)
	if not has_db: abort(400, error)

	result = table.delete().execute()
	rh.close()
	if result > 0:
		return '', 204
	abort(400, 'Error deleting {}.'.format(description.lower()))

def save_cell_args(table, args, id=0, is_new=False):
	gis_col = gis_cols.get(table, None)
	gis_name_to_con = IndexHelper(gis_col[1]).get_id_from_name()
	gis_name = '{}_name'.format(gis_col[0]) # Note, this is simply a UI decision what this is called, so in RescellForm.vue for example, it's just reservoir_id_name for lookup simplicity.

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
