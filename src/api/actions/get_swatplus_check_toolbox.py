from itertools import groupby

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
			'basin_wb_aa', 'basin_nb_aa', 'basin_pw_aa', 'basin_ls_aa', 'basin_sd_cha_aa',
			'hru_pw_aa', 'hru_wb_aa', 'hru_ls_aa', 'hru_nb_aa',
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
			hru_data_lookup = []
			available_landuses = []
			for h in hru_cons:
				hru = check_toolbox.CheckToolboxHru()
				hru.name = h.name
				hru.area = h.area
				hru.landuse = 'No Land Use' if h.hru.lu_mgt is None else h.hru.lu_mgt.name.replace('_lum', '')
				hru_data_lookup.append(hru)
				if hru.landuse not in available_landuses:
					available_landuses.append(hru.landuse)

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

			# read sedorg nitrogen
			# ls stuff
			overallData.lat3no3 = basin_ls_aa.lat3no3
			overallData.sedorgp = basin_ls_aa.sedorgp
			overallData.sedorgn = basin_ls_aa.sedorgn
			overallData.surqno3 = basin_ls_aa.surqno3
			overallData.surqsolp = basin_ls_aa.surqsolp
			overallData.sedyld = basin_ls_aa.sedyld

			# issue overall warnings 			

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

			self.set_common_data(overallData, True, totalFlow)			

			# channel sediment
			hru_total_area = sum([h.area for h in hru_data_lookup])
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

			# Get data by land use
			landuse_data = self.get_landuse_data(hru_data_lookup)
			overallData.maxUplandSedYield = losses.Hru_ls_aa.select(fn.Max(losses.Hru_ls_aa.sedyld)).scalar()

			SetupProjectDatabase.close()
			SetupOutputDatabase.close()
			return json.dumps({
				
			})
		except Exception as ex:
			SetupProjectDatabase.close()
			SetupOutputDatabase.close()
			return json.dumps({'error': 'Error loading SWAT+ Check. Exception: {ex} {tb}'.format(ex=str(ex), tb=traceback.format_exc())})
		
	def set_common_data(self, data, do_water_yield_warnings=False, totalFlow = 0):
		if data.strsp > 60:
			data.warnings.plants.append('More than 60 days of phosphorus stress')
		if data.strsn > 60:
			data.warnings.plants.append('More than 60 days of nitrogen stress')
		if data.strsw > 80:
			data.warnings.plants.append('More than 80 days of water stress')
		if data.strsp < 1:
			data.warnings.plants.append('Unusually low phosphorus stress')
		if data.strsn < 1:
			data.warnings.plants.append('Unusually low nitrogen stress')
		if data.yield_val < 0.5:
			data.warnings.plants.append('Yield may be low if there is harvested crop')
		if data.bioms < 1:
			data.warnings.plants.append('Biomass averages less than 1 metric ton per hectare"')

		if data.denit == 0:
			data.warnings.nb.append('Nitrogen~Denitrification is zero, consider decreasing SDNCO: (Denitrification threshold water content)')
		elif data.fertn != 0:
			calc = data.denit / data.fertn
			if calc < 0.01:
				data.warnings.nb.append('Nitrogen~Denitrification is less than 2% of the applied fertilizer amount')
			elif calc > 0.4:
				data.warnings.nb.append('Nitrogen~Denitrification is greater than 25% of the applied fertilizer amount')
		
		if data.fertn != 0:
			calc = data.nplt / data.fertn
			if calc < 0.5:
				data.warnings.nb.append('Nitrogen~Crop is consuming less than half the amount of applied nitrogen')
				
		data.nLossesTotalLoss = data.sedorgn + data.surqno3 + data.lat3no3
		data.nLossesOrgN = data.sedorgn
		data.nLossesSurfaceRunoff = data.surqno3
		data.nLossesLateralFlow = data.lat3no3
		data.totalN = data.nLossesOrgN + data.nLossesSurfaceRunoff

		if data.totalN != 0:
			data.nLossesSolubilityRatio = data.nLossesSurfaceRunoff / data.totalN

		data.pLossesTotalLoss = data.sedorgp + data.surqsolp
		data.pLossesOrgP = data.sedorgp
		data.pLossesSurfaceRunoff = data.surqsolp

		if data.pLossesTotalLoss != 0:
			data.pLossesSolubilityRatio = data.pLossesSurfaceRunoff / data.pLossesTotalLoss

		if data.nLossesTotalLoss > 0.4 * data.fertn:
			data.warnings.nb.append("Nitrogen~Total nitrogen losses are greater than 40% of applied N")
		elif data.nLossesTotalLoss < 0.1 * data.fertn:
			data.warnings.nb.append("Nitrogen~Total nitrogen losses are less than 8% of applied N, may be incorrect in agricultural areas. Likely fine in unmanaged areas or forest dominated watersheds.")

		if data.nLossesSurfaceRunoff > 4.7:
			data.warnings.nb.append("Nitrogen~Nitrate losses in surface runoff may be high")
		elif data.nLossesSurfaceRunoff < 0.15:
			data.warnings.nb.append("Nitrogen~Nitrate losses in surface runoff may be low")

		if data.nLossesOrgN > 33:
			data.warnings.nb.append("Nitrogen~Organic/Particulate nitrogen losses in surface runoff may be high")
		elif data.nLossesOrgN < 0.3:
			data.warnings.nb.append("Nitrogen~Organic/Particulate nitrogen losses in surface runoff may be low")

		if data.pLossesSurfaceRunoff > 1.2:
			data.warnings.nb.append("Phosphorus~Soluble phosphorus losses in surface runoff may be high")
		elif data.pLossesSurfaceRunoff < 0.025:
			data.warnings.nb.append("Phosphorus~Soluble phosphorus losses in surface runoff may be low")

		if data.pLossesOrgP > 14:
			data.warnings.nb.append("Phosphorus~Organic/Particulate phosphorus losses in surface runoff may be high")
		elif data.pLossesOrgP < 0:
			data.warnings.nb.append("Phosphorus~Organic/Particulate phosphorus losses in surface runoff may be low")

		if data.nLossesSolubilityRatio > 0.85:
			data.warnings.nb.append("Nitrogen~Solubility ratio for nitrogen in runoff is high")
		elif data.nLossesSolubilityRatio < 0.1:
			data.warnings.nb.append("Nitrogen~Solubility ratio for nitrogen in runoff is low")

		if data.pLossesSolubilityRatio > 0.95:
			data.warnings.nb.append("Phosphorus~Solubility ratio for phosphorus in runoff is high, may be ok in uncultivated areas")
		elif data.pLossesSolubilityRatio < 0.13:
			data.warnings.nb.append("Phosphorus~Solubility ratio for phosphorus in runoff is low, may indicate a problem")

		if data.lat3no3 > 50:
			data.warnings.nb.append("Nitrogen~Nitrate leaching is greater than 50 kg/ha, may indicate a problem.")

		if data.fertn != 0:
			ratio = data.lat3no3 / data.fertn
			if ratio < 0.21:
				data.warnings.nb.append("Nitrogen~Nitrate leaching is less than 21% of the applied fertilizer.")
			elif ratio > 0.38:
				data.warnings.nb.append("Nitrogen~Nitrate leaching is greater is more than 38% of the applied fertilizer, may indicate a problem.")

		if data.precip < 65:
			data.warnings.wb.append(f"Precipitation may be too low ({data.precip:.2f} < 65 mm)")
		elif data.precip > 3400:
			data.warnings.wb.append(f"Precipitation seems too high ({data.precip:.2f}) > 3400 mm")

		if data.et > data.precip:
			data.warnings.wb.append("ET Greater than precipitation; may indicate a problem unless irrigated")

		eWaterYield = 0.26 * data.precip
		eET = 0.74 * data.precip
		ratio_ = 0.0129 * data.cn - 0.2857
		eSurq = ratio_ * eWaterYield

		if do_water_yield_warnings and eWaterYield != 0:
			ratio_ = totalFlow / eWaterYield
			if ratio_ > 1.5:
				data.warnings.wb.append("Water yield may be excessive")
			elif ratio_ < 0.5:
				data.warnings.wb.append("Water yield may be too low")

		if eSurq != 0:
			ratio_ = data.surq_gen / eSurq
			if ratio_ > 1.5:
				data.warnings.wb.append("Surface runoff may be excessive")
			elif ratio_ < 0.5:
				data.warnings.wb.append("Surface runoff may be too low")
		
	def get_landuse_data(self, hru_data_lookup):
		# init data by landuse
		landuse_data = {}
		weighted_landuse_data = {}
		for landuse, hrus in groupby(hru_data_lookup, lambda x: x.landuse):
			item = check_toolbox.CheckToolboxLanduseData()
			item.hrus = list(hrus)
			item.area = sum([h.area for h in item.hrus])
			item.data = check_toolbox.CheckToolboxData()
			landuse_data[landuse] = item
			weighted_landuse_data[landuse] = check_toolbox.CheckToolboxData()

		hru_lookup = {hru.name: hru for hru in hru_data_lookup}

		for row in losses.Hru_ls_aa.select():
			match = hru_lookup.get(row.name)
			if match is not None:
				landuse = match.landuse
				data = weighted_landuse_data.get(landuse)
				if data is not None:
					weighted_landuse_data[landuse].lat3no3 += row.lat3no3 * match.area
					weighted_landuse_data[landuse].sedorgp += row.sedorgp * match.area
					weighted_landuse_data[landuse].sedorgn += row.sedorgn * match.area
					weighted_landuse_data[landuse].surqno3 += row.surqno3 * match.area
					weighted_landuse_data[landuse].surqsolp += row.surqsolp * match.area

		for row in plantwx.Hru_pw_aa.select():
			match = hru_lookup.get(row.name)
			if match is not None:
				landuse = match.landuse
				data = weighted_landuse_data.get(landuse)
				if data is not None:
					weighted_landuse_data[landuse].lai += row.lai * match.area
					weighted_landuse_data[landuse].bioms += row.bioms * match.area
					weighted_landuse_data[landuse].yield_val += row.yld * match.area
					weighted_landuse_data[landuse].residue += row.residue * match.area
					weighted_landuse_data[landuse].strsw += row.strsw * match.area
					weighted_landuse_data[landuse].strsa += row.strsa * match.area
					weighted_landuse_data[landuse].strstmp += row.strstmp * match.area
					weighted_landuse_data[landuse].strsn += row.strsn * match.area
					weighted_landuse_data[landuse].strsp += row.strsp * match.area
					weighted_landuse_data[landuse].nplt += row.nplt * match.area
					weighted_landuse_data[landuse].percn += row.percn * match.area
					weighted_landuse_data[landuse].pplnt += row.pplnt * match.area

		for row in nutbal.Hru_nb_aa.select():
			match = hru_lookup.get(row.name)
			if match is not None:
				landuse = match.landuse
				data = weighted_landuse_data.get(landuse)
				if data is not None:
					weighted_landuse_data[landuse].grzn += row.grzn * match.area
					weighted_landuse_data[landuse].grzp += row.grzp * match.area
					weighted_landuse_data[landuse].lab_min_p += row.lab_min_p * match.area
					weighted_landuse_data[landuse].act_sta_p += row.act_sta_p * match.area
					weighted_landuse_data[landuse].fertn += row.fertn * match.area
					weighted_landuse_data[landuse].fertp += row.fertp * match.area
					weighted_landuse_data[landuse].fixn += row.fixn * match.area
					weighted_landuse_data[landuse].denit += row.denit * match.area
					weighted_landuse_data[landuse].act_nit_n += row.act_nit_n * match.area
					weighted_landuse_data[landuse].act_sta_n += row.act_sta_n * match.area
					weighted_landuse_data[landuse].org_lab_p += row.org_lab_p * match.area
					weighted_landuse_data[landuse].rsd_nitorg_n += row.rsd_nitorg_n * match.area
					weighted_landuse_data[landuse].rsd_laborg_p += row.rsd_laborg_p * match.area
					weighted_landuse_data[landuse].no3atmo += row.no3atmo * match.area
					weighted_landuse_data[landuse].nh4atmo += row.nh4atmo * match.area
					weighted_landuse_data[landuse].nuptake += row.nuptake * match.area
					weighted_landuse_data[landuse].puptake += row.puptake * match.area

		for row in waterbal.Hru_wb_aa.select():
			match = hru_lookup.get(row.name)
			if match is not None:
				landuse = match.landuse
				data = weighted_landuse_data.get(landuse)
				if data is not None:
					weighted_landuse_data[landuse].precip += row.precip * match.area
					weighted_landuse_data[landuse].surq_gen += row.surq_gen * match.area
					weighted_landuse_data[landuse].latq += row.latq * match.area
					weighted_landuse_data[landuse].wateryld += row.wateryld * match.area
					weighted_landuse_data[landuse].perc += row.perc * match.area
					weighted_landuse_data[landuse].et += row.et * match.area
					weighted_landuse_data[landuse].eplant += row.eplant * match.area
					weighted_landuse_data[landuse].esoil += row.esoil * match.area
					weighted_landuse_data[landuse].cn += row.cn * match.area
					weighted_landuse_data[landuse].sw_init += row.sw_init * match.area
					weighted_landuse_data[landuse].sw_final += row.sw_final * match.area
					weighted_landuse_data[landuse].pet += row.pet * match.area
					weighted_landuse_data[landuse].qtile += row.qtile * match.area
					weighted_landuse_data[landuse].irr += row.irr * match.area

		for landuse, item in landuse_data.items():
			item.data.lat3no3 = weighted_landuse_data[landuse].lat3no3 / item.area if item.area != 0 else 0
			item.data.sedorgp = weighted_landuse_data[landuse].sedorgp / item.area if item.area != 0 else 0
			item.data.sedorgn = weighted_landuse_data[landuse].sedorgn / item.area if item.area != 0 else 0
			item.data.surqno3 = weighted_landuse_data[landuse].surqno3 / item.area if item.area != 0 else 0
			item.data.surqsolp = weighted_landuse_data[landuse].surqsolp / item.area if item.area != 0 else 0

			item.data.lai = weighted_landuse_data[landuse].lai / item.area if item.area != 0 else 0
			item.data.bioms = weighted_landuse_data[landuse].bioms / item.area if item.area != 0 else 0
			item.data.yield_val = weighted_landuse_data[landuse].yield_val / item.area if item.area != 0 else 0
			item.data.residue = weighted_landuse_data[landuse].residue / item.area if item.area != 0 else 0
			item.data.strsw = weighted_landuse_data[landuse].strsw / item.area if item.area != 0 else 0
			item.data.strsa = weighted_landuse_data[landuse].strsa / item.area if item.area != 0 else 0
			item.data.strstmp = weighted_landuse_data[landuse].strstmp / item.area if item.area != 0 else 0
			item.data.strsn = weighted_landuse_data[landuse].strsn / item.area if item.area != 0 else 0
			item.data.strsp = weighted_landuse_data[landuse].strsp / item.area if item.area != 0 else 0
			item.data.nplt = weighted_landuse_data[landuse].nplt / item.area if item.area != 0 else 0
			item.data.percn = weighted_landuse_data[landuse].percn / item.area if item.area != 0 else 0
			item.data.pplnt = weighted_landuse_data[landuse].pplnt / item.area if item.area != 0 else 0

			item.data.grzn = weighted_landuse_data[landuse].grzn / item.area if item.area != 0 else 0
			item.data.grzp = weighted_landuse_data[landuse].grzp / item.area if item.area != 0 else 0
			item.data.lab_min_p = weighted_landuse_data[landuse].lab_min_p / item.area if item.area != 0 else 0
			item.data.act_sta_p = weighted_landuse_data[landuse].act_sta_p / item.area if item.area != 0 else 0
			item.data.fertn = weighted_landuse_data[landuse].fertn / item.area if item.area != 0 else 0
			item.data.fertp = weighted_landuse_data[landuse].fertp / item.area if item.area != 0 else 0
			item.data.fixn = weighted_landuse_data[landuse].fixn / item.area if item.area != 0 else 0
			item.data.denit = weighted_landuse_data[landuse].denit / item.area if item.area != 0 else 0
			item.data.act_nit_n = weighted_landuse_data[landuse].act_nit_n / item.area if item.area != 0 else 0
			item.data.act_sta_n = weighted_landuse_data[landuse].act_sta_n / item.area if item.area != 0 else 0
			item.data.org_lab_p = weighted_landuse_data[landuse].org_lab_p / item.area if item.area != 0 else 0
			item.data.rsd_nitorg_n = weighted_landuse_data[landuse].rsd_nitorg_n / item.area if item.area != 0 else 0
			item.data.rsd_laborg_p = weighted_landuse_data[landuse].rsd_laborg_p / item.area if item.area != 0 else 0
			item.data.no3atmo = weighted_landuse_data[landuse].no3atmo / item.area if item.area != 0 else 0
			item.data.nh4atmo = weighted_landuse_data[landuse].nh4atmo / item.area if item.area != 0 else 0
			item.data.nuptake = weighted_landuse_data[landuse].nuptake / item.area if item.area != 0 else 0
			item.data.puptake = weighted_landuse_data[landuse].puptake / item.area if item.area != 0 else 0	

			item.data.precip = weighted_landuse_data[landuse].precip / item.area if item.area != 0 else 0
			item.data.surq_gen = weighted_landuse_data[landuse].surq_gen / item.area if item.area != 0 else 0
			item.data.latq = weighted_landuse_data[landuse].latq / item.area if item.area != 0 else 0
			item.data.wateryld = weighted_landuse_data[landuse].wateryld / item.area if item.area != 0 else 0
			item.data.perc = weighted_landuse_data[landuse].perc / item.area if item.area != 0 else 0
			item.data.et = weighted_landuse_data[landuse].et / item.area if item.area != 0 else 0
			item.data.eplant = weighted_landuse_data[landuse].eplant / item.area if item.area != 0 else 0
			item.data.esoil = weighted_landuse_data[landuse].esoil / item.area if item.area != 0 else 0
			item.data.cn = weighted_landuse_data[landuse].cn / item.area if item.area != 0 else 0
			item.data.sw_init = weighted_landuse_data[landuse].sw_init / item.area if item.area != 0 else 0
			item.data.sw_final = weighted_landuse_data[landuse].sw_final / item.area if item.area != 0 else 0
			item.data.pet = weighted_landuse_data[landuse].pet / item.area if item.area != 0 else 0
			item.data.qtile = weighted_landuse_data[landuse].qtile / item.area if item.area != 0 else 0
			item.data.irr = weighted_landuse_data[landuse].irr / item.area if item.area != 0 else 0

			self.set_common_data(item.data)

		return landuse_data