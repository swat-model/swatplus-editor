from peewee import *
from . import base
from database import lib as db_lib


class Cal_parms_cal(base.BaseModel):
	name = CharField()
	obj_typ = CharField()
	abs_min = DoubleField()
	abs_max = DoubleField()
	units = CharField(null=True)


class Calibration_cal(base.BaseModel):
	cal_parm = ForeignKeyField(Cal_parms_cal, on_delete='CASCADE', related_name='calibrations')
	chg_typ = CharField()  # absval, abschg, pctchg
	chg_val = DoubleField()
	soil_lyr1 = IntegerField(null=True)
	soil_lyr2 = IntegerField(null=True)
	yr1 = IntegerField(null=True)
	yr2 = IntegerField(null=True)
	day1 = IntegerField(null=True)
	day2 = IntegerField(null=True)


class Calibration_cal_cond(base.BaseModel):
	calibration_cal = ForeignKeyField(Calibration_cal, on_delete='CASCADE', related_name='conditions')
	cond_typ = CharField()  # hsg, texture, landuse, region
	cond_op = CharField() # = > <
	cond_val = DoubleField(null=True)
	cond_val_text = CharField(null=True)


class Calibration_cal_elem(base.BaseModel):
	calibration_cal = ForeignKeyField(Calibration_cal, on_delete='CASCADE', related_name='elements')
	obj_typ = CharField()
	obj_id = IntegerField()


class Codes_sft(base.BaseModel):
	#hyd_hru = BooleanField()
	#hyd_hrulte = BooleanField()
	landscape = BooleanField(default=False)
	hyd = CharField(default='n')
	plnt = BooleanField(default=False)
	sed = BooleanField(default=False)
	nut = BooleanField(default=False)
	ch_sed = BooleanField(default=False)
	ch_nut = BooleanField(default=False)
	res = BooleanField(default=False)


class Wb_parms_sft(base.BaseModel):
	name = CharField(unique=True)
	chg_typ = CharField()  # absval, abschg, pctchg
	neg = DoubleField()
	pos = DoubleField()
	lo = DoubleField()
	up = DoubleField()

	@classmethod
	def create_defaults(cls):
		items = [
			{ 'name': 'cn2', 'chg_typ': 'abschg', 'neg': -6, 'pos': 6, 'lo': 35, 'up': 95 },
			{ 'name': 'esco', 'chg_typ': 'abschg', 'neg': -1, 'pos': 1, 'lo': 0, 'up': 1 },
			{ 'name': 'latq_co', 'chg_typ': 'abschg', 'neg': -1, 'pos': 1, 'lo': 0, 'up': 1 },
			{ 'name': 'petco', 'chg_typ': 'abschg', 'neg': 0.54, 'pos': 1.85, 'lo': 0.7, 'up': 1.2 },
			{ 'name': 'slope', 'chg_typ': 'pctchg', 'neg': -25, 'pos': 25, 'lo': 0.0001, 'up': 0.9 },
			{ 'name': 'tconc', 'chg_typ': 'pctchg', 'neg': -30, 'pos': 30, 'lo': 5, 'up': 960 },
			{ 'name': 'etco', 'chg_typ': 'abschg', 'neg': -0.4, 'pos': 0.4, 'lo': 0.8, 'up': 1.2 },
			{ 'name': 'perco', 'chg_typ': 'abschg', 'neg': -0.7, 'pos': 0.7, 'lo': 0.001, 'up': 1 },
			{ 'name': 'revapc', 'chg_typ': 'abschg', 'neg': -0.4, 'pos': 0.4, 'lo': 0, 'up': 0.4 },
			{ 'name': 'cn3_swf', 'chg_typ': 'abschg', 'neg': -1.2, 'pos': 1.2, 'lo': 0, 'up': 1 },
		]

		db_lib.bulk_insert(base.db, cls, items)


class Water_balance_sft(base.BaseModel):
	name = CharField(unique=True)


class Water_balance_sft_item(base.BaseModel):
	water_balance_sft = ForeignKeyField(Water_balance_sft, on_delete='CASCADE', related_name='items')
	name = CharField()
	surq_rto = DoubleField(default=0)	#a
	latq_rto = DoubleField(default=0)	#a
	perc_rto = DoubleField(default=0)	#a
	et_rto = DoubleField(default=0)		#a
	tileq_rto = DoubleField(default=0)	#a
	pet = DoubleField(default=0)		#a
	sed = DoubleField(default=0)		#not used
	wyr = DoubleField(default=0)		#b
	bfr = DoubleField(default=0)		#b
	solp = DoubleField(default=0)		#not used


class Ch_sed_budget_sft(base.BaseModel):
	name = CharField(unique=True)

class Ch_sed_budget_sft_item(base.BaseModel):
	ch_sed_budget_sft = ForeignKeyField(Ch_sed_budget_sft, on_delete='CASCADE', related_name='items')
	name = CharField()
	cha_wide = DoubleField()
	cha_dc_accr = DoubleField()
	head_cut = DoubleField()
	fp_accr = DoubleField()


class Ch_sed_parms_sft(base.BaseModel):
	name = CharField(unique=True)
	chg_typ = CharField()  # absval, abschg, pctchg
	neg = DoubleField()
	pos = DoubleField()
	lo = DoubleField()
	up = DoubleField()


class Plant_parms_sft(base.BaseModel):
	name = CharField(unique=True)


class Plant_parms_sft_item(base.BaseModel):
	plant_parms_sft = ForeignKeyField(Plant_parms_sft, on_delete='CASCADE', related_name='items')
	var = CharField()
	name = CharField()
	init = DoubleField(default=0)
	chg_typ = CharField()  # absval, abschg, pctchg
	neg = DoubleField(default=0)
	pos = DoubleField(default=0)
	lo = DoubleField(default=0)
	up = DoubleField(default=0)


class Plant_gro_sft(base.BaseModel):
	name = CharField(unique=True)


class Plant_gro_sft_item(base.BaseModel):
	plant_gro_sft = ForeignKeyField(Plant_gro_sft, on_delete='CASCADE', related_name='items')
	name = CharField()
	yld = DoubleField(default=0)
	npp = DoubleField(default=0)
	lai_mx = DoubleField(default=0)
	wstress = DoubleField(default=0)
	astress = DoubleField(default=0)
	tstress = DoubleField(default=0)
