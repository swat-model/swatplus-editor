from .base import BaseFileModel, FileColumn as col
from database.project import base, gis, gwflow, connect
from database import lib as db_lib
from helpers import utils
from .connect import IndexHelper
import os.path
import configparser
import numpy as np

class Gwflow_files(BaseFileModel):
	def __init__(self, file_name, version=None, swat_version=None, gwflow_ini_file='gwflow.ini'):
		self.file_name = file_name #txtinout directory
		self.version = version
		self.swat_version = swat_version
		self.gwflow_base = gwflow.Gwflow_base.get_or_none()
		self.gwflow_config = None
		if self.gwflow_base is not None:
			self.gwflow_config = configparser.ConfigParser().read(gwflow_ini_file)['DEFAULT']

	def read(self, database ='project'):
		raise NotImplementedError('Reading not implemented.')

	def write(self):
		self.write_input()
		self.write_chancells()
		self.write_hrucell()
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
				file.write(' structured\n')
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

	def write_chancells(self, file_name='gwflow.chancells'):
		if self.gwflow_base is not None:
			with open(os.path.join(self.file_name, file_name), 'w') as file:
				file.write(' Cell-Channel Connection Information ')
				self.write_meta_line(file, file_name)
				file.write('\n')

				header_cols = [col('ID', not_in_db=True, padding_override=utils.DEFAULT_INT_PAD, direction='left'),
				   col('elev_m', not_in_db=True, padding_override=utils.DEFAULT_NUM_PAD, direction='left'),
				   col('channel', not_in_db=True, padding_override=utils.DEFAULT_INT_PAD, direction='left'),
				   col('riv_length_m', not_in_db=True, padding_override=utils.DEFAULT_NUM_PAD, direction='left'),
				   col('zone', not_in_db=True, padding_override=utils.DEFAULT_INT_PAD, direction='left')]
				self.write_headers(file, header_cols)
				file.write('\n')

				grid_cells = gwflow.Gwflow_rivcell.select().join(gwflow.Gwflow_grid).order_by(gwflow.Gwflow_rivcell.cell_id)
				channels_gis_to_con = IndexHelper(connect.Chandeg_con).get()
				for cell in grid_cells:
					utils.write_int(file, cell.cell_id)
					utils.write_num(file, cell.cell.elevation, decimals=2)
					utils.write_int(file, channels_gis_to_con.get(cell.channel, 0))
					utils.write_num(file, cell.length_m, decimals=2)
					utils.write_int(file, cell.cell.zone_id)
					file.write('\n')

	def get_hru_data(self):
		hru_or_lsu_recharge = self.gwflow_config.getint('HRUorLSU_recharge', 2)
		hru_recharge = hru_or_lsu_recharge == 1 or hru_or_lsu_recharge == 3
		hrus_gis_to_con = IndexHelper(connect.Hru_con).get()
		return hru_recharge, hrus_gis_to_con

	def write_hrucell(self, file_names=['gwflow.hrucell','gwflow.cellhru']):
		if self.gwflow_base is not None:
			hru_recharge, hrus_gis_to_con = self.get_hru_data()
			if hru_recharge:
				grid_cells = gwflow.Gwflow_hrucell.select().join(gwflow.Gwflow_grid).join(gis.Gis_hrus)
				with open(os.path.join(self.file_name, file_names[0]), 'w') as file:
					file.write(' HRU-Cell Connection Information ')
					self.write_meta_line(file, file_names[0])
					file.write('\n')

					file.write(' HRUs that are connected to cells\n')
					hru_ids = list(set([v.hru_id for v in grid_cells])).sort()

					file.write('{}\n'.format(len(hru_ids)))
					for hru_id in hru_ids:
						file.write('{}\n'.format(hrus_gis_to_con.get(hru_id, 0)))
					file.write('\n')

					header_cols = [col('hru', not_in_db=True, padding_override=utils.DEFAULT_INT_PAD, direction='left'),
					col('area_m2', not_in_db=True, padding_override=utils.DEFAULT_NUM_PAD, direction='left'),
					col('cell_id', not_in_db=True, padding_override=utils.DEFAULT_INT_PAD, direction='left'),
					col('overlap_m2', not_in_db=True, padding_override=utils.DEFAULT_NUM_PAD, direction='left')]
					self.write_headers(file, header_cols)
					file.write('\n')

					for cell in grid_cells.order_by(gwflow.Gwflow_hrucell.hru_id, gwflow.Gwflow_hrucell.cell_id):
						utils.write_int(file, hrus_gis_to_con.get(cell.hru_id, 0))
						utils.write_num(file, cell.hru.arslp * 10000, decimals=2) # NOT SURE
						utils.write_int(file, cell.cell_id)
						utils.write_num(file, cell.area_m2, decimals=2) # NOT SURE
						file.write('\n')
				
				with open(os.path.join(self.file_name, file_names[1]), 'w') as file:
					file.write(' Cell-HRU Connection Information ')
					self.write_meta_line(file, file_names[1])
					file.write('\n')

					file.write('{}\t\t\tNumber of cells that intersect HRUs\n'.format(len(grid_cells)))

					header_cols = [col('cell_id', not_in_db=True, padding_override=utils.DEFAULT_INT_PAD, direction='left'),
					col('hru', not_in_db=True, padding_override=utils.DEFAULT_INT_PAD, direction='left'),
					col('cell_area', not_in_db=True, padding_override=utils.DEFAULT_NUM_PAD, direction='left'),
					col('overlap_m2', not_in_db=True, padding_override=utils.DEFAULT_NUM_PAD, direction='left')]
					self.write_headers(file, header_cols)
					file.write('\n')

					cell_size = self.gwflow_base.cell_size
					cell_area = cell_size * cell_size
					for cell in grid_cells.order_by(gwflow.Gwflow_hrucell.cell_id):
						utils.write_int(file, cell.cell_id)
						utils.write_int(file, hrus_gis_to_con.get(cell.hru_id, 0))
						utils.write_num(file, cell_area, decimals=2) # NOT SURE
						utils.write_num(file, cell.area_m2, decimals=2) # NOT SURE
						file.write('\n')

	def write_lsucell(self, file_name='gwflow.lsucell'):
		if self.gwflow_base is not None:
			with open(os.path.join(self.file_name, file_name), 'w') as file:
				file.write(' LSU (landscape unit) - Cell Connection Information ')
				self.write_meta_line(file, file_name)
				file.write('\n')

				grid_cells = gwflow.Gwflow_lsucell.select().join(gwflow.Gwflow_grid).join(gis.Gis_lsus)
				lsus_gis_to_con = IndexHelper(connect.Rout_unit_con).get()

				file.write(' HRUs that are connected to cells\n')
				unique_ids = list(set([v.lsu_id for v in grid_cells])).sort()

				file.write('{}\t\t total number of landscape units in model\n'.format(gis.Gis_lsus.select().count()))
				file.write('{}\t\t number of landscape units connected to grid cells\n'.format(len(unique_ids)))

				for id in unique_ids:
					file.write('{}\n'.format(lsus_gis_to_con.get(id, 0)))
				file.write('\n')

				file.write('connection information between landscape units and grid cells\n')

				header_cols = [col('lsu_id', not_in_db=True, padding_override=utils.DEFAULT_INT_PAD, direction='left'),
				col('lsu_area_m2', not_in_db=True, padding_override=utils.DEFAULT_NUM_PAD, direction='left'),
				col('cell_id', not_in_db=True, padding_override=utils.DEFAULT_INT_PAD, direction='left'),
				col('area_m2', not_in_db=True, padding_override=utils.DEFAULT_NUM_PAD, direction='left')]
				self.write_headers(file, header_cols)
				file.write('\n')

				for cell in grid_cells.order_by(gwflow.Gwflow_lsucell.lsu_id, gwflow.Gwflow_lsucell.cell_id):
					utils.write_int(file, lsus_gis_to_con.get(cell.lsu_id, 0))
					utils.write_num(file, cell.lsu.area * 10000, decimals=2) # NOT SURE
					utils.write_int(file, cell.cell_id)
					utils.write_num(file, cell.area_m2, decimals=2) # NOT SURE
					file.write('\n')

	def write_rescells(self, file_name='gwflow.rescells'):
		if self.gwflow_base is not None and gwflow.Gwflow_rivcell.select().count() > 0:
			with open(os.path.join(self.file_name, file_name), 'w') as file:
				file.write(' Cell-Reservoir Connection Information ')
				self.write_meta_line(file, file_name)

				grid_cells = gwflow.Gwflow_rivcell.select().join(gwflow.Gwflow_grid)
				res_gis_to_con = IndexHelper(connect.Reservoir_con).get()

				file.write(' Reservoir bed parameters\n')
				file.write(' {}\t\t bed thickness (m)\n'.format(self.gwflow_base.res_bed_thickness))
				file.write(' {}\t\t bed conductivity (m/day)\n'.format(self.gwflow_base.res_bed_k))
				file.write(' {}\t\t number of cells connected to reservoirs\n'.format(grid_cells.count()))

				header_cols = [col('cell_id', not_in_db=True, padding_override=utils.DEFAULT_INT_PAD, direction='left'),
				col('res_id', not_in_db=True, padding_override=utils.DEFAULT_INT_PAD, direction='left'),
				col('res_stage_m', not_in_db=True, padding_override=utils.DEFAULT_NUM_PAD, direction='left')]
				self.write_headers(file, header_cols)
				file.write('\n')

				for cell in grid_cells.order_by(gwflow.Gwflow_lsucell.lsu_id, gwflow.Gwflow_lsucell.cell_id):
					utils.write_int(file, cell.cell_id)
					utils.write_int(file, res_gis_to_con.get(cell.res_id, 0))
					utils.write_num(file, cell.res_stage, decimals=2) 
					file.write('\n')
			   

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

	def update_swatplus_files(self):
		#Copying code from original GWFLOW module
		#%%Modification of SWAT+ files (file.cio / object.cnt / rout_unit.con)
		#------- Modifying file.cio file---------------
		filename_cio = os.path.join(self.file_name, 'file.cio')
		file_cio = open(filename_cio, 'r')
		file_cio_lst = file_cio.readlines()
		file_cio.close()

		file_cio_lst[4] = file_cio_lst[4].split(' ')
		file_cio_lst[12] = file_cio_lst[12].split(' ')
		count = 0

		for i in range(0, len(file_cio_lst[4])):
			if file_cio_lst[4][i] != '':
				count+= 1
				if count == 5:
					file_cio_lst[4][i] = 'gwflow.con'
				if count == 6:
					file_cio_lst[4][i] = 'null'
		count = 0

		for i in range(0, len(file_cio_lst[12])):
			if file_cio_lst[12][i] != '':
				count+= 1
				if count == 3:
					file_cio_lst[12][i] = 'null'        
					
		file_cio_lst[4] = ' '.join(file_cio_lst[4])
		file_cio_lst[12] = ' '.join(file_cio_lst[12])

		file_cio_out = open(os.path.join(self.file_name, 'file.cio'), 'w')
		for line in file_cio_lst:
			file_cio_out.write(line)    
			
		file_cio_out.close()

		#------ Modifying object.cnt -----
		"""
		filename_objectcnt = os.path.join(self.file_name, 'object.cnt')
		object_cnt = open(filename_objectcnt, 'r')
		object_cnt_lines = object_cnt.readlines()
		object_cnt.close()

		object_cnt_lines[2] = object_cnt_lines[2].split(' ')
		count = 0
		for i in range(0, len(object_cnt_lines[2])):
			if object_cnt_lines[2][i] != '':
				count+= 1
				
				if count == 8:
					object_cnt_lines[2][i] = str(riv_unique_nr)
				if count == 9:
					object_cnt_lines[2][i] = '0'
			
		obj_numr = 0     
		count = 0       
		for i in range(0, len(object_cnt_lines[2])):
			if object_cnt_lines[2][i] != '':
				count+= 1
				if count >= 5 and count != 22:
					obj_numr+= float(object_cnt_lines[2][i])  
		count = 0
		for i in range(0, len(object_cnt_lines[2])):
			if object_cnt_lines[2][i] != '':
				count+= 1
				if count == 4:
					object_cnt_lines[2][i] = str(int(obj_numr))

		object_cnt_lines[2] = ' '.join(object_cnt_lines[2])

		object_cnt_out = open(os.path.join(self.file_name, 'object.cnt'), 'w')
		for line in object_cnt_lines:
			object_cnt_out.write(line)    
			
		#object_cnt.close()
		object_cnt_out.close()
		"""

		#----------Modifying rout_unit.con---------
		filename_routunit = os.path.join(self.file_name, 'rout_unit.con')
		nru = open(filename_routunit, "r")              #Delete first line of text generated by the model to be able to work in a dataframe
		lines = nru.readlines()
		line0 = lines[0]
		rout_unit_data = lines[1:]
		nru.close()

		for i in range(0, len(rout_unit_data)):
			rout_unit_data[i] = rout_unit_data[i].split()
			if i>0:
				rout_unit_data[i][12] = '1'
				del rout_unit_data[i][-4:]


		rout_unit_array = np.array(rout_unit_data)
		np.savetxt(os.path.join(self.file_name, 'rout_unit_data.txt'), rout_unit_array, fmt = '%-8s', delimiter = '\t')
		rout_txt = open(os.path.join(self.file_name, 'rout_unit_data.txt'), 'r')

		routunit = open(os.path.join(self.file_name, 'rout_unit.con'), 'w')            #Generation of base file

		routunit.write(line0)
		routunit.write(rout_txt.read())
		rout_txt.close()
		routunit.close()
