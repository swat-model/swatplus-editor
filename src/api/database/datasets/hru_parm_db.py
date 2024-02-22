from peewee import *
from .base import BaseModel


class Plants_plt(BaseModel):
	name = CharField(unique=True)
	plnt_typ = CharField()
	gro_trig = CharField()
	nfix_co = DoubleField()
	days_mat = DoubleField()
	bm_e = DoubleField()
	harv_idx = DoubleField()
	lai_pot = DoubleField()
	frac_hu1 = DoubleField()
	lai_max1 = DoubleField()
	frac_hu2 = DoubleField()
	lai_max2 = DoubleField()
	hu_lai_decl = DoubleField()
	dlai_rate = DoubleField()
	can_ht_max = DoubleField()
	rt_dp_max = DoubleField()
	tmp_opt = DoubleField()
	tmp_base = DoubleField()
	frac_n_yld = DoubleField()
	frac_p_yld = DoubleField()
	frac_n_em = DoubleField()
	frac_n_50 = DoubleField()
	frac_n_mat = DoubleField()
	frac_p_em = DoubleField()
	frac_p_50 = DoubleField()
	frac_p_mat = DoubleField()
	harv_idx_ws = DoubleField()
	usle_c_min = DoubleField()
	stcon_max = DoubleField()
	vpd = DoubleField()
	frac_stcon = DoubleField()
	ru_vpd = DoubleField()
	co2_hi = DoubleField()
	bm_e_hi = DoubleField()
	plnt_decomp = DoubleField()
	lai_min = DoubleField()
	bm_tree_acc = DoubleField()
	yrs_mat = DoubleField()
	bm_tree_max = DoubleField()
	ext_co = DoubleField()
	leaf_tov_mn = DoubleField()
	leaf_tov_mx = DoubleField()
	bm_dieoff = DoubleField()
	rt_st_beg = DoubleField()
	rt_st_end = DoubleField()
	plnt_pop1 = DoubleField()
	frac_lai1 = DoubleField()
	plnt_pop2 = DoubleField()
	frac_lai2 = DoubleField()
	frac_sw_gro = DoubleField()
	aeration = DoubleField()
	#wnd_dead = DoubleField()
	#wnd_flat = DoubleField()
	rsd_pctcov = DoubleField()
	rsd_covfac = DoubleField()
	description = TextField(null=True)


class Fertilizer_frt(BaseModel):
	name = CharField(unique=True)
	min_n = DoubleField()
	min_p = DoubleField()
	org_n = DoubleField()
	org_p = DoubleField()
	nh3_n = DoubleField()
	pathogens = CharField(null=True)
	description = TextField(null=True)


class Tillage_til(BaseModel):
	name = CharField(unique=True)
	mix_eff = DoubleField()
	mix_dp = DoubleField()
	rough = DoubleField()
	ridge_ht = DoubleField()
	ridge_sp = DoubleField()
	description = TextField(null=True)


class Pesticide_pst(BaseModel):
	name = CharField(unique=True)
	soil_ads = DoubleField()
	frac_wash = DoubleField()
	hl_foliage = DoubleField()
	hl_soil = DoubleField()
	solub = DoubleField()
	aq_hlife = DoubleField()
	aq_volat = DoubleField()
	mol_wt = DoubleField()
	aq_resus = DoubleField()
	aq_settle = DoubleField()
	ben_act_dep = DoubleField()
	ben_bury = DoubleField()
	ben_hlife = DoubleField()
	pl_uptake = DoubleField(default=0.01)
	description = TextField(null=True)
	
	
class Pathogens_pth(BaseModel):
	name = CharField(unique=True)
	die_sol = DoubleField()
	grow_sol = DoubleField()
	die_srb = DoubleField()
	grow_srb = DoubleField()
	sol_srb = DoubleField()
	tmp_adj = DoubleField()
	washoff = DoubleField()
	die_plnt = DoubleField()
	grow_plnt = DoubleField()
	frac_man = DoubleField()
	perc_sol = DoubleField()
	detect = DoubleField()
	die_cha = DoubleField()
	grow_cha = DoubleField()
	die_res = DoubleField()
	grow_res = DoubleField()
	swf = DoubleField()
	conc_min = DoubleField()


class Urban_urb(BaseModel):
	name = CharField(unique=True)
	frac_imp = DoubleField()
	frac_dc_imp = DoubleField()
	curb_den = DoubleField()
	urb_wash = DoubleField()
	dirt_max = DoubleField()
	t_halfmax = DoubleField()
	conc_totn = DoubleField()
	conc_totp = DoubleField()
	conc_no3n = DoubleField()
	urb_cn = DoubleField()
	description = TextField(null=True)


class Septic_sep(BaseModel):
	name = CharField(unique=True)
	q_rate = DoubleField()
	bod = DoubleField()
	tss = DoubleField()
	nh4_n = DoubleField()
	no3_n = DoubleField()
	no2_n = DoubleField()
	org_n = DoubleField()
	min_p = DoubleField()
	org_p = DoubleField()
	fcoli = DoubleField()
	description = TextField(null=True)


class Snow_sno(BaseModel):
	name = CharField(unique=True)
	fall_tmp = DoubleField()
	melt_tmp = DoubleField()
	melt_max = DoubleField()
	melt_min = DoubleField()
	tmp_lag = DoubleField()
	snow_h2o = DoubleField()
	cov50 = DoubleField()
	snow_init = DoubleField()
