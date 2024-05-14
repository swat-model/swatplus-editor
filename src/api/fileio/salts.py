from .base import BaseFileModel, FileColumn as col
from peewee import *
import database.project.salts as db
from helpers import utils
import os.path
from database.project import base as project_base, simulation
from database.project.climate import Atmo_cli_sta
from database import lib as db_lib
import csv
import datetime
import sys

def get_salt_module():
	module, created = db.Salt_module.get_or_create(id=1)
	return module


class Salt_recall_rec(BaseFileModel):
	def __init__(self, file_name, version=None, swat_version=None):
		self.file_name = file_name
		self.version = version
		self.swat_version = swat_version

	def read(self):
		raise NotImplementedError('Reading not implemented yet.')

	def read_data(self, recall_rec_id, delete_existing, rec_typ):
		with open(self.file_name, mode='r') as csv_file:
			dialect = csv.Sniffer().sniff(csv_file.readline())
			csv_file.seek(0)
			replace_commas = dialect is not None and dialect.delimiter != ','
			csv_reader = csv.DictReader(csv_file)
			rows = []

			"""
			recTypOptions: [
				{ value: 1, text: 'Daily' },
				{ value: 2, text: 'Monthly' },
				{ value: 3, text: 'Yearly' }
			]
			"""
			ob_typs = {
				'pt_day' : 1,
				'pt_mon' : 2,
				'pt_yr' : 3
			}
			ob_typ = None
			for row in csv_reader:
				if replace_commas:
					for key in row:
						row[key] = row[key].replace(',', '.', 1)
				row['recall_rec_id'] = recall_rec_id
				rows.append(row)
				ob_typ = ob_typs.get(row['ob_typ'], None)

			if ob_typ is None:
				months = [v['mo'] for v in rows]
				if len(set(months)) == 1:
					ob_typ = 3
				else:
					days = [v['day_mo'] for v in rows]
					if len(set(days)) == 1:
						ob_typ = 2
					else:
						ob_typ = 1

			if rec_typ is None:
				rec_typ = ob_typ
				
			if delete_existing:
				db.Salt_recall_dat.delete().where(db.Salt_recall_dat.recall_rec_id == recall_rec_id).execute()

			db_lib.bulk_insert(project_base.db, db.Salt_recall_dat, rows)
			db.Salt_recall_rec.update(rec_typ=rec_typ).where(db.Salt_recall_rec.id == recall_rec_id).execute()
	
	def write(self):
		table = db.Salt_recall_rec
		order_by = db.Salt_recall_rec.id
		data = table.select().where(table.rec_typ != 4)

		module = get_salt_module()

		if data.count() > 0 and module.enabled and module.recall:
			with open(self.file_name, 'w') as file:
				file.write(self.get_meta_line())
				cols = [col(table.id),
						col(table.name, direction="left"),
						col(table.rec_typ),
						col("file", not_in_db=True, padding_override=utils.DEFAULT_STR_PAD, direction="left")]
				self.write_headers(file, cols)
				file.write("\n")

				i = 1
				for row in data.order_by(order_by):
					file_name = 'salt_{name}.dat'.format(name=row.name)
					file.write(utils.int_pad(i))
					file.write(utils.string_pad(row.name, direction="left"))
					file.write(utils.int_pad(row.rec_typ))
					file.write(utils.string_pad(file_name, direction="left"))
					file.write("\n")

					dir = os.path.dirname(self.file_name)
					self.write_data(row.data, os.path.join(dir, file_name))
					i += 1

	def write_data(self, data, file_name):
		table = db.Salt_recall_dat
		with open(file_name, 'w') as file:
			time_sim = simulation.Time_sim.get()			
			valid_data = []
			for row in data.order_by(db.Salt_recall_dat.yr, db.Salt_recall_dat.jday, db.Salt_recall_dat.id):
				valid_row = row.yr >= time_sim.yrc_start and row.yr <= time_sim.yrc_end
				rec_typ = row.recall_rec.rec_typ
				if valid_row and rec_typ == 1 and row.yr == time_sim.yrc_start: #daily
					valid_row = time_sim.day_start == 0 or row.jday >= time_sim.day_start
				elif valid_row and rec_typ == 1 and row.yr == time_sim.yrc_end: #daily
					valid_row = time_sim.day_end == 0 or row.jday <= time_sim.day_end

				if valid_row and rec_typ == 2 and row.yr == time_sim.yrc_start: #monthly
					rec_jday = datetime.datetime(row.yr, row.mo, 1).timetuple().tm_yday
					valid_row = time_sim.day_start == 0 or rec_jday >= time_sim.day_start	
				elif valid_row and rec_typ == 2 and row.yr == time_sim.yrc_end: #monthly
					rec_jday = datetime.datetime(row.yr, row.mo, 1).timetuple().tm_yday
					valid_row = time_sim.day_end == 0 or rec_jday <= time_sim.day_end

				if valid_row:
					valid_data.append(row)

			file.write(self.get_meta_line())
			file.write(str(len(valid_data)))
			file.write("\n")

			cols = [
				col(table.jday),
				col(table.mo),
				col(table.day_mo),
				col(table.yr),
				col(table.ob_typ),
				col(table.ob_name),
				col(table.so4),
				col(table.ca),
				col(table.mg),
				col(table.na),
				col(table.k),
				col(table.cl),
				col(table.co3),
				col(table.hco3)
			]

			self.write_headers(file, cols)
			file.write("\n")

			for row in valid_data:
				file.write(utils.int_pad(row.jday))
				file.write(utils.int_pad(row.mo))
				file.write(utils.int_pad(row.day_mo))
				file.write(utils.int_pad(row.yr))
				file.write(utils.string_pad(row.ob_typ))
				file.write(utils.string_pad(row.ob_name))
				file.write(utils.num_pad(row.so4))
				file.write(utils.num_pad(row.ca))
				file.write(utils.num_pad(row.mg))
				file.write(utils.num_pad(row.na))
				file.write(utils.num_pad(row.k))
				file.write(utils.num_pad(row.cl))
				file.write(utils.num_pad(row.co3))
				file.write(utils.num_pad(row.hco3))
				file.write("\n")


