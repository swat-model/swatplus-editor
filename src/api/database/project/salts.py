from peewee import *
from .base import BaseModel
from .climate import Atmo_cli_sta
from .hru_parm_db import Fertilizer_frt, Urban_urb, Plants_plt


class Salt_recall_rec(BaseModel):
	name = CharField(unique=True)
	rec_typ = IntegerField()  # 1-day, 2-mon, 3-yr, 4-const


class Salt_recall_dat(BaseModel):
	recall_rec = ForeignKeyField(Salt_recall_rec, on_delete='CASCADE', related_name='data')
	jday = IntegerField()
	mo = IntegerField()
	day_mo = IntegerField()
	yr = IntegerField()
	ob_typ = CharField(null=True)
	ob_name = CharField(null=True)
	so4 = DoubleField()
	ca = DoubleField()
	mg = DoubleField()
	na = DoubleField()
	k = DoubleField()
	cl = DoubleField()
	co3 = DoubleField()
	hco3 = DoubleField()


class Salt_atmo_cli(BaseModel):
	sta = ForeignKeyField(Atmo_cli_sta, on_delete='CASCADE', related_name='salt_values')
	timestep = IntegerField()
	so4_wet = DoubleField()
	ca_wet = DoubleField()
	mg_wet = DoubleField()
	na_wet = DoubleField()
	k_wet = DoubleField()
	cl_wet = DoubleField()
	co3_wet = DoubleField()
	hco3_wet = DoubleField()
	so4_dry = DoubleField()
	ca_dry = DoubleField()
	mg_dry = DoubleField()
	na_dry = DoubleField()
	k_dry = DoubleField()
	cl_dry = DoubleField()
	co3_dry = DoubleField()
	hco3_dry = DoubleField()


class Salt_road(BaseModel):
	sta = ForeignKeyField(Atmo_cli_sta, on_delete='CASCADE', related_name='salt_road_values')
	timestep = IntegerField()
	so4 = DoubleField()
	ca = DoubleField()
	mg = DoubleField()
	na = DoubleField()
	k = DoubleField()
	cl = DoubleField()
	co3 = DoubleField()
	hco3 = DoubleField()


class Salt_fertilizer_frt(BaseModel):
	name = ForeignKeyField(Fertilizer_frt, on_delete='CASCADE', related_name='salts')
	so4 = DoubleField()
	ca = DoubleField()
	mg = DoubleField()
	na = DoubleField()
	k = DoubleField()
	cl = DoubleField()
	co3 = DoubleField()
	hco3 = DoubleField()


class Salt_urban(BaseModel):
	name = ForeignKeyField(Urban_urb, on_delete='CASCADE', related_name='salts')
	so4 = DoubleField()
	ca = DoubleField()
	mg = DoubleField()
	na = DoubleField()
	k = DoubleField()
	cl = DoubleField()
	co3 = DoubleField()
	hco3 = DoubleField()


class Salt_plants_flags(BaseModel):
	enabled = IntegerField()
	soil = IntegerField()
	stress = IntegerField()


class Salt_plants(BaseModel):
	name = ForeignKeyField(Plants_plt, on_delete='CASCADE', related_name='salts')
	a = DoubleField()
	b = DoubleField()


class Salt_uptake(BaseModel):
	name = ForeignKeyField(Plants_plt, on_delete='CASCADE', related_name='salt_uptakes')
	so4 = DoubleField()
	ca = DoubleField()
	mg = DoubleField()
	na = DoubleField()
	k = DoubleField()
	cl = DoubleField()
	co3 = DoubleField()
	hco3 = DoubleField()


# Intialization tables
	
class Salt_aqu_ini(BaseModel):
	name = CharField(unique=True)
	so4 = DoubleField()
	ca = DoubleField()
	mg = DoubleField()
	na = DoubleField()
	k = DoubleField()
	cl = DoubleField()
	co3 = DoubleField()
	hco3 = DoubleField()
	caco3 = DoubleField()
	mgco3 = DoubleField()
	caso4 = DoubleField()
	mgso4 = DoubleField()
	nacl = DoubleField()


class Salt_channel_ini(BaseModel):
	name = CharField(unique=True)
	so4 = DoubleField()
	ca = DoubleField()
	mg = DoubleField()
	na = DoubleField()
	k = DoubleField()
	cl = DoubleField()
	co3 = DoubleField()
	hco3 = DoubleField()


class Salt_res_ini(BaseModel):
	name = CharField(unique=True)
	so4 = DoubleField()
	ca = DoubleField()
	mg = DoubleField()
	na = DoubleField()
	k = DoubleField()
	cl = DoubleField()
	co3 = DoubleField()
	hco3 = DoubleField()


class Salt_hru_ini_cs(BaseModel):
	name = CharField(unique=True)
	soil_so4 = DoubleField()
	soil_ca = DoubleField()
	soil_mg = DoubleField()
	soil_na = DoubleField()
	soil_k = DoubleField()
	soil_cl = DoubleField()
	soil_co3 = DoubleField()
	soil_hco3 = DoubleField()
	soil_caco3 = DoubleField()
	soil_mgco3 = DoubleField()
	soil_caso4 = DoubleField()
	soil_mgso4 = DoubleField()
	soil_nacl = DoubleField()
	plant_so4 = DoubleField()
	plant_ca = DoubleField()
	plant_mg = DoubleField()
	plant_na = DoubleField()
	plant_k = DoubleField()
	plant_cl = DoubleField()
	plant_co3 = DoubleField()
	plant_hco3 = DoubleField()
	plant_caco3 = DoubleField()
	plant_mgco3 = DoubleField()
	plant_caso4 = DoubleField()
	plant_mgso4 = DoubleField()
	plant_nacl = DoubleField()


class Salt_irrigation(BaseModel):
	name = ForeignKeyField(Salt_hru_ini_cs, on_delete='CASCADE', related_name='salts')
	so4 = DoubleField()
	ca = DoubleField()
	mg = DoubleField()
	na = DoubleField()
	k = DoubleField()
	cl = DoubleField()
	co3 = DoubleField()
	hco3 = DoubleField()


class Salt_module(BaseModel):
	enabled = BooleanField(default=False)
	recall = BooleanField(default=False)
	atmo = BooleanField(default=False)
	road = BooleanField(default=False)
	fert = BooleanField(default=False)
	irrigation = BooleanField(default=False)
	urban = BooleanField(default=False)
	atmo_timestep = CharField(null=True)
	road_timestep = CharField(null=True)
