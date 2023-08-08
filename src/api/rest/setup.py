from flask import Blueprint, jsonify, request, abort
from .config import RequestHeaders as rh

from playhouse.shortcuts import model_to_dict
from playhouse.migrate import *

from database.project.config import Project_config
from database import lib

from helpers import utils
from datetime import datetime

bp = Blueprint('setup', __name__, url_prefix='/setup')

@bp.route('/config', methods=['GET'])
def default():
	project_db = request.headers.get(rh.PROJECT_DB)
	has_db,error = rh.init(project_db)
	if not has_db: abort(400, error)

	check_config(project_db)
	m = Project_config.get_or_none()

	rh.close()
	if m is None:
		abort(400, 'Could not retrieve project configuration table.')
	else:
		return jsonify(get_model_to_dict_dates(m, project_db))


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