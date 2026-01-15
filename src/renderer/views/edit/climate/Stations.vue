<script setup lang="ts">
	import { reactive, ref, onMounted, onUnmounted, computed, watch } from 'vue';
	import { useVuelidate } from '@vuelidate/core';
	import { required, requiredIf, helpers } from '@vuelidate/validators';
	import { useRoute } from 'vue-router';
	import { useHelpers } from '@/helpers';
	const route = useRoute();
	const { api, constants, currentProject, errors, formatters, runProcess, utilities } = useHelpers();

	const grid = ref();

	let table:any = {
		apiUrl: 'climate/stations',
		headers: [
			{ key: 'name', label: 'Name' },
			{ key: 'wgn', label: 'Wgn', type: 'object', objectRoutePath: '/edit/climate/wgn/edit/' },
			{ key: 'pcp', label: 'Precipitation', type: 'file', defaultIfNull: 'sim' },
			{ key: 'tmp', label: 'Temperature', type: 'file', defaultIfNull: 'sim' },
			{ key: 'slr', label: 'Solar radiation', type: 'file', defaultIfNull: 'sim' },
			{ key: 'hmd', label: 'Rel. humidity', type: 'file', defaultIfNull: 'sim' },
			{ key: 'wnd', label: 'Wind speed', type: 'file', defaultIfNull: 'sim' },
			{ key: 'pet', label: 'Potential ET', type: 'file', defaultIfNull: 'null' },
			{ key: 'atmo_dep', label: 'Atmo. dep.' },
			{ key: 'lat', label: 'Lat', type: 'number', class: 'text-right' },
			{ key: 'lon', label: 'Lon', type: 'number', class: 'text-right' }
		],
		total: 0
	};

	let page:any = reactive({
		loading: false,
		error: <string|null>null,
		import: {
			form: {
				deleteExisting: false,
				matchExisting: false,
				weatherDataDir: <string|null>null,
				saveDir: <string|null>null,
				format: 'SWAT2012'
			},
			options: {
				formats: [
					{ value: 'SWAT2012', title: 'SWAT2012 / Global Data Websites' },
					{ value: 'SWAT+', title: 'SWAT+' }
				]
			},
			show: false,
			error: <string|null>null,
			saving: false
		},
		delete: {
			show: false,
			error: <string|null>null,
			saving: false
		}
	});

	let task:any = reactive({
		progress: {
			percent: 0,
			message: <string|null>null
		},
		error: <string|null>null,
		running: false,
		currentPid: null
	});

	const formRules = computed(() => ({
		format: { required },
		weatherDataDir: { required },
		saveDir: {
			required: helpers.withMessage('Value is required', requiredIf(() => { return page.import.form.format === 'SWAT2012' }))
		},
		matchExisting: {},
		deleteExisting: {}
	}));
	const v$ = useVuelidate(formRules, page.import.form);

	function getTableTotal(total:any) {
		table.total = total;
	}

	async function get() {
		page.loading = true;
		page.error = null;

		try {
			const response = await api.get(`climate/directory`, currentProject.getApiHeader());
			errors.log(response.data);
			
			page.import.form.weatherDataDir = response.data.weather_data_dir;

			if (formatters.isNullOrEmpty(page.import.form.saveDir)) {
				page.import.form.saveDir = currentProject.txtInOutPath;
			}

			if (formatters.isNullOrEmpty(page.import.form.weatherDataDir)) {
				page.import.form.weatherDataDir = currentProject.txtInOutPath;
			}

			for(let i = 0; i < table.headers.length; i++) {
				table.headers[i].filePath = page.import.form.weatherDataDir;
			}
		} catch (error) {
			page.error = errors.logError(error, 'Unable to get project information from database.');
		}
		
		page.loading = false;
	}

	async function confirmDelete() {
		page.delete.errors = [];
		page.delete.saving = true;

		try {
			const response = await api.delete(`climate/stations`, currentProject.getApiHeader());
			errors.log(response);
			page.delete.show = false;
			await grid?.value?.get();
		} catch (error) {
			page.delete.error = errors.logError(error, 'Unable to delete from database.');
		}

		page.delete.saving = false;
	}

	async function importData() {
		page.import.error = null;
		page.import.saving = true;
		errors.log(page.import.form);

		const valid = await v$.value.$validate();
		if (!valid) {
			page.import.error = 'Please enter a value for all fields below and try again.';
		} else {
			try {
				let data = {
					weather_data_dir: page.import.form.format === 'SWAT+' ? page.import.form.weatherDataDir : page.import.form.saveDir
				};
				const response = await api.put(`climate/directory`, data, currentProject.getApiHeader());
				errors.log(response);
			} catch (error) {
				page.import.error = errors.logError(error, 'Error saving weather directory to database.');
			}

			if (formatters.isNullOrEmpty(page.import.error)) {
				let deleteExisting = page.import.form.deleteExisting ? 'y' : 'n';
				let createStations = page.import.form.matchExisting ? 'n' : 'y';
				let importType = page.import.form.format === 'SWAT2012' ? 'observed2012' : 'observed';

				let args = ['import_weather', 
					'--project_db_file='+ currentProject.projectDb,
					'--delete_existing='+ deleteExisting,
					'--import_type=' + importType,
					'--create_stations='+ createStations];

				if (page.import.form.format != 'SWAT+') {
					args.push('--source_dir='+ page.import.form.weatherDataDir);
				}

				errors.log(args);

				v$.value.$reset();
				page.import.saving = false;
				runTask(args);
			}
		}

		page.import.saving = false;
	}

	function runTask(args:string[]) {
		task.error = null;
		task.running = true;
		task.progress = {
			percent: 0,
			message: null
		};

		task.isGridTask = true;
		task.currentPid = runProcess.runApiProc('weather_stations', 'swatplus_api', args);
	}

	let listeners:any = {
		stdout: undefined,
		stderr: undefined,
		close: undefined
	}

	function initRunProcessHandlers() {
		listeners.stdout = runProcess.processStdout('weather_stations', (data:any) => {
			console.log(`stdout: ${data}`);
			task.progress = runProcess.getApiOutput(data);
		});
		
		listeners.stderr = runProcess.processStderr('weather_stations', (data:any) => {
			console.log(`stderr: ${data}`);
			task.error = data;
			task.running = false;
		});
		
		listeners.close = runProcess.processClose('weather_stations', async (code:any) => {
			console.log(`close: ${code}`);
			if (formatters.isNullOrEmpty(task.error)) {
				await grid?.value?.get();
				task.running = false;
				closeTaskModals();
			}
		});
	}

	function removeRunProcessHandlers() {
		if (listeners.stdout) listeners.stdout();
		if (listeners.stderr) listeners.stderr();
		if (listeners.close) listeners.close();
	}

	function cancelTask() {
		task.error = null;
		runProcess.killProcess(task.currentPid);
		
		task.running = false;
		closeTaskModals();
	}

	function closeTaskModals() {
		page.import.show = false;
	}

	onMounted(async () => {
		page.loading = true;
		initRunProcessHandlers();
		await get();
		page.loading = false;
	});
	
	onUnmounted(() => removeRunProcessHandlers());

	watch(() => route.path, async () => await get())
