from flask import Blueprint, request, abort
from .config import RequestHeaders as rh

from database.project import connect, climate, channel, aquifer, reservoir, hydrology, hru, hru_parm_db, lum, soils, routing_unit, dr, init, decision_table, exco, dr, structural, gis
from helpers import table_mapper # Note: string to table name dictionary moved here

MAX_ROWS = 1000

bp = Blueprint('auto_complete', __name__, url_prefix='/auto_complete')

@bp.route('/match/<table_type>/<partial_name>', methods=['GET'])
def getMatch(table_type, partial_name):
	project_db = request.headers.get(rh.PROJECT_DB)
	has_db,error = rh.init(project_db)
	if not has_db: abort(400, error)

	table = table_mapper.types.get(table_type, None)

	if table is None:
		rh.close()
		return abort(404, 'Unable to find table type for auto-complete.')

	# If table is a decision table, filter based on file_name
	if '.dtl' in table_type:
		m = table.select(table.name).where((table.name.contains(partial_name)) & (table.file_name == table_type)).limit(MAX_ROWS)
		nm = table.select(table.name).where((~(table.name.contains(partial_name))) & (table.file_name == table_type)).limit(MAX_ROWS)
	else:
		m = table.select(table.name).where(table.name.contains(partial_name)).limit(MAX_ROWS)
		nm = table.select(table.name).where(~(table.name.contains(partial_name))).limit(MAX_ROWS)

	matches = [v.name for v in m]
	non_matches = [nv.name for nv in nm]
	
	rh.close()
	if len(matches) > 0:
		if len(non_matches) > 0:
			return matches + non_matches
		return matches
	return non_matches

@bp.route('/all/<table_type>', methods=['GET'])
def getAll(table_type):
	project_db = request.headers.get(rh.PROJECT_DB)
	has_db,error = rh.init(project_db)
	if not has_db: abort(400, error)

	table = table_mapper.types.get(table_type, None)

	if table is None:
		rh.close()
		return abort(404, 'Unable to find table type for auto-complete.')

	# If table is a decision table, filter based on file_name
	if '.dtl' in table_type:
		m = table.select(table.name).where(table.file_name == table_type).order_by(table.name).limit(MAX_ROWS)
	else:
		m = table.select(table.name).order_by(table.name).limit(MAX_ROWS)

	rh.close()
	return [v.name for v in m]

@bp.route('/item-id/<table_type>/<name>', methods=['GET'])
def getItemId(table_type, name):
	project_db = request.headers.get(rh.PROJECT_DB)
	has_db,error = rh.init(project_db)
	if not has_db: abort(400, error)

	table = table_mapper.types.get(table_type, None)

	if table is None:
		rh.close()
		return abort(404, 'Unable to find table type for auto-complete.')

	try:
		m = table.get(table.name == name)
		rh.close()
		return {'id': m.id}
	except table.DoesNotExist:
		rh.close()
		abort(404, '{name} does not exist in the database.'.format(name=name))

@bp.route('/select-list/<table_type>/<value>', methods=['GET'])
def getSelectList(table_type, value):
	project_db = request.headers.get(rh.PROJECT_DB)
	has_db,error = rh.init(project_db)
	if not has_db: abort(400, error)

	table = table_mapper.types.get(table_type, None)

	if table is None:
		rh.close()
		return abort(404, 'Unable to find table type for auto-complete.')
	
	if value == 'index':
		items = []
		i = 1
		for v in table.select(table.id, table.name).order_by(table.id):
			items.append({'value': i, 'text': v.name})
			i += 1
		rh.close()
		return items
	else:
		items = table.select().order_by(table.name)
		
		rh.close()
		if value == 'id':
			return [{'value': m.id, 'text': m.name} for m in items]
		else:
			return [{'value': m.name, 'text': m.name} for m in items]
		
