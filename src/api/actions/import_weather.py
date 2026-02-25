from helpers.executable_api import ExecutableApi, Unbuffered
from database.project import base as project_base
from database.project.setup import SetupProjectDatabase
from database.project.config import Project_config
from database.project.climate import Weather_file, Weather_sta_cli, Weather_sta_cli_scale, Weather_wgn_cli, Weather_wgn_cli_mon, Atmo_cli, Atmo_cli_sta, Atmo_cli_sta_value
from database.project.connect import Aquifer_con, Channel_con, Rout_unit_con, Reservoir_con, Recall_con, Hru_con, Exco_con, Chandeg_con, Hru_lte_con
from database.project.simulation import Time_sim
from database import lib as db_lib
from helpers import utils
from fileio import base as fileio

import sys
import os, os.path
import math
import argparse
import time, datetime
import sqlite3
from peewee import *
import csv


HMD_TXT = "hmd.txt"
PCP_TXT = "pcp.txt"
SLR_TXT = "slr.txt"
TMP_TXT = "tmp.txt"
WND_TXT = "wnd.txt"
PET_TXT = "pet.txt"

HMD_TXT2 = "rh.txt"
SLR_TXT2 = "solar.txt"
WND_TXT2 = "wind.txt"

HMD_CLI = "hmd.cli"
PCP_CLI = "pcp.cli"
SLR_CLI = "slr.cli"
TMP_CLI = "tmp.cli"
WND_CLI = "wnd.cli"
PET_CLI = "pet.cli"

WEATHER_DESC = {
	"hmd": "Relative humidity",
	"pcp": "Precipitation",
	"slr": "Solar radiation",
	"tem": "Temperature",
	"tmp": "Temperature",
	"wnd": "Wind speed",
	"pet": "Potential evapotranspiration"
}

def weather_sta_name(lat, lon, prefix = 's', mult = 1000):
	latp = "n" if lat >= 0 else "s"
	lonp = "e" if lon >= 0 else "w"
	name = "{prefix}{lat}{latp}{lon}{lonp}".format(prefix=prefix, lat=abs(round(lat * mult)), latp=latp, lon=abs(round(lon * mult)), lonp=lonp)
	return name


def update_closest_lat_lon(update_table, update_field, select_table, select_field="id", wtype=None):
	where = ""
	if wtype is not None:
		where = "where t2.type = ?"

	sql = """with r as
		(
			select t1.id as con_id, t2.{select_field} as wid, ((t1.lat - t2.lat) * (t1.lat - t2.lat) + (t1.lon - t2.lon) * (t1.lon - t2.lon)) as ord
			from {update_table} t1, {select_table} t2 {where}
			group by con_id
			having min(ord) or ord = 0
			order by con_id, ord
		)
		update {update_table} set {update_field} = (select wid from r where con_id = {update_table}.id)""".format(
			update_table=update_table, update_field=update_field, select_table=select_table, select_field=select_field, where=where)
	
	if wtype is not None:
		project_base.db.execute_sql(sql, (wtype,))
	else:
		project_base.db.execute_sql(sql)


def closest_lat_lon(db, table_name, lat, lon, wtype=None):
	"""
	See: http://stackoverflow.com/a/7472230
	For explanation of getting the closest lat,long
	"""
	#if not db_lib.exists_table(sqlite3.connect(db), table_name):
		#raise ValueError("Table {table} does not exist in {file}.".format(table=table_name, file=db))

	fudge = math.pow(math.cos(math.radians(lat)), 2)
	q = "order by ((? - lat) * (? - lat) + (? - lon) * (? - lon) * ?) limit 1"
	if wtype is None:
		cursor = project_base.db.execute_sql(
			"select id from {table} {q}".format(table=table_name, q=q),
			(lat, lat, lon, lon, fudge))
	else:
		cursor = project_base.db.execute_sql(
			"select filename from {table} where type = ? {q}".format(table=table_name, q=q),
			(wtype, lat, lat, lon, lon, fudge))
	res = cursor.fetchone()
	
	if res is None:
		return None
	
	return res[0]


