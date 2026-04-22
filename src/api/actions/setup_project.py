from helpers.executable_api import ExecutableApi, Unbuffered
from helpers import utils
from database import lib
from database.project import base as project_base
from database.project.config import Project_config
from database.project.setup import SetupProjectDatabase
from database.datasets.setup import SetupDatasetsDatabase
from database.datasets.definitions import Version
from database.project.hru_parm_db import Plants_plt as project_plants
from database.datasets.hru_parm_db import Plants_plt as dataset_plants
from database.project import simulation, basin
from .import_gis import GisImport
from . import update_project, update_datasets

import sys
import argparse
import os, os.path
import json
from shutil import copyfile
import time
from playhouse.migrate import *

OVERWRITE_PLANTS = False

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
				migrator.add_column('project_config', 'netcdf_data_file', CharField(null=True)),
			)
		if 'swat_exe_filename' not in col_names:
			migrator = SqliteMigrator(SqliteDatabase(project_db))
			migrate(
				migrator.add_column('project_config', 'swat_exe_filename', CharField(null=True)),
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
		m = Project_config.get_or_none()
		if m is not None and (m.editor_version == '3.0.0' or m.editor_version == '3.0.1'):
			cb = basin.Codes_bsn.get_or_none()
			if cb is not None and cb.i_fpwet == 2:
				basin.Codes_bsn.update({basin.Codes_bsn.i_fpwet: 1}).execute()
				Project_config.update({Project_config.editor_version: '3.0.2'}).execute()

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

class SetupProject(ExecutableApi):
	def __init__(self, project_db, editor_version, project_name=None, datasets_db=None, constant_ps=True, is_lte=False, project_description=None, copy_datasets_db=False):
		self.__abort = False

		automatic_updates(project_db)

		base_path = os.path.dirname(project_db)
		rel_project_db = os.path.relpath(project_db, base_path)

		if copy_datasets_db and datasets_db is not None:
			src_datasets_db_path = os.path.dirname(datasets_db)
			if base_path != src_datasets_db_path:
				rel_datasets_db = os.path.relpath(datasets_db, src_datasets_db_path)
				new_datasets_db = os.path.join(base_path, rel_datasets_db)
				copyfile(datasets_db, new_datasets_db)
				datasets_db = new_datasets_db

		if datasets_db is None:
			conn = lib.open_db(project_db)
			if not lib.exists_table(conn, 'project_config'):
				sys.exit('No datasets database provided and the project_config table in your project database does not exist. Please provide either a datasets database file or an existing project database.')
			conn.close()

			SetupProjectDatabase.init(project_db)
			try:
				config = Project_config.get()
				datasets_db = utils.full_path(project_db, config.reference_db)
				if project_name is None:
					project_name = config.project_name
			except Project_config.DoesNotExist:
				sys.exit('Could not retrieve project configuration data.')

		rel_datasets_db = os.path.relpath(datasets_db, base_path)

		ver_check = SetupDatasetsDatabase.check_version(datasets_db, editor_version)
		if ver_check is not None:
			sys.exit(ver_check)

		# Backup original db before beginning
		do_gis = False
		if os.path.exists(project_db):
			do_gis = True
			try:
				self.emit_progress(2, 'Backing up GIS database...')
				filename, file_extension = os.path.splitext(rel_project_db)
				bak_filename = filename + '_bak_' + time.strftime('%Y%m%d-%H%M%S') + file_extension
				bak_dir = os.path.join(base_path, 'DatabaseBackups')
				if not os.path.exists(bak_dir):
					os.makedirs(bak_dir)
				backup_db_file = os.path.join(bak_dir, bak_filename)
				copyfile(project_db, backup_db_file)
			except IOError as err:
				sys.exit(err)

		try:
			SetupProjectDatabase.init(project_db, datasets_db)
			self.emit_progress(10, 'Creating database tables...')
			SetupProjectDatabase.create_tables()
			self.emit_progress(50, 'Copying data from SWAT+ datasets database...')
			description = project_description if project_description is not None and project_description != 'null' else project_name
			SetupProjectDatabase.initialize_data(description, is_lte, overwrite_plants=OVERWRITE_PLANTS)

			# Run updates if needed
			SetupDatasetsDatabase.init(datasets_db)
			version = Version.get_or_none()
			if version is not None and update_datasets.available_to_update(version.value):
				update_datasets.UpdateDatasets(editor_version, datasets_db)

			existing_config = Project_config.get_or_none()
			if existing_config is not None and existing_config.editor_version is not None and update_project.available_to_update(existing_config.editor_version):
				update_project.UpdateProject(project_db, editor_version, update_project_values=True)

			config = Project_config.get_or_create_default(
				editor_version=editor_version,
				project_name=project_name,
				project_db=rel_project_db,
				reference_db=rel_datasets_db,
				project_directory='',
				is_lte=is_lte
			)

			conn = lib.open_db(project_db)
			plant_cols = lib.get_column_names(conn, 'plants_plt')
			plant_col_names = [v['name'] for v in plant_cols]
			conn.close()
			
			if 'days_mat' not in plant_col_names:
				migrator = SqliteMigrator(SqliteDatabase(project_db))
				migrate(
					migrator.rename_column('plants_plt', 'plnt_hu', 'days_mat')
				)
				for p in project_plants:
					dp = dataset_plants.get_or_none(dataset_plants.name == p.name)
					if dp is not None:
						p.days_mat = dp.days_mat
					else:
						p.days_mat = 0
					p.save()
		except Exception as ex:
			if backup_db_file is not None:
				self.emit_progress(50, "Error occurred. Rolling back database...")
				SetupProjectDatabase.rollback(project_db, backup_db_file)
				self.emit_progress(100, "Error occurred.")
			sys.exit(str(ex))

		if do_gis:
			api = GisImport(project_db, True, constant_ps, backup_db_file)
			api.insert_default()
	
	def __del__(self):
		SetupProjectDatabase.close()
		SetupDatasetsDatabase.close()


if __name__ == '__main__':
	sys.stdout = Unbuffered(sys.stdout)
	parser = argparse.ArgumentParser(description="Set up SWAT+ project database")
	parser.add_argument("--project_db_file", type=str, help="full path of project SQLite database file", nargs="?")
	parser.add_argument("--project_name", type=str, help="project name", nargs="?")
	parser.add_argument("--editor_version", type=str, help="editor version", nargs="?")
	parser.add_argument("--datasets_db_file", type=str, help="full path of datasets SQLite database file", nargs="?")
	parser.add_argument("--constant_ps", type=str, help="y/n constant point source values (default n)", nargs="?")
	parser.add_argument("--is_lte", type=str, help="y/n use lte version of SWAT+ (default n)", nargs="?")
	parser.add_argument("--project_description", type=str, help="project name", nargs="?")
	parser.add_argument("--copy_datasets_db", type=str, help="y/n copy datasets sqlite to project folder (default n)", nargs="?")

	args = parser.parse_args()

	constant_ps = True if args.constant_ps == "y" else False
	is_lte = True if args.is_lte == "y" else False
	copy_datasets_db = True if args.copy_datasets_db == "y" else False

	api = SetupProject(args.project_db_file, args.editor_version, args.project_name, args.datasets_db_file, constant_ps, is_lte, args.project_description, copy_datasets_db)
