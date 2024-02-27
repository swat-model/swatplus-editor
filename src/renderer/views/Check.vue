<script setup lang="ts">
	import { reactive, watch, onMounted } from 'vue';
	import { useRoute } from 'vue-router';
	import { useHelpers } from '@/helpers';
	
	const route = useRoute();
	const { api, constants, errors, formatters, runProcess, utilities, currentProject } = useHelpers();

	let data:any = reactive({
		page: {
			loading: false,
			error: null,
			show: {
				info: true,
				hyd: false
			},
			tabIndex: 0,
			tabs: [
				"Information",
				"Hydrology",
				"Sediment",
				"Nitrogen Cycle",
				"Phosphorus Cycle",
				"Plant Growth",
				"Landscape Nutrient Losses",
				"Land Use Summary",
				"Instream Processes",
				"Point Sources",
				"Reservoirs"
			]
		},
		config: {
			input_files_dir: null,
			input_files_last_written: null,
			swat_last_run: null,
			output_last_imported: null
		},
		check: {
			setup: {},
			hydrology: {},
			nitrogenCycle: {},
			phosphorusCycle: {},
			plantGrowth: {},
			landscapeNutrientLosses: {},
			landUseSummary: {},
			pointSources: {},
			reservoirs: {},
			instreamProcesses: {},
			sediment: {},
		},
		modals: {
			hydrology: {
				monthlyBasinValues: false,
				baseflowMap: false
			},
			reservoirs: {
				table: false
			}
		}
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
				const response2 = await api.put(`setup/swatplus-check`, formData, currentProject.getApiHeader());
				errors.log(response2.data);

				if (response2.data.error) {
					data.page.error = response2.data.error;
				} else {
					data.check = response2.data;

					if (!response.data.has_observed_weather) {
						data.check.hydrology.warnings.push('You are using simulated precipitation data; if you intend to calibrate, you should used measured precipitation data');
					}

					if (response.data.print.prt.nyskip < 1) {
						data.check.hydrology.warnings.push('It is highly recomended that you use at least 1 year of model warmup; 2-5 years is better');
					}

					if (data.check.setup.swatVersion === 'development') {
						data.check.setup.swatVersion = constants.appSettings.swatplus;
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

	onMounted(async () => await get());
	watch(() => route.path, async () => await get())
</script>

<template>
	<project-container :loading="data.page.loading" add-error-frame>
		<v-navigation-drawer permanent id="secondary-nav" v-if="!currentProject.isLte && formatters.isNullOrEmpty(data.page.error) && !formatters.isNullOrEmpty(data.config.output_last_imported)">
			<v-list :lines="false" density="compact" nav>
				<v-list-item v-for="(t, i) in data.page.tabs" :key="i"
					@click.prevent="data.page.tabIndex = i" :active="data.page.tabIndex == i" :title="t"></v-list-item>
			</v-list>
		</v-navigation-drawer>

		<v-main>
			<div class="py-3 px-6">
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
				<div v-else>
					<h1 class="text-h5 mb-6">SWAT+ Check {{data.page.tabIndex > 0 ? '/ ' + data.page.tabs[data.page.tabIndex] : ''}}</h1>

					<div v-if="data.page.tabIndex == 0" title="Information">
						<p>
							SWAT+ Check reads model output from a SWAT+ project and performs many simple checks to identify 
							potential model problems. The intended purpose of this program is to identify model problems early in the 
							modeling process. Hidden model problems often result in the need to recalibrate or regenerate a model, 
							resulting in an avoidable waste of time. This program is designed to compare a variety of SWAT+ outputs to 
							nominal ranges based on the judgment of model developers. A warning does not necessarily indicate a problem; 
							the purpose is to bring attention to unusual predictions. This software also provides a visual representation 
							of various model outputs to aid novice users.
						</p>

						<v-row>
							<v-col cols="12" md="6">
								<v-table small density="compact">
									<tbody>
										<tr>
											<th>Model Version</th>
											<td>SWAT+ rev. {{data.check.setup.swatVersion}}</td>
										</tr>
										<tr>
											<th>Simulation Length</th>
											<td>{{data.check.setup.simulationLength}} years</td>
										</tr>
										<tr>
											<th>Warm-up</th>
											<td>{{data.check.setup.warmUp}} years</td>
										</tr>
										<tr>
											<th>Weather</th>
											<td>{{data.check.setup.weatherMethod}}</td>
										</tr>
									</tbody>
								</v-table>
							</v-col>
							<v-col cols="12" md="6">
								<v-table small density="compact">
									<tbody>
										<tr>
											<th>Watershed Area</th>
											<td>{{formatters.toNumberFormat(data.check.setup.watershedArea, 2)}} ha</td>
										</tr>
										<tr>
											<th>HRUs</th>
											<td>{{formatters.toNumberFormat(data.check.setup.hrus, 0)}}</td>
										</tr>
										<tr>
											<th>LSUs</th>
											<td>{{formatters.toNumberFormat(data.check.setup.lsus, 0)}}</td>
										</tr>
										<tr>
											<th>Subbasins</th>
											<td>{{formatters.toNumberFormat(data.check.setup.subbasins, 0)}}</td>
										</tr>
									</tbody>
								</v-table>
							</v-col>
						</v-row>
					</div>

					<div v-if="data.page.tabIndex == 1" title="Hydrology">
						<p>
							Realistic hydrology is the foundation of any model.  Pay particular attention to evapotranspiration, baseflow and surface runoff ratios.
							Baseflow/streamflow ratios for the US are provided by the USGS, these data are accessible via the button below.
							The ranges specified here are general guidelines only, and may not apply to your simulation area.
						</p>
						
						<v-alert v-if="data.check.hydrology.warnings && data.check.hydrology.warnings.length > 0" variant="tonal" color="info" border="start" class="my-4">
							<p class="font-weight-bold mb-0">Messages and Warnings</p>
							<ul class="mb-0">
								<li v-for="(warning, i) in data.check.hydrology.warnings" :key="i">{{warning}}</li>
							</ul>
						</v-alert>

						<v-row>
							<v-col cols="12" xl="6">
								<div id="hydrology" class="picture-holder">
									<span id="pet">PET<br />{{formatters.toNumberFormat(data.check.hydrology.pet, 2)}}</span>
									<span id="et">{{formatters.toNumberFormat(data.check.hydrology.et, 2)}}</span>
									<span id="etPlant">Plant ET<br />{{formatters.toNumberFormat(data.check.hydrology.etPlant, 2)}}</span>
									<span id="etSoil">Soil ET<br />{{formatters.toNumberFormat(data.check.hydrology.etSoil, 2)}}</span>
									<span id="precip">{{formatters.toNumberFormat(data.check.hydrology.precipitation, 2)}}</span>
									<span id="irrigation">Irrigation<br />{{formatters.toNumberFormat(data.check.hydrology.irrigation, 2)}}</span>
									<span id="tile">Tile<br />{{formatters.toNumberFormat(data.check.hydrology.tile, 2)}}</span>
									<span id="cn">Average Curve Number<br />{{formatters.toNumberFormat(data.check.hydrology.averageCn, 2)}}</span>
									<span id="surfacerunoff">{{formatters.toNumberFormat(data.check.hydrology.surfaceRunoff, 2)}}</span>
									<span id="lateralflow">{{formatters.toNumberFormat(data.check.hydrology.lateralFlow, 2)}}</span>
									<span id="returnflow">{{formatters.toNumberFormat(data.check.hydrology.returnFlow, 2)}}</span>
									<span id="perc">{{formatters.toNumberFormat(data.check.hydrology.percolation, 2)}}</span>
									<span id="revap">{{formatters.toNumberFormat(data.check.hydrology.revap, 2)}}</span>
									<span id="recharge">{{formatters.toNumberFormat(data.check.hydrology.recharge, 2)}}</span>
									<span id="hydrology-units">All Units mm</span>
								</div>
							</v-col>
							<v-col cols="12" xl="6">
								<p class="font-weight-bold">Water Balance Ratios</p>
								<v-table small density="compact">
									<tbody>
										<tr>
											<th>Streamflow/Precipitation</th>
											<td>{{formatters.toNumberFormat(data.check.hydrology.streamflowPrecipitation, 2)}}</td>
										</tr>
										<tr>
											<th>Baseflow/Total Flow</th>
											<td>{{formatters.toNumberFormat(data.check.hydrology.baseflowTotalFlow, 2)}}</td>
										</tr>
										<tr>
											<th>Surface Runoff/Total Flow</th>
											<td>{{formatters.toNumberFormat(data.check.hydrology.surfaceRunoffTotalFlow, 2)}}</td>
										</tr>
										<tr>
											<th>Percolation/Precipitation</th>
											<td>{{formatters.toNumberFormat(data.check.hydrology.percolationPrecipitation, 2)}}</td>
										</tr>
										<tr>
											<th>Deep Recharge/Precipitation</th>
											<td>{{formatters.toNumberFormat(data.check.hydrology.deepRechargePrecipitation, 2)}}</td>
										</tr>
										<tr>
											<th>ET/Precipitation</th>
											<td>{{formatters.toNumberFormat(data.check.hydrology.etPrecipitation, 2)}}</td>
										</tr>
									</tbody>
								</v-table>
							</v-col>
						</v-row>
					</div>
					<div v-if="data.page.tabIndex == 2" title="Sediment">
						<p>
							Sediment loss form the landscape is dependent upon many factors.  Sediment overestimation in SWAT+ is most commonly due to 
							inadequate biomass production.  This often occurs on specific land uses.  If your maximum upland sediment yield is excessive, 
							use the landuse summary tab to identify the problem land use.
						</p>

						<p>
							SWAT+ also modifies sediments to account for in-stream deposition and erosion of stream banks and channels.  
							Often there is little or no measured data to differentiate between upland sediment and in-stream sediment changes. 
							Streams may be either a net source of sediment, or a sink.  In-stream sediment modification is impacted by physical channel 
							characteristic’s (slope, width, depth, channel cover, and substrate characteristics) and the quantity of sediment and flow 
							from upstream.
						</p>

						<v-alert v-if="data.check.sediment.warnings && data.check.sediment.warnings.length > 0" variant="tonal" color="info" border="start" class="my-4">
							<p class="font-weight-bold mb-0">Messages and Warnings</p>
							<ul class="mb-0">
								<li v-for="(warning, i) in data.check.sediment.warnings" :key="i">{{warning}}</li>
							</ul>
						</v-alert>

						<div id="sediment" class="picture-holder">
							<span id="maxupland">Maximum Upland Sediment Yield<br /> {{formatters.toNumberFormat(data.check.sediment.maxUplandSedimentYield, 2)}} Mg/ha</span>
							<span id="surfacerunoffsed">Surface Runoff<br /> {{formatters.toNumberFormat(data.check.sediment.surfaceRunoff, 2)}} mm/yr</span>
							<span id="avgupland">Average Upland Sediment Yield<br /> {{formatters.toNumberFormat(data.check.sediment.avgUplandSedimentYield, 2)}} Mg/ha</span>
							<span id="inletsed">Inlet/Point Sources Sediment<br /> {{formatters.toNumberFormat(data.check.sediment.inletSediment, 2)}} Mg/year</span>
							<span id="instreamsed">Instream Sediment Change<br /> {{formatters.toNumberFormat(data.check.sediment.inStreamSedimentChange, 2)}} Mg/ha</span>
						</div>
					</div>
					<div v-if="data.page.tabIndex == 3" title="Nitrogen Cycle">
						<p>
							The nitrogen cycle is key to biomass production, which in turn impacts ET and sediment yield.
							The nitrogen cycle is complex, it is generally not possible to validate these routines outside a research setting.
							Of particular importance are the total applied nitrogen fertilizer and losses due to plant uptake, and volatilization and denitrification.
							Soils contain a large amount of organic nitrogen in the form of organic matter.  Large changes in initial and final nitrogen contents
							(in particular organic n) may indicate under or over fertilization during the simulation.
						</p>

						<v-alert v-if="data.check.nitrogenCycle.warnings && data.check.nitrogenCycle.warnings.length > 0" variant="tonal" color="info" border="start" class="my-4">
							<p class="font-weight-bold mb-0">Messages and Warnings</p>
							<ul class="mb-0">
								<li v-for="(warning, i) in data.check.nitrogenCycle.warnings" :key="i">{{warning}}</li>
							</ul>
						</v-alert>

						<div id="ncycle" class="picture-holder">
							<span id="initno3">
								Initial NO<sub>3</sub>: {{formatters.toNumberFormat(data.check.nitrogenCycle.initialNO3, 2)}}<br />
								Final NO<sub>3</sub>: {{formatters.toNumberFormat(data.check.nitrogenCycle.finalNO3, 2)}}
							</span>
							<span id="volatilization">{{formatters.toNumberFormat(data.check.nitrogenCycle.volatilization, 2)}}</span>
							<span id="nfix">{{formatters.toNumberFormat(data.check.nitrogenCycle.nFixation, 2)}}</span>
							<span id="denit">{{formatters.toNumberFormat(data.check.nitrogenCycle.denitrification, 2)}}</span>
							<span id="inorgnh4">{{formatters.toNumberFormat(data.check.nitrogenCycle.nH4InOrgNFertilizer, 2)}}</span>
							<span id="inorgno3">{{formatters.toNumberFormat(data.check.nitrogenCycle.nO3InOrgNFertilizer, 2)}}</span>
							<span id="nplantuptake">{{formatters.toNumberFormat(data.check.nitrogenCycle.plantUptake, 2)}}</span>
							<span id="nitrification">{{formatters.toNumberFormat(data.check.nitrogenCycle.nitrification, 2)}}</span>
							<span id="nmineralization">{{formatters.toNumberFormat(data.check.nitrogenCycle.mineralization, 2)}}</span>
							<span id="initorgn">
								Initial Org N: {{formatters.toNumberFormat(data.check.nitrogenCycle.initialOrgN, 2)}}<br />
								Final Org N: {{formatters.toNumberFormat(data.check.nitrogenCycle.finalOrgN, 2)}}
							</span>
							<span id="orgn">{{formatters.toNumberFormat(data.check.nitrogenCycle.orgNFertilizer, 2)}}</span>
							<span id="activetostable">{{formatters.toNumberFormat(data.check.nitrogenCycle.activeToStableOrgN, 2)}}</span>
							<span id="nresidue">{{formatters.toNumberFormat(data.check.nitrogenCycle.residueMineralization, 2)}}</span>
							<span id="totaln">Total Fertilizer N: {{formatters.toNumberFormat(data.check.nitrogenCycle.totalFertilizerN, 2)}}</span>

							<span id="ncycle-units">All units kg/ha</span>
						</div>
					</div>
					<div v-if="data.page.tabIndex == 4" title="Phosphorus Cycle">
						<p>
							The phosphorus cycle is of particular interest in watersheds with significant animal manure application.
							Soils contain a large reservoir of both mineral and organic phosphorus.  Large increases in mineral phosphorus
							content during the simulation often result from overfertilization with either commercial or manure phosphorus sources.
							This also means that phosphorus concentrations in runoff also increase during the simulation period.
							Plant uptake is the dominant loss pathway for soil phosphorus under most conditions.
						</p>

						<v-alert v-if="data.check.phosphorusCycle.warnings && data.check.phosphorusCycle.warnings.length > 0" variant="tonal" color="info" border="start" class="my-4">
							<p class="font-weight-bold mb-0">Messages and Warnings</p>
							<ul class="mb-0">
								<li v-for="(warning, i) in data.check.phosphorusCycle.warnings" :key="i">{{warning}}</li>
							</ul>
						</v-alert>

						<div id="pcycle" class="picture-holder">
							<span id="minp">
								Initial Min P: {{formatters.toNumberFormat(data.check.phosphorusCycle.initialMinP, 2)}}<br />
								Final Min P: {{formatters.toNumberFormat(data.check.phosphorusCycle.finalMinP, 2)}}
							</span>
							<span id="orgp">
								Initial Org P: {{formatters.toNumberFormat(data.check.phosphorusCycle.initialOrgP, 2)}}<br />
								Final Org P: {{formatters.toNumberFormat(data.check.phosphorusCycle.finalOrgP, 2)}}
							</span>
							<span id="totalp">Total Fertilizer P: {{formatters.toNumberFormat(data.check.phosphorusCycle.totalFertilizerP, 2)}}</span>
							<span id="inorgp">{{formatters.toNumberFormat(data.check.phosphorusCycle.inOrgPFertilizer, 2)}}</span>
							<span id="pplantuptake">{{formatters.toNumberFormat(data.check.phosphorusCycle.plantUptake, 2)}}</span>
							<span id="pstableactive">{{formatters.toNumberFormat(data.check.phosphorusCycle.stableActive, 2)}}</span>
							<span id="pactivesol">{{formatters.toNumberFormat(data.check.phosphorusCycle.activeSolution, 2)}}</span>
							<span id="pmineralization">{{formatters.toNumberFormat(data.check.phosphorusCycle.mineralization, 2)}}</span>
							<span id="orgpfert">{{formatters.toNumberFormat(data.check.phosphorusCycle.orgPFertilizer, 2)}}</span>
							<span id="presidue">{{formatters.toNumberFormat(data.check.phosphorusCycle.residueMineralization, 2)}}</span>

							<span id="pcycle-units">All units kg/ha</span>
						</div>
					</div>
					<div v-if="data.page.tabIndex == 5" title="Plant Growth">
						<p>
							Proper plant growth is key to accurate runoff and sediment predictions.  Problems in plant growth are often related to excessive
							stress due to temperature or the lack of water/nutrients.  The data presented here are basin averages, and may not reflect problems
							with individual land uses.  Carefully review the land use summary tab.
						</p>

						<v-row>
							<v-col cols="12" md="6">
								<v-alert v-if="data.check.plantGrowth.warnings && data.check.plantGrowth.warnings.length > 0" variant="tonal" color="info" border="start" class="my-4">
									<p class="font-weight-bold mb-0">Messages and Warnings</p>
									<ul class="mb-0">
										<li v-for="(warning, i) in data.check.plantGrowth.warnings" :key="i">{{warning}}</li>
									</ul>
								</v-alert>

								<v-table small density="compact">
									<tbody>
										<tr>
											<th>Temperature Stress Days</th>
											<td>{{formatters.toNumberFormat(data.check.plantGrowth.tempStressDays, 2)}}</td>
										</tr>
										<tr>
											<th>Water Stress Days</th>
											<td>{{formatters.toNumberFormat(data.check.plantGrowth.waterStressDays, 2)}}</td>
										</tr>
										<tr>
											<th>Nitrogen Stress Days</th>
											<td>{{formatters.toNumberFormat(data.check.plantGrowth.nStressDays, 2)}}</td>
										</tr>
										<tr>
											<th>Phosphorus Stress Days</th>
											<td>{{formatters.toNumberFormat(data.check.plantGrowth.pStressDays, 2)}}</td>
										</tr>
										<tr>
											<th>Soil Air Stress Days</th>
											<td>{{formatters.toNumberFormat(data.check.plantGrowth.soilAirStressDays, 2)}}</td>
										</tr>
									</tbody>
								</v-table>
							</v-col>
							<v-col cols="12" md="6">
								<div id="plantgrowth" class="picture-holder">
									<span id="plantavg">
										Average Biomass: {{formatters.toNumberFormat(data.check.plantGrowth.avgBiomass, 2)}} kg/ha<br />
										Average Yield: {{formatters.toNumberFormat(data.check.plantGrowth.avgYield, 2)}} kg/ha
									</span>
									<span id="npremoved">
										N Removed in Yield: {{formatters.toNumberFormat(data.check.plantGrowth.nRemoved, 2)}} kg/ha<br />
										P Removed in Yield: {{formatters.toNumberFormat(data.check.plantGrowth.pRemoved, 2)}} kg/ha
									</span>
									<span id="totalnp">
										Total Fertilizer N: {{formatters.toNumberFormat(data.check.plantGrowth.totalFertilizerN, 2)}} kg/ha<br />
										Total Fertilizer P: {{formatters.toNumberFormat(data.check.plantGrowth.totalFertilizerP, 2)}} kg/ha
									</span>
									<span id="plantuptakenp">
										Plant Uptake N: {{formatters.toNumberFormat(data.check.plantGrowth.plantUptakeN, 2)}} kg/ha<br />
										Plant Uptake P: {{formatters.toNumberFormat(data.check.plantGrowth.plantUptakeP, 2)}} kg/ha
									</span>
								</div>
							</v-col>
						</v-row>
					</div>
					<div v-if="data.page.tabIndex == 6" title="Landscape Nutrient Losses">
						<p>
							Nutrient losses are a critical aspect of many studies.  The data presented here are losses from the landscape surface, which is delivered to reaches.
							These are basin averages. The link below contains a summary of edge of field nutrient losses from monitoring studies by individual crops.
							These data can be compared to SWAT+ predictions to verify the appropriate magnitude of predicted losses.
						</p>

						<v-alert v-if="data.check.landscapeNutrientLosses.warnings && data.check.landscapeNutrientLosses.warnings.length > 0" variant="tonal" color="info" border="start" class="my-4">
							<p class="font-weight-bold mb-0">Messages and Warnings</p>
							<ul class="mb-0">
								<li v-for="(warning, i) in data.check.landscapeNutrientLosses.warnings" :key="i">{{warning}}</li>
							</ul>
						</v-alert>

						<v-row>
							<v-col cols="12" md="6">
								<p class="font-weight-bold">Nitrogen Losses (kg/ha)</p>
								<v-table small density="compact">
									<tbody>
										<tr>
											<th>Total N Loss</th>
											<td>{{formatters.toNumberFormat(data.check.landscapeNutrientLosses.nLosses.totalLoss, 2)}}</td>
										</tr>
										<tr>
											<th>Organic N</th>
											<td>{{formatters.toNumberFormat(data.check.landscapeNutrientLosses.nLosses.orgN, 2)}}</td>
										</tr>
										<tr>
											<th>Nitrate Surface Runoff</th>
											<td>{{formatters.toNumberFormat(data.check.landscapeNutrientLosses.nLosses.surfaceRunoff, 2)}}</td>
										</tr>
										<tr>
											<th>Nitrate Leached</th>
											<td>{{formatters.toNumberFormat(data.check.landscapeNutrientLosses.nLosses.leached, 2)}}</td>
										</tr>
										<tr>
											<th>Nitrate Lateral Flow</th>
											<td>{{formatters.toNumberFormat(data.check.landscapeNutrientLosses.nLosses.lateralFlow, 2)}}</td>
										</tr>
										<tr>
											<th>Nitrate Groundwater Yield</th>
											<td>{{formatters.toNumberFormat(data.check.landscapeNutrientLosses.nLosses.groundwaterYield, 2)}}</td>
										</tr>
										<tr>
											<th>Solubility Ratio in Runoff</th>
											<td>{{formatters.toNumberFormat(data.check.landscapeNutrientLosses.nLosses.solubilityRatio, 2)}}</td>
										</tr>
									</tbody>
								</v-table>
							</v-col>
							<v-col cols="12" md="6">
								<p class="font-weight-bold">Phosphorus Losses (kg/ha)</p>
								<v-table small density="compact">
									<tbody>
										<tr>
											<th>Total P Loss</th>
											<td>{{formatters.toNumberFormat(data.check.landscapeNutrientLosses.pLosses.totalLoss, 2)}}</td>
										</tr>
										<tr>
											<th>Organic P</th>
											<td>{{formatters.toNumberFormat(data.check.landscapeNutrientLosses.pLosses.orgP, 2)}}</td>
										</tr>
										<tr>
											<th>Soluble P Surface Runoff</th>
											<td>{{formatters.toNumberFormat(data.check.landscapeNutrientLosses.pLosses.surfaceRunoff, 2)}}</td>
										</tr>
										<tr>
											<th>Solubility Ratio in Runoff</th>
											<td>{{formatters.toNumberFormat(data.check.landscapeNutrientLosses.pLosses.solubilityRatio, 2)}}</td>
										</tr>
									</tbody>
								</v-table>
							</v-col>
						</v-row>

						<p class="font-weight-bold mt-6">Measured Nutrient Losses by Crop and Tillage</p>
						<p>
							From Harmel, D., et al.  2006 Compilation of Measured Nutrient Load Data for Agricultural Land Uses in the United States. <em>Journal of the American Water Resources Association</em> 42(5):1163-1178.
						</p>
						<p>
							<img class="img-fluid" :src="`/swat-check/nut_croptype2.png`" alt="nut_croptype2.png" />
						</p>
						<p>
							<img class="img-fluid" :src="`/swat-check/nut_croptype3.png`" alt="nut_croptype3.png" />
						</p>
					</div>
					<div v-if="data.page.tabIndex == 7" title="Land Use Summary">
						<p>
							Model errors are often isolated to a particular land use type.  If the land use is relatively minor, these issues
							may go unnoticed at the basin outlet during calibration.  Often, these minor land uses are the focus of scenario
							development, and errors become apparent after the investment of much calibration effort.
						</p>
						
						<v-alert v-if="data.check.landUseSummary.warnings && data.check.landUseSummary.warnings.length > 0" variant="tonal" color="info" border="start" class="my-4">
							<p class="font-weight-bold mb-0">Messages and Warnings</p>
							<ul class="mb-0">
								<li v-for="(warning, i) in data.check.landUseSummary.warnings" :key="i">{{warning}}</li>
							</ul>
						</v-alert>

						<p class="font-weight-bold">Summary by Reported Land Use</p>
						<p>
							This table contains a few important predictions summarized by land use.  These should be reviewed carefully.
						</p>

						<div>
							<v-table small density="compact">
								<thead>
									<tr>
										<th>LULC</th>
										<th>AREA ha</th>
										<th>CN</th>
										<th>AWC mm</th>
										<th>USLE_LS</th>
										<th>IRR mm</th>
										<th>PREC mm</th>
										<th>SURQ mm</th>
										<th>ET mm</th>
										<th>SED th</th>
										<th>NO3 kgh</th>
										<th>ORGN kgh</th>
										<th>BIOM th</th>
										<th>YLD th</th>
									</tr>
								</thead>
								<tbody>
									<tr v-for="(m, i) in data.check.landUseSummary.landUseRows" :key="i">
										<td>{{m.landUse}}</td>
										<td>{{formatters.toNumberFormat(m.area, 2)}}</td>
										<td>{{formatters.toNumberFormat(m.cn, 2)}}</td>
										<td>{{formatters.toNumberFormat(m.awc, 2)}}</td>
										<td>{{formatters.toNumberFormat(m.usle_ls, 2)}}</td>
										<td>{{formatters.toNumberFormat(m.irr, 2)}}</td>
										<td>{{formatters.toNumberFormat(m.prec, 2)}}</td>
										<td>{{formatters.toNumberFormat(m.surq, 2)}}</td>
										<td>{{formatters.toNumberFormat(m.et, 2)}}</td>
										<td>{{formatters.toNumberFormat(m.sed, 2)}}</td>
										<td>{{formatters.toNumberFormat(m.no3, 2)}}</td>
										<td>{{formatters.toNumberFormat(m.orgn, 2)}}</td>
										<td>{{formatters.toNumberFormat(m.biom, 2)}}</td>
										<td>{{formatters.toNumberFormat(m.yld, 2)}}</td>
									</tr>
								</tbody>
							</v-table>
						</div>

						<div v-if="data.check.landUseSummary.hruLevelWarnings.length > 0">
							<p class="font-weight-bold">HRU Level Warnings</p>
							<p>
								These are provided only to help isolate problem HRUs within a particular land use.
								We do not recommend that these be used during routine checking of model output.
							</p>
							<ul>
								<li v-for="(warning, i) in data.check.landUseSummary.hruLevelWarnings" :key="i">{{warning}}</li>
							</ul>
						</div>
					</div>
					<div v-if="data.page.tabIndex == 8" title="Instream Processes">
						<p>
							In-stream processes may have a large impact on sediment and nutrient loads.  It is difficult to gage appropriate values for these outputs.
							In-stream sediment change can be either positive or negative.  Typically streams are a net sink for nutrients.
							Channel geomorphology can provide some guidance as to the net contribution of in-stream processes.
						</p>

						<v-alert v-if="data.check.instreamProcesses.warnings && data.check.instreamProcesses.warnings.length > 0" variant="tonal" color="info" border="start" class="my-4">
							<p class="font-weight-bold mb-0">Messages and Warnings</p>
							<ul class="mb-0">
								<li v-for="(warning, i) in data.check.instreamProcesses.warnings" :key="i">{{warning}}</li>
							</ul>
						</v-alert>

						<v-row>
							<v-col cols="12" md="6">
								<p class="font-weight-bold">Reach Report: Delivery ratio of segment (%)</p>
								<v-data-table small density="compact"
									:items="data.check.instreamProcesses.reaches" :items-per-page="10"
									:headers="[{ key: 'id', title: 'RCH#' }, { key: 'sediment', title: 'Sediment' }, { key: 'phosphorus', title: 'Phosphorus' }, { key: 'nitrogen', title: 'Nitrogen' }]">
									<template v-slot:item.sediment="{ value }">
										{{formatters.toNumberFormat(value, 2)}}
									</template>
									<template v-slot:item.phosphorus="{ value }">
										{{formatters.toNumberFormat(value, 2)}}
									</template>
									<template v-slot:item.nitrogen="{ value }">
										{{formatters.toNumberFormat(value, 2)}}
									</template>
								</v-data-table>
							</v-col>
							<v-col cols="12" md="6">
								<p class="font-weight-bold">Sediment Budget</p>
								<v-table small density="compact" class="instream mb-4">
									<tbody>
										<tr>
											<th>Upland Sediment Yield</th>
											<td>{{formatters.toNumberFormat(data.check.instreamProcesses.uplandSedimentYield, 2)}}</td>
											<td class="min">Mg/ha</td>
										</tr>
										<tr>
											<th>Instream Sediment Change</th>
											<td>{{formatters.toNumberFormat(data.check.instreamProcesses.instreamSedimentChange, 2)}}</td>
											<td class="min">Mg/ha</td>
										</tr>
										<tr>
											<th>Channel Erosion</th>
											<td>{{formatters.toNumberFormat(data.check.instreamProcesses.channelErosion, 2)}}</td>
											<td class="min">%</td>
										</tr>
										<tr>
											<th>Channel Deposition</th>
											<td>{{formatters.toNumberFormat(data.check.instreamProcesses.channelDeposition, 2)}}</td>
											<td class="min">%</td>
										</tr>
									</tbody>
								</v-table>

								<p class="font-weight-bold">Instream Nutrient Modification</p>
								<v-table small density="compact" class="instream mb-4">
									<tbody>
										<tr>
											<th>Total Nitrogen</th>
											<td>{{formatters.toNumberFormat(data.check.instreamProcesses.totalN, 2)}}</td>
											<td class="min">%</td>
										</tr>
										<tr>
											<th>Total Phosphorus</th>
											<td>{{formatters.toNumberFormat(data.check.instreamProcesses.totalP, 2)}}</td>
											<td class="min">%</td>
										</tr>
									</tbody>
								</v-table>

								<p class="font-weight-bold">Instream Water Budget</p>
								<v-table small density="compact" class="instream mb-4">
									<tbody>
										<tr>
											<th>Total Streamflow Losses</th>
											<td>{{formatters.toNumberFormat(data.check.instreamProcesses.totalStreamflowLosses, 2)}}</td>
											<td class="min">%</td>
										</tr>
										<tr>
											<th>Evaporation Loss</th>
											<td>{{formatters.toNumberFormat(data.check.instreamProcesses.evaporationLoss, 2)}}</td>
											<td class="min">%</td>
										</tr>
										<tr>
											<th>Seepage Loss</th>
											<td>{{formatters.toNumberFormat(data.check.instreamProcesses.seepageLoss, 2)}}</td>
											<td class="min">%</td>
										</tr>
									</tbody>
								</v-table>
							</v-col>
						</v-row>
					</div>
					<div v-if="data.page.tabIndex == 9" title="Point Sources">
						<p>
							Point sources constantly discharge pollutants to streams.  These are an optional feature in SWAT+.
							These summaries are presented so that the relative contribution of these sources can be verified.
							Point sources contributions are so varied that there is no reasonable range which can be applied to all basins.
						</p>

						<v-alert v-if="data.check.pointSources.warnings && data.check.pointSources.warnings.length > 0" variant="tonal" color="info" border="start" class="my-4">
							<p class="font-weight-bold mb-0">Messages and Warnings</p>
							<ul class="mb-0">
								<li v-for="(warning, i) in data.check.pointSources.warnings" :key="i">{{warning}}</li>
							</ul>
						</v-alert>

						<v-row>
							<v-col cols="12" lg="4">
								<p class="font-weight-bold">Total Subbasin Load</p>
								<v-table small density="compact" class="mb-4">
									<tbody>
										<tr>
											<th>Flow</th>
											<td>{{formatters.toNumberFormat(data.check.pointSources.subbasinLoad.flow, 4)}}</td>
											<td>cms</td>
										</tr>
										<tr>
											<th>Sediment</th>
											<td>{{formatters.toNumberFormat(data.check.pointSources.subbasinLoad.sediment, 2)}}</td>
											<td>Mg/yr</td>
										</tr>
										<tr>
											<th>Nitrogen</th>
											<td>{{formatters.toNumberFormat(data.check.pointSources.subbasinLoad.nitrogen, 2)}}</td>
											<td>kg/yr</td>
										</tr>
										<tr>
											<th>Phosphorus</th>
											<td>{{formatters.toNumberFormat(data.check.pointSources.subbasinLoad.phosphorus, 2)}}</td>
											<td>kg/yr</td>
										</tr>
									</tbody>
								</v-table>
							</v-col>
							<v-col cols="12" lg="4">
								<p class="font-weight-bold">Total Point Source + Inlet Load</p>
								<v-table small density="compact" class="mb-4">
									<tbody>
										<tr>
											<th>Flow</th>
											<td>{{formatters.toNumberFormat(data.check.pointSources.pointSourceInletLoad.flow, 2)}}</td>
											<td>cms</td>
										</tr>
										<tr>
											<th>Sediment</th>
											<td>{{formatters.toNumberFormat(data.check.pointSources.pointSourceInletLoad.sediment, 2)}}</td>
											<td>Mg/yr</td>
										</tr>
										<tr>
											<th>Nitrogen</th>
											<td>{{formatters.toNumberFormat(data.check.pointSources.pointSourceInletLoad.nitrogen, 2)}}</td>
											<td>kg/yr</td>
										</tr>
										<tr>
											<th>Phosphorus</th>
											<td>{{formatters.toNumberFormat(data.check.pointSources.pointSourceInletLoad.phosphorus, 2)}}</td>
											<td>kg/yr</td>
										</tr>
									</tbody>
								</v-table>
							</v-col>
							<v-col cols="12" lg="4">
								<p class="font-weight-bold">Load from Inlet + PS (%)</p>
								<v-table small density="compact" class="mb-4">
									<tbody>
										<tr>
											<th>Flow</th>
											<td>{{formatters.toNumberFormat(data.check.pointSources.fromInletAndPointSource.flow, 2)}}</td>
											<td>%</td>
										</tr>
										<tr>
											<th>Sediment</th>
											<td>{{formatters.toNumberFormat(data.check.pointSources.fromInletAndPointSource.sediment, 2)}}</td>
											<td>%</td>
										</tr>
										<tr>
											<th>Nitrogen</th>
											<td>{{formatters.toNumberFormat(data.check.pointSources.fromInletAndPointSource.nitrogen, 2)}}</td>
											<td>%</td>
										</tr>
										<tr>
											<th>Phosphorus</th>
											<td>{{formatters.toNumberFormat(data.check.pointSources.fromInletAndPointSource.phosphorus, 2)}}</td>
											<td>%</td>
										</tr>
									</tbody>
								</v-table>
							</v-col>
						</v-row>
					</div>
					<div v-if="data.page.tabIndex == 10" title="Reservoirs">
						<p>
							Reservoirs are an optional feature in SWAT+.   The hydrology of basins with large reservoirs may be completely dominated by reservoir processes and release rates.
							The data presented below is an average of all reservoirs; <a href="#" @click.prevent="data.modals.reservoirs.table = true">see data for individual reservoirs</a>.
							The statistics presented here are designed to identify common reservoir issues.   The use of user specified release rate may cause a reservoir to
							grow continuously or run completely dry.  These common issues can be detected via the final/initial volume ratio and fraction of period empty statistics below.
						</p>

						<v-alert v-if="data.check.reservoirs.warnings && data.check.reservoirs.warnings.length > 0" variant="tonal" color="info" border="start" class="my-4">
							<p class="font-weight-bold mb-0">Messages and Warnings</p>
							<ul class="mb-0">
								<li v-for="(warning, i) in data.check.reservoirs.warnings" :key="i">{{warning}}</li>
							</ul>
						</v-alert>

						<v-dialog v-model="data.modals.reservoirs.table" :max-width="constants.dialogSizes.lg" scrollable>
							<v-card title="Detailed Reservoir Performance Output">
								<v-card-item>
									<div v-if="data.check.reservoirs.reservoirRows && data.check.reservoirs.reservoirRows.length < 1" class="mb-5">
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
												<tr v-for="(m, i) in data.check.reservoirs.reservoirRows" :key="i">
													<td>{{m.id}}</td>
													<td>{{formatters.toNumberFormat(m.sediment, 2)}}</td>
													<td>{{formatters.toNumberFormat(m.phosphorus, 2)}}</td>
													<td>{{formatters.toNumberFormat(m.nitrogen, 2)}}</td>
													<td>{{formatters.toNumberFormat(m.volumeRatio, 2)}}</td>
													<td>{{formatters.toNumberFormat(m.fractionEmpty, 2)}}</td>
													<td>{{formatters.toNumberFormat(m.seepage, 2)}}</td>
													<td>{{formatters.toNumberFormat(m.evapLoss, 2)}}</td>
												</tr>
											</tbody>
										</v-table>
									</div>
								</v-card-item>
								<v-divider></v-divider>
								<v-card-actions>
									<v-btn @click="data.modals.reservoirs.table = false">Close</v-btn>
								</v-card-actions>
							</v-card>
						</v-dialog>

						<v-row>
							<v-col md="4">
								<p class="font-weight-bold">Average Trapping Efficiency (%)</p>
								<v-table small density="compact" class="mb-4">
									<tbody>
										<tr>
											<th>Sediment</th>
											<td class="text-right">{{formatters.toNumberFormat(data.check.reservoirs.avgTrappingEfficiencies.sediment, 2)}}</td>
										</tr>
										<tr>
											<th>Nitrogen</th>
											<td class="text-right">{{formatters.toNumberFormat(data.check.reservoirs.avgTrappingEfficiencies.nitrogen, 2)}}</td>
										</tr>
										<tr>
											<th>Phosphorus</th>
											<td class="text-right">{{formatters.toNumberFormat(data.check.reservoirs.avgTrappingEfficiencies.phosphorus, 2)}}</td>
										</tr>
									</tbody>
								</v-table>

								<p class="font-weight-bold">Average Water Loss (%)</p>
								<v-table small density="compact" class="mb-4">
									<tbody>
										<tr>
											<th>Total Removed + Losses</th>
											<td class="text-right">{{formatters.toNumberFormat(data.check.reservoirs.avgWaterLosses.totalRemoved, 2)}}</td>
										</tr>
										<tr>
											<th>Evaporation</th>
											<td class="text-right">{{formatters.toNumberFormat(data.check.reservoirs.avgWaterLosses.evaporation, 2)}}</td>
										</tr>
										<tr>
											<th>Seepage</th>
											<td class="text-right">{{formatters.toNumberFormat(data.check.reservoirs.avgWaterLosses.seepage, 2)}}</td>
										</tr>
									</tbody>
								</v-table>

								<p class="font-weight-bold">Average Reservoir Trends</p>
								<v-table small density="compact" class="mb-4">
									<tbody>
										<tr>
											<th>Number of Reservoirs</th>
											<td class="text-right">{{formatters.toNumberFormat(data.check.reservoirs.avgReservoirTrends.numberReservoirs, 2)}}</td>
										</tr>
										<tr>
											<th>Final/Initial Volume (Max)</th>
											<td class="text-right">{{formatters.toNumberFormat(data.check.reservoirs.avgReservoirTrends.maxVolume, 2)}}</td>
										</tr>
										<tr>
											<th>Final/Initial Volume (Min)</th>
											<td class="text-right">{{formatters.toNumberFormat(data.check.reservoirs.avgReservoirTrends.minVolume, 2)}}</td>
										</tr>
										<tr>
											<th>Fraction of Period Empty (Max)</th>
											<td class="text-right">{{formatters.toNumberFormat(data.check.reservoirs.avgReservoirTrends.fractionEmpty, 2)}}</td>
										</tr>
									</tbody>
								</v-table>
							</v-col>
							<v-col md>
								<p>
									<img class="img-fluid" :src="`/swat-check/res.jpg`" alt="res image" />
								</p>
							</v-col>
						</v-row>
					</div>

					<action-bar>
						<v-btn variant="flat" @click="nextTab(-1)" class="border mr-2" :disabled="data.page.tabIndex == 0" title="Previous tab"><font-awesome-icon icon="chevron-left" /></v-btn>
						<v-btn variant="flat" @click="nextTab(1)" class="border mr-2" :disabled="data.page.tabIndex == data.page.tabs.length - 1" title="Next tab"><font-awesome-icon icon="chevron-right" /></v-btn>
						<v-btn type="button" variant="flat" color="secondary" @click="utilities.exit" class="ml-auto">Exit SWAT+ Editor</v-btn>
					</action-bar>
				</div>
			</div>
		</v-main>
	</project-container>
</template>

<style scoped>
	.instream td {
		width: 1%;
		white-space: nowrap;
		text-align: right;	
	}

	.instream th {
		width: 85%;
	}

	.picture-holder {
		background: no-repeat 0 0;
		font-size: 0.75em;
		line-height: 1.4em;
		margin: 0 auto;
		position: relative;
	}

	.picture-holder span {
		background: #fff;
		font-weight: bold;
		padding: 0 2px;
		position: absolute;
		text-align: center;
	}

	#hydrology {
		background-image: url(/swat-check/hydro.png);
		height: 491px;
		width: 650px;
	}

	#hydrology #et {
		top: 65px;
		left: 130px;
	}
	
	#hydrology #etPlant {
		top: 95px;
		left: 0;
		width: 50px;
	}

	#hydrology #etSoil {
		top: 145px;
		left: 0;
		width: 50px;
	}

	#hydrology #pet {
		top: 45px;
		left: 0px;
		width: 50px;
	}

	#hydrology #precip {
		top: 110px;
		left: 410px;
	}

	#hydrology #irrigation {
		top: 100px;
		left: 480px;
		width: 150px;
	}

	#hydrology #tile {
		top: 150px;
		left: 480px;
		width: 150px;
	}

	#hydrology #cn {
		top: 50px;
		left: 480px;
		width: 150px;
	}

	#hydrology #surfacerunoff {
		top: 275px;
		left: 545px;
	}

	#hydrology #lateralflow {
		top: 315px;
		left: 450px;
	}

	#hydrology #returnflow {
		top: 355px;
		left: 480px;
	}

	#hydrology #perc {
		top: 350px;
		left: 320px;
	}

	#hydrology #revap {
		top: 350px;
		left: 150px;
	}

	#hydrology #recharge {
		top: 445px;
		left: 320px;
	}

	#hydrology #hydrology-units {
		bottom: 5px;
		right: 5px;
	}

	#sediment {
		background-image: url(/swat-check/WatershedDisplay.jpg);
		height: 396px;
		width: 628px;
	}

	#sediment #maxupland {
		top: 25px;
		left: 400px;
	}

	#sediment #surfacerunoffsed {
		top: 70px;
		left: 150px;
	}

	#sediment #avgupland {
		top: 130px;
		left: 30px;
	}

	#sediment #inletsed {
		top: 220px;
		left: 125px;
	}

	#sediment #instreamsed {
		top: 220px;
		left: 370px;
	}

	#ncycle {
		background-image: url(/swat-check/NCycle.png);
		height: 362px;
		width: 800px;
	}

	#ncycle #initno3 {
		top: 5px;
		left: 5px;
	}

	#ncycle #volatilization {
		top: 115px;
		left: 70px;
	}

	#ncycle #nfix {
		top: 77px;
		left: 242px;
	}

	#ncycle #denit {
		top: 115px;
		left: 275px;
	}

	#ncycle #inorgnh4 {
		top: 160px;
		left: 85px;
	}

	#ncycle #inorgno3 {
		top: 146px;
		left: 317px;
	}

	#ncycle #nplantuptake {
		top: 200px;
		left: 240px;
	}

	#ncycle #nitrification {
		top: 240px;
		left: 115px;
	}

	#ncycle #nmineralization {
		top: 240px;
		left: 300px;
	}

	#ncycle #totaln {
		top: 320px;
		left: 30px;
	}

	#ncycle #initorgn {
		top: 5px;
		left: 405px;
	}

	#ncycle #orgn {
		top: 135px;
		left: 445px;
	}

	#ncycle #activetostable {
		top: 225px;
		left: 520px;
	}

	#ncycle #nresidue {
		top: 315px;
		left: 660px;
	}

	#ncycle #ncycle-units {
		top: 5px;
		right: 5px;
	}

	#pcycle {
		background-image: url(/swat-check/PCycle.png);
		height: 362px;
		width: 800px;
	}

	#pcycle #minp {
		top: 5px;
		left: 5px;
	}

	#pcycle #orgp {
		top: 5px;
		left: 405px;
	}

	#pcycle #totalp {
		top: 65px;
		left: 30px;
	}

	#pcycle #inorgp {
		top: 110px;
		left: 305px;
	}

	#pcycle #pplantuptake {
		top: 150px;
		left: 215px;
	}

	#pcycle #pstableactive {
		top: 220px;
		left: 90px;
	}

	#pcycle #pactivesol {
		top: 220px;
		left: 205px;
	}

	#pcycle #pmineralization {
		top: 255px;
		left: 340px;
	}

	#pcycle #orgpfert {
		top: 180px;
		left: 480px;
	}

	#pcycle #presidue {
		top: 315px;
		left: 660px;
	}

	#pcycle #pcycle-units {
		top: 5px;
		right: 5px;
	}

	#plantgrowth {
		background-image: url(/swat-check/plant.png);
		height: 458px;
		width: 450px;
	}

	#plantgrowth span {
		text-align: right;
	}

	#plantgrowth #plantavg {
		top: 5px;
		left: 5px;
	}

	#plantgrowth #npremoved {
		top: 50px;
		left: 230px;
	}

	#plantgrowth #totalnp {
		top: 220px;
		left: 270px;
	}

	#plantgrowth #plantuptakenp {
		bottom: 10px;
		left: 260px;
	}
</style>