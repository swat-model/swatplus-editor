from peewee import *
from . import base, gis
from .reservoir import Wetland_wet


class Gwflow_config(base.BaseModel):
	grid_type = CharField(default='structured')
	cell_size = DoubleField(default=200)
	num_rows = IntegerField(default=0)
	num_cols = IntegerField(default=0)
	num_cells = IntegerField(default=0)
	boundary_condition = IntegerField(default=2)
	recharge_type = IntegerField(default=2)
	gw_soil_transfer = IntegerField(default=1)
	saturation_excess = IntegerField(default=1)
	external_pumping = IntegerField(default=0)
	tile_drainage = IntegerField(default=0)
	reservoir_exchange = IntegerField(default=1)
	wetland_exchange = IntegerField(default=1)
	floodplain_exchange = IntegerField(default=1)
	canal_seepage = IntegerField(default=0)
	solute_transport = IntegerField(default=0)
	heat_transport = IntegerField(default=0)
	timestep_days = DoubleField(default=1.0)
	daily_output = IntegerField(default=1)
	monthly_output = IntegerField(default=0)
	annual_output = IntegerField(default=1)
	aa_output = IntegerField(default=1)
	river_depth = DoubleField(default=5.0)
	tile_depth = DoubleField(default=1.22)
	tile_area = DoubleField(default=50)
	tile_k = DoubleField(default=5.0)
	resbed_thickness = DoubleField(default=2.0)
	resbed_k = DoubleField(default=9.99e-6)
	wet_thickness = DoubleField(default=0.25)
	transport_steps = IntegerField(default=1)
	disp_coef = DoubleField(default=5.0)
	detail_row = IntegerField(default=0)
	detail_col = IntegerField(default=0)

	class Meta:
		table_name = 'codes_gw'


class Gwflow_zone(base.BaseModel):
	zone_id = IntegerField(primary_key=True)
	aquifer_k = DoubleField(null=True)
	specific_yield = DoubleField(default=0.2)
	streambed_k = DoubleField(default=0.005)
	streambed_thickness = DoubleField(default=0.5)
	thermal_k = DoubleField(column_name='thermal_K', default=0)

	class Meta:
		table_name = 'zones_gw'


class Gwflow_cell(base.BaseModel):
	cell_id = IntegerField(primary_key=True)
	status = IntegerField(default=1)
	row = IntegerField(null=True)
	col = IntegerField(null=True)
	x_centroid = DoubleField()
	y_centroid = DoubleField()
	area = DoubleField()
	elevation = DoubleField(default=0)
	aquifer_thickness = DoubleField(default=50)
	zone_id = ForeignKeyField(Gwflow_zone, on_delete='CASCADE', column_name='zone', lazy_load=False)
	extinction_depth = DoubleField(default=1.0)
	initial_head = DoubleField(null=True)
	tile = IntegerField(default=0)
	streambed_k = DoubleField(null=True)
	streambed_thickness = DoubleField(null=True)
	bc_type = IntegerField(null=True)
	tile_depth = DoubleField(null=True)
	tile_area = DoubleField(null=True)
	tile_k = DoubleField(null=True)
	init_temp = DoubleField(null=True)
	gis_id = IntegerField(null=True)

	class Meta:
		table_name = 'cells_gw'


class Gwflow_cell_connection(base.BaseModel):
	cell_id = ForeignKeyField(Gwflow_cell, on_delete='CASCADE', column_name='cell_id', lazy_load=False)
	connected_cell_id = ForeignKeyField(Gwflow_cell, on_delete='CASCADE', column_name='connected_cell_id', lazy_load=False)

	class Meta:
		primary_key = CompositeKey('cell_id', 'connected_cell_id')
		table_name = 'cellcon_gw'


class Gwflow_hrucell(base.BaseModel):
	cell_id = ForeignKeyField(Gwflow_cell, on_delete='CASCADE', column_name='cell_id', lazy_load=False)
	hru_id = IntegerField()
	area_m2 = DoubleField()

	class Meta:
		primary_key = CompositeKey('cell_id', 'hru_id')
		table_name = 'hrucell_gw'


class Gwflow_lsucell(base.BaseModel):
	cell_id = ForeignKeyField(Gwflow_cell, on_delete='CASCADE', column_name='cell_id', lazy_load=False)
	lsu_id = IntegerField()
	area_m2 = DoubleField()

	class Meta:
		primary_key = CompositeKey('cell_id', 'lsu_id')
		table_name = 'lsucell_gw'


class Gwflow_chancell(base.BaseModel):
	cell_id = ForeignKeyField(Gwflow_cell, on_delete='CASCADE', column_name='cell_id', lazy_load=False)
	channel_id = IntegerField()
	bed_elevation = DoubleField()
	length_m = DoubleField()
	zone_id = ForeignKeyField(Gwflow_zone, on_delete='CASCADE', column_name='zone_id', lazy_load=False, default=1)
	obs = IntegerField(default=0)
	dep_zone = IntegerField(null=True)

	class Meta:
		table_name = 'chancell_gw'


class Gwflow_fpcell(base.BaseModel):
	cell_id = ForeignKeyField(Gwflow_cell, on_delete='CASCADE', column_name='cell_id', lazy_load=False)
	channel_id = IntegerField()
	area_m2 = DoubleField()
	conductivity = DoubleField(default=0)

	class Meta:
		primary_key = CompositeKey('cell_id', 'channel_id')
		table_name = 'floodplain_gw'


