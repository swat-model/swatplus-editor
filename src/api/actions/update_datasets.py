from helpers.executable_api import ExecutableApi, Unbuffered
from helpers import utils
from database import lib
from database.datasets.setup import SetupDatasetsDatabase
from database.project.setup import SetupProjectDatabase
from database.output.base import Project_config
from database.project.config import Project_config as project_config_table

from database.datasets.hru_parm_db import Plants_plt as dataset_plants
from database.datasets.definitions import File_cio as dataset_file_cio, Var_range, Version, Print_prt as dataset_print_prt, Print_prt_object as dataset_print_prt_object, File_cio_classification as dataset_file_cio_classification
from database.datasets import change as datasets_change, init as datasets_init, lum as datasets_lum, basin as datasets_basin, ops as datasets_ops, decision_table as datasets_decision_table, hru_parm_db as datasets_hru_parm_db, base as datasets_base

import sys
import argparse
import os, os.path
from shutil import copyfile
import time
from peewee import *
from playhouse.migrate import *
import datetime

# Map version prefixes/values to required upgrades
UPGRADE_PATHS = {
	'3.1.': ['3_2_0'],
	'3.0.': ['3_1_0', '3_2_0'],
	'2.3.': ['3_0_0', '3_1_0', '3_2_0'],
	('2.1.', '2.2.'): ['2_3_0', '3_0_0', '3_1_0', '3_2_0'],
	'2.0.': ['2_1_0', '2_3_0', '3_0_0', '3_1_0', '3_2_0'],
	('1.3.0', '1.4.0'): ['2_1_0', '2_3_0', '3_0_0', '3_1_0', '3_2_0'],
	('1.2.1', '1.2.2', '1.2.3'): ['1_3_0', '2_1_0', '2_3_0', '3_0_0', '3_1_0', '3_2_0'],
	'1.2.0': ['1_3_0', '2_1_0', '2_3_0', '3_0_0', '3_1_0', '3_2_0'],
	('1.1.0', '1.1.1', '1.1.2'): ['1_2_0', '1_3_0', '2_1_0', '2_3_0', '3_0_0', '3_1_0', '3_2_0'],
	'1.0.0': ['1_2_0', '1_3_0', '2_1_0', '2_3_0', '3_0_0', '3_1_0', '3_2_0'],
}

def matches_pattern(version, pattern):
	"""Check if version matches a pattern (string, tuple, or exact match)."""
	if isinstance(pattern, tuple):
		return any(version == p or version.startswith(p) for p in pattern)
	return version == pattern or version.startswith(pattern)

def available_to_update(version):
	upgrade_chain = None
	for pattern, upgrades in UPGRADE_PATHS.items():
		if matches_pattern(version, pattern):
			upgrade_chain = upgrades
			break
	return upgrade_chain is not None

