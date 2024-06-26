from peewee import *
from . import base, init
from .salts import Salt_channel_ini


class Initial_cha(base.BaseModel):
	name = CharField(unique=True)
	org_min = ForeignKeyField(init.Om_water_ini, on_delete='SET NULL', null=True)
	pest = ForeignKeyField(init.Pest_water_ini, on_delete='SET NULL', null=True)
	path = ForeignKeyField(init.Path_water_ini, on_delete='SET NULL', null=True)
	hmet = ForeignKeyField(init.Hmet_water_ini, on_delete='SET NULL', null=True)
	salt = ForeignKeyField(init.Salt_water_ini, on_delete='SET NULL', null=True)
	salt_cs = ForeignKeyField(Salt_channel_ini, on_delete='SET NULL', null=True)
	description = TextField(null=True)


class Hydrology_cha(base.BaseModel):
	name = CharField(unique=True)
	wd = DoubleField()
	dp = DoubleField()
	slp = DoubleField()
	len = DoubleField()
	mann = DoubleField()
	k = DoubleField()
	wdr = DoubleField()
	alpha_bnk = DoubleField()
	side_slp = DoubleField()
	description = TextField(null=True)


class Sediment_cha(base.BaseModel):
	name = CharField(unique=True)
	sed_eqn = IntegerField()
	erod_fact = DoubleField()
	cov_fact = DoubleField()
	bd_bnk = DoubleField()
	bd_bed = DoubleField()
	kd_bnk = DoubleField()
	kd_bed = DoubleField()
	d50_bnk = DoubleField()
	d50_bed = DoubleField()
	css_bnk = DoubleField()
	css_bed = DoubleField()
	erod1 = DoubleField()
	erod2 = DoubleField()
	erod3 = DoubleField()
	erod4 = DoubleField()
	erod5 = DoubleField()
	erod6 = DoubleField()
	erod7 = DoubleField()
	erod8 = DoubleField()
	erod9 = DoubleField()
	erod10 = DoubleField()
	erod11 = DoubleField()
	erod12 = DoubleField()
	description = TextField(null=True)


class Nutrients_cha(base.BaseModel):
	name = CharField(unique=True)
	plt_n = DoubleField()
	ptl_p = DoubleField()
	alg_stl = DoubleField()
	ben_disp = DoubleField()
	ben_nh3n = DoubleField()
	ptln_stl = DoubleField()
	ptlp_stl = DoubleField()
	cst_stl = DoubleField()
	ben_cst = DoubleField()
	cbn_bod_co = DoubleField()
	air_rt = DoubleField()
	cbn_bod_stl = DoubleField()
	ben_bod = DoubleField()
	bact_die = DoubleField()
	cst_decay = DoubleField()
	nh3n_no2n = DoubleField()
	no2n_no3n = DoubleField()
	ptln_nh3n = DoubleField()
	ptlp_solp = DoubleField()
	q2e_lt = IntegerField()
	q2e_alg = IntegerField()
	chla_alg = DoubleField()
	alg_n = DoubleField()
	alg_p = DoubleField()
	alg_o2_prod = DoubleField()
	alg_o2_resp = DoubleField()
	o2_nh3n = DoubleField()
	o2_no2n = DoubleField()
	alg_grow = DoubleField()
	alg_resp = DoubleField()
	slr_act = DoubleField()
	lt_co = DoubleField()
	const_n = DoubleField()
	const_p = DoubleField()
	lt_nonalg = DoubleField()
	alg_shd_l = DoubleField()
	alg_shd_nl = DoubleField()
	nh3_pref = DoubleField()
	description = TextField(null=True)


class Channel_cha(base.BaseModel):
	name = CharField(unique=True)
	init = ForeignKeyField(Initial_cha, null=True, on_delete='SET NULL')
	hyd = ForeignKeyField(Hydrology_cha, null=True, on_delete='SET NULL')
	sed = ForeignKeyField(Sediment_cha, null=True, on_delete='SET NULL')
	nut = ForeignKeyField(Nutrients_cha, null=True, on_delete='SET NULL')
	description = TextField(null=True)


class Hyd_sed_lte_cha(base.BaseModel):
	name = CharField(unique=True)
	order = CharField(null=True)
	wd = DoubleField()
	dp = DoubleField()
	slp = DoubleField()
	len = DoubleField()
	mann = DoubleField()
	k = DoubleField()
	erod_fact = DoubleField()
	cov_fact = DoubleField()
	#wd_rto = DoubleField()
	sinu = DoubleField()
	eq_slp = DoubleField()
	d50 = DoubleField()
	clay = DoubleField()
	carbon = DoubleField()
	dry_bd = DoubleField()
	side_slp = DoubleField()
	#bed_load = DoubleField()
	bankfull_flo = DoubleField()
	fps = DoubleField()
	fpn = DoubleField()
	n_conc = DoubleField()
	p_conc = DoubleField()
	p_bio = DoubleField()
	description = TextField(null=True)


class Channel_lte_cha(base.BaseModel):
	name = CharField(unique=True)
	init = ForeignKeyField(Initial_cha, null=True, on_delete='SET NULL')
	hyd = ForeignKeyField(Hyd_sed_lte_cha, null=True, on_delete='SET NULL')
	sed = ForeignKeyField(Sediment_cha, null=True, on_delete='SET NULL')
	nut = ForeignKeyField(Nutrients_cha, null=True, on_delete='SET NULL')
	description = TextField(null=True)
