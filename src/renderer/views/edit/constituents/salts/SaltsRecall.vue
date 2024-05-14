<script setup lang="ts">
	import { reactive, ref, onMounted, onUnmounted, watch } from 'vue';
	import { useRoute } from 'vue-router';
	import { useHelpers } from '@/helpers';

	const route = useRoute();
	const { api, constants, errors, formatters, currentProject, runProcess, utilities } = useHelpers();
	const electron = window.electronApi;

	const recallGrid = ref();

	let table:any = {
		apiUrl: 'salts/recall',
		headers: [
			{ key: 'name', label: 'Name' },
			{ key: 'rec_typ', label: 'Time Step', class: 'text-right', formatter: (value:any) => { return value == 1 ? 'Daily' : (value == 2 ? 'Monthly' : (value == 3 ? 'Yearly' : '--')) } }
		],
		total: 0
	};

	let data:any = reactive({
		page: {
			error: null,
			loading: false,
			saving: false,
			saveSuccess: false,
			showError: false,
			showGrid: false
		},
		recall: false,
		options: [
			{ value: false, title: 'Disable salt point sources' },
			{ value: true, title: 'Enable salt point sources' }
		],
		import: {
			show: false,
			saving: false,
			error: null,
			inputFile: null,
			inputDir: null,
			exportDir: null,
			type: 'import_csv',
			options: {
				types: [
					{ text: 'Import', value: 'import_csv' },
					{ text: 'Export', value: 'export_csv' }
				]
			}
		},
		exported: {
			show: false
		},
		delete: {
			show: false,
			error: <string|null>null,
			saving: false
		},
		createTemplates: {
			show: false,
			error: <string|null>null,
			saving: false,
			time_step: 3,
			options: {
				time_step: [
					{ title: 'Daily', value: 1 },
					{ title: 'Monthly', value: 2 },
					{ title: 'Yearly', value: 3 }
				]
			}
		}
	});

	let task:any = reactive({
		progress: {
			percent: 0,
			message: null
		},
		process: null,
		error: null,
		running: false,
		currentPid: null
	});

	function getTableTotal(total:any) {
		table.total = total;
	}

	async function get() {
		data.page.loading = true;
		data.page.error = null;
		data.page.showError = false;

		try {
			const response = await api.get(`salts/enable-recall`, currentProject.getApiHeader());
			data.recall = response.data.recall;
			data.showGrid = data.recall;
		} catch (error) {
			data.page.error = errors.logError(error, 'Unable to get project information from database.');
		}
			
		data.page.showError = data.page.error !== null;
		data.page.loading = false;
	}

	async function save() {
		data.page.error = null;
		data.page.saving = true;
		data.page.showError = false;

		try {
			let formData = {
				recall: data.recall
			};
			const response = await api.put(`salts/enable-recall`, formData, currentProject.getApiHeader());

			data.showGrid = data.recall;
			if (data.showGrid) await recallGrid?.value?.get(false);
		} catch (error) {
			data.page.error = errors.logError(error, 'Unable to save changes to database.');
		}

		data.page.saving = false;
		data.page.showError = data.page.error !== null;
	}
	
	async function confirmDelete() {
		data.delete.errors = [];
		data.delete.saving = true;

		try {
			const response = await api.delete(`salts/recall`, currentProject.getApiHeader());
			errors.log(response);
			data.delete.show = false;
			await recallGrid?.value?.get(false);
		} catch (error) {
			data.delete.error = errors.logError(error, 'Unable to delete from database.');
		}

		data.delete.saving = false;
	}

	async function createTemplates() {
		data.createTemplates.errors = [];
		data.createTemplates.saving = true;

		try {
			let formData = {
				time_step: data.createTemplates.time_step
			};
			const response = await api.post(`salts/enable-recall`, formData, currentProject.getApiHeader());
			errors.log(response);
			data.createTemplates.show = false;
			await recallGrid?.value?.get(false);
		} catch (error) {
			data.createTemplates.error = errors.logError(error, 'Unable to create templates.');
		}

		data.createTemplates.saving = false;
	}

	function importData() {
		data.import.error = null;
		data.import.saving = true;

		if (data.import.type === 'export_csv') {
			if (formatters.isNullOrEmpty(data.import.exportDir)) {
				data.import.error = 'Please select a directory to save your data.';
			} else {
				let args = ['export_salt_recall', 
						'--db_file='+ currentProject.projectDb,
						'--delete_existing=n',
						'--input_files_dir=' + data.import.exportDir];
				console.log(args);
				runTask(args);
			}
		}
		else {
			if (formatters.isNullOrEmpty(data.import.inputDir)) {
				data.import.error = 'Please select a directory containing your data.';
			} else {
				let args = ['import_salt_recall', 
						'--db_file='+ currentProject.projectDb,
						'--delete_existing=y',
						'--input_files_dir=' + data.import.inputDir];
				console.log(args);

				runTask(args);
			}
		}
	}

	function runTask(args:string[]) {
		task.error = null;
		task.running = true;
		task.progress = {
			percent: 0,
			message: null
		};

		task.currentPid = runProcess.runApiProc('salt_recall', 'swatplus_api', args);
	}

	let listeners:any = {
		stdout: undefined,
		stderr: undefined,
		close: undefined
	}

	function initRunProcessHandlers() {
		listeners.stdout = runProcess.processStdout('salt_recall', (ldata:any) => {
			task.progress = runProcess.getApiOutput(ldata);
		});
		
		listeners.stderr = runProcess.processStderr('salt_recall', (ldata:any) => {
			console.log(`stderr: ${ldata}`);
			task.error = ldata;
			task.running = false;
		});
		
		listeners.close = runProcess.processClose('salt_recall', async (code:any) => {
			console.log('recall close')
			if (formatters.isNullOrEmpty(task.error)) {
				if (data.import.type === 'export_csv') {
					task.running = false;
					closeTaskModals();
					data.exported.show = true;
				} else {
					await recallGrid?.value?.get(false);
					task.running = false;
					closeTaskModals();
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
		data.import.show = false;
	}

	onMounted(async () => {
		initRunProcessHandlers();
		await get();
	})
	onUnmounted(() => removeRunProcessHandlers());
	watch(() => route.path, async () => await get())
</script>

<template>
	<project-container :loading="data.page.loading">
		<div v-if="$route.name == 'ConstituentsSaltsRecall'">
			<file-header input-file="constituents.cs" docs-path="constituents" use-io>
				<router-link to="/edit/constituents/salts">Salt Constituents</router-link>
				/ Point Sources
			</file-header>
			
			<v-form @submit.prevent="save">
				<error-alert as-popup v-model="data.page.showError" :show="data.page.showError" :text="data.page.error" :timeout="-1"></error-alert>
				<success-alert v-model="data.page.saveSuccess" :show="data.page.saveSuccess"></success-alert>

				<div class="form-group">
					<v-select label="Turn salt point sources module on/off" v-model="data.recall" :items="data.options">
						<template v-slot:append>
							<v-btn type="submit" :loading="data.page.saving" variant="flat" color="primary">Save Changes</v-btn>
						</template>
					</v-select>
				</div>
			</v-form>

			<grid-view v-if="data.showGrid" ref="recallGrid" :api-url="table.apiUrl" :headers="table.headers" @change="getTableTotal">
				<template v-slot:actions>
					<v-btn variant="flat" color="info" @click="data.import.show = true" class="mr-2">Import/Export</v-btn>
					<v-btn variant="flat" color="info" @click="data.createTemplates.show = true" class="mr-2">Create Templates</v-btn>
					<v-btn v-if="table.total > 0" variant="flat" color="error" class="mr-2" @click="data.delete.show = true">Delete All</v-btn>
				</template>
			</grid-view>

			<v-dialog v-model="data.import.show" :max-width="constants.dialogSizes.lg" persistent>
				<v-card title="Import/Export Data">
					<v-card-text>
						<error-alert :text="data.import.error"></error-alert>
						<stack-trace-error v-if="!formatters.isNullOrEmpty(task.error)" error-title="There was an error importing or exporting your data." :stack-trace="task.error.toString()" />
						
						<div v-if="task.running">
							<v-progress-linear :model-value="task.progress.percent" color="primary" height="15" striped></v-progress-linear>
							<p>
								{{task.progress.message}}
							</p>
						</div>
						<div v-else-if="formatters.isNullOrEmpty(task.error)">
							<p>
								Use the toggle below to import time series CSV files, or to export your existing data to a directory.
							</p>

							<v-btn-toggle v-model="data.import.type" color="primary" variant="outlined" mandatory class="mb-4">
								<v-btn value="import_csv">Import</v-btn>
								<v-btn value="export_csv">Export</v-btn>
							</v-btn-toggle>

							<div v-if="data.import.type === 'import_csv'">
								<v-alert type="info" icon="$info" variant="tonal" border="start" class="mb-4">
									<p>
										Provide a directory containing a CSV file for each recall object. <strong>Each file should be named for the object's name with <code>salt_</code> at the beginning, e.g., 
										object <code>pt001</code> should have a file in the directory <code>salt_pt001.csv</code>.</strong>
									</p>
									<p>
										Time series files may be daily, monthly, or yearly. <strong>Make sure your simulation dates fall within the dates of your data.</strong> 
										Not all recall objects need to be the same time step.
									</p>
									<p class="mb-0">
										To get templates for the time step you desire, use the <strong>Create Templates</strong> button at the bottom of the page, 
										then return to this form and export the data to CSV. 
									</p>
								</v-alert>

								<select-folder-input v-model="data.import.inputDir" :value="data.import.inputDir" class="mb-3"
									label="Directory containing your salt point sources CSV files"
									:required="data.import.type === 'import_csv'" invalidFeedback="Please select a folder"></select-folder-input>
							</div>
							<div v-else>
								<select-folder-input v-model="data.import.exportDir" :value="data.import.exportDir" class="mb-3"
									label="Directory to save your salt point sources CSV files"
									:required="data.import.type === 'export_csv'" invalidFeedback="Please select a folder"></select-folder-input>
							</div>
						</div>
					</v-card-text>
					<v-divider></v-divider>
					<v-card-actions>
						<v-btn v-if="formatters.isNullOrEmpty(task.error)" :loading="task.running" @click="importData" color="primary" variant="text">
							{{ data.import.type === 'export_csv' ? 'Export Data' : 'Import Data' }}
						</v-btn>
						<v-btn @click="cancelTask">Cancel</v-btn>
					</v-card-actions>
				</v-card>
			</v-dialog>

			<v-dialog v-model="data.exported.show" :max-width="constants.dialogSizes.md">
				<v-card title="Data Exported">
					<v-card-text>
						<p>
							Your data has been exported. 
						</p>
						<p>
							<open-file :file-path="data.import.exportDir" text="Open directory" button color="primary"></open-file>
						</p>
					</v-card-text>
					<v-divider></v-divider>
					<v-card-actions>
						<v-btn @click="data.exported.show = false">Close</v-btn>
					</v-card-actions>
				</v-card>
			</v-dialog>

			<v-dialog v-model="data.delete.show" :max-width="constants.dialogSizes.md">
				<v-card title="Confirm delete">
					<v-card-text>
						<error-alert :text="data.delete.error"></error-alert>

						<p>
							Are you sure you want to delete <strong>ALL</strong> salt point source data?
							This action is permanent and cannot be undone. 
						</p>
					</v-card-text>
					<v-divider></v-divider>
					<v-card-actions>
						<v-btn @click="confirmDelete" :loading="data.delete.saving" color="error" variant="text">Delete All</v-btn>
						<v-btn @click="data.delete.show = false">Cancel</v-btn>
					</v-card-actions>
				</v-card>
			</v-dialog>

			<v-dialog v-model="data.createTemplates.show" :max-width="constants.dialogSizes.md">
				<v-card title="Create Data Templates">
					<v-card-text>
						<error-alert :text="data.createTemplates.error"></error-alert>

						<p>
							Create salt point source templates for the selected time step.
							<span class="text-error">WARNING:</span> This will replace any existing data. To change an individual point source object instead,
							click a row in the table and change the time step as needed. 
						</p>

						<v-select label="Time step" v-model="data.createTemplates.time_step" :items="data.createTemplates.options.time_step"></v-select>
					</v-card-text>
					<v-divider></v-divider>
					<v-card-actions>
						<v-btn @click="createTemplates" :loading="data.createTemplates.saving" color="primary" variant="text">Create Templates</v-btn>
						<v-btn @click="data.createTemplates.show = false">Cancel</v-btn>
					</v-card-actions>
				</v-card>
			</v-dialog>
		</div>
		<router-view></router-view>
	</project-container>
</template>
