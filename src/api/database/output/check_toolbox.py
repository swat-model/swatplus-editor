import json

# Note: the interface Run page expects only _aa tables here. Update if that changes.
required_tables = [
	'basin_wb_aa', 'basin_nb_aa', 'basin_pw_aa', 'basin_ls_aa', 'basin_sd_cha_aa',
	'hru_pw_aa', 'hru_wb_aa', 'hru_ls_aa', 'hru_nb_aa',
	'channel_sd_aa'
]

opt_tables = [
	'basin_aqu_aa', 'project_config', 'mgt_out',
	'recall_aa',
	'basin_res_aa', 'reservoir_aa', 'reservoir_yr', 
]

landuse_category_options = [
	'Agriculture',
	'Barley',
	'Beans',
	'Grass',
	'Canola',
	'Clover',
	'Corn',
	'Corn Silage',
	'Cotton',
	'Cover Crop',
	'Cropland',
	'Forest',
	'Grass',
	'Peas',
	'Grain Sorghum',
	'Grapes',
	'Oats',
	'Pasture',
	'Pearl Millet',
	'Range Brush',
	'Range Grasses',
	'Rice',
	'Rye',
	'Soybean',
	'Sparsely Vegetated',
	'Sunflower',
	'Tundra',
	'Urban',
	'Wetland',
	'Wheat',
	'Wildrye'
]

landuse_background_options = [
	'banana',
	'corn',
	'forest',
	'grass',
	'pasture',
	'tomato'
]

class CheckToolboxBase:
	def toJson(self):
		return json.loads(json.dumps(self, default=lambda o: o.__dict__))
	

class CheckToolboxInfo(CheckToolboxBase):
	def __init__(self):
		self.simulationLength = 0
		self.warmUp = 0
		self.hrus = 0
		self.subbasins = 0
		self.lsus = 0
		self.weatherMethod = 'simulated'
		self.watershedArea = 0
		self.hruTotalArea = 0
		self.swatVersion = 'development'
		self.gwflow = False


class CheckToolboxData(CheckToolboxBase):
	def __init__(self):
		# wb_basin
		self.precip = 0.0
		self.snofall = 0.0
		self.surq_gen = 0.0
		self.latq = 0.0
		self.wateryld = 0.0
		self.perc = 0.0
		self.sw_init = 0.0
		self.sw_final = 0.0
		self.et = 0.0
		self.eplant = 0.0
		self.esoil = 0.0
		self.cn = 0.0
		self.pet = 0.0
		self.qtile = 0.0
		self.irr = 0.0
		self.surq_cha = 0.0
		self.surq_res = 0.0
		self.latq_cha = 0.0
		self.latq_res = 0.0
		
		# aqu_basin
		self.aqu_flo = 0.0
		self.aqu_dep_wt = 0.0
		self.aqu_stor = 0.0
		self.aqu_rchrg = 0.0
		self.aqu_seep = 0.0
		self.aqu_revap = 0.0
		self.aqu_flo_cha = 0.0
		self.aqu_flo_res = 0.0
		self.aqu_flo_ls = 0.0
		self.aqu_no3_lat = 0.0
		self.aqu_no3_seep = 0.0
		self.aqu_no3_rchg = 0.0
		
		# pw
		self.lai = 0.0
		self.bioms = 0.0
		self.yield_val = 0.0  # 'yield' is a Python keyword
		self.residue = 0.0
		self.pplnt = 0.0
		self.nplt = 0.0
		
		# stress days
		self.strsw = 0.0
		self.strsa = 0.0
		self.strstmp = 0.0
		self.strsn = 0.0
		self.strsp = 0.0
		
		# nb
		self.percn = 0.0
		self.grzn = 0.0
		self.grzp = 0.0
		self.lab_min_p = 0.0
		self.act_sta_p = 0.0
		self.fertn = 0.0
		self.fertp = 0.0
		self.fixn = 0.0
		self.denit = 0.0
		self.act_nit_n = 0.0
		self.act_sta_n = 0.0
		self.org_lab_p = 0.0
		self.rsd_nitorg_n = 0.0
		self.rsd_laborg_p = 0.0
		self.no3atmo = 0.0
		self.nh4atmo = 0.0
		self.nuptake = 0.0
		self.puptake = 0.0
		
		self.initialNO3 = None
		self.finalNO3 = None
		self.initialOrgN = None
		self.finalOrgN = None
		self.volatilization = None
		self.nitrification = None
		self.mineralization = None
		
		# ls
		self.sedorgn = 0.0
		self.sedorgp = 0.0
		self.sedyld = 0.0
		self.lat3no3 = 0.0
		self.surqno3 = 0.0
		self.surqsolp = 0.0
		self.uplandSedYield = 0.0
		self.maxUplandSedYield = 0.0
		self.chaErosion = 0.0
		self.chaDeposition = 0.0
		
		# derived
		self.nLossesTotalLoss = 0.0
		self.nLossesOrgN = 0.0
		self.nLossesSurfaceRunoff = 0.0
		self.nLossesLateralFlow = 0.0
		self.totalN = 0.0
		self.nLossesSolubilityRatio = 0.0
		self.pLossesTotalLoss = 0.0
		self.pLossesOrgP = 0.0
		self.pLossesSurfaceRunoff = 0.0
		self.pLossesSolubilityRatio = 0.0
		
		# cha stuff
		self.sed_in = 0.0
		self.sed_out = 0.0
		self.sed_stor = 0.0
		
		# ratios
		self.baseflowToTotal = 0.0
		self.surfaceflowToTotal = 0.0
		self.totalFlowToPrecip = 0.0
		self.etToPrecip = 0.0
		self.percoToPrecip = 0.0
		self.seepToPrecip = 0.0

		# point sources
		self.subbasinLoad = CheckToolboxPointSourcesLoad()
		self.pointSourceInletLoad = CheckToolboxPointSourcesLoad()
		self.fromInletAndPointSource = CheckToolboxPointSourcesLoad()

		# reservoirs
		self.reservoirRows = []
		self.avgTrappingEfficiencies = CheckAvgTrappingEfficiency()
		self.avgWaterLosses = CheckAvgWaterLoss()
		self.avgReservoirTrends = CheckAvgReservoirTrend()

		self.reachReport = []
		
		# warnings
		self.warnings = CheckToolboxDataWarnings()


