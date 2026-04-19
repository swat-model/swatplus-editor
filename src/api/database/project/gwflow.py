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


class Gwflow_zone(base.BaseModel):
	zone_id = IntegerField(primary_key=True)
	aquifer_k = DoubleField(null=True)
	specific_yield = DoubleField(default=0.2)
	streambed_k = DoubleField(default=0.005)
	streambed_thickness = DoubleField(default=0.5)


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
	zone_id = ForeignKeyField(Gwflow_zone, on_delete='CASCADE', column_name='zone_id', lazy_load=False)
	extinction_depth = DoubleField(default=1.0)
	initial_head = DoubleField(null=True)
	recharge_delay = DoubleField(default=0)
	tile = IntegerField(default=0)


class Gwflow_cell_connection(base.BaseModel):
	cell_id = ForeignKeyField(Gwflow_cell, on_delete='CASCADE', column_name='cell_id', lazy_load=False)
	connected_cell_id = ForeignKeyField(Gwflow_cell, on_delete='CASCADE', column_name='connected_cell_id', lazy_load=False)

	class Meta:
		primary_key = CompositeKey('cell_id', 'connected_cell_id')


class Gwflow_hrucell(base.BaseModel):
	cell_id = ForeignKeyField(Gwflow_cell, on_delete='CASCADE', column_name='cell_id', lazy_load=False)
	hru_id = IntegerField()
	area_m2 = DoubleField()

	class Meta:
		primary_key = CompositeKey('cell_id', 'hru_id')


class Gwflow_lsucell(base.BaseModel):
	cell_id = ForeignKeyField(Gwflow_cell, on_delete='CASCADE', column_name='cell_id', lazy_load=False)
	lsu_id = IntegerField()
	area_m2 = DoubleField()

	class Meta:
		primary_key = CompositeKey('cell_id', 'lsu_id')


class Gwflow_chancell(base.BaseModel):
	cell_id = ForeignKeyField(Gwflow_cell, on_delete='CASCADE', column_name='cell_id', lazy_load=False)
	channel_id = IntegerField()
	bed_elevation = DoubleField()
	length_m = DoubleField()
	zone_id = ForeignKeyField(Gwflow_zone, on_delete='CASCADE', column_name='zone_id', lazy_load=False, default=1)


class Gwflow_fpcell(base.BaseModel):
	cell_id = ForeignKeyField(Gwflow_cell, on_delete='CASCADE', column_name='cell_id', lazy_load=False)
	channel_id = IntegerField()
	area_m2 = DoubleField()
	conductivity = DoubleField(default=0)

	class Meta:
		primary_key = CompositeKey('cell_id', 'channel_id')


class Gwflow_rescell(base.BaseModel):
	cell_id = ForeignKeyField(Gwflow_cell, on_delete='CASCADE', column_name='cell_id', lazy_load=False)
	reservoir_id = IntegerField()
	stage = DoubleField(default=0)

	class Meta:
		primary_key = CompositeKey('cell_id', 'reservoir_id')


class Gwflow_pump(base.BaseModel):
	cell_id = ForeignKeyField(Gwflow_cell, on_delete='CASCADE', column_name='cell_id', lazy_load=False)
	start_year = IntegerField()
	start_day = IntegerField()
	end_year = IntegerField()
	end_day = IntegerField()
	rate_m3day = DoubleField()


class Gwflow_obs(base.BaseModel):
	cell_id = ForeignKeyField(Gwflow_cell, on_delete='CASCADE', column_name='cell_id', lazy_load=False, primary_key=True)
	name = CharField(null=True)


class Gwflow_out_times(base.BaseModel):
	year = IntegerField()
	jday = IntegerField()

	class Meta:
		primary_key = CompositeKey('year', 'jday')


class Gwflow_solute(base.BaseModel):
	name = CharField()
	sorption_coef = DoubleField(default=1)
	rate_const = DoubleField(default=0)
	canal_irr = DoubleField(default=0)
	init_conc = DoubleField(default=0)


class Gwflow_cell_solute(base.BaseModel):
	cell_id = ForeignKeyField(Gwflow_cell, on_delete='CASCADE', column_name='cell_id', lazy_load=False)
	solute_id = ForeignKeyField(Gwflow_solute, on_delete='CASCADE', column_name='solute_id', lazy_load=False)
	init_conc = DoubleField()

	class Meta:
		primary_key = CompositeKey('cell_id', 'solute_id')


class Gwflow_wetland(base.BaseModel):
	wet_id = ForeignKeyField(Wetland_wet, on_delete='CASCADE', column_name='wet_id', lazy_load=False)
	thickness = DoubleField(null=True)

	class Meta:
		primary_key = False
