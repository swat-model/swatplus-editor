from flask import Blueprint, jsonify, request, abort
from .config import RequestHeaders as rh

from playhouse.shortcuts import model_to_dict
from playhouse.migrate import *

from actions import import_gis
from actions.get_swatplus_check import GetSwatplusCheck
from database.project import config, gis, climate, connect, simulation, regions, basin
from database import lib
from fileio import config as fileio_config

from helpers import utils
from datetime import datetime
import os.path

FILE_CIO_DEFAULT = 0
FILE_CIO_USER_PROVIDED = 1
FILE_CIO_NONE = 2

bp = Blueprint('setup', __name__, url_prefix='/setup')

@bp.route('/config', methods=['GET'])
def getConfig():
	project_db = request.headers.get(rh.PROJECT_DB)
	has_db,error = rh.init(project_db)
	if not has_db: abort(400, error)

	automatic_updates(project_db)
	m = config.Project_config.get_or_none()

	rh.close()
	if m is None:
		abort(400, 'Could not retrieve project configuration table.')
	else:
		if m.gis_version is not None and not import_gis.is_supported_version(m.gis_version, m.gis_type): #and not import_gis_legacy.is_supported_version(m.gis_version):
			gis_type = 'ArcSWAT+' if m.gis_type == 'arcgis' else 'QSWAT+'
			abort(400, 'This version of SWAT+ Editor does not support {gt} {uv}.'.format(gt=gis_type, uv=m.gis_version))

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

	automatic_updates(project_db)
	m = config.Project_config.get_or_none()
	if m is None:
		rh.close()
		abort(400, 'Could not retrieve project configuration table.')
	else:
		gis_type = 'GIS'
		if m.gis_type == 'qgis':
			gis_type = 'QSWAT+'
		elif m.gis_type == 'arcgis':
			gis_type = 'ArcSWAT+'

		gis_text = '' if m.gis_version is None else gis_type + ' ' + m.gis_version

		landuse_distrib = []
		if m.gis_version is not None:
			landuse_distrib = gis.Gis_hrus.select(fn.Lower(fn.Coalesce(gis.Gis_hrus.landuse, "none/barren")).alias('name'), fn.Sum(gis.Gis_hrus.arslp).alias('y')).group_by(gis.Gis_hrus.landuse)

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
	
def getFileCio():
	is_lte = False
	c = config.Project_config.get_or_none()
	if c is not None:
		is_lte = c.is_lte

	ignore = ['pcp_path', 'tmp_path', 'slr_path', 'hmd_path', 'wnd_path', 'out_path']
	classes = config.File_cio_classification.select().where(config.File_cio_classification.name.not_in(ignore)).order_by(config.File_cio_classification.id)
	files = config.File_cio.select().order_by(config.File_cio.order_in_class)
	query = prefetch(classes, files)

	classifications = fileio_config.File_cio('').get_classifications(is_lte)
	data = []
	ignore_files = []
	ignore_cio_files = []
	custom_cio_files = []
	for row in query:
		item = {}
		item['category'] = row.name
		conditions = classifications.get(row.name, {})
		item_files = []
		for f in row.files:
			avail = conditions.get(f.order_in_class, False)
			item_files.append({ 'name': f.file_name, 'available': avail})
			if f.customization == FILE_CIO_USER_PROVIDED and avail:
				ignore_files.append(f.file_name)
			elif f.customization == FILE_CIO_USER_PROVIDED and not avail:
				custom_cio_files.append(f.file_name)
			elif f.customization == FILE_CIO_NONE:
				ignore_cio_files.append(f.file_name)
		item['files'] = item_files
		data.append(item)
	return {
		'data': data,
		'ignore_files': ignore_files,
		'ignore_cio_files': ignore_cio_files,
		'custom_cio_files': custom_cio_files
	}

