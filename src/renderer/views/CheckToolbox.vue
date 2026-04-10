<script setup lang="ts">
	import { reactive, watch, onMounted, computed } from 'vue';
	import { useRoute } from 'vue-router';
	import { useTheme, useDisplay } from 'vuetify';
	import { useHelpers } from '@/helpers';
	import SwatPlusToolboxButton from '../components/SwatPlusToolboxButton.vue';
	import SwatPlusIahrisButton from '../components/SwatPlusIahrisButton.vue';
	
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

		if (data.page.checkByLanduse && !formatters.isNullOrEmpty(data.page.selectedLanduse)) {
			let matches = data.check.landuses.filter((l:any) => l.landuse == data.page.selectedLanduse);
			if (matches.length > 0) {
				let item = matches[0];
				data.page.selectedArea = item.data.area;
				data.page.selectedHruCount = item.data.hrus ? item.data.hrus.length : 0;
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
				<div v-if="data.page.tabIndex == 0" :class="`spcheck_tab ${theme.global.name.value}`" id="spcheck_overview">
					<v-card style="max-width: 800px;" class="semi-transparent" elevation="6">
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

				<div v-if="data.page.tabIndex == 1" :class="`spcheck_tab ${theme.global.name.value}`" id="spcheck_hydrology">
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
										<td>{{formatters.toNumberDecimals(selectedData.etToPrecip, 3)}}</td>
									</tr>
									<tr>
										<th>Deep Recharge/Precipitation</th>
										<td>{{formatters.toNumberDecimals(selectedData.seepToPrecip, 3)}}</td>
									</tr>
									<tr>
										<th>Streamflow/Precipitation</th>
										<td>{{formatters.toNumberDecimals(selectedData.totalFlowToPrecip, 3)}}</td>
									</tr>
									<tr>
										<th>Baseflow/Total Flow</th>
										<td>{{formatters.toNumberDecimals(selectedData.baseflowToTotal, 3)}}</td>
									</tr>
									<tr>
										<th>Surface Runoff/Total Flow</th>
										<td>{{formatters.toNumberDecimals(selectedData.surfaceflowToTotal, 3)}}</td>
									</tr>
									<tr>
										<th>Percolation/Precipitation</th>
										<td>{{formatters.toNumberDecimals(selectedData.percoToPrecip, 3)}}</td>
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

					<div id="hyd_precip" class="value-overlays">
						<div class="label">Precipitation</div>
						<div>{{ formatters.toNumberDecimals(selectedData.precip, 2) }}</div>
					</div>
				</div>

				<div v-if="data.page.tabIndex == 2" :class="`spcheck_tab ${theme.global.name.value}`" id="spcheck_nutrients">

				</div>

				<div v-if="data.page.tabIndex == 3" :class="`spcheck_tab ${theme.global.name.value}`" id="spcheck_sediment">

				</div>

				<div v-if="data.page.tabIndex == 4" :class="`spcheck_tab ${theme.global.name.value}`" id="spcheck_plants">

				</div>

				<v-tabs v-model="data.page.tabIndex" id="spcheck_tabs" align-tabs="center" 
					color="primary" :bg-color="theme.global.name.value == 'dark' ? 'blue-grey-darken-4' : 'blue-grey-lighten-3'">
					<v-tab v-for="(tab, index) in data.page.tabs" :key="index">{{tab}}</v-tab>
				</v-tabs>

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
		max-width: 350px;
		z-index: 449;
		position: absolute;
	}

	.warning-list {
		max-height: 200px;
		overflow-y: auto;
	}

	#spcheck_tabs {
		position: fixed;
		bottom: 100px;
		left: 56px;
		width: calc(100% - 56px);
		z-index: 448;
	}

	.spcheck_tab {
		background-size: cover;
		background-position-x: -30vh;
		background-repeat: no-repeat;
		padding: 2rem;
		height: calc(100vh - 67px);
		position: relative;
		min-height: 500px;
	}

	#spcheck_overview, #spcheck_sediment {
		background-image: url('/swatplus-check/sediment_light.png');

		&.dark {
			background-image: url('/swatplus-check/sediment_dark.png');
		}
	}

	#spcheck_hydrology {
		background-image: url('/swatplus-check/hydrology_light.png');

		&.dark {
			background-image: url('/swatplus-check/hydrology_dark.png');
		}
	}

	#spcheck_nutrients {
		background-image: url('/swatplus-check/nutrients_nitrogen_light.png');

		&.phosphorus {
			background-image: url('/swatplus-check/nutrients_phosphorus_light.png');

			&.dark {
				background-image: url('/swatplus-check/nutrients_phosphorus_dark.png');
			}
		}

		&.dark {
			background-image: url('/swatplus-check/nutrients_nitrogen_dark.png');
		}
	}

	#spcheck_plants {
		background-image: url('/swatplus-check/landuse_overall_light.png');

		&.dark {
			background-image: url('/swatplus-check/landuse_overall_dark.png');
		}
	}

	.value-overlays {
		position: absolute;
		z-index: 450;
		font-size: 0.9rem;
		font-weight: bold;
		text-shadow: 1px 1px 4px rgba(var(--v-theme-surface), 0.8);
	}

	#hyd_precip {
		top: calc(10% + 10vh);
    	left: calc(25% + 5vw + 20vh);
	}
</style>