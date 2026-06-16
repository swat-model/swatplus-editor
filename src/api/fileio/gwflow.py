from .base import BaseFileModel, FileColumn as col
from database.project import gis, gwflow, connect, reservoir, basin, base, simulation
from database.project.config import Project_config
from database import lib
from helpers import table_mapper
from helpers import utils
from .connect import IndexHelper
import os.path
import sys
import datetime
import csv

# This is used by the UI
gis_cols = {
	'gwflow_hrucell': ['hru_id', connect.Hru_con, 'many', False],
	'gwflow_fpcell': ['channel_id', connect.Chandeg_con, 'many', True],
	'gwflow_chancell': ['channel_id', connect.Chandeg_con, 'single', False],
	'gwflow_lsucell': ['lsu_id', connect.Rout_unit_con, 'many', False],
	'gwflow_rescell': ['reservoir_id', connect.Reservoir_con, 'many', True],
}

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
		self._ncell = gwflow.Gwflow_cell.select().count()

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
			self._remove_if_exists('hrucell.gw')
		if self.config.recharge_type in (2, 3):
			self.write_lsucell()
		else:
			self._remove_if_exists('lsucell.gw')
		if self.config.reservoir_exchange:
			self.write_rescells()
		else:
			self._remove_if_exists('rescell.gw')
		if self.config.floodplain_exchange:
			self.write_floodplain()
		else:
			self._remove_if_exists('floodplain.gw')
		if self.config.wetland_exchange:
			self.write_wetland()
		else:
			self._remove_if_exists('wetland.gw')
		if self.config.tile_drainage:
			self.write_tiles()
		else:
			self._remove_if_exists('tile.gw')
		if self.config.external_pumping:
			self.write_pumpex()
		else:
			self._remove_if_exists('pumpex.gw')
		self.write_hru_pump_observe()
		self.write_tvheads()
		self.write_sw_group()
		self.write_ponds()
		self.write_pond_cell()
		self.write_pond_div()
		self.write_phreato()
		self.write_phreato_cell()
		self.write_chan_depth()
		if self.config.solute_transport:
			self.write_solutes()
			self.write_cell_solute()
		else:
			self._remove_if_exists('solute.gw')
			self._remove_if_exists('cell_sol.gw')

	def _open_with_meta(self, name):
		f = open(os.path.join(self.file_name, name), 'w')
		f.write(self.get_meta_line(alt_file_name=name))
		return f

	def write_codes(self):
		cfg = self.config
		is_struct = cfg.grid_type != 'unstructured'
		cols = [
			('grid_type', 'unstructured' if not is_struct else 'structured'),
			('ncell', self._ncell),
			('cell_size', '{:.2f}'.format(cfg.cell_size) if is_struct else '0'),
			('n_rows', cfg.num_rows if is_struct else 0),
			('n_cols', cfg.num_cols if is_struct else 0),
			('bc_type', cfg.boundary_condition),
			('conn_type', cfg.recharge_type),
			('gw_soil', cfg.gw_soil_transfer),
			('satx', cfg.saturation_excess),
			('pumpex', cfg.external_pumping),
			('tile', cfg.tile_drainage),
			('res', cfg.reservoir_exchange),
			('wet', cfg.wetland_exchange),
			('fp', cfg.floodplain_exchange),
			('canal', cfg.canal_seepage),
			('solute', cfg.solute_transport),
			('heat', cfg.heat_transport),
			('time_step', '{:.2f}'.format(cfg.timestep_days)),
			('write_day', cfg.daily_output),
			('write_mon', cfg.monthly_output),
			('write_yr', cfg.annual_output),
			('write_aa', cfg.aa_output),
			('river_thresh', '{:.2f}'.format(cfg.river_depth)),
		]
		with self._open_with_meta('codes.gw') as f:
			f.write(''.join('{:>14}'.format(k) for k, v in cols) + '\n')
			f.write(''.join('{:>14}'.format(str(v)) for k, v in cols) + '\n')

	def write_zones_new(self):
		with self._open_with_meta('zones.gw') as f:
			f.write('{:>10}{:>14}{:>14}{:>14}{:>16}{:>14}\n'.format(
				'zone_id', 'aquifer_K', 'aquifer_Sy', 'streambed_K', 'streambed_thick', 'thermal_K'))
			for z in self._zones:
				f.write('{:>10}{:>14.5f}{:>14.5f}{:>14.5f}{:>16.5f}{:>14.5f}\n'.format(
					self._zone_idx[z.zone_id],
					z.aquifer_k if z.aquifer_k is not None else 0.0,
					z.specific_yield, z.streambed_k, z.streambed_thickness,
					z.thermal_k))

	def write_cells(self):
		cells = list(gwflow.Gwflow_cell.select().order_by(gwflow.Gwflow_cell.cell_id))
		pad = len(str(self._ncell))
		with self._open_with_meta('cells.gw') as f:
			f.write(utils.int_pad('id') + utils.string_pad('name', direction='left') + utils.int_pad('gis_id'))
			f.write('{:>8}{:>10}{:>10}{:>8}{:>8}{:>8}{:>8}{:>10}{:>16}{:>16}{:>14}{:>10}{:>10}{:>10}{:>12}{:>12}{:>12}{:>8}{:>8}{:>12}\n'.format(
				'status', 'elev', 'thck', 'K_zone', 'Sy_zone', 'delay', 'exdp', 'init',
				'x', 'y', 'area',
				'strK', 'strthick', 'bc_type', 'tile_depth', 'tile_area', 'tile_K', 'row', 'col', 'init_temp'))
			for c in cells:
				zi = self._zone_idx.get(c.zone_id, 1)
				init = c.initial_head if c.initial_head is not None else c.elevation - 5
				def fmt_override(v):
					return 'null' if v is None else '{:.5f}'.format(v)
				def fmt_int_override(v):
					return 'null' if v is None else str(v)
				f.write(utils.int_pad(c.cell_id) + utils.string_pad('cell' + str(c.cell_id).zfill(pad), direction='left') + utils.int_pad(c.gis_id if c.gis_id is not None else c.cell_id))
				f.write('{:>8}{:>10.2f}{:>10.2f}{:>8}{:>8}{:>8.2f}{:>8.2f}{:>10.2f}{:>16.2f}{:>16.2f}{:>14.2f}{:>10}{:>10}{:>10}{:>12}{:>12}{:>12}{:>8}{:>8}{:>12}\n'.format(
					c.status,
					c.elevation, c.aquifer_thickness, zi, zi,
					0.0, c.extinction_depth, init,
					c.x_centroid, c.y_centroid, c.area,
					fmt_override(c.streambed_k), fmt_override(c.streambed_thickness),
					fmt_int_override(c.bc_type),
					fmt_override(c.tile_depth), fmt_override(c.tile_area), fmt_override(c.tile_k),
					c.row if c.row is not None else 0, c.col if c.col is not None else 0,
					fmt_override(c.init_temp)))

	def write_cellcons(self):
		conn_map = {}
		for cc in gwflow.Gwflow_cell_connection.select():
			conn_map.setdefault(cc.cell_id_id, []).append(cc.connected_cell_id_id)
		ncell = self._ncell
		with self._open_with_meta('cellcon.gw') as f:
			f.write('{:>8}{:>14}  {}\n'.format('cell_id', 'neighbor_tot', 'neighbor_ids'))
			for cid in range(1, ncell + 1):
				ids = conn_map.get(cid, [])
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
		with self._open_with_meta('outputs.gw') as f:
			f.write('{:<22}{:>10}  {}\n'.format('category', 'value', 'note'))
			for t in times:
				combined = t.year * 1000 + t.jday
				f.write('{:<22}{:>10}  {}\n'.format('head_output_time', combined, 'YYYYDDD'))
			for o in obs:
				f.write('{:<22}{:>10}  {}\n'.format('observation_cell', o.cell_id_id, 'cell_id'))
			f.write('{:<22}{:>10}  {}\n'.format('detail_debug_cell', debug_cell, '0=none'))

	def write_chancells(self):
		rows = list(gwflow.Gwflow_chancell.select().order_by(gwflow.Gwflow_chancell.cell_id))
		if not rows:
			return
		with self._open_with_meta('chancell.gw') as f:
			header_cols = [
				col('cell_id', not_in_db=True, padding_override=utils.DEFAULT_INT_PAD, direction='right'),
				col('elev_m', not_in_db=True, padding_override=utils.DEFAULT_NUM_PAD, direction='right'),
				col('channel', not_in_db=True, padding_override=utils.DEFAULT_INT_PAD, direction='right'),
				col('riv_length_m', not_in_db=True, padding_override=utils.DEFAULT_NUM_PAD, direction='right'),
				col('zone', not_in_db=True, padding_override=utils.DEFAULT_INT_PAD, direction='right'),
				col('dep_zone', not_in_db=True, padding_override=utils.DEFAULT_INT_PAD, direction='right'),
				col('obs', not_in_db=True, padding_override=utils.DEFAULT_INT_PAD, direction='right')]
			self.write_headers(f, header_cols)
			f.write('\n')
			for r in rows:
				utils.write_int(f, r.cell_id)
				utils.write_num(f, r.bed_elevation, decimals=2)
				utils.write_int(f, self._chan_idx.get(r.channel_id, r.channel_id))
				utils.write_num(f, r.length_m, decimals=2)
				utils.write_int(f, self._zone_idx.get(r.zone_id, 1) if r.zone_id else 1)
				utils.write_int(f, r.dep_zone if r.dep_zone is not None else 0)
				utils.write_int(f, r.obs)
				f.write('\n')

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

	def write_hrucell(self):
		hru_idx = IndexHelper(connect.Hru_con).get()
		rows = list(gwflow.Gwflow_hrucell.select().order_by(
			gwflow.Gwflow_hrucell.hru_id, gwflow.Gwflow_hrucell.cell_id))
		if not rows:
			return

		hru_areas = {h.id: h.arslp * 10000 for h in gis.Gis_hrus.select()}

		with self._open_with_meta('hrucell.gw') as f:
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

	def write_lsucell(self):
		lsu_idx = IndexHelper(connect.Rout_unit_con).get()
		rows = list(gwflow.Gwflow_lsucell.select().order_by(
			gwflow.Gwflow_lsucell.lsu_id, gwflow.Gwflow_lsucell.cell_id))
		if not rows:
			return
		with open(os.path.join(self.file_name, 'lsucell.gw'), 'w') as f:
			f.write(' LSU-Cell Connection Information ')
			self.write_meta_line(f, 'lsucell.gw')
			f.write('\n')
			for r in rows:
				utils.write_int(f, r.cell_id)
				utils.write_int(f, lsu_idx.get(r.lsu_id, r.lsu_id))
				utils.write_num(f, r.area_m2, decimals=2)
				f.write('\n')

	def write_rescells(self):
		rows = list(gwflow.Gwflow_rescell.select().order_by(
			gwflow.Gwflow_rescell.reservoir_id, gwflow.Gwflow_rescell.cell_id))
		if not rows:
			return
		res_idx = IndexHelper(connect.Reservoir_con).get()
		cfg = self.config
		with open(os.path.join(self.file_name, 'rescell.gw'), 'w') as f:
			f.write(' Reservoir-cell connection information ')
			self.write_meta_line(f, 'rescell.gw')
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

	def write_floodplain(self):
		rows = list(gwflow.Gwflow_fpcell.select().order_by(
			gwflow.Gwflow_fpcell.channel_id, gwflow.Gwflow_fpcell.cell_id))
		# upstream 455c43c: skip floodplain cells whose channel is not in the connectivity map
		rows = [r for r in rows if r.channel_id in self._chan_idx]
		if not rows:
			return
		with open(os.path.join(self.file_name, 'floodplain.gw'), 'w') as f:
			f.write(' Floodplain-cell connection information ')
			self.write_meta_line(f, 'floodplain.gw')
			f.write('{}\n'.format(len(rows)))
			f.write('cell_id  channel_id  K  area_m2\n')
			for r in rows:
				utils.write_int(f, r.cell_id)
				utils.write_int(f, self._chan_idx[r.channel_id])
				utils.write_num(f, r.conductivity, decimals=4)
				utils.write_num(f, r.area_m2, decimals=2)
				f.write('\n')

	def write_wetland(self):
		with self._open_with_meta('wetland.gw') as f:
			f.write('{:<20}{:>14}\n'.format('name', 'bed_thick'))
			wet_thick = {v.wet_id: v.thickness for v in gwflow.Gwflow_wetland.select()}
			for wet in reservoir.Wetland_wet.select().order_by(reservoir.Wetland_wet.id):
				f.write('{:<20}{:>14.2f}\n'.format(
					wet.name,
					wet_thick.get(wet.id, self.config.wet_thickness)))

	def write_tiles(self):
		tile_cells = list(gwflow.Gwflow_cell.select()
						  .where(gwflow.Gwflow_cell.tile == 1)
						  .order_by(gwflow.Gwflow_cell.cell_id))
		if not tile_cells:
			return
		cfg = self.config
		with open(os.path.join(self.file_name, 'tile.gw'), 'w') as f:
			f.write(' Tile drain cell information ')
			self.write_meta_line(f, 'tile.gw')
			f.write('\n')
			f.write('{}\t{}\t{}\n'.format(
				utils.get_num_format(cfg.tile_depth, 2),
				utils.get_num_format(cfg.tile_area, 2),
				utils.get_num_format(cfg.tile_k, 2)))
			f.write('1\n')
			f.write('{}\n'.format(len(tile_cells)))
			for c in tile_cells:
				f.write('{}\n'.format(c.cell_id))

	def write_pumpex(self):
		rows = list(gwflow.Gwflow_pump.select().order_by(
			gwflow.Gwflow_pump.cell_id, gwflow.Gwflow_pump.start_year, gwflow.Gwflow_pump.start_day))
		if not rows:
			return
		pad = len(str(self._ncell))
		with self._open_with_meta('pumpex.gw') as f:
			f.write('{:>12}{:>10}{:>12}{:>10}{:>10}{:>10}{:>10}\n'.format(
				'name', 'cell_id', 'rate', 'yr_start', 'dy_start', 'yr_end', 'dy_end'))
			for r in rows:
				f.write('{:>12}{:>10}{:>12.2f}{:>10}{:>10}{:>10}{:>10}\n'.format(
					'cell' + str(r.cell_id_id).zfill(pad), r.cell_id_id, r.rate_m3day,
					r.start_year, r.start_day, r.end_year, r.end_day))

	def write_hru_pump_observe(self):
		rows = list(gwflow.Gwflow_hru_pump_obs.select().order_by(gwflow.Gwflow_hru_pump_obs.hru_id))
		if not rows:
			self._remove_if_exists('hru_pump.gw')
			return
		hru_idx = IndexHelper(connect.Hru_con).get()
		with self._open_with_meta('hru_pump.gw') as f:
			f.write('{}\n'.format(len(rows)))
			for r in rows:
				f.write('{:>10}\n'.format(hru_idx.get(r.hru_id, r.hru_id)))

	def write_tvheads(self):
		rows = list(gwflow.Gwflow_tvhead.select().order_by(
			gwflow.Gwflow_tvhead.cell_id, gwflow.Gwflow_tvhead.year))
		if not rows:
			self._remove_if_exists('tvheads.gw')
			return
		sim = simulation.Time_sim.get_or_none()
		yr0 = sim.yrc_start
		nbyr = sim.yrc_end - sim.yrc_start + 1
		by_cell = {}
		for r in rows:
			by_cell.setdefault(r.cell_id, {})[r.year] = r.head
		with self._open_with_meta('tvheads.gw') as f:
			f.write('{:>10}'.format('cell_id') + ''.join('{:>14}'.format('head_yr' + str(j + 1)) for j in range(nbyr)) + '\n')
			for cid in sorted(by_cell):
				heads = by_cell[cid]
				f.write('{:>10}'.format(cid))
				for j in range(nbyr):
					f.write('{:>14.5f}'.format(heads.get(yr0 + j, 0.0)))
				f.write('\n')

	def write_sw_group(self):
		rows = list(gwflow.Gwflow_sw_group.select().order_by(
			gwflow.Gwflow_sw_group.group_id, gwflow.Gwflow_sw_group.cell_id))
		if not rows:
			self._remove_if_exists('sw_group.gw')
			return
		by_g = {}
		for r in rows:
			by_g.setdefault(r.group_id, []).append(r.cell_id)
		with self._open_with_meta('sw_group.gw') as f:
			f.write('{:>10}{:>10}  {}\n'.format('group_id', 'ncell', 'cell_ids'))
			for g in sorted(by_g):
				cids = by_g[g]
				f.write('{:>10}{:>10}'.format(g, len(cids)))
				for c in cids:
					f.write('{:>10}'.format(c))
				f.write('\n')

	def write_ponds(self):
		ponds = list(gwflow.Gwflow_pond.select().order_by(gwflow.Gwflow_pond.id))
		if not ponds:
			self._remove_if_exists('ponds.gw')
			return
		nsol = gwflow.Gwflow_solute.select().count()
		conc = {}
		for ps in gwflow.Gwflow_pond_solute.select():
			conc[(ps.pond_id, ps.solute_idx)] = ps.unl_conc
		with self._open_with_meta('ponds.gw') as f:
			hdr = '{:>8}{:>14}{:>8}{:>8}{:>8}{:>14}{:>8}{:>12}{:>10}{:>10}{:>11}'.format(
				'pond_id', 'area', 'chan', 'canal', 'unl', 'bed_k', 'wsta', 'evap_co', 'start_yr', 'start_mo', 'start_day')
			hdr += ''.join('{:>14}'.format('unl_conc_' + str(i + 1)) for i in range(nsol))
			f.write(hdr + '\n')
			for p in ponds:
				f.write('{:>8}{:>14.5f}{:>8}{:>8}{:>8}{:>14.6f}{:>8}{:>12.5f}{:>10}{:>10}{:>11}'.format(
					p.id, p.area or 0.0, p.chan or 0, p.canal or 0, p.unl or 0,
					p.bed_k or 0.0, p.wsta or 0, p.evap_co or 0.0,
					p.start_yr or 0, p.start_mo or 0, p.start_day or 0))
				for i in range(nsol):
					v = conc.get((p.id, i + 1), 0.0)
					f.write('{:>14.5f}'.format(v if v is not None else 0.0))
				f.write('\n')

	def write_pond_cell(self):
		rows = list(gwflow.Gwflow_pond_cell.select().order_by(
			gwflow.Gwflow_pond_cell.pond_id, gwflow.Gwflow_pond_cell.cell_id))
		if not rows:
			self._remove_if_exists('pond_cell.gw')
			return
		with self._open_with_meta('pond_cell.gw') as f:
			f.write('{:>10}{:>10}{:>14}\n'.format('pond_id', 'cell_id', 'conn_area'))
			for r in rows:
				f.write('{:>10}{:>10}{:>14.5f}\n'.format(r.pond_id, r.cell_id, r.conn_area if r.conn_area is not None else 0.0))

	def write_pond_div(self):
		rows = list(gwflow.Gwflow_pond_div.select())
		if not rows:
			self._remove_if_exists('pond_div.gw')
			return
		pond_ids = [p.id for p in gwflow.Gwflow_pond.select().order_by(gwflow.Gwflow_pond.id)]
		div = {}
		for r in rows:
			div[(r.year, r.month, r.day, r.pond_id)] = r.div
		sim = simulation.Time_sim.get_or_none()
		start = datetime.date(sim.yrc_start, 1, 1)
		if sim.day_start and sim.day_start > 1:
			start = datetime.date(sim.yrc_start, 1, 1) + datetime.timedelta(days=sim.day_start - 1)
		end = datetime.date(sim.yrc_end, 12, 31)
		if sim.day_end and sim.day_end > 0:
			end = datetime.date(sim.yrc_end, 1, 1) + datetime.timedelta(days=sim.day_end - 1)
		with self._open_with_meta('pond_div.gw') as f:
			f.write('{:>8}{:>8}{:>8}'.format('year', 'month', 'day') + ''.join('{:>14}'.format('div_pond' + str(i + 1)) for i in range(len(pond_ids))) + '\n')
			d = start
			step = datetime.timedelta(days=1)
			while d <= end:
				f.write('{:>8}{:>8}{:>8}'.format(d.year, d.month, d.day))
				for pid in pond_ids:
					v = div.get((d.year, d.month, d.day, pid), 0.0)
					f.write('{:>14.5f}'.format(v if v is not None else 0.0))
				f.write('\n')
				d += step

	def write_phreato(self):
		rows = list(gwflow.Gwflow_phreato.select().order_by(gwflow.Gwflow_phreato.id))
		if not rows:
			self._remove_if_exists('phreato.gw')
			return
		with self._open_with_meta('phreato.gw') as f:
			f.write('{:>14}{:>14}\n'.format('depth', 'et_rate'))
			for r in rows:
				f.write('{:>14.5f}{:>14.5f}\n'.format(r.depth, r.et_rate))

	def write_phreato_cell(self):
		rows = list(gwflow.Gwflow_phreato_cell.select().order_by(gwflow.Gwflow_phreato_cell.cell_id))
		if not rows:
			self._remove_if_exists('phreato_cell.gw')
			return
		with self._open_with_meta('phreato_cell.gw') as f:
			f.write('{:>10}{:>14}\n'.format('cell_id', 'area'))
			for r in rows:
				f.write('{:>10}{:>14.5f}\n'.format(r.cell_id, r.area if r.area is not None else 0.0))

	def write_chan_depth(self):
		rows = list(gwflow.Gwflow_chan_depth.select().order_by(
			gwflow.Gwflow_chan_depth.year, gwflow.Gwflow_chan_depth.jday, gwflow.Gwflow_chan_depth.zone_idx))
		if not rows:
			self._remove_if_exists('chan_depth.gw')
			return
		dep_zones = [c.dep_zone for c in gwflow.Gwflow_chancell.select() if c.dep_zone]
		ndpzn = max(dep_zones + [r.zone_idx for r in rows] + [0])
		by_day = {}
		for r in rows:
			by_day.setdefault((r.year, r.jday), {})[r.zone_idx] = r.depth
		with self._open_with_meta('chan_depth.gw') as f:
			f.write('{:>8}{:>8}'.format('jday', 'yr') + ''.join('{:>14}'.format('depth_z' + str(j + 1)) for j in range(ndpzn)) + '\n')
			for (yr, jd) in sorted(by_day):
				d = by_day[(yr, jd)]
				f.write('{:>8}{:>8}'.format(jd, yr))
				for j in range(ndpzn):
					f.write('{:>14.5f}'.format(d.get(j + 1, 0.0)))
				f.write('\n')

	def write_solutes(self):
		solutes = list(gwflow.Gwflow_solute.select().order_by(gwflow.Gwflow_solute.id))
		if not solutes:
			return
		cfg = self.config
		with open(os.path.join(self.file_name, 'solute.gw'), 'w') as f:
			f.write(' Solute transport information ')
			self.write_meta_line(f, 'solute.gw')
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

	def write_cell_solute(self):
		solutes = list(gwflow.Gwflow_solute.select().order_by(gwflow.Gwflow_solute.id))
		if not solutes:
			self._remove_if_exists('cell_sol.gw')
			return
		sol_ids = [s.id for s in solutes]
		conc = {}
		for cs in gwflow.Gwflow_cell_solute.select():
			conc[(cs.cell_id_id, cs.solute_id_id)] = cs.init_conc
		cells = list(gwflow.Gwflow_cell.select().order_by(gwflow.Gwflow_cell.cell_id))
		with self._open_with_meta('cell_sol.gw') as f:
			f.write('{:>8}'.format('cell_id') + ''.join('{:>14}'.format('conc_' + str(i + 1)) for i in range(len(solutes))) + '\n')
			for c in cells:
				f.write('{:>8}'.format(c.cell_id))
				for sid in sol_ids:
					v = conc.get((c.cell_id, sid))
					f.write('{:>14.5f}'.format(v if v is not None else 0.0))
				f.write('\n')

	# The following are used by the UI for import/export

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

			gwflow_config = gwflow.Gwflow_config.get_or_none()
			for wet in reservoir.Wetland_wet.select().order_by(reservoir.Wetland_wet.id):
				values = [wet.name, wet_thick.get(wet.id, gwflow_config.wet_thickness)]
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

	#TODO: make this more graceful later; time crunch and just trying to retain some functionality
	def read_cell_solute_csv(self, file_name, solute_id):
		table = gwflow.Gwflow_cell_solute

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
			for val in csv_reader:
				if replace_commas:
					val = [item.replace(',', '.', 1) for item in val]

				row = {}
				row['cell_id'] = int(val[0])
				row['solute_id'] = solute_id
				row['init_conc'] = float(val[1]) if len(val) > 1 else 0.0
				rows.append(row)
			
		table.delete().where(table.solute_id == solute_id).execute()
		lib.bulk_insert(base.db, table, rows)
