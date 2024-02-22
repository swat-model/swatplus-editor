from .base import BaseFileModel, FileColumn as col
from peewee import *
import database.project.climate as db
from helpers import utils


class Weather_sta_cli(BaseFileModel):
	def __init__(self, file_name, version=None, swat_version=None):
		self.file_name = file_name
		self.version = version
		self.swat_version = swat_version

	def read(self):
		raise NotImplementedError('Reading not implemented yet.')

	def write(self):
		table = db.Weather_sta_cli
		
		query = (table.select(table.name,
							  db.Weather_wgn_cli.name.alias("wgn"),
							  table.pcp,
							  table.tmp,
							  table.slr,
							  table.hmd,
							  table.wnd,
							  table.pet,
							  table.atmo_dep)
					  .join(db.Weather_wgn_cli, JOIN.LEFT_OUTER)
					  .order_by(table.name))

		cols = [col(table.name, direction="left"),
				col(table.wgn, query_alias="wgn"),
				col(table.pcp, padding_override=25, text_if_null="sim"),
				col(table.tmp, padding_override=25, text_if_null="sim"),
				col(table.slr, padding_override=25, text_if_null="sim"),
				col(table.hmd, padding_override=25, text_if_null="sim"),
				col(table.wnd, padding_override=25, text_if_null="sim"),
				col(table.pet, padding_override=25, text_if_null="null"),
				col(table.atmo_dep, text_if_null="null")]
		self.write_query(query, cols)


class Weather_wgn_cli(BaseFileModel):
	def __init__(self, file_name, version=None, swat_version=None):
		self.file_name = file_name
		self.version = version
		self.swat_version = swat_version

	def read(self):
		raise NotImplementedError('Reading not implemented yet.')

	def write(self):
		wgn = db.Weather_wgn_cli.select().order_by(db.Weather_wgn_cli.name)
		months = db.Weather_wgn_cli_mon.select().order_by(db.Weather_wgn_cli_mon.month)
		query = prefetch(wgn, months)

		if wgn.count() > 0:
			with open(self.file_name, 'w') as file:
				self.write_meta_line(file)

				for row in query:
					row_cols = [col(row.name, direction="left", padding_override=25),
								col(row.lat),
								col(row.lon),
								col(row.elev),
								col(row.rain_yrs)]
					self.write_row(file, row_cols)
					file.write("\n")

					mt = db.Weather_wgn_cli_mon
					mon_cols = [col(mt.tmp_max_ave),
								col(mt.tmp_min_ave),
								col(mt.tmp_max_sd),
								col(mt.tmp_min_sd),
								col(mt.pcp_ave),
								col(mt.pcp_sd),
								col(mt.pcp_skew),
								col(mt.wet_dry),
								col(mt.wet_wet),
								col(mt.pcp_days),
								col(mt.pcp_hhr),
								col(mt.slr_ave),
								col(mt.dew_ave),
								col(mt.wnd_ave)]
					self.write_headers(file, mon_cols)
					file.write("\n")

					for month in row.monthly_values:
						month_row_cols = [col(month.tmp_max_ave),
										  col(month.tmp_min_ave),
										  col(month.tmp_max_sd),
										  col(month.tmp_min_sd),
										  col(month.pcp_ave),
										  col(month.pcp_sd),
										  col(month.pcp_skew),
										  col(month.wet_dry),
										  col(month.wet_wet),
										  col(month.pcp_days),
										  col(month.pcp_hhr),
										  col(month.slr_ave),
										  col(month.dew_ave),
										  col(month.wnd_ave)]
						self.write_row(file, month_row_cols)
						file.write("\n")


class Atmo_cli(BaseFileModel):
	def __init__(self, file_name, version=None, swat_version=None):
		self.file_name = file_name
		self.version = version
		self.swat_version = swat_version

	def read(self):
		raise NotImplementedError('Reading not implemented yet.')

	def write(self):
		atmo = db.Atmo_cli.get_or_none()
		stations = db.Atmo_cli_sta.select().order_by(db.Atmo_cli_sta.name)
		values = db.Atmo_cli_sta_value.select().order_by(db.Atmo_cli_sta_value.timestep)
		query = prefetch(stations, values)

		if atmo is not None and stations.count() > 0:
			with open(self.file_name, 'w') as file:
				self.write_meta_line(file)
				header_cols = [col('NUM_STA', direction="right", padding_override=10, not_in_db=True),
							   col('TIMESTEP', direction="right", padding_override=10, not_in_db=True),
							   col('MO_INIT', direction="right", padding_override=10, not_in_db=True),
							   col('YR_INIT', direction="right", padding_override=10, not_in_db=True),
							   col('NUM_TS', direction="right", padding_override=10, not_in_db=True)]
				self.write_headers(file, header_cols)
				file.write("\n")

				row_cols = [col(stations.count(), direction="right", padding_override=10),
							col(atmo.timestep, direction="right", padding_override=10),
							col(atmo.mo_init, direction="right", padding_override=10),
							col(atmo.yr_init, direction="right", padding_override=10),
							col(atmo.num_aa, direction="right", padding_override=10)]
				self.write_row(file, row_cols)
				file.write("\n")

				for row in query:
					file.write(row.name)
					file.write("\n")

					nh4_wet_line = ''
					no3_wet_line = ''
					nh4_dry_line = ''
					no3_dry_line = ''
					for val in row.values:
						nh4_wet_line = '{l}{v}'.format(l=nh4_wet_line, v=utils.num_pad(val.nh4_wet, 2, 9))
						no3_wet_line = '{l}{v}'.format(l=no3_wet_line, v=utils.num_pad(val.no3_wet, 2, 9))
						nh4_dry_line = '{l}{v}'.format(l=nh4_dry_line, v=utils.num_pad(val.nh4_dry, 2, 9))
						no3_dry_line = '{l}{v}'.format(l=no3_dry_line, v=utils.num_pad(val.no3_dry, 2, 9))

					file.write(nh4_wet_line)
					file.write('           (NH4_RF)')
					file.write("\n")

					file.write(no3_wet_line)
					file.write('           (NO3_RF)')
					file.write("\n")

					file.write(nh4_dry_line)
					file.write('           (NH4_DRY)')
					file.write("\n")

					file.write(no3_dry_line)
					file.write('           (NO3_DRY)')
					file.write("\n")
