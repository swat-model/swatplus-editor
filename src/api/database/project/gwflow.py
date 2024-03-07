from peewee import *
from . import base, gis


class Gwflow_base(base.BaseModel):
	cell_size = IntegerField()
	row_count = IntegerField()
	col_count = IntegerField()
	boundary_conditions = IntegerField()
	recharge = IntegerField()
	soil_transfer = IntegerField()
	saturation_excess = IntegerField()
	external_pumping = IntegerField()
	tile_drainage = IntegerField()
	reservoir_exchange = IntegerField()
	wetland_exchange = IntegerField()
	floodplain_exchange = IntegerField()
	canal_seepage = IntegerField()
	solute_transport = IntegerField()
	recharge_delay = IntegerField()
	et_extinction_depth = DoubleField()
	water_table_depth = DoubleField()
	river_depth = DoubleField()
	tile_depth = DoubleField()
	tile_area = DoubleField()
	tile_k = DoubleField()
	tile_groups = IntegerField()
	resbed_thickness = DoubleField()
	resbed_k = DoubleField()
	wet_thickness = DoubleField()
	daily_output = IntegerField()
	annual_output = IntegerField()
	aa_output = IntegerField()
	daily_output_row = IntegerField()
	daily_output_col = IntegerField()
	
	class Meta:
		primary_key = False


class Gwflow_zone(base.BaseModel):
	zone_id = IntegerField(primary_key=True)
	aquifer_k = DoubleField()
	specific_yield = DoubleField()
	streambed_k = DoubleField()
	streambed_thickness = DoubleField()


class Gwflow_grid(base.BaseModel):
	cell_id = IntegerField(primary_key=True)
	status = IntegerField()
	zone = ForeignKeyField(Gwflow_zone, on_delete='CASCADE', column_name = 'zone', lazy_load=False)
	elevation = DoubleField()
	aquifer_thickness = DoubleField()
	initial_head = DoubleField()
	tile = IntegerField()


class Gwflow_out_days(base.BaseModel):
	year = IntegerField()
	jday = IntegerField()
	
	class Meta:
		primary_key = False


# do not make this a foreign key since may accidentally reference inactive cell
class Gwflow_obs_locs(base.BaseModel):
	cell_id = IntegerField()
	
	class Meta:
		primary_key = False


class Gwflow_solutes(base.BaseModel):
	no3 = IntegerField()
	p = IntegerField()
	so4 = IntegerField(default=0)
	ca = IntegerField(default=0)
	mg = IntegerField(default=0)
	na = IntegerField(default=0)
	k = IntegerField(default=0)
	cl = IntegerField(default=0)
	co3 = IntegerField(default=0)
	hco3 = IntegerField(default=0)
	seo4 = IntegerField(default=0)
	seo3 = IntegerField(default=0)
	boron = IntegerField(default=0)
	pest = IntegerField(default=0)
	denit_constant = DoubleField()
	disp_coef = DoubleField()
	nit_sorp = DoubleField()
	pho_sorp = DoubleField()
	transport_steps = DoubleField()
	init_no3 = DoubleField()
	init_p = DoubleField()
	init_so4 = DoubleField(default=0)
	init_ca = DoubleField(default=0)
	init_mg = DoubleField(default=0)
	init_na = DoubleField(default=0)
	init_k = DoubleField(default=0)
	init_cl = DoubleField(default=0)
	init_co3 = DoubleField(default=0)
	init_hco3 = DoubleField(default=0)
	init_seo4 = DoubleField(default=0)
	init_seo3 = DoubleField(default=0)
	init_boron = DoubleField(default=0)
	init_pest = DoubleField(default=0)
	
	class Meta:
		primary_key = False


class Gwflow_hrucell(base.BaseModel):
	cell_id = ForeignKeyField(Gwflow_grid, on_delete='CASCADE', column_name='cell_id', lazy_load=False)
	hru = ForeignKeyField(gis.Gis_hrus, on_delete='CASCADE', column_name='hru', lazy_load=False)
	area_m2 = DoubleField()
	
	class Meta:
		primary_key = False


class Gwflow_fpcell(base.BaseModel):
	cell_id = ForeignKeyField(Gwflow_grid, on_delete='CASCADE', column_name='cell_id', lazy_load=False)
	channel = ForeignKeyField(gis.Gis_channels, on_delete='CASCADE', column_name='channel', lazy_load=False)
	area_m2 = DoubleField()
	
	class Meta:
		primary_key = False


class Gwflow_rivcell(base.BaseModel):
	cell_id = ForeignKeyField(Gwflow_grid, on_delete='CASCADE', column_name='cell_id', lazy_load=False)
	channel = ForeignKeyField(gis.Gis_channels, on_delete='CASCADE', column_name='channel', lazy_load=False)
	length_m = DoubleField()
	
	class Meta:
		primary_key = False


class Gwflow_lsucell(base.BaseModel):
	cell_id = ForeignKeyField(Gwflow_grid, on_delete='CASCADE', column_name='cell_id', lazy_load=False)
	lsu = ForeignKeyField(gis.Gis_lsus, on_delete='CASCADE', column_name='lsu', lazy_load=False)
	area_m2 = DoubleField()
	
	class Meta:
		primary_key = False


class Gwflow_rescell(base.BaseModel):
	cell_id = ForeignKeyField(Gwflow_grid, on_delete='CASCADE', column_name='cell_id', lazy_load=False)
	res = ForeignKeyField(gis.Gis_water, on_delete='CASCADE', column_name='res', lazy_load=False)
	res_stage = DoubleField()
	
	class Meta:
		primary_key = False
