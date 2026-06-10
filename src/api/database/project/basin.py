from peewee import *
from . import base


class Codes_bsn(base.BaseModel):
	pet_file = CharField(null=True)
	wq_file = CharField(null=True)
	pet = IntegerField()
	event = IntegerField() #not used
	crack = IntegerField()
	swift_out = IntegerField()
	sed_det = IntegerField()
	rte_cha = IntegerField()
	deg_cha = IntegerField() #not used
	wq_cha = IntegerField() #not used
	nostress = IntegerField()
	cn = IntegerField() #not used
	c_fact = IntegerField() #not used
	carbon = IntegerField()
	lapse = IntegerField()
	uhyd = IntegerField()
	sed_cha = IntegerField() #not used
	tiledrain = IntegerField()
	wtable = IntegerField()
	soil_p = IntegerField()
	gampt = IntegerField()
	atmo_dep = CharField() #not used???
	stor_max = IntegerField() #not used
	qual2e = IntegerField() #formerly i_fpwet
	gwflow = IntegerField(default=0)
	idc_till = IntegerField(default=3)


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


class Carbon_bsn(base.BaseModel):
	init_seq = DoubleField(default=0.95)
	init_microb = DoubleField(default=0.02)
	init_slow = DoubleField(default=0.44)
	init_passive = DoubleField(default=0.54)
	koc_c = DoubleField(default=1000)
	solc_ratio = DoubleField(default=0.5)
	till_eff_days = DoubleField(default=100)
	manure_c_frac = DoubleField(default=0.5)
	bio_consol = DoubleField(default=0.15)
	till_consol = DoubleField(default=0.1)
	tmpf_eqn = IntegerField(default=2)
	watf_eqn = IntegerField(default=1)
	t_cbn_min = DoubleField(default=-0.5)
	t_cbn_opt = DoubleField(default=30)
	t_cbn_max = DoubleField(default=50)
	bmix_a = DoubleField(default=3)
	bmix_b = DoubleField(default=5)
	bmix_c = DoubleField(default=-5.5)
	tillmix_a = DoubleField(default=3)
	tillmix_b = DoubleField(default=15)
	tillmix_c = DoubleField(default=-3.5)
	sfc_rsd_photodeg = DoubleField(default=0.001)
	n_act_frac = DoubleField(default=0.02)
	cnr_cap = DoubleField(default=500)
	cnr_ref = DoubleField(default=25)
	cpr_cap = DoubleField(default=5000)
	cpr_ref = DoubleField(default=200)
	mathers_method = IntegerField(default=0)


class Carbon_lyr_bsn(base.BaseModel):
	layer = IntegerField(default=1)
	hp_rate = DoubleField(default=1.2e-5)
	hs_rate = DoubleField(default=2.92e-4)
	microb_rate = DoubleField(default=0.0164)
	meta_rate = DoubleField(default=0.0405)
	str_rate = DoubleField(default=0.0107)
	microb_top_rate = DoubleField(default=0.0164)
	hs_hp = DoubleField(default=0.05)
	a1co2 = DoubleField(default=0.6)
	asco2 = DoubleField(default=0.55)
	apco2 = DoubleField(default=0.55)
	abco2 = DoubleField(default=0.55)

	@classmethod
	def create_layer1(cls):
		m = Carbon_lyr_bsn(layer=1)
		m.save()

	@classmethod
	def create_layer2(cls):
		m = Carbon_lyr_bsn(layer=2, 
              hp_rate=1.2e-5, 
              hs_rate=1.81e-4, 
              microb_rate=0.02,
              meta_rate=0.0507,
              str_rate=0.0134,
              microb_top_rate=0.02,
              a1co2=0.55)
		m.save()