# datasets_db = utils.full_path(project_db, m.reference_db)
class UpdateDatasets(ExecutableApi):
	def __init__(self, new_version, datasets_db=None, project_db=None):
		if datasets_db is None and project_db is not None:
			SetupProjectDatabase.init(project_db)
			c = project_config_table.get_or_none()
			if c is None:
				sys.exit("Could not retrieve project configuration data.")
			datasets_db = utils.full_path(project_db, c.reference_db)
		
		SetupDatasetsDatabase.init(datasets_db)
		
		m = Version.get_or_none()
		if m is None:
			sys.exit('No version found in datasets database. Please download the latest datasets database from plus.swat.tamu.edu.')

		# Find matching upgrade path
		version = m.value
		upgrade_chain = None
		for pattern, upgrades in UPGRADE_PATHS.items():
			if matches_pattern(version, pattern):
				upgrade_chain = upgrades
				break

		# Check if version is supported
		if upgrade_chain is not None:
			# Backup original db before beginning
			try:
				self.emit_progress(2, 'Backing up datasets database...')
				base_path = os.path.dirname(datasets_db)
				rel_datasets_db = os.path.relpath(datasets_db, base_path)
				
				filename, file_extension = os.path.splitext(rel_datasets_db)
				bak_filename = filename + '_v' + m.value.replace('.', '_') + '_' + time.strftime('%Y%m%d-%H%M%S') + file_extension
				bak_dir = os.path.join(base_path, 'DatabaseBackups')
				if not os.path.exists(bak_dir):
					os.makedirs(bak_dir)
				backup_db_file = os.path.join(bak_dir, bak_filename)
				copyfile(datasets_db, os.path.join(bak_dir, bak_filename))
			except IOError as err:
				sys.exit(err)

			# Apply all upgrades in chain
			self.emit_progress(15, 'Updating database with new defaults...')
			for upgrade in upgrade_chain:
				try:
					method = getattr(self, f'updates_for_{upgrade}')
					method(datasets_db)
				except Exception as ex:
					if backup_db_file is not None:
						self.emit_progress(50, "Error occurred. Rolling back database...")
						SetupDatasetsDatabase.rollback(datasets_db, backup_db_file)
						self.emit_progress(100, "Error occurred.")
					sys.exit(str(ex))
			
			Version.update({Version.value: new_version, Version.release_date: datetime.datetime.now()}).execute()

	def updates_for_3_2_0(self, datasets_db):
		if not self.name_exists(dataset_file_cio_classification, 'out_path'): dataset_file_cio_classification.insert(name='out_path').execute()
	
	def updates_for_3_1_0(self, datasets_db):
		self.cal_parms_value_updates_for_3_1_0(datasets_change.Cal_parms_cal)
		datasets_basin.Parameters_bsn.update({ datasets_basin.Parameters_bsn.adj_pkrt_sed: 484 }).execute()
	
	def updates_for_3_0_0(self, datasets_db):
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

		dataset_file_cio.update({dataset_file_cio.default_file_name: 'pet.cli'}).where(dataset_file_cio.default_file_name == 'wind-dir.cli').execute()
		dataset_file_cio.update({dataset_file_cio.default_file_name: 'gwflow.con'}).where(dataset_file_cio.default_file_name == 'modflow.con').execute()
		dataset_file_cio.update({dataset_file_cio.default_file_name: 'pesticide.pst'}).where(dataset_file_cio.default_file_name == 'pesticide.pes').execute()
		datasets_hru_parm_db.Pesticide_pst.update({datasets_hru_parm_db.Pesticide_pst.aq_hlife: 142.85, datasets_hru_parm_db.Pesticide_pst.ben_hlife: 20}).execute()
		datasets_basin.Codes_bsn.update({datasets_basin.Codes_bsn.i_fpwet: 1}).execute()

		self.plant_value_updates_for_3_0_0(datasets_hru_parm_db.Plants_plt)
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
		lib.bulk_insert(datasets_base.db, dataset_print_prt_object, new_print_prt)

		#decision table changes
		datasets_decision_table.D_table_dtl_act.update({datasets_decision_table.D_table_dtl_act.fp: 'grain'}).where(datasets_decision_table.D_table_dtl_act.act_typ == 'harvest_kill').execute()

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
	
	def cal_parms_value_updates_for_3_1_0(self, table):
		table.delete().where(table.name == 'rch_dox').execute()
		table.delete().where(table.name == 'rch_cbod').execute()
		table.delete().where(table.name == 'algae').execute()
		table.delete().where(table.name == 'organicn').execute()
		table.delete().where(table.name == 'ammonian').execute()
		table.delete().where(table.name == 'nitriten').execute()
		table.delete().where(table.name == 'organicp').execute()
		table.delete().where(table.name == 'disolvp').execute()
		
		if not self.name_exists(table, 'bank_exp'): table.insert(name='bank_exp', obj_typ='rte', abs_min=1.5, abs_max=6, units=None).execute()
		if not self.name_exists(table, 'mumax'): table.insert(name='mumax', obj_typ='swq', abs_min=1, abs_max=3, units='1/day').execute()
		if not self.name_exists(table, 'res_d50'): table.insert(name='res_d50', obj_typ='res', abs_min=0.1, abs_max=1000, units='um').execute()
		if not self.name_exists(table, 'rsd_covco'): table.insert(name='rsd_covco', obj_typ='bsn', abs_min=0.001, abs_max=1.25, units=None).execute()
		if not self.name_exists(table, 'usle_c'): table.insert(name='usle_c', obj_typ='plt', abs_min=0.001, abs_max=1.95, units=None).execute()
		if not self.name_exists(table, 'vcr_coef'): table.insert(name='vcr_coef', obj_typ='rte', abs_min=0.5, abs_max=2, units=None).execute()
		
		table.update({ table.abs_min: 0.0001 }).where(table.name == 'cherod').execute()
		table.update({ table.abs_min: 0.00001 }).where(table.name == 'chk').execute()
		table.update({ table.abs_min: 0.001 }).where(table.name == 'chl').execute()
		table.update({ table.abs_min: 0.001 }).where(table.name == 'chn').execute()
		table.update({ table.abs_min: 0.0001 }).where(table.name == 'chs').execute()
		table.update({ table.abs_min: 0.001 }).where(table.name == 'cov').execute()
		table.update({ table.abs_min: 0.0001 }).where(table.name == 'sp_yld').execute()
		table.update({ table.abs_min: 0.0000001 }).where(table.name == 'stream_K').execute()
		table.update({ table.abs_min: 250, table.abs_max: 700 }).where(table.name == 'prf').execute()
		
		table.update({ table.obj_typ: 'hru' }).where(table.name == 'harv_idx').execute()
		table.update({ table.obj_typ: 'hru' }).where(table.name == 'lai_pot').execute()
		table.update({ table.obj_typ: 'hru' }).where(table.name == 'phu_mat').execute()
	
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
	
	def updates_for_2_3_0(self, datasets_db):
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

		dataset_file_cio.delete().where(dataset_file_cio.classification == 14).execute()
		dataset_file_cio.insert(classification=14, order_in_class=1, database_table='water_allocation_wro', default_file_name='water_allocation.wro', is_core_file=False).execute()
		dataset_file_cio.insert(classification=14, order_in_class=2, database_table='define_wro', default_file_name='define.wro', is_core_file=False).execute()
		dataset_file_cio.insert(classification=14, order_in_class=3, database_table='element_wro', default_file_name='element.wro', is_core_file=False).execute()

		#print.prt changes
		dataset_print_prt_object.update({dataset_print_prt_object.name: 'water_allo'}).where(dataset_print_prt_object.name == 'region_psc').execute()
		dataset_print_prt_object.update({dataset_print_prt_object.name: 'region_psc'}).where(dataset_print_prt_object.name == 'region_sd_cha').execute()
		dataset_print_prt_object.update({dataset_print_prt_object.name: 'region_sd_cha'}).where(dataset_print_prt_object.name == 'region_cha').execute()

		#cal_parms.cal changes
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
			ds_cp = datasets_change.Cal_parms_cal.get_or_none((datasets_change.Cal_parms_cal.name == cal_parm['name']) & (datasets_change.Cal_parms_cal.obj_typ == cal_parm['obj_typ']))
			if ds_cp is None:
				datasets_change.Cal_parms_cal.insert(name=cal_parm['name'], obj_typ=cal_parm['obj_typ'], abs_min=cal_parm['abs_min'], abs_max=cal_parm['abs_max'], units=cal_parm['units']).execute()

		new_harv_ops = [
			{ 'name': 'cotton_picker', 'harv_typ': 'grain', 'harv_idx': 0.05, 'harv_eff': 0.95, 'harv_bm_min': 0 },
			{ 'name': 'cotton_strip', 'harv_typ': 'grain', 'harv_idx': 0.05, 'harv_eff': 0.95, 'harv_bm_min': 0 }
		]
		for harv_op in new_harv_ops:
			ds_ho = datasets_ops.Harv_ops.get_or_none(datasets_ops.Harv_ops.name == harv_op['name'])
			if ds_ho is None:
				datasets_ops.Harv_ops.insert(name=harv_op['name'], harv_typ=harv_op['harv_typ'], harv_idx=harv_op['harv_idx'], harv_eff=harv_op['harv_eff'], harv_bm_min=harv_op['harv_bm_min']).execute()

	def updates_for_2_1_0(self, datasets_db):
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

		datasets_basin.Parameters_bsn.update({
			datasets_basin.Parameters_bsn.nperco_lchtile: 0.5, 
			datasets_basin.Parameters_bsn.plaps: 0, 
			datasets_basin.Parameters_bsn.tlaps: 6.5, 
			datasets_basin.Parameters_bsn.urb_init_abst: 1, 
			datasets_basin.Parameters_bsn.petco_pmpt: 1, 
			datasets_basin.Parameters_bsn.co2: 400, 
			datasets_basin.Parameters_bsn.day_lag_max: 0, 
		}).execute()

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

	def updates_for_1_3_0(self, datasets_db):
		#Ignore error if already done
		try:
			migrator = SqliteMigrator(SqliteDatabase(datasets_db))
			migrate(
				migrator.rename_column('codes_bsn', 'rte_pest', 'nostress'),
				migrator.rename_column('parameters_bsn', 'cn_co', 'scoef')
			)
		except Exception:
			pass

		datasets_lum.Ovn_table_lum.update({
			datasets_lum.Ovn_table_lum.ovn_mean: 0.011, 
			datasets_lum.Ovn_table_lum.ovn_min: 0.011, 
			datasets_lum.Ovn_table_lum.ovn_max: 0.011
		}).where(datasets_lum.Ovn_table_lum.name == 'urban_asphalt').execute()
		
		datasets_basin.Parameters_bsn.update({datasets_basin.Parameters_bsn.scoef: 1}).execute()

	def updates_for_1_2_0(self, datasets_db):
		dataset_plants.update({dataset_plants.lai_pot: 0.5}).where(dataset_plants.name == 'watr').execute()

		datasets_change.Cal_parms_cal.update({datasets_change.Cal_parms_cal.abs_max: 10, datasets_change.Cal_parms_cal.units: 'm'}).where((datasets_change.Cal_parms_cal.name == 'flo_min') | (datasets_change.Cal_parms_cal.name == 'revap_min')).execute()
		if datasets_change.Cal_parms_cal.select().where(datasets_change.Cal_parms_cal.name == 'dep_bot').count() < 1:
			datasets_change.Cal_parms_cal.insert(name='dep_bot', obj_typ='aqu', abs_min=0, abs_max=10, units='m').execute()

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

if __name__ == '__main__':
	sys.exit('This file is not meant to be run directly. Please call the appropriate function from swatplus_api.py instead.')
