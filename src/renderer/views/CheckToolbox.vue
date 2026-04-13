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
			],
			checkByLanduse: false,
			selectedLanduse: <string|null>null,
			selectedArea: 0,
			selectedHruCount: 0,
			isOverall: true,
			nutrientsTab: 'nitrogen',
		},
		config: {
			input_files_dir: '',
			input_files_last_written: '',
			swat_last_run: '',
			output_last_imported: ''
		},
		check: <any>{
			info: {},
			basin: {},
			landuses: {},
			mgt: [],
			landuseOptions: []
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

	const selectedData = computed(() => {
		data.page.selectedArea = 0;
		data.page.selectedHruCount = 0;
		data.page.isOverall = true;

		if (data.page.checkByLanduse && !formatters.isNullOrEmpty(data.page.selectedLanduse)) {
			let matches = data.check.landuses.filter((l:any) => l.landuse == data.page.selectedLanduse);
			if (matches.length > 0) {
				let item = matches[0];
				data.page.selectedArea = item.data.area;
				data.page.selectedHruCount = item.data.hrus ? item.data.hrus.length : 0;
				data.page.isOverall = false;
				return item.data.data;
			}
		}

		return data.check.basin;
	})

	onMounted(async () => await get());
	watch(() => route.path, async () => await get())
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
									<v-table small density="compact">
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
									<v-table small density="compact">
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
								<v-autocomplete v-if="data.page.checkByLanduse" hide-details
									v-model="data.page.selectedLanduse" :items="data.check.landuseOptions"
									label="Land use" placeholder="Type to search..."
								></v-autocomplete>
								<div v-if="data.page.checkByLanduse && !formatters.isNullOrEmpty(data.page.selectedLanduse)" class="mt-2 text-subtitle-2">
									{{ data.page.selectedLanduse }} /  
									{{ formatters.toNumberFormat(data.page.selectedArea, 2) }} ha / 
									{{ formatters.toNumberFormat(data.page.selectedHruCount, 0) }} HRUs
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
								<v-autocomplete v-if="data.page.checkByLanduse" hide-details
									v-model="data.page.selectedLanduse" :items="data.check.landuseOptions"
									label="Land use" placeholder="Type to search..."
								></v-autocomplete>
								<div v-if="data.page.checkByLanduse && !formatters.isNullOrEmpty(data.page.selectedLanduse)" class="mt-2 text-subtitle-2">
									{{ data.page.selectedLanduse }} /  
									{{ formatters.toNumberFormat(data.page.selectedArea, 2) }} ha / 
									{{ formatters.toNumberFormat(data.page.selectedHruCount, 0) }} HRUs
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

				<div v-if="data.page.tabIndex == 3" :class="`spcheck_tab ${theme.global.name.value}`" id="spcheck_sediment">

				</div>

				<div v-if="data.page.tabIndex == 4" :class="`spcheck_tab ${theme.global.name.value}`" id="spcheck_plants">

				</div>

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
		background-color: rgba(var(--v-theme-surface), 0.7) !important;
	}

	.transparent {
		background-color: transparent !important;
	}

	.details-card {
		width: 350px;
		z-index: 355;
		position: absolute;
		top: 60px
	}

	.warning-list {
		max-height: 200px;
		overflow-y: auto;
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

	#spcheck_overview, #spcheck_sediment {
		background-image: url('/swatplus-check/sediment_light.png');

		&.dark {
			background-image: url('/swatplus-check/sediment_dark.png');
		}
	}
</style>