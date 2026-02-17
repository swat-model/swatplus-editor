from helpers.executable_api import ExecutableApi, Unbuffered
from database.output import data

import csv
import os, os.path
import sqlite3
import re
import sys
from pathlib import Path
from datetime import datetime

def clean_column_name(name):
	"""Clean column names to be valid SQL identifiers."""
	name = name.strip()
	name = re.sub(r'[^\w]+', '_', name)
	name = name.strip('_')
	if name and name[0].isdigit():
		name = 'col_' + name
	return name.lower()

def infer_sql_type(value):
	"""Infer SQL data type from a string value."""
	value = value.strip()
	
	try:
		int(value)
		return 'INTEGER'
	except ValueError:
		pass
	
	try:
		float(value)
		return 'REAL'
	except ValueError:
		pass
	
	return 'TEXT'

def adjust_gis_id(gis_id_value, name_value):
	"""
	Adjust gis_id if it's 0 by extracting digits from name.
	
	Args:
		gis_id_value: Current gis_id value
		name_value: Value from the 'name' column
	
	Returns:
		Adjusted gis_id value
	"""
	try:
		if int(gis_id_value) == 0:
			subbed = re.sub('[^0-9]', '', str(name_value))
			if subbed.isdigit():
				return int(subbed)
			else:
				return 0
		return int(gis_id_value)
	except (ValueError, TypeError):
		return gis_id_value

def reset_database(db_file):
	"""Completely reset a SQLite database."""
	conn = sqlite3.connect(db_file)
	cursor = conn.cursor()
	
	# Get all objects
	cursor.execute("""
		SELECT type, name FROM sqlite_master 
		WHERE name NOT LIKE 'sqlite_%'
		ORDER BY type DESC
	""")
	objects = cursor.fetchall()
	
	# Drop in correct order (tables last)
	for obj_type, obj_name in objects:
		if obj_type == 'table':
			cursor.execute(f"DROP TABLE IF EXISTS {obj_name}")
		elif obj_type == 'index':
			cursor.execute(f"DROP INDEX IF EXISTS {obj_name}")
		elif obj_type == 'view':
			cursor.execute(f"DROP VIEW IF EXISTS {obj_name}")
		elif obj_type == 'trigger':
			cursor.execute(f"DROP TRIGGER IF EXISTS {obj_name}")
	
	conn.commit()
	cursor.execute("VACUUM")
	conn.close()