class Gwflow_rescell(base.BaseModel):
	cell_id = ForeignKeyField(Gwflow_cell, on_delete='CASCADE', column_name='cell_id', lazy_load=False)
	reservoir_id = IntegerField()
	stage = DoubleField(default=0)

	class Meta:
		primary_key = CompositeKey('cell_id', 'reservoir_id')
		table_name = 'rescell_gw'


class Gwflow_pump(base.BaseModel):
	cell_id = ForeignKeyField(Gwflow_cell, on_delete='CASCADE', column_name='cell_id', lazy_load=False)
	start_year = IntegerField()
	start_day = IntegerField()
	end_year = IntegerField()
	end_day = IntegerField()
	rate_m3day = DoubleField()

	class Meta:
		table_name = 'pumpex_gw'


class Gwflow_hru_pump_obs(base.BaseModel):
	hru_id = IntegerField(primary_key=True)

	class Meta:
		table_name = 'hru_pump_gw'


class Gwflow_tvhead(base.BaseModel):
	cell_id = IntegerField()
	year = IntegerField()
	head = DoubleField()

	class Meta:
		primary_key = CompositeKey('cell_id', 'year')
		table_name = 'tvheads_gw'


class Gwflow_obs(base.BaseModel):
	cell_id = ForeignKeyField(Gwflow_cell, on_delete='CASCADE', column_name='cell_id', lazy_load=False, primary_key=True)
	name = CharField(null=True)

	class Meta:
		table_name = 'obs_gw'


class Gwflow_out_times(base.BaseModel):
	year = IntegerField()
	jday = IntegerField()

	class Meta:
		primary_key = CompositeKey('year', 'jday')
		table_name = 'out_times_gw'


class Gwflow_solute(base.BaseModel):
	name = CharField()
	sorption_coef = DoubleField(default=1)
	rate_const = DoubleField(default=0)
	canal_irr = DoubleField(default=0)
	init_conc = DoubleField(default=0)

	class Meta:
		table_name = 'solute_gw'


class Gwflow_cell_solute(base.BaseModel):
	cell_id = ForeignKeyField(Gwflow_cell, on_delete='CASCADE', column_name='cell_id', lazy_load=False)
	solute_id = ForeignKeyField(Gwflow_solute, on_delete='CASCADE', column_name='solute_id', lazy_load=False)
	init_conc = DoubleField()

	class Meta:
		primary_key = CompositeKey('cell_id', 'solute_id')
		table_name = 'cell_sol_gw'


class Gwflow_wetland(base.BaseModel):
	wet_id = ForeignKeyField(Wetland_wet, on_delete='CASCADE', column_name='wet_id', lazy_load=False)
	thickness = DoubleField(null=True)

	class Meta:
		primary_key = False
		table_name = 'wetland_gw'


class Gwflow_sw_group(base.BaseModel):
	group_id = IntegerField()
	cell_id = IntegerField()

	class Meta:
		primary_key = CompositeKey('group_id', 'cell_id')
		table_name = 'sw_group_gw'


class Gwflow_pond(base.BaseModel):
	area = DoubleField(null=True)
	chan = IntegerField(null=True)
	canal = IntegerField(null=True)
	unl = IntegerField(null=True)
	bed_k = DoubleField(null=True)
	wsta = IntegerField(null=True)
	evap_co = DoubleField(null=True)
	start_yr = IntegerField(null=True)
	start_mo = IntegerField(null=True)
	start_day = IntegerField(null=True)

	class Meta:
		table_name = 'ponds_gw'


class Gwflow_pond_solute(base.BaseModel):
	pond_id = IntegerField()
	solute_idx = IntegerField()
	unl_conc = DoubleField(default=0)

	class Meta:
		primary_key = CompositeKey('pond_id', 'solute_idx')
		table_name = 'pond_solute_gw'


class Gwflow_pond_cell(base.BaseModel):
	pond_id = IntegerField()
	cell_id = IntegerField()
	conn_area = DoubleField(null=True)

	class Meta:
		primary_key = CompositeKey('pond_id', 'cell_id')
		table_name = 'pond_cell_gw'


class Gwflow_phreato(base.BaseModel):
	depth = DoubleField()
	et_rate = DoubleField()

	class Meta:
		table_name = 'phreato_gw'


class Gwflow_phreato_cell(base.BaseModel):
	cell_id = IntegerField(primary_key=True)
	area = DoubleField(null=True)

	class Meta:
		table_name = 'phreato_cell_gw'


class Gwflow_chan_depth(base.BaseModel):
	year = IntegerField()
	jday = IntegerField()
	zone_idx = IntegerField()
	depth = DoubleField()

	class Meta:
		primary_key = CompositeKey('year', 'jday', 'zone_idx')
		table_name = 'chan_depth_gw'


class Gwflow_pond_div(base.BaseModel):
	pond_id = IntegerField()
	year = IntegerField()
	month = IntegerField()
	day = IntegerField()
	div = DoubleField(default=0)

	class Meta:
		primary_key = CompositeKey('pond_id', 'year', 'month', 'day')
		table_name = 'pond_div_gw'