@bp.route('/subbasins', methods=['GET'])
def getSubbasins():
	project_db = request.headers.get(rh.PROJECT_DB)
	has_db,error = rh.init(project_db)
	if not has_db: abort(400, error)

	items = gis.Gis_subbasins.select().order_by(gis.Gis_subbasins.id)
	rh.close()
	return [{'value': m.id, 'text': 'Subbasin {}'.format(m.id)} for m in items]

@bp.route('/landuse', methods=['POST'])
def getLanduse():
	project_db = request.headers.get(rh.PROJECT_DB)
	has_db,error = rh.init(project_db)
	if not has_db: abort(400, error)

	if 'selected_subs' not in request.json: abort(400, 'Selected subbasins were omitted from the request.')
	selected_subs = request.json['selected_subs']

	chas = gis.Gis_channels.select(gis.Gis_channels.id).where(gis.Gis_channels.subbasin.in_(selected_subs))
	lsus = gis.Gis_lsus.select(gis.Gis_lsus.id).where(gis.Gis_lsus.channel.in_(chas))
	items = gis.Gis_hrus.select(gis.Gis_hrus.landuse).distinct().where(gis.Gis_hrus.lsu.in_(lsus))
	rh.close()
	return [{'value': m.landuse, 'text': m.landuse} for m in items]

@bp.route('/soils', methods=['POST'])
def getSoils():
	project_db = request.headers.get(rh.PROJECT_DB)
	has_db,error = rh.init(project_db)
	if not has_db: abort(400, error)

	if 'selected_subs' not in request.json: abort(400, 'Selected subbasins were omitted from the request.')
	selected_subs = request.json['selected_subs']
	selected_landuse = request.json['selected_landuse']

	chas = gis.Gis_channels.select(gis.Gis_channels.id).where(gis.Gis_channels.subbasin.in_(selected_subs))
	lsus = gis.Gis_lsus.select(gis.Gis_lsus.id).where(gis.Gis_lsus.channel.in_(chas))
	items = gis.Gis_hrus.select(gis.Gis_hrus.soil).distinct().where((gis.Gis_hrus.lsu.in_(lsus)) & (gis.Gis_hrus.landuse.in_(selected_landuse)))
	rh.close()
	return [{'value': m.soil, 'text': m.soil} for m in items]