class ReadOutput(ExecutableApi):
	def __init__(self, output_files_dir, db_file, swat_version, editor_version, project_name):
		self.__abort = False
		db_file_sanitized = db_file.replace("\\","/")
		try:
			os.remove(db_file_sanitized)
		except:
			reset_database(db_file_sanitized)

		self.output_files_dir = output_files_dir.replace("\\","/")
		self.swat_version = swat_version
		self.editor_version = editor_version
		self.project_name = project_name

		self.conn = sqlite3.connect(db_file_sanitized)
		self.cursor = self.conn.cursor()
	
	def __del__(self):
		self.conn.close()

	def read(self):	
		self.set_safety_level('fastest')	
		self.setup_meta_tables()

		files_out_file = os.path.join(self.output_files_dir, 'files_out.out')

		# Read files_out.out to get list of output CSV files
		files = []
		try:
			with open(files_out_file, "r") as file:
				i = 1
				for line in file:
					if i > 1:
						val = line.split()
						if len(val) < 2:
							raise ValueError('Unexpected number of columns in {}'.format(files_out_file))

						file_name = val[len(val)-1].strip()
						if file_name.endswith('.csv'):
							files.append(file_name)

					i += 1
		except FileNotFoundError:
			pass
		except ValueError as ve:
			sys.exit(ve)

		prog_step = 0 if len(files) < 1 else round(100 / len(files))
		prog = 0
		for file in files:
			self.emit_progress(prog, 'Importing {}...'.format(file))
			table_name = file[:-4].replace('hru-lte', 'hru_lte')
			desc_key = table_name
			time_series_key = ''
			for key in data.time_series_labels:
				desc_key = desc_key.replace('_{}'.format(key), '')
				if key in table_name:
					time_series_key = key

			description = '{ts} {n}'.format(ts=data.time_series_labels.get(time_series_key, ''), n=data.table_labels.get(desc_key, table_name))
			self.cursor.execute('INSERT INTO table_description (table_name, description) VALUES (?, ?)', (table_name, description))

			data_start_line = data.special_start_lines.get(desc_key, data.default_start_line)
			read_units = False if desc_key in data.ignore_units else True
			headings_start_line = data_start_line - 2 if read_units else data_start_line - 1

			file_path = os.path.join(self.output_files_dir, file)

			# Read column headers, units (if applicable), and first data line for type inference
			with open(file_path, 'r') as f:
				i = 1
				while i < headings_start_line:
					f.readline()
					i += 1
				
				column_headers_raw = f.readline()
				column_headers = [clean_column_name(col) for col in column_headers_raw.split(',')]

				units = []
				if read_units:
					units_line = f.readline()
					units = [unit.strip() for unit in units_line.split(',')]

				# First data row for type inference
				first_data_line = f.readline()

			# Parse first data row
			first_data_row = list(csv.reader([first_data_line]))[0]
			
			# Find indices for gis_id and name columns if fix_gis_id is enabled
			gis_id_idx = None
			name_idx = None
			if fix_gis_id:
				try:
					gis_id_idx = column_headers.index('gis_id')
					name_idx = column_headers.index('name')
				except ValueError:
					fix_gis_id = False
			
			# Infer data types from first data row
			column_types = [infer_sql_type(value) for value in first_data_row]
			
			# Create table schema
			columns_with_types = [f"{col_name} {col_type}" for col_name, col_type in zip(column_headers, column_types)]
			
			create_table_sql = f"""
			CREATE TABLE IF NOT EXISTS {table_name} (
				{', '.join(columns_with_types)}
			)
			"""			
			self.cursor.execute(create_table_sql)

			# Insert column descriptions (only for columns with units)
			column_desc_count = 0
			for col_name, unit in zip(column_headers, units):
				# Only insert if unit is not empty
				if unit and unit.strip():
					self.cursor.execute("""
						INSERT INTO column_description (table_name, column_name, units)
						VALUES (?, ?, ?)
					""", (table_name, col_name, unit.strip()))
					column_desc_count += 1
			
			self.conn.commit()

			prog += prog_step
					
		self.cursor.execute("""
			INSERT INTO project_config (project_name, editor_version, swat_version, output_import_time)
			VALUES (?, ?, ?, ?)
		""", (self.project_name, self.editor_version, self.swat_version, datetime.now()))
		self.conn.commit()
		self.conn.close()

	def setup_meta_tables(self):
		self.cursor.execute("""
			CREATE TABLE IF NOT EXISTS column_description (
				id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
				table_name VARCHAR(255) NOT NULL,
				column_name VARCHAR(255) NOT NULL,
				units VARCHAR(255),
				description VARCHAR(255)
			)
		""")

		self.cursor.execute("""
			CREATE TABLE IF NOT EXISTS table_description (
				table_name  VARCHAR (255) NOT NULL PRIMARY KEY,
				description VARCHAR (255) NOT NULL
			)
		""")

		self.cursor.execute("""
			CREATE TABLE IF NOT EXISTS project_config (
				id INTEGER NOT NULL PRIMARY KEY,
				project_name VARCHAR (255),
				editor_version VARCHAR (255),
				swat_version VARCHAR (255),
				output_import_time DATETIME
			)
		""")
		self.conn.commit()
	
	def set_safety_level(self, safety_level):
		# Set PRAGMA based on safety level
		if safety_level == 'safe':
			self.cursor.execute("PRAGMA journal_mode = WAL")
			self.cursor.execute("PRAGMA synchronous = NORMAL")
			self.cursor.execute("PRAGMA cache_size = -2000000")
			self.cursor.execute("PRAGMA temp_store = MEMORY")
			
		elif safety_level == 'balanced':
			self.cursor.execute("PRAGMA journal_mode = MEMORY")
			self.cursor.execute("PRAGMA synchronous = OFF")
			self.cursor.execute("PRAGMA cache_size = -2000000")
			self.cursor.execute("PRAGMA temp_store = MEMORY")
			
		else:  # fastest
			self.cursor.execute("PRAGMA journal_mode = OFF")
			self.cursor.execute("PRAGMA synchronous = OFF")
			self.cursor.execute("PRAGMA cache_size = -2000000")
			self.cursor.execute("PRAGMA temp_store = MEMORY")
			#self.cursor.execute("PRAGMA locking_mode = EXCLUSIVE")