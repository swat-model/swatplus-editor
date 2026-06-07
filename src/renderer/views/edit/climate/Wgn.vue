<script setup lang="ts">
	import { reactive, ref, onMounted, onUnmounted, computed, watch } from 'vue';
	import { useVuelidate } from '@vuelidate/core';
	import { required, requiredIf, helpers } from '@vuelidate/validators';
	import { useRoute } from 'vue-router';
	import { useHelpers } from '@/helpers';
	import { storeToRefs } from 'pinia';
	import { useTaskStore } from '@/store/task';

	const route = useRoute();
	const { api, constants, currentProject, errors, formatters, runProcess, utilities } = useHelpers();
	const taskStore = useTaskStore();
	const { task } = storeToRefs(taskStore);

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
				deleteExisting: true,
				deleteExistingStations: false // ✅ Dikembalikan agar sinkron dengan fungsi hapus stasiun lama
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
			saving: false,
			hasObservedOnLoad: false // ✅ Dikembalikan untuk melacak status data awal
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
			page.import.form.useObserved = response.data.has_observed_weather;
			page.import.hasObservedOnLoad = response.data.has_observed_weather; // ✅ Diaktifkan kembali

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
				let deleteExistingStations = page.import.form.deleteExistingStations && page.import.hasObservedOnLoad ? 'y' : 'n'; // ✅ Dikembalikan

				let args = ['import_weather', 
					'--project_db_file='+ currentProject.projectDb,
					'--delete_existing='+ deleteExisting,
					'--import_type=wgn',
					'--create_stations='+ createStations,
					'--import_method='+ page.import.form.method,
					'--file1='+ page.import.form.csvFile1,
					'--file2='+ page.import.form.csvFile2,
					'--delete_existing_stations='+ deleteExistingStations]; // ✅ Dikembalikan agar argumen Python lengkap
				errors.log(args);

				v$.value.$reset();
				
				taskStore.runTask(args, {
					proc_name: 'wgn', 
					script_name: 'swatplus_api',
					isGridTask : true,
					type: 'import', // ✅ Diubah langsung ke string literal 'import' karena page.import.form.type tidak ada
					routePath: route.path
				}, async () => {
					// ✨ REFRESH UI SETELAH SAKRAL SELESAI IMPOR ✨
					taskStore.task.running = false;
					page.import.saving = false;
					closeTaskModals();
					if (grid?.value) {
						await grid.value.get();
					}
					await validateStations();

				});
				// closeTaskModals();
			} else {
				page.import.saving = false;
			}
    	}
	}

	function openImportDialog() {
		taskStore.task.error = null;
		taskStore.task.running = false;
		taskStore.task.progress = { percent: 0, message: '' };
		
		page.import.error = null;
		page.import.saving = false;
		page.import.show = true; // Buka modal di sini
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
		await get();
		page.loading = false;
	});

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
					Anda memiliki generator cuaca dalam model Anda yang tidak memiliki nilai bulanan yang sesuai.
					Nilai bulanan bukan nol untuk setiap statistik diperlukan agar SWAT+ dapat berjalan.
					Silakan gunakan fungsi impor dengan basis data SWAT+ WGN jika Anda tidak yakin, atau lihat dokumentasi SWAT+.
					Stasiun dengan data yang hilang tercantum di bawah ini.
				</p>
				<ul>
					<li v-for="station in page.validate.data">
						Station <router-link class="text-warning" :to="`/edit/climate/wgn/edit/${station.id}`">{{ station.name }}</router-link> has <b>{{ station.months }}</b> months of data; 12 are required.
					</li>
				</ul>
			</v-alert>

			<grid-view ref="grid" :api-url="table.apiUrl" :headers="table.headers" @change="getTableTotal">
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
							Yakin akan menghapus data <strong>ALL</strong> weather generators?
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
				<v-card title="Import Weather Generator Data">
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
										Diperlukan dua file CSV. Pastikan file yang Anda impor disimpan dengan pengkodean UTF-8. 
										<open-in-browser url="https://plus.swat.tamu.edu/downloads/sample_files/wgn/swatplus_tf_wgn_template.zip" text="Download a template."></open-in-browser>
									</div>
									<ol class="mb-0">
										<li>
											Stations CSV file:
											<ul>
												<li>Columns <code>id, name, lat, lon, elev, rain_yrs</code></li>
												<li><code>id</code> harus diberi nomor unik</li>
											</ul>
										</li>
										<li>
											Monthly values CSV file:
											<ul>
												<li>Columns <code>id, wgn_id, month, tmp_max_ave, tmp_min_ave, tmp_max_sd, tmp_min_sd, pcp_ave, pcp_sd, pcp_skew, wet_dry, wet_wet, pcp_days, pcp_hhr, slr_ave, dew_ave, wnd_ave</code></li>
												<li><code>id</code> harus diberi nomor unik</li>
												<li><code>wgn_id</code> sesuai dengan <code>id</code> column dari file stasiun</li>
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
									Diperlukan satu file CSV. Satu stasiun per baris; semua data 12 bulan berada dalam satu baris. Pastikan file yang Anda impor disimpan dengan pengkodean UTF-8.
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
									Periksa apakah Anda menggunakan data cuaca yang diamati.
								</template>
							</v-checkbox>

							<v-checkbox v-if="page.import.hasObservedOnLoad" v-model="page.import.form.deleteExistingStations" hide-details>
								<template #label>
									Delete existing weather stations? CAUTION:This will remove any imported observed weather data.
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