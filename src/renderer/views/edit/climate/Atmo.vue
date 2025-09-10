<script setup lang="ts">
	import { reactive, ref, onMounted, onUnmounted, computed, watch } from 'vue';
	import { useVuelidate } from '@vuelidate/core';
	import { required, requiredIf, helpers } from '@vuelidate/validators';
	import { useRoute } from 'vue-router';
	import { useHelpers } from '@/helpers';
	const electron = window.electronApi;
	const route = useRoute();
	const { api, constants, currentProject, errors, formatters, runProcess, utilities } = useHelpers();

	const grid = ref();

	let table:any = {
		apiUrl: 'climate/atmo/stations',
		headers: [
			{ key: 'name', label: 'Name' }
		],
		total: 0
	};

	let page:any = reactive({
		loading: false,
		error: <string|null>null,
		import: {
			form: {
				importMethod: 'csv',
				file1: <string|null>null,
				file2: <string|null>null
			},
			options: {
				importMethod: [
					{ title: 'CSV file', value: 'csv' },
					{ title: 'Existing SWAT+ atmo.cli file', value: 'cli' },
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
		exported: {
			show: false,
			fileName: <string|null>null
		},
		form: {
			error: <string|null>null,
			saving: false,
			saveSuccess: false
		},
		data: {
			timestep: 'aa',
			mo_init: 0,
			yr_init: 0,
			num_aa: 0,
			has_weather_stations: false,
			has_atmo_stations: false,
			sim_yr_init: 0,
			sim_num_yrs: 0
		},
		dataOptions: {
			timestep: [
				{ title: 'Average Annual', value: 'aa' },
				{ title: 'Yearly', value: 'yr' },
				{ title: 'Monthly', value: 'mo' }
			]
		}
	});

	let task:any = reactive({
		type: 'import',
		progress: {
			percent: 0,
			message: <string|null>null
		},
		error: <string|null>null,
		running: false,
		currentPid: null
	});

	const formRules = computed(() => ({
		importMethod: { required },
		file1: { required },
		file2: { required }
	}));
	const v$ = useVuelidate(formRules, page.import.form);

	const dataRules = computed(() => ({
		timestep: { required },
		mo_init: { required: helpers.withMessage('Value is required', requiredIf(() => { return page.data.timestep === 'mo'; })) },
		yr_init: { required: helpers.withMessage('Value is required', requiredIf(() => { return page.data.timestep !== 'aa'; })) },
		num_aa: { required: helpers.withMessage('Value is required', requiredIf(() => { return page.data.timestep !== 'aa'; })) }
	}));
	const vd$ = useVuelidate(dataRules, page.data);

	const selectedFileExt = computed(() => {
		return page.import.form.importMethod === 'csv' ? 'csv' : 'txt';
	})

	function getTableTotal(total:any) {
		table.total = total;
	}

	async function get() {
		if (route.name !== 'StationsAtmo') return;
		page.loading = true;
		page.error = null;

		try {
			const response = await api.get(`climate/atmo`, currentProject.getApiHeader());
			errors.log(response.data);
			utilities.assignReactiveObject(page.data, response.data);
		} catch (error) {
			page.error = errors.logError(error, 'Unable to get project information from database.');
		}
		
		page.loading = false;
	}

	function changeTimestep() {
		switch (page.data.timestep) {
			case 'aa':
				page.data.mo_init = 0;
				page.data.yr_init = 0;
				page.data.num_aa = 0;
				break;
			case 'yr':
				page.data.mo_init = 0;
				page.data.yr_init = page.data.sim_yr_init;
				page.data.num_aa = page.data.sim_num_yrs;
				break;
			case 'mo':
				page.data.mo_init = 1;
				page.data.yr_init = page.data.sim_yr_init;
				page.data.num_aa = page.data.sim_num_yrs * 12;
				break;
		}
	}

	async function saveSettings() {
		page.form.saving = true;
		page.form.error = null;
		page.form.saveSuccess = false;

		const valid = await vd$.value.$validate();
		errors.log(vd$.value)
		errors.log(page.data);
		if (!valid) {
			page.form.error = 'Please fix the errors below and try again.';
		} else {
			try {
				let data = {
					filename: 'atmo.cli',
					timestep: page.data.timestep,
					mo_init: page.data.mo_init,
					yr_init: page.data.yr_init,
					num_aa: page.data.num_aa
				}
				const response = await api.put(`climate/atmo`, data, currentProject.getApiHeader());
				errors.log(response.data);			
				vd$.value.$reset();
				page.form.saveSuccess = true;
			} catch (error) {
				page.error = errors.logError(error, 'Unable to get project information from database.');
			}
		}
		
		page.loading = false;
	}

	async function confirmDelete() {
		page.delete.errors = [];
		page.delete.saving = true;

		try {
			const response = await api.delete(`climate/atmo`, currentProject.getApiHeader());
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
		task.type = 'import';

		const valid = await v$.value.$validate();
		if (!valid) {
			page.import.error = 'Please enter a value for all fields below and try again.';
		} else {
			if (formatters.isNullOrEmpty(page.import.error)) {
				let args = ['import_weather', 
					'--project_db_file='+ currentProject.projectDb,
					'--delete_existing=y',
					'--import_type=atmo',
					'--import_method='+ page.import.form.importMethod,
					'--file1='+ page.import.form.file1,
					'--file2='+ page.import.form.file2];

				errors.log(args);

				v$.value.$reset();
				page.import.saving = false;
				runTask(args);
			}
		}

		page.import.saving = false;
	}

	function exportStationsTemplate() {
		let filters = [{ name: 'CSV (Comma delimited)', extensions: ['csv'] }];
		let files = electron.saveFileDialog({filters: filters, defaultPath: 'atmo-weather-station-map.csv'});

		if (files !== undefined) {
			page.exported.fileName = files;
			let args = ['export_csv', 
				'--db_file='+ currentProject.projectDb,
				'--file_name='+ files,
				'--table_name=atmo_map'];

			task.type = 'export';
			runTask(args);
		}
	}

	function runTask(args:string[]) {
		task.error = null;
		task.running = true;
		task.progress = {
			percent: 0,
			message: null
		};

		task.isGridTask = true;
		task.currentPid = runProcess.runApiProc('atmo', 'swatplus_api', args);
	}

	let listeners:any = {
		stdout: undefined,
		stderr: undefined,
		close: undefined
	}

	function initRunProcessHandlers() {
		listeners.stdout = runProcess.processStdout('atmo', (data:any) => {
			console.log(`stdout: ${data}`);
			task.progress = runProcess.getApiOutput(data);
		});
		
		listeners.stderr = runProcess.processStderr('atmo', (data:any) => {
			console.log(`stderr: ${data}`);
			task.error = data;
			task.running = false;
		});
		
		listeners.close = runProcess.processClose('atmo', async (code:any) => {
			console.log(`close: ${code}`);
			if (formatters.isNullOrEmpty(task.error)) {
				if (task.type === 'import') {
					await get();
					await grid?.value?.get();
					task.running = false;
					closeTaskModals();
				} else {
					task.running = false;
					page.exported.show = true;
				}
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
		<div v-if="route.name === 'StationsAtmo'">
			<file-header input-file="atmo.cli" docs-path="climate/atmo.cli" use-io>
				<router-link to="/edit/climate/stations">Weather Stations</router-link>
				/ Atmospheric Deposition
			</file-header>

			<v-alert v-if="!page.data.has_weather_stations" type="info" icon="$info" variant="tonal" border="start" class="mb-4">
				You must add weather stations before atmospheric deposition.
			</v-alert>
			<div v-else>
				<p>
					Configure atmospheric deposition data below.
					The simplest method is to click the <strong>Import Data</strong> button at the bottom of the screen.
					Otherwise use the form below, making sure each station data and timestep created match the selected settings.
					If using monthly or yearly data, be sure the dates fall within your model simulation dates.
				</p>

				<error-alert :text="page.form.error"></error-alert>
				<success-alert v-model="page.form.saveSuccess"></success-alert>

				<v-form @submit.prevent="saveSettings">
					<v-row>
						<v-col cols="12" md="3">
							<div class="form-group mb-0">
								<v-select label="Timestep" v-model="page.data.timestep" @update:model-value="changeTimestep"
									:items="page.dataOptions.timestep" 
									:error-messages="vd$.timestep.$errors.map(e => e.$message).join(', ')"
									@input="vd$.timestep.$touch" @blur="vd$.timestep.$touch"></v-select>
							</div>
						</v-col>
						<v-col cols="12" md="3" v-if="page.data.timestep === 'mo'">
							<div class="form-group mb-0">
								<v-text-field v-model.number="page.data.mo_init" 
									label="Start Month" type="number"
									:error-messages="vd$.mo_init.$errors.map(e => e.$message).join(', ')"
									@input="vd$.mo_init.$touch" @blur="vd$.mo_init.$touch"></v-text-field>
							</div>
						</v-col>
						<v-col cols="12" md="3" v-if="page.data.timestep !== 'aa'">
							<div class="form-group mb-0">
								<v-text-field v-model.number="page.data.yr_init" 
									label="Start Year" type="number"
									:error-messages="vd$.yr_init.$errors.map(e => e.$message).join(', ')"
									@input="vd$.yr_init.$touch" @blur="vd$.yr_init.$touch"></v-text-field>
							</div>
						</v-col>
						<v-col cols="12" md="3" v-if="page.data.timestep !== 'aa'">
							<div class="form-group mb-0">
								<v-text-field v-model.number="page.data.num_aa" 
									:label="`Number of ${page.data.timestep === 'mo' ? 'Months' : 'Years'}`" type="number"
									:error-messages="vd$.num_aa.$errors.map(e => e.$message).join(', ')"
									@input="vd$.num_aa.$touch" @blur="vd$.num_aa.$touch"></v-text-field>
							</div>
						</v-col>
					</v-row>

					<div>
						<v-btn type="submit" :loading="page.saving" variant="flat" color="primary" class="mr-2">
							Update Settings
						</v-btn>
					</div>
				</v-form>

				<v-divider class="mt-6 mb-4"></v-divider>

				<h2 class="text-h5 mb-3">Stations</h2>
				<grid-view ref="grid" :api-url="table.apiUrl" :headers="table.headers" @change="getTableTotal" auto-height>
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
								Are you sure you want to delete <strong>ALL</strong> atmospheric deposition stations?
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
					<v-card title="Import Atmospheric Deposition Data">
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
								<p>
									Any existing atmospheric deposition data will be deleted.
								</p>
								
								<div class="form-group mb-0">
									<v-select label="Select your data format" v-model="page.import.form.importMethod" 
										:items="page.import.options.importMethod" 
										:error-messages="v$.importMethod.$errors.map(e => e.$message).join(', ')"
										@input="v$.importMethod.$touch" @blur="v$.importMethod.$touch"></v-select>
								</div>

								<div class="form-group mb-0 d-flex">
									<select-file-input v-model="page.import.form.file1" :value="page.import.form.file1"
										label="Atmospheric deposition file"
										:fileType="page.import.form.importMethod" required
										invalidFeedback="Please select a file"  class="flex-fill mr-5"></select-file-input>
									<v-menu class="ml-auto">
										<template v-slot:activator="{ props }">
											<v-btn color="info" variant="flat" v-bind="props" class="mt-2">Download Sample File</v-btn>
										</template>
										<v-list>
											<v-list-item><open-in-browser class="text-decoration-none text-high-emphasis" :url="`https://plus.swat.tamu.edu/downloads/sample_files/atmo/atmo_avgannual.${selectedFileExt}`" text="Average Annual"></open-in-browser></v-list-item>
											<v-list-item><open-in-browser class="text-decoration-none text-high-emphasis" :url="`https://plus.swat.tamu.edu/downloads/sample_files/atmo/atmo_yearly.${selectedFileExt}`" text="Yearly"></open-in-browser></v-list-item>
											<v-list-item><open-in-browser class="text-decoration-none text-high-emphasis" :url="`https://plus.swat.tamu.edu/downloads/sample_files/atmo/atmo_monthly.${selectedFileExt}`" text="Monthly"></open-in-browser></v-list-item>
										</v-list>
									</v-menu>
								</div>

								<p>
									Atmospheric deposition stations need to be mapped to your existing weather stations.
									Click the Export Template button to get a CSV containing your weather stations. Fill the first column
									of the CSV with your atmospheric deposition station names.
								</p>
								
								<div class="form-group mb-0 d-flex">
									<select-file-input v-model="page.import.form.file2" :value="page.import.form.file2"
										label="Atmospheric deposition to weather station mapping file"
										fileType="csv" required
										invalidFeedback="Please select a file"  class="flex-fill mr-5"></select-file-input>
									<v-btn color="info" variant="flat" class="ml-auto mt-2" @click="exportStationsTemplate">Export Template File</v-btn>
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

				<v-dialog v-model="page.exported.show" :max-width="constants.dialogSizes.md">
					<v-card title="Data Exported">
						<v-card-text>
							<p>
								Your data has been exported. 
							</p>
							<p>
								<open-file :file-path="page.exported.fileName" text="Open file" button color="primary"></open-file>
							</p>
						</v-card-text>
						<v-divider></v-divider>
						<v-card-actions>
							<v-btn @click="page.exported.show = false">Close</v-btn>
						</v-card-actions>
					</v-card>
				</v-dialog>
			</div>
		</div>
		<router-view></router-view>
	</project-container>
</template>
