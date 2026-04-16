<script setup lang="ts">
	import { reactive, watch, onMounted, computed } from 'vue';
	import { useRoute } from 'vue-router';
	import { useTheme, useDisplay } from 'vuetify';
	import { useHelpers } from '@/helpers';
	import SwatPlusToolboxButton from '../components/SwatPlusToolboxButton.vue';
	import SwatPlusIahrisButton from '../components/SwatPlusIahrisButton.vue';
	import ImageOverlays from '../components/ImageOverlays.vue';
	
	const route = useRoute();
	const theme = useTheme();
	const { api, constants, errors, formatters, runProcess, utilities, currentProject } = useHelpers();

	let data = reactive({
		page: {
			loading: false,
			error: <string|null>null,
			tabIndex: 0,
			tabs: [
				"Overview",
				"Hydrology",
                "Nutrients",
				"Sediment",
				"Plants",
				"Point Sources",
				"Reservoirs"
			],
			checkByLanduse: false,
			/*selectedLanduse: <string|null>null,
			selectedArea: 0,
			selectedHruCount: 0,*/
			selectedLandusesInput: [] as string[],
			selectedLanduses: [] as {
				landuse: string;
				area: number;
				hruCount: number;
			}[],
			isOverall: true,
			nutrientsTab: 'nitrogen',
			selectedHruIndex: <number|null>null,
			selectedCategory: 'Any',
		},
		modals: {
			reservoirs: false,
		},
		config: {
			input_files_dir: '',
			input_files_last_written: '',
			swat_last_run: '',
			output_last_imported: ''
		},
		check: <any>{
			info: {},
			basin: <CheckToolboxData>{},
			landuses: [] as {
				landuse: string;
				area: number;
				hruCount: number;
				data: CheckToolboxData;
			}[],
			mgt: [],
			mgtOptions: [],
			landuseOptions: [],
			landuseCategories: [],
		},
        simulationWarnings: <string[]>[]
	});

	const currentResultsPath = computed(() => {
		return runProcess.resultsPath(data.config.input_files_dir);
	});

	async function get() {
		data.page.loading = true;
		data.page.error = null;

		try {
			const response = await api.get(`setup/run-settings`, currentProject.getApiHeader());
			errors.log(response.data);
			data.config = response.data.config;

			if (!formatters.isNullOrEmpty(data.config.output_last_imported)) {
				let outputDb = runProcess.outputDbPath(data.config.input_files_dir);
				let formData = {
					'output_db': outputDb
				}
				const response2 = await api.put(`setup/swatplus-check-toolbox`, formData, currentProject.getApiHeader());
				errors.log(response2.data);

				if (response2.data.error) {
					data.page.error = response2.data.error;
				} else {
					data.check = response2.data;

					if (!response.data.has_observed_weather) {
						data.simulationWarnings.push('You are using simulated precipitation data; if you intend to calibrate, you should used measured precipitation data');
					}

					if (response.data.print.prt.nyskip < 1) {
						data.simulationWarnings.push('It is highly recomended that you use at least 1 year of model warmup; 2-5 years is better');
					}

					if (data.check.info.swatVersion === 'development') {
						data.check.info.swatVersion = constants.appSettings.swatplus;
					}
				}
			}
		} catch (error) {
			data.page.error = errors.logError(error, 'Unable to get SWAT+ Check data from database.');
		}
		
		data.page.loading = false;
	}

	function nextTab(position:number) {
		let maxTabPos = data.page.tabs.length - 1;
		data.page.tabIndex += position;

		if (data.page.tabIndex > maxTabPos)
			data.page.tabIndex = 0;
		if (data.page.tabIndex < 0)
			data.page.tabIndex = maxTabPos;
	}

	const canLoad = computed(() => {
		return !currentProject.isLte && formatters.isNullOrEmpty(data.page.error) && !formatters.isNullOrEmpty(data.config.output_last_imported);
	})

	function setLanduseInCategory() {
		if (data.page.selectedCategory === 'Any') {
			data.page.selectedLandusesInput = [];
			return;
		}

		let matches = data.check.landuseCategories.filter((c:any) => c.name === data.page.selectedCategory);
		if (matches.length > 0) {
			data.page.selectedLandusesInput = matches[0].landuses;
		}
	}

	const selectedData = computed(() => {
		data.page.selectedLanduses = [];
		data.page.isOverall = true;

		if (data.page.checkByLanduse && !formatters.isNullOrEmpty(data.page.selectedLandusesInput)) {
			let matches = data.check.landuses.filter((l:any) => data.page.selectedLandusesInput.includes(l.landuse));
			if (matches.length > 0) {
				for (let m of matches) {
					data.page.selectedLanduses.push({
						landuse: m.landuse,
						area: m.area,
						hruCount: m.hruCount
					});
				}
				data.page.isOverall = false;
				return computeWeightedData(matches);
			}
		}

		return data.check.basin;
	})

	function computeWeightedData(matches:{
		landuse: string;
		area: number;
		hruCount: number;
		data: CheckToolboxData;
	}[]) {
		let weightedAverage:CheckToolboxData = {
			// wb_basin
			precip: 0,
			snofall: 0,
			surq_gen: 0,
			latq: 0,
			wateryld: 0,
			perc: 0,
			sw_init: 0,
			sw_final: 0,
			et: 0,
			eplant: 0,
			esoil: 0,
			cn: 0,
			pet: 0,
			qtile: 0,
			irr: 0,
			surq_cha: 0,
			surq_res: 0,
			latq_cha: 0,
			latq_res: 0,
			
			// aqu_basin
			aqu_flo: 0,
			aqu_dep_wt: 0,
			aqu_stor: 0,
			aqu_rchrg: 0,
			aqu_seep: 0,
			aqu_revap: 0,
			aqu_flo_cha: 0,
			aqu_flo_res: 0,
			aqu_flo_ls: 0,
			aqu_no3_lat: 0,
			aqu_no3_seep: 0,
			aqu_no3_rchg: 0,
			
			// pw
			lai: 0,
			bioms: 0,
			yield_val: 0,
			residue: 0,
			pplnt: 0,
			nplt: 0,
			
			// stress days
			strsw: 0,
			strsa: 0,
			strstmp: 0,
			strsn: 0,
			strsp: 0,
			
			// nb
			percn: 0,
			grzn: 0,
			grzp: 0,
			lab_min_p: 0,
			act_sta_p: 0,
			fertn: 0,
			fertp: 0,
			fixn: 0,
			denit: 0,
			act_nit_n: 0,
			act_sta_n: 0,
			org_lab_p: 0,
			rsd_nitorg_n: 0,
			rsd_laborg_p: 0,
			no3atmo: 0,
			nh4atmo: 0,
			nuptake: 0,
			puptake: 0,
			
			initialNO3: null,
			finalNO3: null,
			initialOrgN: null,
			finalOrgN: null,
			volatilization: null,
			nitrification: null,
			mineralization: null,
			
			// ls
			sedorgn: 0,
			sedorgp: 0,
			sedyld: 0,
			lat3no3: 0,
			surqno3: 0,
			surqsolp: 0,
			uplandSedYield: 0,
			maxUplandSedYield: 0,
			chaErosion: 0,
			chaDeposition: 0,
			
			// derived
			nLossesTotalLoss: 0,
			nLossesOrgN: 0,
			nLossesSurfaceRunoff: 0,
			nLossesLateralFlow: 0,
			totalN: 0,
			nLossesSolubilityRatio: 0,
			pLossesTotalLoss: 0,
			pLossesOrgP: 0,
			pLossesSurfaceRunoff: 0,
			pLossesSolubilityRatio: 0,
			
			// cha stuff
			sed_in: 0,
			sed_out: 0,
			sed_stor: 0,
			
			// ratios
			baseflowToTotal: 0,
			surfaceflowToTotal: 0,
			totalFlowToPrecip: 0,
			etToPrecip: 0,
			percoToPrecip: 0,
			seepToPrecip: 0,

			//point sources
			subbasinLoad: {} as CheckToolboxPointSourcesLoad,
			pointSourceInletLoad: {} as CheckToolboxPointSourcesLoad,
			fromInletAndPointSource: {} as CheckToolboxPointSourcesLoad,

			// reservoirs
			reservoirRows: [] as CheckReservoirRow[],
			avgTrappingEfficiencies: {} as CheckAvgTrappingEfficiency,
			avgWaterLosses: {} as CheckAvgWaterLoss,
			avgReservoirTrends: {} as CheckAvgReservoirTrend,

			// warnings
			warnings: {
				plants: [],
				nb_nitrogen: [],
				nb_phosphorus: [],
				wb: [],
				sed: [],
				ptsrc: [],
				res: [],
			}
		};

		let totalArea = 0;
		for (let m of matches) {
			totalArea += m.area;
		}

		if (totalArea === 0) return weightedAverage;

		for (let m of matches) {
			let item = m.data;
			let weight = m.area / totalArea;
			// wb_basin
			weightedAverage.precip += item.precip * weight;
			weightedAverage.snofall += item.snofall * weight;
			weightedAverage.surq_gen += item.surq_gen * weight;
			weightedAverage.latq += item.latq * weight;
			weightedAverage.wateryld += item.wateryld * weight;
			weightedAverage.perc += item.perc * weight;
			weightedAverage.sw_init += item.sw_init * weight;
			weightedAverage.sw_final += item.sw_final * weight;
			weightedAverage.et += item.et * weight;
			weightedAverage.eplant += item.eplant * weight;
			weightedAverage.esoil += item.esoil * weight;
			weightedAverage.cn += item.cn * weight;
			weightedAverage.pet += item.pet * weight;
			weightedAverage.qtile += item.qtile * weight;
			weightedAverage.irr += item.irr * weight;
			weightedAverage.surq_cha += item.surq_cha * weight;
			weightedAverage.surq_res += item.surq_res * weight;
			weightedAverage.latq_cha += item.latq_cha * weight;
			weightedAverage.latq_res += item.latq_res * weight;

			// aqu_basin
			weightedAverage.aqu_flo += item.aqu_flo * weight;
			weightedAverage.aqu_dep_wt += item.aqu_dep_wt * weight;
			weightedAverage.aqu_stor += item.aqu_stor * weight;
			weightedAverage.aqu_rchrg += item.aqu_rchrg * weight;
			weightedAverage.aqu_seep += item.aqu_seep * weight;
			weightedAverage.aqu_revap += item.aqu_revap * weight;
			weightedAverage.aqu_flo_cha += item.aqu_flo_cha * weight;
			weightedAverage.aqu_flo_res += item.aqu_flo_res * weight;
			weightedAverage.aqu_flo_ls += item.aqu_flo_ls * weight;
			weightedAverage.aqu_no3_lat += item.aqu_no3_lat * weight;
			weightedAverage.aqu_no3_seep += item.aqu_no3_seep * weight;
			weightedAverage.aqu_no3_rchg += item.aqu_no3_rchg * weight;

			// pw
			weightedAverage.lai += item.lai * weight;
			weightedAverage.bioms += item.bioms * weight;
			weightedAverage.yield_val += item.yield_val * weight;
			weightedAverage.residue += item.residue * weight;
			weightedAverage.pplnt += item.pplnt * weight;
			weightedAverage.nplt += item.nplt * weight;

			// stress days
			weightedAverage.strsw += item.strsw * weight;
			weightedAverage.strsa += item.strsa * weight;
			weightedAverage.strstmp += item.strstmp * weight;
			weightedAverage.strsn += item.strsn * weight;
			weightedAverage.strsp += item.strsp * weight;

			// nb
			weightedAverage.percn += item.percn * weight;
			weightedAverage.grzn += item.grzn * weight;
			weightedAverage.grzp += item.grzp * weight;
			weightedAverage.lab_min_p += item.lab_min_p * weight;
			weightedAverage.act_sta_p += item.act_sta_p * weight;
			weightedAverage.fertn += item.fertn * weight;
			weightedAverage.fertp += item.fertp * weight;
			weightedAverage.fixn += item.fixn * weight;
			weightedAverage.denit += item.denit * weight;
			weightedAverage.act_nit_n += item.act_nit_n * weight;
			weightedAverage.act_sta_n += item.act_sta_n * weight;
			weightedAverage.org_lab_p += item.org_lab_p * weight;
			weightedAverage.rsd_nitorg_n += item.rsd_nitorg_n * weight;
			weightedAverage.rsd_laborg_p += item.rsd_laborg_p * weight;
			weightedAverage.no3atmo += item.no3atmo * weight;
			weightedAverage.nh4atmo += item.nh4atmo * weight;
			weightedAverage.nuptake += item.nuptake * weight;
			weightedAverage.puptake += item.puptake * weight;

			// ls
			weightedAverage.sedorgn += item.sedorgn * weight;
			weightedAverage.sedorgp += item.sedorgp * weight;
			weightedAverage.sedyld += item.sedyld * weight;
			weightedAverage.lat3no3 += item.lat3no3 * weight;
			weightedAverage.surqno3 += item.surqno3 * weight;
			weightedAverage.surqsolp += item.surqsolp * weight;
			weightedAverage.uplandSedYield += item.uplandSedYield * weight;
			weightedAverage.maxUplandSedYield += item.maxUplandSedYield * weight;
			weightedAverage.chaErosion += item.chaErosion * weight;
			weightedAverage.chaDeposition += item.chaDeposition * weight;

			// derived
			weightedAverage.nLossesTotalLoss += item.nLossesTotalLoss * weight;
			weightedAverage.nLossesOrgN += item.nLossesOrgN * weight;
			weightedAverage.nLossesSurfaceRunoff += item.nLossesSurfaceRunoff * weight;
			weightedAverage.nLossesLateralFlow += item.nLossesLateralFlow * weight;
			weightedAverage.totalN += item.totalN * weight;
			weightedAverage.nLossesSolubilityRatio += item.nLossesSolubilityRatio * weight;
			weightedAverage.pLossesTotalLoss += item.pLossesTotalLoss * weight;
			weightedAverage.pLossesOrgP += item.pLossesOrgP * weight;
			weightedAverage.pLossesSurfaceRunoff += item.pLossesSurfaceRunoff * weight;
			weightedAverage.pLossesSolubilityRatio += item.pLossesSolubilityRatio * weight;

			// cha stuff
			weightedAverage.sed_in += item.sed_in * weight;
			weightedAverage.sed_out += item.sed_out * weight;
			weightedAverage.sed_stor += item.sed_stor * weight;

			for (let w of item.warnings.wb) {
				weightedAverage.warnings.wb.push(`${m.landuse}: ${w}`);
			}
			for (let w of item.warnings.plants) {
				weightedAverage.warnings.plants.push(`${m.landuse}: ${w}`);
			}
			for (let w of item.warnings.nb_nitrogen) {
				weightedAverage.warnings.nb_nitrogen.push(`${m.landuse}: ${w}`);
			}
			for (let w of item.warnings.nb_phosphorus) {
				weightedAverage.warnings.nb_phosphorus.push(`${m.landuse}: ${w}`);
			}			
		}

		weightedAverage.percoToPrecip = weightedAverage.perc / weightedAverage.precip;
		weightedAverage.seepToPrecip = weightedAverage.aqu_seep / weightedAverage.precip;
		weightedAverage.totalFlowToPrecip = (weightedAverage.surq_gen + weightedAverage.latq + weightedAverage.aqu_flo_cha) / weightedAverage.precip;
		weightedAverage.etToPrecip = weightedAverage.et / weightedAverage.precip;
		weightedAverage.baseflowToTotal = weightedAverage.aqu_flo_cha / (weightedAverage.surq_gen + weightedAverage.latq + weightedAverage.aqu_flo_cha);
		weightedAverage.surfaceflowToTotal = (weightedAverage.surq_gen) / (weightedAverage.surq_gen + weightedAverage.latq + weightedAverage.aqu_flo_cha);

		return weightedAverage;
	}

	const selectedHru = computed(() => {
		if (!formatters.isNullOrEmpty(data.page.selectedHruIndex)) {
			let matches = data.check.mgt.filter((l:any) => l.index == data.page.selectedHruIndex);
			if (matches.length > 0) {
				return matches[0];
			}
		}

		return null;
	})

	const filteredMgtOptions = computed(() => {
		if (data.page.checkByLanduse && data.page.selectedLandusesInput.length > 0) {
			return data.check.mgtOptions.filter((m:any) => 
				data.page.selectedLandusesInput.some((lu:any) => m.title.toLowerCase().includes(lu.toLowerCase())));
		}
		return data.check.mgtOptions;
	})

	function getMgtIconAndColor(op:string) {
		op = formatters.toLower(op)||'';
		if (op.includes('plant')) return { icon: 'fas fa-seedling', color: 'green' };
		if (op.includes('harv') || op.includes('kill')) return { icon: 'fas fa-trowel', color: 'brown' };
		if (op.includes('irr')) return { icon: 'fas fa-droplet', color: 'blue' };
		if (op.includes('fert')) return { icon: 'fas fa-leaf', color: 'orange' };
		if (op.includes('tillage')) return { icon: 'fas fa-tractor', color: 'grey' };
		return { icon: 'fas fa-check', color: 'blue-grey' };
	}

	onMounted(async () => await get());
	watch(() => route.path, async () => await get())

	interface CheckToolboxData {
		// wb_basin
		precip: number;
		snofall: number;
		surq_gen: number;
		latq: number;
		wateryld: number;
		perc: number;
		sw_init: number;
		sw_final: number;
		et: number;
		eplant: number;
		esoil: number;
		cn: number;
		pet: number;
		qtile: number;
		irr: number;
		surq_cha: number;
		surq_res: number;
		latq_cha: number;
		latq_res: number;
		
		// aqu_basin
		aqu_flo: number;
		aqu_dep_wt: number;
		aqu_stor: number;
		aqu_rchrg: number;
		aqu_seep: number;
		aqu_revap: number;
		aqu_flo_cha: number;
		aqu_flo_res: number;
		aqu_flo_ls: number;
		aqu_no3_lat: number;
		aqu_no3_seep: number;
		aqu_no3_rchg: number;
		
		// pw
		lai: number;
		bioms: number;
		yield_val: number;
		residue: number;
		pplnt: number;
		nplt: number;
		
		// stress days
		strsw: number;
		strsa: number;
		strstmp: number;
		strsn: number;
		strsp: number;
		
		// nb
		percn: number;
		grzn: number;
		grzp: number;
		lab_min_p: number;
		act_sta_p: number;
		fertn: number;
		fertp: number;
		fixn: number;
		denit: number;
		act_nit_n: number;
		act_sta_n: number;
		org_lab_p: number;
		rsd_nitorg_n: number;
		rsd_laborg_p: number;
		no3atmo: number;
		nh4atmo: number;
		nuptake: number;
		puptake: number;
		
		initialNO3: number | null;
		finalNO3: number | null;
		initialOrgN: number | null;
		finalOrgN: number | null;
		volatilization: number | null;
		nitrification: number | null;
		mineralization: number | null;
		
		// ls
		sedorgn: number;
		sedorgp: number;
		sedyld: number;
		lat3no3: number;
		surqno3: number;
		surqsolp: number;
		uplandSedYield: number;
		maxUplandSedYield: number;
		chaErosion: number;
		chaDeposition: number;
		
		// derived
		nLossesTotalLoss: number;
		nLossesOrgN: number;
		nLossesSurfaceRunoff: number;
		nLossesLateralFlow: number;
		totalN: number;
		nLossesSolubilityRatio: number;
		pLossesTotalLoss: number;
		pLossesOrgP: number;
		pLossesSurfaceRunoff: number;
		pLossesSolubilityRatio: number;
		
		// cha stuff
		sed_in: number;
		sed_out: number;
		sed_stor: number;
		
		// ratios
		baseflowToTotal: number;
		surfaceflowToTotal: number;
		totalFlowToPrecip: number;
		etToPrecip: number;
		percoToPrecip: number;
		seepToPrecip: number;

		//point sources
		subbasinLoad: CheckToolboxPointSourcesLoad
		pointSourceInletLoad: CheckToolboxPointSourcesLoad
		fromInletAndPointSource: CheckToolboxPointSourcesLoad

		// reservoirs
		reservoirRows: CheckReservoirRow[]
		avgTrappingEfficiencies: CheckAvgTrappingEfficiency
		avgWaterLosses: CheckAvgWaterLoss
		avgReservoirTrends: CheckAvgReservoirTrend
		
		// warnings
		warnings: CheckToolboxDataWarnings;
	}

	interface CheckToolboxDataWarnings {
		plants: string[];
		nb_nitrogen: string[];
		nb_phosphorus: string[];
		wb: string[];
		sed: string[];
		ptsrc: string[];
		res: string[];
	}

	interface CheckReservoirRow {
		id: string;
		sediment: number;
		phosphorus: number;
		nitrogen: number;
		volumeRatio: number;
		fractionEmpty: number;
		seepage: number;
		evapLoss: number;
	}

	interface CheckAvgTrappingEfficiency {
		sediment: number;
		phosphorus: number;
		nitrogen: number;
	}

	interface CheckAvgWaterLoss {
		totalRemoved: number;
		evaporation: number;
		seepage: number;
	}

	interface CheckAvgReservoirTrend {
		numberReservoirs: number;
		maxVolume: number;
		minVolume: number;
		fractionEmpty: number;
	}

	interface CheckToolboxPointSourcesLoad {
		flow: number;
		sediment: number;
		nitrogen: number;
		phosphorus: number;
	}
