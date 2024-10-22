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
		apiUrl: 'climate/wgn',
		headers: [
			{ key: 'name', label: 'Name' },
			{ key: 'lat', label: 'Lat', type: 'number', class: 'text-right' },
			{ key: 'lon', label: 'Lon', type: 'number', class: 'text-right' },
			{ key: 'elev', label: 'Elev (m)', type: 'number', class: 'text-right' },
			{ key: 'rain_yrs', label: 'Rain years', type: 'number', class: 'text-right' }
		],
		total: 0
	};

	let page:any = reactive({
		loading: false,
		error: <string|null>null,
		import: {
			defaults: {
				db: 'C:/SWAT/SWATPlus/Databases/swatplus_wgn.sqlite',
				table: 'wgn_cfsr_world'
			},
			form: {
				method: 'database',
				csvFile1: <string|null>null,
				csvFile2: <string|null>null,
				db: <string|null>null,
				table: <string|null>null,
				useObserved: false,
				deleteExisting: true
			},
			options: {
				methods: [
					{ title: 'Database', value: 'database' },
					{ title: 'Two CSV files (separate file for stations and monthly values)', value: 'two_file' },
					{ title: 'One CSV file', value: 'one_file' }
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
		},
		validate: {
			is_invalid: false,
			data: <any[]>[],
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
		method: { required },
		csvFile1: {
			required: helpers.withMessage('Value is required', requiredIf(() => { return page.import.form.method === 'two_file' || page.import.form.method === 'one_file' }))
		},
		csvFile2: {
			required: helpers.withMessage('Value is required', requiredIf(() => { return page.import.form.method === 'two_file' }))
		},
		db: {
			required: helpers.withMessage('Value is required', requiredIf(() => { return page.import.form.method === 'database' }))
		},
		table: {
			required: helpers.withMessage('Value is required', requiredIf(() => { return page.import.form.method === 'database' }))
		},
		useObserved: {},
		deleteExisting: {}
	}));
	const v$ = useVuelidate(formRules, page.import.form);

	async function getTableTotal(total:any) {
		table.total = total;
		await validateStations();
	}

	async function get() {
		page.loading = true;
		page.error = null;

		try {
			const response = await api.get(`climate/wgn/db`, currentProject.getApiHeader());
			errors.log(response.data);
			
			let defaultDb = utilities.getDatabaseInstallPath('swatplus_wgn.sqlite');
			errors.log(defaultDb);
			let defaultTable = formatters.isNullOrEmpty(defaultDb) ? null : page.import.defaults.table

			page.import.form.db = formatters.toValue(response.data.wgn_db, defaultDb);
			page.import.form.table = formatters.toValue(response.data.wgn_table_name, defaultTable);

			await validateStations();
		} catch (error) {
			page.error = errors.logError(error, 'Unable to get project information from database.');
		}
		
		page.loading = false;
	}

	async function validateStations() {
		page.validate.loading = true;
		page.validate.error = null;

		try {
			const response = await api.get(`climate/wgn/validate`, currentProject.getApiHeader());
			errors.log(response.data);
			page.validate.is_invalid = response.data.is_invalid;
			page.validate.data = response.data.data;
		} catch (error) {
			page.validate.error = errors.logError(error, 'Unable to get project information from database.');
		}
		
		page.validate.loading = false;
	}

	async function confirmDelete() {
		page.delete.errors = [];
		page.delete.saving = true;

		try {
			const response = await api.delete(`climate/wgn`, currentProject.getApiHeader());
			errors.log(response);
			page.delete.show = false;
			await grid?.value?.get();
			await validateStations();
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
			if (page.import.form.method === 'database') {
				try {
					let data = {
						wgn_db: page.import.form.db,
						wgn_table_name: page.import.form.table
					};
					const response = await api.put(`climate/wgn/db`, data, currentProject.getApiHeader());
					errors.log(response);
				} catch (error) {
					page.import.error = errors.logError(error, 'Error saving wgn database and table parameters.');
				}
			}

			if (formatters.isNullOrEmpty(page.import.error)) {
				let deleteExisting = page.import.form.deleteExisting ? 'y' : 'n';
				let createStations = page.import.form.useObserved ? 'n' : 'y';

				let args = ['import_weather', 
					'--project_db_file='+ currentProject.projectDb,
					'--delete_existing='+ deleteExisting,
					'--import_type=wgn',
					'--create_stations='+ createStations,
					'--import_method='+ page.import.form.method,
					'--file1='+ page.import.form.csvFile1,
					'--file2='+ page.import.form.csvFile2];
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
		task.currentPid = runProcess.runApiProc('wgn', 'swatplus_api', args);
	}

	let listeners:any = {
		stdout: undefined,
		stderr: undefined,
		close: undefined
	}

	function initRunProcessHandlers() {
		listeners.stdout = runProcess.processStdout('wgn', (data:any) => {
			console.log(`stdout: ${data}`);
			task.progress = runProcess.getApiOutput(data);
		});
		
		listeners.stderr = runProcess.processStderr('wgn', (data:any) => {
			console.log(`stderr: ${data}`);
			task.error = data;
			task.running = false;
		});
		
		listeners.close = runProcess.processClose('wgn', async (code:any) => {
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
		<div v-if="route.name === 'Wgn'">
			<file-header input-file="weather-wgn.cli" docs-path="climate">
				Weather Generator
			</file-header>

			<error-alert :text="page.validate.error"></error-alert>
			<page-loading :loading="page.validate.loading"></page-loading>
			<v-alert v-if="!page.validate.loading && page.validate.is_invalid" type="warning" icon="$warning" variant="tonal" border="start" class="mb-4">
				<p>
					You have weather generators in your model that do not have corresponding monthly values. 
					Non-zero monthly values for each statistic are required for SWAT+ to run. 
					Please use the import function with the SWAT+ WGN database if you are unsure, or refer to the SWAT+ documentation.
					Stations with missing data are listed below.
				</p>
				<ul>
					<li v-for="station in page.validate.data">
						Station <router-link class="text-warning" :to="`/edit/climate/wgn/edit/${station.id}`">{{ station.name }}</router-link> has <b>{{ station.months }}</b> months of data; 12 are required.
					</li>
				</ul>
			</v-alert>

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
							Are you sure you want to delete <strong>ALL</strong> weather generators?
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
				<v-card title="Import Weather Generator Data">
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
							<div class="form-group mb-0">
								<v-select label="Select your data format" v-model="page.import.form.method" 
									:items="page.import.options.methods" 
									:error-messages="v$.method.$errors.map(e => e.$message).join(', ')"
									@input="v$.method.$touch" @blur="v$.method.$touch"></v-select>
							</div>

							<div v-if="page.import.form.method === 'database'">
								<v-alert type="info" icon="$info" variant="tonal" border="start" class="mb-4" v-if="formatters.isNullOrEmpty(page.import.form.db)">
									Need wgn data? 
									<open-in-browser url="https://plus.swat.tamu.edu/downloads/swatplus_wgn.zip" text="Download the global SWAT+ wgn database (180MB)."></open-in-browser>
								</v-alert>

								<div class="form-group mb-0">
									<select-file-input v-model="page.import.form.db" :value="page.import.form.db"
										label="Database file"
										fileType="sqlite" :required="page.import.form.method === 'database'" 
										invalidFeedback="Please select a SQLite database file"></select-file-input>
								</div>

								<div class="form-group mb-0">
									<v-text-field v-model="page.import.form.table"
										label="Table name in database"
										:error-messages="v$.table.$errors.map(e => e.$message).join(', ')"
										@input="v$.table.$touch" @blur="v$.table.$touch"></v-text-field>
								</div>
							</div>
							<div v-else-if="page.import.form.method === 'two_file'">
								<v-alert type="info" icon="$info" variant="tonal" border="start" class="mb-4">
									<div>
										Two CSV files are required. Please ensure the files you're importing are saved with UTF-8 encoding. 
										<open-in-browser url="https://plus.swat.tamu.edu/downloads/sample_files/wgn/swatplus_tf_wgn_template.zip" text="Download a template."></open-in-browser>
									</div>
									<ol class="mb-0">
										<li>
											Stations CSV file:
											<ul>
												<li>Columns <code>id, name, lat, lon, elev, rain_yrs</code></li>
												<li><code>id</code> should be uniquely numbered</li>
											</ul>
										</li>
										<li>
											Monthly values CSV file:
											<ul>
												<li>Columns <code>id, wgn_id, month, tmp_max_ave, tmp_min_ave, tmp_max_sd, tmp_min_sd, pcp_ave, pcp_sd, pcp_skew, wet_dry, wet_wet, pcp_days, pcp_hhr, slr_ave, dew_ave, wnd_ave</code></li>
												<li><code>id</code> should be uniquely numbered</li>
												<li><code>wgn_id</code> corresponds to the <code>id</code> column from the stations file</li>
											</ul>
										</li>
									</ol>
								</v-alert>

								<div class="form-group mb-0">
									<select-file-input v-model="page.import.form.csvFile1" :value="page.import.form.csvFile1"
										label="Stations CSV file"
										fileType="csv" :required="page.import.form.method === 'two_file'" 
										invalidFeedback="Please select a CSV file"></select-file-input>
								</div>

								<div class="form-group mb-0">
									<select-file-input v-model="page.import.form.csvFile2" :value="page.import.form.csvFile2"
										label="Monthly values CSV file"
										fileType="csv" :required="page.import.form.method === 'two_file'" 
										invalidFeedback="Please select a CSV file"></select-file-input>
								</div>
							</div>
							<div v-else-if="page.import.form.method === 'one_file'">
								<v-alert type="info" icon="$info" variant="tonal" border="start" class="mb-4">
									One CSV file is required. One station per row; all 12 months of data are in a single row. Please ensure the files you're importing are saved with UTF-8 encoding. 
									<open-in-browser url="https://plus.swat.tamu.edu/downloads/sample_files/wgn/swatplus_sf_wgn_template.csv" text="Download a template."></open-in-browser>
								</v-alert>

								<div class="form-group mb-0">
									<select-file-input v-model="page.import.form.csvFile1" :value="page.import.form.csvFile1"
										label="CSV file"
										fileType="csv" :required="page.import.form.method === 'one_file'" 
										invalidFeedback="Please select a CSV file"></select-file-input>
								</div>
							</div>

							<v-checkbox v-model="page.import.form.deleteExisting" v-if="table.total > 0" hide-details>
								<template #label>
									Delete existing weather generators? 
								</template>
							</v-checkbox>

							<v-checkbox v-model="page.import.form.useObserved" hide-details>
								<template #label>
									Check if you are using observed weather data
								</template>
							</v-checkbox>
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