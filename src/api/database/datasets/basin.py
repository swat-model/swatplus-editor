from peewee import *
from . import base


class Codes_bsn(base.BaseModel):
	pet_file = CharField(null=True)
	wq_file = CharField(null=True)
	pet = IntegerField()
	event = IntegerField()
	crack = IntegerField()
	swift_out = IntegerField()
	sed_det = IntegerField()
	rte_cha = IntegerField()
	deg_cha = IntegerField()
	wq_cha = IntegerField()
	nostress = IntegerField()
	cn = IntegerField()
	c_fact = IntegerField()
	carbon = IntegerField()
	lapse = IntegerField()
	uhyd = IntegerField()
	sed_cha = IntegerField()
	tiledrain = IntegerField()
	wtable = IntegerField()
	soil_p = IntegerField()
	gampt = IntegerField()
	atmo_dep = CharField()
	stor_max = IntegerField()
	i_fpwet = IntegerField()


class Parameters_bsn(base.BaseModel):
	lai_noevap = DoubleField()
	sw_init = DoubleField()
	surq_lag = DoubleField()
	adj_pkrt = DoubleField()
	adj_pkrt_sed = DoubleField()
	lin_sed = DoubleField()
	exp_sed = DoubleField()
	orgn_min = DoubleField()
	n_uptake = DoubleField()
	p_uptake = DoubleField()
	n_perc = DoubleField()
	p_perc = DoubleField()
	p_soil = DoubleField()
	p_avail = DoubleField()
	rsd_decomp = DoubleField()
	pest_perc = DoubleField()
	msk_co1 = DoubleField()
	msk_co2 = DoubleField()
	msk_x = DoubleField()
	nperco_lchtile = DoubleField()
	evap_adj = DoubleField()
	scoef = DoubleField()
	denit_exp = DoubleField()
	denit_frac = DoubleField()
	man_bact = DoubleField()
	adj_uhyd = DoubleField()
	cn_froz = DoubleField()
	dorm_hr = DoubleField()
	plaps = DoubleField()
	tlaps = DoubleField()
	n_fix_max = DoubleField()
	rsd_decay = DoubleField()
	rsd_cover = DoubleField()
	urb_init_abst = DoubleField()
	petco_pmpt = DoubleField()
	uhyd_alpha = DoubleField()
	splash = DoubleField()
	rill = DoubleField()
	surq_exp = DoubleField()
	cov_mgt = DoubleField()
	cha_d50 = DoubleField()
	co2 = DoubleField()
	day_lag_max = DoubleField()
	igen = IntegerField()