class Salt_atmo_cli(BaseFileModel):
	def __init__(self, file_name, version=None, swat_version=None):
		self.file_name = file_name
		self.version = version
		self.swat_version = swat_version

	def read(self):
		module = get_salt_module()

		csv_file = open(self.file_name, "r")

		dialect = csv.Sniffer().sniff(csv_file.readline())
		csv_file.seek(0)
		replace_commas = dialect is not None and dialect.delimiter != ','
		hasHeader = csv.Sniffer().has_header(csv_file.readline())
		csv_file.seek(0)

		csv_reader = csv.reader(csv_file, dialect)

		if hasHeader:
			headerLine = next(csv_reader)

		i = 0
		stations_to_ids = {}
		rows = []
		for row in Atmo_cli_sta.select():
			stations_to_ids[row.name] = row.id

		for val in csv_reader:
			if replace_commas:
				val = [item.replace(',', '.', 1) for item in val]

			if len(val) < 7:
				sys.exit('Invalid csv file format. Ensure your data has the following columns: name,month,year,nh4_rf,no3_rf,nh4_dry,no3_dry')
			name = utils.val_if_null(val[0], 'atmo{}'.format(i+1))
			month = utils.val_if_null(int(val[1]), 0)
			year = utils.val_if_null(int(val[2]), 0)
			so4_wet = utils.val_if_null(float(val[3]), 0)
			ca_wet = utils.val_if_null(float(val[4]), 0)
			mg_wet = utils.val_if_null(float(val[5]), 0)
			na_wet = utils.val_if_null(float(val[6]), 0)
			k_wet = utils.val_if_null(float(val[7]), 0)
			cl_wet = utils.val_if_null(float(val[8]), 0)
			co3_wet = utils.val_if_null(float(val[9]), 0)
			hco3_wet = utils.val_if_null(float(val[10]), 0)
			so4_dry = utils.val_if_null(float(val[11]), 0)
			ca_dry = utils.val_if_null(float(val[12]), 0)
			mg_dry = utils.val_if_null(float(val[13]), 0)
			na_dry = utils.val_if_null(float(val[14]), 0)
			k_dry = utils.val_if_null(float(val[15]), 0)
			cl_dry = utils.val_if_null(float(val[16]), 0)
			co3_dry = utils.val_if_null(float(val[17]), 0)
			hco3_dry = utils.val_if_null(float(val[18]), 0)

			if i == 0:
				if month == 0 and year == 0:
					module.atmo_timestep = 'aa'
				elif month == 0:
					module.atmo_timestep = 'yr'
				else:
					module.atmo_timestep = 'mo'

				module.save()

			if name not in stations_to_ids:
				sys.exit('Invalid atmo. station name: {}. Make sure the station name exists in your Climate/ Weather Stations / Atmospheric Deposition table'.format(name))

			timestep = 0
			if module.atmo_timestep == 'mo':
				timestep = int('{y}{m}'.format(y=year, m=str(month).rjust(2, '0')))
			elif module.atmo_timestep == 'yr':
				timestep = year

			data = {
				'sta_id': stations_to_ids[name],
				'timestep': timestep,
				'so4_wet': so4_wet,
				'ca_wet': ca_wet,
				'mg_wet': mg_wet,
				'na_wet': na_wet,
				'k_wet': k_wet,
				'cl_wet': cl_wet,
				'co3_wet': co3_wet,
				'hco3_wet': hco3_wet,
				'so4_dry': so4_dry,
				'ca_dry': ca_dry,
				'mg_dry': mg_dry,
				'na_dry': na_dry,
				'k_dry': k_dry,
				'cl_dry': cl_dry,
				'co3_dry': co3_dry,
				'hco3_dry': hco3_dry
			}

			rows.append(data)
			i += 1

		db.Salt_atmo_cli.delete().execute()
		db_lib.bulk_insert(project_base.db, db.Salt_atmo_cli, rows)

	def write_csv(self):
		module = get_salt_module()
		stations = Atmo_cli_sta.select().order_by(Atmo_cli_sta.name)
		values = db.Salt_atmo_cli.select().order_by(db.Salt_atmo_cli.timestep)
		query = prefetch(stations, values)

		with open(self.file_name, mode='w') as file:
			csv_writer = csv.writer(file, delimiter=',', lineterminator='\n', quotechar='"', quoting=csv.QUOTE_MINIMAL)

			headers = ['name', 'month', 'year', 'so4_wet', 'ca_wet', 'mg_wet', 'na_wet', 'k_wet', 'cl_wet', 'co3_wet', 'hco3_wet', 'so4_dry', 'ca_dry', 'mg_dry', 'na_dry', 'k_dry', 'cl_dry', 'co3_dry', 'hco3_dry']
			csv_writer.writerow(headers)

			for row in query:
				for val in row.salt_values:
					mo = 0
					yr = 0
					if module.atmo_timestep == 'mo':
						mo = int(str(val.timestep)[4:])
						yr = int(str(val.timestep)[:4])
					if module.atmo_timestep == 'yr':
						yr = val.timestep

					values = [row.name, mo, yr, val.so4_wet, val.ca_wet, val.mg_wet, val.na_wet, val.k_wet, val.cl_wet, val.co3_wet, val.hco3_wet, val.so4_dry, val.ca_dry, val.mg_dry, val.na_dry, val.k_dry, val.cl_dry, val.co3_dry, val.hco3_dry]
					csv_writer.writerow(values)

	def write(self):
		module = get_salt_module()
		stations = Atmo_cli_sta.select().order_by(Atmo_cli_sta.name)
		values = db.Salt_atmo_cli.select().order_by(db.Salt_atmo_cli.timestep)
		query = prefetch(stations, values)

		if stations.count() > 0 and values.count() > 0 and module.enabled and module.atmo:
			with open(self.file_name, 'w') as file:
				self.write_meta_line(file)
				file.write(" values for each climate station (atmo.cli)\n")
				file.write(" first set of values = rain concentration (g/m3)\n")
				file.write(" second set of values = dry deposits (kg/ha)\n")
				header_cols = [col('NUM_STA', direction="right", padding_override=10, not_in_db=True),
							   col('TIMESTEP', direction="right", padding_override=10, not_in_db=True),
							   col('MO_INIT', direction="right", padding_override=10, not_in_db=True),
							   col('YR_INIT', direction="right", padding_override=10, not_in_db=True),
							   col('NUM_TS', direction="right", padding_override=10, not_in_db=True)]
				self.write_headers(file, header_cols)
				file.write("\n")

				first_sta = query[0]
				timestep = first_sta.salt_values[0].timestep
				mo_init = 0
				yr_init = 0
				num_aa = 0 if module.atmo_timestep == 'aa' else len(first_sta.salt_values)

				if module.atmo_timestep == 'mo':
					mo_init = int(str(timestep)[4:])
					yr_init = int(str(timestep)[:4])
				if module.atmo_timestep == 'yr':
					yr_init = timestep

				row_cols = [col(stations.count(), direction="right", padding_override=10),
							col(module.atmo_timestep, direction="right", padding_override=10),
							col(mo_init, direction="right", padding_override=10),
							col(yr_init, direction="right", padding_override=10),
							col(num_aa, direction="right", padding_override=10)]
				self.write_row(file, row_cols)
				file.write("\n")

				for row in query:
					file.write(row.name)
					file.write("\n")

					so4_wet_line = 'so4   '
					ca_wet_line = 'ca    '
					mg_wet_line = 'mg    '
					na_wet_line = 'na    '
					k_wet_line = 'k     '
					cl_wet_line = 'cl    '
					co3_wet_line = 'co3   '
					hco3_wet_line = 'hco3  '
					so4_dry_line = 'so4   '
					ca_dry_line = 'ca    '
					mg_dry_line = 'mg    '
					na_dry_line = 'na    '
					k_dry_line = 'k     '
					cl_dry_line = 'cl    '
					co3_dry_line = 'co3   '
					hco3_dry_line = 'hco3  '
					for val in row.salt_values:
						so4_wet_line = '{l}{v}'.format(l=so4_wet_line, v=utils.num_pad(val.so4_wet, 2, 9))
						ca_wet_line = '{l}{v}'.format(l=ca_wet_line, v=utils.num_pad(val.ca_wet, 2, 9))
						mg_wet_line = '{l}{v}'.format(l=mg_wet_line, v=utils.num_pad(val.mg_wet, 2, 9))
						na_wet_line = '{l}{v}'.format(l=na_wet_line, v=utils.num_pad(val.na_wet, 2, 9))
						k_wet_line = '{l}{v}'.format(l=k_wet_line, v=utils.num_pad(val.k_wet, 2, 9))
						cl_wet_line = '{l}{v}'.format(l=cl_wet_line, v=utils.num_pad(val.cl_wet, 2, 9))
						co3_wet_line = '{l}{v}'.format(l=co3_wet_line, v=utils.num_pad(val.co3_wet, 2, 9))
						hco3_wet_line = '{l}{v}'.format(l=hco3_wet_line, v=utils.num_pad(val.hco3_wet, 2, 9))
						so4_dry_line = '{l}{v}'.format(l=so4_dry_line, v=utils.num_pad(val.so4_dry, 2, 9))
						ca_dry_line = '{l}{v}'.format(l=ca_dry_line, v=utils.num_pad(val.ca_dry, 2, 9))
						mg_dry_line = '{l}{v}'.format(l=mg_dry_line, v=utils.num_pad(val.mg_dry, 2, 9))
						na_dry_line = '{l}{v}'.format(l=na_dry_line, v=utils.num_pad(val.na_dry, 2, 9))
						k_dry_line = '{l}{v}'.format(l=k_dry_line, v=utils.num_pad(val.k_dry, 2, 9))
						cl_dry_line = '{l}{v}'.format(l=cl_dry_line, v=utils.num_pad(val.cl_dry, 2, 9))
						co3_dry_line = '{l}{v}'.format(l=co3_dry_line, v=utils.num_pad(val.co3_dry, 2, 9))
						hco3_dry_line = '{l}{v}'.format(l=hco3_dry_line, v=utils.num_pad(val.hco3_dry, 2, 9))

					file.write(so4_wet_line + '\n')
					file.write(ca_wet_line + '\n')
					file.write(mg_wet_line + '\n')
					file.write(na_wet_line + '\n')
					file.write(k_wet_line + '\n')
					file.write(cl_wet_line + '\n')
					file.write(co3_wet_line + '\n')
					file.write(hco3_wet_line + '\n')
					file.write(so4_dry_line + '\n')
					file.write(ca_dry_line + '\n')
					file.write(mg_dry_line + '\n')
					file.write(na_dry_line + '\n')
					file.write(k_dry_line + '\n')
					file.write(cl_dry_line + '\n')
					file.write(co3_dry_line + '\n')
					file.write(hco3_dry_line + '\n')
					