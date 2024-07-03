<script setup lang="ts">
	import { reactive, computed, onMounted, onUnmounted, watch } from 'vue';
	import { useRoute } from 'vue-router';
	import { useHelpers } from '@/helpers';
	import SwatPlusToolboxButton from '../components/SwatPlusToolboxButton.vue';
	import moment from 'moment';

	const route = useRoute();
	const { api, constants, errors, formatters, currentProject, runProcess, utilities } = useHelpers();
	
	let data:any = reactive({
		page: {
			loading: false,
			error: null,
			validated: false,
			submitted: false,
			saving: false,
			saveError: null,
			run: {
				show: false
			},
			completed: {
				show: false
			},
			saveScenario: {
				show: false,
				name: null,
				error: null
			},
			savedScenario: {
				show: false
			},
			inputs: {
				show: false,
				maxCols: 20
			}
		},
		hasImportedWeather: false,
		hasObservedWeather: false,
		config: {
			swat_last_run: null,
			input_files_dir: null,
			input_files_last_written: null
		},
		timeDisplay: {
			startDate: null,
			endDate: null
		},
		time: {
			day_start: 0,
			yrc_start: 1980,
			day_end: 0,
			yrc_end: 1985,
			step: 0
		},
		printDisplay: {
			startDate: null,
			endDate: null
		},
		print: {
			prt: {
				nyskip: 1,
				day_start: 0,
				yrc_start: 0,
				day_end: 0,
				yrc_end: 0,
				interval: 1,
				crop_yld: false,
				mgtout: false,
				hydcon: false,
				fdcout: false,
				csvout: false
			},
			objects: []
		},
		file_cio: [],
		inputs: {
			ignore_files: [],
			ignore_cio_files: [],
			custom_cio_files: []
		},
		options: {
			timeSteps: [
				{ value: 0, title: 'Daily' },
				{ value: 1, title: 'Increment' },
				{ value: 24, title: 'Hourly' },
				{ value: 96, title: '15 Minutes' },
				{ value: 1440, title: '1 Minute' }
			],
			printAll: {
				daily: false,
				monthly: false,
				yearly: false,
				avann: false
			},
			cropYldFiles: [
				{ value: 'b', title: 'Print both yearly and average annual files (recommended)' },
				{ value: 'y', title: 'Print yearly file only' },
				{ value: 'n', title: 'Do not print' }
			]
		},
		task: {
			progress: {
				percent: 0,
				message: null
			},
			process: null,
			error: null,
			running: false,
			modelMessages: [],
			modelYear: -1,
			currentPids: [],
			killMode: true
		},
		status: {
			inputs: false,
			model: false,
			output: false,
			saveScenario: false
		},
		selection: {
			inputs: true,
			model: true,
			output: true,
			debug: false
		},
		printGroups: {
			model: {
				'channel': 'Channel',
				'channel_sd': 'Channel',
				'aquifer': 'Aquifer',
				'reservoir': 'Reservoir',
				'recall': 'Point Source (Recall)',
				'ru': 'Routing Unit',
				'hyd': 'Hydrology',
				'water_allo': 'Water Allocation'
			},
			modelBasin: {
				'basin_cha': 'Channel',
				'basin_sd_cha': 'Channel',
				'basin_aqu': 'Aquifer',
				'basin_res': 'Reservoir',
				'basin_psc': 'Point Source (Recall)'
			},
			modelRegion: {
				'region_sd_cha': 'Channel',
				'region_aqu': 'Aquifer',
				'region_res': 'Reservoir',
				'region_psc': 'Point Source (Recall)'
			},
			nutrients: {
				'basin_nb': 'Basin',
				'lsunit_nb': 'Landscape Unit',
				'hru_nb': 'HRU',
				'hru-lte_nb': 'HRU-LTE',
				'region_nb': 'Region',
			},
			water: {
				'basin_wb': 'Basin',
				'lsunit_wb': 'Landscape Unit',
				'hru_wb': 'HRU',
				'hru-lte_wb': 'HRU-LTE',
				'region_wb': 'Region',
			},
			plant: {
				'basin_pw': 'Basin',
				'lsunit_pw': 'Landscape Unit',
				'hru_pw': 'HRU',
				'hru-lte_pw': 'HRU-LTE',
				'region_pw': 'Region',
			},
			losses: {
				'basin_ls': 'Basin',
				'lsunit_ls': 'Landscape Unit',
				'hru_ls': 'HRU',
				'hru-lte_ls': 'HRU-LTE',
				'region_ls': 'Region',
			},
			salts: {
				'basin_salt': 'Basin',
				'hru_salt': 'HRU',
				'ru_salt': 'Routing Unit',
				'aqu_salt': 'Aquifer',
				'channel_salt': 'Channel',
				'res_salt': 'Reservoir',
				'wetland_salt': 'Wetland',
			},
			cs: {
				'basin_cs': 'Basin',
				'hru_cs': 'HRU',
				'ru_cs': 'Routing Unit',
				'aqu_cs': 'Aquifer',
				'channel_cs': 'Channel',
				'res_cs': 'Reservoir',
				'wetland_cs': 'Wetland',
			}
		},
		printConfig: {
			inactive: [
				'region_wb',
				'region_nb',
				'region_ls',
				'region_pw',
				'region_aqu',
				'region_res',
				'region_cha',
				'region_sd_cha',
				'region_psc',
				'basin_cha', 
				'channel'
			],
			hru: ['hru_wb', 'hru_nb', 'hru_ls', 'hru_pw'],
			hru_lte: ['hru-lte_wb', 'hru-lte_nb', 'hru-lte_ls', 'hru-lte_pw'],
			showInactive: false,
			changedObjects: []
		}
	});

	const noneSelected = computed(() => {
		return !(data.selection.inputs || data.selection.model || data.selection.output);
	});

	const totalProgress = computed(() => {
		if (!data.task.running) return 0;

		let numTasks = 3;
		let eachTaskPer = 100 / numTasks;
		let thisTaskPer = eachTaskPer * data.task.progress.percent / 100;
		if (data.status.inputs) return thisTaskPer;
		if (data.status.model) return eachTaskPer + thisTaskPer;
		if (data.status.output) return eachTaskPer * 2 + thisTaskPer;

		return 0;
	});

	const modalTitle = computed(() => {
		if (data.status.inputs) return 'Writing SWAT+ Input Files';
		else if (data.status.model) return `Running SWAT+ rev. ${constants.appSettings.swatplus}`;
		else if (data.status.output) return 'Reading SWAT+ Output Files';
		return 'Running SWAT+';
	})

	const errorTitle = computed(() => {
		if (data.status.inputs) return 'There was an error writing your input files.';
		else if (data.status.output) return 'There was an error processing your output files.';
		return 'SWAT+ Editor has encountered an error.';
	})

	const currentResultsPath = computed(() => {
		return runProcess.resultsPath(data.config.input_files_dir);
	});

	const newScenarioPath = computed(() => {
		if (formatters.isNullOrEmpty(data.page.saveScenario.name)) return '';
		let scenPath = utilities.joinPaths([currentProject.projectPath, 'Scenarios']);
		return utilities.joinPaths([scenPath, formatters.toValidFileName(data.page.saveScenario.name)]);
	});

	async function get() {
		data.page.loading = true;
		data.page.error = null;

		try {
			const response = await api.get(`setup/run-settings`, currentProject.getApiHeader());
			errors.log(response.data);
			data.config = response.data.config;
			data.time = response.data.time;
			data.print = response.data.print;
			data.hasImportedWeather = response.data.imported_weather;
			data.hasObservedWeather = response.data.has_observed_weather;
			data.file_cio = response.data.file_cio;
			data.inputs = response.data.inputs;

			let cols = 0;
			for (let cat of data.file_cio) {
				if (cat.files.length > cols) cols = cat.files.length;
			}
			data.page.inputs.maxCols = cols;

			data.timeDisplay.startDate = getDateStringFromTime(data.time.day_start, data.time.yrc_start);
			data.timeDisplay.endDate = getDateStringFromTime(data.time.day_end, data.time.yrc_end, true);
			data.printDisplay.startDate = getDateStringFromTime(data.print.prt.day_start, data.print.prt.yrc_start);
			data.printDisplay.endDate = getDateStringFromTime(data.print.prt.day_end, data.print.prt.yrc_end, true);
			
			if (currentProject.isLte) {
				data.printConfig.inactive = data.printConfig.inactive.concat(data.printConfig.hru);
			} else {
				data.printConfig.inactive = data.printConfig.inactive.concat(data.printConfig.hru_lte);
			}
			
			if (formatters.isNullOrEmpty(data.config.input_files_dir)) {
				data.config.input_files_dir = currentProject.txtInOutPath;
			}
		} catch (error) {
			data.page.error = errors.logError(error, 'Unable to get project information from database.');
		}
		
		data.page.loading = false;
	}

	onMounted(async () => {
		data.page.loading = true;
		initRunProcessHandlers();
		await get();
		data.page.loading = false;
	});
	
	onUnmounted(() => removeRunProcessHandlers());

	watch(() => route.path, async () => await get())

	async function runSelected() {
		data.page.saving = true;
		data.page.saveError = null;
		data.page.showError = false;
		data.page.submitted = true;
		data.task.killMode = false;

		if (noneSelected.value) {
			data.page.saveError = 'Please select at least one task to run';
		} else {
			try {
				let startTimeUpdate = getDayYearFromDateString(data.timeDisplay.startDate);
				let endTimeUpdate = getDayYearFromDateString(data.timeDisplay.endDate, true);
				data.time.day_start = startTimeUpdate.day;
				data.time.yrc_start = startTimeUpdate.year;
				data.time.day_end = endTimeUpdate.day;
				data.time.yrc_end = endTimeUpdate.year;

				let startPrintUpdate = getDayYearFromDateString(data.printDisplay.startDate);
				let endPrintUpdate = getDayYearFromDateString(data.printDisplay.endDate, true);
				data.print.prt.day_start = startPrintUpdate.day;
				data.print.prt.yrc_start = startPrintUpdate.year;
				data.print.prt.day_end = endPrintUpdate.day;
				data.print.prt.yrc_end = endPrintUpdate.year;

				let infoData = { 
					input_files_dir: data.config.input_files_dir.replace(/\\/g,"/"),
					time: data.time,
					print: data.print.prt,
					print_objects: data.print.objects,
					inputs: data.inputs
				};
				await api.put(`setup/run-settings`, infoData, currentProject.getApiHeader());
				data.page.validated = false;
				
				if (data.selection.inputs) {
					data.page.run.show = true;
					runInputs();
				} else if (data.selection.model) {
					if (formatters.isNullOrEmpty(data.config.input_files_last_written)) 
						data.page.saveError = 'You must write input files before running the model.';
					else  {
						data.page.run.show = true;
						runModel();
					}
				} else if (data.selection.output) {
					if (formatters.isNullOrEmpty(data.config.swat_last_run)) 
						data.page.saveError = 'You must run SWAT+ before analyzing output.';
					else {
						data.page.run.show = true;
						runOutput();
					}
				}
			} catch (error) {
				data.page.saveError = errors.logError(error, 'Unable to update input files directory.');
			}
		}
		
		data.page.saving = false;
		data.page.submitted = false;
		data.page.showError = data.page.saveError !== null;
	}

	function runInputs() {
		data.status.inputs = true;
		data.status.model = false;
		data.status.output = false;
		data.status.saveScenario = false;

		let args = [
			'write_files', 
			'--project_db_file='+ currentProject.projectDb, 
			'--swat_version='+ constants.appSettings.swatplus
		];

		if (data.inputs.ignore_files.length > 0) args.push(`--ignore_files=${data.inputs.ignore_files.join(',')}`);
		if (data.inputs.ignore_cio_files.length > 0) args.push(`--ignore_cio_files=${data.inputs.ignore_cio_files.join(',')}`);
		if (data.inputs.custom_cio_files.length > 0) args.push(`--custom_cio_files=${data.inputs.custom_cio_files.join(',')}`);

		runTask(false, args, '', false);
	}

	function runModel() {
		if (data.task.killMode) return;
		data.status.inputs = false;
		data.status.model = true;
		data.status.output = false;
		data.status.saveScenario = false;

		runTask(true, null, data.config.input_files_dir, data.selection.debug);
	}

	function runOutput() {
		if (data.task.killMode) return;
		data.status.inputs = false;
		data.status.model = false;
		data.status.output = true;
		data.status.saveScenario = false;

		let args = [
			'read_output', 
			'--output_files_dir='+ data.config.input_files_dir.replace(/\\/g,"/"), 
			'--output_db_file='+ runProcess.outputDbPath(data.config.input_files_dir),
			'--swat_version='+ constants.appSettings.swatplus,
			'--editor_version='+ constants.appSettings.version,
			'--project_name='+ currentProject.name
		];

		runTask(false, args, '', false);
	}

	function saveScenario() {
		data.page.saveScenario.error = null;

		if (formatters.isNullOrEmpty(data.page.saveScenario.name)) {
			data.page.saveScenario.error = 'Please enter a name for the scenario.';
		} else {
			data.status.inputs = false;
			data.status.model = false;
			data.status.output = false;
			data.status.saveScenario = true;

			let args = [
				'save_scenario', 
				'--project_db_file='+ currentProject.projectDb,
				'--input_files_dir='+ data.config.input_files_dir,
				'--output_files_dir='+ currentResultsPath.value,
				'--project_name='+ formatters.toValidFileName(data.page.saveScenario.name)
			];

			runTask(false, args, '', false);
		}
	}

	function runTask(isSwat:boolean, args:string[]|null, inputDir:string, debug:boolean) {
		data.task.error = null;
		data.task.running = true;
		data.task.progress = {
			percent: 0,
			message: null
		};

		data.task.modelMessages = [];
		data.task.modelYear = -1;

		let currentPid = null;
		if (isSwat) {
			currentPid = runProcess.runSwatProc(inputDir, debug);
		} else {
			currentPid = runProcess.runApiProc('runmodel', 'swatplus_api', args||[]);
		}
		if (currentPid != null) data.task.currentPids.push(currentPid);
	}

	let listeners:any = {
		stdout: undefined,
		stderr: undefined,
		close: undefined,
		stdoutSwat: undefined,
		stderrSwat: undefined,
		closeSwat: undefined
	}

	function initRunProcessHandlers() {
		listeners.stdout = runProcess.processStdout('runmodel', (stdData:any) => {
			data.task.progress = runProcess.getApiOutput(stdData);
		});

		listeners.stdoutSwat = runProcess.processStdout('run-swat', (stdData:any) => {
			let str = stdData.toString().trim();
			let arr = str.split(' ').filter(function(el:any) { return el !== '' });
			let yrIdx = arr.indexOf('Yr');
			if (yrIdx > -1) {
				let thisYr = arr[yrIdx + 1];
				if (thisYr !== data.task.modelYear) {
					let modelStr = '';
					try {
						for (let i = 0; i < yrIdx - 3; i++) {
							modelStr += arr[i] + ' ';
						}
					} catch (error) { modelStr = 'model'; }

					let totalYears = data.time.yrc_end - data.time.yrc_start + 1;
					let yrProg = data.time.yrc_start + Number(thisYr) - 1;
					data.task.modelYear = thisYr;
					data.task.progress = { percent: thisYr / totalYears * 100, message: `Executing ${formatters.toLower(modelStr)} year ${yrProg} (${thisYr} of ${totalYears})` };
				}
			} else {
				data.task.progress = { percent: 5, message: 'Running SWAT+' };
			}
		});
		
		listeners.stderr = runProcess.processStderr('runmodel', async (stdData:any) => {
			console.log(`stderr: ${stdData}`);
			data.task.error = stdData;
			data.task.running = false;
		});

		listeners.stderrSwat = runProcess.processStderr('run-swat', async (stdData:any) => {
			console.log(`stderr: ${stdData}`);
			data.task.error = 'There was an error running SWAT+';
			if (data.task.modelMessages.length > 500) data.task.modelMessages = [];
			data.task.modelMessages.push(stdData);
			await get();
			data.task.running = false;
		});
		
		listeners.close = runProcess.processClose('runmodel', async (code:any) => {
			if (formatters.isNullOrEmpty(data.task.error)) {
				if (data.status.inputs && data.selection.model) {
					errors.log('Done inputs, run model');
					runModel();
				} else if (data.status.model) {
					errors.log('Done model');
					await api.put(`setup/save-model-run`, {}, currentProject.getApiHeader());
					if (data.selection.output) {
						runOutput();
					} else {
						data.task.running = false;
						closeTaskModals();
						await get();
						data.page.completed.show = true;
						data.task.currentPids = [];
					}
				} else if (data.status.output) {
					errors.log('Done output');
					await api.put(`setup/save-output-read`, {}, currentProject.getApiHeader());
					data.task.running = false;
					closeTaskModals();
					await get();
					data.page.completed.show = true;
					data.task.currentPids = [];
				} else if (data.status.saveScenario) {
					data.task.running = false;
					closeTaskModals();
					data.page.savedScenario.show = true;
					data.status.saveScenario = false;
				} else {
					errors.log('Done all');
					data.task.running = false;
					closeTaskModals();
					await get();
					data.page.completed.show = true;
					data.task.currentPids = [];
				}
			}
		});

		listeners.closeSwat = runProcess.processClose('run-swat', async (code:any) => {
			if (formatters.isNullOrEmpty(data.task.error)) {
				errors.log('Done model');
				await api.put(`setup/save-model-run`, {}, currentProject.getApiHeader());
				if (data.selection.output) {
					runOutput();
				} else {
					data.task.running = false;
					closeTaskModals();
					await get();
					data.page.completed.show = true;
					data.task.currentPids = [];
				}
			}
		});
	}

	function removeRunProcessHandlers() {
		if (listeners.stdout) listeners.stdout();
		if (listeners.stderr) listeners.stderr();
		if (listeners.close) listeners.close();
		if (listeners.stdoutSwat) listeners.stdoutSwat();
		if (listeners.stderrSwat) listeners.stderrSwat();
		if (listeners.closeSwat) listeners.closeSwat();
	}

	function cancelTask() {
		data.task.killMode = true;
		data.task.error = null;
		for (let pid of data.task.currentPids)
			runProcess.killProcess(pid);
		
		data.task.currentPids = [];
		data.task.running = false;
		closeTaskModals();
	}

	function closeTaskModals() {
		data.page.run.show = false;
		data.page.saveScenario.show = false;
	}

	function getDateStringFromTime(day:any, year:any, isEnd=false) {
		if (year === 0) return null;
		if (isEnd && day === 0) return `${year}-12-31`;
		let d = moment(`${year}-01-01`);
		if (day !== 0) d.add(day-1, 'days');
		return d.format('YYYY-MM-DD');
	}
	
	function getDayYearFromDateString(value:any, isEnd=false) {
		if (formatters.isNullOrEmpty(value)) {
			return {
				day: 0,
				year: 0
			};
		}

		let d = moment(String(value));
		let day = d.dayOfYear();

		if (!isEnd && day === 1) day = 0;
		else if (isEnd && d.month() === 11 && d.date() === 31) day = 0;

		return {
			day: day,
			year: d.year()
		};
	}

	function checkAllDaily() {
		//data.options.printAll.daily = !data.options.printAll.daily;
		for (let i = 0; i < data.print.objects.length; i++) {
			data.print.objects[i].daily = data.options.printAll.daily;
			pushChg(i);
		}
	}

	function checkAllMonthly() {
		//data.options.printAll.monthly = !data.options.printAll.monthly;
		for (let i = 0; i < data.print.objects.length; i++) {
			data.print.objects[i].monthly = data.options.printAll.monthly;
			pushChg(i);
		}
	}

	function checkAllYearly() {
		//data.options.printAll.yearly = !data.options.printAll.yearly;
		for (let i = 0; i < data.print.objects.length; i++) {
			data.print.objects[i].yearly = data.options.printAll.yearly;
			pushChg(i);
		}
	}

	function checkAllAvann() {
		//data.options.printAll.avann = !data.options.printAll.avann;
		for (let i = 0; i < data.print.objects.length; i++) {
			data.print.objects[i].avann = data.options.printAll.avann;
			pushChg(i);
		}
	}

	function pushChg(i:number) {
		if (data.printConfig.changedObjects.indexOf(i) == -1) {
			data.printConfig.changedObjects.push(i);
		}
	}

	function printIndex(name:any) {
		return data.print.objects.findIndex((x:any) => { return x.name === name});
	}

	function inputCustomizationColor(name:any) {
		return data.inputs.ignore_files.includes(name) || data.inputs.ignore_cio_files.includes(name) || data.inputs.custom_cio_files.includes(name) ? 'primary' : undefined;
	}
