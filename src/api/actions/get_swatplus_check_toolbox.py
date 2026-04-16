from helpers.executable_api import ExecutableApi, Unbuffered
from peewee import *

from database.project.setup import SetupProjectDatabase
from database.output.setup import SetupOutputDatabase
from database.output import check_toolbox, aquifer, channel, hyd, losses, misc, nutbal, plantwx, reservoir, waterbal, pest, base
from database.project import connect, climate, gis, regions, simulation, hru_parm_db, config
from database import lib
from helpers import utils

import traceback
import json, sys, argparse
from itertools import groupby
from datetime import date


class GetSwatplusCheckToolbox(ExecutableApi):
	def __init__(self, project_db_file, output_db_file, save_to_file=None):
		self.output_db_file = output_db_file.replace("\\","/")
		self.project_db_file = project_db_file.replace("\\","/")
		self.save_to_file = None if save_to_file is None else save_to_file.replace("\\","/")

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
		pc = config.Project_config.get()
		use_gwflow = pc.use_gwflow == 1

		conn = lib.open_db(self.output_db_file)
		sys.stdout.write(self.output_db_file)
		for table in check_toolbox.required_tables:
			if not lib.exists_table(conn, table):
				conn.close()
				return json.dumps({'error': 'Output file "{}" does not exist in your output database. Re-run your model and check all yearly and average annual files under the print options, and keep the analyze output box checked.'.format(table)})
		
		unavailable_tables = []
		for table in check_toolbox.opt_tables:
			if not lib.exists_table(conn, table):
				unavailable_tables.append(table)
		conn.close()

		try:
			no_land_use_name = 'no land use'
			no_soil_name = 'no soil'

			#read HRUs
			hru_cons = connect.Hru_con.select().order_by(connect.Hru_con.id)
			hru_data_lookup = []
			available_landuses = []
			totalArea = 0
			i = 1
			for h in hru_cons:
				hru = check_toolbox.CheckToolboxHru()
				hru.name = h.name
				hru.area = h.area
				totalArea += h.area

				hru.landuse = no_land_use_name if h.hru.lu_mgt is None else h.hru.lu_mgt.name.replace('_lum', '')
				hru.soil = no_soil_name if h.hru.soil is None else h.hru.soil.name
				hru.index = i
				i += 1
				hru_data_lookup.append(hru)
				if hru.landuse not in available_landuses:
					available_landuses.append(hru.landuse)

			# read data from output database
			overall_data = self.get_overall_data(unavailable_tables, hru_data_lookup, totalArea)
			landuse_data = self.get_landuse_data(hru_data_lookup)
			overall_data.maxUplandSedYield = losses.Hru_ls_aa.select(fn.Max(losses.Hru_ls_aa.sedyld)).scalar()

			# set swat+ check sections
			info = self.get_info('project_config' not in unavailable_tables, use_gwflow, totalArea)

			# get plant list
			plant_desc_lookup = {p.name: utils.readable_name(p.description) for p in hru_parm_db.Plants_plt.select().order_by(hru_parm_db.Plants_plt.name)}
			urban_desc_lookup = {p.name: utils.readable_name(p.description) for p in hru_parm_db.Urban_urb.select().order_by(hru_parm_db.Urban_urb.name)}

			plant_options = []
			category_dict = {}
			for p in sorted(available_landuses):
				found_items = []
				d = ''
				if p in plant_desc_lookup:
					d = plant_desc_lookup[p]
					found_items = [item for item in check_toolbox.landuse_category_options if item.lower() in d.lower()]
				elif p in urban_desc_lookup:
					d = urban_desc_lookup[p]
					found_items = ['Urban']
				plant_options.append({'value': p, 'title': f"({p}) {d}" if p != no_land_use_name else no_land_use_name})
				if len(found_items) > 0:
					for cat in found_items:
						if cat not in category_dict:
							category_dict[cat] = []
						category_dict[cat].append(p)

			categories = []
			for cat in category_dict:
				if (len(category_dict[cat]) > 1):
					categories.append({
						'name': cat,
						'landuses': category_dict[cat]
					})
			
			if len(categories) > 0:
				categories = sorted(categories, key=lambda x: x['name'])
				categories.insert(0, { 'name': 'Any', 'landuses': [] })

			# read mgt_out data if available
			has_mgt = 'mgt_out' not in unavailable_tables
			hru_mgt = []
			hru_mgt_options = []
			if has_mgt:
				hru_lookup = {hru.index: hru for hru in hru_data_lookup}
				processed_hru_indices = set()  # Track which HRUs have been processed				

				mgt_out_data = base.Mgt_out.select().order_by(base.Mgt_out.hru, base.Mgt_out.year, base.Mgt_out.mon, base.Mgt_out.day)
				for hru_index, ops in groupby(mgt_out_data, lambda x: x.hru):
					hru = hru_lookup.get(hru_index)
					if hru is not None:
						processed_hru_indices.add(hru_index)
						mgts = []
						for op in ops:
							mgt = check_toolbox.CheckToolboxMgtItem()
							mgt.date = date(op.year, op.mon, op.day).isoformat()
							mgt.op = op.operation
							if op.operation == "PLANT":
								mgt.description = "Plant " + plant_desc_lookup[op.crop]
							elif op.operation == "HARV/KILL":
								mgt.description = "Harvest and kill\n" + plant_desc_lookup[op.crop]
							elif op.operation == "HARV":
								mgt.description = "Harvest " + plant_desc_lookup[op.crop]
							elif op.operation == "HARVEST":
								mgt.description = "Harvest " + plant_desc_lookup[op.crop]
							elif op.operation == "KILL":
								mgt.description = "Kill " + plant_desc_lookup[op.crop]
							elif op.operation == "IRRIGATE":
								mgt.description = "Irrigate"
							elif op.operation == "FERT":
								mgt.description = "Apply fertilizer"
							elif op.operation == "TILLAGE":
								mgt.description = f"Till ({plant_desc_lookup[op.crop]} option)"
							elif op.operation == "RESET WEIR":  
								mgt.description = f"Reset weir ({plant_desc_lookup[op.crop]}) to {round(op.soil_water, 2)}m"
							elif op.operation == "STOP PADDY":  
								mgt.description = "Stop paddy irrigation (set 0mm)"
							elif op.operation == "PADDY":
								mgt.description = f"Irrigate Paddy ({plant_desc_lookup[op.crop]})"
							elif op.operation == "BEGIN/ADJUST":
								mgt.description = f"Adjust paddy irrigation\nto {round(op.soil_water, 0)}mm"
							elif op.operation == "PUDDLE":
								mgt.description = "Puddle"
							elif op.operation == "TRANSPLANT":
								mgt.description = f"Transplant {plant_desc_lookup[op.crop]}"
							else:
								mgt.description = f"{op.operation} {op.crop}"
							mgts.append(mgt)

						hru_mgt_item = check_toolbox.CheckToolboxHruMgt()
						hru_mgt_item.name = hru.name
						hru_mgt_item.landuse = hru.landuse
						hru_mgt_item.soil = hru.soil
						hru_mgt_item.area = hru.area
						hru_mgt_item.index = hru.index
						hru_mgt_item.mgts = mgts
						hru_mgt.append(hru_mgt_item)
				
				"""for hru_index, hru in hru_lookup.items():
					if hru_index not in processed_hru_indices:
						hru_mgt_item = check_toolbox.CheckToolboxHruMgt()
						hru_mgt_item.name = hru.name
						hru_mgt_item.landuse = hru.landuse
						hru_mgt_item.soil = hru.soil
						hru_mgt_item.area = hru.area
						hru_mgt_item.index = hru.index
						hru_mgt_item.mgts = []  # Empty management list
						hru_mgt.append(hru_mgt_item)"""
				
				hru_mgt = sorted(hru_mgt, key=lambda x: x.index)
				hru_mgt_options = [{
						'value': hru.index, 
						'title': f"{hru.name} / {hru.landuse} / {hru.soil} / {hru.area:.2f} ha" + (f" (no mgt)" if len(hru.mgts) == 0 else '')
					} for hru in hru_mgt]

			SetupProjectDatabase.close()
			SetupOutputDatabase.close()

			landuse_list = []
			for key in landuse_data:
				landuse_list.append({
					'landuse': key,
					'data': landuse_data[key].data.toJson(),
					'area': landuse_data[key].area,
					'hruCount': len(landuse_data[key].hrus),
				})

			if self.save_to_file is not None:
				with open(self.save_to_file, 'w') as f:
					json.dump({
						'info': info.toJson(),
						'basin': overall_data.toJson(),
						'landuses': landuse_list,
						'mgt': [hru.toJson() for hru in hru_mgt],
						'mgtOptions': hru_mgt_options,
						'landuseOptions': plant_options,
						'landuseCategories': categories,
					}, f, indent=2)
				return json.dumps({'success': self.save_to_file})

			return json.dumps({
				'info': info.toJson(),
				'basin': overall_data.toJson(),
				'landuses': landuse_list,
				'mgt': [hru.toJson() for hru in hru_mgt],
				'mgtOptions': hru_mgt_options,
				'landuseOptions': plant_options,
				'landuseCategories': categories,
			})
		except Exception as ex:
			SetupProjectDatabase.close()
			SetupOutputDatabase.close()
			return json.dumps({'error': 'Error loading SWAT+ Check. Exception: {ex} {tb}'.format(ex=str(ex), tb=traceback.format_exc())})
		
	def set_common_data(self, data, is_overall=False):
		# derived metrics
		aqu_flo_cha = 0 if data.aqu_flo_cha is None else data.aqu_flo_cha
		totalFlow = aqu_flo_cha + data.latq + data.surq_gen
		if totalFlow != 0:			
			data.baseflowToTotal = (aqu_flo_cha + data.latq) / totalFlow
			data.surfaceflowToTotal = data.surq_gen / totalFlow

		if data.precip != 0:
			data.totalFlowToPrecip = totalFlow / data.precip
			data.etToPrecip = data.et / data.precip
			data.percoToPrecip = data.perc / data.precip
			data.seepToPrecip = None if data.aqu_seep is None else data.aqu_seep / data.precip

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
			data.warnings.nb_nitrogen.append('Denitrification is zero, consider decreasing SDNCO: (Denitrification threshold water content)')
		elif data.fertn != 0:
			calc = data.denit / data.fertn
			if calc < 0.01:
				data.warnings.nb_nitrogen.append('Denitrification is less than 2% of the applied fertilizer amount')
			elif calc > 0.4:
				data.warnings.nb_nitrogen.append('Denitrification is greater than 25% of the applied fertilizer amount')
		
		if data.fertn != 0:
			calc = data.nplt / data.fertn
			if calc < 0.5:
				data.warnings.nb_nitrogen.append('Crop is consuming less than half the amount of applied nitrogen')
				
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
			data.warnings.nb_nitrogen.append("Total nitrogen losses are greater than 40% of applied N")
		elif data.nLossesTotalLoss < 0.1 * data.fertn:
			data.warnings.nb_nitrogen.append("Total nitrogen losses are less than 8% of applied N, may be incorrect in agricultural areas. Likely fine in unmanaged areas or forest dominated watersheds.")

		if data.nLossesSurfaceRunoff > 4.7:
			data.warnings.nb_nitrogen.append("Nitrate losses in surface runoff may be high")
		elif data.nLossesSurfaceRunoff < 0.15:
			data.warnings.nb_nitrogen.append("Nitrate losses in surface runoff may be low")

		if data.nLossesOrgN > 33:
			data.warnings.nb_nitrogen.append("Organic/Particulate nitrogen losses in surface runoff may be high")
		elif data.nLossesOrgN < 0.3:
			data.warnings.nb_nitrogen.append("Organic/Particulate nitrogen losses in surface runoff may be low")

		if data.pLossesSurfaceRunoff > 1.2:
			data.warnings.nb_phosphorus.append("Soluble phosphorus losses in surface runoff may be high")
		elif data.pLossesSurfaceRunoff < 0.025:
			data.warnings.nb_phosphorus.append("Soluble phosphorus losses in surface runoff may be low")

		if data.pLossesOrgP > 14:
			data.warnings.nb_phosphorus.append("Organic/Particulate phosphorus losses in surface runoff may be high")
		elif data.pLossesOrgP < 0:
			data.warnings.nb_phosphorus.append("Organic/Particulate phosphorus losses in surface runoff may be low")

		if data.nLossesSolubilityRatio > 0.85:
			data.warnings.nb_nitrogen.append("Solubility ratio for nitrogen in runoff is high")
		elif data.nLossesSolubilityRatio < 0.1:
			data.warnings.nb_nitrogen.append("Solubility ratio for nitrogen in runoff is low")

		if data.pLossesSolubilityRatio > 0.95:
			data.warnings.nb_phosphorus.append("Solubility ratio for phosphorus in runoff is high, may be ok in uncultivated areas")
		elif data.pLossesSolubilityRatio < 0.13:
			data.warnings.nb_phosphorus.append("Solubility ratio for phosphorus in runoff is low, may indicate a problem")

		if data.lat3no3 > 50:
			data.warnings.nb_nitrogen.append("Nitrate leaching is greater than 50 kg/ha, may indicate a problem.")

		if data.fertn != 0:
			ratio = data.lat3no3 / data.fertn
			if ratio < 0.21:
				data.warnings.nb_nitrogen.append("Nitrate leaching is less than 21% of the applied fertilizer.")
			elif ratio > 0.38:
				data.warnings.nb_nitrogen.append("Nitrate leaching is greater is more than 38% of the applied fertilizer, may indicate a problem.")

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

		if eSurq != 0:
			ratio_ = data.surq_gen / eSurq
			if ratio_ > 1.5:
				data.warnings.wb.append("Surface runoff may be excessive")
			elif ratio_ < 0.5:
				data.warnings.wb.append("Surface runoff may be too low")			
			
		if is_overall:
			if eWaterYield != 0:
				ratio_ = totalFlow / eWaterYield
				if ratio_ > 1.5:
					data.warnings.wb.append("Water yield may be excessive")
				elif ratio_ < 0.5:
					data.warnings.wb.append("Water yield may be too low")

			if data.surfaceflowToTotal > 0.80:
				data.warnings.wb.append(f"'Surface Runoff' to 'Total Flow' ratio may be too high ({data.surfaceflowToTotal:.2f} > 0.8)")
			elif data.surfaceflowToTotal < 0.20:
				data.warnings.wb.append(f"'Surface Runoff' to 'Total Flow' ratio appears too low ({data.surfaceflowToTotal:.2f} < 0.2)")

			if data.aqu_flo_cha is not None and totalFlow != 0:
				gwqRatio = data.aqu_flo_cha / totalFlow
				if gwqRatio > 0.69:
					data.warnings.wb.append("Groundwater ratio may be high")
				elif gwqRatio < 0.22:
					data.warnings.wb.append("Groundwater ratio may be low")

			if data.aqu_flo_cha is not None and data.latq > data.aqu_flo_cha:
				data.warnings.wb.append("Lateral flow is greater than groundwater flow; may indicate a problem")

	def get_overall_data(self, unavailable_tables, hru_data_lookup, totalArea):
		overall_data = check_toolbox.CheckToolboxData()

		basin_wb_aa = waterbal.Basin_wb_aa.get_or_none()
		basin_aqu_aa = None if 'basin_aqu_aa' in unavailable_tables else aquifer.Basin_aqu_aa.get_or_none()
		basin_nb_aa = nutbal.Basin_nb_aa.get_or_none()
		basin_pw_aa = plantwx.Basin_pw_aa.get_or_none()
		basin_ls_aa = losses.Basin_ls_aa.get_or_none()
		basin_sd_cha_aa = channel.Basin_sd_cha_aa.get_or_none()
		has_recall = 'recall_aa' not in unavailable_tables
		basin_res_aa = None if 'basin_res_aa' in unavailable_tables else reservoir.Basin_res_aa.get_or_none()
		has_yr_res = 'reservoir_yr' not in unavailable_tables

		# surface
		overall_data.et = basin_wb_aa.et
		overall_data.pet = basin_wb_aa.pet
		overall_data.precip = basin_wb_aa.precip
		overall_data.snofall = basin_wb_aa.snofall
		overall_data.cn = basin_wb_aa.cn
		overall_data.surq_gen = basin_wb_aa.surq_gen
		overall_data.latq = basin_wb_aa.latq
		overall_data.irr = basin_wb_aa.irr
		overall_data.perc = basin_wb_aa.perc

		# aquifer
		if basin_aqu_aa is not None:
			overall_data.aqu_flo_cha = basin_aqu_aa.flo_cha
			overall_data.aqu_revap = basin_aqu_aa.revap
			overall_data.aqu_seep = basin_aqu_aa.seep
			overall_data.aqu_no3_lat = basin_aqu_aa.no3_lat
			overall_data.aqu_no3_seep = basin_aqu_aa.no3_seep
			overall_data.aqu_no3_rchg = basin_aqu_aa.no3_rchg

		# gather information about nutrients

		# read nitrogen
		overall_data.grzn = basin_nb_aa.grzn
		overall_data.grzp = basin_nb_aa.grzp
		overall_data.lab_min_p = basin_nb_aa.lab_min_p
		overall_data.act_sta_p = basin_nb_aa.act_sta_p
		overall_data.fertn = basin_nb_aa.fertn
		overall_data.fertp = basin_nb_aa.fertp
		overall_data.fixn = basin_nb_aa.fixn
		overall_data.denit = basin_nb_aa.denit
		overall_data.act_nit_n = basin_nb_aa.act_nit_n
		overall_data.act_sta_n = basin_nb_aa.act_sta_n
		overall_data.org_lab_p = basin_nb_aa.org_lab_p
		overall_data.rsd_nitorg_n = basin_nb_aa.rsd_nitorg_n
		overall_data.rsd_laborg_p = basin_nb_aa.rsd_laborg_p
		overall_data.no3atmo = basin_nb_aa.no3atmo
		overall_data.nh4atmo = basin_nb_aa.nh4atmo
		overall_data.nuptake = basin_nb_aa.nuptake
		overall_data.puptake = basin_nb_aa.puptake

		# read plant uptake of nitrogen
		overall_data.nplt = basin_pw_aa.nplt
		overall_data.pplnt = basin_pw_aa.pplnt
		overall_data.yield_val = basin_pw_aa.yld
		overall_data.bioms = basin_pw_aa.bioms
		# read stress days
		overall_data.strsw = basin_pw_aa.strsw
		overall_data.strsa = basin_pw_aa.strsa
		overall_data.strstmp = basin_pw_aa.strstmp
		overall_data.strsn = basin_pw_aa.strsn
		overall_data.strsp = basin_pw_aa.strsp

		# read sedorg nitrogen
		# ls stuff
		overall_data.lat3no3 = basin_ls_aa.lat3no3
		overall_data.sedorgp = basin_ls_aa.sedorgp
		overall_data.sedorgn = basin_ls_aa.sedorgn
		overall_data.surqno3 = basin_ls_aa.surqno3
		overall_data.surqsolp = basin_ls_aa.surqsolp
		overall_data.sedyld = basin_ls_aa.sedyld

		# issue warnings 
		overall_data.warnings = check_toolbox.CheckToolboxDataWarnings()
		self.set_common_data(overall_data, True)

		# channel sediment
		overall_data.sed_in = basin_sd_cha_aa.sed_in / totalArea
		overall_data.sed_out = basin_sd_cha_aa.sed_out / totalArea
		overall_data.sed_stor = basin_sd_cha_aa.sed_stor

		sed_chg = basin_sd_cha_aa.sed_out - basin_sd_cha_aa.sed_in
		overall_data.uplandSedYield = overall_data.sedyld * totalArea

		denom = overall_data.uplandSedYield + sed_chg
		if denom != 0 and sed_chg > 0:
			overall_data.chaErosion = (sed_chg / denom) * 100
			if overall_data.chaErosion > 50:
				overall_data.warnings.sed.append("More than 50% of sediment is from instream processes")

		if overall_data.uplandSedYield != 0 and sed_chg <= 0:
			overall_data.chaDeposition = sed_chg * -1 / overall_data.uplandSedYield * 100
			if overall_data.chaDeposition > 95:
				overall_data.warnings.sed.append("More than 95% of sediment is deposited instream")

		if overall_data.chaErosion == 0 and overall_data.chaDeposition == 0:
			overall_data.warnings.sed.append("No in-stream sediment modification; this is unusual")
		elif (overall_data.chaErosion > -2 and overall_data.chaErosion < 2) or (overall_data.chaDeposition > -2 and overall_data.chaDeposition < 2):
			overall_data.warnings.sed.append("Very little in-stream sediment modification (< +-2%); this is unusual")

		# point sources
		subLoad = check_toolbox.CheckToolboxPointSourcesLoad()
		psLoad = check_toolbox.CheckToolboxPointSourcesLoad()
		fromLoad = check_toolbox.CheckToolboxPointSourcesLoad()

		if channel.Channel_sd_aa.select().count() > 0:
			cha = channel.Channel_sd_aa.select().order_by(channel.Channel_sd_aa.flo_out.desc())[0]
			subLoad.flow = cha.flo_out / 365
			subLoad.sediment = cha.sed_out
			subLoad.nitrogen = cha.orgn_out + cha.no3_out + cha.nh3_out + cha.no2_out
			subLoad.phosphorus = cha.sedp_out + cha.solp_out

		if has_recall:
			ptable = hyd.Recall_aa
			if ptable.select().count() > 0:
				pts = ptable.select(fn.SUM(ptable.flo).alias('flow_total'), fn.SUM(ptable.sed).alias('sed_total'), fn.SUM(ptable.orgn).alias('orgn_total'), fn.SUM(ptable.sedp).alias('sedp_total'), fn.SUM(ptable.no3).alias('no3_total'), fn.SUM(ptable.nh3).alias('nh3_total'), fn.SUM(ptable.no2).alias('no2_total'), fn.SUM(ptable.solp).alias('solp_total')).get()
				psLoad.flow = pts.flow_total / 365
				psLoad.sediment = pts.sed_total
				psLoad.nitrogen = pts.orgn_total + pts.no3_total + pts.nh3_total + pts.no2_total
				psLoad.phosphorus = pts.sedp_total + pts.solp_total

		fromLoad.flow = 0 if subLoad.flow == 0 else psLoad.flow / (psLoad.flow + subLoad.flow) * 100
		fromLoad.sediment = 0 if subLoad.sediment == 0 else psLoad.sediment / (psLoad.sediment + subLoad.sediment) * 100
		fromLoad.nitrogen = 0 if subLoad.nitrogen == 0 else psLoad.nitrogen / (psLoad.nitrogen + subLoad.nitrogen) * 100
		fromLoad.phosphorus = 0 if subLoad.phosphorus == 0 else psLoad.phosphorus / (psLoad.phosphorus + subLoad.phosphorus) * 100

		ptsrc_warnings = []
		if fromLoad.flow > 30:
			ptsrc_warnings.append('Inlets/point sources contribute more than 30% of the total streamflow')
		if fromLoad.phosphorus > 55:
			ptsrc_warnings.append('Inlets/point sources contribute more than 55% of the total phosphorus')
		if fromLoad.nitrogen > 20:
			ptsrc_warnings.append('Inlets/point sources contribute more than 20% of the total nitrogen')
		if fromLoad.sediment > 30:
			ptsrc_warnings.append('Inlets/point sources contribute more than 30% of the total sediment')

		if psLoad.flow == 0 and psLoad.sediment > 0:
			ptsrc_warnings.append('Inlets/point sources contribute sediment but not flow, error likely')
		if psLoad.flow == 0 and psLoad.phosphorus > 0:
			ptsrc_warnings.append('Inlets/point sources contribute phosphorus but not flow, error likely')
		if psLoad.flow == 0 and psLoad.nitrogen > 0:
			ptsrc_warnings.append('Inlets/point sources contribute nitrogen but not flow, error likely')

		if psLoad.flow > 0 and psLoad.sediment == 0:
			ptsrc_warnings.append('Inlets/point sources contribute flow, but not sediment')
		if psLoad.flow > 0 and psLoad.phosphorus == 0:
			ptsrc_warnings.append('Inlets/point sources contribute flow, but not phosphorus')
		if psLoad.flow > 0 and psLoad.nitrogen == 0:
			ptsrc_warnings.append('Inlets/point sources contribute flow, but not nitrogen')

		if psLoad.flow == 0 and psLoad.nitrogen == 0 and psLoad.phosphorus == 0 and psLoad.sediment == 0:
			ptsrc_warnings.append('Inlets/point source not present')

		if psLoad.phosphorus > 0:
			if psLoad.nitrogen / psLoad.phosphorus > 8.8:
				ptsrc_warnings.append('Inlets/point sources N:P ratio greater than 8.8')
			elif psLoad.nitrogen / psLoad.phosphorus < 2.8:
				ptsrc_warnings.append('Inlets/point sources N:P ratio less than 2.8')

		overall_data.subbasinLoad = subLoad
		overall_data.pointSourceInletLoad = psLoad
		overall_data.fromInletAndPointSource = fromLoad
		overall_data.warnings.ptsrc = ptsrc_warnings

		# reservoirs
		if basin_res_aa is None:
			overall_data.warnings.res.append('No reservoir data available.')
		else:
			basin_n_in = basin_res_aa.orgn_in + basin_res_aa.no3_in + basin_res_aa.no2_in + basin_res_aa.nh3_in
			basin_n_out = basin_res_aa.orgn_out + basin_res_aa.no3_out + basin_res_aa.no2_out + basin_res_aa.nh3_out
			basin_p_in = basin_res_aa.sedp_in + basin_res_aa.solp_in
			basin_p_out = basin_res_aa.sedp_out + basin_res_aa.solp_out

			overall_data.avgTrappingEfficiencies.sediment = self.get_in_out_percent(basin_res_aa.sed_in, basin_res_aa.sed_out)
			overall_data.avgTrappingEfficiencies.nitrogen = self.get_in_out_percent(basin_n_in, basin_n_out)
			overall_data.avgTrappingEfficiencies.phosphorus = self.get_in_out_percent(basin_p_in, basin_p_out)

			overall_data.avgWaterLosses.totalRemoved = self.get_in_out_percent(basin_res_aa.flo_in, basin_res_aa.flo_out)
			overall_data.avgWaterLosses.seepage = 0 if basin_res_aa.flo_stor == 0 else basin_res_aa.seep / basin_res_aa.flo_stor * 100
			overall_data.avgWaterLosses.evaporation = 0 if basin_res_aa.flo_stor == 0 else basin_res_aa.evap / basin_res_aa.flo_stor * 100

			num_yrs = 0
			init_yr = 0
			final_yr = 0
			if has_yr_res:
				res_yrs = reservoir.Reservoir_yr.select().where(reservoir.Reservoir_yr.unit == 1).order_by(reservoir.Reservoir_yr.yr)
				num_yrs = res_yrs.count()
				if (num_yrs > 0):
					init_yr = res_yrs[0].yr
					final_yr = res_yrs[num_yrs - 1].yr


			res_list = reservoir.Reservoir_aa.select()
			overall_data.avgReservoirTrends.numberReservoirs = res_list.count()

			per_res_warns = [None] * 9
			ratios = []
			empty_vols = []
			for r in res_list:
				n_in = r.orgn_in + r.no3_in + r.no2_in + r.nh3_in
				n_out = r.orgn_out + r.no3_out + r.no2_out + r.nh3_out
				p_in = r.sedp_in + r.solp_in
				p_out = r.sedp_out + r.solp_out

				row = check_toolbox.CheckReservoirRow()
				row.id = r.name
				row.sediment = self.get_in_out_percent(r.sed_in, r.sed_out)
				row.phosphorus = self.get_in_out_percent(p_in, p_out)
				row.nitrogen = self.get_in_out_percent(n_in, n_out)
				row.seepage = 0 if r.flo_stor == 0 else r.seep / r.flo_stor * 100
				row.evapLoss = 0 if r.flo_stor == 0 else r.evap / r.flo_stor * 100

				row.volumeRatio = 'NA'
				row.fractionEmpty = 'NA'
				if has_yr_res:
					init_vol = reservoir.Reservoir_yr.select().where((reservoir.Reservoir_yr.unit == r.unit) & (reservoir.Reservoir_yr.yr == init_yr)).get().flo_stor
					final_vol = reservoir.Reservoir_yr.select().where((reservoir.Reservoir_yr.unit == r.unit) & (reservoir.Reservoir_yr.yr == final_yr)).get().flo_stor
					empty_vol_count = reservoir.Reservoir_yr.select().where((reservoir.Reservoir_yr.unit == r.unit) & (reservoir.Reservoir_yr.flo_stor < 1)).count()

					ratio = 0 if init_vol == 0 else final_vol / init_vol
					empty_frac = 0 if num_yrs == 0 else empty_vol_count / num_yrs

					row.volumeRatio = ratio
					row.fractionEmpty = empty_frac
					ratios.append(ratio)
					empty_vols.append(empty_frac)

				overall_data.reservoirRows.append(row)

				if row.sediment < 40:
					per_res_warns[0] = 'Sediment trapping efficiency less than 40% at one or more reservoirs'
				if row.sediment > 98:
					per_res_warns[1] = 'Sediment trapping efficiency greater than 98% at one or more reservoirs'

				if row.nitrogen< 7:
					per_res_warns[2] = 'Nitrogen trapping efficiency less than 7% at one or more reservoirs'
				if row.nitrogen > 72:
					per_res_warns[3] = 'Nitrogen trapping efficiency greater than 72% at one or more reservoirs'

				if row.phosphorus < 18:
					per_res_warns[4] = 'Phosphorus trapping efficiency less than 18% at one or more reservoirs'
				if row.phosphorus > 82:
					per_res_warns[5] = 'Phosphorus trapping efficiency greater than 82% at one or more reservoirs'

				if row.evapLoss < 5:
					per_res_warns[6] = 'Evaporation losses are less than 2% at one or more reservoirs'
				if row.evapLoss > 50:
					per_res_warns[7] = 'Evaporation losses are more than 30% at one or more reservoirs'

				if row.seepage > 25:
					per_res_warns[8] = 'Seepage losses are more than 10% at one or more reservoirs'

			for w in per_res_warns:
				if w is not None:
					overall_data.warnings.res.append(w)
			
			if has_yr_res:
				overall_data.avgReservoirTrends.fractionEmpty = max(empty_vols)
				overall_data.avgReservoirTrends.maxVolume = max(ratios)
				overall_data.avgReservoirTrends.minVolume = min(ratios)

				if overall_data.avgReservoirTrends.fractionEmpty > 0:
					overall_data.warnings.res.append('At least one of your reservoirs has become complexly dry during the simulation')
				if overall_data.avgReservoirTrends.maxVolume > 5:
					overall_data.warnings.res.append('At least one of your reservoirs ends the simulation with at least 500% more volume that it begins with. Check your release parameters.')
				if overall_data.avgReservoirTrends.minVolume > 0.2:
					overall_data.warnings.res.append('At least one of your reservoirs ends the simulation with less than 20% volume that it begins with. Check your release parameters.')
			
		return overall_data
	
	def get_in_out_percent(self, value_in, value_out):
		return 0 if value_in == 0 else (value_in - value_out) / value_in * 100

	def get_landuse_data(self, hru_data_lookup):
		# init data by landuse
		landuse_data = {}
		weighted_landuse_data = {}
		sorted_hru_data = sorted(hru_data_lookup, key=lambda x: x.landuse)
		for landuse, hrus in groupby(sorted_hru_data, lambda x: x.landuse):
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
	
	def get_info(self, has_project_config, use_gwflow, hruArea):
		info = check_toolbox.CheckToolboxInfo()

		time_sim = simulation.Time_sim.get_or_none()
		if time_sim is not None:
			info.simulationLength = time_sim.yrc_end - time_sim.yrc_start + 1

		prt = simulation.Print_prt.get_or_none()
		if prt is not None:
			info.warmUp = prt.nyskip

		info.hrus = connect.Hru_con.select().count()
		info.subbasins = gis.Gis_subbasins.select().count()
		info.lsus = regions.Ls_unit_def.select().count()
		info.weatherMethod = 'Observed' if climate.Weather_sta_cli.observed_count() > 0 else 'Simulated'
		info.watershedArea = connect.Rout_unit_con.select(fn.Sum(connect.Rout_unit_con.area)).scalar()
		info.gwflow = use_gwflow
		info.hruTotalArea = hruArea

		if has_project_config:
			pc = base.Project_config.get_or_none()
			if pc is not None:
				info.swatVersion = pc.swat_version

		return info
	