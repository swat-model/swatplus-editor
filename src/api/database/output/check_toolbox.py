import json

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
		self.swatVersion = 'development'
		self.gwflow = False
		

class CheckToolboxHydrology(CheckToolboxBase):
	def __init__(self):
		self.warnings = []
		self.et = 0
		self.pet = 0
		self.precipitation = 0
		self.snowfall = 0
		self.averageCn = 0
		self.surfaceRunoff = 0
		self.lateralFlow = 0
		self.returnFlow = 0
		self.irr = 0
		self.percolation = 0
		self.revap = 0
		self.recharge = 0
		
		self.etPrecipitation = 0
		self.deepRechargePrecipitation = 0
		self.streamflowPrecipitation = 0
		self.baseflowTotalFlow = 0
		self.surfaceRunoffTotalFlow = 0
		self.percolationPrecipitation = 0
		self.monthlyBasinValues = []
		

class CheckToolboxNitrogen(CheckToolboxBase):
	def __init__(self):
		self.warnings = []
		self.residueMineralization = 0
		self.mineralization = 0
		self.organicFertilizer = 0
		self.uptake = 0
		self.decay = 0
		self.denitrification = 0
		self.totalInorganic = 0
		self.volatilization = 0
		self.nitrification = 0
		self.plantResidue = 0
		
		self.totalLoss = 0
		self.surfaceRunoff = 0
		self.lateralFlow = 0
		self.solubilityRatio = 0
		

class CheckToolboxPhosphorus(CheckToolboxBase):
	def __init__(self):
		self.warnings = []
		self.residueMineralization = 0
		self.mineralization = 0
		self.organicFertilizer = 0
		self.uptake = 0
		self.activeStable = 0
		self.inorganicFertilizer = 0
		
		self.totalLoss = 0
		self.surfaceRunoff = 0
		self.solubilityRatio = 0
		

class CheckToolboxSediment(CheckToolboxBase):
	def __init__(self):
		self.warnings = []
		self.surfaceRunoff = 0
		self.instreamSedimentChange = 0
		self.uplandSedimentYieldMax = 0
		self.uplandSedimentYieldAvg = 0
		self.instreamSedimentChangePerHa = 0
		self.channelErosion = 0
		self.channelDeposition = 0


class CheckToolboxPlantGrowth(CheckToolboxBase):
	def __init__(self):
		self.warnings = []
		self.tempStressDays = 0
		self.waterStressDays = 0
		self.nStressDays = 0
		self.pStressDays = 0
		self.soilAirStressDays = 0
		self.avgBiomass = 0
		self.avgYield = 0
		self.nRemoved = 0
		self.pRemoved = 0
		self.totalFertilizerN = 0
		self.totalFertilizerP = 0
		self.plantUptakeN = 0
		self.plantUptakeP = 0
		self.hruMgts = []
		

class CheckToolboxHruMgt(CheckToolboxBase):
	def __init__(self):
		self.hru = 0
		self.mgts = []
		

class CheckToolboxMgtItem(CheckToolboxBase):
	def __init__(self):
		self.date = ''
		self.description = ''


class CheckToolboxData:
	def __init__(self):
		# wb_basin
		self.precip = 0.0
		self.snofall = 0.0
		self.surq_gen = 0.0
		self.latq = 0.0
		self.wateryld = 0.0
		self.perc = 0.0
		self.sw_init = None
		self.sw_final = None
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
		self.aqu_flo = None
		self.aqu_dep_wt = None
		self.aqu_stor = None
		self.aqu_rchrg = None
		self.aqu_seep = None
		self.aqu_revap = None
		self.aqu_flo_cha = None
		self.aqu_flo_res = None
		self.aqu_flo_ls = None
		self.aqu_no3_lat = None
		self.aqu_no3_seep = None
		self.aqu_no3_rchg = None
		
		# pw
		self.lai = None
		self.bioms = None
		self.yield_val = None  # 'yield' is a Python keyword
		self.residue = None
		self.pplnt = None
		self.nplt = None
		
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
		self.uplandSedYield = None
		self.maxUplandSedYield = None
		self.chaErosion = None
		self.chaDeposition = None
		
		# derived
		self.nLossesTotalLoss = None
		self.nLossesOrgN = None
		self.nLossesSurfaceRunoff = None
		self.nLossesLateralFlow = None
		self.totalN = None
		self.nLossesSolubilityRatio = None
		self.pLossesTotalLoss = None
		self.pLossesOrgP = None
		self.pLossesSurfaceRunoff = None
		self.pLossesSolubilityRatio = None
		
		# cha stuff
		self.sed_in = None
		self.sed_out = None
		self.sed_stor = None
		
		# ratios
		self.baseflowToTotal = None
		self.surfaceflowToTotal = None
		self.totalFlowToPrecip = None
		self.etToPrecip = None
		self.percoToPrecip = None
		self.seepToPrecip = None
		
		# warnings
		self.warnings = CheckToolboxDataWarnings()


class CheckToolboxDataWarnings:
	def __init__(self):
		self.plants = []
		self.nb = []
		self.wb = []
		self.sed = []


class CheckToolboxHru:
	def __init__(self):
		self.name = ''
		self.landuse = ''
		self.area = 0.0


class CheckToolboxLanduseData:
	def __init__(self):
		self.area = 0.0
		self.hrus = []
		self.data = CheckToolboxData()