from .base import BaseFileModel, FileColumn as col
import database.project.salts as db
from helpers import utils
import os.path
from database.project import base as project_base, simulation
from database import lib as db_lib
import csv
import datetime


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

		if data.count() > 0:
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