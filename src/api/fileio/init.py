from .base import BaseFileModel, FileColumn as col
from peewee import *
from helpers import utils
from database.project import soils
from database.project.simulation import Constituents_cs
from database.project.salts import Salt_hru_ini_cs, Salt_module
import database.project.init as db


class Plant_ini(BaseFileModel):
	def __init__(self, file_name, version=None, swat_version=None):
		self.file_name = file_name
		self.version = version
		self.swat_version = swat_version

	def read(self):
		raise NotImplementedError('Reading not implemented yet.')

	def write(self):
		table = db.Plant_ini
		order_by = db.Plant_ini.id

		if table.select().count() > 0:
			with open(self.file_name, 'w') as file:
				file.write(self.get_meta_line())
				file.write(utils.string_pad("pcom_name", direction="left"))
				file.write(utils.int_pad("plt_cnt"))
				file.write(utils.int_pad("rot_yr_ini"))
				file.write(utils.string_pad("plt_name", default_pad=utils.DEFAULT_KEY_PAD))
				file.write(utils.code_pad("lc_status"))
				file.write(utils.num_pad("lai_init"))
				file.write(utils.num_pad("bm_init"))
				file.write(utils.num_pad("phu_init"))
				file.write(utils.num_pad("plnt_pop"))
				file.write(utils.num_pad("yrs_init"))
				file.write(utils.num_pad("rsd_init"))
				file.write("\n")

				for row in table.select().order_by(order_by):
					file.write(utils.string_pad(row.name, direction="left"))
					file.write(utils.int_pad(row.plants.count()))
					file.write(utils.int_pad(row.rot_yr_ini))
					file.write("\n")

					for plant in row.plants:
						file.write(utils.string_pad("", text_if_null=""))
						file.write(utils.string_pad("", text_if_null="", default_pad=utils.DEFAULT_INT_PAD))
						file.write(utils.key_name_pad(plant.plnt_name))
						utils.write_bool_yn(file, plant.lc_status)
						file.write(utils.num_pad(plant.lai_init))
						file.write(utils.num_pad(plant.bm_init))
						file.write(utils.num_pad(plant.phu_init))
						file.write(utils.num_pad(plant.plnt_pop))
						file.write(utils.num_pad(plant.yrs_init))
						file.write(utils.num_pad(plant.rsd_init))
						file.write("\n")


class Om_water_ini(BaseFileModel):
	def __init__(self, file_name, version=None, swat_version=None):
		self.file_name = file_name
		self.version = version
		self.swat_version = swat_version

	def read(self):
		raise NotImplementedError('Reading not implemented yet.')

	def write(self):
		self.write_default_table(db.Om_water_ini, ignore_id_col=True)


class Soil_plant_ini(BaseFileModel):
	def __init__(self, file_name, version=None, swat_version=None):
		self.file_name = file_name
		self.version = version
		self.swat_version = swat_version

	def read(self):
		raise NotImplementedError('Reading not implemented yet.')

	def write(self):
		table = db.Soil_plant_ini
		query = (table.select(table.name,
							  table.sw_frac,
							  soils.Nutrients_sol.name.alias("nutrients"),
							  db.Pest_hru_ini.name.alias("pest"),
							  db.Path_hru_ini.name.alias("path"),
							  db.Hmet_hru_ini.name.alias("hmet"),
							  Salt_hru_ini_cs.name.alias("salt"))
					  .join(soils.Nutrients_sol, JOIN.LEFT_OUTER)
					  .switch(table)
					  .join(db.Pest_hru_ini, JOIN.LEFT_OUTER)
					  .switch(table)
					  .join(db.Path_hru_ini, JOIN.LEFT_OUTER)
					  .switch(table)
					  .join(db.Hmet_hru_ini, JOIN.LEFT_OUTER)
					  .switch(table)
					  .join(Salt_hru_ini_cs, JOIN.LEFT_OUTER)
					  .order_by(table.id))

		cols = [col(table.name, direction="left"),
				col(table.sw_frac),
				col(table.nutrients, query_alias="nutrients"),
				col("pest", not_in_db=True, value_override="null"),
				col("path", not_in_db=True, value_override="null"),
				col("hmet", not_in_db=True, value_override="null"),
				col("salt", not_in_db=True, value_override="null")]
		self.write_query(query, cols)

		module, created = Salt_module.get_or_create(id=1)
		if module.enabled or db.Pest_hru_ini.select().count() > 0 or db.Path_hru_ini.select().count() > 0 or db.Hmet_hru_ini.select().count() > 0:
			self.file_name = self.file_name + "_cs"
			cols_cs = [col(table.name, direction="left"),
					col(table.pest, query_alias="pest"),
					col(table.path, query_alias="path"),
					col(table.hmet, query_alias="hmet"),
					col(table.salt_cs, query_alias="salt"),
					col("cs", not_in_db=True, value_override="null")]
			self.write_query(query, cols_cs)



