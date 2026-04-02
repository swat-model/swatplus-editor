from helpers.executable_api import ExecutableApi, Unbuffered
from peewee import *

from database.project.setup import SetupProjectDatabase
from database.output.setup import SetupOutputDatabase
from database.output import check_toolbox, aquifer, channel, hyd, losses, misc, nutbal, plantwx, reservoir, waterbal, pest, base
from database.project import connect, climate, gis, regions, simulation, hru_parm_db, config
from database import lib

import traceback
import json, sys, argparse


class GetSwatplusCheckToolbox(ExecutableApi):
	def __init__(self, project_db_file, output_db_file):
		self.output_db_file = output_db_file.replace("\\","/")
		self.project_db_file = project_db_file.replace("\\","/")
		SetupOutputDatabase.init(self.output_db_file)
		SetupProjectDatabase.init(self.project_db_file)

	def __del__(self):
		SetupOutputDatabase.close()
		SetupProjectDatabase.close()

	def table_exists(self, table_name):
		conn = lib.open_db(self.output_db_file)
		exists = lib.exists_table(conn, table_name)
		conn.close()
		return exists
	
	def get(self):
		required_tables = [
			'basin_wb_aa', 'basin_nb_aa', 'basin_pw_aa', 'basin_ls_aa',
			'basin_sd_cha_aa'
		]
		
		opt_tables = [
			'basin_aqu_aa'
		]
		
		pc = config.Project_config.get()
		use_gwflow = pc.use_gwflow == 1

		conn = lib.open_db(self.output_db_file)
		sys.stdout.write(self.output_db_file)
		for table in required_tables:
			if not lib.exists_table(conn, table):
				conn.close()
				return json.dumps({'error': 'Output file "{}" does not exist in your output database. Re-run your model and check all yearly and average annual files under the print options, and keep the analyze output box checked.'.format(table)})
		
		unavailable_tables = []
		for table in opt_tables:
			if not lib.exists_table(conn, table):
				unavailable_tables.append(table)
		conn.close()

		try:
			total_area = connect.Rout_unit_con.select(fn.Sum(connect.Rout_unit_con.area)).scalar()

			basin_wb_aa = waterbal.Basin_wb_aa.get_or_none()
			basin_aqu_aa = None if 'basin_aqu_aa' in unavailable_tables else aquifer.Basin_aqu_aa.get_or_none()
			basin_nb_aa = nutbal.Basin_nb_aa.get_or_none()
			basin_pw_aa = plantwx.Basin_pw_aa.get_or_none()
			basin_ls_aa = losses.Basin_ls_aa.get_or_none()
			basin_sd_cha_aa = channel.Basin_sd_cha_aa.get_or_none()

			#read HRUs
			hru_cons = connect.Hru_con.select()
			hruDataLookup = []
			for h in hru_cons:
				hru = check_toolbox.CheckToolboxHru()
				hru.name = h.name
				hru.area = h.area
				hru.landuse = 'No Land Use' if h.hru.lu_mgt is None else h.hru.lu_mgt.name.replace('_lum', '')
				hruDataLookup.append(hru)

			overallData = check_toolbox.CheckToolboxData()

			# surface
			overallData.et = basin_wb_aa.et
			overallData.pet = basin_wb_aa.pet
			overallData.precip = basin_wb_aa.precip
			overallData.snofall = basin_wb_aa.snofall
			overallData.cn = basin_wb_aa.cn
			overallData.surq_gen = basin_wb_aa.surq_gen
			overallData.latq = basin_wb_aa.latq
			overallData.irr = basin_wb_aa.irr
			overallData.perc = basin_wb_aa.perc

			# aquifer
			if basin_aqu_aa is not None:
				overallData.aqu_flo_cha = basin_aqu_aa.flo_cha
				overallData.aqu_revap = basin_aqu_aa.revap
				overallData.aqu_seep = basin_aqu_aa.seep
				overallData.aqu_no3_lat = basin_aqu_aa.no3_lat
				overallData.aqu_no3_seep = basin_aqu_aa.no3_seep
				overallData.aqu_no3_rchg = basin_aqu_aa.no3_rchg

			# derived metrics
			totalFlow = overallData.aqu_flo_cha + overallData.latq + overallData.surq_gen
			if totalFlow != 0:
				aqu_flo_cha = 0 if overallData.aqu_flo_cha is None else overallData.aqu_flo_cha
				overallData.baseflowToTotal = (aqu_flo_cha + overallData.latq) / totalFlow
				overallData.surfaceToTotal = overallData.surq_gen / totalFlow

			if overallData.precip != 0:
				overallData.totalFlowToPrecip = totalFlow / overallData.precip
				overallData.etToPrecip = overallData.et / overallData.precip
				overallData.percoToPrecip = overallData.perc / overallData.precip
				overallData.seepToPrecip = None if overallData.aqu_seep is None else overallData.aqu_seep / overallData.precip

			# gather information about nutrients

			# read nitrogen
			overallData.grzn = basin_nb_aa.grzn
			overallData.grzp = basin_nb_aa.grzp
			overallData.lab_min_p = basin_nb_aa.lab_min_p
			overallData.act_sta_p = basin_nb_aa.act_sta_p
			overallData.fertn = basin_nb_aa.fertn
			overallData.fertp = basin_nb_aa.fertp
			overallData.fixn = basin_nb_aa.fixn
			overallData.denit = basin_nb_aa.denit
			overallData.act_nit_n = basin_nb_aa.act_nit_n
			overallData.act_sta_n = basin_nb_aa.act_sta_n
			overallData.org_lab_p = basin_nb_aa.org_lab_p
			overallData.rsd_nitorg_n = basin_nb_aa.rsd_nitorg_n
			overallData.rsd_laborg_p = basin_nb_aa.rsd_laborg_p
			overallData.no3atmo = basin_nb_aa.no3atmo
			overallData.nh4atmo = basin_nb_aa.nh4atmo
			overallData.nuptake = basin_nb_aa.nuptake
			overallData.puptake = basin_nb_aa.puptake

			# read plant uptake of nitrogen
			overallData.nplt = basin_pw_aa.nplt
			overallData.pplnt = basin_pw_aa.pplnt
			overallData.yield_val = basin_pw_aa.yield_val
			overallData.bioms = basin_pw_aa.bioms
			# read stress days
			overallData.strsw = basin_pw_aa.strsw
			overallData.strsa = basin_pw_aa.strsa
			overallData.strstmp = basin_pw_aa.strstmp
			overallData.strsn = basin_pw_aa.strsn
			overallData.strsp = basin_pw_aa.strsp

			# issue warnings
			overallData.warnings = check_toolbox.CheckToolboxDataWarnings()

			if overallData.strsp > 60:
				overallData.warnings.plants.append('More than 60 days of phosphorus stress')
			if overallData.strsn > 60:
				overallData.warnings.plants.append('More than 60 days of nitrogen stress')
			if overallData.strsw > 80:
				overallData.warnings.plants.append('More than 80 days of water stress')
			if overallData.strsp < 1:
				overallData.warnings.plants.append('Unusually low phosphorus stress')
			if overallData.strsn < 1:
				overallData.warnings.plants.append('Unusually low nitrogen stress')
			if overallData.yield_val < 0.5:
				overallData.warnings.plants.append('Yield may be low if there is harvested crop')
			if overallData.bioms < 1:
				overallData.warnings.plants.append('Biomass averages less than 1 metric ton per hectare"')

			# read sedorg nitrogen
			# ls stuff
			overallData.lat3no3 = basin_ls_aa.lat3no3
			overallData.sedorgp = basin_ls_aa.sedorgp
			overallData.sedorgn = basin_ls_aa.sedorgn
			overallData.surqno3 = basin_ls_aa.surqno3
			overallData.surqsolp = basin_ls_aa.surqsolp
			overallData.sedyld = basin_ls_aa.sedyld

			# issue warnings 
			if overallData.denit == 0:
				overallData.warnings.nb.append('Nitrogen~Denitrification is zero, consider decreasing SDNCO: (Denitrification threshold water content)')
			elif overallData.fertn != 0:
				calc = overallData.denit / overallData.fertn
				if calc < 0.01:
					overallData.warnings.nb.append('Nitrogen~Denitrification is less than 2% of the applied fertilizer amount')
				elif calc > 0.4:
					overallData.warnings.nb.append('Nitrogen~Denitrification is greater than 25% of the applied fertilizer amount')
			
			if overallData.fertn != 0:
				calc = overallData.nplt / overallData.fertn
				if calc < 0.5:
					overallData.warnings.nb.append('Nitrogen~Crop is consuming less than half the amount of applied nitrogen')

			overallData.nLossesTotalLoss = overallData.sedorgn + overallData.surqno3 + overallData.lat3no3
			overallData.nLossesOrgN = overallData.sedorgn
			overallData.nLossesSurfaceRunoff = overallData.surqno3
			overallData.nLossesLateralFlow = overallData.lat3no3
			overallData.totalN = overallData.nLossesOrgN + overallData.nLossesSurfaceRunoff

			if overallData.totalN != 0:
				overallData.nLossesSolubilityRatio = overallData.nLossesSurfaceRunoff / overallData.totalN

			overallData.pLossesTotalLoss = overallData.sedorgp + overallData.surqsolp
			overallData.pLossesOrgP = overallData.sedorgp
			overallData.pLossesSurfaceRunoff = overallData.surqsolp

			if overallData.pLossesTotalLoss != 0:
				overallData.pLossesSolubilityRatio = overallData.pLossesSurfaceRunoff / overallData.pLossesTotalLoss

			if overallData.nLossesTotalLoss > 0.4 * overallData.fertn:
				overallData.warnings.nb.append("Nitrogen~Total nitrogen losses are greater than 40% of applied N")
			elif overallData.nLossesTotalLoss < 0.1 * overallData.fertn:
				overallData.warnings.nb.append("Nitrogen~Total nitrogen losses are less than 8% of applied N, may be incorrect in agricultural areas. Likely fine in unmanaged areas or forest dominated watersheds.")

			if overallData.nLossesSurfaceRunoff > 4.7:
				overallData.warnings.nb.append("Nitrogen~Nitrate losses in surface runoff may be high")
			elif overallData.nLossesSurfaceRunoff < 0.15:
				overallData.warnings.nb.append("Nitrogen~Nitrate losses in surface runoff may be low")

			if overallData.nLossesOrgN > 33:
				overallData.warnings.nb.append("Nitrogen~Organic/Particulate nitrogen losses in surface runoff may be high")
			elif overallData.nLossesOrgN < 0.3:
				overallData.warnings.nb.append("Nitrogen~Organic/Particulate nitrogen losses in surface runoff may be low")

			if overallData.pLossesSurfaceRunoff > 1.2:
				overallData.warnings.nb.append("Phosphorus~Soluble phosphorus losses in surface runoff may be high")
			elif overallData.pLossesSurfaceRunoff < 0.025:
				overallData.warnings.nb.append("Phosphorus~Soluble phosphorus losses in surface runoff may be low")

			if overallData.pLossesOrgP > 14:
				overallData.warnings.nb.append("Phosphorus~Organic/Particulate phosphorus losses in surface runoff may be high")
			elif overallData.pLossesOrgP < 0:
				overallData.warnings.nb.append("Phosphorus~Organic/Particulate phosphorus losses in surface runoff may be low")

			if overallData.nLossesSolubilityRatio > 0.85:
				overallData.warnings.nb.append("Nitrogen~Solubility ratio for nitrogen in runoff is high")
			elif overallData.nLossesSolubilityRatio < 0.1:
				overallData.warnings.nb.append("Nitrogen~Solubility ratio for nitrogen in runoff is low")

			if overallData.pLossesSolubilityRatio > 0.95:
				overallData.warnings.nb.append("Phosphorus~Solubility ratio for phosphorus in runoff is high, may be ok in uncultivated areas")
			elif overallData.pLossesSolubilityRatio < 0.13:
				overallData.warnings.nb.append("Phosphorus~Solubility ratio for phosphorus in runoff is low, may indicate a problem")

			if overallData.lat3no3 > 50:
				overallData.warnings.nb.append("Nitrogen~Nitrate leaching is greater than 50 kg/ha, may indicate a problem.")

			if overallData.fertn != 0:
				ratio = overallData.lat3no3 / overallData.fertn
				if ratio < 0.21:
					overallData.warnings.nb.append("Nitrogen~Nitrate leaching is less than 21% of the applied fertilizer.")
				elif ratio > 0.38:
					overallData.warnings.nb.append("Nitrogen~Nitrate leaching is greater is more than 38% of the applied fertilizer, may indicate a problem.")

			if overallData.precip < 65:
				overallData.warnings.wb.append(f"Precipitation may be too low ({overallData.precip:.2f} < 65 mm)")
			elif overallData.precip > 3400:
				overallData.warnings.wb.append(f"Precipitation seems too high ({overallData.precip:.2f}) > 3400 mm")

			if overallData.surfaceflowToTotal > 0.80:
				overallData.warnings.wb.append(f"'Surface Runoff' to 'Total Flow' ratio may be too high ({overallData.surfaceflowToTotal:.2f} > 0.8)")
			elif overallData.surfaceflowToTotal < 0.20:
				overallData.warnings.wb.append(f"'Surface Runoff' to 'Total Flow' ratio appears too low ({overallData.surfaceflowToTotal:.2f} < 0.2)")

			if totalFlow != 0:
				gwqRatio = overallData.aqu_flo_cha / totalFlow
				if gwqRatio > 0.69:
					overallData.warnings.wb.append("Groundwater ratio may be high")
				elif gwqRatio < 0.22:
					overallData.warnings.wb.append("Groundwater ratio may be low")

			if overallData.latq > overallData.aqu_flo_cha:
				overallData.warnings.wb.append("Lateral flow is greater than groundwater flow; may indicate a problem")

			if overallData.et > overallData.precip:
				overallData.warnings.wb.append("ET Greater than precipitation; may indicate a problem unless irrigated")

			eWaterYield = 0.26 * overallData.precip
			eET = 0.74 * overallData.precip
			ratio_ = 0.0129 * overallData.cn - 0.2857
			eSurq = ratio_ * eWaterYield

			if eWaterYield != 0:
				ratio_ = totalFlow / eWaterYield
				if ratio_ > 1.5:
					overallData.warnings.wb.append("Water yield may be excessive")
				elif ratio_ < 0.5:
					overallData.warnings.wb.append("Water yield may be too low")

			if eSurq != 0:
				ratio_ = overallData.surq_gen / eSurq
				if ratio_ > 1.5:
					overallData.warnings.wb.append("Surface runoff may be excessive")
				elif ratio_ < 0.5:
					overallData.warnings.wb.append("Surface runoff may be too low")

			# channel sediment
			hru_total_area = sum([h.area for h in hruDataLookup])
			overallData.sed_in = basin_sd_cha_aa.sed_in / hru_total_area
			overallData.sed_out = basin_sd_cha_aa.sed_out / hru_total_area
			overallData.sed_stor = basin_sd_cha_aa.sed_stor

			sed_chg = overallData.sed_out - overallData.sed_in
			overallData.uplandSedYield = overallData.sedyld * hru_total_area

			denom = (overallData.uplandSedYield * hru_total_area) + sed_chg
			if denom != 0:
				overallData.chaErosion = (sed_chg / denom) * 100

			if overallData.uplandSedYield != 0:
				overallData.chaDeposition = ((sed_chg * -1) / overallData.uplandSedYield) * 100

			cha_erosion = 0
			cha_deposition = 0
			if overallData.uplandSedYield > 0:
				if sed_chg > 0:
					cha_erosion = (sed_chg / (overallData.uplandSedYield + sed_chg)) * 100
					if cha_erosion > 50:
						overallData.warnings.sed.append("More than 50% of sediment is from instream processes")
				else:
					cha_deposition = ((sed_chg * -1) / overallData.uplandSedYield) * 100
					if cha_deposition > 95:
						overallData.warnings.sed.append("More than 95% of sediment is deposited instream")

			if cha_erosion == 0 and cha_deposition == 0:
				overallData.warnings.sed.append("No in-stream sediment modification; this is unusual")
			elif (cha_erosion > -2 and cha_erosion < 2) or (cha_deposition > -2 and cha_deposition < 2):
				overallData.warnings.sed.append("Very little in-stream sediment modification (< +-2%); this is unusual")

			SetupProjectDatabase.close()
			SetupOutputDatabase.close()
			return json.dumps({
				
			})
		except Exception as ex:
			SetupProjectDatabase.close()
			SetupOutputDatabase.close()
			return json.dumps({'error': 'Error loading SWAT+ Check. Exception: {ex} {tb}'.format(ex=str(ex), tb=traceback.format_exc())})