@bp.route('/run-settings', methods=['GET'])
def getRunSettings():
	project_db = request.headers.get(rh.PROJECT_DB)
	has_db,error = rh.init(project_db)
	if not has_db: abort(400, error)

	try:
		c = config.Project_config.get()
		conf = get_model_to_dict_dates(c, project_db)

		t = simulation.Time_sim.get_or_create_default()
		time =  model_to_dict(t)

		m = simulation.Print_prt.get()
		prt = model_to_dict(m, recurse=False)

		o = simulation.Print_prt_object.select()
		objects = [model_to_dict(v, recurse=False) for v in o]

		prt = {'prt': prt, 'objects': objects}

		cioSettings = getFileCio()

		model = {
			'config': conf,
			'time': time,
			'print': prt,
			'imported_weather': climate.Weather_sta_cli.select().count() > 0 and climate.Weather_wgn_cli.select().count() > 0,
			'has_observed_weather': climate.Weather_sta_cli.observed_count() > 0,
			'file_cio': cioSettings['data'],
			'inputs': {
				'ignore_files': cioSettings['ignore_files'],
				'ignore_cio_files': cioSettings['ignore_cio_files'],
				'custom_cio_files': cioSettings['custom_cio_files']
			}
		}

		rh.close()
		return model
	except config.Project_config.DoesNotExist:
		rh.close()
		abort(404, "Could not retrieve project configuration data.")
	except simulation.Print_prt.DoesNotExist:
		rh.close()
		abort(404, "Could not retrieve print_prt data.")

@bp.route('/run-settings', methods=['PUT'])
def putRunSettings():
	project_db = request.headers.get(rh.PROJECT_DB)
	has_db,error = rh.init(project_db)
	if not has_db: abort(400, error)

	args = request.json
	try:
		m = config.Project_config.get()			
		m.input_files_dir = utils.rel_path(project_db, args['input_files_dir'])
		result = m.save()

		time = args['time']
		result = simulation.Time_sim.update_and_exec(time['day_start'], time['yrc_start'], time['day_end'], time['yrc_end'], time['step'])

		prt = args['print']
		q = simulation.Print_prt.update(
			nyskip=prt['nyskip'],
			day_start=prt['day_start'],
			day_end=prt['day_end'],
			yrc_start=prt['yrc_start'],
			yrc_end=prt['yrc_end'],
			interval=prt['interval'],
			csvout=prt['csvout'],
			dbout=prt['dbout'],
			cdfout=prt['cdfout'],
			crop_yld=prt['crop_yld'],
			mgtout=prt['mgtout'],
			hydcon=prt['hydcon'],
			fdcout=prt['fdcout']
		)
		result = q.execute()

		prtObj = args['print_objects']
		if prtObj is not None:
			for o in prtObj:
				simulation.Print_prt_object.update(
					daily=o['daily'],
					monthly=o['monthly'],
					yearly=o['yearly'],
					avann=o['avann']
				).where(simulation.Print_prt_object.id == o['id']).execute()

		if 'inputs' in args:
			ignore_files = args['inputs']['ignore_files']
			ignore_cio_files = args['inputs']['ignore_cio_files']
			custom_cio_files = args['inputs']['custom_cio_files']
			config.File_cio.update(customization=FILE_CIO_DEFAULT).execute()
			config.File_cio.update(customization=FILE_CIO_USER_PROVIDED).where((config.File_cio.file_name.in_(ignore_files)) | (config.File_cio.file_name.in_(custom_cio_files))).execute()			
			config.File_cio.update(customization=FILE_CIO_NONE).where(config.File_cio.file_name.in_(ignore_cio_files)).execute()

		rh.close()
		if result > 0:
			return '',200

		abort(400, "Unable to update project configuration table.")
	except config.Project_config.DoesNotExist:
		rh.close()
		abort(404, "Could not retrieve project configuration data.")