</script>

<template>
	<project-container :loading="page.loading" :load-error="page.error">
		<div v-if="route.name === 'Stations'">
			<file-header input-file="weather-sta.cli" docs-path="climate">
				Weather Stations
			</file-header>

			<grid-view ref="grid" :api-url="table.apiUrl" :headers="table.headers" @change="getTableTotal">
				<template #actions>
					<v-btn variant="flat" color="info" class="mr-2" @click="page.import.show = true">Import Data</v-btn>
					<v-btn v-if="table.total > 0" variant="flat" color="error" class="mr-2" @click="page.delete.show = true">Delete All</v-btn>
				</template>
			</grid-view>

			<v-dialog v-model="page.delete.show" :max-width="constants.dialogSizes.md">
				<v-card title="Confirm delete">
					<v-card-text>
						<error-alert :text="page.delete.error"></error-alert>

						<p>
							Are you sure you want to delete <strong>ALL</strong> weather stations?
							This action is permanent and cannot be undone. 
						</p>
					</v-card-text>
					<v-divider></v-divider>
					<v-card-actions>
						<v-btn @click="confirmDelete" :loading="page.delete.saving" color="error" variant="text">Delete All</v-btn>
						<v-btn @click="page.delete.show = false">Cancel</v-btn>
					</v-card-actions>
				</v-card>
			</v-dialog>

			<v-dialog v-model="page.import.show" :max-width="constants.dialogSizes.lg" persistent>
				<v-card title="Import Weather Stations">
					<v-card-text>
						<error-alert :text="page.import.error"></error-alert>
						<stack-trace-error v-if="!formatters.isNullOrEmpty(task.error)" error-title="There was an error importing your data." :stack-trace="task.error.toString()" />
						
						<div v-if="task.running">
							<v-progress-linear :model-value="task.progress.percent" color="primary" height="15" striped indeterminate></v-progress-linear>
							<p>
								{{task.progress.message}}
							</p>
						</div>
						<div v-else-if="formatters.isNullOrEmpty(task.error)">
							<v-alert type="info" icon="$info" variant="tonal" border="start" class="mb-4">
								Need weather data? 
								<open-in-browser url="https://swat.tamu.edu/data/" text="See options on the SWAT website."></open-in-browser>
								<br>Have <b>hourly</b> data? This is only supported in SWAT+ format, not SWAT2012.
							</v-alert>
							
							<div class="form-group mb-0">
								<v-select label="Select your data format" v-model="page.import.form.format" 
									:items="page.import.options.formats" 
									:error-messages="v$.format.$errors.map(e => e.$message).join(', ')"
									@input="v$.format.$touch" @blur="v$.format.$touch"></v-select>
							</div>

							<v-alert type="info" icon="$info" variant="tonal" border="start" class="mb-4">
								<span v-if="page.import.form.format === 'SWAT2012'">
									Each measurement provided must have a file named as: <code>pcp.txt</code>, <code>rh.txt</code>, <code>solar.txt</code>, 
									<code>tmp.txt</code>, <code>wind.txt</code>, and <code>pet.txt</code>. 
									<open-in-browser url="https://plus.swat.tamu.edu/downloads/sample_files/weather-stations/swat2012-weather-stations.zip" text="Download a sample format"></open-in-browser>
									and 
									<open-in-browser url="https://swatplus.gitbook.io/docs/user/editor/inputs/climate#swat2012-global-weather-websites-format" text="read the instructions"></open-in-browser>.
								</span>
								<span v-else>
									Each measurement provided must have a file named as: <code>pcp.cli</code>, <code>hmd.cli</code>, <code>slr.cli</code>, 
									<code>tmp.cli</code>, <code>wnd.cli</code>, and <code>pet.cli</code>.
									<open-in-browser url="https://plus.swat.tamu.edu/downloads/sample_files/weather-stations/swatplus-weather-stations.zip" text="Download a sample format"></open-in-browser>
									and 
									<open-in-browser url="https://swatplus.gitbook.io/docs/user/editor/inputs/climate#swat+-format" text="read the instructions"></open-in-browser>.
								</span>

								Please ensure the files you're importing are saved with UTF-8 encoding. Replace any accent or non-unicode characters in the station names or comment lines of all files.
							</v-alert>

							<div class="form-group mb-0">
								<select-folder-input v-model="page.import.form.weatherDataDir" :value="page.import.form.weatherDataDir"
									:label="page.import.form.format + ' weather files directory'" required
									invalidFeedback="Required"></select-folder-input>
							</div>

							<div class="form-group mb-0" v-if="page.import.form.format !== 'SWAT+'">
								<select-folder-input v-model="page.import.form.saveDir" :value="page.import.form.saveDir"
								label="Directory to save your SWAT+ weather files" :required="page.import.form.format !== 'SWAT+'"
									invalidFeedback="Required"></select-folder-input>
							</div>

							<div v-if="table.total > 0">
								<v-checkbox v-model="page.import.form.deleteExisting" hide-details>
									<template #label>
										Delete existing stations? Leave unchecked to keep. 
									</template>
								</v-checkbox>

								<v-checkbox v-model="page.import.form.matchExisting" hide-details>
									<template #label>
										Match files to existing stations? Leave unchecked to create new weather stations.
									</template>
								</v-checkbox>
							</div>							
						</div>
					</v-card-text>
					<v-divider></v-divider>
					<v-card-actions>
						<v-btn v-if="formatters.isNullOrEmpty(task.error)" :loading="task.running || page.import.saving" @click="importData" color="primary" variant="text">Import Data</v-btn>
						<v-btn @click="cancelTask">Cancel</v-btn>
					</v-card-actions>
				</v-card>
			</v-dialog>
		</div>
		<router-view></router-view>
	</project-container>
</template>