class WeatherImport(ExecutableApi):
	def __init__(self, project_db_file, delete_existing, create_stations):
		self.__abort = False
		SetupProjectDatabase.init(project_db_file)
		self.project_db_file = project_db_file
		self.project_db = project_base.db
		self.create_stations = create_stations
		self.coords_to_stations = {}

		if delete_existing:
			self.delete_existing()

	def import_data(self):
		try:
			config = Project_config.get()
			
			weather_data_dir = utils.full_path(self.project_db_file, config.weather_data_dir)
			if not os.path.exists(weather_data_dir):
				sys.exit('Weather data directory {dir} does not exist.'.format(dir=weather_data_dir))

			self.add_weather_files(weather_data_dir)

			if self.create_stations:
				self.create_weather_stations(20, 45)
				self.match_stations(65)
			else:
				self.match_files_to_stations(20, 45)
		except Project_config.DoesNotExist:
			sys.exit('Could not retrieve project configuration from database')

	def delete_existing(self):
		Weather_file.delete().execute()
		Weather_sta_cli.delete().execute()

	def match_stations(self, start_prog):
		self.emit_progress(start_prog, "Adding weather stations to spatial connection tables...")
		wst_col = "wst_id"
		wst_table = "weather_sta_cli"
		update_closest_lat_lon("aquifer_con", wst_col, wst_table)
		update_closest_lat_lon("channel_con", wst_col, wst_table)
		update_closest_lat_lon("chandeg_con", wst_col, wst_table)
		update_closest_lat_lon("rout_unit_con", wst_col, wst_table)
		update_closest_lat_lon("reservoir_con", wst_col, wst_table)
		update_closest_lat_lon("recall_con", wst_col, wst_table)
		update_closest_lat_lon("exco_con", wst_col, wst_table)
		update_closest_lat_lon("hru_con", wst_col, wst_table)
		update_closest_lat_lon("hru_lte_con", wst_col, wst_table)
		update_closest_lat_lon("weather_sta_cli", "wgn_id", "weather_wgn_cli")

		"""self.match_stations_table(Aquifer_con, "aquifer connections", start_prog)
		self.match_stations_table(Channel_con, "channel connections", start_prog + 5)
		self.match_stations_table(Chandeg_con, "channel connections", start_prog + 5)
		self.match_stations_table(Rout_unit_con, "routing unit connections", start_prog + 10)
		self.match_stations_table(Reservoir_con, "reservoir connections", start_prog + 15)
		self.match_stations_table(Recall_con, "recall connections", start_prog + 20)
		self.match_stations_table(Exco_con, "exco connections", start_prog + 20)
		self.match_stations_table(Hru_con, "hru connections", start_prog + 25)
		self.match_stations_table(Hru_lte_con, "hru connections", start_prog + 25)
		self.match_wgn(start_prog + 30)"""

	def match_stations_table(self, table, name, prog):
		self.emit_progress(prog, "Adding weather stations to {name}...".format(name=name))
		with project_base.db.atomic():
			for row in table.select():
				coords_key = "{lat},{lon}".format(lat=row.lat, lon=row.lon)
				id = self.coords_to_stations.get(coords_key, None)
				if id is None:
					id = closest_lat_lon(project_base.db, "weather_sta_cli", row.lat, row.lon)
					self.coords_to_stations[coords_key] = id

				row.wst = id
				row.save()

	def match_wgn(self, prog):
		if Weather_wgn_cli.select().count() > 0:
			self.emit_progress(prog, "Matching wgn to weather stations...")
			with project_base.db.atomic():
				for row in Weather_sta_cli.select():
					id = closest_lat_lon(project_base.db, "weather_wgn_cli", row.lat, row.lon)
					row.wgn = id
					row.save()

	def create_weather_stations(self, start_prog, total_prog):  # total_prog is the total progress percentage available for this method
		if self.__abort: return

		stations = []
		cursor = project_base.db.execute_sql("select lat, lon from weather_file group by lat, lon")
		data = cursor.fetchall()
		records = len(data)
		i = 1
		for row in data:
			if self.__abort: return

			lat = row[0]
			lon = row[1]
			name = weather_sta_name(lat, lon)

			prog = round(i * total_prog / records) + start_prog
			self.emit_progress(prog, "Creating weather station {name}...".format(name=name))

			try:
				existing = Weather_sta_cli.get(Weather_sta_cli.name == name)
			except Weather_sta_cli.DoesNotExist:
				station = {
					"name": name,
					"atmo_dep": None,
					"lat": lat,
					"lon": lon,
					
				}

				"""
					"hmd": closest_lat_lon(project_base.db, "weather_file", lat, lon, "hmd"),
					"pcp": closest_lat_lon(project_base.db, "weather_file", lat, lon, "pcp"),
					"slr": closest_lat_lon(project_base.db, "weather_file", lat, lon, "slr"),
					"tmp": closest_lat_lon(project_base.db, "weather_file", lat, lon, "tmp"),
					"wnd": closest_lat_lon(project_base.db, "weather_file", lat, lon, "wnd")
					"""

				stations.append(station)
			i += 1

		db_lib.bulk_insert(project_base.db, Weather_sta_cli, stations)
		self.match_files_to_stations(45, 45)

	def match_files_to_stations(self, start_prog, total_prog):
		self.emit_progress(start_prog, "Matching files to weather station...")
		update_closest_lat_lon("weather_sta_cli", "hmd", "weather_file", "filename", "hmd")
		update_closest_lat_lon("weather_sta_cli", "pcp", "weather_file", "filename", "pcp")
		update_closest_lat_lon("weather_sta_cli", "slr", "weather_file", "filename", "slr")
		update_closest_lat_lon("weather_sta_cli", "tmp", "weather_file", "filename", "tmp")
		update_closest_lat_lon("weather_sta_cli", "wnd", "weather_file", "filename", "wnd")
		update_closest_lat_lon("weather_sta_cli", "pet", "weather_file", "filename", "pet")
		"""with project_base.db.atomic():
			query = Weather_sta_cli.select()
			records = query.count()
			i = 1
			for row in query:
				prog = round(i * total_prog / records) + start_prog
				self.emit_progress(prog, "Matching files to weather station {name}...".format(name=row.name))
				row.hmd = closest_lat_lon(project_base.db, "weather_file", row.lat, row.lon, "hmd")
				row.pcp = closest_lat_lon(project_base.db, "weather_file", row.lat, row.lon, "pcp")
				row.slr = closest_lat_lon(project_base.db, "weather_file", row.lat, row.lon, "slr")
				row.tmp = closest_lat_lon(project_base.db, "weather_file", row.lat, row.lon, "tmp")
				row.wnd = closest_lat_lon(project_base.db, "weather_file", row.lat, row.lon, "wnd")
				row.save()
				i += 1"""

	def add_weather_files(self, dir):
		if self.__abort: return
		hmd_start, hmd_end = self.add_weather_files_type(os.path.join(dir, HMD_CLI), "hmd", 0)
		if self.__abort: return
		pcp_start, pcp_end = self.add_weather_files_type(os.path.join(dir, PCP_CLI), "pcp", 5)
		if self.__abort: return
		slr_start, slr_end = self.add_weather_files_type(os.path.join(dir, SLR_CLI), "slr", 10)
		if self.__abort: return
		tmp_start, tmp_end = self.add_weather_files_type(os.path.join(dir, TMP_CLI), "tmp", 15)
		if self.__abort: return
		wnd_start, wnd_end = self.add_weather_files_type(os.path.join(dir, WND_CLI), "wnd", 20)
		if self.__abort: return
		pet_start, pet_end = self.add_weather_files_type(os.path.join(dir, PET_CLI), "pet", 25)

		starts = [hmd_start, pcp_start, slr_start, tmp_start, wnd_start, pet_start]
		ends = [hmd_end, pcp_end, slr_end, tmp_end, wnd_end, pet_end]
		starts = [v for v in starts if v is not None]
		ends = [v for v in ends if v is not None]
		if len(starts) > 0:
			"""ustarts = list(dict.fromkeys(starts))
			uends = list(dict.fromkeys(ends))
			if len(ustarts) > 1 or len(uends) > 1:
				raise ValueError("Dates in weather files do not match. Make sure all weather files have the same starting and ending dates.")
			"""
			start_date = max(starts)
			end_date = min(ends)
			st = start_date.timetuple()
			start_day = st.tm_yday if st.tm_yday > 1 else 0
			start_year = st.tm_year

			et = end_date.timetuple()
			end_day = 0 if et.tm_mon == 12 and et.tm_mday == 31 else et.tm_yday
			end_year = et.tm_year

			Time_sim.update(day_start=start_day, yrc_start=start_year, day_end=end_day, yrc_end=end_year).execute()

		if self.__abort: return
		"""warnings = []
		warnings.append(hmd_res)
		warnings.append(pcp_res)
		warnings.append(slr_res)
		warnings.append(tmp_res)
		warnings.append(wnd_res)
		has_warnings = any(x is not None for x in warnings)

		if has_warnings:
			with open(os.path.join( dir, "__warnings.txt"), 'w+') as warning_file:
				for w in warnings:
					if w is not None:
						warning_file.write(w)
						warning_file.write("\n")"""

	def add_weather_files_type(self, source_file, weather_type, prog):
		start_date = None
		end_date = None
		starts = []
		ends = []
		if os.path.exists(source_file):
			self.emit_progress(prog, "Inserting {type} files and coordinates...".format(type=weather_type))
			weather_files = []
			dir = os.path.dirname(source_file)
			try:
				with open(source_file, "r") as source_data:
					i = 0
					for line in source_data:
						if self.__abort:
							break

						if i > 1:
							station_name = line.strip('\n')
							station_file = os.path.join(dir, station_name)
							if not os.path.exists(station_file):
								raise IOError("File {file} not found. Weather data import aborted.".format(file=station_file))

							existing = Weather_file.get_or_none((Weather_file.filename == station_name) & (Weather_file.type == weather_type))
							if existing is None:
								try:
									with open(station_file, "r") as station_data:
										j = 0
										for sline in station_data:
											if j == 2:
												station_info = sline.strip().split()
												if len(station_info) < 4:
													raise ValueError("Invalid value at line {ln} of {file}. Expecting nbyr, tstep, lat, long, elev values separated by a space.".format(ln=str(j + 1), file=station_file))

												lat = float(station_info[2])
												lon = float(station_info[3])

												file = {
													"filename": station_name,
													"type": weather_type,
													"lat": lat,
													"lon": lon
												}
												weather_files.append(file)
											elif j == 3:
												begin_data = sline.strip().split()
												if len(begin_data) < 3:
													raise ValueError("Invalid value at line {ln} of {file}. Expecting year, julian day, and weather value separated by a space.".format(ln=str(j + 1), file=station_file))

												date = datetime.datetime(int(begin_data[0]), 1, 1)
												current_start_date = date + datetime.timedelta(days=int(begin_data[1])-1)
												#if start_date is not None and current_start_date != start_date:
												#	raise ValueError("Start dates in weather files do not match. Make sure all weather files have the same starting and ending dates.")

												#start_date = current_start_date
												starts.append(current_start_date)
											elif j > 3:
												break

											j += 1

										#non_empty_lines = [sline for sline in station_data if sline]
										#last_line = non_empty_lines[len(non_empty_lines)-1].strip().split()
										last_line = list(filter(str.strip, station_data))[-1].strip().split()
										
										date = datetime.datetime(int(last_line[0]), 1, 1)
										current_end_date = date + datetime.timedelta(days=int(last_line[1])-1)
										#if end_date is not None and current_end_date != end_date:
										#	raise ValueError("Ending dates in weather files do not match. Make sure all weather files have the same starting and ending dates.")

										#end_date = current_end_date
										ends.append(current_end_date)
								except UnicodeDecodeError:
									sys.exit('Non-unicode character detected in {}. Please check the first line of the file and remove any accents or other characters that are not UTF-8 encoding.'.format(station_file))

						i += 1
			except UnicodeDecodeError:
				sys.exit('Non-unicode character detected in {}. Please check your station names and remove any accents or other characters that are not UTF-8 encoding.'.format(source_file))

			db_lib.bulk_insert(project_base.db, Weather_file, weather_files)
			if len(starts) > 0 and len(ends) > 0:
				start_date = max(starts)
				end_date = min(ends)
		return start_date, end_date


