<script setup lang="ts">
	import { reactive, ref, onMounted, onUnmounted } from 'vue';
	import { useRoute } from 'vue-router';
	import { useHelpers } from '@/helpers';
	const route = useRoute();
	const { api, constants, errors, formatters, currentProject, runProcess, utilities } = useHelpers();
	const electron = window.electronApi;

	const recallGrid = ref();

	let table:any = {
		apiUrl: 'recall/items',
		headers: [
			{ key: 'name', label: 'Name' },
			{ key: 'area', label: 'Area (ha)', type: 'number', class: 'text-right' },
			{ key: 'lat', label: 'Lat', type: 'number', class: 'text-right' },
			{ key: 'lon', label: 'Lon', type: 'number', class: 'text-right' },
			{ key: 'elev', label: 'Elev (m)', type: 'number', class: 'text-right' },
			{ key: 'wst', label: 'Weather Station', type: 'object', class: 'text-right', objectRoutePath: '/edit/climate/stations/edit/' },
			{ key: 'rec_typ', label: 'Time Step', class: 'text-right', formatter: (value:any) => { return value == 1 ? 'Daily' : (value == 2 ? 'Monthly' : (value == 3 ? 'Yearly' : 'Constant')) } },
			{ key: 'outflow', label: '# Outflow', class: 'text-right' }
		],
	};

	let page:any = reactive({
		import: {
			show: false,
			saving: false,
			error: null,
			inputFile: null,
			inputDir: null,
			exportDir: null,
			type: 'import_csv',
			options: {
				formats: [
					{ value: 'rec_cnst', text: 'Constant' },
					{ value: 'rec_dat', text: 'Time Series' }
				],
				types: [
					{ text: 'Import', value: 'import_csv' },
					{ text: 'Export', value: 'export_csv' }
				]
			}
		},
		exported: {
			show: false
		},
		showInfo: false
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

	function importData() {
		page.import.error = null;
		page.import.saving = true;

		if (page.import.type === 'export_csv') {
			if (formatters.isNullOrEmpty(page.import.exportDir)) {
				page.import.error = 'Please select a directory to save your data.';
			} else {
				let args = ['export_recall', 
						'--db_file='+ currentProject.projectDb,
						'--delete_existing=n',
						'--input_files_dir=' + page.import.exportDir];
				console.log(args);
				runTask(args);
			}
		}
		else {
			if (formatters.isNullOrEmpty(page.import.inputDir)) {
				page.import.error = 'Please select a directory containing your data.';
			} else {
				let args = ['import_recall', 
						'--db_file='+ currentProject.projectDb,
						'--delete_existing=y',
						'--input_files_dir=' + page.import.inputDir];
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

		task.currentPid = runProcess.runApiProc('recall', 'swatplus_api', args);
	}

	let listeners:any = {
		stdout: undefined,
		stderr: undefined,
		close: undefined
	}

	function initRunProcessHandlers() {
		listeners.stdout = runProcess.processStdout('recall', (data:any) => {
			task.progress = runProcess.getApiOutput(data);
		});
		
		listeners.stderr = runProcess.processStderr('recall', (data:any) => {
			console.log(`stderr: ${data}`);
			task.error = data;
			task.running = false;
		});
		
		listeners.close = runProcess.processClose('recall', async (code:any) => {
			console.log('recall close')
			if (formatters.isNullOrEmpty(task.error)) {
				if (page.import.type === 'export_csv') {
					task.running = false;
					closeTaskModals();
					page.exported.show = true;
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
		page.import.show = false;
	}

	onMounted(() => initRunProcessHandlers());
	onUnmounted(() => removeRunProcessHandlers());
</script>

<template>
	<project-container>
		<div v-if="route.name == 'Recall'">
			<file-header input-file="recall.con" docs-path="connections/recall">
				Point Source / Inlet Data
			</file-header>

			<grid-view ref="recallGrid" :api-url="table.apiUrl" :headers="table.headers">
				<template v-slot:header>
					<v-dialog v-model="page.showInfo" :max-width="constants.dialogSizes.md">
						<template v-slot:activator="{ props }">
							<v-btn elevation="1" color="info" class="mx-3" size="large" prepend-icon="fas fa-circle-exclamation" v-bind="props">
								Note
							</v-btn>
						</template>

						<v-card>
							<v-card-text>
								<p>
									In SWAT+, constant values for point sources and inlets are stored in the export coefficients properties file, exco.exc, while time series data are stored entirely in the recall section.
									However, in the editor, we keep both time series and constant recall and export coefficients in the same section. When you write input files, the editor will write to the appropriate files.
								</p>
								<p>
									QSWAT+ automatically generates an empty point source location for each channel in your model. We recommend keeping all of these points in your model. They will not be used unless you update the data yourself.
									If keeping constant point source data, flow will need to be greater than 0 in order to be read by the model. Click a point below to modify its data, or use the import/export button at the bottom of the page.
								</p>
							</v-card-text>
							<v-card-actions>
								<v-btn color="primary" block @click="page.showInfo = false">Close</v-btn>
							</v-card-actions>
						</v-card>
					</v-dialog>
				</template>

				<template v-slot:actions>
					<v-btn variant="flat" color="info" @click="page.import.show = true" class="mr-2">Import/Export</v-btn>
				</template>
			</grid-view>

			<v-dialog v-model="page.import.show" :max-width="constants.dialogSizes.lg" persistent>
				<v-card title="Import/Export Data">
					<v-card-text>
						<error-alert :text="page.import.error"></error-alert>
						<stack-trace-error v-if="!formatters.isNullOrEmpty(task.error)" error-title="There was an error importing or exporting your data." :stack-trace="task.error.toString()" />
						
						<div v-if="task.running">
							<v-progress-linear :model-value="task.progress.percent" color="primary" height="15" striped></v-progress-linear>
							<p>
								{{task.progress.message}}
							</p>
						</div>
						<div v-else-if="formatters.isNullOrEmpty(task.error)">
							<p>
								Use the toggle below to import constant or time series CSV files, or to export your existing data to a directory.
							</p>

							<v-btn-toggle v-model="page.import.type" color="primary" variant="outlined" mandatory class="mb-4">
								<v-btn value="import_csv">Import</v-btn>
								<v-btn value="export_csv">Export</v-btn>
							</v-btn-toggle>

							<div v-if="page.import.type === 'import_csv'">
								<v-alert type="info" icon="$info" variant="tonal" border="start" class="mb-4">
									<p>
										Provide a directory containing a CSV file for each recall object. For time series data, each file should be named for the object's name, e.g., 
										object <code>pt001</code> should have a file in the directory <code>pt001.csv</code>.
									</p>
									<p>
										Time series files may be daily, monthly, or yearly. <strong>Make sure your simulation dates fall within the dates of your data.</strong> 
										Not all recall objects need to be the same time step.
										You do not need to have a time series file or constant record for each recall object. Just leave it out of the directory to ignore.
									</p>
									<p>
										Constant data should be contained in a single CSV file named <code>recall.csv</code>.
										The first column should be the name of each record.
									</p>
									<p class="mb-0">
										To get templates for the time step you desire, we recommend clicking a row in the recall table, change the time step as needed,
										save changes, then return to this form and export the data to CSV. You may also <open-in-browser class="text-primary" url="https://plus.swat.tamu.edu/downloads/sample_files/point-source/swatplus-editor-point-source.zip" text="download an example here" />. For additional help,
										<open-in-browser class="text-primary" url="https://swatplus.gitbook.io/docs/user/editor/inputs/connections/recall" text="view the documentation online" />.
									</p>
								</v-alert>

								<select-folder-input v-model="page.import.inputDir" :value="page.import.inputDir" class="mb-3"
									label="Directory containing your recall CSV files"
									:required="page.import.type === 'import_csv'" invalidFeedback="Please select a folder"></select-folder-input>
							</div>
							<div v-else>
								<select-folder-input v-model="page.import.exportDir" :value="page.import.exportDir" class="mb-3"
									label="Directory to save your recall CSV files"
									:required="page.import.type === 'export_csv'" invalidFeedback="Please select a folder"></select-folder-input>
							</div>
						</div>
					</v-card-text>
					<v-divider></v-divider>
					<v-card-actions>
						<v-btn v-if="formatters.isNullOrEmpty(task.error)" :loading="task.running" @click="importData" color="primary" variant="text">
							{{ page.import.type === 'export_csv' ? 'Export Data' : 'Import Data' }}
						</v-btn>
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
							<open-file :file-path="page.import.exportDir" text="Open directory" button color="primary"></open-file>
						</p>
					</v-card-text>
					<v-divider></v-divider>
					<v-card-actions>
						<v-btn @click="page.exported.show = false">Close</v-btn>
					</v-card-actions>
				</v-card>
			</v-dialog>
		</div>
		<router-view></router-view>
	</project-container>
</template>