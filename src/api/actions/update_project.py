from helpers.executable_api import ExecutableApi, Unbuffered
from helpers import utils
from database import lib
from database.project import base, init, dr, channel, reservoir, simulation, hru, lum, exco, connect, routing_unit, recall, change, soils, aquifer, hru_parm_db, decision_table, ops, basin, water_rights, salts
from database.project.config import Project_config, File_cio
from database.project.setup import SetupProjectDatabase
from database.datasets.setup import SetupDatasetsDatabase

from database.datasets.hru_parm_db import Plants_plt as dataset_plants
from database.datasets.definitions import File_cio as dataset_file_cio, Var_range, Version, Print_prt as dataset_print_prt, Print_prt_object as dataset_print_prt_object
from database.datasets import change as datasets_change, init as datasets_init, lum as datasets_lum, basin as datasets_basin, ops as datasets_ops, decision_table as datasets_decision_table, hru_parm_db as datasets_hru_parm_db, base as datasets_base
from actions.import_gis import GisImport

from .reimport_gis import ReimportGis

import sys
import argparse
import os, os.path
from shutil import copyfile
import time
from peewee import *
from playhouse.migrate import *
import datetime

available_to_update = [
	'2.3',
	'2.2',
	'2.1',
	'2.0',
	'1.4',
	'1.3',
	'1.2',
	'1.1',
	'1.0'
]


