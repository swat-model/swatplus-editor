<script setup lang="ts">
	import { reactive, ref } from 'vue'
	const electron = window.electronApi;

	let globals:any = {
		dev_mode: true,
		platform: null,
		project_path: null,
		version: null
	}

	globals = electron.getGlobals();
	electron.setWindowTitle(`SWAT Check v${globals.version}`);
	
	let page:any = reactive({
		errors: false,
		projectPath: globals.project_path,
		readFiles: true,
		tab: 'setup',
		isReady: false,
		isRunning: false,
		hasError: false,
		currentPid: null,
		emptyPathError: false,
		hideSetup: false,
		currentTabIndex: 0
	})

	let status:any = reactive({
		progress: 0,
		message: '',
		exception: null,
		data: null,
		runTime: null
	})

	let tabs = [
		'setup',
		'hydrology',
		'sediment',
		'nitrogenCycle',
		'phosphorusCycle',
		'plantGrowth',
		'landscapeNutrientLosses',
		'landUseSummary',
		'instreamProcesses',
		'pointSources',
		'reservoirs'
	];

	let hydBaseflowModal = ref(null);
	function showHydBaseflowModal():void {
		// @ts-ignore
		hydBaseflowModal.value.show();
	}

	let hydAvgMonValuesModal = ref(null);
	function showHydAvgMonValuesModal():void {
		// @ts-ignore
		hydAvgMonValuesModal.value.show();
	}

	let resModal = ref(null);
	function showResModal():void {
		// @ts-ignore
		resModal.value.show();
	}

	function getTabClass(menuItem:string):string {
		if (menuItem === page.tab) return 'nav-link active';
		return 'nav-link text-white';
	}

	function setPageTab(selected:string):void {
		page.tab = selected;
		page.currentTabIndex = tabs.indexOf(selected);
	}

	function setPageTabFromIndex(idx:number):void {
		if (idx >= tabs.length) page.currentTabIndex = 0;
		else if (idx < 0) page.currentTabIndex = tabs.length - 1;
		else page.currentTabIndex = idx;
		page.tab = tabs[page.currentTabIndex];
	}

	function selectDirectory():void {
		var files = electron.openFileDialog({properties: ['openDirectory']});
		if (files !== undefined) {
			page.projectPath = files[0];
		}
	}

	function runSwatCheck():void {
		if (page.projectPath === null || page.projectPath === '') {
			page.emptyPathError = true;
		} else {
			page.emptyPathError = false;
			page.isRunning = true;
			page.isReady = false;
			page.currentPid = electron.runApi(page.projectPath, page.readFiles);
		}
	}

	function cancelRun():void {
		if (page.currentPid !== null) electron.killProcess(page.currentPid);
		page.isRunning = false;
		page.isReady = false;
		page.hasError = false;
	}

	function quitApp():void {
		electron.quitApp();
	}

	electron.processStdout((event:any, data:any) => {
		//if (globals.dev_mode) console.log(`stdout: ${data}`);
		let obj = JSON.parse(data);
		status.message = obj.message;
		status.progress = obj.progress;
		status.exception = obj.exception;
		//status.data = obj.data;
		status.runTime = obj.runTime;

		if (obj.progress === 100) {
			status.data = JSON.parse(electron.readSwatCheck(page.projectPath));
			page.isReady = true;
			page.hideSetup = true;
			electron.setWindowTitle(`SWAT Check v${globals.version} - ${page.projectPath}`);
		}
	});

	electron.processStderr((event:any, data:any) => {
		console.log(`stderr: ${data}`);
		let obj = JSON.parse(data);
		status.message = obj.message;
		status.progress = obj.progress;
		status.exception = obj.exception;
		status.data = obj.data;
		status.runTime = obj.runTime;

		page.hasError = true;
		page.isRunning = false;
	});

	electron.processClose((event:any, data:any) => {
		page.isRunning = false;
		//if (globals.dev_mode) console.log(`data: ${data}`);
	});

	function numberFormat(value:any, decimals:number = 2, includeCommas:boolean = true):any {
		if (isNaN(Number(value))) return value;
		var x = Number(value).toFixed(decimals);
		if (includeCommas) {
			var parts = x.toString().split(".");
			parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ",");
			return parts.join(".");
		}
		return x;
	}

	function getArrayKeys(arr:object[]):string[] {
		if (arr === null || arr.length < 1) return [];
		return Object.keys(arr[0]);
	}
</script>