@bp.route('/save-model-run', methods=['PUT'])
def putModelRun():
	project_db = request.headers.get(rh.PROJECT_DB)
	has_db,error = rh.init(project_db)
	if not has_db: abort(400, error)

	try:
		m = config.Project_config.get()
		m.swat_last_run = datetime.now()
		m.output_last_imported = None
		result = m.save()

		rh.close()
		if result > 0:
			return '',200

		abort(400, "Unable to update project configuration table.")
	except config.Project_config.DoesNotExist:
		rh.close()
		abort(404, "Could not retrieve project configuration data.")

@bp.route('/save-output-read', methods=['PUT'])
def putOutputRead():
	project_db = request.headers.get(rh.PROJECT_DB)
	has_db,error = rh.init(project_db)
	if not has_db: abort(400, error)

	try:
		m = config.Project_config.get()
		m.output_last_imported = datetime.now()
		result = m.save()

		rh.close()
		if result > 0:
			return '',200

		abort(400, "Unable to update project configuration table.")
	except config.Project_config.DoesNotExist:
		rh.close()
		abort(404, "Could not retrieve project configuration data.")

@bp.route('/swatplus-check', methods=['PUT'])
def putSwatplusCheck():
	project_db = request.headers.get(rh.PROJECT_DB)
	has_db,error = rh.init(project_db)
	if not has_db: abort(400, error)

	args = request.json
	if 'output_db' not in args: abort(400, 'Output database file was omitted from the request.')

	api = GetSwatplusCheck(project_db, args['output_db'])
	return api.get(), 200

"""
Helper functions
"""

def automatic_updates(project_db):
	#Remove duplicate print objects
	try:
		subq = (simulation.Print_prt_object.select(fn.MIN(simulation.Print_prt_object.id).alias('min_id')).group_by(simulation.Print_prt_object.name))
		(simulation.Print_prt_object.delete().where(simulation.Print_prt_object.id.not_in(subq)).execute())
	except:
		pass

	conn = lib.open_db(project_db)

	if lib.exists_table(conn, 'project_config'):
		config_cols = lib.get_column_names(conn, 'project_config')
		col_names = [v['name'] for v in config_cols]
		if 'netcdf_data_file' not in col_names:
			migrator = SqliteMigrator(SqliteDatabase(project_db))
			migrate(
				migrator.add_column('project_config', 'netcdf_data_file', TextField(null=True)),
			)
		if 'use_gwflow' not in col_names:
			migrator = SqliteMigrator(SqliteDatabase(project_db))
			migrate(
				migrator.add_column('project_config', 'use_gwflow', BooleanField(default=False)),
			)
		if 'output_last_imported' not in col_names:
			migrator = SqliteMigrator(SqliteDatabase(project_db))
			migrate(
				migrator.add_column('project_config', 'output_last_imported', DateTimeField(null=True)),
				migrator.add_column('project_config', 'imported_gis', BooleanField(default=False)),
				migrator.add_column('project_config', 'is_lte', BooleanField(default=False)),
			)

			if lib.exists_table(conn, 'plants_plt'):
				lib.delete_table(project_db, 'plants_plt')
	
	if lib.exists_table(conn, 'codes_bsn'):
		m = config.Project_config.get_or_none()
		if m is not None and (m.editor_version == '3.0.0' or m.editor_version == '3.0.1'):
			cb = basin.Codes_bsn.get_or_none()
			if cb is not None and cb.i_fpwet == 2:
				basin.Codes_bsn.update({basin.Codes_bsn.i_fpwet: 1}).execute()
				config.Project_config.update({config.Project_config.editor_version: '3.0.2'}).execute()

	if lib.exists_table(conn, 'file_cio'):
		config_cols = lib.get_column_names(conn, 'file_cio')
		col_names = [v['name'] for v in config_cols]
		if 'customization' not in col_names:
			migrator = SqliteMigrator(SqliteDatabase(project_db))
			migrate(
				migrator.add_column('file_cio', 'customization', IntegerField(default=0)),
			)

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