class UpdateProject(ExecutableApi):
	def __init__(self, project_db, new_version, datasets_db=None, update_project_values=False, reimport_gis=False):
		SetupProjectDatabase.init(project_db)
		try:
			m = self.check_config(new_version)

			base_path = os.path.dirname(project_db)
			rel_project_db = os.path.relpath(project_db, base_path)

			if datasets_db is None:
				datasets_db = utils.full_path(project_db, m.reference_db)
			else:				
				rel_datasets_db = os.path.relpath(datasets_db, base_path)
				m.reference_db = rel_datasets_db

			# Ensure correct version of datasets db
			ver_check = SetupDatasetsDatabase.check_version(datasets_db, new_version, True)
			if ver_check is not None:
				sys.exit(ver_check)

			# Backup original db before beginning
			try:
				self.emit_progress(2, 'Backing up project database...')
				filename, file_extension = os.path.splitext(rel_project_db)
				bak_filename = filename + '_v' + m.editor_version.replace('.', '_') + '_' + time.strftime('%Y%m%d-%H%M%S') + file_extension
				bak_dir = os.path.join(base_path, 'DatabaseBackups')
				if not os.path.exists(bak_dir):
					os.makedirs(bak_dir)
				backup_db_file = os.path.join(bak_dir, bak_filename)
				copyfile(project_db, os.path.join(bak_dir, bak_filename))
			except IOError as err:
				sys.exit(err)
			
			did_update = False
			if m.editor_version.startswith('2.3.'):
				self.updates_for_3_0_0(project_db, datasets_db, backup_db_file)
				did_update = True
				reimport_gis = False
			elif m.editor_version.startswith('2.1.') or m.editor_version.startswith('2.2.'):
				self.updates_for_2_3_0(project_db, datasets_db, backup_db_file)
				self.updates_for_3_0_0(project_db, datasets_db, backup_db_file)
				did_update = True
				reimport_gis = False
			elif m.editor_version.startswith('2.0.'):
				self.updates_for_2_1_0(project_db, datasets_db, backup_db_file)
				self.updates_for_2_3_0(project_db, datasets_db, backup_db_file)
				self.updates_for_3_0_0(project_db, datasets_db, backup_db_file)
				did_update = True
				reimport_gis = False
			elif m.editor_version == '1.3.0' or m.editor_version == '1.4.0':
				self.updates_for_2_0_0(project_db, datasets_db, backup_db_file)
				self.updates_for_2_1_0(project_db, datasets_db, backup_db_file)
				self.updates_for_2_3_0(project_db, datasets_db, backup_db_file)
				self.updates_for_3_0_0(project_db, datasets_db, backup_db_file)
				did_update = True
				reimport_gis = False
			elif m.editor_version == '1.2.1' or m.editor_version == '1.2.2' or m.editor_version == '1.2.3':
				self.updates_for_1_3_0(project_db, datasets_db, backup_db_file)
				self.updates_for_2_0_0(project_db, datasets_db, backup_db_file)
				self.updates_for_2_1_0(project_db, datasets_db, backup_db_file)
				self.updates_for_2_3_0(project_db, datasets_db, backup_db_file)
				self.updates_for_3_0_0(project_db, datasets_db, backup_db_file)
				did_update = True
				reimport_gis = False
			elif m.editor_version == '1.2.0':
				self.updates_for_1_2_1(project_db, backup_db_file)
				self.updates_for_1_3_0(project_db, datasets_db, backup_db_file)
				self.updates_for_2_0_0(project_db, datasets_db, backup_db_file)
				self.updates_for_2_1_0(project_db, datasets_db, backup_db_file)
				self.updates_for_2_3_0(project_db, datasets_db, backup_db_file)
				self.updates_for_3_0_0(project_db, datasets_db, backup_db_file)
				did_update = True
				reimport_gis = False
			elif m.editor_version == '1.1.0' or m.editor_version == '1.1.1' or m.editor_version == '1.1.2':
				self.updates_for_1_2_0(project_db, update_project_values, backup_db_file)
				self.updates_for_1_2_1(project_db, backup_db_file)
				self.updates_for_1_3_0(project_db, datasets_db, backup_db_file)
				self.updates_for_2_0_0(project_db, datasets_db, backup_db_file)
				self.updates_for_2_1_0(project_db, datasets_db, backup_db_file)
				self.updates_for_2_3_0(project_db, datasets_db, backup_db_file)
				self.updates_for_3_0_0(project_db, datasets_db, backup_db_file)
				did_update = True
			elif m.editor_version == '1.0.0':
				self.updates_for_1_1_0(project_db, datasets_db, backup_db_file)
				self.updates_for_1_2_0(project_db, update_project_values, backup_db_file)
				self.updates_for_1_2_1(project_db, backup_db_file)
				self.updates_for_1_3_0(project_db, datasets_db, backup_db_file)
				self.updates_for_2_0_0(project_db, datasets_db, backup_db_file)
				self.updates_for_2_1_0(project_db, datasets_db, backup_db_file)
				self.updates_for_2_3_0(project_db, datasets_db, backup_db_file)
				self.updates_for_3_0_0(project_db, datasets_db, backup_db_file)
				did_update = True
			
			m.editor_version = new_version
			result = m.save()

			if did_update and reimport_gis:
				ReimportGis(project_db, new_version, m.project_name, datasets_db, False, m.is_lte)
		except Project_config.DoesNotExist:
			sys.exit("Could not retrieve project configuration data.")

	def check_config(self, new_version):
		m = Project_config.get()
		if m.editor_version[:3] not in available_to_update:
			sys.exit("Unable to update this project to {new_version}. Updates from {current_version} unavailable.".format(new_version=new_version, current_version=m.editor_version))
			
		return m
	
	def updates_for_3_0_0(self, project_db, datasets_db, rollback_db):
		try:
			self.emit_progress(3, 'Creating salinity tables...')
			"""migrator = SqliteMigrator(SqliteDatabase(project_db))
			migrate(
				#migrator.drop_foreign_key_constraint('initial_aqu', 'salt_id'),
				migrator.drop_column('initial_aqu', 'salt_id'),
				#migrator.drop_foreign_key_constraint('initial_cha', 'salt_id'),
				migrator.drop_column('initial_cha', 'salt_id'),
				#migrator.drop_foreign_key_constraint('initial_res', 'salt_id'),
				migrator.drop_column('initial_res', 'salt_id'),
				#migrator.drop_foreign_key_constraint('soil_plant_ini', 'salt_id'),
				migrator.drop_column('soil_plant_ini', 'salt_id'),
			)"""

			#base.db.drop_tables([init.Salt_hru_ini_item, init.Salt_hru_ini, init.Salt_water_ini_item, init.Salt_water_ini])
			base.db.create_tables([salts.Salt_recall_rec, 
						  salts.Salt_recall_dat,
						  salts.Salt_atmo_cli,
						  salts.Salt_road,
						  salts.Salt_fertilizer_frt,
						  salts.Salt_urban,
						  salts.Salt_plants_flags,
						  salts.Salt_plants,
						  salts.Salt_irrigation,
						  salts.Salt_aqu_ini,
						  salts.Salt_channel_ini,
						  salts.Salt_res_ini,
						  salts.Salt_hru_ini_cs,
						  salts.Salt_module])

			self.emit_progress(5, 'Running migrations...')
			migrator = SqliteMigrator(SqliteDatabase(project_db))
			migrate(
				migrator.add_column('codes_bsn', 'gwflow', IntegerField(default=0)),
				migrator.add_column('pesticide_pst', 'pl_uptake', DoubleField(default=0.01)),
				migrator.rename_column('hyd_sed_lte_cha', 'bed_load', 'bankfull_flo'),
				migrator.rename_column('weather_sta_cli', 'wnd_dir', 'pet'),

				migrator.add_column('initial_aqu', 'salt_cs_id', ForeignKeyField(salts.Salt_aqu_ini, salts.Salt_aqu_ini.id, on_delete='SET NULL', null=True)),
				migrator.add_column('initial_cha', 'salt_cs_id', ForeignKeyField(salts.Salt_channel_ini, salts.Salt_channel_ini.id, on_delete='SET NULL', null=True)),
				migrator.add_column('initial_res', 'salt_cs_id', ForeignKeyField(salts.Salt_res_ini, salts.Salt_res_ini.id, on_delete='SET NULL', null=True)),
				migrator.add_column('soil_plant_ini', 'salt_cs_id', ForeignKeyField(salts.Salt_hru_ini_cs, salts.Salt_hru_ini_cs.id, on_delete='SET NULL', null=True)),
			)

			#Datasets DB - Ignore error if already done
			try:
				dsmigrator = SqliteMigrator(SqliteDatabase(datasets_db))
				migrate(
					dsmigrator.add_column('codes_bsn', 'gwflow', IntegerField(default=0)),
					dsmigrator.add_column('pesticide_pst', 'pl_uptake', DoubleField(default=0.01)),
				)
			except Exception:
				pass

			self.emit_progress(15, 'Updating database with new defaults...')

			File_cio.update({File_cio.file_name: 'pet.cli'}).where(File_cio.file_name == 'wind-dir.cli').execute()
			File_cio.update({File_cio.file_name: 'gwflow.con'}).where(File_cio.file_name == 'modflow.con').execute()
			File_cio.update({File_cio.file_name: 'pesticide.pst'}).where(File_cio.file_name == 'pesticide.pes').execute()
			dataset_file_cio.update({dataset_file_cio.default_file_name: 'pet.cli'}).where(dataset_file_cio.default_file_name == 'wind-dir.cli').execute()
			dataset_file_cio.update({dataset_file_cio.default_file_name: 'gwflow.con'}).where(dataset_file_cio.default_file_name == 'modflow.con').execute()
			dataset_file_cio.update({dataset_file_cio.default_file_name: 'pesticide.pst'}).where(dataset_file_cio.default_file_name == 'pesticide.pes').execute()

			hru_parm_db.Pesticide_pst.update({hru_parm_db.Pesticide_pst.aq_hlife: 142.85, hru_parm_db.Pesticide_pst.ben_hlife: 20}).execute()
			datasets_hru_parm_db.Pesticide_pst.update({datasets_hru_parm_db.Pesticide_pst.aq_hlife: 142.85, datasets_hru_parm_db.Pesticide_pst.ben_hlife: 20}).execute()

			basin.Codes_bsn.update({basin.Codes_bsn.i_fpwet: 1}).execute()
			datasets_basin.Codes_bsn.update({datasets_basin.Codes_bsn.i_fpwet: 1}).execute()

			self.plant_value_updates_for_3_0_0(hru_parm_db.Plants_plt)
			self.plant_value_updates_for_3_0_0(datasets_hru_parm_db.Plants_plt)

			self.cal_parms_value_updates_for_3_0_0(change.Cal_parms_cal)
			self.cal_parms_value_updates_for_3_0_0(datasets_change.Cal_parms_cal)

			new_print_prt = [
				{ 'name': 'basin_salt', 'daily': 0, 'monthly': 0, 'yearly': 0, 'avann': 0 },
				{ 'name': 'hru_salt', 'daily': 0, 'monthly': 0, 'yearly': 0, 'avann': 0 },
				{ 'name': 'ru_salt', 'daily': 0, 'monthly': 0, 'yearly': 0, 'avann': 0 },
				{ 'name': 'aqu_salt', 'daily': 0, 'monthly': 0, 'yearly': 0, 'avann': 0 },
				{ 'name': 'channel_salt', 'daily': 0, 'monthly': 0, 'yearly': 0, 'avann': 0 },
				{ 'name': 'res_salt', 'daily': 0, 'monthly': 0, 'yearly': 0, 'avann': 0 },
				{ 'name': 'wetland_salt', 'daily': 0, 'monthly': 0, 'yearly': 0, 'avann': 0 },
				{ 'name': 'basin_cs', 'daily': 0, 'monthly': 0, 'yearly': 0, 'avann': 0 },
				{ 'name': 'hru_cs', 'daily': 0, 'monthly': 0, 'yearly': 0, 'avann': 0 },
				{ 'name': 'ru_cs', 'daily': 0, 'monthly': 0, 'yearly': 0, 'avann': 0 },
				{ 'name': 'aqu_cs', 'daily': 0, 'monthly': 0, 'yearly': 0, 'avann': 0 },
				{ 'name': 'channel_cs', 'daily': 0, 'monthly': 0, 'yearly': 0, 'avann': 0 },
				{ 'name': 'res_cs', 'daily': 0, 'monthly': 0, 'yearly': 0, 'avann': 0 },
				{ 'name': 'wetland_cs', 'daily': 0, 'monthly': 0, 'yearly': 0, 'avann': 0 },
			]
			new_print_project = []
			for p in new_print_prt:
				new_print_project.append({
					'name': p['name'],
					'daily': p['daily'],
					'monthly': p['monthly'],
					'yearly': p['yearly'],
					'avann': p['avann'],
					'print_prt_id': 1
				})
			lib.bulk_insert(base.db, simulation.Print_prt_object, new_print_project)
			lib.bulk_insert(datasets_base.db, dataset_print_prt_object, new_print_prt)

			#decision table changes
			decision_table.D_table_dtl_act.update({decision_table.D_table_dtl_act.fp: 'grain'}).where(decision_table.D_table_dtl_act.act_typ == 'harvest_kill').execute()
			datasets_decision_table.D_table_dtl_act.update({datasets_decision_table.D_table_dtl_act.fp: 'grain'}).where(datasets_decision_table.D_table_dtl_act.act_typ == 'harvest_kill').execute()
			
			Version.update({Version.value: '3.0.0', Version.release_date: datetime.datetime.now()}).execute()
			
		except Exception as ex:
			if rollback_db is not None:
				self.emit_progress(50, "Error occurred. Rolling back database...")
				SetupProjectDatabase.rollback(project_db, rollback_db)
				self.emit_progress(100, "Error occurred.")
			sys.exit(str(ex))

	def plant_value_updates_for_3_0_0(self, table):
		all_rice = ['rice', 'rice120', 'rice140', 'rice160', 'rice180']
		table.update({table.days_mat: 130}).where(table.name == 'rice').execute()
		table.update({
				table.bm_e: 26, 
				table.lai_max1: 0.15, 
				table.frac_hu2: 0.5, 
				table.hu_lai_decl: 0.8, 
				table.dlai_rate: 0.1
			}).where(table.name.in_(all_rice)).execute()
		
		table.update({table.ext_co: 1}).where(table.name == 'berm').execute()
		table.update({table.ext_co: 0.8}).where(table.name == 'bsvg').execute()
		table.update({table.ext_co: 1.1}).where(table.name == 'blug').execute()
		table.update({table.ext_co: 0.85}).where(table.name == 'crdy').execute()
		table.update({table.ext_co: 0.85}).where(table.name == 'crgr').execute()
		table.update({table.ext_co: 0.85}).where(table.name == 'crir').execute()
		table.update({table.ext_co: 0.83}).where(table.name == 'crwo').execute()
		table.update({table.ext_co: 0.83}).where(table.name == 'fodb').execute()
		table.update({table.ext_co: 0.83}).where(table.name == 'fodn').execute()
		table.update({table.ext_co: 0.77}).where(table.name == 'foeb').execute()
		table.update({table.ext_co: 0.77}).where(table.name == 'foen').execute()
		table.update({table.ext_co: 0.79}).where(table.name == 'fomi').execute()
		table.update({table.ext_co: 0.84, table.bm_dieoff: 1}).where(table.name == 'gras').execute()
		table.update({table.ext_co: 0.82, table.bm_dieoff: 1}).where(table.name == 'migs').execute()
		table.update({table.ext_co: 0.82}).where(table.name == 'sava').execute()
		table.update({table.ext_co: 1}).where(table.name == 'sept').execute()
		table.update({table.ext_co: 1.12}).where(table.name == 'side').execute()
		table.update({table.ext_co: 0.79}).where(table.name == 'tubg').execute()
		table.update({table.ext_co: 0.79}).where(table.name == 'tumi').execute()
		table.update({table.ext_co: 0.79}).where(table.name == 'tuwo').execute()
		table.update({table.ext_co: 1}).where(table.name == 'urbn_warm').execute()

		table.update({table.bm_dieoff: 1}).where(table.name.in_(['fesc', 'hay', 'indn', 'jhgr', 'lbls', 'past', 'rnge', 'rnge_sudrf', 'rnge_suds', 'rnge_suhf', 'rnge_sums', 'rnge_sust', 'rnge_tecf', 'rnge_teds', 'rnge_tems', 'rnge_teof', 'rnge_test', 'ryea', 'ryeg', 'ryer', 'sava', 'sghy', 'side', 'spas', 'swch', 'swgr', 'teff', 'timo'])).execute()

		all_fracs = ['euca', 'fodb', 'fodn', 'foeb', 'foen', 'fomi', 'frsd', 'frsd_suhf', 'frsd_sums', 'frsd_sust', 'frsd_tecf', 'frsd_tems', 'frsd_teof', 'frsd_test', 'frse', 'frse_sudrf', 'frse_suds', 'frse_suhf', 'frse_sums', 'frse_sust', 'frse_tecf', 'frse_teds', 'frse_tems', 'frse_teof', 'frse_test', 'frst', 'frst_suhf', 'frst_sums', 'frst_sust', 'frst_tecf', 'frst_tems', 'frst_teof', 'frst_test', 'oilp', 'oliv', 'oran', 'orcd', 'pine', 'wetf', 'wewo', 'will', 'wspr']
		table.update({
			table.frac_n_em: 0.06,	
			table.frac_n_50: 0.02,	
			table.frac_n_mat: 0.015,	
			table.frac_p_em: 0.007,	
			table.frac_p_50:0.004,	
			table.frac_p_mat: 0.003
		}).where(table.name.in_(all_fracs)).execute()

	def name_exists(self, table, name):
		return table.select().where(table.name == name).count() > 0
	
	def cal_parms_value_updates_for_3_0_0(self, table):
		if not self.name_exists(table, 'nperco_lchtile'): table.insert(name='nperco_lchtile', obj_typ='bsn', abs_min=0, abs_max=1, units=None).execute()
		table.delete().where(table.name == 'spcon').execute()
		table.delete().where(table.name == 'spexp').execute()
		table.update({
				table.name: 'bankfull_flo',
				table.abs_min: 0.5,
				table.abs_max: 1.5,
				table.units: 'fraction'
			}).where(table.name == 'bedldcoef').execute()
		table.update({
				table.name: 'flood_sedfrac',
				table.abs_min: 0.1,
				table.abs_max: 0.9,
				table.units: 'fraction'
			}).where(table.name == 'chseq').execute()
		
		table.update({ table.abs_min: 0.00001 }).where(table.name == 'd50').execute()
		table.update({ table.abs_min: 0.8, table.abs_max: 1.2 }).where(table.name == 'petco').execute()	
		table.update({ table.abs_max: 400 }).where(table.name == 'phoskd').execute()		
		table.update({ table.abs_min: 5, table.abs_max: 20 }).where(table.name == 'pperco').execute()
		table.update({ table.abs_max: 11000000 }).where(table.name == 'pst_solub').execute()
		table.update({ table.abs_max: 0.5 }).where(table.name == 'rs2').execute()
		table.update({ table.abs_max: 2 }).where(table.name == 'rs3').execute()
		table.update({ table.name: 'withdraw_rate' }).where(table.name == 'withdrawal_rate').execute()
		if not self.name_exists(table, 'arc_len_fr'): table.insert(name='arc_len_fr', obj_typ='rte', abs_min=0.5, abs_max=2, units='frac').execute()
		if not self.name_exists(table, 'ch_n_conc'): table.insert(name='ch_n_conc', obj_typ='rte', abs_min=0, abs_max=500, units='mg/kg').execute()
		if not self.name_exists(table, 'ch_p_bio'): table.insert(name='ch_p_bio', obj_typ='rte', abs_min=0, abs_max=1, units='frac').execute()
		if not self.name_exists(table, 'ch_p_conc'): table.insert(name='ch_p_conc', obj_typ='rte', abs_min=0, abs_max=50.9, units='mg/kg').execute()
		if not self.name_exists(table, 'fp_inun_days'): table.insert(name='fp_inun_days', obj_typ='rte', abs_min=0.05, abs_max=30, units='days').execute()
		if not self.name_exists(table, 'hum_c_n'): table.insert(name='hum_c_n', obj_typ='sol', abs_min=0, abs_max=20, units='mg/kg').execute()
		if not self.name_exists(table, 'hum_c_p'): table.insert(name='hum_c_p', obj_typ='sol', abs_min=0, abs_max=160, units='mg/kg').execute()
		if not self.name_exists(table, 'lab_p'): table.insert(name='lab_p', obj_typ='sol', abs_min=0, abs_max=30, units='mg/kg').execute()
		if not self.name_exists(table, 'n_dep_enr'): table.insert(name='n_dep_enr', obj_typ='rte', abs_min=0.2, abs_max=1, units='frac').execute()
		if not self.name_exists(table, 'n_setl'): table.insert(name='n_setl', obj_typ='rte', abs_min=0.05, abs_max=0.9, units='frac').execute()
		if not self.name_exists(table, 'n_sol_part'): table.insert(name='n_sol_part', obj_typ='rte', abs_min=0.001, abs_max=0.1, units=None).execute()
		if not self.name_exists(table, 'p_dep_enr'): table.insert(name='p_dep_enr', obj_typ='rte', abs_min=0.2, abs_max=1, units='frac').execute()
		if not self.name_exists(table, 'p_setl'): table.insert(name='p_setl', obj_typ='rte', abs_min=0.05, abs_max=0.9, units='frac').execute()
		if not self.name_exists(table, 'p_sol_part'): table.insert(name='p_sol_part', obj_typ='rte', abs_min=0.001, abs_max=0.1, units=None).execute()
		if not self.name_exists(table, 'part_size'): table.insert(name='part_size', obj_typ='rte', abs_min=0.001, abs_max=0.01, units='mm').execute()
		if not self.name_exists(table, 'pk_rto'): table.insert(name='pk_rto', obj_typ='rte', abs_min=1, abs_max=3, units=None).execute()
		if not self.name_exists(table, 'sed_stlr'): table.insert(name='sed_stlr', obj_typ='res', abs_min=0.1, abs_max=2, units=None).execute()
		if not self.name_exists(table, 'velsetlr'): table.insert(name='velsetlr', obj_typ='res', abs_min=0.1, abs_max=15, units='m/day').execute()
		if not self.name_exists(table, 'wash_bed_fr'): table.insert(name='wash_bed_fr', obj_typ='rte', abs_min=0, abs_max=0.8, units='frac').execute()
		
		if not self.name_exists(table, 'aquifer_K'): table.insert(name='aquifer_K', obj_typ='gwf', abs_min=0.0001, abs_max=40, units='m/day').execute()
		if not self.name_exists(table, 'aquifer_Sy'): table.insert(name='aquifer_Sy', obj_typ='gwf', abs_min=0.001, abs_max=0.6, units='m3/m3').execute()
		if not self.name_exists(table, 'aquifer_delay'): table.insert(name='aquifer_delay', obj_typ='hru', abs_min=0, abs_max=1000, units='days').execute()
		if not self.name_exists(table, 'aquifer_exdp'): table.insert(name='aquifer_exdp', obj_typ='gwf', abs_min=0, abs_max=4, units='m').execute()
		if not self.name_exists(table, 'stream_K'): table.insert(name='stream_K', obj_typ='gwf_riv', abs_min=0.0000001, abs_max=0.01, units='m/day').execute()
		if not self.name_exists(table, 'stream_thk'): table.insert(name='stream_thk', obj_typ='gwf_riv', abs_min=0.01, abs_max=2, units='m').execute()
		if not self.name_exists(table, 'stream_bed'): table.insert(name='stream_bed', obj_typ='gwf_sgl', abs_min=0, abs_max=20, units='m').execute()
	
	def updates_for_2_3_0(self, project_db, datasets_db, rollback_db):
		try:
			self.emit_progress(5, 'Running migrations...')
			migrator = SqliteMigrator(SqliteDatabase(project_db))
			migrate(
				migrator.drop_column('weir_res', 'disch_co'),
				migrator.drop_column('weir_res', 'energy_co'),
				migrator.drop_column('weir_res', 'weir_wd'),
				migrator.drop_column('weir_res', 'vel_co'),
				migrator.drop_column('weir_res', 'dp_co'),
				migrator.drop_column('weir_res', 'num_steps'),
				migrator.add_column('weir_res', 'linear_c', DoubleField(default=1.84)),
				migrator.add_column('weir_res', 'exp_k', DoubleField(default=2.6)),
				migrator.add_column('weir_res', 'width', DoubleField(default=2.5)),
				migrator.add_column('weir_res', 'height', DoubleField(default=0.0)),

				migrator.rename_column('codes_bsn', 'rtu_wq', 'swift_out'),

				migrator.drop_column('print_prt', 'soilout'),
				migrator.add_column('print_prt', 'crop_yld', CharField(default='b')),

				migrator.drop_column('codes_sft', 'hyd_hru'),
				migrator.drop_column('codes_sft', 'hyd_hrulte'),
				migrator.add_column('codes_sft', 'landscape', BooleanField(default=False)),
				migrator.add_column('codes_sft', 'hyd', CharField(default='n')),

				migrator.drop_column('hyd_sed_lte_cha', 'wd_rto'),
				migrator.add_column('hyd_sed_lte_cha', 'sinu', DoubleField(default=1.05)),

				migrator.drop_column('hydrology_hyd', 'harg_pet'),
				migrator.add_column('hydrology_hyd', 'pet_co', DoubleField(default=1)),
			)

			#Plant columns may already have been updated during project open. Ignore if so
			try:
				migrator = SqliteMigrator(SqliteDatabase(project_db))
				migrate(
					migrator.rename_column('plants_plt', 'wnd_dead', 'rsd_pctcov'),
					migrator.rename_column('plants_plt', 'wnd_flat', 'rsd_covfac'),
				)
			except Exception:
				pass

			#Datasets DB - Ignore error if already done
			try:
				migrator = SqliteMigrator(SqliteDatabase(datasets_db))
				migrate(
					migrator.rename_column('codes_bsn', 'rtu_wq', 'swift_out'),

					migrator.drop_column('print_prt', 'soilout'),
					migrator.add_column('print_prt', 'crop_yld', CharField(default='b')),

					migrator.rename_column('plants_plt', 'wnd_dead', 'rsd_pctcov'),
					migrator.rename_column('plants_plt', 'wnd_flat', 'rsd_covfac'),
				)
			except Exception:
				pass

			self.emit_progress(10, 'Creating water allocation tables...')
			base.db.create_tables([water_rights.Water_allocation_wro, water_rights.Water_allocation_src_ob, water_rights.Water_allocation_dmd_ob, water_rights.Water_allocation_dmd_ob_src])

			self.emit_progress(15, 'Updating database with new defaults...')

			#file.cio changes
			File_cio.delete().where(File_cio.classification == 14).execute()
			File_cio.insert(classification=14, order_in_class=1, file_name='water_allocation.wro').execute()
			File_cio.insert(classification=14, order_in_class=2, file_name='define.wro').execute()
			File_cio.insert(classification=14, order_in_class=3, file_name='element.wro').execute()
			dataset_file_cio.delete().where(dataset_file_cio.classification == 14).execute()
			dataset_file_cio.insert(classification=14, order_in_class=1, database_table='water_allocation_wro', default_file_name='water_allocation.wro', is_core_file=False).execute()
			dataset_file_cio.insert(classification=14, order_in_class=2, database_table='define_wro', default_file_name='define.wro', is_core_file=False).execute()
			dataset_file_cio.insert(classification=14, order_in_class=3, database_table='element_wro', default_file_name='element.wro', is_core_file=False).execute()

			#print.prt changes
			simulation.Print_prt_object.update({simulation.Print_prt_object.name: 'water_allo'}).where(simulation.Print_prt_object.name == 'region_psc').execute()
			simulation.Print_prt_object.update({simulation.Print_prt_object.name: 'region_psc'}).where(simulation.Print_prt_object.name == 'region_sd_cha').execute()
			simulation.Print_prt_object.update({simulation.Print_prt_object.name: 'region_sd_cha'}).where(simulation.Print_prt_object.name == 'region_cha').execute()
			
			dataset_print_prt_object.update({dataset_print_prt_object.name: 'water_allo'}).where(dataset_print_prt_object.name == 'region_psc').execute()
			dataset_print_prt_object.update({dataset_print_prt_object.name: 'region_psc'}).where(dataset_print_prt_object.name == 'region_sd_cha').execute()
			dataset_print_prt_object.update({dataset_print_prt_object.name: 'region_sd_cha'}).where(dataset_print_prt_object.name == 'region_cha').execute()

			#cal_parms.cal changes
			change.Cal_parms_cal.delete().where((change.Cal_parms_cal.name == 'wd_rto') & (change.Cal_parms_cal.obj_typ == 'rte')).execute()
			change.Cal_parms_cal.update({change.Cal_parms_cal.abs_min: 0.7, change.Cal_parms_cal.abs_max: 1.3}).where(change.Cal_parms_cal.name == 'petco').execute()
			datasets_change.Cal_parms_cal.delete().where((datasets_change.Cal_parms_cal.name == 'wd_rto') & (datasets_change.Cal_parms_cal.obj_typ == 'rte')).execute()
			datasets_change.Cal_parms_cal.update({datasets_change.Cal_parms_cal.abs_min: 0.7, datasets_change.Cal_parms_cal.abs_max: 1.3}).where(datasets_change.Cal_parms_cal.name == 'petco').execute()

			new_cal_parms = [
				{ 'name': 'cbn_init', 'obj_typ': 'aqu', 'abs_min': 0, 'abs_max': 20, 'units': '%' },
				{ 'name': 'dep_bot', 'obj_typ': 'aqu', 'abs_min': 1, 'abs_max': 50, 'units': 'm' },
				{ 'name': 'dep_wt_init', 'obj_typ': 'aqu', 'abs_min': 0, 'abs_max': 50, 'units': 'm' },
				{ 'name': 'flo_dist', 'obj_typ': 'aqu', 'abs_min': 0, 'abs_max': 300, 'units': 'm' },
				{ 'name': 'flo_init_mm', 'obj_typ': 'aqu', 'abs_min': 0, 'abs_max': 5, 'units': 'mm' },
				{ 'name': 'hlife_n', 'obj_typ': 'aqu', 'abs_min': 0, 'abs_max': 365, 'units': 'days' },
				{ 'name': 'minp_init', 'obj_typ': 'aqu', 'abs_min': 0, 'abs_max': 10, 'units': 'kg' },
				{ 'name': 'no3_init', 'obj_typ': 'aqu', 'abs_min': 0, 'abs_max': 30, 'units': 'ppm' },
				{ 'name': 'phu_mat', 'obj_typ': 'plt', 'abs_min': 50, 'abs_max': 6000, 'units': 'deg_C' },
				{ 'name': 'lai_pot', 'obj_typ': 'plt', 'abs_min': 0.01, 'abs_max': 12, 'units': 'm/m' },
				{ 'name': 'harv_idx', 'obj_typ': 'plt', 'abs_min': 0.01, 'abs_max': 0.95, 'units': None },
				{ 'name': 'drawdown_days', 'obj_typ': 'rdt', 'abs_min': 0.05, 'abs_max': 5000, 'units': 'days' },
				{ 'name': 'withdrawal_rate', 'obj_typ': 'rdt', 'abs_min': 0, 'abs_max': 100000, 'units': 'm3/s' },
			]
			for cal_parm in new_cal_parms:
				cp = change.Cal_parms_cal.get_or_none((change.Cal_parms_cal.name == cal_parm['name']) & (change.Cal_parms_cal.obj_typ == cal_parm['obj_typ']))
				if cp is None:
					change.Cal_parms_cal.insert(name=cal_parm['name'], obj_typ=cal_parm['obj_typ'], abs_min=cal_parm['abs_min'], abs_max=cal_parm['abs_max'], units=cal_parm['units']).execute()

				ds_cp = datasets_change.Cal_parms_cal.get_or_none((datasets_change.Cal_parms_cal.name == cal_parm['name']) & (datasets_change.Cal_parms_cal.obj_typ == cal_parm['obj_typ']))
				if ds_cp is None:
					datasets_change.Cal_parms_cal.insert(name=cal_parm['name'], obj_typ=cal_parm['obj_typ'], abs_min=cal_parm['abs_min'], abs_max=cal_parm['abs_max'], units=cal_parm['units']).execute()

			new_harv_ops = [
				{ 'name': 'cotton_picker', 'harv_typ': 'grain', 'harv_idx': 0.05, 'harv_eff': 0.95, 'harv_bm_min': 0 },
				{ 'name': 'cotton_strip', 'harv_typ': 'grain', 'harv_idx': 0.05, 'harv_eff': 0.95, 'harv_bm_min': 0 }
			]
			for harv_op in new_harv_ops:
				ho = ops.Harv_ops.get_or_none(ops.Harv_ops.name == harv_op['name'])
				if ho is None:
					ops.Harv_ops.insert(name=harv_op['name'], harv_typ=harv_op['harv_typ'], harv_idx=harv_op['harv_idx'], harv_eff=harv_op['harv_eff'], harv_bm_min=harv_op['harv_bm_min'])
			
				ds_ho = datasets_ops.Harv_ops.get_or_none(datasets_ops.Harv_ops.name == harv_op['name'])
				if ds_ho is None:
					datasets_ops.Harv_ops.insert(name=harv_op['name'], harv_typ=harv_op['harv_typ'], harv_idx=harv_op['harv_idx'], harv_eff=harv_op['harv_eff'], harv_bm_min=harv_op['harv_bm_min'])
			
			Version.update({Version.value: '2.3.0', Version.release_date: datetime.datetime.now()}).execute()
			
		except Exception as ex:
			if rollback_db is not None:
				self.emit_progress(50, "Error occurred. Rolling back database...")
				SetupProjectDatabase.rollback(project_db, rollback_db)
				self.emit_progress(100, "Error occurred.")
			sys.exit(str(ex))

	def updates_for_2_1_0(self, project_db, datasets_db, rollback_db):
		try:
			self.emit_progress(5, 'Running migrations...')
			migrator = SqliteMigrator(SqliteDatabase(project_db))
			migrate(
				#migrator.add_column('project_config', 'project_description', CharField(null=True)),

				migrator.rename_column('codes_bsn', 'baseflo', 'lapse'),
				migrator.rename_column('codes_bsn', 'abstr_init', 'gampt'),
				migrator.rename_column('codes_bsn', 'headwater', 'i_fpwet'),

				migrator.rename_column('parameters_bsn', 'trans_loss', 'nperco_lchtile'),
				migrator.rename_column('parameters_bsn', 's_max', 'plaps'),
				migrator.rename_column('parameters_bsn', 'n_fix', 'tlaps'),
				migrator.rename_column('parameters_bsn', 'vel_crit', 'urb_init_abst'),
				migrator.rename_column('parameters_bsn', 'res_sed', 'petco_pmpt'),
				migrator.rename_column('parameters_bsn', 'cha_part_sd', 'co2'),
				migrator.rename_column('parameters_bsn', 'adj_cn', 'day_lag_max'),
				
				migrator.rename_column('hyd_sed_lte_cha', 't_conc', 'fps'),
				migrator.rename_column('hyd_sed_lte_cha', 'shear_bnk', 'fpn'),
				migrator.rename_column('hyd_sed_lte_cha', 'hc_erod', 'n_conc'),
				migrator.rename_column('hyd_sed_lte_cha', 'hc_ht', 'p_conc'),
				migrator.rename_column('hyd_sed_lte_cha', 'hc_len', 'p_bio'),
				
				migrator.rename_column('nutrients_sol', 'dp_co', 'exp_co'),
				migrator.rename_column('nutrients_sol', 'tot_n', 'lab_p'),
				migrator.rename_column('nutrients_sol', 'min_n', 'nitrate'),
				migrator.rename_column('nutrients_sol', 'org_n', 'fr_hum_act'),
				migrator.rename_column('nutrients_sol', 'tot_p', 'hum_c_n'),
				migrator.rename_column('nutrients_sol', 'min_p', 'hum_c_p'),
				migrator.rename_column('nutrients_sol', 'org_p', 'inorgp'),
				migrator.rename_column('nutrients_sol', 'sol_p', 'watersol_p'),
				migrator.rename_column('nutrients_sol', 'mehl_p', 'mehlich_p'),
				migrator.rename_column('nutrients_sol', 'bray_p', 'bray_strong_p'),
				
				migrator.rename_column('water_balance_sft_item', 'orgp', 'wyr'),
				migrator.rename_column('water_balance_sft_item', 'no3', 'bfr'),

				migrator.rename_column('recall_dat', 't_step', 'jday'),
				migrator.rename_column('recall_dat', 'ptl_n', 'orgn'),
				migrator.rename_column('recall_dat', 'ptl_p', 'sedp'),
				migrator.rename_column('recall_dat', 'no3_n', 'no3'),
				migrator.rename_column('recall_dat', 'sol_p', 'solp'),
				migrator.rename_column('recall_dat', 'nh3_n', 'nh3'),
				migrator.rename_column('recall_dat', 'no2_n', 'no2'),
				migrator.rename_column('recall_dat', 'cbn_bod', 'cbod'),
				migrator.rename_column('recall_dat', 'oxy', 'dox'),
				migrator.rename_column('recall_dat', 'sm_agg', 'sag'),
				migrator.rename_column('recall_dat', 'lg_agg', 'lag'),
				migrator.add_column('recall_dat', 'mo', IntegerField(default=1)),
				migrator.add_column('recall_dat', 'day_mo', IntegerField(default=1)),
				migrator.add_column('recall_dat', 'ob_typ', CharField(null=True)),
				migrator.add_column('recall_dat', 'ob_name', CharField(null=True)),

				migrator.add_column('management_sch_auto', 'plant1', CharField(null=True)),
				migrator.add_column('management_sch_auto', 'plant2', CharField(null=True)),

				migrator.add_column('d_table_dtl', 'description', CharField(null=True)),
				migrator.add_column('d_table_dtl_cond', 'description', CharField(null=True)),
			)

			try:
				migrator = SqliteMigrator(SqliteDatabase(project_db))
				migrate(
					migrator.rename_column('plants_plt', 'wnd_live', 'aeration')
				)
			except Exception:
				pass

			#Datasets DB - Ignore error if already done
			try:
				migrator = SqliteMigrator(SqliteDatabase(datasets_db))
				migrate(
					migrator.rename_column('codes_bsn', 'baseflo', 'lapse'),
					migrator.rename_column('codes_bsn', 'abstr_init', 'gampt'),
					migrator.rename_column('codes_bsn', 'headwater', 'i_fpwet'),

					migrator.rename_column('parameters_bsn', 'trans_loss', 'nperco_lchtile'),
					migrator.rename_column('parameters_bsn', 's_max', 'plaps'),
					migrator.rename_column('parameters_bsn', 'n_fix', 'tlaps'),
					migrator.rename_column('parameters_bsn', 'vel_crit', 'urb_init_abst'),
					migrator.rename_column('parameters_bsn', 'res_sed', 'petco_pmpt'),
					migrator.rename_column('parameters_bsn', 'cha_part_sd', 'co2'),
					migrator.rename_column('parameters_bsn', 'adj_cn', 'day_lag_max'),

					migrator.rename_column('plants_plt', 'wnd_live', 'aeration'),

					migrator.add_column('management_sch_auto', 'plant1', CharField(null=True)),
					migrator.add_column('management_sch_auto', 'plant2', CharField(null=True)),
					
					migrator.add_column('d_table_dtl', 'description', CharField(null=True)),
					migrator.add_column('d_table_dtl_cond', 'description', CharField(null=True)),
					migrator.alter_column_type('d_table_dtl_act', 'const', DoubleField())
				)
			except Exception:
				pass

			self.emit_progress(10, 'Updating database with new defaults...')

			basin.Parameters_bsn.update({
				basin.Parameters_bsn.nperco_lchtile: 0.5, 
				basin.Parameters_bsn.plaps: 0, 
				basin.Parameters_bsn.tlaps: 6.5, 
				basin.Parameters_bsn.urb_init_abst: 1, 
				basin.Parameters_bsn.petco_pmpt: 1, 
				basin.Parameters_bsn.co2: 400, 
				basin.Parameters_bsn.day_lag_max: 0, 
			}).execute()

			datasets_basin.Parameters_bsn.update({
				basin.Parameters_bsn.nperco_lchtile: 0.5, 
				basin.Parameters_bsn.plaps: 0, 
				basin.Parameters_bsn.tlaps: 6.5, 
				basin.Parameters_bsn.urb_init_abst: 1, 
				basin.Parameters_bsn.petco_pmpt: 1, 
				basin.Parameters_bsn.co2: 400, 
				basin.Parameters_bsn.day_lag_max: 0, 
			}).execute()

			channel.Hyd_sed_lte_cha.update({
				channel.Hyd_sed_lte_cha.fps: 0.00001,
				channel.Hyd_sed_lte_cha.fpn: 0.1,
				channel.Hyd_sed_lte_cha.n_conc: 0,
				channel.Hyd_sed_lte_cha.p_conc: 0,
				channel.Hyd_sed_lte_cha.p_bio: 0
			}).execute()

			soils.Nutrients_sol.update({
				soils.Nutrients_sol.exp_co: 0.0005,
				soils.Nutrients_sol.lab_p: 5,
				soils.Nutrients_sol.nitrate: 7,
				soils.Nutrients_sol.fr_hum_act: 0.02,
				soils.Nutrients_sol.hum_c_n: 10,
				soils.Nutrients_sol.hum_c_p: 80,
				soils.Nutrients_sol.inorgp: 3.5,
				soils.Nutrients_sol.watersol_p: 0.15,
				soils.Nutrients_sol.h3a_p: 0.25,
				soils.Nutrients_sol.mehlich_p: 1.2,
			}).execute()

			plaps = change.Cal_parms_cal.get_or_none((change.Cal_parms_cal.name == 'plaps') & (change.Cal_parms_cal.obj_typ == 'bsn'))
			if plaps is None:
				change.Cal_parms_cal.insert(name='plaps', obj_typ='bsn', abs_min=0, abs_max=200, units=None).execute()

			tlaps = change.Cal_parms_cal.get_or_none((change.Cal_parms_cal.name == 'tlaps') & (change.Cal_parms_cal.obj_typ == 'bsn'))
			if tlaps is None:
				change.Cal_parms_cal.insert(name='tlaps', obj_typ='bsn', abs_min=-10, abs_max=10, units=None).execute()

			deep_seep = change.Cal_parms_cal.get_or_none((change.Cal_parms_cal.name == 'deep_seep') & (change.Cal_parms_cal.obj_typ == 'aqu'))
			if deep_seep is None:
				change.Cal_parms_cal.insert(name='deep_seep', obj_typ='aqu', abs_min=0.001, abs_max=0.4, units='m/m').execute()

			sp_yld = change.Cal_parms_cal.get_or_none((change.Cal_parms_cal.name == 'sp_yld') & (change.Cal_parms_cal.obj_typ == 'aqu'))
			if sp_yld is None:
				change.Cal_parms_cal.insert(name='sp_yld', obj_typ='aqu', abs_min=0, abs_max=0.5, units='fraction').execute()

			change.Cal_parms_cal.update({
				change.Cal_parms_cal.abs_max: 50, 
				change.Cal_parms_cal.units: 'm'
			}).where((change.Cal_parms_cal.name == 'flo_min') & (change.Cal_parms_cal.obj_typ == 'aqu')).execute()

			change.Cal_parms_cal.update({
				change.Cal_parms_cal.name: 'ch_clay'
			}).where((change.Cal_parms_cal.name == 'clay') & (change.Cal_parms_cal.obj_typ == 'rte')).execute()

			change.Cal_parms_cal.update({
				change.Cal_parms_cal.name: 'ch_bd'
			}).where((change.Cal_parms_cal.name == 'bd') & (change.Cal_parms_cal.obj_typ == 'rte')).execute()

			change.Cal_parms_cal.delete().where((change.Cal_parms_cal.name == 'trnsrch') & (change.Cal_parms_cal.obj_typ == 'bsn')).execute()

			#Datasets changes for cal_parms.cal
			ds_plaps = datasets_change.Cal_parms_cal.get_or_none((datasets_change.Cal_parms_cal.name == 'plaps') & (datasets_change.Cal_parms_cal.obj_typ == 'bsn'))
			if ds_plaps is None:
				datasets_change.Cal_parms_cal.insert(name='plaps', obj_typ='bsn', abs_min=0, abs_max=200, units=None).execute()

			ds_tlaps = datasets_change.Cal_parms_cal.get_or_none((datasets_change.Cal_parms_cal.name == 'tlaps') & (datasets_change.Cal_parms_cal.obj_typ == 'bsn'))
			if ds_tlaps is None:
				datasets_change.Cal_parms_cal.insert(name='tlaps', obj_typ='bsn', abs_min=-10, abs_max=10, units=None).execute()

			ds_deep_seep = datasets_change.Cal_parms_cal.get_or_none((datasets_change.Cal_parms_cal.name == 'deep_seep') & (datasets_change.Cal_parms_cal.obj_typ == 'aqu'))
			if ds_deep_seep is None:
				datasets_change.Cal_parms_cal.insert(name='deep_seep', obj_typ='aqu', abs_min=0.001, abs_max=0.4, units='m/m').execute()

			ds_sp_yld = datasets_change.Cal_parms_cal.get_or_none((datasets_change.Cal_parms_cal.name == 'sp_yld') & (datasets_change.Cal_parms_cal.obj_typ == 'aqu'))
			if ds_sp_yld is None:
				datasets_change.Cal_parms_cal.insert(name='sp_yld', obj_typ='aqu', abs_min=0, abs_max=0.5, units='fraction').execute()

			datasets_change.Cal_parms_cal.update({
				datasets_change.Cal_parms_cal.abs_max: 50, 
				datasets_change.Cal_parms_cal.units: 'm'
			}).where((datasets_change.Cal_parms_cal.name == 'flo_min') & (datasets_change.Cal_parms_cal.obj_typ == 'aqu')).execute()

			datasets_change.Cal_parms_cal.update({
				datasets_change.Cal_parms_cal.name: 'ch_clay'
			}).where((datasets_change.Cal_parms_cal.name == 'clay') & (datasets_change.Cal_parms_cal.obj_typ == 'rte')).execute()

			datasets_change.Cal_parms_cal.update({
				datasets_change.Cal_parms_cal.name: 'ch_bd'
			}).where((datasets_change.Cal_parms_cal.name == 'bd') & (datasets_change.Cal_parms_cal.obj_typ == 'rte')).execute()

			datasets_change.Cal_parms_cal.delete().where((datasets_change.Cal_parms_cal.name == 'trnsrch') & (datasets_change.Cal_parms_cal.obj_typ == 'bsn')).execute()

			self.emit_progress(80, 'Updating recall data where applicable...')
			ob_typs = {
				1: 'pt_day',
				2: 'pt_mon',
				3: 'pt_yr',
				4: 'pt_const'
			}
			with base.db.atomic():
				for row in recall.Recall_dat.select().join(recall.Recall_rec).where(recall.Recall_rec.rec_typ == 1):
					dt = datetime.datetime(row.yr, 1, 1) + datetime.timedelta(row.jday - 1)
					tt = dt.timetuple()
					row.mo = tt.tm_mon
					row.day_mo = tt.tm_mday
					row.ob_typ = 'pt_day'
					row.ob_name = row.recall_rec.name
					row.save()
				for row in recall.Recall_dat.select().join(recall.Recall_rec).where(recall.Recall_rec.rec_typ != 1):
					row.mo = row.jday if row.jday != 0 else 1
					row.jday = 1
					row.day_mo = 1
					row.yr = row.yr if row.yr != 0 else 1
					row.ob_typ = ob_typs.get(row.recall_rec.rec_typ, 'pt')
					row.ob_name = row.recall_rec.name
					row.save()
		except Exception as ex:
			if rollback_db is not None:
				self.emit_progress(50, "Error occurred. Rolling back database...")
				SetupProjectDatabase.rollback(project_db, rollback_db)
				self.emit_progress(100, "Error occurred.")
			sys.exit(str(ex))

	def updates_for_2_0_0(self, project_db, datasets_db, rollback_db):
		try:
			self.emit_progress(5, 'Running migrations...')
			migrator = SqliteMigrator(SqliteDatabase(project_db))
			migrate(
				migrator.drop_column('water_balance_sft_item', 'orgn'),
				migrator.drop_column('plant_parms_sft', 'chg_typ'),
				migrator.drop_column('plant_parms_sft', 'neg'),
				migrator.drop_column('plant_parms_sft', 'pos'),
				migrator.drop_column('plant_parms_sft', 'lo'),
				migrator.drop_column('plant_parms_sft', 'up'),
				migrator.rename_column('hyd_sed_lte_cha', 'hc_cov', 'wd_rto'),
				migrator.drop_index('cal_parms_cal', 'cal_parms_cal_name')
			)

			base.db.create_tables([change.Plant_parms_sft_item])
			base.db.create_tables([init.Pest_hru_ini, init.Pest_hru_ini_item, init.Pest_water_ini, init.Pest_water_ini_item, 
								init.Path_hru_ini, init.Path_hru_ini_item, init.Path_water_ini, init.Path_water_ini_item, 
								init.Hmet_hru_ini, init.Hmet_hru_ini_item, init.Hmet_water_ini, init.Hmet_water_ini_item, 
								init.Salt_hru_ini, init.Salt_hru_ini_item, init.Salt_water_ini, init.Salt_water_ini_item])

			self.emit_progress(80, 'Updating decision table bugs from previous version...')
			d_act = decision_table.D_table_dtl_act
			d_act.update(const2=1).where(((d_act.act_typ == 'plant') | (d_act.act_typ == 'harvest_kill')) & (d_act.const2 == 0)).execute()
			d_act.update(fp='grain').where((d_act.act_typ == 'harvest_kill') & (d_act.fp == 'null')).execute()

			self.emit_progress(80, 'Updating channel width/depth ratio...')
			with base.db.atomic():
				for row in channel.Hyd_sed_lte_cha.select():
					row.wd_rto = 4 if row.dp == 0 else row.wd / row.dp
					row.save()

		except Exception as ex:
			if rollback_db is not None:
				self.emit_progress(50, "Error occurred. Rolling back database...")
				SetupProjectDatabase.rollback(project_db, rollback_db)
				self.emit_progress(100, "Error occurred.")
			sys.exit(str(ex))

	def updates_for_1_3_0(self, project_db, datasets_db, rollback_db):
		try:
			self.emit_progress(5, 'Running migrations...')
			migrator = SqliteMigrator(SqliteDatabase(project_db))
			migrate(
				migrator.rename_column('codes_bsn', 'rte_pest', 'nostress'),
				migrator.rename_column('aquifer_aqu', 'ptl_n', 'carbon'),
				migrator.rename_column('aquifer_aqu', 'ptl_p', 'flo_dist'),
				migrator.rename_column('parameters_bsn', 'cn_co', 'scoef'),
				migrator.rename_column('hydrology_hyd', 'evap_pothole', 'cn3_swf'),
				migrator.rename_column('hydrology_hyd', 'cn_plntet', 'latq_co'),
				migrator.add_column('water_balance_sft_item', 'pet', DoubleField(default=0))
			)

			#Ignore error if already done
			try:
				migrator = SqliteMigrator(SqliteDatabase(datasets_db))
				migrate(
					migrator.rename_column('codes_bsn', 'rte_pest', 'nostress'),
					migrator.rename_column('parameters_bsn', 'cn_co', 'scoef')
				)
			except Exception:
				pass

			self.emit_progress(10, 'Updating database...')
			lum.Ovn_table_lum.update({
				lum.Ovn_table_lum.ovn_mean: 0.011, 
				lum.Ovn_table_lum.ovn_min: 0.011, 
				lum.Ovn_table_lum.ovn_max: 0.011
			}).where(lum.Ovn_table_lum.name == 'urban_asphalt').execute()

			datasets_lum.Ovn_table_lum.update({
				datasets_lum.Ovn_table_lum.ovn_mean: 0.011, 
				datasets_lum.Ovn_table_lum.ovn_min: 0.011, 
				datasets_lum.Ovn_table_lum.ovn_max: 0.011
			}).where(datasets_lum.Ovn_table_lum.name == 'urban_asphalt').execute()

			aquifer.Aquifer_aqu.update({
				aquifer.Aquifer_aqu.carbon: 0.5,
				aquifer.Aquifer_aqu.flo_dist: 50
			}).execute()

			basin.Parameters_bsn.update({basin.Parameters_bsn.scoef: 1}).execute()
			datasets_basin.Parameters_bsn.update({datasets_basin.Parameters_bsn.scoef: 1}).execute()
		except Exception as ex:
			if rollback_db is not None:
				self.emit_progress(50, "Error occurred. Rolling back database...")
				SetupProjectDatabase.rollback(project_db, rollback_db)
				self.emit_progress(100, "Error occurred.")
			sys.exit(str(ex))

	def updates_for_1_2_1(self, project_db, rollback_db):
		try:
			lum.Landuse_lum.update({lum.Landuse_lum.plnt_com: None}).where(lum.Landuse_lum.name == 'barr_lum').execute()
		except Exception as ex:
			if rollback_db is not None:
				self.emit_progress(50, "Error occurred. Rolling back database...")
				SetupProjectDatabase.rollback(project_db, rollback_db)
				self.emit_progress(100, "Error occurred.")
			sys.exit(str(ex))

	def updates_for_1_2_0(self, project_db, update_project_values, rollback_db):
		try:
			self.emit_progress(5, 'Running migrations...')
			migrator = SqliteMigrator(SqliteDatabase(project_db))
			migrate(
				migrator.drop_column('wetland_wet', 'rel'),
				migrator.add_column('wetland_wet', 'rel_id', ForeignKeyField(decision_table.D_table_dtl, decision_table.D_table_dtl.id, on_delete='SET NULL', null=True)),
				migrator.drop_column('wetland_wet', 'hyd_id'),
				migrator.add_column('wetland_wet', 'hyd_id', ForeignKeyField(reservoir.Hydrology_wet, reservoir.Hydrology_wet.id, on_delete='SET NULL', null=True)),
				migrator.drop_column('hru_data_hru', 'surf_stor'),
				migrator.add_column('hru_data_hru', 'surf_stor_id', ForeignKeyField(reservoir.Wetland_wet, reservoir.Wetland_wet.id, on_delete='SET NULL', null=True))
			)

			self.emit_progress(10, 'Updating datasets database...')
			dataset_plants.update({dataset_plants.lai_pot: 0.5}).where(dataset_plants.name == 'watr').execute()
			hru_parm_db.Plants_plt.update({hru_parm_db.Plants_plt.lai_pot: 0.5}).where(hru_parm_db.Plants_plt.name == 'watr').execute()

			datasets_change.Cal_parms_cal.update({datasets_change.Cal_parms_cal.abs_max: 10, datasets_change.Cal_parms_cal.units: 'm'}).where((datasets_change.Cal_parms_cal.name == 'flo_min') | (datasets_change.Cal_parms_cal.name == 'revap_min')).execute()
			if datasets_change.Cal_parms_cal.select().where(datasets_change.Cal_parms_cal.name == 'dep_bot').count() < 1:
				datasets_change.Cal_parms_cal.insert(name='dep_bot', obj_typ='aqu', abs_min=0, abs_max=10, units='m').execute()

			"""Var_range.update({Var_range.max_value: 2, Var_range.default_value: 0.05}).where((Var_range.table == 'aquifer_aqu') & (Var_range.variable == 'gw_flo')).execute()
			Var_range.update({Var_range.max_value: 10, Var_range.default_value: 10}).where((Var_range.table == 'aquifer_aqu') & (Var_range.variable == 'dep_wt')).execute()
			Var_range.update({
				Var_range.max_value: 10, 
				Var_range.default_value: 5, 
				Var_range.units: 'm', 
				Var_range.description: 'Water table depth for return flow to occur'
			}).where((Var_range.table == 'aquifer_aqu') & (Var_range.variable == 'flo_min')).execute()
			Var_range.update({
				Var_range.max_value: 10, 
				Var_range.default_value: 3, 
				Var_range.units: 'm', 
				Var_range.description: 'Water table depth for revap to occur'
			}).where((Var_range.table == 'aquifer_aqu') & (Var_range.variable == 'revap_min')).execute()
			Var_range.update({
				Var_range.description: 'Fraction of years to maturity'
			}).where((Var_range.table == 'plant_ini') & (Var_range.variable == 'yrs_init')).execute()"""

			datasets_init.Plant_ini_item.update({
				datasets_init.Plant_ini_item.yrs_init: 1
			}).where(datasets_init.Plant_ini_item.yrs_init == 15).execute()

			bm_50k_plants = ['aspn', 'cedr', 'frsd', 'frsd_SuHF', 'frsd_SuMs', 'frsd_SuSt', 'frsd_TeCF', 'frsd_TeMs', 'frsd_TeOF', 'frsd_TeST', 'frse', 'frse_SuDrF', 'frse_SuDs', 'frse_SuHF', 'frse_SuMs', 'frse_SuSt', 'frse_TeCF', 'frse_TeDs', 'frse_TeMs', 'frse_TeOF', 'frse_TeST', 'frst', 'frst_SuHF', 'frst_SuMs', 'frst_SuSt', 'frst_TeCF', 'frst_TeMs', 'frst_TeOF', 'frst_TeST', 'juni', 'ldgp', 'mapl', 'mesq', 'oak', 'oilp', 'pine', 'popl', 'rngb', 'rngb_SuDrF', 'rngb_SuDs', 'rngb_SuHF', 'rngb_SuMs', 'rngb_SuSt', 'rngb_TeCF', 'rngb_TeDs', 'rngb_TeMs', 'rngb_TeOF', 'rngb_TeST', 'rubr', 'swrn', 'wetf', 'wetl', 'wetn', 'will', 'wspr']
			bm_20k_plants = ['almd', 'appl', 'barr', 'cash', 'coco', 'coct', 'coff', 'grap', 'oliv', 'oran', 'orcd', 'papa', 'past', 'plan', 'rnge', 'rnge_SuDrF', 'rnge_SuDs', 'rnge_SuHF', 'rnge_SuMs', 'rnge_SuSt', 'rnge_TeCF', 'rnge_TeDs', 'rnge_TeMs', 'rnge_TeOF', 'rnge_TeST', 'waln']
			bm_50k_ids = dataset_plants.select(dataset_plants.id).where(dataset_plants.name << bm_50k_plants)
			bm_20k_ids = dataset_plants.select(dataset_plants.id).where(dataset_plants.name << bm_20k_plants)

			datasets_init.Plant_ini_item.update({
				datasets_init.Plant_ini_item.bm_init: 50000
			}).where(datasets_init.Plant_ini_item.plnt_name_id << bm_50k_ids).execute()
			datasets_init.Plant_ini_item.update({
				datasets_init.Plant_ini_item.bm_init: 20000
			}).where(datasets_init.Plant_ini_item.plnt_name_id << bm_20k_ids).execute()
			datasets_init.Plant_ini_item.update({
				datasets_init.Plant_ini_item.lc_status: 1,
				datasets_init.Plant_ini_item.yrs_init: 1
			}).where(datasets_init.Plant_ini_item.plnt_name.name == 'past').execute()
			datasets_init.Plant_ini_item.update({
				datasets_init.Plant_ini_item.lc_status: 1
			}).where(datasets_init.Plant_ini_item.plnt_name.name == 'barr').execute()

			datasets_basin.Codes_bsn.update({
				datasets_basin.Codes_bsn.pet: 1,
				datasets_basin.Codes_bsn.rtu_wq: 1,
				datasets_basin.Codes_bsn.wq_cha: 1
			}).execute()

			Version.update({Version.value: '1.2.0', Version.release_date: datetime.datetime.now()}).execute()

			if update_project_values:
				self.emit_progress(60, 'Updating project cal_parms_cal and aquifer_aqu...')
				change.Cal_parms_cal.update({change.Cal_parms_cal.abs_max: 10, change.Cal_parms_cal.units: 'm'}).where((change.Cal_parms_cal.name == 'flo_min') | (change.Cal_parms_cal.name == 'revap_min')).execute()
				if change.Cal_parms_cal.select().where(change.Cal_parms_cal.name == 'dep_bot').count() < 1:
					change.Cal_parms_cal.insert(name='dep_bot', obj_typ='aqu', abs_min=0, abs_max=10, units='m').execute()

				aquifer.Aquifer_aqu.update({
					aquifer.Aquifer_aqu.gw_flo: 0.05,
					aquifer.Aquifer_aqu.dep_wt: 10,
					aquifer.Aquifer_aqu.flo_min: 5,
					aquifer.Aquifer_aqu.revap_min: 3
				}).execute()

				init.Plant_ini_item.update({
					init.Plant_ini_item.yrs_init: 1
				}).where(init.Plant_ini_item.yrs_init == 15).execute()

				bm_50k_ids = hru_parm_db.Plants_plt.select(hru_parm_db.Plants_plt.id).where(hru_parm_db.Plants_plt.name << bm_50k_plants)
				bm_20k_ids = hru_parm_db.Plants_plt.select(hru_parm_db.Plants_plt.id).where(hru_parm_db.Plants_plt.name << bm_20k_plants)

				init.Plant_ini_item.update({
					init.Plant_ini_item.bm_init: 50000
				}).where(init.Plant_ini_item.plnt_name_id << bm_50k_ids).execute()
				init.Plant_ini_item.update({
					init.Plant_ini_item.bm_init: 20000
				}).where(init.Plant_ini_item.plnt_name_id << bm_20k_ids).execute()
				init.Plant_ini_item.update({
					init.Plant_ini_item.lc_status: 1,
					init.Plant_ini_item.yrs_init: 1
				}).where(init.Plant_ini_item.plnt_name.name == 'past').execute()
				init.Plant_ini_item.update({
					init.Plant_ini_item.lc_status: 1
				}).where(init.Plant_ini_item.plnt_name.name == 'barr').execute()

				basin.Codes_bsn.update({
					basin.Codes_bsn.pet: 1,
					basin.Codes_bsn.rtu_wq: 1,
					basin.Codes_bsn.wq_cha: 1
				}).execute()
		except Exception as ex:
			if rollback_db is not None:
				self.emit_progress(50, "Error occurred. Rolling back database...")
				SetupProjectDatabase.rollback(project_db, rollback_db)
				self.emit_progress(100, "Error occurred.")
			sys.exit(str(ex))

	def updates_for_1_1_0(self, project_db, datasets_db, rollback_db):
		try:
			conn = lib.open_db(project_db)
			aquifer_cols = lib.get_column_names(conn, 'aquifer_aqu')
			aquifer_col_names = [v['name'] for v in aquifer_cols]
			if 'gw_dp' not in aquifer_col_names:
				sys.exit('It appears some of your tables may have already been migrated even though your project version is still listed at 1.0.0. Please check your tables, restart the upgrade using the backup database in the DatabaseBackups folder, or contact support.')
			conn.close()
			
			self.emit_progress(10, 'Running migrations...')
			base.db.create_tables([aquifer.Initial_aqu]) 
			migrator = SqliteMigrator(SqliteDatabase(project_db))
			migrate(
				migrator.rename_column('aquifer_aqu', 'gw_dp', 'dep_bot'),
				migrator.rename_column('aquifer_aqu', 'gw_ht', 'dep_wt'),
				migrator.drop_column('aquifer_aqu', 'delay'),
				migrator.add_column('aquifer_aqu', 'bf_max', DoubleField(default=1)),
				migrator.add_column('aquifer_aqu', 'init_id', ForeignKeyField(aquifer.Initial_aqu, aquifer.Initial_aqu.id, on_delete='SET NULL', null=True)),
				
				migrator.drop_column('codes_bsn', 'atmo_dep'),
				migrator.add_column('codes_bsn', 'atmo_dep', CharField(default='a')),

				migrator.drop_column('cal_parms_cal', 'units'),
				migrator.add_column('cal_parms_cal', 'units', CharField(null=True)),
				migrator.rename_table('codes_cal', 'codes_sft'),
				migrator.rename_column('codes_sft', 'landscape', 'hyd_hru'),
				migrator.rename_column('codes_sft', 'hyd', 'hyd_hrulte'),
				migrator.rename_table('ls_parms_cal', 'wb_parms_sft'),
				migrator.rename_table('ch_parms_cal', 'ch_sed_parms_sft'),
				migrator.rename_table('pl_parms_cal', 'plant_parms_sft'),
				
				migrator.drop_column('channel_cha', 'pest_id'),
				migrator.drop_column('channel_cha', 'ls_link_id'),
				migrator.drop_column('channel_cha', 'aqu_link_id'),
				migrator.drop_column('initial_cha', 'vol'),
				migrator.drop_column('initial_cha', 'sed'),
				migrator.drop_column('initial_cha', 'ptl_n'),
				migrator.drop_column('initial_cha', 'no3_n'),
				migrator.drop_column('initial_cha', 'no2_n'),
				migrator.drop_column('initial_cha', 'nh4_n'),
				migrator.drop_column('initial_cha', 'ptl_p'),
				migrator.drop_column('initial_cha', 'sol_p'),
				migrator.drop_column('initial_cha', 'secchi'),
				migrator.drop_column('initial_cha', 'sand'),
				migrator.drop_column('initial_cha', 'silt'),
				migrator.drop_column('initial_cha', 'clay'),
				migrator.drop_column('initial_cha', 'sm_agg'),
				migrator.drop_column('initial_cha', 'lg_agg'),
				migrator.drop_column('initial_cha', 'gravel'),
				migrator.drop_column('initial_cha', 'chla'),
				migrator.drop_column('initial_cha', 'sol_pest'),
				migrator.drop_column('initial_cha', 'srb_pest'),
				migrator.drop_column('initial_cha', 'lp_bact'),
				migrator.drop_column('initial_cha', 'p_bact'),
				migrator.add_column('initial_cha', 'org_min_id', ForeignKeyField(init.Om_water_ini, init.Om_water_ini.id, on_delete='SET NULL', null=True)),
				migrator.add_column('initial_cha', 'pest_id', ForeignKeyField(init.Pest_water_ini, init.Pest_water_ini.id, on_delete='SET NULL', null=True)),
				migrator.add_column('initial_cha', 'path_id', ForeignKeyField(init.Path_water_ini, init.Path_water_ini.id, on_delete='SET NULL', null=True)),
				migrator.add_column('initial_cha', 'hmet_id', ForeignKeyField(init.Hmet_water_ini, init.Hmet_water_ini.id, on_delete='SET NULL', null=True)),
				migrator.add_column('initial_cha', 'salt_id', ForeignKeyField(init.Salt_water_ini, init.Salt_water_ini.id, on_delete='SET NULL', null=True)),

				migrator.add_column('d_table_dtl', 'file_name', CharField(null=True)),
				migrator.add_column('d_table_dtl_act', 'const2', DoubleField(default=0)),
				migrator.rename_column('d_table_dtl_act', 'application', 'fp'),
				migrator.rename_column('d_table_dtl_act', 'type', 'option'),

				migrator.drop_column('exco_om_exc', 'sol_pest'),
				migrator.drop_column('exco_om_exc', 'srb_pest'),
				migrator.drop_column('exco_om_exc', 'p_bact'),
				migrator.drop_column('exco_om_exc', 'lp_bact'),
				migrator.drop_column('exco_om_exc', 'metl1'),
				migrator.drop_column('exco_om_exc', 'metl2'),
				migrator.drop_column('exco_om_exc', 'metl3'),
				migrator.rename_column('exco_om_exc', 'ptl_n', 'orgn'),
				migrator.rename_column('exco_om_exc', 'ptl_p', 'sedp'),
				migrator.rename_column('exco_om_exc', 'no3_n', 'no3'),
				migrator.rename_column('exco_om_exc', 'sol_p', 'solp'),
				migrator.rename_column('exco_om_exc', 'nh3_n', 'nh3'),
				migrator.rename_column('exco_om_exc', 'no2_n', 'no2'),
				migrator.rename_column('exco_om_exc', 'bod', 'cbod'),
				migrator.rename_column('exco_om_exc', 'oxy', 'dox'),
				migrator.rename_column('exco_om_exc', 'sm_agg', 'sag'),
				migrator.rename_column('exco_om_exc', 'lg_agg', 'lag'),
				migrator.drop_column('exco_pest_exc', 'aatrex_sol'),
				migrator.drop_column('exco_pest_exc', 'aatrex_sor'),
				migrator.drop_column('exco_pest_exc', 'banvel_sol'),
				migrator.drop_column('exco_pest_exc', 'banvel_sor'),
				migrator.drop_column('exco_pest_exc', 'prowl_sol'),
				migrator.drop_column('exco_pest_exc', 'prowl_sor'),
				migrator.drop_column('exco_pest_exc', 'roundup_sol'),
				migrator.drop_column('exco_pest_exc', 'roundup_sor'),
				migrator.drop_column('exco_path_exc', 'fecals_sol'),
				migrator.drop_column('exco_path_exc', 'fecals_sor'),
				migrator.drop_column('exco_path_exc', 'e_coli_sol'),
				migrator.drop_column('exco_path_exc', 'e_coli_sor'),
				migrator.drop_column('exco_hmet_exc', 'mercury_sol'),
				migrator.drop_column('exco_hmet_exc', 'mercury_sor'),
				migrator.drop_column('exco_salt_exc', 'sodium_sol'),
				migrator.drop_column('exco_salt_exc', 'sodium_sor'),
				migrator.drop_column('exco_salt_exc', 'magnesium_sol'),
				migrator.drop_column('exco_salt_exc', 'magnesium_sor'),

				migrator.drop_column('fertilizer_frt', 'p_bact'),
				migrator.drop_column('fertilizer_frt', 'lp_bact'),
				migrator.drop_column('fertilizer_frt', 'sol_bact'),
				migrator.add_column('fertilizer_frt', 'pathogens', CharField(null=True)),

				migrator.drop_column('hru_data_hru', 'soil_nut_id'),
				migrator.add_column('hru_data_hru', 'soil_plant_init_id', ForeignKeyField(init.Soil_plant_ini, init.Soil_plant_ini.id, null=True, on_delete='SET NULL')),

				migrator.drop_column('hydrology_hyd', 'dp_imp'),

				migrator.rename_table('pest_soil_ini', 'pest_hru_ini'),
				migrator.rename_table('pest_soil_ini_item', 'pest_hru_ini_item'),
				migrator.rename_table('path_soil_ini', 'path_hru_ini'),
				migrator.rename_table('hmet_soil_ini', 'hmet_hru_ini'),
				migrator.rename_table('salt_soil_ini', 'salt_hru_ini'),

				migrator.add_column('plant_ini', 'rot_yr_ini', IntegerField(default=1)),
				migrator.rename_column('plants_plt', 'plnt_hu', 'days_mat'),

				migrator.drop_column('recall_dat', 'sol_pest'),
				migrator.drop_column('recall_dat', 'srb_pest'),
				migrator.drop_column('recall_dat', 'p_bact'),
				migrator.drop_column('recall_dat', 'lp_bact'),
				migrator.drop_column('recall_dat', 'metl1'),
				migrator.drop_column('recall_dat', 'metl2'),
				migrator.drop_column('recall_dat', 'metl3'),

				migrator.drop_column('reservoir_res', 'pest_id'),
				migrator.drop_column('wetland_wet', 'pest_id'),
				migrator.drop_column('initial_res', 'vol'),
				migrator.drop_column('initial_res', 'sed'),
				migrator.drop_column('initial_res', 'ptl_n'),
				migrator.drop_column('initial_res', 'no3_n'),
				migrator.drop_column('initial_res', 'no2_n'),
				migrator.drop_column('initial_res', 'nh3_n'),
				migrator.drop_column('initial_res', 'ptl_p'),
				migrator.drop_column('initial_res', 'sol_p'),
				migrator.drop_column('initial_res', 'secchi'),
				migrator.drop_column('initial_res', 'sand'),
				migrator.drop_column('initial_res', 'silt'),
				migrator.drop_column('initial_res', 'clay'),
				migrator.drop_column('initial_res', 'sm_agg'),
				migrator.drop_column('initial_res', 'lg_agg'),
				migrator.drop_column('initial_res', 'gravel'),
				migrator.drop_column('initial_res', 'chla'),
				migrator.drop_column('initial_res', 'sol_pest'),
				migrator.drop_column('initial_res', 'srb_pest'),
				migrator.drop_column('initial_res', 'lp_bact'),
				migrator.drop_column('initial_res', 'p_bact'),
				migrator.add_column('initial_res', 'org_min_id', ForeignKeyField(init.Om_water_ini, init.Om_water_ini.id, on_delete='SET NULL', null=True)),
				migrator.add_column('initial_res', 'pest_id', ForeignKeyField(init.Pest_water_ini, init.Pest_water_ini.id, on_delete='SET NULL', null=True)),
				migrator.add_column('initial_res', 'path_id', ForeignKeyField(init.Path_water_ini, init.Path_water_ini.id, on_delete='SET NULL', null=True)),
				migrator.add_column('initial_res', 'hmet_id', ForeignKeyField(init.Hmet_water_ini, init.Hmet_water_ini.id, on_delete='SET NULL', null=True)),
				migrator.add_column('initial_res', 'salt_id', ForeignKeyField(init.Salt_water_ini, init.Salt_water_ini.id, on_delete='SET NULL', null=True)),
				migrator.add_column('sediment_res', 'carbon', DoubleField(default=0)),
				migrator.add_column('sediment_res', 'bd', DoubleField(default=0)),

				migrator.drop_column('rout_unit_ele', 'hyd_typ'),
				migrator.rename_column('rout_unit_ele', 'rtu_id', 'old_rtu_id'),
				migrator.drop_index('rout_unit_ele', 'rout_unit_ele_rtu_id'),
				migrator.add_column('rout_unit_ele', 'rtu_id', ForeignKeyField(connect.Rout_unit_con, connect.Rout_unit_con.id, on_delete='SET NULL', null=True)),

				migrator.drop_not_null('soils_sol', 'texture'),
			)

			self.emit_progress(30, 'Updating rout_unit_ele foreign keys...')
			# Move foreign key from rout_unit_rtu to rout_unit_con
			lib.execute_non_query(base.db.database, 'UPDATE rout_unit_ele SET rtu_id = old_rtu_id')
			migrate(
				migrator.drop_column('rout_unit_ele', 'old_rtu_id')
			)

			self.emit_progress(35, 'Drop and re-creating recall, change, init, lte, constituents, dr, irr ops, and exco tables...')
			# Drop and re-create recall tables since they had no data and had significant structure changes
			base.db.drop_tables([recall.Recall_rec, recall.Recall_dat])
			base.db.create_tables([recall.Recall_rec, recall.Recall_dat])

			# Drop and re-create calibration tables
			base.db.drop_tables([change.Calibration_cal]) 
			base.db.create_tables([change.Calibration_cal, change.Calibration_cal_cond, change.Calibration_cal_elem, change.Water_balance_sft, change.Water_balance_sft_item, change.Plant_gro_sft, change.Plant_gro_sft_item, change.Ch_sed_budget_sft, change.Ch_sed_budget_sft_item])

			# Drop and re-create irrigation ops table
			base.db.drop_tables([ops.Irr_ops])
			base.db.create_tables([ops.Irr_ops])
			lib.copy_table('irr_ops', datasets_db, project_db)

			# Drop and re-create init tables since they had no data and had significant structure changes
			base.db.drop_tables([init.Pest_hru_ini, init.Pest_hru_ini_item, init.Pest_water_ini, init.Path_hru_ini, init.Path_water_ini, init.Hmet_hru_ini, init.Hmet_water_ini, init.Salt_hru_ini, init.Salt_water_ini])
			base.db.create_tables([init.Om_water_ini, init.Pest_hru_ini, init.Pest_hru_ini_item, init.Pest_water_ini, init.Path_hru_ini, init.Path_water_ini, init.Hmet_hru_ini, init.Hmet_water_ini, init.Salt_hru_ini, init.Salt_water_ini, init.Soil_plant_ini])
			
			lib.bulk_insert(base.db, init.Om_water_ini, init.Om_water_ini.get_default_data())
			channel.Initial_cha.update({channel.Initial_cha.org_min: 1}).execute()
			reservoir.Initial_res.update({reservoir.Initial_res.org_min: 1}).execute()

			self.emit_progress(40, 'Updating channels tables...')
			base.db.drop_tables([channel.Channel_lte_cha])
			base.db.create_tables([channel.Hyd_sed_lte_cha, channel.Channel_lte_cha])
			hydrology_chas = []
			for hc in channel.Hydrology_cha.select():
				hyd_cha = {
					'id': hc.id,
					'name': hc.name,
					'order': 'first',
					'wd': hc.wd,
					'dp': hc.dp,
					'slp': hc.slp,
					'len': hc.len,
					'mann': hc.mann,
					'k': hc.k,
					'erod_fact': 0.01,
					'cov_fact': 0.005,
					'hc_cov': 0,
					'eq_slp': 0.001,
					'd50': 12,
					'clay': 50,
					'carbon': 0.04,
					'dry_bd': 1,
					'side_slp': 0.5,
					'bed_load': 0.5,
					't_conc': 10,
					'shear_bnk': 0.75,
					'hc_erod': 0.1,
					'hc_ht': 0.3,
					'hc_len': 0.3
				}
				hydrology_chas.append(hyd_cha)
			lib.bulk_insert(base.db, channel.Hyd_sed_lte_cha, hydrology_chas)

			channel_chas = []
			for cha in channel.Channel_cha.select():
				chan_cha = {
					'id': cha.id,
					'name': cha.name,
					'hyd': cha.hyd_id,
					'init': cha.init_id,
					'nut': cha.nut_id
				}
				channel_chas.append(chan_cha)
			lib.bulk_insert(base.db, channel.Channel_lte_cha, channel_chas)

			channel_cons = []
			channel_con_outs = []
			for cc in connect.Channel_con.select():
				chan_con = {
					'lcha': cc.cha_id,
					'id': cc.id,
					'name': cc.name,
					'gis_id': cc.gis_id,
					'lat': cc.lat,
					'lon': cc.lon,
					'elev': cc.elev,
					'wst': cc.wst_id,
					'area': cc.area,
					'ovfl': cc.ovfl,
					'rule': cc.rule
				}
				channel_cons.append(chan_con)

				for co in cc.con_outs:
					cha_out = {
						'id': co.id,
						'chandeg_con_id': co.channel_con.id,
						'order': co.order,
						'obj_typ': co.obj_typ,
						'obj_id': co.obj_id,
						'hyd_typ': co.hyd_typ,
						'frac': co.frac
					}
					channel_con_outs.append(cha_out)
			lib.bulk_insert(base.db, connect.Chandeg_con, channel_cons)
			lib.bulk_insert(base.db, connect.Chandeg_con_out, channel_con_outs)

			# Update from cha to sdc
			connect.Chandeg_con_out.update(obj_typ='sdc').where(connect.Chandeg_con_out.obj_typ=='cha').execute()
			connect.Hru_con_out.update(obj_typ='sdc').where(connect.Hru_con_out.obj_typ=='cha').execute()
			connect.Rout_unit_con_out.update(obj_typ='sdc').where(connect.Rout_unit_con_out.obj_typ=='cha').execute()
			connect.Aquifer_con_out.update(obj_typ='sdc').where(connect.Aquifer_con_out.obj_typ=='cha').execute()
			connect.Reservoir_con_out.update(obj_typ='sdc').where(connect.Reservoir_con_out.obj_typ=='cha').execute()
			connect.Recall_con_out.update(obj_typ='sdc').where(connect.Recall_con_out.obj_typ=='cha').execute()
			connect.Exco_con_out.update(obj_typ='sdc').where(connect.Exco_con_out.obj_typ=='cha').execute()
			connect.Delratio_con_out.update(obj_typ='sdc').where(connect.Delratio_con_out.obj_typ=='cha').execute()

			connect.Channel_con.delete().execute()
			connect.Channel_con_out.delete().execute()
			channel.Channel_cha.delete().execute()
			channel.Hydrology_cha.delete().execute()
			channel.Sediment_cha.delete().execute()
			
			# Drop and re-create all dr tables since not used previously
			base.db.drop_tables([dr.Dr_om_del, dr.Dr_pest_del, dr.Dr_path_del, dr.Dr_hmet_del, dr.Dr_salt_del, dr.Delratio_del])
			base.db.create_tables([dr.Dr_om_del, 
									dr.Dr_pest_del, dr.Dr_pest_col, dr.Dr_pest_val,
									dr.Dr_path_del, dr.Dr_path_col, dr.Dr_path_val,
									dr.Dr_hmet_del, dr.Dr_hmet_col, dr.Dr_hmet_val, 
									dr.Dr_salt_del, dr.Dr_salt_col, dr.Dr_salt_val, 
									dr.Delratio_del])

			# Drop and re-create exco tables since not used previously
			base.db.create_tables([exco.Exco_pest_col, exco.Exco_pest_val,
									exco.Exco_path_col, exco.Exco_path_val,
									exco.Exco_hmet_col, exco.Exco_hmet_val, 
									exco.Exco_salt_col, exco.Exco_salt_val])
			
			# Drop and re-create constituents.cs
			base.db.drop_tables([simulation.Constituents_cs])
			base.db.create_tables([simulation.Constituents_cs])

			# LTE tables
			base.db.drop_tables([hru.Hru_lte_hru])
			base.db.create_tables([hru.Hru_lte_hru, soils.Soils_lte_sol])

			self.emit_progress(50, 'Update aquifer, calibration parameters, fertilizer, and pesticides data...')
			aquifer.Initial_aqu.insert(name='initaqu1', org_min=1).execute()
			aquifer.Aquifer_aqu.update({aquifer.Aquifer_aqu.dep_bot: 10, aquifer.Aquifer_aqu.dep_wt: 5, aquifer.Aquifer_aqu.spec_yld: 0.05, aquifer.Aquifer_aqu.init: 1}).execute()

			lib.copy_table('cal_parms_cal', datasets_db, project_db)

			# Drop and re-create pesticide_pst
			base.db.drop_tables([hru_parm_db.Pesticide_pst])
			base.db.create_tables([hru_parm_db.Pesticide_pst])
			lib.copy_table('pesticide_pst', datasets_db, project_db)

			sp = init.Soil_plant_ini.create(
				name='soilplant1',
				sw_frac=0,
				nutrients=1
			)

			hru.Hru_data_hru.update({hru.Hru_data_hru.soil_plant_init: sp.id}).execute()

			hru_parm_db.Fertilizer_frt.delete().execute()
			lib.copy_table('fertilizer_frt', datasets_db, project_db, include_id=True)

			self.emit_progress(60, 'Update decision tables...')
			res_rels = {}
			for r in reservoir.Reservoir_res.select():
				res_rels[r.id] = r.rel.name

			decision_table.D_table_dtl.delete().execute()
			decision_table.D_table_dtl_cond.delete().execute()
			decision_table.D_table_dtl_cond_alt.delete().execute()
			decision_table.D_table_dtl_act.delete().execute()
			decision_table.D_table_dtl_act_out.delete().execute()
			lib.copy_table('d_table_dtl', datasets_db, project_db, include_id=True)
			lib.copy_table('d_table_dtl_cond', datasets_db, project_db, include_id=True)
			lib.copy_table('d_table_dtl_cond_alt', datasets_db, project_db, include_id=True)
			lib.copy_table('d_table_dtl_act', datasets_db, project_db, include_id=True)
			lib.copy_table('d_table_dtl_act_out', datasets_db, project_db, include_id=True)

			for r in reservoir.Reservoir_res.select():
				try:
					d_tbl_name = res_rels.get(r.id, None)
					if d_tbl_name is not None:
						r.rel_id = decision_table.D_table_dtl.get(decision_table.D_table_dtl.name == d_tbl_name).id
						r.save()
				except decision_table.D_table_dtl.DoesNotExist:
					pass

			self.emit_progress(70, 'Update management schedules...')
			lum.Management_sch.delete().execute()
			lum.Management_sch_auto.delete().execute()
			lum.Management_sch_op.delete().execute()
			lum.Landuse_lum.update(cal_group=None,mgt=None).execute()
			for lu in lum.Landuse_lum.select():
				plant_name = lu.name.replace('_lum', '')

				plant = hru_parm_db.Plants_plt.get_or_none(hru_parm_db.Plants_plt.name == plant_name)
				if plant is not None:
					new_d_table_id = None
					if plant.plnt_typ == 'warm_annual':
						new_d_table_id = GisImport.insert_decision_table(plant.name, 'pl_hv_corn')
					elif plant.plnt_typ == 'cold_annual':
						new_d_table_id = GisImport.insert_decision_table(plant.name, 'pl_hv_wwht') 

					if new_d_table_id is not None:
						mgt_name = '{plant}_rot'.format(plant=plant.name)
						
						mgt_id = lum.Management_sch.insert(
							name = mgt_name
						).execute()
						lum.Management_sch_auto.insert(
							management_sch=mgt_id,
							d_table=new_d_table_id
						).execute()

						lu.mgt = mgt_id
						lu.save()

			self.emit_progress(80, 'Update file_cio and print tables...')
			simulation.Print_prt_object.create(name='pest', daily=False, monthly=False, yearly=False, avann=False, print_prt_id=1)

			File_cio.delete().execute()
			file_cios = []
			for f in dataset_file_cio.select():
				file_cio = {
					'classification': f.classification.id,
					'order_in_class': f.order_in_class,
					'file_name': f.default_file_name
				}
				file_cios.append(file_cio)

			lib.bulk_insert(base.db, File_cio, file_cios)

			self.emit_progress(90, 'Update plants table to use days_mat column...')
			for p in hru_parm_db.Plants_plt:
				dp = dataset_plants.get_or_none(dataset_plants.name == p.name)
				if dp is not None:
					p.days_mat = dp.days_mat
				else:
					p.days_mat = 0
				p.save()
		except Exception as ex:
			if rollback_db is not None:
				self.emit_progress(50, "Error occurred. Rolling back database...")
				SetupProjectDatabase.rollback(project_db, rollback_db)
				self.emit_progress(100, "Error occurred.")
			sys.exit(str(ex))


if __name__ == '__main__':
	sys.stdout = Unbuffered(sys.stdout)
	parser = argparse.ArgumentParser(description="Update SWAT+ project database")
	parser.add_argument("--project_db_file", type=str, help="full path of project SQLite database file", nargs="?")
	parser.add_argument("--datasets_db_file", type=str, help="full path of datasets SQLite database file", nargs="?")
	parser.add_argument("--editor_version", type=str, help="editor version", nargs="?")
	parser.add_argument("--update_project_values", type=str, help="y/n update project values (default n)", nargs="?")
	parser.add_argument("--reimport_gis", type=str, help="y/n re-import GIS data (default n)", nargs="?")

	args = parser.parse_args()

	update_project_values = True if args.update_project_values == "y" else False
	reimport_gis = True if args.reimport_gis == "y" else False
	api = UpdateProject(args.project_db_file, args.editor_version, args.datasets_db_file, update_project_values, reimport_gis)