<template>
	<div id="app">
		<main v-if="page.isRunning">
			<div class="p-5 text-center w-75 mx-auto">
				<h1 class="h3">Running SWAT Check</h1>

				<div class="progress" role="progressbar" aria-label="SWAT Check Progress" :aria-valuenow="status.progress" aria-valuemin="0" aria-valuemax="100">
					<div class="progress-bar progress-bar-striped progress-bar-animated" :style="`width: ${status.progress}%`"></div>
				</div>

				<div class="my-3">
					{{ status.message }}
				</div>

				<div class="my-3">
					<a href="#" @click="cancelRun" class="text-danger">Cancel</a>
				</div>
			</div>
		</main>
		<main v-else-if="page.hasError">
			<div class="p-5 w-75 mx-auto">
				<h1 class="h3 text-center">Error Running SWAT Check</h1>

				<div class="alert alert-warning lead" role="alert">
					{{ status.message }}
				</div>

				<p>
					Please read through the message and stack trace carefully in case you
					can fix the error on your own. If unsure the cause of the error, 
					copy and paste the text below into the <open-in-browser url="http://groups.google.com/group/swatuser" text="SWAT User Support Group" />.
				</p>

				<div class="my-3">
					<textarea class="form-control" rows="10" readonly>SWAT Check v{{ globals.version }}
{{ status.exception }}</textarea>
				</div>

				<div class="my-3">
					<button @click="cancelRun" type="button" class="btn btn-lg btn-success">Clear Error and Return to Setup</button>
				</div>
			</div>
		</main>
		<main v-else class="d-flex flex-nowrap">
			<div class="d-flex flex-column flex-shrink-0 p-3 text-bg-dark" style="width: 280px;">
				<div class="fs-4">SWAT Check</div>
				<hr />
				<ul class="nav nav-pills flex-column mb-auto">
					<li class="nav-item"><a href="#" @click="setPageTab('setup')" :class="getTabClass('setup')">Setup</a></li>
					<li class="nav-item"><a href="#" @click="setPageTab('hydrology')" :class="getTabClass('hydrology')">Hydrology</a></li>
					<li class="nav-item"><a href="#" @click="setPageTab('sediment')" :class="getTabClass('sediment')">Sediment</a></li>
					<li class="nav-item"><a href="#" @click="setPageTab('nitrogenCycle')" :class="getTabClass('nitrogenCycle')">Nitrogen Cycle</a></li>
					<li class="nav-item"><a href="#" @click="setPageTab('phosphorusCycle')" :class="getTabClass('phosphorusCycle')">Phosphorus Cycle</a></li>
					<li class="nav-item"><a href="#" @click="setPageTab('plantGrowth')" :class="getTabClass('plantGrowth')">Plant Growth</a></li>
					<li class="nav-item"><a href="#" @click="setPageTab('landscapeNutrientLosses')" :class="getTabClass('landscapeNutrientLosses')">Landscape Nutrient Losses</a></li>
					<li class="nav-item"><a href="#" @click="setPageTab('landUseSummary')" :class="getTabClass('landUseSummary')">Land Use Summary</a></li>
					<li class="nav-item"><a href="#" @click="setPageTab('instreamProcesses')" :class="getTabClass('instreamProcesses')">Instream Processes</a></li>
					<li class="nav-item"><a href="#" @click="setPageTab('pointSources')" :class="getTabClass('pointSources')">Point Sources</a></li>
					<li class="nav-item"><a href="#" @click="setPageTab('reservoirs')" :class="getTabClass('reservoirs')">Reservoirs</a></li>
				</ul>
				<hr />
				<div>
					<a href="#" @click="setPageTab('help')" class="text-white text-decoration-none"><font-awesome-icon :icon="['fas', 'question-circle']" fixed-width /> Help</a>
				</div>
			</div>

			<div id="content-window" class="flex-grow-1 d-flex flex-column">
				<div id="inner-content-window" class="py-3 px-4 flex-column flex-grow-1 mb-auto">
					<div v-if="page.tab === 'setup'">
						<h1 class="h3 mb-3">Run SWAT Check</h1>

						<div class="bg-light p-3 mb-4" v-if="!page.hideSetup">
							<div class="mb-3">
								<label for="projectPath" class="form-label">Project location (typically Scenarios/Default/TxtInOut)</label>
								<div class="input-group">
									<input id="projectPath" type="text" class="form-control" v-model="page.projectPath" />
									<button class="btn btn-primary" type="button" @click="selectDirectory">Browse</button>
								</div>
								<div v-if="page.emptyPathError" class="text-danger">
									Please select the path to your project files.
								</div>
							</div>
							<div class="form-check mb-3">
								<input class="form-check-input" type="checkbox" id="readFiles" v-model="page.readFiles">
								<label class="form-check-label" for="readFiles">
									Read SWAT output files into SQLite?
									<br />
									<em>If you have already run SWAT Check on this project and the model hasn't changed/run again, 
									you may save time by unchecking this box.</em>
								</label>
							</div>

							<div class="mt-4 mb-3">
								<button class="btn btn-success btn-lg" type="button" @click="runSwatCheck">Examine Model Output</button>
							</div>
						</div>
						<div v-if="page.isReady" class="mt-3 mb-4">
							<button type="button" class="btn btn-light border" @click="page.hideSetup = !page.hideSetup">
								{{ page.hideSetup ? 'Select another project...' : 'Hide setup' }}
							</button>
						</div>

						<p>
							SWAT Check reads model output from a SWAT project and performs many simple checks to identify
							potential model problems. The intended purpose of this program is to identify model problems early 
							in the modeling process. Hidden model problems often result in the need to recalibrate or regenerate a model, 
							resulting in an avoidable waste of time. This program is designed to compare a variety of SWAT outputs to 
							nominal ranges based on the judgment of model developers. A warning does not necessarily indicate a problem; 
							the purpose is to bring attention to unusual predictions. This software also provides a visual representation 
							of various model outputs to aid novice users.
						</p>
						<p v-if="!page.isReady">
							<span class="text-danger">WARNING:</span> SWAT Check must have write-access to your SWAT project directory. For large, daily output models, 
							reading SWAT's output.rch file may take a while (for example, if output.rch is over 200MB).
						</p>

						<div v-if="page.isReady">
							<div class="row">
								<div class="col">
									<table class="table table-striped border-top table-min-width-th">
										<tbody>
											<tr>
												<th scope="row">SWAT Version</th>
												<td>{{status.data.setup.swatVersion}}</td>
											</tr>
											<tr>
												<th scope="row">Simulation Length</th>
												<td>{{status.data.setup.simulationLength}} years</td>
											</tr>
											<tr>
												<th scope="row">Warm-up</th>
												<td>{{status.data.setup.warmUp}} years</td>
											</tr>
											<tr>
												<th scope="row">HRUs</th>
												<td>{{numberFormat(status.data.setup.hrus, 0)}}</td>
											</tr>
											<tr>
												<th scope="row">Subbasins</th>
												<td>{{numberFormat(status.data.setup.subbasins, 0)}}</td>
											</tr>
										</tbody>
									</table>
								</div>
								<div class="col">
									<table class="table table-striped border-top table-min-width-th">
										<tbody>
											<tr>
												<th scope="row">Output Timestep</th>
												<td>{{status.data.setup.outputTimestep}}</td>
											</tr>
											<tr>
												<th scope="row">Precipitation Method</th>
												<td>{{status.data.setup.precipMethod}}</td>
											</tr>
											<tr>
												<th scope="row">Watershed Area</th>
												<td>{{numberFormat(status.data.setup.watershedArea)}} km<sup>2</sup></td>
											</tr>
										</tbody>
									</table>
								</div>
							</div>
							
						</div>
					</div>

					<div v-else-if="page.tab === 'help'">
						<h1 class="h3">Help with SWAT Check</h1>

						<p>
							This version of SWAT Check has been tested with <b>SWAT 2012 revisions up to 688</b>. 
							SWAT 2009 revisions 500 or earlier may not run properly. This version is also NOT compatible with SWAT+.
							For SWAT+, SWAT+ Check is included with <open-in-browser url="https://swat.tamu.edu/software/plus" text="SWAT+ Editor" />.
						</p>

						<ul class="list-group list-group-flush border-top border-bottom">
							<li class="list-group-item"><open-in-browser url="https://swat.tamu.edu/software/swat-check/" text="SWAT Check Website" /></li>
							<li class="list-group-item"><open-in-browser url="https://swat.tamu.edu/" text="SWAT Website" /></li>
							<li class="list-group-item"><open-in-browser url="http://groups.google.com/group/swatuser" text="SWAT User Support Group" /></li>
						</ul>

						<div class="card mt-4">
							<div class="card-header">
								<h4 class="mb-0">Troubleshooting</h4>
							</div>
							<div class="card-body">
								<p>
									Trouble running SWAT Check? Please send the information below to the user group along with your error message.
								</p>
								<div>SWAT Check Version: {{ globals.version }}</div>
								<div>Platform: {{ globals.platform }}</div>
								<div>Project CMD Input: {{ globals.project_path }}</div>
								<div>Development Mode: {{ globals.dev_mode ? 'Yes' : 'No' }}</div>
							</div>
						</div>
					</div>

					<div v-else-if="!page.isReady" class="mx-auto text-center">
						<div class="alert alert-warning w-50 mx-auto lead" role="alert">
							Please load your model from the <a href="#" @click="setPageTab('setup')">setup</a> section.
						</div>
					</div>

					<div v-else-if="page.tab === 'hydrology'">
						<div class="row">
							<div class="col-xl-7">
								<h1 class="h3 mb-3">Hydrology</h1>

								<p>
									Realistic hydrology is the foundation of any model.  Pay particular attention to evapotranspiration, baseflow and surface runoff ratios.
									Baseflow/streamflow ratios for the US are provided by the USGS, these data are accessible via the button below.
									The ranges specified here are general guidelines only, and may not apply to your simulation area.
								</p>

								<div class="alert alert-primary mb-3" v-if="status.data.hydrology.warnings.length > 0">
									<h5>Messages and Warnings</h5>
									<ul class="mb-0">
										<li v-for="(warning, i) in status.data.hydrology.warnings" :key="i">{{warning}}</li>
									</ul>
								</div>

								<p class="mb-2">
									<button type="button" class="btn btn-primary me-1" @click="showHydAvgMonValuesModal">Average monthly basin values</button>
									<button type="button" class="btn btn-primary me-1" @click="showHydBaseflowModal">US baseflow map</button>
								</p>

								<b-modal title="Average monthly basin values" size="xl" ref="hydAvgMonValuesModal">
									<template #body>
										<table class="table table-sm table-striped nowrap-headers">
											<thead>
												<tr>
													<th>Mon</th>
													<th>Rain (MM)</th>
													<th>Snow Fall (MM)</th>
													<th>SURF Q (MM)</th>
													<th>LAT Q (MM)</th>
													<th>Water Yield (MM)</th>
													<th>ET (MM)</th>
													<th>Sed. Yield (T/HA)</th>
													<th>PET (MM)</th>
												</tr>
											</thead>
											<tbody>
												<tr v-for="(m, i) in status.data.hydrology.monthlyBasinValues" :key="i">
													<td>{{m.mon}}</td>
													<td>{{numberFormat(m.rain)}}</td>
													<td>{{numberFormat(m.snowFall)}}</td>
													<td>{{numberFormat(m.surfQ)}}</td>
													<td>{{numberFormat(m.latQ)}}</td>
													<td>{{numberFormat(m.waterYield)}}</td>
													<td>{{numberFormat(m.et)}}</td>
													<td>{{numberFormat(m.sedYield)}}</td>
													<td>{{numberFormat(m.pet)}}</td>
												</tr>
											</tbody>
										</table>
									</template>
								</b-modal>

								<b-modal title="Fraction of streamflow derived from baseflow" ref="hydBaseflowModal">
									<template #body>
										<div>
											<img class="img-fluid" src="/swat-check/Baseflow_Map.png" alt="Baseflow_Map.png" />
										</div>
									</template>
								</b-modal>
							</div>
							<div class="col-xl">
								<h5>Water Balance Ratios</h5>
								<table class="table table-striped table-sm border-top my-3">
									<tbody>
										<tr>
											<th>Streamflow/Precipitation</th>
											<td>{{numberFormat(status.data.hydrology.streamflowPrecipitation, 2)}}</td>
										</tr>
										<tr>
											<th>Baseflow/Total Flow</th>
											<td>{{numberFormat(status.data.hydrology.baseflowTotalFlow, 2)}}</td>
										</tr>
										<tr>
											<th>Surface Runoff/Total Flow</th>
											<td>{{numberFormat(status.data.hydrology.surfaceRunoffTotalFlow, 2)}}</td>
										</tr>
										<tr>
											<th>Percolation/Precipitation</th>
											<td>{{numberFormat(status.data.hydrology.percolationPrecipitation, 2)}}</td>
										</tr>
										<tr>
											<th>Deep Recharge/Precipitation</th>
											<td>{{numberFormat(status.data.hydrology.deepRechargePrecipitation, 2)}}</td>
										</tr>
										<tr>
											<th>ET/Precipitation</th>
											<td>{{numberFormat(status.data.hydrology.etPrecipitation, 2)}}</td>
										</tr>
									</tbody>
								</table>

								
							</div>
						</div>

						<div id="hydrology" class="picture-holder">
									<span id="pet">PET<br />{{numberFormat(status.data.hydrology.pet, 2)}}</span>
									<span id="et">{{numberFormat(status.data.hydrology.et, 2)}}</span>
									<span id="precip">{{numberFormat(status.data.hydrology.precipitation, 2)}}</span>
									<span id="cn">Average Curve Number<br />{{numberFormat(status.data.hydrology.averageCN, 2)}}</span>
									<span id="surfacerunoff">{{numberFormat(status.data.hydrology.surfaceRunoff, 2)}}</span>
									<span id="lateralflow">{{numberFormat(status.data.hydrology.lateralFlow, 2)}}</span>
									<span id="returnflow">{{numberFormat(status.data.hydrology.returnFlow, 2)}}</span>
									<span id="perc">{{numberFormat(status.data.hydrology.percolation, 2)}}</span>
									<span id="revap">{{numberFormat(status.data.hydrology.revap, 2)}}</span>
									<span id="recharge">{{numberFormat(status.data.hydrology.recharge, 2)}}</span>
									<span id="hydrology-units">All Units mm</span>
								</div>
					</div>

					<div v-else-if="page.tab === 'sediment'">
						<h1 class="h3 mb-3">Sediment</h1>

						<p>
							Sediment loss form the landscape is dependent upon many factors.  Sediment overestimation in SWAT is most commonly due to inadequate biomass production.  This often occurs on specific land uses.  If your maximum upland sediment yield is excessive, use the landuse summary tab to identify the problem land use.
						</p>

						<p>
							SWAT also modifies sediments to account for in-stream deposition and erosion of stream banks and channels.  Often there is little or no measured data to differentiate between upland sediment and in-stream sediment changes. Streams may be either a net source of sediment, or a sink.  In-stream sediment modification is impacted by physical channel characteristic’s (slope, width, depth, channel cover, and substrate characteristics) and the quantity of sediment and flow from upstream.
						</p>

						<div class="alert alert-primary mb-3" v-if="status.data.sediment.warnings.length > 0">
							<h5>Messages and Warnings</h5>
							<ul class="mb-0">
								<li v-for="(warning, i) in status.data.sediment.warnings" :key="i">{{warning}}</li>
							</ul>
						</div>

						<div id="sediment" class="picture-holder">
							<span id="maxupland">Maximum Upland Sediment Yield<br /> {{numberFormat(status.data.sediment.maxUplandSedimentYield, 2)}} Mg/ha</span>
							<span id="surfacerunoffsed">Surface Runoff<br /> {{numberFormat(status.data.sediment.surfaceRunoff, 2)}} mm/yr</span>
							<span id="avgupland">Average Upland Sediment Yield<br /> {{numberFormat(status.data.sediment.avgUplandSedimentYield, 2)}} Mg/ha</span>
							<span id="inletsed">Inlet/Point Sources Sediment<br /> {{numberFormat(status.data.sediment.inletSediment, 2)}} Mg/year</span>
							<span id="instreamsed">Instream Sediment Change<br /> {{numberFormat(status.data.sediment.inStreamSedimentChange, 2)}} Mg/ha</span>
						</div>
					</div>

					<div v-else-if="page.tab === 'nitrogenCycle'">
						<h1 class="h3 mb-3">Nitrogen Cycle</h1>

						<p>
							The nitrogen cycle is key to biomass production, which in turn impacts ET and sediment yield.
							The nitrogen cycle is complex, it is generally not possible to validate these routines outside a research setting.
							Of particular importance are the total applied nitrogen fertilizer and losses due to plant uptake, and volatilization and denitrification.
							Soils contain a large amount of organic nitrogen in the form of organic matter.  Large changes in initial and final nitrogen contents
							(in particular organic n) may indicate under or over fertilization during the simulation.
						</p>

						<div class="alert alert-primary mb-3" v-if="status.data.nitrogenCycle.warnings.length > 0">
							<h5>Messages and Warnings</h5>
							<ul class="mb-0">
								<li v-for="(warning, i) in status.data.nitrogenCycle.warnings" :key="i">{{warning}}</li>
							</ul>
						</div>

						<div id="ncycle" class="picture-holder">
							<span id="initno3">
								Initial NO<sub>3</sub>: {{numberFormat(status.data.nitrogenCycle.initialNO3, 2)}}<br />
								Final NO<sub>3</sub>: {{numberFormat(status.data.nitrogenCycle.finalNO3, 2)}}
							</span>
							<span id="volatilization">{{numberFormat(status.data.nitrogenCycle.volatilization, 2)}}</span>
							<span id="nfix">{{numberFormat(status.data.nitrogenCycle.nFixation, 2)}}</span>
							<span id="denit">{{numberFormat(status.data.nitrogenCycle.denitrification, 2)}}</span>
							<span id="inorgnh4">{{numberFormat(status.data.nitrogenCycle.nH4InOrgNFertilizer, 2)}}</span>
							<span id="inorgno3">{{numberFormat(status.data.nitrogenCycle.nO3InOrgNFertilizer, 2)}}</span>
							<span id="nplantuptake">{{numberFormat(status.data.nitrogenCycle.plantUptake, 2)}}</span>
							<span id="nitrification">{{numberFormat(status.data.nitrogenCycle.nitrification, 2)}}</span>
							<span id="nmineralization">{{numberFormat(status.data.nitrogenCycle.mineralization, 2)}}</span>
							<span id="initorgn">
								Initial Org N: {{numberFormat(status.data.nitrogenCycle.initialOrgN, 2)}}<br />
								Final Org N: {{numberFormat(status.data.nitrogenCycle.finalOrgN, 2)}}
							</span>
							<span id="orgn">{{numberFormat(status.data.nitrogenCycle.orgNFertilizer, 2)}}</span>
							<span id="activetostable">{{numberFormat(status.data.nitrogenCycle.activeToStableOrgN, 2)}}</span>
							<span id="nresidue">{{numberFormat(status.data.nitrogenCycle.residueMineralization, 2)}}</span>
							<span id="totaln">Total Fertilizer N: {{numberFormat(status.data.nitrogenCycle.totalFertilizerN, 2)}}</span>

							<span id="ncycle-units">All units kg/ha</span>
						</div>

						<h2 class="h4 my-3">Average Annual Values by Land Use</h2>

						<p>
							The following table is read from your output.hru file, which might not print all HRUs and 
							variables by default. Adjust lines 69 and 70 of your file.cio to either have all 0s, which will
							print all HRUs and variables, or select specific HRUs and columns (up to 20). Save and re-run your
							model and SWAT Check, keeping in mind that HRU output can potentially be very large (several GB) and time-consuming.
							See the <open-in-browser url="https://swat.tamu.edu/docs/" text="SWAT IO documentation" /> for help.
						</p>

						<div class="table-responsive" v-if="status.data.nitrogenCycle.avgAnnualByLandUse !== null && status.data.nitrogenCycle.avgAnnualByLandUse.length > 0">
							<table class="table table-sm table-striped table-min-width-th border-top">
								<thead>
									<tr>
										<th v-for="(h, hi) in getArrayKeys(status.data.nitrogenCycle.avgAnnualByLandUse)" :key="hi">
											<abbr :title="status.data.nitrogenCycle.avgAnnualDefinitions[h]">{{ h.toUpperCase() }}</abbr>
										</th>
									</tr>
								</thead>
								<tbody>
									<tr v-for="(row, r) in status.data.nitrogenCycle.avgAnnualByLandUse" :key="r">
										<td v-for="(k, ki) in getArrayKeys(status.data.nitrogenCycle.avgAnnualByLandUse)" :key="ki">
											<span v-if="k === 'lulc'">{{ row[k] }}</span>
											<span v-else-if="row[k] === null">N/A</span>
											<span v-else>{{ numberFormat(row[k]) }}</span>
										</td>
									</tr>
								</tbody>
							</table>
						</div>
						<div v-else class="alert alert-info">
							Data not available. Check your output.hru settings described above.
						</div>
					</div>

					<div v-else-if="page.tab === 'phosphorusCycle'">
						<h1 class="h3 mb-3">Phosphorus Cycle</h1>

						<p>
							The phosphorus cycle is of particular interest in watersheds with significant animal manure application.
							Soils contain a large reservoir of both mineral and organic phosphorus.  Large increases in mineral phosphorus
							content during the simulation often result from overfertilization with either commercial or manure phosphorus sources.
							This also means that phosphorus concentrations in runoff also increase during the simulation period.
							Plant uptake is the dominant loss pathway for soil phosphorus under most conditions.
						</p>

						<div class="alert alert-primary mb-3" v-if="status.data.phosphorusCycle.warnings.length > 0">
							<h5>Messages and Warnings</h5>
							<ul class="mb-0">
								<li v-for="(warning, i) in status.data.phosphorusCycle.warnings" :key="i">{{warning}}</li>
							</ul>
						</div>

						<div id="pcycle" class="picture-holder">
							<span id="minp">
								Initial Min P: {{numberFormat(status.data.phosphorusCycle.initialMinP, 2)}}<br />
								Final Min P: {{numberFormat(status.data.phosphorusCycle.finalMinP, 2)}}
							</span>
							<span id="orgp">
								Initial Org P: {{numberFormat(status.data.phosphorusCycle.initialOrgP, 2)}}<br />
								Final Org P: {{numberFormat(status.data.phosphorusCycle.finalOrgP, 2)}}
							</span>
							<span id="totalp">Total Fertilizer P: {{numberFormat(status.data.phosphorusCycle.totalFertilizerP, 2)}}</span>
							<span id="inorgp">{{numberFormat(status.data.phosphorusCycle.inOrgPFertilizer, 2)}}</span>
							<span id="pplantuptake">{{numberFormat(status.data.phosphorusCycle.plantUptake, 2)}}</span>
							<span id="pstableactive">{{numberFormat(status.data.phosphorusCycle.stableActive, 2)}}</span>
							<span id="pactivesol">{{numberFormat(status.data.phosphorusCycle.activeSolution, 2)}}</span>
							<span id="pmineralization">{{numberFormat(status.data.phosphorusCycle.mineralization, 2)}}</span>
							<span id="orgpfert">{{numberFormat(status.data.phosphorusCycle.orgPFertilizer, 2)}}</span>
							<span id="presidue">{{numberFormat(status.data.phosphorusCycle.residueMineralization, 2)}}</span>

							<span id="pcycle-units">All units kg/ha</span>
						</div>

						<h2 class="h4 my-3">Average Annual Values by Land Use</h2>

						<p>
							The following table is read from your output.hru file, which might not print all HRUs and 
							variables by default. Adjust lines 69 and 70 of your file.cio to either have all 0s, which will
							print all HRUs and variables, or select specific HRUs and columns (up to 20). Save and re-run your
							model and SWAT Check, keeping in mind that HRU output can potentially be very large (several GB) and time-consuming.
							See the <open-in-browser url="https://swat.tamu.edu/docs/" text="SWAT IO documentation" /> for help.
						</p>

						<div class="table-responsive" v-if="status.data.phosphorusCycle.avgAnnualByLandUse !== null && status.data.phosphorusCycle.avgAnnualByLandUse.length > 0">
							<table class="table table-sm table-striped table-min-width-th border-top">
								<thead>
									<tr>
										<th v-for="(h, hi) in getArrayKeys(status.data.phosphorusCycle.avgAnnualByLandUse)" :key="hi">
											<abbr :title="status.data.phosphorusCycle.avgAnnualDefinitions[h]">{{ h.toUpperCase() }}</abbr>
										</th>
									</tr>
								</thead>
								<tbody>
									<tr v-for="(row, r) in status.data.phosphorusCycle.avgAnnualByLandUse" :key="r">
										<td v-for="(k, ki) in getArrayKeys(status.data.phosphorusCycle.avgAnnualByLandUse)" :key="ki">
											<span v-if="k === 'lulc'">{{ row[k] }}</span>
											<span v-else-if="row[k] === null">N/A</span>
											<span v-else>{{ numberFormat(row[k]) }}</span>
										</td>
									</tr>
								</tbody>
							</table>
						</div>
						<div v-else class="alert alert-info">
							Data not available. Check your output.hru settings described above.
						</div>
					</div>

					<div v-else-if="page.tab === 'plantGrowth'">
						<h1 class="h3 mb-3">Plant Growth</h1>

						<p>
							Proper plant growth is key to accurate runoff and sediment predictions.  Problems in plant growth are often related to excessive
							stress due to temperature or the lack of water/nutrients.  The data presented here are basin averages, and may not reflect problems
							with individual land uses.  Carefully review the land use summary tab.
						</p>

						<div class="row">
							<div class="col-lg">
								<div class="alert alert-primary mb-3" v-if="status.data.plantGrowth.warnings.length > 0">
									<h5>Messages and Warnings</h5>
									<ul class="mb-0">
										<li v-for="(warning, i) in status.data.plantGrowth.warnings" :key="i">{{warning}}</li>
									</ul>
								</div>

								<table class="table table-sm table-striped border-top">
									<tbody>
										<tr>
											<th>Temperature Stress Days</th>
											<td>{{numberFormat(status.data.plantGrowth.tempStressDays, 2)}}</td>
										</tr>
										<tr>
											<th>Water Stress Days</th>
											<td>{{numberFormat(status.data.plantGrowth.waterStressDays, 2)}}</td>
										</tr>
										<tr>
											<th>Nitrogen Stress Days</th>
											<td>{{numberFormat(status.data.plantGrowth.nStressDays, 2)}}</td>
										</tr>
										<tr>
											<th>Phosphorus Stress Days</th>
											<td>{{numberFormat(status.data.plantGrowth.pStressDays, 2)}}</td>
										</tr>
									</tbody>
								</table>
							</div>
							<div class="col-lg">
								<div id="plantgrowth" class="picture-holder">
									<span id="plantavg">
										Average Biomass: {{numberFormat(status.data.plantGrowth.avgBiomass, 2)}} kg/ha<br />
										Average Yield: {{numberFormat(status.data.plantGrowth.avgYield, 2)}} kg/ha
									</span>
									<span id="npremoved">
										N Removed in Yield: {{numberFormat(status.data.plantGrowth.nRemoved, 2)}} kg/ha<br />
										P Removed in Yield: {{numberFormat(status.data.plantGrowth.pRemoved, 2)}} kg/ha
									</span>
									<span id="totalnp">
										Total Fertilizer N: {{numberFormat(status.data.plantGrowth.totalFertilizerN, 2)}} kg/ha<br />
										Total Fertilizer P: {{numberFormat(status.data.plantGrowth.totalFertilizerP, 2)}} kg/ha
									</span>
									<span id="plantuptakenp">
										Plant Uptake N: {{numberFormat(status.data.plantGrowth.plantUptakeN, 2)}} kg/ha<br />
										Plant Uptake P: {{numberFormat(status.data.plantGrowth.plantUptakeP, 2)}} kg/ha
									</span>
								</div>
							</div>
						</div>
					</div>

					<div v-else-if="page.tab === 'landscapeNutrientLosses'">
						<h1 class="h3 mb-3">Landscape Nutrient Losses</h1>

						<p>
							Nutrient losses are a critical aspect of many studies.  The data presented here are losses from the landscape surface, which is delivered to reaches.
							These are basin averages. The link below contains a summary of edge of field nutrient losses from monitoring studies by individual crops.
							These data can be compared to SWAT+ predictions to verify the appropriate magnitude of predicted losses.
						</p>

						<div class="alert alert-primary mb-3" v-if="status.data.landscapeNutrientLosses.warnings.length > 0">
							<h5>Messages and Warnings</h5>
							<ul class="mb-0">
								<li v-for="(warning, i) in status.data.landscapeNutrientLosses.warnings" :key="i">{{warning}}</li>
							</ul>
						</div>

						<div class="row">
							<div class="col-lg">
								<h5>Nitrogen Losses (kg/ha)</h5>
								<table class="table table-sm table-striped border-top">
									<tbody>
										<tr>
											<th>Total N Loss</th>
											<td>{{numberFormat(status.data.landscapeNutrientLosses.nLosses.totalLoss, 2)}}</td>
										</tr>
										<tr>
											<th>Organic N</th>
											<td>{{numberFormat(status.data.landscapeNutrientLosses.nLosses.orgN, 2)}}</td>
										</tr>
										<tr>
											<th>Nitrate Surface Runoff</th>
											<td>{{numberFormat(status.data.landscapeNutrientLosses.nLosses.surfaceRunoff, 2)}}</td>
										</tr>
										<tr>
											<th>Nitrate Leached</th>
											<td>{{numberFormat(status.data.landscapeNutrientLosses.nLosses.leached, 2)}}</td>
										</tr>
										<tr>
											<th>Nitrate Lateral Flow</th>
											<td>{{numberFormat(status.data.landscapeNutrientLosses.nLosses.lateralFlow, 2)}}</td>
										</tr>
										<tr>
											<th>Nitrate Groundwater Yield</th>
											<td>{{numberFormat(status.data.landscapeNutrientLosses.nLosses.groundwaterYield, 2)}}</td>
										</tr>
										<tr>
											<th>Solubility Ratio in Runoff</th>
											<td>{{numberFormat(status.data.landscapeNutrientLosses.nLosses.solubilityRatio, 2)}}</td>
										</tr>
									</tbody>
								</table>
							</div>
							<div class="col-lg">
								<h5>Phosphorus Losses (kg/ha)</h5>
								<table class="table table-sm table-striped border-top">
									<tbody>
										<tr>
											<th>Total P Loss</th>
											<td>{{numberFormat(status.data.landscapeNutrientLosses.pLosses.totalLoss, 2)}}</td>
										</tr>
										<tr>
											<th>Organic P</th>
											<td>{{numberFormat(status.data.landscapeNutrientLosses.pLosses.orgP, 2)}}</td>
										</tr>
										<tr>
											<th>Soluble P Surface Runoff</th>
											<td>{{numberFormat(status.data.landscapeNutrientLosses.pLosses.surfaceRunoff, 2)}}</td>
										</tr>
										<tr>
											<th>Solubility Ratio in Runoff</th>
											<td>{{numberFormat(status.data.landscapeNutrientLosses.pLosses.solubilityRatio, 2)}}</td>
										</tr>
									</tbody>
								</table>
							</div>
						</div>

						<h5 class="mt-4">Measured Nutrient Losses by Crop and Tillage</h5>
						<p>
							From Harmel, D., et al.  2006 Compilation of Measured Nutrient Load Data for Agricultural Land Uses in the United States. <em>Journal of the American Water Resources Association</em> 42(5):1163-1178.
						</p>
						<p>
							<img class="img-fluid" src="/swat-check/nut_croptype2.png" alt="nut_croptype2.png" />
						</p>
						<p>
							<img class="img-fluid" src="/swat-check/nut_croptype3.png" alt="nut_croptype3.png" />
						</p>
					</div>

					<div v-else-if="page.tab === 'landUseSummary'">
						<h1 class="h3 mb-3">Land Use Summary</h1>

						<p>
							Model errors are often isolated to a particular land use type.  If the land use is relatively minor, these issues
							may go unnoticed at the basin outlet during calibration.  Often, these minor land uses are the focus of scenario
							development, and errors become apparent after the investment of much calibration effort.
						</p>
						
						<div class="alert alert-primary mb-3" v-if="status.data.landUseSummary.warnings.length > 0">
							<h5>Messages and Warnings</h5>
							<ul class="mb-0">
								<li v-for="(warning, i) in status.data.landUseSummary.warnings" :key="i">{{warning}}</li>
							</ul>
						</div>

						<h5>Summary by Reported Land Use</h5>
						<p>
							This table contains a few important predictions summarized by land use.  These should be reviewed carefully.
						</p>

						<div class="table-responsive">
							<table class="table table-sm table-striped table-min-width-th border-top">
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
										<th>GWQ mm</th>
										<th>ET mm</th>
										<th>SED th</th>
										<th>NO3 kgh</th>
										<th>ORGN kgh</th>
										<th>BIOM th</th>
										<th>YLD th</th>
									</tr>
								</thead>
								<tbody>
									<tr v-for="(m, i) in status.data.landUseSummary.landUseRows" :key="i">
										<td>{{m.landUse}}</td>
										<td>{{numberFormat(m.area, 2)}}</td>
										<td>{{numberFormat(m.cn, 2)}}</td>
										<td>{{numberFormat(m.awc, 2)}}</td>
										<td>{{numberFormat(m.uslE_LS, 2)}}</td>
										<td>{{numberFormat(m.irr, 2)}}</td>
										<td>{{numberFormat(m.prec, 2)}}</td>
										<td>{{numberFormat(m.surq, 2)}}</td>
										<td>{{numberFormat(m.gwq, 2)}}</td>
										<td>{{numberFormat(m.et, 2)}}</td>
										<td>{{numberFormat(m.sed, 2)}}</td>
										<td>{{numberFormat(m.nO3, 2)}}</td>
										<td>{{numberFormat(m.orgn, 2)}}</td>
										<td>{{numberFormat(m.biom, 2)}}</td>
										<td>{{numberFormat(m.yld, 2)}}</td>
									</tr>
								</tbody>
							</table>
						</div>

						<div v-if="status.data.landUseSummary.hruLevelWarnings.length > 0">
							<h5>HRU Level Warnings</h5>
							<p>
								These are provided only to help isolate problem HRUs within a particular land use.
								We do not recommend that these be used during routine checking of model output.
							</p>
							<ul>
								<li v-for="(warning, i) in status.data.landUseSummary.hruLevelWarnings" :key="i">{{warning}}</li>
							</ul>
						</div>
					</div>

					<div v-else-if="page.tab === 'instreamProcesses'">
						<h1 class="h3 mb-3">Instream Processes</h1>

						<p>
							In-stream processes may have a large impact on sediment and nutrient loads.  It is difficult to gage appropriate values for these outputs.
							In-stream sediment change can be either positive or negative.  Typically streams are a net sink for nutrients.
							Channel geomorphology can provide some guidance as to the net contribution of in-stream processes.
						</p>

						<div class="alert alert-primary mb-3" v-if="status.data.instreamProcesses.warnings.length > 0">
							<h5>Messages and Warnings</h5>
							<ul class="mb-0">
								<li v-for="(warning, i) in status.data.instreamProcesses.warnings" :key="i">{{warning}}</li>
							</ul>
						</div>

						<div class="row">
							<div class="col-lg">
								<h5>Reach Report: Delivery ratio of segment (%)</h5>

								<table class="table table-sm table-striped border-top">
									<thead>
										<tr>
											<th>RCH#</th>
											<th>Sediment</th>
											<th>Phosphorus</th>
											<th>Nitrogen</th>
										</tr>
									</thead>
									<tbody>
										<tr v-for="(rch, i) in status.data.instreamProcesses.reaches" :key="i">
											<td>{{ rch.id }}</td>
											<td>{{ numberFormat(rch.sediment, 2) }}</td>
											<td>{{ numberFormat(rch.phosphorus, 2) }}</td>
											<td>{{ numberFormat(rch.nitrogen, 2) }}</td>
										</tr>
									</tbody>
								</table>
							</div>
							<div class="col-lg">
								<h5>Sediment Budget</h5>
								<table class="table table-definitions instream table-sm border-top mb-4">
									<tbody>
										<tr>
											<th>Upland Sediment Yield</th>
											<td>{{numberFormat(status.data.instreamProcesses.uplandSedimentYield, 2)}}</td>
											<td>Mg/ha</td>
										</tr>
										<tr>
											<th>Instream Sediment Change</th>
											<td>{{numberFormat(status.data.instreamProcesses.instreamSedimentChange, 2)}}</td>
											<td>Mg/ha</td>
										</tr>
										<tr>
											<th>Channel Erosion</th>
											<td>{{numberFormat(status.data.instreamProcesses.channelErosion, 2)}}</td>
											<td>%</td>
										</tr>
										<tr>
											<th>Channel Deposition</th>
											<td>{{numberFormat(status.data.instreamProcesses.channelDeposition, 2)}}</td>
											<td>%</td>
										</tr>
									</tbody>
								</table>

								<h5>Instream Nutrient Modification</h5>
								<table class="table table-definitions instream table-sm border-top mb-4">
									<tbody>
										<tr>
											<th>Total Nitrogen</th>
											<td>{{numberFormat(status.data.instreamProcesses.totalN, 2)}}</td>
											<td>%</td>
										</tr>
										<tr>
											<th>Total Phosphorus</th>
											<td>{{numberFormat(status.data.instreamProcesses.totalP, 2)}}</td>
											<td>%</td>
										</tr>
									</tbody>
								</table>

								<h5>Instream Water Budget</h5>
								<table class="table table-definitions instream table-sm border-top">
									<tbody>
										<tr>
											<th>Total Streamflow Losses</th>
											<td>{{numberFormat(status.data.instreamProcesses.totalStreamflowLosses, 2)}}</td>
											<td>%</td>
										</tr>
										<tr>
											<th>Evaporation Loss</th>
											<td>{{numberFormat(status.data.instreamProcesses.evaporationLoss, 2)}}</td>
											<td>%</td>
										</tr>
										<tr>
											<th>Seepage Loss</th>
											<td>{{numberFormat(status.data.instreamProcesses.seepageLoss, 2)}}</td>
											<td>%</td>
										</tr>
									</tbody>
								</table>
							</div>
						</div>
					</div>

					<div v-else-if="page.tab === 'pointSources'">
						<h1 class="h3 mb-3">Point Sources</h1>

						<p>
							Point sources constantly discharge pollutants to streams.  These are an optional feature in SWAT+.
							These summaries are presented so that the relative contribution of these sources can be verified.
							Point sources contributions are so varied that there is no reasonable range which can be applied to all basins.
						</p>

						<div class="alert alert-primary mb-3" v-if="status.data.pointSources.warnings.length > 0">
							<h5>Messages and Warnings</h5>
							<ul class="mb-0">
								<li v-for="(warning, i) in status.data.pointSources.warnings" :key="i">{{warning}}</li>
							</ul>
						</div>

						<div class="row">
							<div class="col-xl">
								<h5>Total Subbasin Load</h5>
								<table class="table table-striped table-definitions table-sm border-top">
									<tbody>
										<tr>
											<th>Flow</th>
											<td>{{numberFormat(status.data.pointSources.subbasinLoad.flow, 2)}}</td>
											<td>cms</td>
										</tr>
										<tr>
											<th>Sediment</th>
											<td>{{numberFormat(status.data.pointSources.subbasinLoad.sediment, 2)}}</td>
											<td>Mg/yr</td>
										</tr>
										<tr>
											<th>Nitrogen</th>
											<td>{{numberFormat(status.data.pointSources.subbasinLoad.nitrogen, 2)}}</td>
											<td>kg/yr</td>
										</tr>
										<tr>
											<th>Phosphorus</th>
											<td>{{numberFormat(status.data.pointSources.subbasinLoad.phosphorus, 2)}}</td>
											<td>kg/yr</td>
										</tr>
									</tbody>
								</table>
							</div>
							<div class="col-xl">
								<h5>Total Point Source + Inlet Load</h5>
								<table class="table table-striped table-definitions table-sm border-top">
									<tbody>
										<tr>
											<th>Flow</th>
											<td>{{numberFormat(status.data.pointSources.pointSourceInletLoad.flow, 2)}}</td>
											<td>cms</td>
										</tr>
										<tr>
											<th>Sediment</th>
											<td>{{numberFormat(status.data.pointSources.pointSourceInletLoad.sediment, 2)}}</td>
											<td>Mg/yr</td>
										</tr>
										<tr>
											<th>Nitrogen</th>
											<td>{{numberFormat(status.data.pointSources.pointSourceInletLoad.nitrogen, 2)}}</td>
											<td>kg/yr</td>
										</tr>
										<tr>
											<th>Phosphorus</th>
											<td>{{numberFormat(status.data.pointSources.pointSourceInletLoad.phosphorus, 2)}}</td>
											<td>kg/yr</td>
										</tr>
									</tbody>
								</table>
							</div>
							<div class="col-xl">
								<h5>Load from Inlet + PS (%)</h5>
								<table class="table table-striped table-definitions table-sm border-top">
									<tbody>
										<tr>
											<th>Flow</th>
											<td>{{numberFormat(status.data.pointSources.fromInletAndPointSource.flow, 2)}}</td>
											<td>%</td>
										</tr>
										<tr>
											<th>Sediment</th>
											<td>{{numberFormat(status.data.pointSources.fromInletAndPointSource.sediment, 2)}}</td>
											<td>%</td>
										</tr>
										<tr>
											<th>Nitrogen</th>
											<td>{{numberFormat(status.data.pointSources.fromInletAndPointSource.nitrogen, 2)}}</td>
											<td>%</td>
										</tr>
										<tr>
											<th>Phosphorus</th>
											<td>{{numberFormat(status.data.pointSources.fromInletAndPointSource.phosphorus, 2)}}</td>
											<td>%</td>
										</tr>
									</tbody>
								</table>
							</div>
						</div>
					</div>

					<div v-else-if="page.tab === 'reservoirs'">
						<h1 class="h3 mb-3">Reservoirs</h1>

						<p>
							Reservoirs are an optional feature in SWAT+.   The hydrology of basins with large reservoirs may be completely dominated by reservoir processes and release rates.
							The data presented below is an average of all reservoirs; <a href="#" @click.prevent="showResModal">see data for individual reservoirs</a>.
							The statistics presented here are designed to identify common reservoir issues.   The use of user specified release rate may cause a reservoir to
							grow continuously or run completely dry.  These common issues can be detected via the final/initial volume ratio and fraction of period empty statistics below.
						</p>

						<div class="alert alert-primary mb-3" v-if="status.data.reservoirs.warnings.length > 0">
							<h5>Messages and Warnings</h5>
							<ul class="mb-0">
								<li v-for="(warning, i) in status.data.reservoirs.warnings" :key="i">{{warning}}</li>
							</ul>
						</div>

						<b-modal title="Detailed Reservoir Performance Output" ref="resModal">
							<template #body>
								<div class="table-responsive">
									<table class="table table-striped">
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
											<tr v-for="(m, i) in status.data.reservoirs.reservoirRows" :key="i">
												<td>{{m.id}}</td>
												<td>{{numberFormat(m.sediment, 2)}}</td>
												<td>{{numberFormat(m.phosphorus, 2)}}</td>
												<td>{{numberFormat(m.nitrogen, 2)}}</td>
												<td>{{numberFormat(m.volumeRatio, 2)}}</td>
												<td>{{numberFormat(m.fractionEmpty, 2)}}</td>
												<td>{{numberFormat(m.seepage, 2)}}</td>
												<td>{{numberFormat(m.evapLoss, 2)}}</td>
											</tr>
										</tbody>
									</table>
								</div>
							</template>
						</b-modal>

						<div class="row">
							<div class="col-lg-4">
								<h5>Average Trapping Efficiency (%)</h5>
								<table class="table table-striped table-definitions table-sm border-top mb-4">
									<tbody>
										<tr>
											<th>Sediment</th>
											<td class="text-end">{{numberFormat(status.data.reservoirs.avgTrappingEfficiencies.sediment, 2)}}</td>
										</tr>
										<tr>
											<th>Nitrogen</th>
											<td class="text-end">{{numberFormat(status.data.reservoirs.avgTrappingEfficiencies.nitrogen, 2)}}</td>
										</tr>
										<tr>
											<th>Phosphorus</th>
											<td class="text-end">{{numberFormat(status.data.reservoirs.avgTrappingEfficiencies.phosphorus, 2)}}</td>
										</tr>
									</tbody>
								</table>

								<h5>Average Water Loss (%)</h5>
								<table class="table table-striped table-definitions table-sm border-top mb-4">
									<tbody>
										<tr>
											<th>Total Removed + Losses</th>
											<td class="text-end">{{numberFormat(status.data.reservoirs.avgWaterLosses.totalRemoved, 2)}}</td>
										</tr>
										<tr>
											<th>Evaporation</th>
											<td class="text-end">{{numberFormat(status.data.reservoirs.avgWaterLosses.evaporation, 2)}}</td>
										</tr>
										<tr>
											<th>Seepage</th>
											<td class="text-end">{{numberFormat(status.data.reservoirs.avgWaterLosses.seepage, 2)}}</td>
										</tr>
									</tbody>
								</table>

								<h5>Average Reservoir Trends</h5>
								<table class="table table-striped table-definitions table-sm border-top">
									<tbody>
										<tr>
											<th>Number of Reservoirs</th>
											<td class="text-end">{{numberFormat(status.data.reservoirs.avgReservoirTrends.numberReservoirs, 2)}}</td>
										</tr>
										<tr>
											<th>Final/Initial Volume (Max)</th>
											<td class="text-end">{{numberFormat(status.data.reservoirs.avgReservoirTrends.maxVolume, 2)}}</td>
										</tr>
										<tr>
											<th>Final/Initial Volume (Min)</th>
											<td class="text-end">{{numberFormat(status.data.reservoirs.avgReservoirTrends.minVolume, 2)}}</td>
										</tr>
										<tr>
											<th>Fraction of Period Empty (Max)</th>
											<td class="text-end">{{numberFormat(status.data.reservoirs.avgReservoirTrends.fractionEmpty, 2)}}</td>
										</tr>
									</tbody>
								</table>
							</div>
							<div class="col-lg">
								<p>
									<img class="img-fluid" src="/swat-check/res.jpg" alt="res image" />
								</p>
							</div>
						</div>
					</div>
				</div>
				<div class="bg-light border-top p-3 d-flex">
					<div class="flex-fill">
						<button v-if="page.isReady && page.tab !== 'help'" type="button" class="btn bg-white border me-1" @click="setPageTabFromIndex(page.currentTabIndex-1)" title="Previous Section">
							<font-awesome-icon icon="chevron-left" />
						</button>
						<button v-if="page.isReady && page.tab !== 'help'" type="button" class="btn bg-white border me-1" @click="setPageTabFromIndex(page.currentTabIndex+1)" title="Next Section">
							<font-awesome-icon icon="chevron-right" />
						</button>
					</div>
					<button type="button" class="btn btn-secondary ml-auto" @click="quitApp">Exit SWAT Check</button>
				</div>
			</div>
		</main>
	</div>
</template>

<style lang="scss">
	@import 'app.scss';
</style>