</script>

<template>
    <project-container :loading="data.page.loading" add-error-frame>
        <v-main>
			<div class="py-3 px-6" v-if="!canLoad">
                <div v-if="currentProject.isLte">			
					<h1 class="text-h5 mb-6">SWAT+ Check Not Available</h1>

					<v-alert color="info" icon="$info" variant="tonal" border="start" class="my-4">
						SWAT+ Check is not available for SWAT+ lte models.					
					</v-alert>

					<v-btn @click="utilities.exit" variant="flat" color="primary">Exit SWAT+ Editor</v-btn>
				</div>
				<div v-else-if="!formatters.isNullOrEmpty(data.page.error)">
					<h1 class="text-h5 mb-6">There was an error loading SWAT+ Check for your project.</h1>
					<error-alert :text="data.page.error"></error-alert>
					<v-btn to="/run" variant="flat" color="primary">Re-Configure Model Run</v-btn>
				</div>
				<div v-else-if="formatters.isNullOrEmpty(data.config.output_last_imported)">
					<h1 class="text-h5 mb-6">Not ready to run SWAT+ Check</h1>

					<v-alert color="info" icon="$info" variant="tonal" border="start" class="my-4">
						You must run the model and analyze output before running SWAT+ Check.				
					</v-alert>

					<v-btn to="/run" variant="flat" color="primary">Configure Model Run</v-btn>
				</div>
            </div>
			<div v-else>
				<v-tabs v-model="data.page.tabIndex" id="spcheck_tabs" align-tabs="center" 
					color="primary" :bg-color="theme.global.name.value == 'dark' ? 'blue-grey-darken-4' : 'blue-grey-lighten-3'">
					<v-tab v-for="(tab, index) in data.page.tabs" :key="index">{{tab}}</v-tab>
				</v-tabs>

				<div v-if="data.page.tabIndex == 0" :class="`spcheck_tab ${theme.global.name.value}`" id="spcheck_overview">
					<v-card style="max-width: 800px;" class="semi-transparent mt-8" elevation="6">
						<v-card-item>
							<h1 class="text-h5 mb-6">SWAT+ Check</h1>

							<p> 
								SWAT+ Check reads model output from a SWAT+ project and performs many simple checks to identify 
								potential model problems. The intended purpose of this program is to identify model problems early in the 
								modeling process. Hidden model problems often result in the need to recalibrate or regenerate a model, 
								resulting in an avoidable waste of time. This program is designed to compare a variety of SWAT+ outputs to 
								nominal ranges based on the judgment of model developers. A warning does not necessarily indicate a problem; 
								the purpose is to bring attention to unusual predictions. This software also provides a visual representation 
								of various model outputs to aid novice users.
							</p>

							<v-alert v-if="data.check.info.gwflow" type="warning" icon="$warning" variant="tonal" border="start" class="my-4">
								<p>
									Your model is using the GWFLOW module. SWAT+ Check is not fully compatible with GWFLOW at this time.
									We will update this as soon as possible. For now the following values are unavailable:
								</p>
								<ul>
									<li>Hydrology: return flow, revap, recharge, baseflow total flow, deep recharge precipitation</li>
									<li>Landscape Nitrogen Losses: leached, groundwater yield</li>
								</ul>
								<p>
									We encourage you to look in the GWFLOW output files on your own until a fix is available.
								</p>
							</v-alert>

							<v-row class="mb-2">
								<v-col cols="12" md="6">
									<v-table small density="compact" class="transparent">
										<tbody>
											<tr>
												<th>Model Version</th>
												<td>SWAT+ {{data.check.info.swatVersion}}</td>
											</tr>
											<tr>
												<th>Simulation Length</th>
												<td>{{data.check.info.simulationLength}} years</td>
											</tr>
											<tr>
												<th>Warm-up</th>
												<td>{{data.check.info.warmUp}} years</td>
											</tr>
											<tr>
												<th>Weather</th>
												<td>{{data.check.info.weatherMethod}}</td>
											</tr>
										</tbody>
									</v-table>
								</v-col>
								<v-col cols="12" md="6">
									<v-table small density="compact" class="transparent">
										<tbody>
											<tr>
												<th>Watershed Area</th>
												<td>{{formatters.toNumberFormat(data.check.info.watershedArea, 2)}} ha</td>
											</tr>
											<tr>
												<th>HRUs</th>
												<td>{{formatters.toNumberFormat(data.check.info.hrus, 0)}}</td>
											</tr>
											<tr>
												<th>LSUs</th>
												<td>{{formatters.toNumberFormat(data.check.info.lsus, 0)}}</td>
											</tr>
											<tr>
												<th>Subbasins</th>
												<td>{{formatters.toNumberFormat(data.check.info.subbasins, 0)}}</td>
											</tr>
										</tbody>
									</v-table>
								</v-col>
							</v-row>
						</v-card-item>
					</v-card>					
				</div>				

				<image-overlays v-if="data.page.tabIndex == 1" class="spcheck_tab" id="spcheck_hydrology"
					:image-path="`/swatplus-check/hydrology_${data.page.isOverall ? 'overall_' : ''}light.png`"
					:dark-image-path="`/swatplus-check/hydrology_${data.page.isOverall ? 'overall_' : ''}dark.png`"
					:image-ratio="2886/1023"
					:overlays="[
						{ x: 0.445, y: 0.20, slot: 'hyd_precip' },
						{ x: 0.6, y: 0.3, slot: 'hyd_et' },
						{ x: 0.655, y: 0.3, slot: 'hyd_pet' },
						{ x: 0.6, y: 0.58, slot: 'hyd_surq_gen' },
						{ x: 0.49, y: 0.58, slot: 'hyd_latq' },
						{ x: 0.385, y: 0.43, slot: 'hyd_irr' },
						{ x: 0.41, y: 0.71, slot: 'hyd_aqu_revap' },
						{ x: 0.48, y: 0.69, slot: 'hyd_perc' },
						{ x: 0.668, y: 0.74, slot: 'hyd_aqu_flo_cha' },
						{ x: 0.56, y: 0.8, slot: 'hyd_aqu_seep' },
						{ x: 0.68, y: 0.53, slot: 'hyd_cn' },
					]">
					<template #mainContent>
						<v-card class="semi-transparent details-card" elevation="6">
							<v-card-item>
								<v-switch label="Check by land use" v-model="data.page.checkByLanduse" color="primary" hide-details></v-switch>
								<v-select v-if="data.page.checkByLanduse && data.check.landuseCategories.length > 0" hide-details density="comfortable" 
									:items="data.check.landuseCategories" item-title="name" item-value="name"
									label="Filter by category" 
									v-model="data.page.selectedCategory" @update:model-value="setLanduseInCategory">
								</v-select>
								<v-autocomplete v-if="data.page.checkByLanduse" hide-details density="comfortable" multiple chips closable-chips
									v-model="data.page.selectedLandusesInput" :items="data.check.landuseOptions"
									label="Land use" placeholder="Type to search...">
									<template v-slot:chip="{ props, item }:any">
										<v-chip v-bind="props" :text="item.raw.value"></v-chip>
									</template>
								</v-autocomplete>
								<div v-if="data.page.checkByLanduse && data.page.selectedLandusesInput.length > 0" class="mt-2 text-subtitle-2">
									<div v-for="(lu, index) in data.page.selectedLanduses" :key="index">
										{{ lu.landuse }} /  
										{{ formatters.toNumberFormat(lu.area, 2) }} ha / 
										{{ formatters.toNumberFormat(lu.hruCount, 0) }} HRUs
									</div>
								</div>

								<h4 class="mt-4">Water Balance Ratios</h4>
								<v-table small density="compact" class="transparent">
									<tbody>
										<tr>
											<th>ET/Precipitation</th>
											<td class="text-right">{{formatters.toNumberDecimals(selectedData.etToPrecip, 3)}}</td>
										</tr>
										<tr>
											<th>Deep Recharge/Precipitation</th>
											<td class="text-right">{{formatters.toNumberDecimals(selectedData.seepToPrecip, 3)}}</td>
										</tr>
										<tr>
											<th>Streamflow/Precipitation</th>
											<td class="text-right">{{formatters.toNumberDecimals(selectedData.totalFlowToPrecip, 3)}}</td>
										</tr>
										<tr>
											<th>Baseflow/Total Flow</th>
											<td class="text-right">{{formatters.toNumberDecimals(selectedData.baseflowToTotal, 3)}}</td>
										</tr>
										<tr>
											<th>Surface Runoff/Total Flow</th>
											<td class="text-right">{{formatters.toNumberDecimals(selectedData.surfaceflowToTotal, 3)}}</td>
										</tr>
										<tr>
											<th>Percolation/Precipitation</th>
											<td class="text-right">{{formatters.toNumberDecimals(selectedData.percoToPrecip, 3)}}</td>
										</tr>
									</tbody>
								</v-table>

								<h4 class="mt-4 mb-2">Messages and Warnings</h4>
								<div class="warning-list mb-2">
									<ul>
										<li v-for="(w, index) in selectedData.warnings.wb" :key="index" class="text-body-2">
											{{w}}
										</li>
										<li v-if="!selectedData.warnings.wb || selectedData.warnings.wb.length === 0" class="text-body-2">
											<i>None</i>
										</li>
									</ul>
								</div>
							</v-card-item>
						</v-card>
					</template>

					<template #hyd_precip>
						<div class="label">Precipitation</div>
						<div>{{ formatters.toNumberDecimals(selectedData.precip, 3) }} mm</div>
					</template>

					<template #hyd_et>
						<div class="label">ET</div>
						<div>{{ formatters.toNumberDecimals(selectedData.et, 3) }} mm</div>
					</template>

					<template #hyd_pet>
						<div class="label">PET</div>
						<div>{{ formatters.toNumberDecimals(selectedData.pet, 3) }} mm</div>
					</template>

					<template #hyd_surq_gen>
						<div class="label">Surface Runoff</div>
						<div>{{ formatters.toNumberDecimals(selectedData.surq_gen, 3) }} mm</div>
					</template>

					<template #hyd_latq>
						<div class="label">Lateral Flow</div>
						<div>{{ formatters.toNumberDecimals(selectedData.latq, 3) }} mm</div>
					</template>

					<template #hyd_irr>
						<div class="label">Irrigation</div>
						<div>{{ formatters.toNumberDecimals(selectedData.irr, 3) }} mm</div>
					</template>

					<template #hyd_aqu_revap>
						<div class="label">Revap</div>
						<div>{{ formatters.toNumberDecimals(selectedData.aqu_revap, 3) }} mm</div>
					</template>

					<template #hyd_perc>
						<div class="label">Percolation</div>
						<div>{{ formatters.toNumberDecimals(selectedData.perc, 3) }} mm</div>
					</template>

					<template #hyd_aqu_flo_cha v-if="data.page.isOverall">
						<div class="label">Return Flow</div>
						<div>{{ formatters.toNumberDecimals(selectedData.aqu_flo_cha, 3) }} mm</div>
					</template>

					<template #hyd_aqu_seep v-if="data.page.isOverall">
						<div class="label">Deep Aquifer Recharge</div>
						<div>{{ formatters.toNumberDecimals(selectedData.aqu_seep, 3) }} mm</div>
					</template>

					<template #hyd_cn>
						<div class="label">{{ data.page.isOverall ? 'Average' : '' }} CN</div>
						<div>{{ formatters.toNumberDecimals(selectedData.cn, 3) }}</div>
					</template>
				</image-overlays>

				<image-overlays v-if="data.page.tabIndex == 2" class="spcheck_tab" id="spcheck_nutrients"
					:image-path="`/swatplus-check/nutrients_${data.page.nutrientsTab}_light.png`"
					:dark-image-path="`/swatplus-check/nutrients_${data.page.nutrientsTab}_dark.png`"
					:image-ratio="2586/1023"
					:overlays="[
						{ x: 0.65, y: 0.10, slot: 'nut_units' },
						{ x: 0.457, y: 0.10, slot: 'nutn_orgn' },
						{ x: 0.502, y: 0.10, slot: 'nutn_minn' },
						{ x: 0.635, y: 0.67, slot: 'nutn_inorgn' },
						{ x: 0.43, y: 0.81, slot: 'nutn_rsd_nitorg_n' },
						{ x: 0.475, y: 0.65, slot: 'nutn_mineralization' },
						{ x: 0.45, y: 0.56, slot: 'nutn_sedorgn' },
						{ x: 0.6, y: 0.58, slot: 'nutn_nplt' },
						{ x: 0.4, y: 0.62, slot: 'nutn_act_sta_n' },
						{ x: 0.575, y: 0.38, slot: 'nutn_denit' },
						{ x: 0.642, y: 0.3, slot: 'nutn_fertn' },
						{ x: 0.75, y: 0.4, slot: 'nutn_volatilization' },
						{ x: 0.512, y: 0.34, slot: 'nutn_fixn' },

						{ x: 0.457, y: 0.10, slot: 'nutp_orgp' },
						{ x: 0.502, y: 0.10, slot: 'nutp_minp' },
						{ x: 0.372, y: 0.459, slot: 'nutp_residue' },
						{ x: 0.43, y: 0.81, slot: 'nutp_rsd_laborg_p' },
						{ x: 0.45, y: 0.56, slot: 'nutp_sedorgp' },
						{ x: 0.605, y: 0.58, slot: 'nutp_pplnt' },
						{ x: 0.4, y: 0.62, slot: 'nutp_decay' },
						{ x: 0.692, y: 0.67, slot: 'nutp_act_sta_p' },
						{ x: 0.56, y: 0.34, slot: 'nutp_fertp' },
					]">
					<template #mainContent>
						<v-card class="semi-transparent details-card" elevation="6">
							<v-card-item>
								<v-switch label="Check by land use" v-model="data.page.checkByLanduse" color="primary" hide-details></v-switch>
								<v-autocomplete v-if="data.page.checkByLanduse" hide-details density="comfortable" multiple chips closable-chips
									v-model="data.page.selectedLandusesInput" :items="data.check.landuseOptions"
									label="Land use" placeholder="Type to search...">
									<template v-slot:chip="{ props, item }:any">
										<v-chip v-bind="props" :text="item.raw.value"></v-chip>
									</template>
								</v-autocomplete>
								<div v-if="data.page.checkByLanduse && data.page.selectedLandusesInput.length > 0" class="mt-2 text-subtitle-2">
									<div v-for="(lu, index) in data.page.selectedLanduses" :key="index">
										{{ lu.landuse }} /  
										{{ formatters.toNumberFormat(lu.area, 2) }} ha / 
										{{ formatters.toNumberFormat(lu.hruCount, 0) }} HRUs
									</div>
								</div>

								<v-tabs v-model="data.page.nutrientsTab" align-tabs="center" :class="data.page.isOverall ? 'mt-0' : 'mt-4'"
									color="primary" :bg-color="theme.global.name.value == 'dark' ? 'blue-grey-darken-2' : 'blue-grey-lighten-5'">
									<v-tab value="nitrogen">Nitrogen</v-tab>
									<v-tab value="phosphorus">Phosphorus</v-tab>
								</v-tabs>

								<div v-if="data.page.nutrientsTab === 'nitrogen'">
									<h4 class="mt-4">Landscape Nitrogen Losses</h4>
									<v-table small density="compact" class="transparent">
										<tbody>
											<tr>
												<th>Total N Loss</th>
												<td class="text-right">{{formatters.toNumberDecimals(selectedData.nLossesTotalLoss, 3)}}</td>
											</tr>
											<tr>
												<th>Organic N</th>
												<td class="text-right">{{formatters.toNumberDecimals(selectedData.nLossesOrgN, 3)}}</td>
											</tr>
											<tr>
												<th>Nitrate Surface Runoff</th>
												<td class="text-right">{{formatters.toNumberDecimals(selectedData.nLossesSurfaceRunoff, 3)}}</td>
											</tr>
											<tr>
												<th>Nitrate Lateral Flow</th>
												<td class="text-right">{{formatters.toNumberDecimals(selectedData.nLossesLateralFlow, 3)}}</td>
											</tr>
											<tr>
												<th>Solubility Ratio in Runoff</th>
												<td class="text-right">{{formatters.toNumberDecimals(selectedData.nLossesSolubilityRatio, 3)}}</td>
											</tr>
										</tbody>
									</v-table>
								</div>

								<div v-else>
									<h4 class="mt-4">Landscape Phosphorus Losses</h4>
									<v-table small density="compact" class="transparent">
										<tbody>
											<tr>
												<th>Total P Loss</th>
												<td class="text-right">{{formatters.toNumberDecimals(selectedData.pLossesTotalLoss, 3)}}</td>
											</tr>
											<tr>
												<th>Organic P</th>
												<td class="text-right">{{formatters.toNumberDecimals(selectedData.pLossesOrgP, 3)}}</td>
											</tr>
											<tr>
												<th>Soluble P Surface Runoff</th>
												<td class="text-right">{{formatters.toNumberDecimals(selectedData.pLossesSurfaceRunoff, 3)}}</td>
											</tr>
											<tr>
												<th>Solubility Ratio in Runoff</th>
												<td class="text-right">{{formatters.toNumberDecimals(selectedData.pLossesSolubilityRatio, 3)}}</td>
											</tr>
										</tbody>
									</v-table>
								</div>

								<h4 class="mt-4 mb-2">Messages and Warnings</h4>
								<div class="warning-list mb-2">
									<ul v-if="data.page.nutrientsTab === 'nitrogen'">
										<li v-for="(w, index) in selectedData.warnings.nb_nitrogen" :key="index" class="text-body-2">
											{{w}}
										</li>
										<li v-if="!selectedData.warnings.nb_nitrogen || selectedData.warnings.nb_nitrogen.length === 0" class="text-body-2">
											<i>None</i>
										</li>
									</ul>
									<ul v-else>
										<li v-for="(w, index) in selectedData.warnings.nb_phosphorus" :key="index" class="text-body-2">
											{{w}}
										</li>
										<li v-if="!selectedData.warnings.nb_phosphorus || selectedData.warnings.nb_phosphorus.length === 0" class="text-body-2">
											<i>None</i>
										</li>
									</ul>
								</div>
							</v-card-item>
						</v-card>
					</template>

					<template #nut_units>
						<div class="label">All units kg/ha</div>
					</template>

					<template #nutp_orgp v-if="data.page.nutrientsTab === 'phosphorus'">
						<div class="label">Organic P</div>
					</template>

					<template #nutp_minp v-if="data.page.nutrientsTab === 'phosphorus'">
						<div class="label">Mineral P</div>
					</template>

					<template #nutp_residue>
						<div class="label">Plant Residue</div>
					</template>

					<template #nutp_rsd_laborg_p v-if="data.page.nutrientsTab === 'phosphorus'">
						<div class="label">Residue Mineralization</div>
						<div>{{ formatters.toNumberDecimals(selectedData.rsd_laborg_p, 3) }}</div>
					</template>

					<template #nutp_sedorgp v-if="data.page.nutrientsTab === 'phosphorus'">
						<div class="label">Organic Fertilizer</div>
						<div>{{ formatters.toNumberDecimals(selectedData.sedorgp, 3) }}</div>
					</template>

					<template #nutp_pplnt v-if="data.page.nutrientsTab === 'phosphorus'">
						<div class="label">Uptake</div>
						<div>{{ formatters.toNumberDecimals(selectedData.pplnt, 3) }}</div>
					</template>

					<template #nutp_decay v-if="data.page.nutrientsTab === 'phosphorus'">
						<div class="label">Decay</div>
					</template>

					<template #nutp_act_sta_p v-if="data.page.nutrientsTab === 'phosphorus'">
						<div>{{ formatters.toNumberDecimals(selectedData.act_sta_p, 3) }}</div>
					</template>

					<template #nutp_fertp v-if="data.page.nutrientsTab === 'phosphorus'">
						<div class="label">Inorganic Fertilizer</div>
						<div>{{ formatters.toNumberDecimals(selectedData.fertp, 3) }}</div>
					</template>



					<template #nutn_orgn v-if="data.page.nutrientsTab === 'nitrogen'">
						<div class="label">Organic N</div>
					</template>

					<template #nutn_minn v-if="data.page.nutrientsTab === 'nitrogen'">
						<div class="label">Mineral N</div>
					</template>

					<template #nutn_inorgn v-if="data.page.nutrientsTab === 'nitrogen'">
						<div class="label">Inorganic Fertilizer</div>
					</template>

					<template #nutn_rsd_nitorg_n v-if="data.page.nutrientsTab === 'nitrogen'">
						<div class="label">Residue Mineralization</div>
						<div>{{ formatters.toNumberDecimals(selectedData.rsd_nitorg_n, 3) }}</div>
					</template>

					<template #nutn_mineralization>
						<div class="label">Mineralization</div>
						<div>{{ formatters.toNumberDecimals(selectedData.mineralization, 3) }}</div>
					</template>

					<template #nutn_sedorgn v-if="data.page.nutrientsTab === 'nitrogen'">
						<div class="label">Organic Fertilizer</div>
						<div>{{ formatters.toNumberDecimals(selectedData.sedorgn, 3) }}</div>
					</template>

					<template #nutn_nplt v-if="data.page.nutrientsTab === 'nitrogen'">
						<div class="label">Uptake</div>
						<div>{{ formatters.toNumberDecimals(selectedData.nplt, 3) }}</div>
					</template>

					<template #nutn_act_sta_n v-if="data.page.nutrientsTab === 'nitrogen'">
						<div class="label">Decay</div>
						<div>{{ formatters.toNumberDecimals(selectedData.act_sta_n, 3) }}</div>
					</template>

					<template #nutn_denit v-if="data.page.nutrientsTab === 'nitrogen'">
						<div class="label">Denitrification</div>
						<div>{{ formatters.toNumberDecimals(selectedData.denit, 3) }}</div>
					</template>

					<template #nutn_fertn v-if="data.page.nutrientsTab === 'nitrogen'">
						<div class="label">Total Inorganic</div>
						<div>{{ formatters.toNumberDecimals(selectedData.fertn, 3) }}</div>
					</template>

					<template #nutn_volatilization v-if="data.page.nutrientsTab === 'nitrogen'">
						<div class="label">Volatilization</div>
						<div>{{ formatters.toNumberDecimals(selectedData.volatilization, 3) }}</div>
					</template>

					<template #nutn_fixn v-if="data.page.nutrientsTab === 'nitrogen'">
						<div class="label">Nitrification</div>
						<div>{{ formatters.toNumberDecimals(selectedData.fixn, 3) }}</div>
					</template>
				</image-overlays>

				<image-overlays v-if="data.page.tabIndex == 3" class="spcheck_tab" id="spcheck_sediment"
					:image-path="`/swatplus-check/sediment_light.png`"
					:dark-image-path="`/swatplus-check/sediment_dark.png`"
					:image-ratio="2886/1023"
					:overlays="[
						{ x: 0.38, y: 0.55, slot: 'sed_runoff' },
						{ x: 0.41, y: 0.71, slot: 'sed_change' },
						{ x: 0.625, y: 0.57, slot: 'sed_yield' },
					]">
					<template #mainContent>
						<v-card class="semi-transparent details-card" elevation="6">
							<v-card-item>
								<v-alert color="primary" variant="tonal" class="mt-2 mb-4" density="compact">
									<small>Note: sediment is only available for the entire basin and cannot be checked by land use.</small>
								</v-alert>

								<h4 class="mt-4">Sediment Budget</h4>
								<v-table small density="compact" class="transparent">
									<tbody>
										<tr>
											<th>Upland Sediment Yield</th>
											<td class="text-right">{{formatters.toNumberDecimals(data.check.basin.sedyld, 3)}} t/ha</td>
										</tr>
										<tr>
											<th>Instream Sediment Change</th>
											<td class="text-right">{{formatters.toNumberDecimals(data.check.basin.sed_out - data.check.basin.sed_in, 3)}} t/ha</td>
										</tr>
										<tr>
											<th>Channel Erosion</th>
											<td class="text-right">{{formatters.toNumberDecimals(data.check.basin.chaErosion, 3)}} %</td>
										</tr>
										<tr>
											<th>Channel Deposition</th>
											<td class="text-right">{{formatters.toNumberDecimals(data.check.basin.chaDeposition, 3)}} %</td>
										</tr>
									</tbody>
								</v-table>

								<h4 class="mt-4 mb-2">Messages and Warnings</h4>
								<div class="warning-list mb-2">
									<ul>
										<li v-for="(w, index) in data.check.basin.warnings.sed" :key="index" class="text-body-2">
											{{w}}
										</li>
										<li v-if="!data.check.basin.warnings.sed || data.check.basin.warnings.sed.length === 0" class="text-body-2">
											<i>None</i>
										</li>
									</ul>
								</div>
							</v-card-item>
						</v-card>
					</template>

					<template #sed_runoff>
						<div class="label">Surface Runoff</div>
						<div>{{ formatters.toNumberDecimals(data.check.basin.surq_gen, 3) }} mm/yr</div>
					</template>

					<template #sed_change>
						<div class="label">Instream Sediment Change</div>
						<div>{{ formatters.toNumberDecimals(data.check.info.hruTotalArea * (data.check.basin.sed_out - data.check.basin.sed_in), 3) }} tons</div>
					</template>

					<template #sed_yield>
						<div class="label">Upland Sediment Yield</div>
						<div>Maximum: {{ formatters.toNumberDecimals(data.check.basin.maxUplandSedYield, 3) }} t/ha</div>
						<div>Average: {{ formatters.toNumberDecimals(data.check.basin.sedyld, 3) }} t/ha</div>
					</template>
				</image-overlays>

				<image-overlays v-if="data.page.tabIndex == 4" class="spcheck_tab" id="spcheck_plants"
					:image-path="`/swatplus-check/landuse_overall_light.png`"
					:dark-image-path="`/swatplus-check/landuse_overall_dark.png`"
					:image-ratio="2886/1023"
					:overlays="[
						{ x: 0.5, y: 0.6, slot: 'plant_nplt_pplnt' },
						{ x: 0.55, y: 0.20, slot: 'plant_yield_bioms' },
						{ x: 0.74, y: 0.74, slot: 'plant_nuptake_puptake' },
						{ x: 0.7, y: 0.3, slot: 'plant_removed' },
					]">
					<template #mainContent>
						<v-card class="semi-transparent details-card" elevation="6">
							<v-card-item>
								<v-switch label="Check by land use" v-model="data.page.checkByLanduse" color="primary" hide-details></v-switch>
								<v-autocomplete v-if="data.page.checkByLanduse" hide-details density="comfortable" multiple chips closable-chips
									v-model="data.page.selectedLandusesInput" :items="data.check.landuseOptions"
									label="Land use" placeholder="Type to search...">
									<template v-slot:chip="{ props, item }:any">
										<v-chip v-bind="props" :text="item.raw.value"></v-chip>
									</template>
								</v-autocomplete>
								<div v-if="data.page.checkByLanduse && data.page.selectedLandusesInput.length > 0" class="mt-2 text-subtitle-2">
									<div v-for="(lu, index) in data.page.selectedLanduses" :key="index">
										{{ lu.landuse }} /  
										{{ formatters.toNumberFormat(lu.area, 2) }} ha / 
										{{ formatters.toNumberFormat(lu.hruCount, 0) }} HRUs
									</div>
								</div>

								<h4 class="mt-4">Stress Days</h4>
								<v-table small density="compact" class="transparent">
									<tbody>
										<tr>
											<th>Temperature Stress Days</th>
											<td class="text-right">{{formatters.toNumberDecimals(selectedData.strstmp, 3)}}</td>
										</tr>
										<tr>
											<th>Water Stress Days</th>
											<td class="text-right">{{formatters.toNumberDecimals(selectedData.strsw, 3)}}</td>
										</tr>
										<tr>
											<th>Nitrogen Stress Days</th>
											<td class="text-right">{{formatters.toNumberDecimals(selectedData.strsn, 3)}}</td>
										</tr>
										<tr>
											<th>Phosphorus Stress Days</th>
											<td class="text-right">{{formatters.toNumberDecimals(selectedData.strsp, 3)}}</td>
										</tr>
										<tr>
											<th>Soil Air Stress Days</th>
											<td class="text-right">{{formatters.toNumberDecimals(selectedData.strsa, 3)}}</td>
										</tr>
									</tbody>
								</v-table>

								<h4 class="mt-4 mb-2">Messages and Warnings</h4>
								<div class="warning-list mb-2">
									<ul>
										<li v-for="(w, index) in selectedData.warnings.plants" :key="index" class="text-body-2">
											{{w}}
										</li>
										<li v-if="!selectedData.warnings.plants || selectedData.warnings.plants.length === 0" class="text-body-2">
											<i>None</i>
										</li>
									</ul>
								</div>

								<h4 class="mt-4 mb-2">Preview HRU Management</h4>
								<v-autocomplete v-if="filteredMgtOptions && filteredMgtOptions.length > 0" hide-details class="mb-2" density="compact"
									v-model="data.page.selectedHruIndex" :items="filteredMgtOptions"
									label="Select an HRU" placeholder="Type to search..."
								></v-autocomplete>
							</v-card-item>
						</v-card>

						<v-card v-if="selectedHru != null" class="mgt-card" elevation="0" density="compact">
							<v-card-item>
								<h4 class="mt-4 mb-0">Management Events</h4>
								<div class="text-subtitle-2">
									{{ selectedHru.name }} /  {{ selectedHru.landuse }} / {{ selectedHru.soil }} /
									{{ formatters.toNumberFormat(selectedHru.area, 2) }} ha 
								</div>

								<div v-if="selectedHru.mgts.length < 1">
									<em>No management events for this HRU.</em>
								</div>
								<div v-else>
									<v-timeline align="start" side="end" density="compact">
										<v-timeline-item v-for="(mgt, index) in selectedHru.mgts" :key="index" :dot-color="getMgtIconAndColor(mgt.op).color" :icon="getMgtIconAndColor(mgt.op).icon" fill-dot size="small">
											<div class="text-body-2"><b>{{ mgt.date }}</b></div>
											<div class="text-body-2">{{ mgt.description }}</div>											
										</v-timeline-item>
									</v-timeline>
								</div>
							</v-card-item>
						</v-card>
					</template>

					<template #plant_nplt_pplnt>
						<div class="label">Total Fertilizer</div>
						<div>Nitrogen: {{ formatters.toNumberDecimals(selectedData.nuptake, 3) }} kg/ha</div>
						<div>Phosphorus: {{ formatters.toNumberDecimals(selectedData.puptake, 3) }} kg/ha</div>
					</template>

					<template #plant_yield_bioms>
						<div>Average Yield: {{ formatters.toNumberDecimals(selectedData.yield_val, 3) }} kg/ha</div>
						<div>Average Biomass: {{ formatters.toNumberDecimals(selectedData.bioms, 3) }} kg/ha</div>
					</template>

					<template #plant_nuptake_puptake>
						<div class="label">Plant Uptake</div>
						<div>Nitrogen: {{ formatters.toNumberDecimals(selectedData.nplt, 3) }} kg/ha</div>
						<div>Phosphorus: {{ formatters.toNumberDecimals(selectedData.pplnt, 3) }} kg/ha</div>
					</template>

					<template #plant_removed>
						<div class="label">Removed in Yield</div>
						<div>Nitrogen: NA</div>
						<div>Phosphorus: NA</div>
					</template>
				</image-overlays>

				<image-overlays v-if="data.page.tabIndex == 5" class="spcheck_tab" id="spcheck_ptsrc"
					:image-path="`/swatplus-check/pointsource_light.png`"
					:dark-image-path="`/swatplus-check/pointsource_dark.png`"
					:image-ratio="2886/1023"
					:overlays="[]">
					<template #mainContent>
						<v-row class="mt-7">
							<v-col cols="12" lg="3">
								<v-card class="semi-transparent" elevation="6">
									<v-card-item>
										<h4 class="mt-4">Point Sources</h4>
										<p class="text-body-2">
											Point sources constantly discharge pollutants to streams. These are an optional feature in SWAT+. These summaries are presented so that the relative contribution of these sources can be verified. Point sources contributions are so varied that there is no reasonable range which can be applied to all basins.
										</p>

										<h4 class="mt-4 mb-2">Messages and Warnings</h4>
										<div class="warning-list mb-2">
											<ul>
												<li v-for="(w, index) in data.check.basin.warnings.ptsrc" :key="index" class="text-body-2">
													{{w}}
												</li>
												<li v-if="!data.check.basin.warnings.ptsrc || data.check.basin.warnings.ptsrc.length === 0" class="text-body-2">
													<i>None</i>
												</li>
											</ul>
										</div>
									</v-card-item>
								</v-card>
							</v-col>

							<v-col cols="12" lg="3">
								<v-card class="semi-transparent" elevation="6">
									<v-card-item>
										<h4 class="mt-4">Total Subbasin Load</h4>
										<v-table small density="compact" class="my-2 transparent">
											<tbody>
												<tr>
													<th>Flow</th>
													<td class="text-right">{{formatters.toNumberDecimals(data.check.basin.subbasinLoad.flow, 3)}}</td>
													<td>cms</td>
												</tr>
												<tr>
													<th>Sediment</th>
													<td class="text-right">{{formatters.toNumberDecimals(data.check.basin.subbasinLoad.sediment, 3)}}</td>
													<td>Mg/yr</td>
												</tr>
												<tr>
													<th>Nitrogen</th>
													<td class="text-right">{{formatters.toNumberDecimals(data.check.basin.subbasinLoad.nitrogen, 3)}}</td>
													<td>kg/yr</td>
												</tr>
												<tr>
													<th>Phosphorus</th>
													<td class="text-right">{{formatters.toNumberDecimals(data.check.basin.subbasinLoad.phosphorus, 3)}}</td>
													<td>kg/yr</td>
												</tr>
											</tbody>
										</v-table>
									</v-card-item>
								</v-card>
							</v-col>

							<v-col cols="12" lg="3">
								<v-card class="semi-transparent" elevation="6">
									<v-card-item>
										<h4 class="mt-4">Total Point Source + Inlet Load</h4>
										<v-table small density="compact" class="my-2 transparent">
											<tbody>
												<tr>
													<th>Flow</th>
													<td class="text-right">{{formatters.toNumberDecimals(data.check.basin.pointSourceInletLoad.flow, 3)}}</td>
													<td>cms</td>
												</tr>
												<tr>
													<th>Sediment</th>
													<td class="text-right">{{formatters.toNumberDecimals(data.check.basin.pointSourceInletLoad.sediment, 3)}}</td>
													<td>Mg/yr</td>
												</tr>
												<tr>
													<th>Nitrogen</th>
													<td class="text-right">{{formatters.toNumberDecimals(data.check.basin.pointSourceInletLoad.nitrogen, 3)}}</td>
													<td>kg/yr</td>
												</tr>
												<tr>
													<th>Phosphorus</th>
													<td class="text-right">{{formatters.toNumberDecimals(data.check.basin.pointSourceInletLoad.phosphorus, 3)}}</td>
													<td>kg/yr</td>
												</tr>
											</tbody>
										</v-table>
									</v-card-item>
								</v-card>
							</v-col>

							<v-col cols="12" lg="3">
								<v-card class="semi-transparent" elevation="6">
									<v-card-item>
										<h4 class="mt-4">Load from Inlet + PS (%)</h4>
										<v-table small density="compact" class="my-2 transparent">
											<tbody>
												<tr>
													<th>Flow</th>
													<td class="text-right">{{formatters.toNumberDecimals(data.check.basin.fromInletAndPointSource.flow, 3)}}</td>
													<td>%</td>
												</tr>
												<tr>
													<th>Sediment</th>
													<td class="text-right">{{formatters.toNumberDecimals(data.check.basin.fromInletAndPointSource.sediment, 3)}}</td>
													<td>%</td>
												</tr>
												<tr>
													<th>Nitrogen</th>
													<td class="text-right">{{formatters.toNumberDecimals(data.check.basin.fromInletAndPointSource.nitrogen, 3)}}</td>
													<td>%</td>
												</tr>
												<tr>
													<th>Phosphorus</th>
													<td class="text-right">{{formatters.toNumberDecimals(data.check.basin.fromInletAndPointSource.phosphorus, 3)}}</td>
													<td>%</td>
												</tr>
											</tbody>
										</v-table>
									</v-card-item>
								</v-card>
							</v-col>
						</v-row>
						
					</template>
				</image-overlays>

				<image-overlays v-if="data.page.tabIndex == 6" class="spcheck_tab" id="spcheck_res"
					:image-path="`/swatplus-check/reservoirs_light.png`"
					:dark-image-path="`/swatplus-check/reservoirs_dark.png`"
					:image-ratio="2886/1023"
					:overlays="[]">
					<template #mainContent>
						<v-row class="mt-7">
							<v-col cols="12" lg="3">
								<v-card class="semi-transparent" elevation="6">
									<v-card-item>
										<h4 class="mt-4">Reservoirs</h4>
										<p class="text-body-2">
											Reservoirs are an optional feature in SWAT+.   The hydrology of basins with large reservoirs may be completely dominated by reservoir processes and release rates.
											The data presented below is an average of all reservoirs; <a href="#" @click.prevent="data.modals.reservoirs = true">see data for individual reservoirs</a>.
											The statistics presented here are designed to identify common reservoir issues.   The use of user specified release rate may cause a reservoir to
											grow continuously or run completely dry.  These common issues can be detected via the final/initial volume ratio and fraction of period empty statistics below.
										</p>

										<h4 class="mt-4 mb-2">Messages and Warnings</h4>
										<div class="warning-list mb-2">
											<ul>
												<li v-for="(w, index) in data.check.basin.warnings.res" :key="index" class="text-body-2">
													{{w}}
												</li>
												<li v-if="!data.check.basin.warnings.res || data.check.basin.warnings.res.length === 0" class="text-body-2">
													<i>None</i>
												</li>
											</ul>
										</div>
									</v-card-item>
								</v-card>
							</v-col>
							<v-col cols="12" lg="3">
								<v-card class="semi-transparent" elevation="6" style="min-height:240px">
									<v-card-item>
										<h4 class="mt-4">Average Trapping Efficiency (%)</h4>
										<v-table small density="compact" class="my-2 transparent">
											<tbody>
												<tr>
													<th>Sediment</th>
													<td class="text-right">{{formatters.toNumberDecimals(data.check.basin.avgTrappingEfficiencies.sediment, 3)}}</td>
												</tr>
												<tr>
													<th>Nitrogen</th>
													<td class="text-right">{{formatters.toNumberDecimals(data.check.basin.avgTrappingEfficiencies.nitrogen, 3)}}</td>
												</tr>
												<tr>
													<th>Phosphorus</th>
													<td class="text-right">{{formatters.toNumberDecimals(data.check.basin.avgTrappingEfficiencies.phosphorus, 3)}}</td>
												</tr>
											</tbody>
										</v-table>
										
										<h4 class="mt-4">Average Water Loss (%)</h4>
										<v-table small density="compact" class="my-2 transparent">
											<tbody>
												<tr>
													<th>Total Removed + Losses</th>
													<td class="text-right">{{formatters.toNumberDecimals(data.check.basin.avgWaterLosses.totalRemoved, 3)}}</td>
												</tr>
												<tr>
													<th>Evaporation</th>
													<td class="text-right">{{formatters.toNumberDecimals(data.check.basin.avgWaterLosses.evaporation, 3)}}</td>
												</tr>
												<tr>
													<th>Seepage</th>
													<td class="text-right">{{formatters.toNumberDecimals(data.check.basin.avgWaterLosses.seepage, 3)}}</td>
												</tr>
											</tbody>
										</v-table>
										
										<h4 class="mt-4">Average Reservoir Trends</h4>
										<v-table small density="compact" class="my-2 transparent">
											<tbody>
												<tr>
													<th>Number of Reservoirs</th>
													<td class="text-right">{{formatters.toNumberFormat(data.check.basin.avgReservoirTrends.numberReservoirs, 0)}}</td>
												</tr>
												<tr>
													<th>Final/Initial Volume (Max)</th>
													<td class="text-right">{{formatters.toNumberDecimals(data.check.basin.avgReservoirTrends.maxVolume, 3)}}</td>
												</tr>
												<tr>
													<th>Final/Initial Volume (Min)</th>
													<td class="text-right">{{formatters.toNumberDecimals(data.check.basin.avgReservoirTrends.minVolume, 3)}}</td>
												</tr>
												<tr>
													<th>Fraction of Period Empty (Max)</th>
													<td class="text-right">{{formatters.toNumberDecimals(data.check.basin.avgReservoirTrends.fractionEmpty, 3)}}</td>
												</tr>
											</tbody>
										</v-table>
									</v-card-item>
								</v-card>
							</v-col>
						</v-row>
					</template>
				</image-overlays>

				<v-dialog v-model="data.modals.reservoirs" :max-width="constants.dialogSizes.lg" scrollable>
					<v-card title="Detailed Reservoir Performance Output">
						<v-card-item>
							<div v-if="data.check.basin.reservoirRows && data.check.basin.reservoirRows.length < 1" class="mb-5">
								<em>No reservoirs in model.</em>
							</div>
							<div v-else class="table-responsive mb-5">
								<v-table small density="compact">
									<thead>
										<tr>
											<th>RES#</th>
											<th>Sediment</th>
											<th>Phosphorus</th>
											<th>Nitrogen</th>
											<th>Vol. Ratio</th>
											<th>Fraction Empty</th>
											<th>Seepage</th>
											<th>Evap. Loss</th>
										</tr>
									</thead>
									<tbody>
										<tr v-for="(m, i) in data.check.basin.reservoirRows" :key="i">
											<td>{{m.id}}</td>
											<td>{{formatters.toNumberDecimals(m.sediment, 3)}}</td>
											<td>{{formatters.toNumberDecimals(m.phosphorus, 3)}}</td>
											<td>{{formatters.toNumberDecimals(m.nitrogen, 3)}}</td>
											<td>{{formatters.toNumberDecimals(m.volumeRatio, 3)}}</td>
											<td>{{formatters.toNumberDecimals(m.fractionEmpty, 3)}}</td>
											<td>{{formatters.toNumberDecimals(m.seepage, 3)}}</td>
											<td>{{formatters.toNumberDecimals(m.evapLoss, 3)}}</td>
										</tr>
									</tbody>
								</v-table>
							</div>
						</v-card-item>
						<v-divider></v-divider>
						<v-card-actions>
							<v-btn @click="data.modals.reservoirs = false">Close</v-btn>
						</v-card-actions>
					</v-card>
				</v-dialog>

				<action-bar full-width>
					<v-btn variant="flat" @click="nextTab(-1)" class="border mr-2" :disabled="data.page.tabIndex == 0" title="Previous tab"><font-awesome-icon icon="chevron-left" /></v-btn>
					<v-btn variant="flat" @click="nextTab(1)" class="border mr-2" :disabled="data.page.tabIndex == data.page.tabs.length - 1" title="Next tab"><font-awesome-icon icon="chevron-right" /></v-btn>
					<v-menu>
						<template v-slot:activator="{ props }">
							<v-btn type="button" variant="flat" color="primary" class="ml-auto mr-2" v-bind="props">More Actions...</v-btn>
						</template>
						<v-list>
							<v-list-item to="/run"><v-list-item-title>Back to Model Run / Save Scenario</v-list-item-title></v-list-item>
							<swat-plus-toolbox-button :ran-swat="true" as-list-item text="Open SWAT+ Toolbox"></swat-plus-toolbox-button>
							<swat-plus-iahris-button :ran-swat="true" as-list-item text="Open SWAT+ IAHRIS"></swat-plus-iahris-button>
							<open-file as-list-item :file-path="currentResultsPath">Open Results Directory</open-file>
						</v-list>
					</v-menu>
					<v-btn type="button" variant="flat" color="secondary" @click="utilities.exit">Exit SWAT+ Editor</v-btn>
				</action-bar>
			</div>
        </v-main>
    </project-container>
</template>

<style scoped>
	.semi-transparent {
		background-color: rgba(var(--v-theme-surface), 0.75) !important;
	}

	.transparent {
		background-color: transparent !important;
	}

	.details-card {
		width: 350px;
		z-index: 355;
		position: absolute;
		top: 60px;
		max-height: calc(100vh - 147px);
		overflow-y: auto;
	}

	.mgt-card {
		width: 300px;
		z-index: 355;
		position: absolute;
		top: 60px;
		left: 400px;
		background-color: rgba(var(--v-theme-secondary), 0.3) !important;
		height: calc(100vh - 147px);
		overflow-y: auto;
		text-shadow: 0px 0px 8px rgba(var(--v-theme-surface), 1);
	}

	#spcheck_tabs {
		position: fixed;
		top: 0px;
		left: 56px;
		width: calc(100% - 56px);
		z-index: 352;
	}

	.spcheck_tab {
		padding: 2rem;
		height: calc(100vh - 67px);
		min-height: 680px;
		min-width: 1350px;
		overflow-x: auto;
	}

	#spcheck_overview {
		background-image: url('/swatplus-check/sediment_light.png');

		&.dark {
			background-image: url('/swatplus-check/sediment_dark.png');
		}
	}
</style>