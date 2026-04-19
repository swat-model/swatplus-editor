from .base import BaseFileModel, FileColumn as col
from database.project import gis, gwflow, connect, reservoir, basin, base
from database.project.config import Project_config
from database import lib
from helpers import utils
from .connect import IndexHelper
import os.path
import sys


class Gwflow_files(BaseFileModel):
	def __init__(self, file_name, version=None, swat_version=None, project_db_file=None):
		self.file_name = file_name
		self.version = version
		self.swat_version = swat_version
		self.config = None

		pc = Project_config.get()
		if pc.use_gwflow:
			self.config = gwflow.Gwflow_config.get_or_none()

	def exists(self):
		return self.config is not None

	def update_codes_bsn(self):
		codes_bsn = basin.Codes_bsn.get_or_none()
		if codes_bsn is not None:
			codes_bsn.gwflow = 1 if self.config is not None else 0
			codes_bsn.save()

	def read(self, database='project'):
		raise NotImplementedError('Reading not implemented.')

	def _remove_if_exists(self, filename):
		path = os.path.join(self.file_name, filename)
		if os.path.isfile(path):
			os.remove(path)

	def write(self):
		self._zones = list(gwflow.Gwflow_zone.select().order_by(gwflow.Gwflow_zone.zone_id))
		self._zone_idx = {z.zone_id: i + 1 for i, z in enumerate(self._zones)}
		self._chan_idx = IndexHelper(connect.Chandeg_con).get()

		self.write_input()
		self.write_codes()
		self.write_zones_new()
		self.write_cells()
		self.write_cellcons()
		self.write_outputs()
		self.write_chancells()
		self.write_con()
		if self.config.recharge_type in (1, 3):
			self.write_hrucell()
		else:
			self._remove_if_exists('gwflow.hrucell')
		if self.config.recharge_type in (2, 3):
			self.write_lsucell()
		else:
			self._remove_if_exists('gwflow.lsucell')
		if self.config.reservoir_exchange:
			self.write_rescells()
		else:
			self._remove_if_exists('gwflow.rescells')
		if self.config.floodplain_exchange:
			self.write_floodplain()
		else:
			self._remove_if_exists('gwflow.floodplain')
		if self.config.wetland_exchange:
			self.write_wetland()
		else:
			self._remove_if_exists('gwflow.wetland')
		if self.config.tile_drainage:
			self.write_tiles()
		else:
			self._remove_if_exists('gwflow.tiles')
		if self.config.solute_transport:
			self.write_solutes()

	# ------------------------------------------------------------------
	# gwflow.input
	# ------------------------------------------------------------------

	def write_input(self):
		cfg = self.config
		with open(os.path.join(self.file_name, 'gwflow.input'), 'w') as f:
			f.write(' INPUT FOR GWFLOW MODULE ')
			self.write_meta_line(f, 'gwflow.input')
			f.write(' Basic information\n')

			is_struct = cfg.grid_type != 'unstructured'
			f.write(' {}\n'.format('structured' if is_struct else 'unstructured'))

			if is_struct:
				self._write_param(f, cfg.cell_size, 1, 'cell size (m)')
				f.write(' {} number of rows, number of columns\n'.format(
					utils.string_pad('{} {}'.format(cfg.num_rows, cfg.num_cols),
					direction='left', default_pad=utils.DEFAULT_NUM_PAD, no_space_removal=True)))
			else:
				self._write_param(f, cfg.num_cells, 0, 'number of gwflow cells')

			self._write_param(f, cfg.boundary_condition, 0, 'boundary condition type (1=constant head; 2=no-flow)')
			self._write_param(f, cfg.recharge_type, 0, 'recharge connection type (1=HRU-cell; 2=LSU-cell)')
			self._write_param(f, cfg.gw_soil_transfer, 0, 'groundwater-->soil transfer (0=off; 1=on)')
			self._write_param(f, cfg.saturation_excess, 0, 'groundwater saturation excess flow (0=off; 1=on)')
			self._write_param(f, cfg.external_pumping, 0, 'external groundwater pumping (0=off; 1=on)')
			self._write_param(f, cfg.tile_drainage, 0, 'groundwater tile drainage (0=off; 1=on)')
			self._write_param(f, cfg.reservoir_exchange, 0, 'groundwater-reservoir exchange (0=off; 1=on)')
			self._write_param(f, cfg.wetland_exchange, 0, 'groundwater-wetland exchange (0=off; 1=on)')
			self._write_param(f, cfg.floodplain_exchange, 0, 'groundwater-floodplain exchange (0=off; 1=on)')
			self._write_param(f, cfg.canal_seepage, 0, 'canal seepage to groundwater (0=off; 1=on)')
			self._write_param(f, cfg.solute_transport, 0, 'groundwater solute transport (0=off; 1=on)')
			self._write_param(f, cfg.timestep_days, 2, 'time step (days)')
			f.write(' {} write flags (daily, monthly, annual, avg. annual)\n'.format(
				utils.string_pad('{} {} {} {}'.format(
					cfg.daily_output, cfg.monthly_output, cfg.annual_output, cfg.aa_output),
				direction='left', default_pad=utils.DEFAULT_NUM_PAD, no_space_removal=True)))
			self._write_param(f, 1, 0, 'number of columns in output files')

			self._write_zones(f)

			f.write(' Grid Cell Information\n')
			if is_struct:
				self._write_structured_grid(f, cfg)
			else:
				self._write_unstructured_grid(f)

			self._write_output_times(f)
			self._write_obs_wells(f)

			f.write(' Cell for detailed daily sources/sink output\n')
			cell_det = 0
			if cfg.detail_row > 0 and cfg.detail_col > 0 and is_struct:
				cell_det = (cfg.detail_row - 1) * cfg.num_cols + cfg.detail_col
			f.write(' {}\n'.format(cell_det))

			f.write(' River Cell Information\n')
			f.write(' {}\n'.format(utils.get_num_format(cfg.river_depth, 2)))

	def _write_param(self, f, value, decimals, label):
		f.write(' {} {}\n'.format(utils.num_pad(value, decimals=decimals, direction='left'), label))

	def _write_zones(self, f):
		f.write(' Aquifer and Streambed Parameter Zones\n')
		n = len(self._zones)
		for label, attr in [('Aquifer Hydraulic Conductivity (m/day)', 'aquifer_k'),
							('Aquifer Specific Yield', 'specific_yield'),
							('Streambed Hydraulic Conductivity (m/day)', 'streambed_k'),
							('Streambed Thickness (m)', 'streambed_thickness')]:
			f.write(' {} Zones\n'.format(label))
			f.write(' {}\n'.format(n))
			for i, z in enumerate(self._zones, 1):
				f.write('{}\t{}\n'.format(i, utils.get_num_format(getattr(z, attr))))

	def _write_structured_grid(self, f, cfg):
		cells = {c.cell_id: c for c in gwflow.Gwflow_cell.select()}
		ncols = cfg.num_cols
		total = cfg.num_rows * ncols

		grid_attrs = [
			('Cell Status (0=inactive; 1=active; 2=boundary)', 'status', True),
			('Ground Surface Elevation (m)', 'elevation', False),
			('Aquifer Thickness(m)', 'aquifer_thickness', False),
			('Hydraulic conductivity zone', '_zone', True),
			('Specific yield zone', '_zone', True),
			('Recharge delay(Days)', 'recharge_delay', False),
			('Groundwater ET Extinction Depth (m)', 'extinction_depth', False),
			('Initial Groundwater Head (m)', 'initial_head', False),
		]

		for header, attr, is_int in grid_attrs:
			f.write(header + '\n')
			for row in range(cfg.num_rows):
				vals = []
				for col in range(ncols):
					idx = row * ncols + col + 1
					cell = cells.get(idx)
					if cell is None:
						vals.append('0')
					elif attr == '_zone':
						vals.append(str(self._zone_idx.get(cell.zone_id, 0)))
					elif is_int:
						vals.append(str(getattr(cell, attr, 0)))
					else:
						v = getattr(cell, attr, 0)
						if v is None:
							v = cell.elevation - 5 if attr == 'initial_head' else 0
						vals.append(utils.get_num_format(v, 2))
				f.write('\t'.join(vals) + '\n')

	def _write_unstructured_grid(self, f):
		"""Write per-cell rows. Fortran reader skips 13 lines before cell data."""
		cells = list(gwflow.Gwflow_cell.select().order_by(gwflow.Gwflow_cell.cell_id))
		conn_map = {}
		for cc in gwflow.Gwflow_cell_connection.select():
			conn_map.setdefault(cc.cell_id, []).append(cc.connected_cell_id)

		# Fortran skips 13 lines (do i=1,13; read header) before cell data.
		# Line 1 is "Grid Cell Information" written by caller.
		f.write('cell_id  status  elev  thck  K_zone  Sy_zone  delay  exdp  init  x  y  area  ncon  connections\n')
		for i in range(11):
			f.write('.\n')
		for c in cells:
			conns = conn_map.get(c.cell_id, [])
			zi = self._zone_idx.get(c.zone_id, 1)
			init = c.initial_head if c.initial_head else c.elevation - 5
			parts = [
				str(c.cell_id), str(c.status),
				'{:.2f}'.format(c.elevation),
				'{:.2f}'.format(c.aquifer_thickness),
				str(zi), str(zi),
				'{:.2f}'.format(c.recharge_delay),
				'{:.2f}'.format(c.extinction_depth),
				'{:.2f}'.format(init),
				'{:.2f}'.format(c.x_centroid),
				'{:.2f}'.format(c.y_centroid),
				'{:.2f}'.format(c.area),
				str(len(conns)),
			]
			parts.extend(str(x) for x in conns)
			f.write('\t'.join(parts) + '\n')

	def _write_output_times(self, f):
		f.write(' Times for Groundwater Head Output\n')
		times = list(gwflow.Gwflow_out_times.select().order_by(
			gwflow.Gwflow_out_times.year, gwflow.Gwflow_out_times.jday))
		f.write('\t\t{}\n'.format(len(times)))
		for t in times:
			f.write('{} {}\n'.format(utils.int_pad(t.year), utils.int_pad(t.jday)))

	def _write_obs_wells(self, f):
		f.write(' Groundwater Observation Locations\n')
		obs = list(gwflow.Gwflow_obs.select())
		f.write('\t\t{}\n'.format(len(obs)))
		for o in obs:
			f.write('{}\n'.format(o.cell_id))

	# ------------------------------------------------------------------
	# new split files: codes, zones, cells, cellcons, outputs
	# ------------------------------------------------------------------

	def _open_with_meta(self, name):
		f = open(os.path.join(self.file_name, name), 'w')
		f.write(self.get_meta_line(alt_file_name=name))
		return f

	def write_codes(self):
		cfg = self.config
		is_struct = cfg.grid_type != 'unstructured'
		rows = [
			('grid_type', 'unstructured' if not is_struct else 'structured', 'grid topology'),
			('ncell', cfg.num_cells if not is_struct else cfg.num_rows * cfg.num_cols, 'number of cells'),
			('cell_size', '{:.2f}'.format(cfg.cell_size) if is_struct else '0', 'cell size m (0=unstructured)'),
			('n_rows', cfg.num_rows if is_struct else 0, 'grid rows (0=unstructured)'),
			('n_cols', cfg.num_cols if is_struct else 0, 'grid cols (0=unstructured)'),
			('bc_type', cfg.boundary_condition, 'boundary condition (1=const head, 2=no flow)'),
			('conn_type', cfg.recharge_type, 'recharge connection (1=HRU, 2=LSU, 3=both)'),
			('gw_soil', cfg.gw_soil_transfer, 'groundwater to soil transfer (0=off, 1=on)'),
			('satx', cfg.saturation_excess, 'saturation excess flow (0=off, 1=on)'),
			('pumpex', cfg.external_pumping, 'external pumping (0=off, 1=on)'),
			('tile', cfg.tile_drainage, 'tile drainage (0=off, 1=on)'),
			('res', cfg.reservoir_exchange, 'reservoir exchange (0=off, 1=on)'),
			('wet', cfg.wetland_exchange, 'wetland exchange (0=off, 1=on)'),
			('fp', cfg.floodplain_exchange, 'floodplain exchange (0=off, 1=on)'),
			('canal', cfg.canal_seepage, 'canal seepage (0=off, 1=on)'),
			('solute', cfg.solute_transport, 'solute transport (0=off, 1=on)'),
			('time_step', '{:.2f}'.format(cfg.timestep_days), 'time step (days)'),
			('write_day', cfg.daily_output, 'daily output (0=off, 1=on)'),
			('write_mon', cfg.monthly_output, 'monthly output (0=off, 1=on)'),
			('write_yr', cfg.annual_output, 'annual output (0=off, 1=on)'),
			('write_aa', cfg.aa_output, 'avg annual output (0=off, 1=on)'),
			('river_thresh', '{:.2f}'.format(cfg.river_depth), 'river-bed elevation threshold (m)'),
		]
		with self._open_with_meta('gwflow.codes') as f:
			f.write('{:<16}{:<16}{}\n'.format('key', 'value', 'description'))
			for k, v, d in rows:
				f.write('{:<16}{:<16}{}\n'.format(str(k), str(v), d))

	def write_zones_new(self):
		with self._open_with_meta('gwflow.zones') as f:
			f.write('{:>10}{:>14}{:>14}{:>14}{:>16}\n'.format(
				'zone_id', 'aquifer_K', 'aquifer_Sy', 'streambed_K', 'streambed_thick'))
			for z in self._zones:
				f.write('{:>10}{:>14.5f}{:>14.5f}{:>14.5f}{:>16.5f}\n'.format(
					self._zone_idx[z.zone_id],
					z.aquifer_k if z.aquifer_k is not None else 0.0,
					z.specific_yield, z.streambed_k, z.streambed_thickness))

	def write_cells(self):
		cells = list(gwflow.Gwflow_cell.select().order_by(gwflow.Gwflow_cell.cell_id))
		with self._open_with_meta('gwflow.cells') as f:
			f.write('{:>8}{:>8}{:>10}{:>10}{:>8}{:>8}{:>8}{:>8}{:>10}{:>16}{:>16}{:>14}{:>10}{:>10}{:>10}{:>12}{:>12}{:>12}\n'.format(
				'cell_id', 'status', 'elev', 'thck', 'K_zone', 'Sy_zone', 'delay', 'exdp', 'init',
				'x', 'y', 'area',
				'strK', 'strthick', 'bc_type', 'tile_depth', 'tile_area', 'tile_K'))
			for c in cells:
				zi = self._zone_idx.get(c.zone_id, 1)
				init = c.initial_head if c.initial_head is not None else c.elevation - 5
				f.write('{:>8}{:>8}{:>10.2f}{:>10.2f}{:>8}{:>8}{:>8.2f}{:>8.2f}{:>10.2f}{:>16.2f}{:>16.2f}{:>14.2f}{:>10}{:>10}{:>10}{:>12}{:>12}{:>12}\n'.format(
					c.cell_id, c.status,
					c.elevation, c.aquifer_thickness, zi, zi,
					c.recharge_delay, c.extinction_depth, init,
					c.x_centroid, c.y_centroid, c.area,
					'null', 'null', 'null', 'null', 'null', 'null'))

	def write_cellcons(self):
		conn_map = {}
		for cc in gwflow.Gwflow_cell_connection.select():
			conn_map.setdefault(cc.cell_id_id, []).append(cc.connected_cell_id_id)
		cell_ids = sorted(conn_map.keys())
		with self._open_with_meta('gwflow.cellcons') as f:
			f.write('{:>8}{:>14}  {}\n'.format('cell_id', 'neighbor_tot', 'neighbor_ids'))
			for cid in cell_ids:
				ids = conn_map[cid]
				f.write('{:>8}{:>14}'.format(cid, len(ids)))
				for nid in ids:
					f.write('{:>8}'.format(nid))
				f.write('\n')

	def write_outputs(self):
		cfg = self.config
		times = list(gwflow.Gwflow_out_times.select().order_by(
			gwflow.Gwflow_out_times.year, gwflow.Gwflow_out_times.jday))
		obs = list(gwflow.Gwflow_obs.select())
		debug_cell = 0
		if cfg.detail_row > 0 and cfg.detail_col > 0 and cfg.grid_type != 'unstructured':
			debug_cell = (cfg.detail_row - 1) * cfg.num_cols + cfg.detail_col
		with self._open_with_meta('gwflow.outputs') as f:
			f.write('{:<22}{:>10}  {}\n'.format('category', 'value', 'note'))
			for t in times:
				combined = t.year * 1000 + t.jday
				f.write('{:<22}{:>10}  {}\n'.format('head_output_time', combined, 'YYYYDDD'))
			for o in obs:
				f.write('{:<22}{:>10}  {}\n'.format('observation_cell', o.cell_id_id, 'cell_id'))
			f.write('{:<22}{:>10}  {}\n'.format('detail_debug_cell', debug_cell, '0=none'))

	# ------------------------------------------------------------------
	# gwflow.chancells
	# ------------------------------------------------------------------

	def write_chancells(self):
		rows = list(gwflow.Gwflow_chancell.select().order_by(gwflow.Gwflow_chancell.cell_id))
		if not rows:
			return
		with self._open_with_meta('gwflow.chancells') as f:
			header_cols = [
				col('cell_id', not_in_db=True, padding_override=utils.DEFAULT_INT_PAD, direction='right'),
				col('elev_m', not_in_db=True, padding_override=utils.DEFAULT_NUM_PAD, direction='right'),
				col('channel', not_in_db=True, padding_override=utils.DEFAULT_INT_PAD, direction='right'),
				col('riv_length_m', not_in_db=True, padding_override=utils.DEFAULT_NUM_PAD, direction='right'),
				col('zone', not_in_db=True, padding_override=utils.DEFAULT_INT_PAD, direction='right')]
			self.write_headers(f, header_cols)
			f.write('\n')
			for r in rows:
				utils.write_int(f, r.cell_id)
				utils.write_num(f, r.bed_elevation, decimals=2)
				utils.write_int(f, self._chan_idx.get(r.channel_id, r.channel_id))
				utils.write_num(f, r.length_m, decimals=2)
				utils.write_int(f, self._zone_idx.get(r.zone_id, 1) if r.zone_id else 1)
				f.write('\n')

	# ------------------------------------------------------------------
	# gwflow.con
	# ------------------------------------------------------------------

	def write_con(self):
		rows = list(gwflow.Gwflow_chancell.select().order_by(gwflow.Gwflow_chancell.cell_id))
		if not rows:
			return
		with open(os.path.join(self.file_name, 'gwflow.con'), 'w') as f:
			f.write('gwflow.con: channel-cell spatial connections\n')
			f.write('{:<10}{:<10}{:<10}{:<10}{:<10}{:<10}{:<10}{:<10}{:<10}{:<10}{:<10}{:<10}{:<10}{:<14}{:<14}{:<12}{:<10}\n'.format(
				'NUMB', 'NAME', 'GISID', 'AREA', 'LAT', 'LONG', 'ELEV',
				'CELL', 'WST', 'CONST', 'OVER', 'RULE', 'SRC_TOT',
				'OBTYPE_OUT1', 'OBTYPNO_OUT1', 'HTYPE_OUT1', 'FRAC_OUT1'))
			for k, r in enumerate(rows, start=1):
				chan_con = self._chan_idx.get(r.channel_id, r.channel_id)
				f.write('{:>5}{:>5}{:>6}{:>5}{:>4}{:>5}{:>5}{:>9}{:>4}{:>6}{:>5}{:>5}{:>8}         sdc{:>12}        tot  1.00\n'.format(
					k, k, k, 0, 0, 0, 0, r.cell_id, 1, 0, 0, 0, 1, chan_con))

	# ------------------------------------------------------------------
	# gwflow.hrucell
	# ------------------------------------------------------------------

	def write_hrucell(self):
		hru_idx = IndexHelper(connect.Hru_con).get()
		rows = list(gwflow.Gwflow_hrucell.select().order_by(
			gwflow.Gwflow_hrucell.hru_id, gwflow.Gwflow_hrucell.cell_id))
		if not rows:
			return

		hru_areas = {h.id: h.arslp * 10000 for h in gis.Gis_hrus.select()}

		with self._open_with_meta('gwflow.hrucell') as f:
			header_cols = [
				col('hru', not_in_db=True, padding_override=utils.DEFAULT_INT_PAD, direction='right'),
				col('area_m2', not_in_db=True, padding_override=utils.DEFAULT_NUM_PAD, direction='right'),
				col('cell_id', not_in_db=True, padding_override=utils.DEFAULT_INT_PAD, direction='right'),
				col('overlap_m2', not_in_db=True, padding_override=utils.DEFAULT_NUM_PAD, direction='right')]
			self.write_headers(f, header_cols)
			f.write('\n')
			for r in rows:
				utils.write_int(f, hru_idx.get(r.hru_id, r.hru_id))
				utils.write_num(f, hru_areas.get(r.hru_id, 0), decimals=2)
				utils.write_int(f, r.cell_id)
				utils.write_num(f, r.area_m2, decimals=2)
				f.write('\n')

	# ------------------------------------------------------------------
	# gwflow.lsucell
	# ------------------------------------------------------------------

	def write_lsucell(self):
		lsu_idx = IndexHelper(connect.Rout_unit_con).get()
		rows = list(gwflow.Gwflow_lsucell.select().order_by(
			gwflow.Gwflow_lsucell.lsu_id, gwflow.Gwflow_lsucell.cell_id))
		if not rows:
			return
		with open(os.path.join(self.file_name, 'gwflow.lsucell'), 'w') as f:
			f.write(' LSU-Cell Connection Information ')
			self.write_meta_line(f, 'gwflow.lsucell')
			f.write('\n')
			for r in rows:
				utils.write_int(f, r.cell_id)
				utils.write_int(f, lsu_idx.get(r.lsu_id, r.lsu_id))
				utils.write_num(f, r.area_m2, decimals=2)
				f.write('\n')

	# ------------------------------------------------------------------
	# gwflow.rescells
	# ------------------------------------------------------------------

	def write_rescells(self):
		rows = list(gwflow.Gwflow_rescell.select().order_by(
			gwflow.Gwflow_rescell.reservoir_id, gwflow.Gwflow_rescell.cell_id))
		if not rows:
			return
		res_idx = IndexHelper(connect.Reservoir_con).get()
		cfg = self.config
		with open(os.path.join(self.file_name, 'gwflow.rescells'), 'w') as f:
			f.write(' Reservoir-cell connection information ')
			self.write_meta_line(f, 'gwflow.rescells')
			f.write('.\n')
			f.write('{}\n'.format(utils.get_num_format(cfg.resbed_thickness, 2)))
			f.write('{}\n'.format(utils.get_num_format(cfg.resbed_k, 6)))
			f.write('{}\n'.format(len(rows)))
			f.write('cell_id  res_id  res_stage\n')
			for r in rows:
				utils.write_int(f, r.cell_id)
				utils.write_int(f, res_idx.get(r.reservoir_id, r.reservoir_id))
				utils.write_num(f, r.stage, decimals=2)
				f.write('\n')

	# ------------------------------------------------------------------
	# gwflow.floodplain
	# ------------------------------------------------------------------

	def write_floodplain(self):
		rows = list(gwflow.Gwflow_fpcell.select().order_by(
			gwflow.Gwflow_fpcell.channel_id, gwflow.Gwflow_fpcell.cell_id))
		# upstream 455c43c: skip floodplain cells whose channel is not in the connectivity map
		rows = [r for r in rows if r.channel_id in self._chan_idx]
		if not rows:
			return
		with open(os.path.join(self.file_name, 'gwflow.floodplain'), 'w') as f:
			f.write(' Floodplain-cell connection information ')
			self.write_meta_line(f, 'gwflow.floodplain')
			f.write('{}\n'.format(len(rows)))
			f.write('cell_id  channel_id  K  area_m2\n')
			for r in rows:
				utils.write_int(f, r.cell_id)
				utils.write_int(f, self._chan_idx[r.channel_id])
				utils.write_num(f, r.conductivity, decimals=4)
				utils.write_num(f, r.area_m2, decimals=2)
				f.write('\n')

	# ------------------------------------------------------------------
	# gwflow.wetland
	# ------------------------------------------------------------------

	def write_wetland(self):
		with self._open_with_meta('gwflow.wetland') as f:
			f.write('{:<20}{:>14}\n'.format('name', 'bed_thick'))
			wet_thick = {v.wet_id: v.thickness for v in gwflow.Gwflow_wetland.select()}
			for wet in reservoir.Wetland_wet.select().order_by(reservoir.Wetland_wet.id):
				f.write('{:<20}{:>14.2f}\n'.format(
					wet.name,
					wet_thick.get(wet.id, self.config.wet_thickness)))

	# ------------------------------------------------------------------
	# gwflow.tiles
	# ------------------------------------------------------------------

	def write_tiles(self):
		tile_cells = list(gwflow.Gwflow_cell.select()
						  .where(gwflow.Gwflow_cell.tile == 1)
						  .order_by(gwflow.Gwflow_cell.cell_id))
		if not tile_cells:
			return
		cfg = self.config
		with open(os.path.join(self.file_name, 'gwflow.tiles'), 'w') as f:
			f.write(' Tile drain cell information ')
			self.write_meta_line(f, 'gwflow.tiles')
			f.write('\n')
			f.write('{}\t{}\t{}\n'.format(
				utils.get_num_format(cfg.tile_depth, 2),
				utils.get_num_format(cfg.tile_area, 2),
				utils.get_num_format(cfg.tile_k, 2)))
			f.write('1\n')
			f.write('{}\n'.format(len(tile_cells)))
			for c in tile_cells:
				f.write('{}\n'.format(c.cell_id))

	# ------------------------------------------------------------------
	# gwflow.solutes
	# ------------------------------------------------------------------

	def write_solutes(self):
		solutes = list(gwflow.Gwflow_solute.select().order_by(gwflow.Gwflow_solute.id))
		if not solutes:
			return
		cfg = self.config
		with open(os.path.join(self.file_name, 'gwflow.solutes'), 'w') as f:
			f.write(' Solute transport information ')
			self.write_meta_line(f, 'gwflow.solutes')
			f.write('\n')
			f.write('{}\n'.format(cfg.transport_steps))
			f.write('{}\n'.format(utils.get_num_format(cfg.disp_coef, 2)))
			f.write('{}\n'.format(len(solutes)))
			for s in solutes:
				f.write('{}\t{}\t{}\t{}\t{}\n'.format(
					s.name,
					utils.get_num_format(s.sorption_coef, 2),
					utils.get_num_format(s.rate_const, 6),
					utils.get_num_format(s.canal_irr, 2),
					utils.get_num_format(s.init_conc, 2)))