class CheckReservoirRow(CheckToolboxBase):
	def __init__(self):
		self.id = ''
		self.sediment = 0
		self.phosphorus = 0
		self.nitrogen = 0
		self.volumeRatio = 0
		self.fractionEmpty = 0
		self.seepage = 0
		self.evapLoss = 0


class CheckAvgTrappingEfficiency(CheckToolboxBase):
	def __init__(self):
		self.sediment = 0
		self.phosphorus = 0
		self.nitrogen = 0


class CheckAvgWaterLoss(CheckToolboxBase):
	def __init__(self):
		self.totalRemoved = 0
		self.evaporation = 0
		self.seepage = 0


class CheckAvgReservoirTrend(CheckToolboxBase):
	def __init__(self):
		self.numberReservoirs = 0
		self.maxVolume = 0
		self.minVolume = 0
		self.fractionEmpty = 0


class CheckToolboxPointSourcesLoad(CheckToolboxBase):
	def __init__(self):
		self.flow = 0
		self.sediment = 0
		self.nitrogen = 0
		self.phosphorus = 0


class CheckToolboxDataWarnings(CheckToolboxBase):
	def __init__(self):
		self.plants = []
		self.nb_nitrogen = []
		self.nb_phosphorus = []
		self.wb = []
		self.sed = []
		self.ptsrc = []
		self.res = []


class CheckToolboxHru(CheckToolboxBase):
	def __init__(self):
		self.name = ''
		self.landuse = ''
		self.soil = ''
		self.area = 0.0
		self.index = 0


class CheckToolboxLanduseData(CheckToolboxBase):
	def __init__(self):
		self.area = 0.0
		self.hrus = []
		self.data = CheckToolboxData()
		

class CheckToolboxHruMgt(CheckToolboxBase):
	def __init__(self):
		self.name = ''
		self.landuse = ''
		self.soil = ''
		self.area = 0.0
		self.index = 0
		self.mgts = []
		

class CheckToolboxMgtItem(CheckToolboxBase):
	def __init__(self):
		self.date = ''
		self.op = ''
		self.description = ''


class CheckReach(CheckToolboxBase):
	def __init__(self):
		self.id = ''
		self.sediment = 0
		self.phosphorus = 0
		self.nitrogen = 0