class Pest_hru_ini(BaseFileModel):
	def __init__(self, file_name, version=None, swat_version=None):
		self.file_name = file_name
		self.version = version
		self.swat_version = swat_version

	def read(self):
		raise NotImplementedError('Reading not implemented yet.')

	def write(self):
		table = db.Pest_hru_ini.select().order_by(db.Pest_hru_ini.id)
		items = db.Pest_hru_ini_item.select().order_by(db.Pest_hru_ini_item.name)
		query = prefetch(table, items)

		if table.count() > 0 and Constituents_cs.select().count() > 0:
			constits_row = Constituents_cs.select().first()
			constits = [] if constits_row.pest_coms is None else sorted(constits_row.pest_coms.split(','))
			if len(constits) > 0:
				with open(self.file_name, 'w') as file:
					file.write(self.get_meta_line())

					file.write(utils.string_pad("name", direction="left", default_pad=25))
					file.write(utils.string_pad("SOIL(ppm)", direction="left", default_pad=25))
					file.write(utils.string_pad("PLANT", direction="left", default_pad=25))
					file.write("\n")

					for row in query:
						file.write(utils.string_pad(row.name, direction="left", default_pad=25))
						file.write("\n")

						for item in row.pest_hrus:
							file.write(" ")
							file.write(utils.string_pad(item.name.name, direction="left", default_pad=24))
							file.write(utils.num_pad(item.soil, decimals=3, direction="left", default_pad=25))
							file.write(utils.num_pad(item.plant, decimals=3, direction="left", default_pad=25))
							file.write("\n")


class Pest_water_ini(BaseFileModel):
	def __init__(self, file_name, version=None, swat_version=None):
		self.file_name = file_name
		self.version = version
		self.swat_version = swat_version

	def read(self):
		raise NotImplementedError('Reading not implemented yet.')

	def write(self):
		table = db.Pest_water_ini.select().order_by(db.Pest_water_ini.id)
		items = db.Pest_water_ini_item.select().order_by(db.Pest_water_ini_item.name)
		query = prefetch(table, items)

		if table.count() > 0 and Constituents_cs.select().count() > 0:
			constits_row = Constituents_cs.select().first()
			constits = [] if constits_row.pest_coms is None else sorted(constits_row.pest_coms.split(','))
			if len(constits) > 0:
				with open(self.file_name, 'w') as file:
					file.write(self.get_meta_line())

					file.write(utils.string_pad("name", direction="left", default_pad=25))
					file.write(utils.string_pad("water", direction="left", default_pad=25))
					file.write(utils.string_pad("benthic", direction="left", default_pad=25))
					file.write("\n")

					for row in query:
						file.write(utils.string_pad(row.name, direction="left", default_pad=25))
						file.write("\n")

						for item in row.pest_waters:
							file.write(" ")
							file.write(utils.string_pad(item.name.name, direction="left", default_pad=24))
							file.write(utils.num_pad(item.water, decimals=3, direction="left", default_pad=25))
							file.write(utils.num_pad(item.benthic, decimals=3, direction="left", default_pad=25))
							file.write("\n")


class Path_hru_ini(BaseFileModel):
	def __init__(self, file_name, version=None, swat_version=None):
		self.file_name = file_name
		self.version = version
		self.swat_version = swat_version

	def read(self):
		raise NotImplementedError('Reading not implemented yet.')

	def write(self):
		table = db.Path_hru_ini.select().order_by(db.Path_hru_ini.id)
		items = db.Path_hru_ini_item.select().order_by(db.Path_hru_ini_item.name)
		query = prefetch(table, items)

		if table.count() > 0 and Constituents_cs.select().count() > 0:
			constits_row = Constituents_cs.select().first()
			constits = [] if constits_row.path_coms is None else sorted(constits_row.path_coms.split(','))
			if len(constits) > 0:
				with open(self.file_name, 'w') as file:
					file.write(self.get_meta_line())

					file.write(utils.string_pad("name", direction="left", default_pad=25))
					file.write(utils.string_pad("SOIL(cfu/ml)", direction="left", default_pad=25))
					file.write(utils.string_pad("PLANT", direction="left", default_pad=25))
					file.write("\n")

					for row in query:
						file.write(utils.string_pad(row.name, direction="left", default_pad=25))
						file.write("\n")

						for item in row.path_hrus:
							file.write(" ")
							file.write(utils.string_pad(item.name.name, direction="left", default_pad=24))
							file.write(utils.num_pad(item.soil, decimals=3, direction="left", default_pad=25))
							file.write(utils.num_pad(item.plant, decimals=3, direction="left", default_pad=25))
							file.write("\n")


class Path_water_ini(BaseFileModel):
	def __init__(self, file_name, version=None, swat_version=None):
		self.file_name = file_name
		self.version = version
		self.swat_version = swat_version

	def read(self):
		raise NotImplementedError('Reading not implemented yet.')

	def write(self):
		table = db.Path_water_ini.select().order_by(db.Path_water_ini.id)
		items = db.Path_water_ini_item.select().order_by(db.Path_water_ini_item.name)
		query = prefetch(table, items)

		if table.count() > 0 and Constituents_cs.select().count() > 0:
			constits_row = Constituents_cs.select().first()
			constits = [] if constits_row.path_coms is None else sorted(constits_row.path_coms.split(','))
			if len(constits) > 0:
				with open(self.file_name, 'w') as file:
					file.write(self.get_meta_line())

					file.write(utils.string_pad("name", direction="left", default_pad=25))
					file.write(utils.string_pad("water", direction="left", default_pad=25))
					file.write(utils.string_pad("benthic", direction="left", default_pad=25))
					file.write("\n")

					for row in query:
						file.write(utils.string_pad(row.name, direction="left", default_pad=25))
						file.write("\n")

						for item in row.path_waters:
							file.write(" ")
							file.write(utils.string_pad(item.name.name, direction="left", default_pad=24))
							file.write(utils.num_pad(item.water, decimals=3, direction="left", default_pad=25))
							file.write(utils.num_pad(item.benthic, decimals=3, direction="left", default_pad=25))
							file.write("\n")
