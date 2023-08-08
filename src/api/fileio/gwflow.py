from .base import BaseFileModel, FileColumn as col
from database.project import base, gwflow
from database import lib as db_lib
from helpers import utils
import os.path
import configparser


class Gwflow_files(BaseFileModel):
	def __init__(self, file_name, version=None, swat_version=None, gwflow_ini_file='C:/SWAT/SWATPlus/gwflow/gwflow.ini'):
		self.file_name = file_name #txtinout directory
		self.version = version
		self.swat_version = swat_version
		self.gwflow_base = gwflow.self.gwflow_base.get_or_none()
		self.gwflow_config = configparser.ConfigParser().read(gwflow_ini_file)['DEFAULT']

	def read(self, database ='project'):
		raise NotImplementedError('Reading not implemented.')

	def write(self):
		self.write_input()
		self.write_rivcells()
		self.write_hrucell()
		self.write_cellhru()
		self.write_lsucell()
		self.write_rescells()
		self.write_floodplain()
		self.write_wetland()
		self.write_tiles()
		self.write_solutes()

	def write_input(self, file_name='gwflow.input'):
		if self.gwflow_base is not None:
			with open(os.path.join(self.file_name, file_name), 'w') as file:
				file.write(' INPUT FOR GWFLOW MODULE ')
				self.write_meta_line(file, file_name)

				file.write(' Basic information\n')
				file.write(' {} cell size (m)\n'.format(utils.num_pad(self.gwflow_base.cell_size, decimals=1, direction='left')))
				file.write(' {} number of rows, number of columns\n'.format(utils.string_pad('{} {}'.format(self.gwflow_base.row_count, self.gwflow_base.col_count), direction='left', default_pad=utils.DEFAULT_NUM_PAD)))
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
				file.write(' {} time step (days)\n'.format(utils.num_pad(self.gwflow_config.getfloat('timestep_balance', 1), decimals=2, direction='left'))) # missing in QSWAT+ tables?
				file.write(' {} write flags (daily, annual, avg. annual)\n'.format(utils.string_pad('{} {} {}'.format(self.gwflow_base.daily_output, self.gwflow_base.annual_output, self.gwflow_base.aa_output), direction='left', default_pad=utils.DEFAULT_NUM_PAD)))

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
				grid_cells = gwflow.Gwflow_grid.select().order_by(gwflow.Gwflow_grid.cell_id)

				status_lines = 'Cell Status (0=inactive; 1=active; 2=boundary)\n'
				elevation_lines = 'Ground Surface Elevation (m)\n'
				aquifer_thickness_lines = 'Aquifer Thickness(m)\n'
				zone_k_lines = 'Hydraulic conductivity zone\n'
				zone_yld_lines = 'Specific yield zone\n'
				recharge_lines = 'Recharge delay(Days)\n'
				et_lines = 'Groundwater ET Extinction Depth (m)	\n'
				init_head_lines = 'Initial Groundwater Head (m)\n'

				col = 1
				for cell in grid_cells:
					if col == self.gwflow_base.col_count:
						status_lines += '\n'
						elevation_lines += '\n'
						aquifer_thickness_lines += '\n'
						zone_k_lines += '\n'
						zone_yld_lines += '\n'
						recharge_lines += '\n'
						et_lines += '\n'
						init_head_lines += '\n'
						col = 1

					status_lines += '{}\t'.format(cell.status)
					elevation_lines += '{}\t'.format(utils.get_num_format(cell.elevation, 2))
					aquifer_thickness_lines += '{}\t'.format(utils.get_num_format(cell.aquifer_thickness, 2))
					zone_k_lines += '{}\t'.format(zone_id_index.get(cell.zone, 0))
					zone_yld_lines += '{}\t'.format(zone_id_index.get(cell.zone, 0))
					recharge_lines += '{}\t'.format(utils.get_num_format(self.gwflow_base.recharge_delay, 2))
					et_lines += '{}\t'.format(utils.get_num_format(self.gwflow_base.et_extinction_depth, 2))
					init_head_lines += '{}\t'.format(utils.get_num_format(cell.initial_head, 2))
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
				file.write('  Row  Column\n')
				file.write(' {} {}\n'.format(utils.int_pad(self.gwflow_config.getint('row_det', 0), 4), utils.int_pad(self.gwflow_config.getint('col_det', 0), 8)))
				file.write(' River Cell Information\n')
				file.write(' {}\n'.format(utils.get_num_format(self.gwflow_config.getfloat('river_depth', 5.0), 2)))

	def write_rivcells(self, file_name='gwflow.rivcells'):
		if self.gwflow_base is not None:
			with open(os.path.join(self.file_name, file_name), 'w') as file:
				file.write(' Cell-Channel Connection Information ')
				self.write_meta_line(file, file_name)

	def write_hrucell(self, file_name='gwflow.hrucell'):
		if self.gwflow_base is not None:
			with open(os.path.join(self.file_name, file_name), 'w') as file:
				file.write(' HRU-Cell Connection Information ')
				self.write_meta_line(file, file_name)

	def write_cellhru(self, file_name='gwflow.cellhru'):
		if self.gwflow_base is not None:
			with open(os.path.join(self.file_name, file_name), 'w') as file:
				file.write(' Cell-HRU Connection Information ')
				self.write_meta_line(file, file_name)

	def write_lsucell(self, file_name='gwflow.lsucell'):
		if self.gwflow_base is not None:
			with open(os.path.join(self.file_name, file_name), 'w') as file:
				file.write(' LSU (landscape unit) - Cell Connection Information ')
				self.write_meta_line(file, file_name)

	def write_rescells(self, file_name='gwflow.rescells'):
		if self.gwflow_base is not None:
			with open(os.path.join(self.file_name, file_name), 'w') as file:
				file.write(' Cell-Reservoir Connection Information ')
				self.write_meta_line(file, file_name)

	def write_floodplain(self, file_name='gwflow.floodplain'):
		if self.gwflow_base is not None:
			with open(os.path.join(self.file_name, file_name), 'w') as file:
				file.write(' gwflow floodplain cells (optional file; list cells that interact with channels, when channel water is in the floodplain) ')
				self.write_meta_line(file, file_name)

	def write_wetland(self, file_name='gwflow.wetland'):
		if self.gwflow_base is not None:
			with open(os.path.join(self.file_name, file_name), 'w') as file:
				file.write(' gwflow.wetland: parameters for groundwater-wetland interactions ')
				self.write_meta_line(file, file_name)

	def write_tiles(self, file_name='gwflow.tiles'):
		if self.gwflow_base is not None:
			with open(os.path.join(self.file_name, file_name), 'w') as file:
				file.write(' gwflow tile drain information ')
				self.write_meta_line(file, file_name)

	def write_solutes(self, file_name='gwflow.solutes'):
		if self.gwflow_base is not None:
			with open(os.path.join(self.file_name, file_name), 'w') as file:
				file.write(' solute parameters and initial concentrations ')
				self.write_meta_line(file, file_name)
