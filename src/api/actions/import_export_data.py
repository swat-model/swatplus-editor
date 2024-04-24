from helpers.executable_api import ExecutableApi, Unbuffered
from helpers import table_mapper
from database.project.setup import SetupProjectDatabase
from database.project import base as project_base
from database.project.recall import Recall_rec, Recall_dat
from database.project.climate import Weather_sta_cli
from database.project.salts import Salt_recall_rec, Salt_recall_dat
from fileio import base as fileio
from fileio import connect, exco, dr, recall, climate, channel, aquifer, hydrology, reservoir, hru, lum, soils, init, routing_unit, regions, simulation, hru_parm_db, config, ops, structural, decision_table, basin, change, gwflow, salts

import sys
import argparse
import os, os.path
import json

dtl_names = [
	'lum.dtl', 'res_rel.dtl', 'scen_lu.dtl', 'flo_con.dtl'
]

gwflow_cell_tables = [
	'gwflow_hrucell', 'gwflow_fpcell', 'gwflow_rivcell', 'gwflow_lsucell', 'gwflow_rescell'
]

class ImportExportData(ExecutableApi):
	def __init__(self, file_name, table_name, db_file, delete_existing=False, related_id=0, ignore_id_col=True, version=None, input_files_dir=None, rec_typ=None, column_name=None, swat_version=None):
		self.__abort = False
		SetupProjectDatabase.init(db_file)
		self.db_file = db_file
		self.file_name = file_name
		self.table = table_mapper.types.get(table_name, None)

		self.table_name = table_name
		self.delete_existing = delete_existing
		self.related_id = related_id
		self.ignore_id_col = ignore_id_col
		self.version = version
		self.input_files_dir = input_files_dir
		self.rec_typ = rec_typ
		self.column_name = column_name
		self.swat_version = swat_version

		if self.table is None:
			sys.exit("Table '{table}' does not exist.".format(table=table_name))

	def import_recall(self):
		if self.input_files_dir is None or not os.path.exists(self.input_files_dir):
			sys.exit('Please provide an input files directory containing your files.')

		prog_items = Recall_rec.select().count()
		prog_step = 0 if prog_items == 0 else 100 / prog_items
		prog = 0
		for rec in Recall_rec.select():
			rec_path = os.path.join(self.input_files_dir, '{}.csv'.format(rec.name.strip()))
			if os.path.exists(rec_path):
				prog += prog_step
				self.emit_progress(prog, "Importing {}.csv...".format(rec.name.strip()))
				recall.Recall_rec(rec_path).read_data(rec.id, self.delete_existing, None)

		rec_path = os.path.join(self.input_files_dir, 'recall.csv')
		if os.path.exists(rec_path):
			recall.Recall_rec(rec_path).read_const_data()

	def export_recall(self):
		if self.input_files_dir is None or not os.path.exists(self.input_files_dir):
			sys.exit('Please provide a directory to save your files.')

		prog_items = Recall_rec.select().count()
		prog_step = 0 if prog_items == 0 else 100 / prog_items
		prog = 0
		has_const = False
		self.table = table_mapper.types.get('rec_dat', None)
		for rec in Recall_rec.select():
			rec_path = os.path.join(self.input_files_dir, '{}.csv'.format(rec.name.strip()))
			if rec.rec_typ != 4:
				prog += prog_step
				self.emit_progress(prog, "Exporting {}.csv...".format(rec.name.strip()))
				self.file_name = rec_path
				self.table_name = 'rec_dat'
				self.related_id = rec.id
				self.export_csv()
			else:
				has_const = True

		if has_const:
			self.file_name = os.path.join(self.input_files_dir, 'recall.csv')
			self.table_name = 'rec_cnst'
			self.table = table_mapper.types.get('rec_cnst', None)
			self.export_csv()
			
	def import_salt_recall(self):
		if self.input_files_dir is None or not os.path.exists(self.input_files_dir):
			sys.exit('Please provide an input files directory containing your files.')

		prog_items = Salt_recall_rec.select().count()
		prog_step = 0 if prog_items == 0 else 100 / prog_items
		prog = 0
		for rec in Salt_recall_rec.select():
			rec_path = os.path.join(self.input_files_dir, 'salt_{}.csv'.format(rec.name.strip()))
			if os.path.exists(rec_path):
				prog += prog_step
				self.emit_progress(prog, "Importing {}.csv...".format(rec.name.strip()))
				salts.Salt_recall_rec(rec_path).read_data(rec.id, self.delete_existing, None)

	def export_salt_recall(self):
		if self.input_files_dir is None or not os.path.exists(self.input_files_dir):
			sys.exit('Please provide a directory to save your files.')

		prog_items = Salt_recall_rec.select().count()
		prog_step = 0 if prog_items == 0 else 100 / prog_items
		prog = 0
		self.table = table_mapper.types.get('salt_rec_dat', None)
		for rec in Salt_recall_rec.select():
			rec_path = os.path.join(self.input_files_dir, 'salt_{}.csv'.format(rec.name.strip()))
			prog += prog_step
			self.emit_progress(prog, "Exporting salt_{}.csv...".format(rec.name.strip()))
			self.file_name = rec_path
			self.table_name = 'salt_rec_dat'
			self.related_id = rec.id
			self.export_csv()

	def import_csv(self):
		if self.table_name == 'rec_dat':
			recall.Recall_rec(self.file_name).read_data(self.related_id, self.delete_existing, self.rec_typ)
		elif self.table_name == 'rec_cnst':
			recall.Recall_rec(self.file_name).read_const_data()
		elif self.table_name == 'salt_rec_dat':
			salts.Salt_recall_rec(self.file_name).read_data(self.related_id, self.delete_existing, self.rec_typ)
		elif self.table_name in dtl_names:
			decision_table.D_table_dtl(self.file_name, file_type=self.table_name).read()
		elif self.table_name == 'mgt_sch':
			lum.Management_sch(self.file_name).read()
		elif self.table_name == 'gwflow_grid':
			gwflow_writer = gwflow.Gwflow_files('', self.version, self.swat_version, self.db_file)
			gwflow_writer.read_grid(self.file_name, self.column_name)
		elif self.table_name in gwflow_cell_tables:
			gwflow_writer = gwflow.Gwflow_files('', self.version, self.swat_version, self.db_file)
			gwflow_writer.read_cell_csv(self.file_name, self.table_name)
		elif self.table_name == 'gwflow_wetland':
			gwflow_writer = gwflow.Gwflow_files('', self.version, self.swat_version, self.db_file)
			gwflow_writer.read_wetland_csv(self.file_name)
		else:
			fileio.read_csv_file(self.file_name, self.table, project_base.db, 0, ignore_id_col=self.ignore_id_col, overwrite=fileio.FileOverwrite.replace, remove_spaces_cols=['name'], primary_key=self.column_name)

	def export_csv(self):
		if self.table_name in dtl_names:
			decision_table.D_table_dtl(self.file_name, self.version, file_type=self.table_name).write()
		elif self.table_name == 'mgt_sch':
			lum.Management_sch(self.file_name, self.version).write()
		elif self.table_name == 'gwflow_grid':
			gwflow_writer = gwflow.Gwflow_files('', self.version, self.swat_version, self.db_file)
			gwflow_writer.write_grid(self.file_name, self.column_name)
		elif self.table_name in gwflow_cell_tables:
			gwflow_writer = gwflow.Gwflow_files('', self.version, self.swat_version, self.db_file)
			gwflow_writer.write_cell_csv(self.file_name, self.table_name)
		elif self.table_name == 'gwflow_wetland':
			gwflow_writer = gwflow.Gwflow_files('', self.version, self.swat_version, self.db_file)
			gwflow_writer.write_wetland_csv(self.file_name)
		else:
			ignored_cols = []
			initial_headers = []
			custom_query = None
			if self.table_name == 'rec_dat' or self.table_name == 'salt_rec_dat':
				ignored_cols.append('recall_rec')
				custom_query = self.table.select().where(self.table.recall_rec_id == self.related_id)
			elif self.table_name == 'rec_cnst':
				ignored_cols.append('recall_rec')
				ignored_cols.append('yr')
				ignored_cols.append('jday')
				ignored_cols.append('mo')
				ignored_cols.append('day_mo')
				ignored_cols.append('ob_typ')
				ignored_cols.append('ob_name')
				initial_headers.append('name')
				custom_query = Recall_dat.select(Recall_rec.name, Recall_dat).join(Recall_rec).where(Recall_rec.rec_typ == 4)
			elif self.table_name == 'atmo_map':
				ignored_cols.append('name')
				ignored_cols.append('wgn')
				ignored_cols.append('pcp')
				ignored_cols.append('tmp')
				ignored_cols.append('slr')
				ignored_cols.append('hmd')
				ignored_cols.append('wnd')
				ignored_cols.append('pet')
				ignored_cols.append('atmo_dep')
				initial_headers.append('atmo_station')
				initial_headers.append('weather_station')
				ws = Weather_sta_cli
				custom_query = ws.select(ws.atmo_dep.alias('atmo_station'), ws.name.alias('weather_station'), ws.lat, ws.lon)

			try:
				fileio.write_csv(self.file_name, self.table, ignore_id_col=self.ignore_id_col, ignored_cols=ignored_cols, custom_query=custom_query, initial_headers=initial_headers, primary_key=self.column_name)
			except PermissionError:
				sys.exit('Permission error. Please check to make sure the file is not open.')

	def export_text(self):
		t = self.table_name
		if t == 'weather_wgn_cli':
			climate.Weather_wgn_cli(self.file_name, self.version).write()


