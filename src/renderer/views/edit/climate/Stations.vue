<script setup lang="ts">
	import { reactive, ref, onMounted, onUnmounted, computed, watch } from 'vue';
	import { useVuelidate } from '@vuelidate/core';
	import { required, requiredIf, helpers } from '@vuelidate/validators';
	import { useRoute } from 'vue-router';
	import { useHelpers } from '@/helpers';
	import { storeToRefs } from 'pinia';
	import {useTaskStore} from '@/store/task';

	
	const route = useRoute();
	const { api, constants, currentProject, errors, formatters, runProcess, utilities } = useHelpers();
	const taskStore = useTaskStore();
	const { task } = storeToRefs(taskStore);



	interface GridComponent {
		get: () => Promise<void>;
	}
	const grid = ref<GridComponent | null>(null);

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
					{ value: 'SWAT+', title: 'SWAT+' },
					{ value: 'CSV', title: 'CSV Files (Advanced, requires specific formatting)' }
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

	const formRules = computed(() => ({
		format: { required },
		weatherDataDir: { required },
		saveDir: {
			required: helpers.withMessage('Value is required', requiredIf(() => { return page.import.form.format === 'SWAT2012' || page.import.form.format === 'CSV' }))
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

	function openImportDialog() {
		taskStore.task.error = null;
		taskStore.task.running = false;
		taskStore.task.progress = { percent: 0, message: '' };
		
		page.import.error = null;
		page.import.saving = false;
		page.import.show = true; // Buka modal di sini
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
				// let importType = page.import.form.format === 'SWAT2012' ? 'observed2012' : 'observed';

				let importType = 'observed';
				if (page.import.form.format === 'SWAT2012') importType = 'observed2012';
				else if (page.import.form.format === 'CSV') importType = 'csv';

				let args = ['import_weather', 
					'--project_db_file='+ currentProject.projectDb,
					'--delete_existing='+ deleteExisting,
					'--import_type=' + importType,
					'--create_stations='+ createStations];

				// if (page.import.form.format != 'SWAT+') {
				// 	args.push('--source_dir='+ page.import.form.weatherDataDir);
				// }

				if (page.import.form.format === 'CSV') {
					if (!page.import.form.saveDir) {
						page.import.form.saveDir = currentProject.txtInOutPath; // Ambil path default proyek
					}
				// Sesuai dengan parser baru di swatplus_api.py
					args.push('--csv_dir=' + page.import.form.weatherDataDir);
					args.push('--weather_output_dir=' + page.import.form.saveDir);
				} else if (page.import.form.format !== 'SWAT+') {
					args.push('--source_dir='+ page.import.form.weatherDataDir);
				}

				errors.log(args);
				v$.value.$reset();
				taskStore.runTask(args, {
					proc_name: 'weather_stations', // Sesuaikan dengan nama proses di listener Anda
					script_name: 'swatplus_api',
					// type: 'import',
					isGridTask : true,
					type: 'import',
					routePath: route.path
					}, 
					async () => {
					// --- LOGIKA SETELAH IMPORT SELESAI ---
					taskStore.task.running = false;
					page.import.saving = false;
                	closeTaskModals();
					// await grid?.value?.get();
					if (grid.value) {
        				await grid.value.get();
    				}
                // Opsional: panggil get() untuk refresh data
            });
			} else {
				page.import.saving = false;
			}
    	}
	}


	function cancelTask() {
		taskStore.cancelTask();
		closeTaskModals();
	}

	function closeTaskModals() {
		page.import.show = false;
	}

	onMounted(async () => {
		page.loading = true;
		// initRunProcessHandlers();
		await get();
		page.loading = false;
	});

	onUnmounted(() => {
		taskStore.cleanupListeners();// removeRunProcessHandlers();
	});


	watch(() => route.path, async () => await get())
</script>

<template>
	<project-container :loading="page.loading" :load-error="page.error">
		<div v-if="route.name === 'Stations'">
			<file-header input-file="weather-sta.cli" docs-path="climate">
				Weather Stations
			</file-header>

			<grid-view ref="grid" :api-url="table.apiUrl" :headers="table.headers" @change="getTableTotal" hide-create>
				<template #actions>
					<v-btn variant="flat" color="info" class="mr-2" @click="openImportDialog">Import Data</v-btn>
					<v-btn v-if="table.total > 0" variant="flat" color="error" class="mr-2" @click="page.delete.show = true">Delete All</v-btn>
				</template>
			</grid-view>

			<v-dialog v-model="page.delete.show" :max-width="constants.dialogSizes.md">
				<v-card title="Confirm delete">
					<v-card-text>
						<error-alert :text="page.delete.error"></error-alert>

						<p>
							Yakin akan menghapus data <strong>ALL</strong> weather stations?
							Tindakan ini bersifat permanen dan tidak dapat dibatalkan. 
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
						<stack-trace-error v-if="!formatters.isNullOrEmpty(task.error)" error-title="There was an error importing your data." :stack-trace="task.error ? task.error.toString() : ''" />
						
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
								<br>Have <b>hourly</b> data? Ini hanya didukung dalam format SWAT+, bukan SWAT2012.
							</v-alert>
							
							<div class="form-group mb-0">
								<v-select label="Select your data format" v-model="page.import.form.format" 
									:items="page.import.options.formats" 
									:error-messages="v$.format.$errors.map(e => e.$message).join(', ')"
									@input="v$.format.$touch" @blur="v$.format.$touch"></v-select>
							</div>

							<v-alert type="info" icon="$info" variant="tonal" border="start" class="mb-4">
								<span v-if="page.import.form.format === 'SWAT2012'">
									Setiap pengukuran yang diberikan harus memiliki file bernama sebagai: <code>pcp.txt</code>, <code>rh.txt</code>, <code>solar.txt</code>, 
									<code>tmp.txt</code>, <code>wind.txt</code>, and <code>pet.txt</code>. 
									<open-in-browser url="https://plus.swat.tamu.edu/downloads/sample_files/weather-stations/swat2012-weather-stations.zip" text="Download a sample format"></open-in-browser>
									and 
									<open-in-browser url="https://swatplus.gitbook.io/docs/user/editor/inputs/climate#swat2012-global-weather-websites-format" text="read the instructions"></open-in-browser>.
								</span>
								<!-- CSV Format Instructions -->
								<span v-else-if="page.import.form.format === 'CSV'">
									Pastikan file CSV Anda memiliki header yang sesuai dengan format database... 
									(tulis instruksi singkat CSV Anda di sini)
								</span>
								<span v-else>
									Setiap pengukuran yang diberikan harus memiliki file bernama sebagai: <code>pcp.cli</code>, <code>hmd.cli</code>, <code>slr.cli</code>, 
									<code>tmp.cli</code>, <code>wnd.cli</code>, and <code>pet.cli</code>.
									<open-in-browser url="https://plus.swat.tamu.edu/downloads/sample_files/weather-stations/swatplus-weather-stations.zip" text="Download a sample format"></open-in-browser>
									and 
									<open-in-browser url="https://swatplus.gitbook.io/docs/user/editor/inputs/climate#swat+-format" text="read the instructions"></open-in-browser>.
								</span>

								Pastikan file yang Anda impor disimpan dengan pengkodean UTF-8. Ganti semua karakter beraksen atau karakter non-Unicode dalam nama stasiun atau baris komentar di semua file.
							</v-alert>

							<!-- <div class="form-group mb-0">
								<select-folder-input v-model="page.import.form.weatherDataDir" :value="page.import.form.weatherDataDir"
									:label="page.import.form.format + ' weather files directory'" required
									invalidFeedback="Required"></select-folder-input>
							</div> -->
							<!-- CSV Format Instructions -->
							<div class="form-group mb-0">
								<select-folder-input 
									v-model="page.import.form.weatherDataDir" 
									:value="page.import.form.weatherDataDir"
									:label="page.import.form.format === 'CSV' ? 'CSV weather files directory' : page.import.form.format + ' weather files directory'" 
									required
									invalidFeedback="Required">
								</select-folder-input>
							</div>

							<div class="form-group mb-0" v-if="page.import.form.format !== 'SWAT+'">
								<select-folder-input v-model="page.import.form.saveDir" :value="page.import.form.saveDir"
								label="Directory to save your SWAT+ weather files" :required="page.import.form.format !== 'SWAT+'"
									invalidFeedback="Required"></select-folder-input>
							</div>

							<div v-if="table.total > 0">
								<v-checkbox v-model="page.import.form.deleteExisting" hide-details>
									<template #label>
										Hapus stasiun yang sudah ada? Biarkan tidak dicentang untuk mempertahankannya. 
									</template>
								</v-checkbox>

								<v-checkbox v-model="page.import.form.matchExisting" hide-details>
									<template #label>
										Cocokkan berkas dengan stasiun yang sudah ada? Biarkan tidak dicentang untuk membuat stasiun cuaca baru.
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