@bp.route('/objects/<table_type>', methods=['POST'])
def getObjects(table_type):
	project_db = request.headers.get(rh.PROJECT_DB)
	has_db,error = rh.init(project_db)
	if not has_db: abort(400, error)

	table = table_mapper.types.get(table_type, None)

	if table is None:
		rh.close()
		return abort(404, 'Invalid connection table name provided.')

	items = table.select(table.id, table.name)

	if 'selected_subs' in request.json and len(request.json['selected_subs']) > 0:
		con_to_gis = {
			'aqu_con': gis.Gis_aquifers,
			'init_aqu': gis.Gis_aquifers,

			'res_con': gis.Gis_water,
			'init_res': gis.Gis_water,
			'hyd_res': gis.Gis_water,
			'sed_res': gis.Gis_water,
			'nut_res': gis.Gis_water,

			'rtu_con': gis.Gis_lsus,
			'fld': gis.Gis_lsus,
			'topo': gis.Gis_lsus,

			'hru_con': gis.Gis_hrus,
			'hru_lte_con': gis.Gis_hrus,
			'hyd': gis.Gis_hrus,
			'topo_hru': gis.Gis_hrus,
			'wet_res': gis.Gis_hrus,
			'hyd_wet': gis.Gis_hrus,

			'chandeg_con': gis.Gis_channels,
			'init_cha': gis.Gis_channels,
			'hyd_sed_lte_cha': gis.Gis_channels,
			'nut_cha': gis.Gis_channels,

			'rec_con': gis.Gis_points
		}

		hru_types = ['rtu_con', 'hru_con', 'hru_lte_con', 'hyd', 'topo_hru', 'wet_res', 'hyd_wet']
		rtu_types = ['rtu_con', 'fld', 'topo']

		gis_table = con_to_gis.get(table_type, None)
		if gis_table is None:
			rh.close()
			return abort(404, 'Could not find matching GIS table.')
		
		prop_data = {
			'init_cha': (connect.Chandeg_con, channel.Channel_lte_cha, channel.Channel_lte_cha.init_id),
			'hyd_sed_lte_cha': (connect.Chandeg_con, channel.Channel_lte_cha, channel.Channel_lte_cha.hyd_id),
			'nut_cha': (connect.Chandeg_con, channel.Channel_lte_cha, channel.Channel_lte_cha.nut_id),

			'fld': (connect.Rout_unit_con, routing_unit.Rout_unit_rtu, routing_unit.Rout_unit_rtu.field_id),
			'topo': (connect.Rout_unit_con, routing_unit.Rout_unit_rtu, routing_unit.Rout_unit_rtu.topo_id),

			'hyd': (connect.Hru_con, hru.Hru_data_hru, hru.Hru_data_hru.hydro_id),
			'topo_hru': (connect.Hru_con, hru.Hru_data_hru, hru.Hru_data_hru.topo_id),
			'wet_res': (connect.Hru_con, hru.Hru_data_hru, hru.Hru_data_hru.surf_stor_id),
			'hyd_wet': (connect.Hru_con, hru.Hru_data_hru, hru.Hru_data_hru.surf_stor_id, reservoir.Wetland_wet, reservoir.Wetland_wet.hyd_id),

			'init_aqu': (connect.Aquifer_con, aquifer.Aquifer_aqu, aquifer.Aquifer_aqu.init_id),

			'init_res': (connect.Reservoir_con, reservoir.Reservoir_res, reservoir.Reservoir_res.init_id),
			'hyd_res': (connect.Reservoir_con, reservoir.Reservoir_res, reservoir.Reservoir_res.hyd_id),
			'sed_res': (connect.Reservoir_con, reservoir.Reservoir_res, reservoir.Reservoir_res.sed_id),
			'nut_res': (connect.Reservoir_con, reservoir.Reservoir_res, reservoir.Reservoir_res.nut_id)
		}
		prop_types = prop_data.get(table_type, None)

		selected_subs = request.json['selected_subs']

		if table_type in hru_types or table_type in rtu_types:
			chas = gis.Gis_channels.select(gis.Gis_channels.id).where(gis.Gis_channels.subbasin.in_(selected_subs))
			lsus = gis.Gis_lsus.select(gis.Gis_lsus.id).where(gis.Gis_lsus.channel.in_(chas))
			if table_type in hru_types:
				w = (gis.Gis_hrus.lsu.in_(lsus))
				if 'selected_landuse' in request.json and len(request.json['selected_landuse']) > 0:
					w = w & (gis.Gis_hrus.landuse.in_(request.json['selected_landuse']))
					if 'selected_soils' in request.json and len(request.json['selected_soils']) > 0:
						w = w & (gis.Gis_hrus.soil.in_(request.json['selected_soils']))
				sub_items = gis.Gis_hrus.select(gis.Gis_hrus.id).where(w)
			else:
				sub_items = lsus
		else:
			sub_items = gis_table.select(gis_table.id).where(gis_table.subbasin.in_(selected_subs))

		if prop_types is None:
			items = items.where(table.gis_id.in_(sub_items))
		else:
			con_table = prop_types[0]
			prop_table = prop_types[1]
			prop_col = prop_types[2]

			con_items = con_table.select(prop_col).join(prop_table).where(con_table.gis_id.in_(sub_items))

			if len(prop_types) > 3:
				second_prop_table = prop_types[3]
				second_prop_col = prop_types[4]
				second_items = second_prop_table.select(second_prop_col).where(second_prop_table.id.in_(con_items))
				items = items.where(table.id.in_(second_items))
			else:
				items = items.where(table.id.in_(con_items))

	rh.close()
	return [{'value': m.id, 'text': m.name} for m in items.order_by(table.name)]