from playhouse.shortcuts import model_to_dict
from .base import BaseFileModel, FileColumn as col
from database.project import gis, gwflow, connect, reservoir, basin, base, setup
from database.project.config import Project_config
from database import lib
from helpers import table_mapper
from helpers import utils
from .connect import IndexHelper
import os.path
import sys
import csv

solute_grid_cols = ['init_no3', 'init_p', 'init_so4', 'init_ca', 'init_mg', 'init_na', 'init_k', 'init_cl', 'init_co3', 'init_hco3']

gis_cols = {
	'gwflow_hrucell': ['hru', connect.Hru_con, 'many', False],
	'gwflow_fpcell': ['channel', connect.Chandeg_con, 'single', True],
	'gwflow_rivcell': ['channel', connect.Chandeg_con, 'single', False],
	'gwflow_lsucell': ['lsu', connect.Rout_unit_con, 'many', False],
	'gwflow_rescell': ['res', connect.Reservoir_con, 'single', True],
}

class Gwflow_files(BaseFileModel):
	def __init__(self, file_name, version=None, swat_version=None, project_db_file=None):
		self.file_name = file_name #txtinout directory
		self.version = version
		self.swat_version = swat_version

		self.gwflow_base = None
		pc = Project_config.get()
		if pc.use_gwflow and project_db_file is not None:
			conn = lib.open_db(project_db_file)
			if lib.exists_table(conn, 'gwflow_base'):
				self.gwflow_base = gwflow.Gwflow_base.get_or_none()
			conn.close()	

	def exists(self):
		return self.gwflow_base is not None

	def update_codes_bsn(self):
		codes_bsn = basin.Codes_bsn.get_or_none()
		if codes_bsn is not None:
			if self.gwflow_base is not None:
				codes_bsn.gwflow = 1
			else:
				codes_bsn.gwflow = 0
			codes_bsn.save()	

	def get_grid_index_to_cell(self, table = gwflow.Gwflow_grid):
		data_dict = {}
		if self.gwflow_base is None:
			return
		
		grid_cells = table.select().order_by(table.cell_id)
		active_grid_cells = { cell.cell_id: cell for cell in grid_cells }

		cell_count = self.gwflow_base.row_count * self.gwflow_base.col_count
		for i in range(1, cell_count + 1):
			data_dict[i] = active_grid_cells.get(i, None)
		return data_dict

	def set_grid_index_to_cell(self):
		self.grid_index_to_cell = self.get_grid_index_to_cell()

	def read(self, database ='project'):
		raise NotImplementedError('Reading not implemented.')

	def write(self):
		self.set_grid_index_to_cell()
		self.write_input()
		self.write_chancells()
		self.write_hrucell()
		self.write_lsucell()
		self.write_rescells()
		self.write_floodplain()
		self.write_wetland()
		self.write_tiles()
		self.write_solutes()

	def write_cell_csv(self, file_name, table_name):
		table = table_mapper.types.get(table_name, None)
		gis_col = gis_cols.get(table_name, None)
		if table is None or gis_col is None:
			sys.exit("Table '{table}' is not valid for this request.".format(table=table_name))

		with open(file_name, mode='w') as file:
			csv_writer = csv.writer(file, delimiter=',', lineterminator='\n', quotechar='"', quoting=csv.QUOTE_MINIMAL)

			headers = []
			for field in table._meta.sorted_fields:
				headers.append(field.name)

			csv_writer.writerow(headers)

			query = table.select().order_by(table.cell_id)
			gis_to_con_name = IndexHelper(gis_col[1]).get_names()
				
			for row in query.dicts():
				values = []
				for col in headers:
					if col == gis_col[0]:
						values.append(gis_to_con_name.get(row[col], 'null'))
					else:
						values.append(row[col])
				csv_writer.writerow(values)

	def read_cell_csv(self, file_name, table_name):
		table = table_mapper.types.get(table_name, None)
		gis_col = gis_cols.get(table_name, None)
		if table is None or gis_col is None:
			sys.exit("Table '{table}' is not valid for this request.".format(table=table_name))

		gis_name_to_con = IndexHelper(gis_col[1]).get_id_from_name()

		with open(file_name, mode='r') as csv_file:
			dialect = csv.Sniffer().sniff(csv_file.readline())
			csv_file.seek(0)
			replace_commas = dialect is not None and dialect.delimiter != ','
			hasHeader = csv.Sniffer().has_header(csv_file.readline())
			csv_file.seek(0)

			csv_reader = csv.reader(csv_file, dialect)
			if hasHeader:
				headerLine = next(csv_reader)

			rows = []
			fields = table._meta.sorted_fields
			for val in csv_reader:
				if replace_commas:
					val = [item.replace(',', '.', 1) for item in val]

				row = {}
				j = 0
				table_gis_field = None
				for field in fields:
					value = None
					if len(val) > j:
						if field.name == gis_col[0]:
							table_gis_field = field
							value = gis_name_to_con.get(val[j], None)
						else:
							value = val[j]

					if type(value) is str:
						if value == 'null':
							value = None
					
					row[field.name] = value

					j += 1

				if gis_col[2] == 'single':
					m = table.get_or_none(table.cell_id == row['cell_id'])
				else:
					m = table.get_or_none((table.cell_id == row['cell_id']) & (table_gis_field == row[gis_col[0]]))

				if m is not None:
					if gis_col[2] == 'single':
						table.update(row).where(table.cell_id == row['cell_id']).execute()
					else:
						table.update(row).where((table.cell_id == row['cell_id']) & (table_gis_field == row[gis_col[0]])).execute()
				elif gis_col[3]:
					rows.append(row)
			
		lib.bulk_insert(base.db, table, rows)

	def write_wetland_csv(self, file_name):
		with open(file_name, mode='w') as file:
			csv_writer = csv.writer(file, delimiter=',', lineterminator='\n', quotechar='"', quoting=csv.QUOTE_MINIMAL)

			headers = ['wet_id', 'thickness']
			csv_writer.writerow(headers)

			wet_thick = { v.wet_id: v.thickness for v in gwflow.Gwflow_wetland.select().order_by(gwflow.Gwflow_wetland.wet_id) }

			for wet in reservoir.Wetland_wet.select().order_by(reservoir.Wetland_wet.id):
				values = [wet.name, wet_thick.get(wet.id, self.gwflow_base.wet_thickness)]
				csv_writer.writerow(values)

	def read_wetland_csv(self, file_name):
		with open(file_name, mode='r') as csv_file:
			dialect = csv.Sniffer().sniff(csv_file.readline())
			csv_file.seek(0)
			replace_commas = dialect is not None and dialect.delimiter != ','
			hasHeader = csv.Sniffer().has_header(csv_file.readline())
			csv_file.seek(0)

			csv_reader = csv.reader(csv_file, dialect)
			if hasHeader:
				headerLine = next(csv_reader)

			wet_names = { v.name: v.id for v in reservoir.Wetland_wet.select().order_by(reservoir.Wetland_wet.id) }

			rows = []
			for val in csv_reader:
				if replace_commas:
					val = [item.replace(',', '.', 1) for item in val]

				row = {}
				name = val[0]
				thickness = float(val[1])
				if name in wet_names:
					row['wet_id'] = wet_names[name]
					row['thickness'] = thickness

					m = gwflow.Gwflow_wetland.get_or_none(gwflow.Gwflow_wetland.wet_id == row['wet_id'])
					if m is not None:
						gwflow.Gwflow_wetland.update(row).where(gwflow.Gwflow_wetland.wet_id == row['wet_id']).execute()
					else:
						rows.append(row)
			
		lib.bulk_insert(base.db, gwflow.Gwflow_wetland, rows)

	def write_grid(self, file_name, column_name='', separator='\t', skip_header=False, return_string=False):
		table = gwflow.Gwflow_grid if column_name not in solute_grid_cols else gwflow.Gwflow_init_conc
		grid_cell_dict = self.get_grid_index_to_cell(table)
		if not return_string:
			file = open(file_name, 'w')
			
		if not skip_header and not return_string:
			self.write_meta_line(file, 'Gwflow grid data for "{}"'.format(column_name))
		lines = ''
		col = 1
		for key in grid_cell_dict:
			if col == self.gwflow_base.col_count + 1:
				lines += '\n'
				col = 1

			cell = grid_cell_dict[key]

			value = 0
			decimals = 2

			if cell is not None:
				cell_dict = model_to_dict(cell, recurse=False)
				value = cell_dict.get(column_name, 0)

				if column_name == 'tile':
					decimals = 0
			
			lines += '{}{}'.format(utils.get_num_format(value, decimals), separator)
			col += 1

		if not lines.endswith('\n'): lines += '\n'
		if return_string:
			return lines
		else:
			file.write(lines)

	def read_grid(self, file_name, column_name=''):
		table = gwflow.Gwflow_grid if column_name not in solute_grid_cols else gwflow.Gwflow_init_conc

		if column_name in solute_grid_cols and gwflow.Gwflow_init_conc.select().count() == 0:
			init_rows = []
			for cell in gwflow.Gwflow_grid.select().order_by(gwflow.Gwflow_grid.cell_id):
				init_row = {}
				init_row['cell_id'] = cell.cell_id
				init_row['init_no3'] = 0
				init_row['init_p'] = 0
				init_row['init_so4'] = 0
				init_row['init_ca'] = 0
				init_row['init_mg'] = 0
				init_row['init_na'] = 0
				init_row['init_k'] = 0
				init_row['init_cl'] = 0
				init_row['init_co3'] = 0
				init_row['init_hco3'] = 0
				init_rows.append(init_row)
			lib.bulk_insert(base.db, gwflow.Gwflow_init_conc, init_rows)
			
		grid_cell_dict = self.get_grid_index_to_cell(table)

		with open(file_name, 'r') as file:
			start_line = 2
			i = 1
			row = 1
			col = 1
			updated_cells = []
			for line in file:
				if i >= start_line:
					col = 1
					values = utils.split_multiple_delimiters(line)
					for value in values:
						cell_index = (row - 1) * self.gwflow_base.col_count + col
						cell = grid_cell_dict.get(cell_index, None)

						if cell is not None:
							cell_dict = model_to_dict(cell, recurse=False)
							if column_name in cell_dict:
								#sys.stdout.write('Updating cell {} with {} value {}\n'.format(cell_index, column_name, value))
								cell_dict[column_name] = float(value) if column_name != 'tile' else int(value)
								updated_cells.append(cell_dict)
						col += 1
					row += 1
				i += 1
		
			if len(updated_cells) > 0:
				sys.stdout.write('Updating {} cells\n'.format(len(updated_cells)))
				with base.db.atomic():
					#table.bulk_update(updated_cells, fields=[column_name], batch_size=100)
					for cell in updated_cells:
						table.update(cell).where(table.cell_id == cell['cell_id']).execute()

	def write_input(self, file_name='gwflow.input'):
		if self.gwflow_base is not None:
			with open(os.path.join(self.file_name, file_name), 'w') as file:
				file.write(' INPUT FOR GWFLOW MODULE ')
				self.write_meta_line(file, file_name)

				file.write(' Basic information\n')
				file.write(' structured\n')
				file.write(' {} cell size (m)\n'.format(utils.num_pad(self.gwflow_base.cell_size, decimals=1, direction='left')))
				file.write(' {} number of rows, number of columns\n'.format(utils.string_pad('{} {}'.format(self.gwflow_base.row_count, self.gwflow_base.col_count), direction='left', default_pad=utils.DEFAULT_NUM_PAD, no_space_removal=True)))
				file.write(' {} boundary condition type (1=constant head; 2=no-flow)\n'.format(utils.num_pad(self.gwflow_base.boundary_conditions, decimals=0, direction='left')))
				file.write(' {} recharge connection type (1=HRU-cell; 2=LSU-cell)\n'.format(utils.num_pad(self.gwflow_base.recharge, decimals=0, direction='left')))
				file.write(' {} groundwater-->soil transfer (0=off; 1=on)\n'.format(utils.num_pad(self.gwflow_base.soil_transfer, decimals=0, direction='left')))
				file.write(' {} groundwater saturation excess flow (0=off; 1=on)\n'.format(utils.num_pad(self.gwflow_base.saturation_excess, decimals=0, direction='left')))
				file.write(' {} external groundwater pumping (0=off; 1=on)\n'.format(utils.num_pad(self.gwflow_base.external_pumping, decimals=0, direction='left')))
				file.write(' {} groundwater tile drainage (0=off; 1=on)\n'.format(utils.num_pad(self.gwflow_base.tile_drainage, decimals=0, direction='left')))
				file.write(' {} groundwater-reservoir exchange (0=off; 1=on)\n'.format(utils.num_pad(self.gwflow_base.reservoir_exchange, decimals=0, direction='left')))
				file.write(' {} groundwater-wetland exchange (0=off; 1=on)\n'.format(utils.num_pad(self.gwflow_base.wetland_exchange, decimals=0, direction='left')))
				file.write(' {} groundwater-floodplain exchange (0=off; 1=on)\n'.format(utils.num_pad(self.gwflow_base.floodplain_exchange, decimals=0, direction='left')))
				file.write(' {} canal seepage to groundwater (0=off; 1=on)\n'.format(utils.num_pad(self.gwflow_base.canal_seepage, decimals=0, direction='left')))
				file.write(' {} groundwater solute transport (0=off; 1=on)\n'.format(utils.num_pad(self.gwflow_base.solute_transport, decimals=0, direction='left')))
				file.write(' {} time step (days)\n'.format(utils.num_pad(self.gwflow_base.timestep_balance, decimals=2, direction='left'))) # missing in QSWAT+ tables?
				file.write(' {} write flags (daily, annual, avg. annual)\n'.format(utils.string_pad('{} {} {}'.format(self.gwflow_base.daily_output, self.gwflow_base.annual_output, self.gwflow_base.aa_output), direction='left', default_pad=utils.DEFAULT_NUM_PAD, no_space_removal=True)))
				file.write(' {} number of columns in output files\n'.format(utils.num_pad(1, decimals=0, direction='left')))
				
				file.write(' Aquifer and Streambed Parameter Zones\n')

				zones = gwflow.Gwflow_zone.select().order_by(gwflow.Gwflow_zone.zone_id)
				zone_cnt = zones.count()
				zone_id_index = {} # just in case non-sequential IDs, map the ID to auto-num index

				file.write(' Aquifer Hydraulic Conductivity (m/day) Zones\n')
				file.write(' {}\n'.format(zone_cnt))
				i = 1
				for zone in zones:
					zone_id_index[zone.zone_id] = i
					file.write('{}\t{}\n'.format(i, utils.get_num_format(zone.aquifer_k)))
					i += 1

				file.write(' Aquifer Specific Yield Zones\n')
				file.write(' {}\n'.format(zone_cnt))
				i = 1
				for zone in zones:
					file.write('{}\t{}\n'.format(i, utils.get_num_format(zone.specific_yield)))
					i += 1

				file.write(' Streambed Hydraulic Conductivity (m/day) Zones\n')
				file.write(' {}\n'.format(zone_cnt))
				i = 1
				for zone in zones:
					file.write('{}\t{}\n'.format(i, utils.get_num_format(zone.streambed_k)))
					i += 1

				file.write(' Streambed Thickness (m) Zones\n')
				file.write(' {}\n'.format(zone_cnt))
				i = 1
				for zone in zones:
					file.write('{}\t{}\n'.format(i, utils.get_num_format(zone.streambed_thickness)))
					i += 1

				file.write(' Grid Cell Information\n')
				#grid_cells = gwflow.Gwflow_grid.select().order_by(gwflow.Gwflow_grid.cell_id)

				status_lines = 'Cell Status (0=inactive; 1=active; 2=boundary)\n'
				elevation_lines = 'Ground Surface Elevation (m)\n'
				aquifer_thickness_lines = 'Aquifer Thickness(m)\n'
				zone_k_lines = 'Hydraulic conductivity zone\n'
				zone_yld_lines = 'Specific yield zone\n'
				recharge_lines = 'Recharge delay(Days)\n'
				et_lines = 'Groundwater ET Extinction Depth (m)	\n'
				init_head_lines = 'Initial Groundwater Head (m)\n'

				col = 1
				for key in self.grid_index_to_cell:
					if col == self.gwflow_base.col_count + 1:
						status_lines += '\n'
						elevation_lines += '\n'
						aquifer_thickness_lines += '\n'
						zone_k_lines += '\n'
						zone_yld_lines += '\n'
						recharge_lines += '\n'
						et_lines += '\n'
						init_head_lines += '\n'
						col = 1

					cell = self.grid_index_to_cell[key]
					status_lines += '{}\t'.format(0 if cell is None else cell.status)
					elevation_lines += '{}\t'.format(utils.get_num_format(0 if cell is None else cell.elevation, 2))
					aquifer_thickness_lines += '{}\t'.format(utils.get_num_format(0 if cell is None else cell.aquifer_thickness, 2))
					zone_k_lines += '{}\t'.format(zone_id_index.get(0 if cell is None else cell.zone, 0))
					zone_yld_lines += '{}\t'.format(zone_id_index.get(0 if cell is None else cell.zone, 0))
					init_head_lines += '{}\t'.format(utils.get_num_format(0 if cell is None else cell.initial_head, 2))
					recharge_lines += '{}\t'.format(utils.get_num_format(self.gwflow_base.recharge_delay, 2))
					et_lines += '{}\t'.format(utils.get_num_format(0 if cell is None else cell.extinction_depth, 2))
					col += 1

				if not status_lines.endswith('\n'): status_lines += '\n'
				if not elevation_lines.endswith('\n'): elevation_lines += '\n'
				if not aquifer_thickness_lines.endswith('\n'): aquifer_thickness_lines += '\n'
				if not zone_k_lines.endswith('\n'): zone_k_lines += '\n'
				if not zone_yld_lines.endswith('\n'): zone_yld_lines += '\n'
				if not recharge_lines.endswith('\n'): recharge_lines += '\n'
				if not et_lines.endswith('\n'): et_lines += '\n'
				if not init_head_lines.endswith('\n'): init_head_lines += '\n'

				file.write(status_lines)
				file.write(elevation_lines)
				file.write(aquifer_thickness_lines)
				file.write(zone_k_lines)
				file.write(zone_yld_lines)
				file.write(recharge_lines)
				file.write(et_lines)
				file.write(init_head_lines)

				file.write(' Times for Groundwater Head Output\n')
				out_days = gwflow.Gwflow_out_days.select().order_by(gwflow.Gwflow_out_days.year, gwflow.Gwflow_out_days.jday)
				file.write('\t\t{}\n'.format(out_days.count()))
				for out_day in out_days:
					file.write('{} {}\n'.format(utils.int_pad(out_day.year), utils.int_pad(out_day.jday)))

				file.write(' Groundwater Observation Locations\n')
				obs_loc = gwflow.Gwflow_obs_locs.select()
				file.write('\t\t{}\n'.format(obs_loc.count()))
				for loc in obs_loc:
					file.write('{}\n'.format(loc.cell_id))

				file.write(' Cell for detailed daily sources/sink output\n')
				row_det = self.gwflow_base.daily_output_row
				col_det = self.gwflow_base.daily_output_col
				cell_det = 0
				if row_det > 0 and col_det > 0:
					cell_det = (row_det - 1) * self.gwflow_base.col_count + col_det
				file.write(' {}\n'.format(cell_det))
				
				file.write(' River Cell Information\n')
				file.write(' {}\n'.format(utils.get_num_format(self.gwflow_base.river_depth, 2)))

	def write_chancells(self, file_name='gwflow.chancells'):
		if self.gwflow_base is not None:
			with open(os.path.join(self.file_name, file_name), 'w') as file:
				file.write(' Cell-Channel Connection Information ')
				self.write_meta_line(file, file_name)
				file.write('\n')

				header_cols = [col('ID', not_in_db=True, padding_override=utils.DEFAULT_INT_PAD, direction='right'),
				   col('elev_m', not_in_db=True, padding_override=utils.DEFAULT_NUM_PAD, direction='right'),
				   col('channel', not_in_db=True, padding_override=utils.DEFAULT_INT_PAD, direction='right'),
				   col('riv_length_m', not_in_db=True, padding_override=utils.DEFAULT_NUM_PAD, direction='right'),
				   col('zone', not_in_db=True, padding_override=utils.DEFAULT_INT_PAD, direction='right')]
				self.write_headers(file, header_cols)
				file.write('\n')

				grid_cells = gwflow.Gwflow_rivcell.select(gwflow.Gwflow_rivcell, gwflow.Gwflow_grid).join(gwflow.Gwflow_grid).order_by(gwflow.Gwflow_rivcell.cell_id)
				channels_gis_to_con = IndexHelper(connect.Chandeg_con).get()
				for cell in grid_cells:
					utils.write_int(file, cell.cell_id.cell_id)
					utils.write_num(file, cell.cell_id.elevation, decimals=2)
					utils.write_int(file, channels_gis_to_con.get(cell.channel, 0))
					utils.write_num(file, cell.length_m, decimals=2)
					utils.write_int(file, cell.cell_id.zone_id)
					file.write('\n')

	def get_hru_data(self):
		hru_or_lsu_recharge = self.gwflow_base.recharge
		hru_recharge = hru_or_lsu_recharge == 1 or hru_or_lsu_recharge == 3
		hrus_gis_to_con = IndexHelper(connect.Hru_con).get()
		return hru_recharge, hrus_gis_to_con

	def write_hrucell(self, file_names=['gwflow.hrucell','gwflow.cellhru']):
		if self.gwflow_base is not None:
			hru_recharge, hrus_gis_to_con = self.get_hru_data()
			if hru_recharge:
			#if True:
				grid_cells = gwflow.Gwflow_hrucell.select(gwflow.Gwflow_hrucell, gwflow.Gwflow_grid, gis.Gis_hrus).join(gwflow.Gwflow_grid).switch(gwflow.Gwflow_hrucell).join(gis.Gis_hrus)
				
				#sql = grid_cells.sql()
				#sys.stdout.write(sql[0] % tuple(sql[1]))
				
				with open(os.path.join(self.file_name, file_names[0]), 'w') as file:
					file.write(' HRU-Cell Connection Information ')
					self.write_meta_line(file, file_names[0])
					file.write('\n')

					file.write(' HRUs that are connected to cells\n')
					hru_ids = list(set([v.hru.id for v in grid_cells]))
					hru_ids.sort()

					file.write('{}\n'.format(len(hru_ids)))
					for hru_id in hru_ids:
						file.write('{}\n'.format(hrus_gis_to_con.get(hru_id, 0)))
					file.write('\n')

					header_cols = [col('hru', not_in_db=True, padding_override=utils.DEFAULT_INT_PAD, direction='right'),
					col('area_m2', not_in_db=True, padding_override=utils.DEFAULT_NUM_PAD, direction='right'),
					col('cell_id', not_in_db=True, padding_override=utils.DEFAULT_INT_PAD, direction='right'),
					col('overlap_m2', not_in_db=True, padding_override=utils.DEFAULT_NUM_PAD, direction='right')]
					self.write_headers(file, header_cols)
					file.write('\n')

					for cell in grid_cells.order_by(gwflow.Gwflow_hrucell.hru.id, gwflow.Gwflow_hrucell.cell_id.cell_id):
						utils.write_int(file, hrus_gis_to_con.get(cell.hru.id, 0))
						utils.write_num(file, cell.hru.arslp * 10000, decimals=2) # NOT SURE
						utils.write_int(file, cell.cell_id.cell_id)
						utils.write_num(file, cell.area_m2, decimals=2) # NOT SURE
						file.write('\n')
				
				with open(os.path.join(self.file_name, file_names[1]), 'w') as file:
					file.write(' Cell-HRU Connection Information ')
					self.write_meta_line(file, file_names[1])
					file.write('\n')

					#file.write('{}\t\t\tNumber of cells that intersect HRUs\n'.format(len(grid_cells)))

					num_intersect = gwflow.Gwflow_hrucell.select(gwflow.Gwflow_hrucell.cell_id).distinct().count()
					file.write('{}\t\t\tNumber of cells that intersect HRUs\n'.format(num_intersect))

					header_cols = [col('cell_id', not_in_db=True, padding_override=utils.DEFAULT_INT_PAD, direction='right'),
					col('hru', not_in_db=True, padding_override=utils.DEFAULT_INT_PAD, direction='right'),
					col('cell_area', not_in_db=True, padding_override=utils.DEFAULT_NUM_PAD, direction='right'),
					col('overlap_m2', not_in_db=True, padding_override=utils.DEFAULT_NUM_PAD, direction='right')]
					self.write_headers(file, header_cols)
					file.write('\n')

					cell_size = self.gwflow_base.cell_size
					cell_area = cell_size * cell_size
					for cell in grid_cells.order_by(gwflow.Gwflow_hrucell.cell_id.cell_id):
						utils.write_int(file, cell.cell_id.cell_id)
						utils.write_int(file, hrus_gis_to_con.get(cell.hru.id, 0))
						utils.write_num(file, cell_area, decimals=2) # NOT SURE
						utils.write_num(file, cell.area_m2, decimals=2) # NOT SURE
						file.write('\n')

	def write_lsucell(self, file_name='gwflow.lsucell'):
		if self.gwflow_base is not None and (self.gwflow_base.recharge == 2 or self.gwflow_base.recharge == 3):
			with open(os.path.join(self.file_name, file_name), 'w') as file:
				file.write(' LSU (landscape unit) - Cell Connection Information ')
				self.write_meta_line(file, file_name)

				grid_cells = gwflow.Gwflow_lsucell.select(gwflow.Gwflow_lsucell, gis.Gis_lsus).join(gwflow.Gwflow_grid).switch(gwflow.Gwflow_lsucell).join(gis.Gis_lsus)
				lsus_gis_to_con = IndexHelper(connect.Rout_unit_con).get()
				
				unique_ids = list(set([v.lsu.id for v in grid_cells]))
				unique_ids.sort()

				file.write('{}\t\t total number of landscape units in model\n'.format(gis.Gis_lsus.select().count()))
				file.write('{}\t\t number of landscape units connected to grid cells\n'.format(len(unique_ids)))

				for id in unique_ids:
					file.write('{}\n'.format(lsus_gis_to_con.get(id, 0)))
				file.write('\n')

				file.write('connection information between landscape units and grid cells\n')

				header_cols = [col('lsu_id', not_in_db=True, padding_override=utils.DEFAULT_INT_PAD, direction='right'),
				col('lsu_area_m2', not_in_db=True, padding_override=utils.DEFAULT_NUM_PAD, direction='right'),
				col('cell_id', not_in_db=True, padding_override=utils.DEFAULT_INT_PAD, direction='right'),
				col('area_m2', not_in_db=True, padding_override=utils.DEFAULT_NUM_PAD, direction='right')]
				self.write_headers(file, header_cols)
				file.write('\n')

				for cell in grid_cells.order_by(gwflow.Gwflow_lsucell.cell_id):
					utils.write_int(file, lsus_gis_to_con.get(cell.lsu.id, 0))
					utils.write_num(file, cell.lsu.area * 10000, decimals=2) # NOT SURE
					utils.write_int(file, cell.cell_id)
					utils.write_num(file, cell.area_m2, decimals=2) # NOT SURE
					file.write('\n')

	def write_rescells(self, file_name='gwflow.rescells'):
		if self.gwflow_base is not None and self.gwflow_base.reservoir_exchange == 1 and gwflow.Gwflow_rescell.select().count() > 0:
			with open(os.path.join(self.file_name, file_name), 'w') as file:
				file.write(' Cell-Reservoir Connection Information ')
				self.write_meta_line(file, file_name)

				grid_cells = gwflow.Gwflow_rescell.select(gwflow.Gwflow_rescell, gwflow.Gwflow_grid).join(gwflow.Gwflow_grid)
				res_gis_to_con = IndexHelper(connect.Reservoir_con).get()

				file.write(' Reservoir bed parameters\n')
				file.write(' {}\t\t bed thickness (m)\n'.format(self.gwflow_base.resbed_thickness))
				file.write(' {}\t\t bed conductivity (m/day)\n'.format(self.gwflow_base.resbed_k))
				file.write(' {}\t\t number of cells connected to reservoirs\n'.format(grid_cells.count()))

				header_cols = [col('cell_id', not_in_db=True, padding_override=utils.DEFAULT_INT_PAD, direction='right'),
				col('res_id', not_in_db=True, padding_override=utils.DEFAULT_INT_PAD, direction='right'),
				col('res_stage_m', not_in_db=True, padding_override=utils.DEFAULT_NUM_PAD, direction='right')]
				self.write_headers(file, header_cols)
				file.write('\n')

				for cell in grid_cells.order_by(gwflow.Gwflow_rescell.cell_id.cell_id):
					utils.write_int(file, cell.cell_id.cell_id)
					utils.write_int(file, res_gis_to_con.get(cell.res_id, 0))
					utils.write_num(file, cell.res_stage, decimals=2) 
					file.write('\n')
			   
	def write_floodplain(self, file_name='gwflow.floodplain'):
		if self.gwflow_base is not None and self.gwflow_base.floodplain_exchange == 1 and gwflow.Gwflow_fpcell.select().count() > 0:
			with open(os.path.join(self.file_name, file_name), 'w') as file:
				file.write('gwflow floodplain cells (optional file; list cells that interact with channels, when channel water is in the floodplain) ')
				self.write_meta_line(file, file_name)

				grid_cells = gwflow.Gwflow_fpcell.select(gwflow.Gwflow_fpcell, gwflow.Gwflow_grid).join(gwflow.Gwflow_grid)
				cha_gis_to_con = IndexHelper(connect.Chandeg_con).get()
				file.write('{}\t\t\t\t\tNumber of floodplain cells\n'.format(grid_cells.count()))

				header_cols = [col('cell_id', not_in_db=True, padding_override=utils.DEFAULT_INT_PAD, direction='right'),
				col('chan_id', not_in_db=True, padding_override=utils.DEFAULT_INT_PAD, direction='right'),
				col('fp_K', not_in_db=True, padding_override=utils.DEFAULT_NUM_PAD, direction='right'),
				col('area_m2', not_in_db=True, padding_override=utils.DEFAULT_NUM_PAD, direction='right')]
				self.write_headers(file, header_cols)
				file.write('\n')

				for cell in grid_cells.order_by(gwflow.Gwflow_fpcell.cell_id.cell_id):
					utils.write_int(file, cell.cell_id.cell_id)
					utils.write_int(file, cha_gis_to_con.get(cell.channel_id, 0))
					utils.write_exp(file, 0, decimals=4) # CAN'T FIND IN DB
					utils.write_num(file, cell.area_m2, decimals=2) 
					file.write('\n')

	def write_wetland(self, file_name='gwflow.wetland'):
		if self.gwflow_base is not None and self.gwflow_base.wetland_exchange == 1:
			setup.SetupProjectDatabase.create_these_tables([gwflow.Gwflow_wetland])
			with open(os.path.join(self.file_name, file_name), 'w') as file:
				file.write('gwflow.wetland: parameters for groundwater-wetland interactions ')
				self.write_meta_line(file, file_name)

				file.write('wet_id = same as id listed in wetland.wet\n')
				file.write('thick_m = thickness (in meters) of wetland bottom material\n')
				file.write('(hydraulic conductivity is listed in hydrology.wet)\n')

				header_cols = [col('wet_id', not_in_db=True, padding_override=utils.DEFAULT_INT_PAD, direction='right'),
				col('thick_m', not_in_db=True, padding_override=utils.DEFAULT_NUM_PAD, direction='right')]
				self.write_headers(file, header_cols)
				file.write('\n')

				wet_thick = { v.wet_id: v.thickness for v in gwflow.Gwflow_wetland.select().order_by(gwflow.Gwflow_wetland.wet_id) }

				for wet in reservoir.Wetland_wet.select().order_by(reservoir.Wetland_wet.id):
					utils.write_int(file, wet.id)
					utils.write_num(file, wet_thick.get(wet.id, self.gwflow_base.wet_thickness), decimals=2) 
					file.write('\n')

	def write_tiles(self, file_name='gwflow.tiles'):
		if self.gwflow_base is not None and self.gwflow_base.tile_drainage == 1:
			with open(os.path.join(self.file_name, file_name), 'w') as file:
				file.write('gwflow tile drain information ')
				self.write_meta_line(file, file_name)

				file.write(' {}\t\t Depth (m) of tiles below ground surface\n'.format(utils.num_pad(self.gwflow_base.tile_depth, 5)))
				file.write(' {}\t\t Area (m2) of groundwater inflow * flow length\n'.format(utils.num_pad(self.gwflow_base.tile_area, 5)))
				file.write(' {}\t\t Hydraulic conductivity (m/day) of the drain perimeter\n'.format(utils.num_pad(self.gwflow_base.tile_k, 5)))
				file.write(' {}\t\t Tile cell groups (flag: 0=no; 1=yes)\n'.format(utils.int_pad(self.gwflow_base.tile_groups, default_pad=utils.DEFAULT_NUM_PAD)))

				grid_cells = gwflow.Gwflow_grid.select().order_by(gwflow.Gwflow_grid.cell_id)

				status_lines = 'gwflow tile cells (0=no tile; 1=tiles are present)\n'

				col = 1
				for key in self.grid_index_to_cell:
					if col == self.gwflow_base.col_count + 1:
						status_lines += '\n'
						col = 1

					cell = self.grid_index_to_cell[key]
					status_lines += '{}\t'.format(0 if cell is None else cell.tile)
					col += 1

				if not status_lines.endswith('\n'): status_lines += '\n'

				file.write(status_lines)

	def write_solutes(self, file_name='gwflow.solutes'):
		if self.gwflow_base is not None and self.gwflow_base.solute_transport == 1:
			with open(os.path.join(self.file_name, file_name), 'w') as file:
				file.write('solute parameters and initial concentrations ')
				self.write_meta_line(file, file_name)

				file.write('general parameters\n')
				file.write(' {}\t\t number of transport time steps for flow time step\n'.format(self.gwflow_base.transport_steps))
				file.write(' {}\t\t dispersion coefficient (m2/day)\n'.format(self.gwflow_base.disp_coef))

				file.write('solute parameters: name,sorption,rate constant,canal_irrig (one row per active solute)\n')
				solutes = gwflow.Gwflow_solutes.select()
				for solute in solutes:
					utils.write_string(file, solute.solute_name, default_pad=8, direction='left')
					utils.write_num(file, solute.sorption, decimals=2)
					utils.write_num(file, solute.rate_const, decimals=4)
					utils.write_num(file, solute.canal_irr, decimals=2)
					file.write('\n')

				file.write('initial concentrations (g/m3)\n')
				for solute in solutes:
					file.write('{}\n'.format(solute.solute_name))
					file.write('{}\n'.format(solute.init_data))

					if solute.init_data == 'single':
						file.write(utils.get_num_format(solute.init_conc, 2))
						file.write('\n')
					else:
						solute_name = solute.solute_name if solute.solute_name != 'no3-n' else 'no3'
						grid_text = self.write_grid(os.path.join(self.file_name, file_name), column_name='init_{}'.format(solute_name), skip_header=True, return_string=True)
						file.write(grid_text)
