from flask import Blueprint, jsonify, request, abort
from .config import RequestHeaders as rh

from playhouse.shortcuts import model_to_dict
from playhouse.migrate import *

from actions import import_gis
from database.project import config, gis, climate, connect, simulation, regions
from database import lib

from helpers import utils
from datetime import datetime
import os.path

bp = Blueprint('setup', __name__, url_prefix='/setup')

@bp.route('/config', methods=['GET'])
def getConfig():
	project_db = request.headers.get(rh.PROJECT_DB)
	has_db,error = rh.init(project_db)
	if not has_db: abort(400, error)

	check_config(project_db)
	m = config.Project_config.get_or_none()

	rh.close()
	if m is None:
		abort(400, 'Could not retrieve project configuration table.')
	else:
		if m.gis_version is not None and not import_gis.is_supported_version(m.gis_version): #and not import_gis_legacy.is_supported_version(m.gis_version):
			abort(400, 'This version of SWAT+ Editor does not support QSWAT+ {uv}.'.format(uv=m.gis_version))

		d = get_model_to_dict_dates(m, project_db)

		description = None
		conn = lib.open_db(project_db)
		if lib.exists_table(conn, 'object_cnt'):
			oc = simulation.Object_cnt.get_or_none()
			if oc is not None:
				description = oc.name
		d["project_description"] = description
		conn.close()

		return jsonify(d)
	
@bp.route('/config', methods=['PUT'])
def saveConfig():
	project_db = request.headers.get(rh.PROJECT_DB)
	has_db,error = rh.init(project_db)
	if not has_db: abort(400, error)

	data = request.json
	if 'name' not in data: abort(400, 'Project name was omitted from the request.')
	
	m = config.Project_config.get_or_none()
	
	if m is None:
		rh.close()
		abort(400, 'Could not retrieve project configuration table.')
	
	m.project_name = data['name']
	result = m.save()

	oc = simulation.Object_cnt.get_or_none()
	if oc is None:
		rh.close()
		abort(400, 'Could not retrieve object_cnt table.')
	
	if 'description' in data and data['description'] is not None:
		oc.name = data['description']
	else:
		oc.name = data['name']
	result = oc.save()

	rh.close()
	if result > 0: return '', 200
	abort(400, 'Unable to update project configuration table.')

	
