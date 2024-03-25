<script setup lang="ts">
	import { reactive, onMounted, onUnmounted } from 'vue';
	import { useRoute } from 'vue-router';
	import { useHelpers } from '@/helpers';

	const route = useRoute();
	const { api, currentProject, errors, utilities, formatters, runProcess, constants } = useHelpers();

	let page:any = reactive({
		loading: false,
		error: null,
		import: {
			form: {
				fileName: null,
				type: 'export_csv',
				columnName: 'elevation'
			},
			options: {
				types: [
					{ text: 'Import', value: 'import_csv' },
					{ text: 'Export', value: 'export_csv' }
				],
				columns: [
					{ title: 'Ground Surface Elevation (m)', value: 'elevation' },
					{ title: 'Aquifer Thickness(m)', value: 'aquifer_thickness' },
					{ title: 'Groundwater ET Extinction Depth (m)', value: 'extinction_depth' },
					{ title: 'Initial Groundwater Head (m)', value: 'initial_head' },
				]
			},
			show: false,
			saving: false,
			error: null
		},
		exported: {
			show: false
		}
	});

	let task:any = reactive({
		progress: {
			percent: 0,
			message: null
		},
		error: null,
		running: false,
		currentPid: null,
		isGridTask: false
	});

	function importData() {
		page.import.error = null;
		page.import.saving = true;
		page.import.show = false;

		if (formatters.isNullOrEmpty(page.import.form.fileName)) {
			page.import.error = 'Please select a file below.';
		} else {
			let args = [page.import.form.type, 
					'--db_file='+ currentProject.projectDb,
					'--file_name='+ page.import.form.fileName,
					'--table_name=gwflow_grid',
					'--column_name=' + page.import.form.columnName,
					'--swat_version=' + constants.appSettings.swatplus];

			runTask(args);
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
		task.currentPid = runProcess.runApiProc('gwflowgrids', 'swatplus_api', args);
	}

	let listeners:any = {
		stdout: undefined,
		stderr: undefined,
		close: undefined
	}

	function initRunProcessHandlers() {
		listeners.stdout = runProcess.processStdout('gwflowgrids', (data:any) => {
			console.log(`stdout: ${data}`);
			task.progress = runProcess.getApiOutput(data);
		});
		
		listeners.stderr = runProcess.processStderr('gwflowgrids', (data:any) => {
			console.log(`stderr: ${data}`);
			task.error = data;
			task.running = false;
		});
		
		listeners.close = runProcess.processClose('gwflowgrids', (code:any) => {
			errors.log(`close: ${code}`);
			if (formatters.isNullOrEmpty(task.error)) {
				if (page.import.form.type === 'export_csv') {
					task.running = false;
					page.exported.show = true;
				} else {
					task.running = false;
					page.import.show = true;
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
	}

	onMounted(() => initRunProcessHandlers())
	onUnmounted(() => removeRunProcessHandlers());
</script>

<template>
	<project-container :loading="page.loading" :load-error="page.error">
		<file-header input-file="gwflow.input" docs-path="modflow" use-io>
			<router-link to="/edit/cons/gwflow">Groundwater Flow</router-link>
			/ Grid Data
		</file-header>

		<p>
			Grid cells are setup in QSWAT+ step 2. You cannot modify the grid structure through the editor, however you may modify some grid cell values below.
			The editor cannot handle shape files, but you can import a text file of your grid instead using columns and rows delimited by spaces, tabs, or commas.
			Any values set for inactive cells will be ignored. Export your current data first for a template.
		</p>

		<div>
			<error-alert :text="page.import.error"></error-alert>
			<success-alert v-if="page.import.show" no-popup text="Data imported successfully"></success-alert>
			<stack-trace-error v-if="!formatters.isNullOrEmpty(task.error)" error-title="There was an error importing or exporting your data." :stack-trace="task.error.toString()" />
			
			<div v-if="task.running">
				<v-progress-linear :model-value="task.progress.percent" color="primary" height="15" striped indeterminate></v-progress-linear>
				<p>
					{{task.progress.message}}
				</p>
			</div>
			<div v-else-if="formatters.isNullOrEmpty(task.error)">
				<v-btn-toggle v-model="page.import.form.type" color="primary" variant="outlined" mandatory class="mb-4">
					<v-btn value="import_csv">Import</v-btn>
					<v-btn value="export_csv">Export</v-btn>
				</v-btn-toggle>

				<v-select v-model="page.import.form.columnName" :items="page.import.options.columns" @update:model-value="page.import.form.fileName = ''"
					:label="`Select a column to ${page.import.form.type === 'import_csv' ? 'import' : 'export'}`" class="mb-3" required></v-select>

				<select-file-input v-model="page.import.form.fileName" :value="page.import.form.fileName" class="mb-3"
					:label="page.import.form.type == 'import_csv' ? `Select a file to import` : `Select where to save your file`"
					fileType="text" required :default-file-name="`gwflow-grid-data-${page.import.form.columnName}.txt`" :save-dialog="page.import.form.type == 'export_csv'"
					invalidFeedback="Please select a file."></select-file-input>
			</div>
		</div>

		<action-bar>
			<v-btn v-if="formatters.isNullOrEmpty(task.error)" :loading="task.running" @click="importData" color="primary" variant="flat">
				{{ page.import.form.type === 'export_csv' ? 'Export Data' : 'Import Data' }}
			</v-btn>
			<v-btn @click="cancelTask" v-if="task.running" variant="tonal">Cancel</v-btn>
			<v-btn @click="cancelTask" v-if="!formatters.isNullOrEmpty(task.error)" variant="tonal">Try Again</v-btn>
		</action-bar>

		<v-dialog v-model="page.exported.show" :max-width="constants.dialogSizes.md">
			<v-card title="Data Exported">
				<v-card-text>
					<p>
						Your data has been exported to a text file. 
					</p>
					<p>
						<open-file :file-path="page.import.form.fileName" text="Open file" button color="primary"></open-file>
					</p>
				</v-card-text>
				<v-divider></v-divider>
				<v-card-actions>
					<v-btn @click="page.exported.show = false">Close</v-btn>
				</v-card-actions>
			</v-card>
		</v-dialog>
	</project-container>
</template>