</script>

<template>
	<project-container :loading="data.page.loading" add-error-frame>
		<v-main>
			<div class="py-3 px-6">
				<div v-if="!data.hasImportedWeather">
					<h1 class="text-h5">Not ready to run the model</h1>

					<v-alert color="info" icon="$info" variant="tonal" border="start" class="my-4">
						You must add weather generators and stations before writing inputs and running the model.					
					</v-alert>

					<v-btn to="/edit/climate/wgn" variant="flat" color="primary">Add Now</v-btn>
				</div>
				
				<v-form v-else @submit.prevent="runSelected">
					<error-alert as-popup v-model="data.page.showError" :show="data.page.showError" :text="data.page.saveError" :timeout="-1"></error-alert>

					<h1 class="text-h5 mb-6">Confirm Simulation Settings</h1>

					<v-expansion-panels variant="accordion">
						<v-expansion-panel>
							<v-expansion-panel-title>
								<v-row no-gutters>
									<v-col cols="12" md="4" class="d-flex justify-start font-weight-bold">Choose where to write your input files</v-col>
									<v-col cols="8" class="text-right pr-6 text-secondary d-none d-md-block">{{data.config.input_files_dir}}</v-col>
								</v-row>
							</v-expansion-panel-title>
							<v-expansion-panel-text>
								<div class="mt-5">
									<select-folder-input v-model="data.config.input_files_dir" :value="data.config.input_files_dir"
										label="Directory to write your input files"
										required invalidFeedback="Please select a folder"></select-folder-input>
								</div>
								<div>
									<v-btn @click="data.page.inputs.show = true" variant="flat" class="border">Advanced: Customize files to write...</v-btn>
								</div>
							</v-expansion-panel-text>
						</v-expansion-panel>
						<v-expansion-panel>
							<v-expansion-panel-title>
								<v-row no-gutters>
									<v-col cols="12" md="4" class="d-flex justify-start font-weight-bold">Set your simulation period</v-col>
									<v-col cols="8" class="text-right pr-6 text-secondary d-none d-md-block">{{data.time.yrc_start}} - {{data.time.yrc_end}}</v-col>
								</v-row>
							</v-expansion-panel-title>
							<v-expansion-panel-text>
								<div class="mt-5">
									<p v-if="data.hasObservedWeather">
										Make sure your simulation dates fall within the dates in your 
										<router-link to="/edit/climate/stations" class="text-primary">observed weather files</router-link>. 
										Simulation dates outside this range will result in simulated weather.
									</p>

									<div class="form-group mb-5">
										<v-text-field v-model="data.timeDisplay.startDate" 
											label="Starting date of simulation" required type="date"
											:hint="formatters.toDate(data.timeDisplay.startDate, 'MMMM D, YYYY')||''" persistent-hint></v-text-field>
									</div>
									<div class="form-group">
										<v-text-field v-model="data.timeDisplay.endDate" 
											label="Ending date of simulation" required type="date"
											:hint="formatters.toDate(data.timeDisplay.endDate, 'MMMM D, YYYY')||''" persistent-hint></v-text-field>
									</div>

									<v-expansion-panels variant="inset" class="my-5">
										<v-expansion-panel title="Advanced Options...">
											<v-expansion-panel-text>
												<div class="mt-5">
													<v-select v-model="data.time.step" :items="data.options.timeSteps" 
														label="Time steps in a day for rainfall, runoff and routing" required></v-select>
												</div>
											</v-expansion-panel-text>
										</v-expansion-panel>
									</v-expansion-panels>
								</div>
							</v-expansion-panel-text>
						</v-expansion-panel>
						<v-expansion-panel>
							<v-expansion-panel-title>
								<v-row no-gutters>
									<v-col cols="12" md="4" class="d-flex justify-start font-weight-bold">Choose output to print</v-col>
									<v-col cols="8" class="text-right pr-6 text-secondary d-none d-md-block"></v-col>
								</v-row>
							</v-expansion-panel-title>
							<v-expansion-panel-text>
								<v-row class="mt-5">
									<v-col cols="12" lg="6">
										<div class="form-group mb-5">
											<v-text-field type="number" min="0" required v-model.number="data.print.prt.nyskip"
												label="Warm-up period" hint="Number of years to skip printing output" persistent-hint></v-text-field>
										</div>

										<v-table class="table-editor" density="compact">
											<thead>
												<tr class="bg-surface">
													<th class="bg-secondary-tonal"></th>
													<th class="bg-secondary-tonal">Daily</th>
													<th class="bg-secondary-tonal">Monthly</th>
													<th class="bg-secondary-tonal">Yearly</th>
													<th class="bg-secondary-tonal">Average</th>
													<th class="bg-secondary-tonal" title="SWAT+ Output File/Table">Outputs</th>
												</tr>
												<tr>
													<th></th>
													<th class="text-center mx-auto"><v-checkbox density="compact" hide-details v-model="data.options.printAll.daily" @update:model-value="checkAllDaily"></v-checkbox></th>
													<th class="text-center"><v-checkbox density="compact" hide-details v-model="data.options.printAll.monthly" @update:model-value="checkAllMonthly"></v-checkbox></th>
													<th class="text-center"><v-checkbox density="compact" hide-details v-model="data.options.printAll.yearly" @update:model-value="checkAllYearly"></v-checkbox></th>
													<th class="text-center"><v-checkbox density="compact" hide-details v-model="data.options.printAll.avann" @update:model-value="checkAllAvann"></v-checkbox></th>
													<th></th>
												</tr>
											</thead>
											<tbody>
												<tr class="bg-secondary-tonal">
													<th colspan="6">Model Components</th>
												</tr>
												<tr v-for="([k, v], i) in Object.entries(data.printGroups.model)" :key="i" v-show="!data.printConfig.inactive.includes(k) || data.printConfig.showInactive">
													<td>{{v}}</td>
													<td class="text-center"><v-checkbox density="compact" hide-details v-model="data.print.objects[printIndex(k)].daily" /></td>
													<td class="text-center"><v-checkbox density="compact" hide-details v-model="data.print.objects[printIndex(k)].monthly" /></td>
													<td class="text-center"><v-checkbox density="compact" hide-details v-model="data.print.objects[printIndex(k)].yearly" /></td>
													<td class="text-center"><v-checkbox density="compact" hide-details v-model="data.print.objects[printIndex(k)].avann" /></td>
													<td class="code text-muted">
														{{k}}
														<div v-if="k === 'channel_sd'">channel_sdmorph</div>
													</td>
												</tr>
												<tr class="bg-secondary-tonal">
													<th colspan="6">Basin Model Components</th>
												</tr>
												<tr v-for="([k, v], i) in Object.entries(data.printGroups.modelBasin)" :key="i" v-show="!data.printConfig.inactive.includes(k) || data.printConfig.showInactive">
													<td>{{v}}</td>
													<td class="text-center"><v-checkbox density="compact" hide-details v-model="data.print.objects[printIndex(k)].daily" /></td>
													<td class="text-center"><v-checkbox density="compact" hide-details v-model="data.print.objects[printIndex(k)].monthly" /></td>
													<td class="text-center"><v-checkbox density="compact" hide-details v-model="data.print.objects[printIndex(k)].yearly" /></td>
													<td class="text-center"><v-checkbox density="compact" hide-details v-model="data.print.objects[printIndex(k)].avann" /></td>
													<td class="code text-muted">
														{{k}}
														<div v-if="k === 'basin_sd_cha'">basin_sd_chamorph</div>
													</td>
												</tr>
												<tr class="bg-secondary-tonal" v-show="data.printConfig.showInactive">
													<th colspan="6">Region Model Components</th>
												</tr>
												<tr v-for="([k, v], i) in Object.entries(data.printGroups.modelRegion)" :key="i" v-show="!data.printConfig.inactive.includes(k) || data.printConfig.showInactive">
													<td>{{v}}</td>
													<td class="text-center"><v-checkbox density="compact" hide-details v-model="data.print.objects[printIndex(k)].daily" /></td>
													<td class="text-center"><v-checkbox density="compact" hide-details v-model="data.print.objects[printIndex(k)].monthly" /></td>
													<td class="text-center"><v-checkbox density="compact" hide-details v-model="data.print.objects[printIndex(k)].yearly" /></td>
													<td class="text-center"><v-checkbox density="compact" hide-details v-model="data.print.objects[printIndex(k)].avann" /></td>
													<td class="code text-muted">{{k}}</td>
												</tr>
												<tr class="bg-secondary-tonal">
													<th colspan="6">Nutrient Balance</th>
												</tr>
												<tr v-for="([k, v], i) in Object.entries(data.printGroups.nutrients)" :key="i" v-show="!data.printConfig.inactive.includes(k) || data.printConfig.showInactive">
													<td>{{v}}</td>
													<td class="text-center"><v-checkbox density="compact" hide-details v-model="data.print.objects[printIndex(k)].daily" /></td>
													<td class="text-center"><v-checkbox density="compact" hide-details v-model="data.print.objects[printIndex(k)].monthly" /></td>
													<td class="text-center"><v-checkbox density="compact" hide-details v-model="data.print.objects[printIndex(k)].yearly" /></td>
													<td class="text-center"><v-checkbox density="compact" hide-details v-model="data.print.objects[printIndex(k)].avann" /></td>
													<td class="code text-muted">{{k}}</td>
												</tr>
												<tr class="bg-secondary-tonal">
													<th colspan="6">Water Balance</th>
												</tr>
												<tr v-for="([k, v], i) in Object.entries(data.printGroups.water)" :key="i" v-show="!data.printConfig.inactive.includes(k) || data.printConfig.showInactive">
													<td>{{v}}</td>
													<td class="text-center"><v-checkbox density="compact" hide-details v-model="data.print.objects[printIndex(k)].daily" /></td>
													<td class="text-center"><v-checkbox density="compact" hide-details v-model="data.print.objects[printIndex(k)].monthly" /></td>
													<td class="text-center"><v-checkbox density="compact" hide-details v-model="data.print.objects[printIndex(k)].yearly" /></td>
													<td class="text-center"><v-checkbox density="compact" hide-details v-model="data.print.objects[printIndex(k)].avann" /></td>
													<td class="code text-muted">{{k}}</td>
												</tr>
												<tr class="bg-secondary-tonal">
													<th colspan="6">Plant Weather</th>
												</tr>
												<tr v-for="([k, v], i) in Object.entries(data.printGroups.plant)" :key="i" v-show="!data.printConfig.inactive.includes(k) || data.printConfig.showInactive">
													<td>{{v}}</td>
													<td class="text-center"><v-checkbox density="compact" hide-details v-model="data.print.objects[printIndex(k)].daily" /></td>
													<td class="text-center"><v-checkbox density="compact" hide-details v-model="data.print.objects[printIndex(k)].monthly" /></td>
													<td class="text-center"><v-checkbox density="compact" hide-details v-model="data.print.objects[printIndex(k)].yearly" /></td>
													<td class="text-center"><v-checkbox density="compact" hide-details v-model="data.print.objects[printIndex(k)].avann" /></td>
													<td class="code text-muted">{{k}}</td>
												</tr>
												<tr class="bg-secondary-tonal">
													<th colspan="6">Losses</th>
												</tr>
												<tr v-for="([k, v], i) in Object.entries(data.printGroups.losses)" :key="i" v-show="!data.printConfig.inactive.includes(k) || data.printConfig.showInactive">
													<td>{{v}}</td>
													<td class="text-center"><v-checkbox density="compact" hide-details v-model="data.print.objects[printIndex(k)].daily" /></td>
													<td class="text-center"><v-checkbox density="compact" hide-details v-model="data.print.objects[printIndex(k)].monthly" /></td>
													<td class="text-center"><v-checkbox density="compact" hide-details v-model="data.print.objects[printIndex(k)].yearly" /></td>
													<td class="text-center"><v-checkbox density="compact" hide-details v-model="data.print.objects[printIndex(k)].avann" /></td>
													<td class="code text-muted">{{k}}</td>
												</tr>
												<tr class="bg-secondary-tonal">
													<th colspan="6">Salts</th>
												</tr>
												<tr v-for="([k, v], i) in Object.entries(data.printGroups.salts)" :key="i" v-show="!data.printConfig.inactive.includes(k) || data.printConfig.showInactive">
													<td>{{v}}</td>
													<td class="text-center"><v-checkbox density="compact" hide-details v-model="data.print.objects[printIndex(k)].daily" /></td>
													<td class="text-center"><v-checkbox density="compact" hide-details v-model="data.print.objects[printIndex(k)].monthly" /></td>
													<td class="text-center"><v-checkbox density="compact" hide-details v-model="data.print.objects[printIndex(k)].yearly" /></td>
													<td class="text-center"><v-checkbox density="compact" hide-details v-model="data.print.objects[printIndex(k)].avann" /></td>
													<td class="code text-muted">{{k}}</td>
												</tr>
												<tr class="bg-secondary-tonal">
													<th colspan="6">Constituents</th>
												</tr>
												<tr v-for="([k, v], i) in Object.entries(data.printGroups.cs)" :key="i" v-show="!data.printConfig.inactive.includes(k) || data.printConfig.showInactive">
													<td>{{v}}</td>
													<td class="text-center"><v-checkbox density="compact" hide-details v-model="data.print.objects[printIndex(k)].daily" /></td>
													<td class="text-center"><v-checkbox density="compact" hide-details v-model="data.print.objects[printIndex(k)].monthly" /></td>
													<td class="text-center"><v-checkbox density="compact" hide-details v-model="data.print.objects[printIndex(k)].yearly" /></td>
													<td class="text-center"><v-checkbox density="compact" hide-details v-model="data.print.objects[printIndex(k)].avann" /></td>
													<td class="code text-muted">{{k}}</td>
												</tr>
											</tbody>
										</v-table>

										<p class="mb-0 mt-3">
											<v-checkbox hide-details v-model="data.printConfig.showInactive">
												<template v-slot:label>Show all print objects? Leave unchecked to hide print objects that are not relevant for this project.</template>
											</v-checkbox>
										</p>
									</v-col>
									<v-col cols="12" lg="6">
										<v-expansion-panels variant="inset">
											<v-expansion-panel title="Advanced Options...">
												<v-expansion-panel-text>
													<div class="my-5">
														<v-select v-model="data.print.prt.crop_yld" :items="data.options.cropYldFiles" 
															label="Print crop yield output files" required 
															hint="Crop yield files are required for SWAT+ Check, so we recommend printing." persistent-hint></v-select>
													</div>

													<div class="d-flex">
														<div class="pr-3">
															<v-checkbox density="comfortable" hide-details v-model="data.print.prt.hydcon" label="Hydrograph connect output file"></v-checkbox>
															<v-checkbox density="comfortable" hide-details v-model="data.print.prt.csvout" label="Print output files in CSV format"></v-checkbox>
														</div>
														<div>
															<v-checkbox density="comfortable" hide-details v-model="data.print.prt.mgtout" label="Management output file"></v-checkbox>
															<v-checkbox density="comfortable" hide-details v-model="data.print.prt.fdcout" label="Flow duration curve output file"></v-checkbox>
														</div>
													</div>

													<v-divider class="my-4"></v-divider>

													<div class="form-group mb-5">
														<v-text-field v-model="data.printDisplay.startDate" 
															label="Date to start printing output" required type="date"
															:hint="formatters.toDate(data.printDisplay.startDate, 'MMMM D, YYYY')||'Leave blank to print entire simulation period'" persistent-hint></v-text-field>
													</div>
													<div class="form-group mb-5">
														<v-text-field v-model="data.printDisplay.endDate" 
															label="Date to stop printing output" required type="date"
															:hint="formatters.toDate(data.printDisplay.endDate, 'MMMM D, YYYY')||'Leave blank to print entire simulation period'" persistent-hint></v-text-field>
													</div>

													<div>
														<v-text-field v-model="data.print.prt.interval" 
															label="Daily print within the period (e.g., interval=2 will print every other day)" required type="number" min="0"></v-text-field>
													</div>
												</v-expansion-panel-text>
											</v-expansion-panel>
										</v-expansion-panels>
									</v-col>
								</v-row>
							</v-expansion-panel-text>
						</v-expansion-panel>
					</v-expansion-panels>

					<v-divider class="my-6"></v-divider>

					<h1 class="text-h5 mb-4">Run SWAT+</h1>

					<p>
						Before running the model, we must write the input files used by the model.
						If you have modified your inputs via the edit section since last running the model, be sure to keep this box checked.
						Check the third box to read your output files into a SQLite database. 
						This will be used by the visualization tool in QSWAT+. If you do not intend to use this feature, 
						you may uncheck this box to save time.
					</p>

					<v-card>
						<v-card-item>
							<div class="d-flex align-start my-3">
								<div class="mr-4">
									<v-checkbox density="compact" hide-details v-model="data.selection.inputs" id="select_inputs"></v-checkbox>
								</div>
								<div class="pt-1">
									<label for="select_inputs"><b>Write input files</b></label>
									<span class="text-secondary" v-if="!formatters.isNullOrEmpty(data.config.input_files_last_written)">
										<br>Last written {{ formatters.toDate(data.config.input_files_last_written) }}
									</span>
								</div>
							</div>
						</v-card-item>

						<v-divider></v-divider>

						<v-card-item>
							<div class="d-flex align-start my-3">
								<div class="mr-4">
									<v-checkbox density="compact" hide-details v-model="data.selection.model" id="select_model"></v-checkbox>
								</div>
								<div class="pt-1">
									<label for="select_model">
										Run SWAT+ rev. {{ constants.appSettings.swatplus }}
										<open-file :file-path="constants.globals.swat_path" class="text-secondary"><font-awesome-icon :icon="['fas', 'fa-folder-open']" class="ml-1"></font-awesome-icon></open-file>
									</label>
									<span class="text-secondary" v-if="!formatters.isNullOrEmpty(data.config.swat_last_run)">
										<br>Last run {{ formatters.toDate(data.config.swat_last_run) }}
									</span>
									<div class="mt-1" v-if="data.selection.model">
										<v-checkbox density="compact" hide-details v-model="data.selection.debug" label="Use debug version?"></v-checkbox>
									</div>
								</div>
							</div>
						</v-card-item>

						<v-divider></v-divider>

						<v-card-item>
							<div class="d-flex align-start my-3">
								<div class="mr-4">
									<v-checkbox density="compact" hide-details v-model="data.selection.output" id="select_output"></v-checkbox>
								</div>
								<div class="pt-1">
									<label for="select_output"><b>Analyze output for visualization</b></label>
									<span class="text-secondary" v-if="!formatters.isNullOrEmpty(data.config.output_last_imported)">
										<br>Last analyzed {{ formatters.toDate(data.config.output_last_imported) }}
									</span>
								</div>
							</div>
						</v-card-item>
					</v-card>

					<v-alert v-if="currentProject.isLte" color="info" icon="$info" variant="tonal" border="start" class="my-4">
						Looking for <strong>SWAT+ Check</strong>? SWAT+ Check is not available in SWAT+ lte.
						You must run the full version of SWAT+ to get the checker functionality.					
					</v-alert>

					<action-bar full-width>
						<v-btn type="submit" :loading="data.page.saving" :disabled="data.page.saving || noneSelected" variant="flat" color="primary" class="mr-2">
							Save Settings &amp; Run Selected
						</v-btn>
						<v-menu>
							<template v-slot:activator="{ props }">
								<v-btn type="button" variant="flat" color="primary" class="mr-2" v-bind="props">More Actions...</v-btn>
							</template>
							<v-list>
								<v-list-item v-if="!formatters.isNullOrEmpty(data.config.output_last_imported) && !currentProject.isLte" to="/check"><v-list-item-title>Run SWAT+ Check</v-list-item-title></v-list-item>
								<swat-plus-toolbox-button v-if="!formatters.isNullOrEmpty(data.config.swat_last_run) && !currentProject.isLte" :ran-swat="!formatters.isNullOrEmpty(data.config.swat_last_run)" as-list-item text="Open SWAT+ Toolbox"></swat-plus-toolbox-button>
								<v-list-item @click="data.page.completed.show = false; data.page.saveScenario.show = true"><v-list-item-title>Save Scenario</v-list-item-title></v-list-item>
								<open-file as-list-item :file-path="currentResultsPath">Open Results Directory</open-file>
							</v-list>
						</v-menu>
						<v-btn type="button" variant="flat" color="secondary" @click="utilities.exit" class="ml-auto">Exit SWAT+ Editor</v-btn>
					</action-bar>
				</v-form>

				<v-dialog v-model="data.page.run.show" :max-width="constants.dialogSizes.lg" persistent>
					<v-card :title="modalTitle">
						<v-card-text>
							<error-alert :text="data.page.run.error"></error-alert>
							<stack-trace-error v-if="!formatters.isNullOrEmpty(data.task.error) && !data.status.model" :error-title="errorTitle" :stack-trace="data.task.error.toString()" />

							<v-alert variant="tonal" type="error" icon="$error" border="start" v-if="!formatters.isNullOrEmpty(data.task.error) && data.status.model" class="mb-4">
								{{data.task.error}}
								<span v-if="!data.selection.debug">Please run the model in debug mode to get a detailed error report.</span>
								<span v-else>
									If you cannot determine the cause of the error, please copy and paste the output log below to the 
									<open-in-browser url="https://groups.google.com/d/forum/swatplus" text="SWAT+ model user group" />.
								</span>
							</v-alert>
							
							<div v-if="data.task.running">
								<v-progress-linear :model-value="data.task.progress.percent" color="primary" height="15" striped></v-progress-linear>
								<p>
									{{data.task.progress.message}}
								</p>
							</div>
							<div v-if="data.status.model && !formatters.isNullOrEmpty(data.task.error)" class="scroll-bottom mt-2">
								<pre><div v-for="(message, i) in data.task.modelMessages" :key="i">{{message}}</div></pre>
							</div>
						</v-card-text>
						<v-divider></v-divider>
						<v-card-actions>
							<v-btn @click="cancelTask">Cancel</v-btn>
						</v-card-actions>
					</v-card>
				</v-dialog>

				<v-dialog v-model="data.page.completed.show" :max-width="constants.dialogSizes.sm">
					<v-card title="All selected tasks have completed">
						<v-card-item>
							<div class="mb-8">
								<v-btn v-if="!formatters.isNullOrEmpty(data.config.output_last_imported) && !currentProject.isLte" type="button" variant="flat" color="primary" size="large" rounded="xl" to="/check" block class="my-2">Run SWAT+ Check</v-btn>
								<swat-plus-toolbox-button v-if="!formatters.isNullOrEmpty(data.config.swat_last_run) && !currentProject.isLte" :ran-swat="!formatters.isNullOrEmpty(data.config.swat_last_run)" variant="flat" color="primary" size="large" rounded="xl" block class="my-2" no-icon text="Open SWAT+ Toolbox"></swat-plus-toolbox-button>
								<v-btn type="button" block variant="flat" color="primary" size="large" rounded="xl" @click="data.page.completed.show = false; data.page.saveScenario.show = true" class="my-2">Save Scenario</v-btn>
								<open-file button block variant="flat" color="primary" size="large" rounded="xl" :file-path="currentResultsPath" class="my-2">Open Results Directory</open-file>
								<v-row class="mt-2" no-gutters>
									<v-col md class="mr-2"><v-btn type="button" variant="flat" color="secondary" size="large" rounded="xl" @click="data.page.completed.show = false" block class="mr-1">Back to Editor</v-btn></v-col>
									<v-col md><v-btn type="button" variant="flat" color="secondary" size="large" rounded="xl" @click="utilities.exit" block>Exit SWAT+ Editor</v-btn></v-col>
								</v-row>
							</div>
						</v-card-item>
					</v-card>
				</v-dialog>

				<v-dialog v-model="data.page.saveScenario.show" :max-width="constants.dialogSizes.lg" persistent>
					<v-card :title="modalTitle">
						<v-card-text>
							<error-alert :text="data.page.saveScenario.error"></error-alert>
							<stack-trace-error v-if="!formatters.isNullOrEmpty(data.task.error)" error-title="There was an error saving your scenario" :stack-trace="data.task.error.toString()" />

							<div v-if="data.task.running">
								<v-progress-linear :model-value="data.task.progress.percent" color="primary" height="15" striped></v-progress-linear>
								<p>
									{{data.task.progress.message}}
								</p>
							</div>
							<div v-else>
								<p>
									Saving a scenario will make a copy your project database as well as all model input and output text files.
									We recommend running the model before saving your scenario. After saving completes, any additional changes
									made to your project will not affect the saved scenario. 
									You may load the saved scenario back to the editor from the 
									<router-link to="/">project setup screen</router-link>.
								</p>

								<div class="form-group">
									<v-text-field type="text" required v-model="data.page.saveScenario.name"
										label="Give your scenario a unique name" 
										hint="Will create a new folder with this name under your project's Scenarios directory. Cannot be the same name as an existing scenario." persistent-hint></v-text-field>
								</div>
							</div>

						</v-card-text>
						<v-divider></v-divider>
						<v-card-actions>
							<v-btn v-if="formatters.isNullOrEmpty(data.task.error)" :loading="data.task.running" @click="saveScenario" color="primary" variant="text">
								Save Scenario
							</v-btn>
							<v-btn @click="cancelTask">Cancel</v-btn>
						</v-card-actions>
					</v-card>
				</v-dialog>

				<v-dialog v-model="data.page.savedScenario.show" :max-width="constants.dialogSizes.sm">
					<v-card title="Scenario Saved">
						<v-card-text>
							<p>
								<b>Your scenario has been saved.</b>
								Any additional changes made to your project will not affect the saved scenario. 
								You may load the saved scenario back to the editor from the <router-link to="/">project setup screen</router-link>.
							</p>
						</v-card-text>
						<v-divider></v-divider>
						<v-card-actions>
							<open-file button color="primary" variant="text" :file-path="newScenarioPath">Open Scenario Directory</open-file>
							<v-btn @click="data.page.savedScenario.show = false">Close</v-btn>
						</v-card-actions>
					</v-card>
				</v-dialog>

				<v-dialog v-model="data.page.inputs.show" scrollable>
					<v-card title="Customize input files to write">
						<v-card-text>
							<p>
								By default, the editor will write all SWAT+ input files determined by your model setup.
								If you are modifying any files outside of the editor, you may choose to skip writing them below.
								Be sure the files still exist in your input file directory, otherwise the model will crash.
								You may also choose to ignore input files entirely by selecting not to write to the file.cio.
								This option is not recommended for novice users and may break your model.
							</p>

							<v-table small density="compact">
								<thead>
									<tr class="bg-secondary-tonal">
										<th>Category</th>
										<th :colspan="data.page.inputs.maxCols">Files</th>
									</tr>
								</thead>
								<tbody>
									<tr v-for="cat in data.file_cio" :key="cat.category">
										<td><b>{{cat.category}}</b></td>
										<td v-for="f in cat.files" :key="f.name" style="white-space: nowrap;">
											<v-btn variant="text" append-icon="fas fa-angle-down" class="plain-button" :color="inputCustomizationColor(f.name)">
												{{ f.available ? f.name : 'none' }}
												<v-menu activator="parent">
													<v-card>
														<v-card-item>
															<label class="d-flex align-center" v-if="f.available">
																<div style="width:30px"><v-checkbox hide-details v-model="data.inputs.ignore_files" :value="f.name" density="compact"></v-checkbox></div>
																<div>provide my own {{ f.name }}</div>
															</label>
															<label class="d-flex align-center" v-if="f.available">
																<div style="width:30px"><v-checkbox hide-details v-model="data.inputs.ignore_cio_files" :value="f.name" density="compact"></v-checkbox></div>
																<div>exclude {{ f.name }} from file.cio</div>
															</label>
															<label class="d-flex align-center" v-if="!f.available">
																<div style="width:30px"><v-checkbox hide-details v-model="data.inputs.custom_cio_files" :value="f.name" density="compact"></v-checkbox></div>
																<div>provide my own {{ f.name }}</div>
															</label>
														</v-card-item>
													</v-card>
													
												</v-menu>
											</v-btn>
										</td>
										<td v-if="cat.files.length < data.page.inputs.maxCols" :colspan="data.page.inputs.maxCols - cat.files.length"></td>
									</tr>
								</tbody>
							</v-table>
						</v-card-text>
						<v-divider></v-divider>
						<v-card-actions>
							<v-btn @click="data.page.inputs.show = false" color="primary">Save &amp; Close</v-btn>
						</v-card-actions>
					</v-card>
				</v-dialog>
			</div>
		</v-main>
	</project-container>
</template>

<style scoped>
.scroll-bottom {
	width: 100%;
	height: 350px;
	border: 1px solid #ccc;
	overflow:auto;
	padding: 5px;
	font-size: 0.8rem;
}

.plain-button {
	text-transform:lowercase; 
	letter-spacing: normal;
}
</style>