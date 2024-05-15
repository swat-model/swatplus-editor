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
	enabled = IntegerField(default=0)
	soil = IntegerField(default=1)
	stress = IntegerField(default=2)
	conversion_factor = DoubleField(default=500)


class Salt_plants(BaseModel):
	name = ForeignKeyField(Plants_plt, on_delete='CASCADE', related_name='salts')
	a = DoubleField()
	b = DoubleField()
	so4 = DoubleField()
	ca = DoubleField()
	mg = DoubleField()
	na = DoubleField()
	k = DoubleField()
	cl = DoubleField()
	co3 = DoubleField()
	hco3 = DoubleField()

	@classmethod
	def get_a_b_defaults(cls):
		return {
			'agrc': [0,0],
			'agrl': [0,0],
			'agrr': [0,0],
			'alfa': [2,7.3],
			'almd': [1.5,19],
			'appl': [1.3,17.5],
			'aspn': [0,0],
			'aspr': [4.1,2],
			'bana': [0,0],
			'barl': [8,5],
			'barl100': [8,5],
			'barl105': [8,5],
			'bbls': [0,0],
			'berm': [6.9,6.4],
			'blug': [0,0],
			'bocu': [0,0],
			'broc': [2.8,19.2],
			'brom': [4.4,6.8],
			'bros': [7,5.1],
			'bsvg': [0,0],
			'cabg': [1.8,9.7],
			'cana': [10,11.2],
			'cang': [6,5.6],
			'canp': [10,11.2],
			'cant': [1.3,5.7],
			'cash': [0,0],
			'cauf': [3,7.7],
			'cedr': [0,0],
			'celr': [1.8,6.2],
			'clva': [1.5,12],
			'clvr': [1.5,12],
			'clvs': [6,5.6],
			'cngr': [0,0],
			'cocb': [0,0],
			'coco': [0,0],
			'coct': [0,0],
			'coff': [0,0],
			'cont': [0,0],
			'corn': [1.7,12],
			'corn100': [1.7,12],
			'corn110': [1.7,12],
			'corn120': [1.7,12],
			'corn50': [1.7,12],
			'corn90': [1.7,12],
			'cotp': [7.7,5.2],
			'cotp135': [7.7,5.2],
			'cotp145': [7.7,5.2],
			'cotp155': [7.7,5.2],
			'cotp180': [7.7,5.2],
			'cots': [7.7,5.2],
			'cots135': [7.7,5.2],
			'cots145': [7.7,5.2],
			'cots155': [7.7,5.2],
			'cots180': [7.7,5.2],
			'crdy': [0,0],
			'crgr': [0,0],
			'crir': [0,0],
			'crrt': [1,14],
			'crwo': [0,0],
			'csil': [1.8,7.4],
			'csil100': [1.8,7.4],
			'csil110': [1.8,7.4],
			'csil120': [1.8,7.4],
			'csil90': [1.8,7.4],
			'cucm': [2.5,13],
			'cwgr': [3.5,4],
			'cwps': [2.5,11],
			'deil': [2.5,11],
			'dwht': [5.9,3.8],
			'dwht110': [5.9,3.8],
			'dwht120': [5.9,3.8],
			'egam': [0,0],
			'eggp': [1.1,6.9],
			'fesc': [3.9,5.3],
			'flax': [1.7,12],
			'fodb': [0,0],
			'fodn': [0,0],
			'foeb': [0,0],
			'foen': [0,0],
			'fomi': [0,0],
			'fpea': [1.3,17.5],
			'frsd': [0,0],
			'frsd_suhf': [0,0],
			'frsd_sums': [0,0],
			'frsd_sust': [0,0],
			'frsd_tecf': [0,0],
			'frsd_tems': [0,0],
			'frsd_teof': [0,0],
			'frsd_test': [0,0],
			'frse': [0,0],
			'frse_sudrf': [0,0],
			'frse_suds': [0,0],
			'frse_suhf': [0,0],
			'frse_sums': [0,0],
			'frse_sust': [0,0],
			'frse_tecf': [0,0],
			'frse_teds': [0,0],
			'frse_tems': [0,0],
			'frse_teof': [0,0],
			'frse_test': [0,0],
			'frst': [0,0],
			'frst_suhf': [0,0],
			'frst_sums': [0,0],
			'frst_sust': [0,0],
			'frst_tecf': [0,0],
			'frst_tems': [0,0],
			'frst_teof': [0,0],
			'frst_test': [0,0],
			'grap': [1.5,16],
			'grar': [1.5,16],
			'gras': [0,0],
			'grbn': [1,19],
			'grsg': [6.8,16],
			'grsg100': [6.8,16],
			'grsg105': [6.8,16],
			'grsg110': [6.8,16],
			'grsg95': [6.8,16],
			'hay': [2,7.3],
			'hmel': [1.3,5.7],
			'indn': [0,0],
			'jhgr': [0,0],
			'ldgp': [0,0],
			'lent': [0,0],
			'lett': [1.3,13],
			'lima': [6,5.6],
			'mapl': [0,0],
			'mesq': [0,0],
			'migs': [0,0],
			'mint': [0,0],
			'mixc': [0,0],
			'mung': [0,0],
			'oak': [0,0],
			'oats': [6,5.6],
			'oats110': [6,5.6],
			'oats120': [6,5.6],
			'oilp': [0,0],
			'oliv': [6,5.6],
			'onio': [1.2,16],
			'oran': [1.7,16],
			'orcd': [3,7.7],
			'papa': [6,5.6],
			'part': [0,0],
			'past': [0,0],
			'peas': [1.3,17.5],
			'pepp': [1.5,14],
			'pepr': [1.5,14],
			'pine': [0,0],
			'pinp': [6,5.6],
			'plan': [0,0],
			'pmil': [6,5.6],
			'pmil100': [6,5.6],
			'pmil105': [6,5.6],
			'pmil110': [6,5.6],
			'pmil95': [6,5.6],
			'pnut': [3.2,29],
			'popl': [0,0],
			'popy': [0,0],
			'pota': [1.7,12],
			'ptbn': [1,19],
			'radi': [1.3,13],
			'rice': [1.9,19.1],
			'rice120': [1.9,19.1],
			'rice140': [1.9,19.1],
			'rice160': [1.9,19.1],
			'rice180': [1.9,19.1],
			'rngb': [0,0],
			'rngb_sudrf': [0,0],
			'rngb_suds': [0,0],
			'rngb_suhf': [0,0],
			'rngb_sums': [0,0],
			'rngb_sust': [0,0],
			'rngb_tecf': [0,0],
			'rngb_teds': [0,0],
			'rngb_tems': [0,0],
			'rngb_teof': [0,0],
			'rngb_test': [0,0],
			'rnge': [0,0],
			'rnge_sudrf': [0,0],
			'rnge_suds': [0,0],
			'rnge_suhf': [0,0],
			'rnge_sums': [0,0],
			'rnge_sust': [0,0],
			'rnge_tecf': [0,0],
			'rnge_teds': [0,0],
			'rnge_tems': [0,0],
			'rnge_teof': [0,0],
			'rnge_test': [0,0],
			'rubr': [0,0],
			'rye': [11.4,10.8],
			'rye90': [11.4,10.8],
			'ryea': [11.4,10.8],
			'ryeg': [11.4,10.8],
			'ryer': [11.4,10.8],
			'saaz': [11.4,10.8],
			'sava': [0,0],
			'scrn': [1.7,12],
			'scsc': [1.7,12],
			'sept': [0,0],
			'sesb': [2.3,7],
			'sgbt': [7,5.9],
			'sghy': [6.8,16],
			'shrb': [0,0],
			'side': [0,0],
			'soct': [0,0],
			'sont': [0,0],
			'sonu': [0,0],
			'sosa': [0,0],
			'soyb': [5,20],
			'soyb100': [5,20],
			'soyb105': [5,20],
			'soyb110': [5,20],
			'soyb115': [5,20],
			'soyb120': [5,20],
			'spas': [0,0],
			'spin': [2,7.6],
			'spot': [1.5,11],
			'strw': [1,33],
			'sugc': [1.7,5.9],
			'sunf': [4.8,5],
			'sunf100': [4.8,5],
			'sunf110': [4.8,5],
			'sunf90': [4.8,5],
			'swch': [0,0],
			'swgr': [6,5.6],
			'swht': [6,7.1],
			'swht110': [6,7.1],
			'swht120': [6,7.1],
			'swrn': [0,0],
			'teff': [0,0],
			'timo': [3,7.7],
			'tobc': [0,0],
			'toma': [2.5,9.9],
			'tral': [2.5,9.9],
			'trit': [6.1,2.5],
			'tubg': [0,0],
			'tuhb': [0,0],
			'tumi': [0,0],
			'tuwo': [0,0],
			'urbn_cool': [0,0],
			'urbn_warm': [0,0],
			'waln': [1.7,16.1],
			'wbar': [0,0],
			'wehb': [0,0],
			'wetf': [0,0],
			'wetl': [0,0],
			'wetn': [0,0],
			'wewo': [0,0],
			'will': [0,0],
			'wmel': [3,7.7],
			'wpas': [0,0],
			'wspr': [0,0],
			'wwgr': [0,0],
			'wwht': [6,7.1],
			'wwht150': [6,7.1],
			'wwht160': [6,7.1],
			'wwht170': [6,7.1],
			'wetw': [0,0],
			'wetm': [0,0],
		}


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
	plants_uptake = BooleanField(default=False)
	atmo_timestep = CharField(null=True)
	road_timestep = CharField(null=True)