@bp.route('/info', methods=['GET'])
def getInfo():
	project_db = request.headers.get(rh.PROJECT_DB)
	has_db,error = rh.init(project_db)
	if not has_db: abort(400, error)

	conn = lib.open_db(project_db)
	if not lib.exists_table(conn, 'chandeg_con'):
		conn.close()
		rh.close()
		abort(400, 'Project has not been set up.')
	conn.close()

	m = config.Project_config.get_or_none()
	if m is None:
		rh.close()
		abort(400, 'Could not retrieve project configuration table.')
	else:
		gis_type = 'QSWAT+ ' if m.gis_type == 'qgis' else 'GIS '
		gis_text = '' if m.gis_version is None else gis_type + m.gis_version

		landuse_distrib = []
		if m.gis_version is not None:
			landuse_distrib = gis.Gis_hrus.select(fn.Lower(gis.Gis_hrus.landuse).alias('name'), fn.Sum(gis.Gis_hrus.arslp).alias('y')).group_by(gis.Gis_hrus.landuse)

		current_path = os.path.dirname(project_db)
		scenarios_path = os.path.join(current_path, 'Scenarios')
		scenarios = []
		if os.path.isdir(scenarios_path):
			for p in os.listdir(scenarios_path):
				if os.path.isdir(os.path.join(scenarios_path, p)) and p != 'Default' and p != 'default':
					db_files = [f for f in os.listdir(os.path.join(scenarios_path, p)) if f.endswith('.sqlite')]
					if len(db_files) > 0:
						scenarios.append({'name': p, 'path': os.path.join(scenarios_path, p, db_files[0])})

		oc = simulation.Object_cnt.get_or_none()

		project_area = connect.Rout_unit_con.select(fn.Sum(connect.Rout_unit_con.area)).scalar()
		if m.is_lte:
			project_area = connect.Hru_lte_con.select(fn.Sum(connect.Hru_lte_con.area)).scalar()

		info = {
			'name': m.project_name,
			'description': oc.name,
			'file_path': current_path,
			'last_modified': utils.json_encode_datetime(datetime.fromtimestamp(os.path.getmtime(project_db))),
			'is_lte': m.is_lte,
			'status': {
				'imported_weather': climate.Weather_sta_cli.select().count() > 0 and climate.Weather_wgn_cli.select().count() > 0,
				'wrote_inputs': m.input_files_last_written is not None,
				'ran_swat': m.swat_last_run is not None,
				'imported_output': m.output_last_imported is not None,
				'using_gis': m.gis_version is not None
			},
			'simulation': model_to_dict(simulation.Time_sim.get_or_none()),
			'total_area': project_area, #gis.Gis_subbasins.select(fn.Sum(gis.Gis_subbasins.area)).scalar(),
			'totals': {
				'hru': connect.Hru_con.select().count(),
				'lhru': connect.Hru_lte_con.select().count(),
				'rtu': connect.Rout_unit_con.select().count(),
				'mfl': connect.Modflow_con.select().count(),
				'aqu': connect.Aquifer_con.select().count(),
				'cha': connect.Channel_con.select().count(),
				'res': connect.Reservoir_con.select().count(),
				'rec': connect.Recall_con.select().count(),
				'exco': connect.Exco_con.select().count(),
				'dlr': connect.Delratio_con.select().count(),
				'out': connect.Outlet_con.select().count(),
				'lcha': connect.Chandeg_con.select().count(),
				'aqu2d': connect.Aquifer2d_con.select().count(),
				'lsus': regions.Ls_unit_def.select().count(),
				'subs': gis.Gis_subbasins.select().count()
			},
			'editor_version': m.editor_version,
			'gis_version': gis_text,
			'charts': {
				'landuse': [{'name': o.name, 'y': o.y} for o in landuse_distrib]
			},
			'scenarios': scenarios
		}

		rh.close()
		return jsonify(info)

"""
Helper functions
"""

def check_config(project_db):
	conn = lib.open_db(project_db)
	if lib.exists_table(conn, 'project_config'):
		config_cols = lib.get_column_names(conn, 'project_config')
		col_names = [v['name'] for v in config_cols]
		if 'output_last_imported' not in col_names:
			migrator = SqliteMigrator(SqliteDatabase(project_db))
			migrate(
				migrator.add_column('project_config', 'output_last_imported', DateTimeField(null=True)),
				migrator.add_column('project_config', 'imported_gis', BooleanField(default=False)),
				migrator.add_column('project_config', 'is_lte', BooleanField(default=False)),
			)

			if lib.exists_table(conn, 'plants_plt'):
				lib.delete_table(project_db, 'plants_plt')

	if lib.exists_table(conn, 'plants_plt'):
		plt_cols = lib.get_column_names(conn, 'plants_plt')
		plt_col_names = [v['name'] for v in plt_cols]
		if 'rsd_pctcov' not in plt_col_names:
			migrator = SqliteMigrator(SqliteDatabase(project_db))
			migrate(
				migrator.rename_column('plants_plt', 'wnd_dead', 'rsd_pctcov'),
				migrator.rename_column('plants_plt', 'wnd_flat', 'rsd_covfac'),
			)
	conn.close()


def get_model_to_dict_dates(m, project_db):
	d = model_to_dict(m)
	d['reference_db'] = utils.full_path(project_db, m.reference_db)
	d['wgn_db'] = utils.full_path(project_db, m.wgn_db)
	d['weather_data_dir'] = utils.full_path(project_db, m.weather_data_dir)
	d['input_files_dir'] = utils.full_path(project_db, m.input_files_dir)
	d['input_files_last_written'] = utils.json_encode_datetime(m.input_files_last_written)
	d['swat_last_run'] = utils.json_encode_datetime(m.swat_last_run)
	d['output_last_imported'] = utils.json_encode_datetime(m.output_last_imported)
	return d