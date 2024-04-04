from peewee import *
from . import base, gis
from .reservoir import Wetland_wet


class Gwflow_base(base.BaseModel):
	cell_size = IntegerField(null=True)
	row_count = IntegerField(null=True)
	col_count = IntegerField(null=True)
	boundary_conditions = IntegerField(null=True)
	recharge = IntegerField(null=True)
	soil_transfer = IntegerField(null=True)
	saturation_excess = IntegerField(null=True)
	external_pumping = IntegerField(null=True)
	tile_drainage = IntegerField(null=True)
	reservoir_exchange = IntegerField(null=True)
	wetland_exchange = IntegerField(null=True)
	floodplain_exchange = IntegerField(null=True)
	canal_seepage = IntegerField(null=True)
	solute_transport = IntegerField(null=True)
	transport_steps = DoubleField(null=True)
	disp_coef = DoubleField(null=True)
	recharge_delay = IntegerField(null=True)
	et_extinction_depth = DoubleField(null=True)
	water_table_depth = DoubleField(null=True)
	river_depth = DoubleField(null=True)
	tile_depth = DoubleField(null=True)
	tile_area = DoubleField(null=True)
	tile_k = DoubleField(null=True)
	tile_groups = IntegerField(null=True)
	resbed_thickness = DoubleField(null=True)
	resbed_k = DoubleField(null=True)
	wet_thickness = DoubleField(null=True)
	daily_output = IntegerField(null=True)
	annual_output = IntegerField(null=True)
	aa_output = IntegerField(null=True)
	daily_output_row = IntegerField(null=True)
	daily_output_col = IntegerField(null=True)
	timestep_balance = DoubleField(null=True)
	
	class Meta:
		primary_key = False


class Gwflow_zone(base.BaseModel):
	zone_id = IntegerField(primary_key=True)
	aquifer_k = DoubleField(null=True)
	specific_yield = DoubleField(null=True)
	streambed_k = DoubleField(null=True)
	streambed_thickness = DoubleField(null=True)


class Gwflow_grid(base.BaseModel):
	cell_id = IntegerField(primary_key=True)
	status = IntegerField(null=True)
	zone = ForeignKeyField(Gwflow_zone, on_delete='CASCADE', column_name = 'zone', lazy_load=False)
	elevation = DoubleField(null=True)
	aquifer_thickness = DoubleField(null=True)
	extinction_depth = DoubleField(null=True)
	initial_head = DoubleField(null=True)
	tile = IntegerField(null=True)


class Gwflow_out_days(base.BaseModel):
	year = IntegerField(null=True)
	jday = IntegerField(null=True)
	
	class Meta:
		primary_key = False


# do not make this a foreign key since may accidentally reference inactive cell
class Gwflow_obs_locs(base.BaseModel):
	cell_id = IntegerField(null=True)
	
	class Meta:
		primary_key = False


class Gwflow_solutes(base.BaseModel):
	solute_name = CharField(null=True)
	sorption = DoubleField(null=True)
	rate_const = DoubleField(null=True)
	canal_irr = DoubleField(null=True)
	init_data = CharField(null=True)
	init_conc = DoubleField(null=True)
	
	class Meta:
		primary_key = False


class Gwflow_init_conc(base.BaseModel):
	cell_id = ForeignKeyField(Gwflow_grid, on_delete='CASCADE', column_name='cell_id', lazy_load=False)
	init_no3 = DoubleField(default=0)
	init_p   = DoubleField(default=0)
	init_so4 = DoubleField(default=0)
	init_ca  = DoubleField(default=0)
	init_mg  = DoubleField(default=0)
	init_na  = DoubleField(default=0)
	init_k   = DoubleField(default=0)
	init_cl  = DoubleField(default=0)
	init_co3 = DoubleField(default=0)
	init_hco3 = DoubleField(default=0)
	
	class Meta:
		primary_key = False


class Gwflow_hrucell(base.BaseModel):
	cell_id = ForeignKeyField(Gwflow_grid, on_delete='CASCADE', column_name='cell_id', lazy_load=False)
	hru = ForeignKeyField(gis.Gis_hrus, on_delete='CASCADE', column_name='hru', lazy_load=False)
	area_m2 = DoubleField(null=True)
	
	class Meta:
		primary_key = False


class Gwflow_fpcell(base.BaseModel):
	cell_id = ForeignKeyField(Gwflow_grid, on_delete='CASCADE', column_name='cell_id', lazy_load=False)
	channel = ForeignKeyField(gis.Gis_channels, on_delete='CASCADE', column_name='channel', lazy_load=False)
	area_m2 = DoubleField(null=True)
	conductivity = DoubleField(null=True)
	
	class Meta:
		primary_key = False


class Gwflow_rivcell(base.BaseModel):
	cell_id = ForeignKeyField(Gwflow_grid, on_delete='CASCADE', column_name='cell_id', lazy_load=False)
	channel = ForeignKeyField(gis.Gis_channels, on_delete='CASCADE', column_name='channel', lazy_load=False)
	length_m = DoubleField(null=True)
	
	class Meta:
		primary_key = False


class Gwflow_lsucell(base.BaseModel):
	cell_id = ForeignKeyField(Gwflow_grid, on_delete='CASCADE', column_name='cell_id', lazy_load=False)
	lsu = ForeignKeyField(gis.Gis_lsus, on_delete='CASCADE', column_name='lsu', lazy_load=False)
	area_m2 = DoubleField(null=True)
	
	class Meta:
		primary_key = False


class Gwflow_rescell(base.BaseModel):
	cell_id = ForeignKeyField(Gwflow_grid, on_delete='CASCADE', column_name='cell_id', lazy_load=False)
	res = ForeignKeyField(gis.Gis_water, on_delete='CASCADE', column_name='res', lazy_load=False)
	res_stage = DoubleField(null=True)
	
	class Meta:
		primary_key = False


class Gwflow_wetland(base.BaseModel):
	wet_id = ForeignKeyField(Wetland_wet, on_delete='CASCADE', column_name='wet_id', lazy_load=False)
	thickness = DoubleField(null=True)
	
	class Meta:
		primary_key = False