if __name__ == '__main__':
	sys.stdout = Unbuffered(sys.stdout)
	parser = argparse.ArgumentParser(description="Import/Export data to SWAT+ project database")
	parser.add_argument("action", type=str, help="import_csv or export_csv")
	parser.add_argument("file_name", type=str, help="full path of csv file")
	parser.add_argument("table_name", type=str, help="database table")
	parser.add_argument("db_file", type=str, help="full path of project SQLite database file")
	parser.add_argument("delete_existing", type=str, help="y/n delete existing data first", nargs="?")
	parser.add_argument("related_id", type=int, help="database table", nargs="?")
	parser.add_argument("ignore_id", type=str, help="y/n ignore id column", nargs="?")
	parser.add_argument("version", type=str, help="editor version", nargs="?")
	parser.add_argument("input_files_dir", type=str, help="input files directory", nargs="?")
	parser.add_argument("rec_typ", type=str, help="recall type", nargs="?")
	args = parser.parse_args()

	del_ex = True if args.delete_existing == "y" else False
	related_id = 0 if args.related_id is None else args.related_id
	ignore_id = False if args.ignore_id == "n" else True

	api = ImportExportData(args.file_name, args.table_name, args.db_file, del_ex, related_id, ignore_id, args.version, args.input_files_dir, args.rec_typ)
	
	if args.action == "import_csv":
		api.import_csv()
	elif args.action == "export_csv":
		api.export_csv()