class NetCDFWeatherImport(ExecutableApi):
	"""
	Import weather stations from a CSV file containing station coordinates and variable availability.
	This is used when weather data comes from NetCDF files where station locations are defined in a CSV.
	
	CSV format: lat,lon,elev,pcp,tmin,tmax,slr,hmd,wnd,pet
	- elev: can be null (treated as 0)
	- variable columns: scaling factor as float, null/-99 = no data (stored as None)
	"""
	def __init__(self, project_db_file, delete_existing, create_stations, stations_csv_file, nc_data_file=None):
		self.__abort = False
		SetupProjectDatabase.init(project_db_file)
		self.project_db_file = project_db_file
		self.project_db = project_base.db
		self.create_stations = create_stations
		self.stations_csv_file = stations_csv_file
		self.nc_data_file = nc_data_file
		self.coords_to_stations = {}
		# Store scale factors per station name for later insertion
		self.station_scale_factors = {}

		# Ensure the scale table exists (for databases created before this feature)
		project_base.db.create_tables([Weather_sta_cli_scale], safe=True)

		# Ensure netcdf_data_file column exists in project_config (for databases created before this feature)
		self._ensure_netcdf_data_file_column()
		
		# Ensure out_path classification exists in file_cio_classification (for databases created before this feature)
		self._ensure_out_path_classification()

		if delete_existing:
			self.delete_existing()

	def _ensure_netcdf_data_file_column(self):
		"""Add the netcdf_data_file column to project_config if it doesn't exist."""
		try:
			cursor = project_base.db.execute_sql("PRAGMA table_info(project_config)")
			columns = [row[1] for row in cursor.fetchall()]
			if 'netcdf_data_file' not in columns:
				project_base.db.execute_sql("ALTER TABLE project_config ADD COLUMN netcdf_data_file VARCHAR(255) NULL")
		except Exception as e:
			print("Warning: Could not add netcdf_data_file column: {}".format(e))

	def _ensure_out_path_classification(self):
		"""Add the out_path classification to file_cio_classification if it doesn't exist."""
		try:
			cursor = project_base.db.execute_sql("SELECT id FROM file_cio_classification WHERE name = 'out_path'")
			if cursor.fetchone() is None:
				project_base.db.execute_sql("INSERT INTO file_cio_classification (id, name) VALUES (31, 'out_path')")
		except Exception as e:
			print("Warning: Could not add out_path classification: {}".format(e))

	def import_data(self):
		try:
			if not os.path.exists(self.stations_csv_file):
				sys.exit('Stations CSV file {file} does not exist.'.format(file=self.stations_csv_file))

			self.add_weather_files_from_csv()

			if self.create_stations:
				self.create_weather_stations(20, 45)
				self.add_scale_factors(85)
				self.match_stations(90)
			else:
				self.match_files_to_stations(20, 45)
				self.add_scale_factors(85)
			
			# Update project_config to indicate netcdf weather format
			self.update_project_config()
		except Exception as e:
			sys.exit('Error importing NetCDF stations: {}'.format(str(e)))

	def delete_existing(self):
		Weather_sta_cli_scale.delete().execute()
		Weather_file.delete().execute()
		Weather_sta_cli.delete().execute()

	def update_project_config(self):
		"""Update project_config to set weather_data_format to 'netcdf' and store nc data file path."""
		self.emit_progress(95, "Updating project configuration...")
		try:
			config = Project_config.get()
			config.weather_data_format = 'netcdf'
			if self.nc_data_file:
				config.netcdf_data_file = self.nc_data_file
			config.save()
		except Project_config.DoesNotExist:
			pass

	def parse_scale_value(self, val):
		"""Parse a scale value from CSV. Returns None for null/-99, float otherwise."""
		if val is None:
			return None
		val_str = val.strip().lower()
		if val_str in ('null', '-99', ''):
			return None
		try:
			return float(val)
		except ValueError:
			return None

	def add_weather_files_from_csv(self):
		"""Read the stations CSV file and add weather file entries for each station/variable combination."""
		if self.__abort: return
		
		self.emit_progress(0, "Reading stations CSV file...")
		
		weather_files = []
		
		# Map CSV column names to weather types for weather_file table
		# CSV has: pcp, tmin, tmax (combined as tmp), slr, hmd, wnd, pet
		var_to_type = {
			'pcp': 'pcp',
			'tmin': 'tmp',  # tmin and tmax are combined as tmp
			'tmax': 'tmp',
			'slr': 'slr',
			'hmd': 'hmd',
			'wnd': 'wnd',
			'pet': 'pet'
		}
		
		# Scale factor columns in CSV (stored separately in weather_sta_cli_scale)
		scale_cols = ['pcp', 'tmin', 'tmax', 'slr', 'hmd', 'wnd', 'pet']
		
		try:
			with open(self.stations_csv_file, 'r') as csvfile:
				reader = csv.DictReader(csvfile)
				
				row_count = 0
				for row in reader:
					if self.__abort: return
					
					lat = float(row['lat'])
					lon = float(row['lon'])
					
					# Generate a station filename based on coordinates
					station_name = weather_sta_name(lat, lon)
					
					# Store scale factors for this station
					scale_factors = {}
					for col in scale_cols:
						if col in row:
							scale_factors[col] = self.parse_scale_value(row[col])
						else:
							scale_factors[col] = None
					self.station_scale_factors[station_name] = scale_factors
					
					# Track which weather types we've added for this station
					# (to avoid duplicates for tmp from tmin/tmax)
					added_types = set()
					
					for var_col, weather_type in var_to_type.items():
						if var_col in row:
							scale_val = self.parse_scale_value(row[var_col])
							# Check if this variable has data (scale value is not None)
							has_data = scale_val is not None
							
							if has_data and weather_type not in added_types:
								filename = "{name}.{ext}".format(name=station_name, ext=weather_type)
								
								try:
									existing = Weather_file.get((Weather_file.filename == filename) & (Weather_file.type == weather_type))
								except Weather_file.DoesNotExist:
									file_entry = {
										"filename": filename,
										"type": weather_type,
										"lat": lat,
										"lon": lon
									}
									weather_files.append(file_entry)
									added_types.add(weather_type)
					
					row_count += 1
					if row_count % 100 == 0:
						self.emit_progress(min(15, row_count // 50), "Processing station {num}...".format(num=row_count))
				
				self.emit_progress(15, "Inserting {count} weather file entries...".format(count=len(weather_files)))
				db_lib.bulk_insert(project_base.db, Weather_file, weather_files)
				
		except UnicodeDecodeError:
			sys.exit('Non-unicode character detected in {}. Please check your CSV file encoding.'.format(self.stations_csv_file))

	def create_weather_stations(self, start_prog, total_prog):
		"""Create weather stations from unique lat/lon combinations in weather_file table."""
		if self.__abort: return

		stations = []
		cursor = project_base.db.execute_sql("select lat, lon from weather_file group by lat, lon")
		data = cursor.fetchall()
		records = len(data)
		i = 1
		for row in data:
			if self.__abort: return

			lat = row[0]
			lon = row[1]
			name = weather_sta_name(lat, lon)

			prog = round(i * total_prog / records) + start_prog
			self.emit_progress(prog, "Creating weather station {name}...".format(name=name))

			try:
				existing = Weather_sta_cli.get(Weather_sta_cli.name == name)
			except Weather_sta_cli.DoesNotExist:
				station = {
					"name": name,
					"atmo_dep": None,
					"lat": lat,
					"lon": lon,
				}
				stations.append(station)
			i += 1

		db_lib.bulk_insert(project_base.db, Weather_sta_cli, stations)
		self.match_files_to_stations(start_prog + total_prog, 20)

	def match_files_to_stations(self, start_prog, total_prog):
		"""Match weather files to weather stations based on lat/lon proximity."""
		self.emit_progress(start_prog, "Matching files to weather station...")
		update_closest_lat_lon("weather_sta_cli", "hmd", "weather_file", "filename", "hmd")
		update_closest_lat_lon("weather_sta_cli", "pcp", "weather_file", "filename", "pcp")
		update_closest_lat_lon("weather_sta_cli", "slr", "weather_file", "filename", "slr")
		update_closest_lat_lon("weather_sta_cli", "tmp", "weather_file", "filename", "tmp")
		update_closest_lat_lon("weather_sta_cli", "wnd", "weather_file", "filename", "wnd")
		update_closest_lat_lon("weather_sta_cli", "pet", "weather_file", "filename", "pet")

	def match_stations(self, start_prog):
		"""Assign weather stations to spatial connection tables."""
		self.emit_progress(start_prog, "Adding weather stations to spatial connection tables...")
		wst_col = "wst_id"
		wst_table = "weather_sta_cli"
		update_closest_lat_lon("aquifer_con", wst_col, wst_table)
		update_closest_lat_lon("channel_con", wst_col, wst_table)
		update_closest_lat_lon("chandeg_con", wst_col, wst_table)
		update_closest_lat_lon("rout_unit_con", wst_col, wst_table)
		update_closest_lat_lon("reservoir_con", wst_col, wst_table)
		update_closest_lat_lon("recall_con", wst_col, wst_table)
		update_closest_lat_lon("exco_con", wst_col, wst_table)
		update_closest_lat_lon("hru_con", wst_col, wst_table)
		update_closest_lat_lon("hru_lte_con", wst_col, wst_table)
		update_closest_lat_lon("weather_sta_cli", "wgn_id", "weather_wgn_cli")

	def add_scale_factors(self, start_prog):
		"""Add scale factors for each weather station from the stored CSV values."""
		self.emit_progress(start_prog, "Adding scale factors for weather stations...")
		
		scale_entries = []
		for station in Weather_sta_cli.select():
			if station.name in self.station_scale_factors:
				factors = self.station_scale_factors[station.name]
				scale_entry = {
					"weather_sta_cli": station.id,
					"pcp": factors.get('pcp'),
					"tmin": factors.get('tmin'),
					"tmax": factors.get('tmax'),
					"slr": factors.get('slr'),
					"hmd": factors.get('hmd'),
					"wnd": factors.get('wnd'),
					"pet": factors.get('pet')
				}
				scale_entries.append(scale_entry)
		
		if scale_entries:
			db_lib.bulk_insert(project_base.db, Weather_sta_cli_scale, scale_entries)


class Swat2012WeatherImport(ExecutableApi):
	def __init__(self, project_db_file, delete_existing, create_stations, source_dir):
		self.__abort = False
		SetupProjectDatabase.init(project_db_file)
		config = Project_config.get()
		
		weather_data_dir = utils.full_path(project_db_file, config.weather_data_dir)
		if not os.path.exists(weather_data_dir):
			sys.exit('Weather data directory {dir} does not exist.'.format(dir=weather_data_dir))

		self.output_dir = weather_data_dir
		self.project_db_file = project_db_file
		self.project_db = project_base.db
		self.source_dir = source_dir
		self.delete_existing = delete_existing
		self.create_stations = create_stations

	def import_data(self):
		try:
			self.write_to_swatplus(self.source_dir)
			weather_api = WeatherImport(self.project_db_file, self.delete_existing, self.create_stations)
			weather_api.import_data()
		except Project_config.DoesNotExist:
			sys.exit('Could not retrieve project configuration from database')

	def write_to_swatplus(self, dir):
		warnings = []

		if not os.path.exists(self.output_dir):
			os.makedirs(self.output_dir)

		total_files = len(os.listdir(dir))

		if self.__abort: return
		hmd_file = os.path.join(dir, HMD_TXT)
		if not os.path.exists(hmd_file):
			hmd_file = os.path.join(dir, HMD_TXT2)
		hmd_res = self.write_weather(hmd_file, os.path.join(self.output_dir, HMD_CLI), "hmd", 1, total_files)

		if self.__abort: return
		pcp_res = self.write_weather(os.path.join(dir, PCP_TXT), os.path.join(self.output_dir, PCP_CLI), "pcp", hmd_res[0], total_files)

		if self.__abort: return
		slr_file = os.path.join(dir, SLR_TXT)
		if not os.path.exists(slr_file):
			slr_file = os.path.join(dir, SLR_TXT2)
		slr_res = self.write_weather(slr_file, os.path.join(self.output_dir, SLR_CLI), "slr", pcp_res[0], total_files)

		if self.__abort: return
		tmp_res = self.write_weather(os.path.join(dir, TMP_TXT), os.path.join(self.output_dir, TMP_CLI), "tem", slr_res[0], total_files)

		if self.__abort: return
		wnd_file = os.path.join(dir, WND_TXT)
		if not os.path.exists(wnd_file):
			wnd_file = os.path.join(dir, WND_TXT2)
		wnd_res = self.write_weather(wnd_file, os.path.join(self.output_dir, WND_CLI), "wnd", tmp_res[0], total_files)

		if self.__abort: return
		pet_res = self.write_weather(os.path.join(dir, PET_TXT), os.path.join(self.output_dir, PET_CLI), "pet", wnd_res[0], total_files)

		if self.__abort: return
		warnings.append(hmd_res[1])
		warnings.append(pcp_res[1])
		warnings.append(slr_res[1])
		warnings.append(tmp_res[1])
		warnings.append(wnd_res[1])
		warnings.append(pet_res[1])
		has_warnings = any(x is not None for x in warnings)

		if has_warnings:
			with open(os.path.join(self.output_dir, "__warnings.txt"), 'w+') as warning_file:
				for w in warnings:
					if w is not None:
						warning_file.write(w)
						warning_file.write("\n")

	def write_weather(self, source_file, dest_file, weather_type, starting_file_num, total_files):
		if not os.path.exists(source_file):
			return starting_file_num, "Skipping {type} import. File does not exist: {file}".format(type=weather_type, file=source_file)
		else:
			with open(dest_file, 'w+') as new_file:
				new_file.write("{file}.cli: {desc} file names - file written by SWAT+ editor {today}\n".format(file=weather_type, desc=WEATHER_DESC[weather_type], today=datetime.datetime.now()))
				new_file.write("filename\n")
				new_file_names = []

				try:
					with open(source_file, "r") as source_data:
						i = 0
						curr_file_num = starting_file_num
						for line in source_data:
							if self.__abort:
								break

							if i == 0 and not "ID,NAME,LAT,LONG,ELEVATION" in line:
								return curr_file_num, "Skipping {type} import. Invalid file format in header: {file}. Expecting 'ID,NAME,LAT,LONG,ELEVATION'".format(type=weather_type, file=source_file)
							if i > 0:
								station_obj = [x.strip() for x in line.split(',')]
								if len(station_obj) != 5:
									return curr_file_num, "Skipping {type} import. Invalid file format in line {line_no}: {file}, {line}".format(type=weather_type, line_no=i+1, file=source_file, line=line)

								new_file_name = "{s}.{ext}".format(s=station_obj[1].replace("-", ""), ext=weather_type)
								new_file_names.append(new_file_name)
								#new_file.write(new_file_name)
								#new_file.write("\n")

								self.write_station(os.path.dirname(source_file), station_obj, weather_type)
								prog = round(curr_file_num * 100 / total_files)
								self.emit_progress(prog, "Writing {type}, {file}...".format(type=weather_type, file=new_file_name))
								curr_file_num += 1

							i += 1
				except UnicodeDecodeError:
					sys.exit('Non-unicode character detected in {}. Please check your station names and remove any accents or other characters that are not UTF-8 encoding.'.format(source_file))

				for fn in sorted(new_file_names, key=str.lower):
					new_file.write(fn)
					new_file.write("\n")

			return curr_file_num, None

	def write_station(self, dir, station_obj, weather_type):
		source_file = os.path.join(dir, "{s}.txt".format(s=station_obj[1]))
		if not os.path.exists(source_file):
			return "Skipping {type} import. Station file does not exist: {file}".format(type=weather_type, file=source_file)

		dest_file_name = "{s}.{ext}".format(s=station_obj[1].replace("-", ""), ext=weather_type)
		dest_file = os.path.join(self.output_dir, dest_file_name)

		with open(dest_file, 'w+') as new_file:
			new_file.write("{file}: {desc} data - file written by SWAT+ editor {today}\n".format(file=dest_file_name, desc=WEATHER_DESC[weather_type], today=datetime.datetime.now()))
			new_file.write("nbyr".rjust(4))
			new_file.write("tstep".rjust(10))
			new_file.write("lat".rjust(10))
			new_file.write("lon".rjust(10))
			new_file.write("elev".rjust(10))
			new_file.write("\n")

			linecount = self.file_len(source_file)
			total_days = linecount - 2 if linecount > 0 else 0

			with open(source_file, "r") as station_file:
				i = 0
				date = None
				for line in station_file:
					if i == 0:
						ts = time.strptime(line.strip(), "%Y%m%d")
						date = datetime.datetime(ts.tm_year, ts.tm_mon, ts.tm_mday)
						start_date = date

						end_date = start_date + datetime.timedelta(days=total_days)
						nbyr = end_date.year - start_date.year + 1

						new_file.write(str(nbyr).rjust(4))
						new_file.write("0".rjust(10))
						new_file.write("{0:.3f}".format(float(station_obj[2])).rjust(10))
						new_file.write("{0:.3f}".format(float(station_obj[3])).rjust(10))
						new_file.write("{0:.3f}".format(float(station_obj[4])).rjust(10))
						new_file.write("\n")
					else:
						day_of_year = date.timetuple().tm_yday

						new_file.write(str(date.year))
						new_file.write(str(day_of_year).rjust(5))
						new_file.write(' ')

						if weather_type == "tmp" or weather_type == "tem":
							tmp = [x.strip() for x in line.split(',')]
							utils.write_num(new_file, tmp[0], default_pad=10)
							utils.write_num(new_file, tmp[1], default_pad=10)
						else:
							utils.write_num(new_file, line, default_pad=10)
						new_file.write("\n")

						date = date + datetime.timedelta(days=1)

					i += 1

	def file_len(self, fname):
		with open(fname) as f:
			for i, l in enumerate(f):
				pass
		return i + 1


class WgnImport(ExecutableApi):
	def __init__(self, project_db_file, delete_existing, create_stations, import_method='database', file1=None, file2=None):
		self.__abort = False
		SetupProjectDatabase.init(project_db_file)
		self.project_db_file = project_db_file
		self.project_db = project_base.db
		self.create_stations = create_stations
		self.import_method = import_method
		self.file1 = file1
		self.file2 = file2

		try:
			config = Project_config.get()
			if self.import_method == 'database' and self.project_db_file != '' and self.project_db_file is not None:
				wgn_db = utils.full_path(self.project_db_file, config.wgn_db)
				if not os.path.exists(wgn_db):
					sys.exit('WGN path {dir} does not exist.'.format(dir=wgn_db))
					
				if config.wgn_table_name is None:
					sys.exit('Weather generator table name not set in config table.')

				self.wgn_database = wgn_db
				self.wgn_table = config.wgn_table_name
		except Project_config.DoesNotExist:
			sys.exit('Could not retrieve project configuration from database')

		if delete_existing:
			self.delete_existing()

	def import_data(self):
		if self.create_stations:
			self.add_wgn_stations(0, 50)
			self.create_weather_stations(50, 15)
			wi = WeatherImport(self.project_db_file, False, False)
			wi.match_stations(65)
		else:
			self.add_wgn_stations(0, 70)
			self.match_to_weather_stations(70, 30)

	def delete_existing(self):
		Weather_wgn_cli_mon.delete().execute()
		Weather_wgn_cli.delete().execute()

	def add_wgn_stations(self, start_prog, total_prog):
		if self.import_method == 'database':
			self.add_wgn_stations_db(start_prog, total_prog)
		elif self.import_method == 'two_file':
			self.add_wgn_stations_tf(start_prog, total_prog)
		elif self.import_method == 'one_file':
			self.add_wgn_stations_sf(start_prog, total_prog)
		else:
			sys.exit('Unsupported wgn import method.')

	def add_wgn_stations_tf(self, start_prog, total_prog):
		if self.__abort: return
		prog = (total_prog - start_prog) / 4 + start_prog
		self.emit_progress(prog, 'Adding weather generator stations...')
		old_to_new_id = fileio.read_csv_file(self.file1, Weather_wgn_cli, self.project_db, 0, ignore_id_col=True, overwrite=fileio.FileOverwrite.replace, remove_spaces_cols=['name'], return_id_dict=True)
		prog = (total_prog - start_prog) / 2 + start_prog
		self.emit_progress(prog, 'Adding weather generator monthly values...')
		try:
			fileio.read_csv_file(self.file2, Weather_wgn_cli_mon, self.project_db, 0, ignore_id_col=True, overwrite=fileio.FileOverwrite.ignore, replace_id_col='weather_wgn_cli', replace_id_dict=old_to_new_id)
		except UnicodeDecodeError:
			sys.exit('Your CSV files contain a character that is not UTF-8 encoding. Please check your station names and remove any accents or other non-unicode characters.')

	def add_wgn_stations_db(self, start_prog, total_prog):
		if self.__abort: return
		conn = sqlite3.connect(self.wgn_database)
		conn.row_factory = sqlite3.Row

		monthly_table = "{}_mon".format(self.wgn_table)

		if not db_lib.exists_table(conn, self.wgn_table):
			raise ValueError(
				"Table {table} does not exist in {file}.".format(table=self.wgn_table, file=self.wgn_database))

		if not db_lib.exists_table(conn, monthly_table):
			raise ValueError(
				"Table {table} does not exist in {file}.".format(table=monthly_table, file=self.wgn_database))

		if Rout_unit_con.select().count() > 0:
			coords = Rout_unit_con.select(fn.Min(Rout_unit_con.lat).alias("min_lat"),
										  fn.Max(Rout_unit_con.lat).alias("max_lat"),
										  fn.Min(Rout_unit_con.lon).alias("min_lon"),
										  fn.Max(Rout_unit_con.lon).alias("max_lon")
										  ).get()

			query = "select * from {table_name} where lat between ? and ? and lon between ? and ? order by name".format(table_name=self.wgn_table)
			tol = 0.5
			cursor = conn.cursor().execute(query, (coords.min_lat - tol, coords.max_lat + tol, coords.min_lon - tol, coords.max_lon + tol))
		elif Chandeg_con.select().count() > 0:
			coords = Chandeg_con.select(fn.Min(Chandeg_con.lat).alias("min_lat"),
										  fn.Max(Chandeg_con.lat).alias("max_lat"),
										  fn.Min(Chandeg_con.lon).alias("min_lon"),
										  fn.Max(Chandeg_con.lon).alias("max_lon")
										  ).get()

			query = "select * from {table_name} where lat between ? and ? and lon between ? and ? order by name".format(table_name=self.wgn_table)
			tol = 0.5
			cursor = conn.cursor().execute(query, (coords.min_lat - tol, coords.max_lat + tol, coords.min_lon - tol, coords.max_lon + tol))
		else:
			query = "select * from {table_name} order by name".format(table_name=self.wgn_table)
			cursor = conn.cursor().execute(query)

		wgns = []
		ids = []

		data = cursor.fetchall()
		records = len(data)
		#print(records)

		i = 1
		for row in data:
			if self.__abort: return

			try:
				existing = Weather_wgn_cli.get(Weather_wgn_cli.name == row['name'])
			except Weather_wgn_cli.DoesNotExist:
				prog = round(i * (total_prog / 2) / records) + start_prog
				self.emit_progress(prog, "Preparing weather generator {name}...".format(name=row['name']))
				i += 1

				ids.append(row['id'])
				wgn = {
					"id": row['id'],
					"name": row['name'],
					"lat": row['lat'],
					"lon": row['lon'],
					"elev": row['elev'],
					"rain_yrs": row['rain_yrs']
				}
				wgns.append(wgn)

		prog = start_prog if records < 1 else round(i * (total_prog / 2) / records) + start_prog
		self.emit_progress(prog, "Inserting {total} weather generators...".format(total=len(ids)))
		db_lib.bulk_insert(project_base.db, Weather_wgn_cli, wgns)

		# Chunk the id array so we don't hit the SQLite parameter limit!
		max_length = 999
		id_chunks = [ids[i:i + max_length] for i in range(0, len(ids), max_length)]

		i = 1
		start_prog = start_prog + (total_prog / 2)

		mon_count_query = "select count(*) from {table_name}".format(table_name=monthly_table)
		total_mon_rows = conn.cursor().execute(mon_count_query).fetchone()[0]
		current_total = 0

		for chunk in id_chunks:
			monthly_values = []
			mon_query = "select * from {table_name} where wgn_id in ({ids})".format(table_name=monthly_table, ids=",".join('?'*len(chunk)))
			mon_cursor = conn.cursor().execute(mon_query, chunk)
			mon_data = mon_cursor.fetchall()
			mon_records = len(mon_data)
			i = 1

			for row in mon_data:
				if self.__abort: return

				if i == 1 or (i % 12 == 0):
					prog = round(i * (total_prog / 2) / mon_records) + start_prog
					self.emit_progress(prog, "Preparing monthly values {i}/{total}...".format(i=i, total=mon_records))
				i += 1

				mon = {
					"weather_wgn_cli": row['wgn_id'],
					"month": row['month'],
					"tmp_max_ave": row['tmp_max_ave'],
					"tmp_min_ave": row['tmp_min_ave'],
					"tmp_max_sd": row['tmp_max_sd'],
					"tmp_min_sd": row['tmp_min_sd'],
					"pcp_ave": row['pcp_ave'],
					"pcp_sd": row['pcp_sd'],
					"pcp_skew": row['pcp_skew'],
					"wet_dry": row['wet_dry'],
					"wet_wet": row['wet_wet'],
					"pcp_days": row['pcp_days'],
					"pcp_hhr": row['pcp_hhr'],
					"slr_ave": row['slr_ave'],
					"dew_ave": row['dew_ave'],
					"wnd_ave": row['wnd_ave']
				}
				monthly_values.append(mon)

			prog = round(i * (total_prog / 2) / mon_records) + start_prog
			current_total = current_total + mon_records
			self.emit_progress(prog, "Inserting monthly values {rec}/{total}...".format(rec=current_total, total=total_mon_rows))
			db_lib.bulk_insert(project_base.db, Weather_wgn_cli_mon, monthly_values)

	def add_wgn_stations_sf(self, start_prog, total_prog):
		if self.__abort: return
		try:
			csv_file = open(self.file1, "r")

			dialect = csv.Sniffer().sniff(csv_file.readline())
			csv_file.seek(0)
			replace_commas = dialect is not None and dialect.delimiter != ','
			hasHeader = csv.Sniffer().has_header(csv_file.readline())
			csv_file.seek(0)

			csv_reader = csv.reader(csv_file, dialect)

			if hasHeader:
				headerLine = next(csv_reader)

			#row_count = sum(1 for row in csv_reader)

			i = 0
			stations = [] 
			station_to_mv = {}
			self.emit_progress(round(total_prog*0.5), 'Reading CSV file...')
			for val in csv_reader:
				if replace_commas:
					val = [item.replace(',', '.', 1) for item in val]
				
				station = {}
				station['name'] = utils.remove_space(val[0])

				#Check for duplicate name
				table = Weather_wgn_cli
				try:
					m = table.get(table.name == station['name'])

					k = 1
					while table.select().where(table.name == '{name}{num}'.format(name=station['name'], num=k)).exists():
						k += 1

					station['name'] = '{name}{num}'.format(name=station['name'], num=k)
				except table.DoesNotExist:
					pass

				station['lat'] = utils.val_if_null(val[1], 0)
				station['lon'] = utils.val_if_null(val[2], 0)
				station['elev'] = utils.val_if_null(val[3], 0)
				station['rain_yrs'] = utils.val_if_null(val[4], 0)

				idx = 5
				monthly_values = []
				for m in range(1, 13):
					month = {}
					month['month'] = m
					month['tmp_max_ave'] = utils.val_if_null(val[idx], 0)
					idx += 1
					month['tmp_min_ave'] = utils.val_if_null(val[idx], 0)
					idx += 1
					month['tmp_max_sd'] = utils.val_if_null(val[idx], 0)
					idx += 1
					month['tmp_min_sd'] = utils.val_if_null(val[idx], 0)
					idx += 1
					month['pcp_ave'] = utils.val_if_null(val[idx], 0)
					idx += 1
					month['pcp_sd'] = utils.val_if_null(val[idx], 0)
					idx += 1
					month['pcp_skew'] = utils.val_if_null(val[idx], 0)
					idx += 1
					month['wet_dry'] = utils.val_if_null(val[idx], 0)
					idx += 1
					month['wet_wet'] = utils.val_if_null(val[idx], 0)
					idx += 1
					month['pcp_days'] = utils.val_if_null(val[idx], 0)
					idx += 1
					month['pcp_hhr'] = utils.val_if_null(val[idx], 0)
					idx += 1
					month['slr_ave'] = utils.val_if_null(val[idx], 0)
					idx += 1
					month['dew_ave'] = utils.val_if_null(val[idx], 0)
					idx += 1
					month['wnd_ave'] = utils.val_if_null(val[idx], 0)
					idx += 1
					monthly_values.append(month)
				
				stations.append(station)
				station_to_mv[station['name']] = monthly_values
				i += 1

			self.emit_progress(round(total_prog*0.75), 'Inserting stations into project database...')
			db_lib.bulk_insert(self.project_db, Weather_wgn_cli, stations)
			name_to_id = {}
			for row in Weather_wgn_cli.select(Weather_wgn_cli.id, Weather_wgn_cli.name):
				name_to_id[row.name] = row.id

			mv_to_insert = []
			for name in station_to_mv:
				id = name_to_id[name]
				for m in station_to_mv[name]:
					m['weather_wgn_cli'] = id
					mv_to_insert.append(m)

			self.emit_progress(round(total_prog*0.90), 'Inserting monthly values into project database...')
			db_lib.bulk_insert(self.project_db, Weather_wgn_cli_mon, mv_to_insert)
		except UnicodeDecodeError:
			sys.exit('Your CSV file contains a character that is not UTF-8 encoding. Please check your station names and remove any accents or other non-unicode characters.')


	def create_weather_stations(self, start_prog, total_prog):  # total_prog is the total progress percentage available for this method
		if self.__abort: return

		stations = []
		query = Weather_wgn_cli.select()
		records = query.count()
		i = 1
		for row in query:
			if self.__abort: return

			lat = row.lat
			lon = row.lon
			#name = "w{lat}{lon}".format(lat=abs(round(lat*1000)), lon=abs(round(lon*1000)))
			name = weather_sta_name(lat, lon)

			prog = round(i * total_prog / records) + start_prog
			self.emit_progress(prog, "Creating weather station {name}...".format(name=name))

			try:
				existing = Weather_sta_cli.get(Weather_sta_cli.name == name)
			except Weather_sta_cli.DoesNotExist:
				station = {
					"name": name,
					"hmd": None,
					"pcp": None,
					"slr": None,
					"tmp": None,
					"wnd": None,
					"pet": None,
					"atmo_dep": None,
					"lat": lat,
					"lon": lon,
					"wgn": row.id
				}

				stations.append(station)
			i += 1

		db_lib.bulk_insert(project_base.db, Weather_sta_cli, stations)

	def match_to_weather_stations(self, start_prog, total_prog):
		if Weather_wgn_cli.select().count() > 0:
			with project_base.db.atomic():
				query = Weather_sta_cli.select()
				records = query.count()
				i = 1
				for row in query:
					if self.__abort: return

					prog = round(i * total_prog / records) + start_prog
					i += 1

					if row.lat is not None and row.lon is not None:
						id = closest_lat_lon(project_base.db, "weather_wgn_cli", row.lat, row.lon)

						self.emit_progress(prog, "Updating weather station with generator {i}/{total}...".format(i=i, total=records))
						row.wgn_id = id
						row.save()



class AtmoImport(ExecutableApi):
	def __init__(self, project_db_file, delete_existing, import_method='csv', file1=None, file2=None):
		self.__abort = False
		SetupProjectDatabase.init(project_db_file)
		project_base.db.execute_sql("PRAGMA foreign_keys = ON")
		self.project_db_file = project_db_file
		self.project_db = project_base.db
		self.import_method = import_method
		self.atmo_data_file = file1
		self.atmo_to_stations_file = file2

		if delete_existing:
			self.delete_existing()

		self.atmo_cli = Atmo_cli.get_or_none()
		if self.atmo_cli is None:
			self.atmo_cli = Atmo_cli.create(filename='atmo.cli',timestamp='aa', mo_init=0, yr_init=0, num_aa=0)

	def delete_existing(self):
		Atmo_cli_sta_value.delete().execute()
		Atmo_cli_sta.delete().execute()
		#Atmo_cli.delete().execute()

	def import_data(self):
		if self.import_method == 'csv':
			self.read_data_file_csv(0, 75)
		elif self.import_method == 'cli':
			self.read_data_file_cli(0, 75)
		else:
			sys.exit('Unsupported data file format. Must be csv or cli.')
		
		self.match_to_stations(75, 25)

	def read_data_file_csv(self, start_prog, total_prog):
		#csv headers: name,month,year,nh4_rf,no3_rf,nh4_dry,no3_dry
		if self.__abort: return

		csv_file = open(self.atmo_data_file, "r")

		dialect = csv.Sniffer().sniff(csv_file.readline())
		csv_file.seek(0)
		replace_commas = dialect is not None and dialect.delimiter != ','
		hasHeader = csv.Sniffer().has_header(csv_file.readline())
		csv_file.seek(0)

		csv_reader = csv.reader(csv_file, dialect)

		if hasHeader:
			headerLine = next(csv_reader)

		i = 0
		stations = []
		stations_to_values = {}
		self.emit_progress(round(total_prog*0.5), 'Reading CSV file...')
		for val in csv_reader:
			if replace_commas:
				val = [item.replace(',', '.', 1) for item in val]

			if len(val) < 7:
				sys.exit('Invalid csv file format. Ensure your data has the following columns: name,month,year,nh4_rf,no3_rf,nh4_dry,no3_dry')
			name = utils.val_if_null(val[0], 'atmo{}'.format(i+1))
			month = utils.val_if_null(int(val[1]), 0)
			year = utils.val_if_null(int(val[2]), 0)
			nh4_rf = utils.val_if_null(float(val[3]), 0)
			no3_rf = utils.val_if_null(float(val[4]), 0)
			nh4_dry = utils.val_if_null(float(val[5]), 0)
			no3_dry = utils.val_if_null(float(val[6]), 0)

			if i == 0:
				if month == 0 and year == 0:
					self.atmo_cli.timestep = 'aa'
				elif month == 0:
					self.atmo_cli.timestep = 'yr'
				else:
					self.atmo_cli.timestep = 'mo'

				self.atmo_cli.mo_init = month
				self.atmo_cli.yr_init = year
				self.atmo_cli.save()

			if name not in stations:
				stations.append(name)
				stations_to_values[name] = []

			timestep = 0
			if self.atmo_cli.timestep == 'mo':
				timestep = int('{y}{m}'.format(y=year, m=str(month).rjust(2, '0')))
			elif self.atmo_cli.timestep == 'yr':
				timestep = year

			data = {
				'timestep': timestep,
				'nh4_wet': nh4_rf,
				'no3_wet': no3_rf,
				'nh4_dry': nh4_dry,
				'no3_dry': no3_dry
			}

			stations_to_values[name].append(data)
			i += 1

		self.emit_progress(round(total_prog*0.75), 'Inserting stations into project database...')
		stations_db = [{ 'atmo_cli': self.atmo_cli.id, 'name': v } for v in stations]
		db_lib.bulk_insert(self.project_db, Atmo_cli_sta, stations_db)
		name_to_id = {}
		for row in Atmo_cli_sta.select(Atmo_cli_sta.id, Atmo_cli_sta.name):
			name_to_id[row.name] = row.id

		station_values = []
		i = 0
		for name in stations_to_values:
			id = name_to_id[name]
			for v in stations_to_values[name]:
				v['sta'] = id
				station_values.append(v)
			if i == 0:
				self.atmo_cli.num_aa = 0 if self.atmo_cli.timestep == 'aa' else len(stations_to_values[name])
				self.atmo_cli.save()
			i += 1

		self.emit_progress(round(total_prog*0.90), 'Inserting values into project database...')
		db_lib.bulk_insert(self.project_db, Atmo_cli_sta_value, station_values)
		

	def read_data_file_cli(self, start_prog, total_prog):
		if self.__abort: return
		with open(self.atmo_data_file, 'r') as atmo_data:
			i = 0
			current_station_line = 3
			current_station = ''
			stations = []
			stations_to_values = {}
			self.emit_progress(start_prog + round(total_prog*0.5), 'Reading atmo.cli file...')
			for line in atmo_data:
				if self.__abort: break
				if i == 2:
					val = line.split()
					if len(val) < 5:
						sys.exit('Invalid atmo.cli file format, line 3. Ensure your data matched the required format in the same file. Line: "{}", Length: {}'.format(line, len(val)))
					#num_stations = int(val[0].strip())
					self.atmo_cli.timestep = val[1].strip()
					self.atmo_cli.mo_init = int(val[2].strip())
					self.atmo_cli.yr_init = int(val[3].strip())
					self.atmo_cli.num_aa = int(val[4].strip())
					self.atmo_cli.save()
				
				if i > 2:
					val = line.split()
					if len(val) > 0:
						if i == current_station_line:
							current_station = val[0].strip()
							stations.append(current_station)
							stations_to_values[current_station] = {}
						elif i == current_station_line + 1:
							stations_to_values[current_station]['nh4_rf'] = self.get_atmo_cli_data_line(line)
						elif i == current_station_line + 2:
							stations_to_values[current_station]['no3_rf'] = self.get_atmo_cli_data_line(line)
						elif i == current_station_line + 3:
							stations_to_values[current_station]['nh4_dry'] = self.get_atmo_cli_data_line(line)
						elif i == current_station_line + 4:
							stations_to_values[current_station]['no3_dry'] = self.get_atmo_cli_data_line(line)
							current_station_line += 5
				
				i += 1

		self.emit_progress(round(total_prog*0.75), 'Inserting stations into project database...')
		stations_db = [{ 'atmo_cli': self.atmo_cli.id, 'name': v } for v in stations]
		db_lib.bulk_insert(self.project_db, Atmo_cli_sta, stations_db)
		name_to_id = {}
		for row in Atmo_cli_sta.select(Atmo_cli_sta.id, Atmo_cli_sta.name):
			name_to_id[row.name] = row.id

		station_values = []
		num_aa = 1 if self.atmo_cli.timestep == 'aa' else self.atmo_cli.num_aa
		start_date = datetime.date.today()
		if self.atmo_cli.timestep == 'mo':
			start_date = datetime.date(self.atmo_cli.yr_init, self.atmo_cli.mo_init, 1)
		for name in stations_to_values:
			id = name_to_id[name]
			j = 0
			while j < num_aa:
				timestep = 0
				if self.atmo_cli.timestep == 'mo':
					item_date = utils.add_months(start_date, j)
					timestep = int('{y}{m}'.format(y=item_date.year, m=str(item_date.month).rjust(2, '0')))
				elif self.atmo_cli.timestep == 'yr':
					timestep = self.atmo_cli.yr_init + j
				data = {
					'sta': id,
					'timestep': timestep,
					'nh4_wet': stations_to_values[name]['nh4_rf'][j],
					'no3_wet': stations_to_values[name]['no3_rf'][j],
					'nh4_dry': stations_to_values[name]['nh4_dry'][j],
					'no3_dry': stations_to_values[name]['no3_dry'][j]
				}
				station_values.append(data)
				j += 1
				
		self.emit_progress(round(total_prog*0.90), 'Inserting values into project database...')
		db_lib.bulk_insert(self.project_db, Atmo_cli_sta_value, station_values)

	def get_atmo_cli_data_line(self, line):
		data = line.split()
		j = 0
		values = []
		num_aa = 1 if self.atmo_cli.timestep == 'aa' else self.atmo_cli.num_aa
		while j < num_aa:
			values.append(float(data[j].strip()))
			j += 1
		return values
	
	def match_to_stations(self, start_prog, total_prog):
		#csv headers: atmo_station,weather_station,lat,lon
		if self.__abort: return

		csv_file = open(self.atmo_to_stations_file, "r")

		dialect = csv.Sniffer().sniff(csv_file.readline())
		csv_file.seek(0)
		replace_commas = dialect is not None and dialect.delimiter != ','
		hasHeader = csv.Sniffer().has_header(csv_file.readline())
		csv_file.seek(0)

		csv_reader = csv.reader(csv_file, dialect)

		if hasHeader:
			headerLine = next(csv_reader)

		self.emit_progress(round(total_prog*0.5), 'Matching atmo data to weather stations...')
		for val in csv_reader:
			if replace_commas:
				val = [item.replace(',', '.', 1) for item in val]

			if len(val) < 2:
				sys.exit('Invalid csv file format. Ensure your data has the following columns: atmo_station,weather_station')
			
			atmo_station = val[0].strip()
			weather_station = val[1].strip()
			if atmo_station is not None and atmo_station != 'null':
				Weather_sta_cli.update(atmo_dep=atmo_station).where(Weather_sta_cli.name == weather_station).execute()


if __name__ == '__main__':
	sys.stdout = Unbuffered(sys.stdout)
	parser = argparse.ArgumentParser(description="Import weather generator data into project SQLite database.")
	parser.add_argument("--project_db_file", type=str, help="full path of project SQLite database file", nargs="?")
	parser.add_argument("--delete_existing", type=str, help="y/n delete existing data first", nargs="?")

	# import weather
	parser.add_argument("--import_type", type=str, help="type of weather to import: observed, observed2012, wgn", nargs="?")
	parser.add_argument("--create_stations", type=str, help="y/n create stations for wgn", nargs="?")
	parser.add_argument("--source_dir", type=str, help="full path of SWAT2012 weather files", nargs="?")
	parser.add_argument("--import_method", type=str, help="import method for wgn (database, two_file, one_file)", nargs="?")
	parser.add_argument("--file1", type=str, help="full path of file", nargs="?")
	parser.add_argument("--file2", type=str, help="full path of file", nargs="?")
	args = parser.parse_args()

	del_ex = True if args.delete_existing == "y" else False
	cre_sta = True if args.create_stations == "y" else False

	if args.import_type == "observed":
		api = WeatherImport(args.project_db_file, del_ex, cre_sta)
		api.import_data()
	elif args.import_type == "observed2012":
		api = Swat2012WeatherImport(args.project_db_file, del_ex, cre_sta, args.source_dir)
		api.import_data()
	elif args.import_type == "wgn":
		api = WgnImport(args.project_db_file, del_ex, cre_sta, args.import_method, args.file1, args.file2)
		api.import_data()
	elif args.import_type == "atmo":
		api = AtmoImport(args.project_db_file, del_ex, args.import_method, args.file1, args.file2)
		api.import_data()
