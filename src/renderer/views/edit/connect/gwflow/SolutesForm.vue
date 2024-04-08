<script setup lang="ts">
	import { reactive, onMounted, computed, onUnmounted } from 'vue';
	import { useRouter } from 'vue-router';
	import { useHelpers } from '@/helpers';

	const router = useRouter();
	const { api, constants, currentProject, errors, formatters, utilities, runProcess } = useHelpers();

	interface Props {
		item: any,
		isUpdate?: boolean
	}

	const props = withDefaults(defineProps<Props>(), {
		apiUrl: '',
		item: {},
		isUpdate: false
	});

	let page:any = reactive({
		loading: true,
		error: null,
		validated: false,
		saving: false,
		saveSuccess: false,
		options: {
			init_data: [
				{ value: 'single', title: 'Single' },
				{ value: 'array', title: 'Array' }
			]
		},
		import: {
			form: {
				fileName: null,
				type: 'export_csv'
			},
			show: false,
			saving: false,
			error: null
		},
		exported: {
			show: false
		},
		imported: {
			show: false
		}
	});

	function putDb(data:any) {
		if (props.isUpdate)
			return api.put(`gwflow/solutes/${props.item.solute_name}`, data, currentProject.getApiHeader());
		else
			return api.post(`gwflow/solutes`, data, currentProject.getApiHeader());
	}

	async function save() {
		page.error = null;
		page.saving = true;
		page.saveSuccess = false;
		page.validated = true;
		let val_error = false;
		
		if (!val_error) {
			try {
				const response = await putDb(props.item);

				if (props.isUpdate)
					page.saveSuccess = true;
				else
					router.push({ name: 'GwflowRescell' });
			} catch (error) {
				page.error = errors.logError(error, 'Unable to save changes to database.');
			}
		}
		
		page.saving = false;
		page.validated = false;
	}

	const arrayColumnName = computed(() => {
		if (props.item.solute_name === 'no3-n') return 'init_no3';
		return 'init_' + props.item.solute_name;
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
		page.imported.show = false;

		if (formatters.isNullOrEmpty(page.import.form.fileName)) {
			page.import.error = 'Please select a file below.';
		} else {
			let args = [page.import.form.type, 
					'--db_file='+ currentProject.projectDb,
					'--file_name='+ page.import.form.fileName,
					'--table_name=gwflow_grid',
					'--column_name=' + arrayColumnName.value,
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
		task.currentPid = runProcess.runApiProc('gwflowsolutes', 'swatplus_api', args);
	}

	let listeners:any = {
		stdout: undefined,
		stderr: undefined,
		close: undefined
	}

	function initRunProcessHandlers() {
		listeners.stdout = runProcess.processStdout('gwflowsolutes', (data:any) => {
			console.log(`stdout: ${data}`);
			task.progress = runProcess.getApiOutput(data);
		});
		
		listeners.stderr = runProcess.processStderr('gwflowsolutes', (data:any) => {
			console.log(`stderr: ${data}`);
			task.error = data;
			task.running = false;
		});
		
		listeners.close = runProcess.processClose('gwflowsolutes', (code:any) => {
			errors.log(`close: ${code}`);
			if (formatters.isNullOrEmpty(task.error)) {
				if (page.import.form.type === 'export_csv') {
					task.running = false;
					closeTaskModals();
					page.exported.show = true;
				} else {
					task.running = false;
					closeTaskModals();
					page.imported.show = true;
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

	onMounted(() => initRunProcessHandlers())
	onUnmounted(() => removeRunProcessHandlers());
</script>

<template>
	<div>
		<error-alert :text="page.error"></error-alert>
		<success-alert v-model="page.saveSuccess" :show="page.saveSuccess"></success-alert>

		<v-form @submit.prevent="save">
			<div class="form-group">
				<v-text-field v-model.number="item.solute_name" :rules="[constants.formRules.required]" :readonly="props.isUpdate"
					label="Name" :hint="props.isUpdate ? 'Solute name cannot be modified.' : ''" persistent-hint></v-text-field>
			</div>

			<div class="form-group">
				<v-text-field v-model.number="item.sorption" :rules="[constants.formRules.required]" 
					label="Sorption" type="number" step="any"></v-text-field>
			</div>

			<div class="form-group">
				<v-text-field v-model.number="item.rate_const" :rules="[constants.formRules.required]" 
					label="Rate Constant" type="number" step="any"></v-text-field>
			</div>

			<div class="form-group">
				<v-text-field v-model.number="item.canal_irr" :rules="[constants.formRules.required]" 
					label="Canal Irrigation" type="number" step="any"></v-text-field>
			</div>

			<div class="form-group">
				<v-select v-model.number="item.init_data" :rules="[constants.formRules.required]" 
					label="Initial Concentration Data Type" :items="page.options.init_data"></v-select>
			</div>

			<div v-if="item.init_data === 'single'" class="form-group">
				<v-text-field v-model.number="item.init_conc" :rules="[constants.formRules.required]" 
					label="Initial Concentration (g/m3)" type="number" step="any"></v-text-field>
			</div>

			<div v-else>
				<p>
					Use the import/export tool below to add or edit the grid array of initial concentration values.
					We recommend exporting first to get a file template.
				</p>
				<p>
					<v-btn variant="flat" color="info" class="mr-2" @click="page.import.show = true">Import/Export Grid Array</v-btn>
				</p>
				<success-alert v-if="page.imported.show" no-popup text="Data imported successfully. Be sure to click 'Save Changes' below to finish saving this solute."></success-alert>
			</div>

			<action-bar>
				<v-btn type="submit" :loading="page.saving" variant="flat" color="primary" class="mr-2">Save Changes</v-btn>
				<back-button></back-button>
			</action-bar>
		</v-form>

		<v-dialog v-model="page.import.show" :max-width="constants.dialogSizes.lg" persistent>
			<v-card title="Import/Export Data">
				<v-card-text>
					<error-alert :text="page.import.error"></error-alert>
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

						<select-file-input v-model="page.import.form.fileName" :value="page.import.form.fileName" class="mb-3"
							:label="page.import.form.type == 'import_csv' ? `Select a file to import` : `Select where to save your file`"
							fileType="text" required :default-file-name="`gwflow-grid-solutes-${arrayColumnName}.txt`" :save-dialog="page.import.form.type == 'export_csv'"
							invalidFeedback="Please select a file."></select-file-input>
					</div>
				</v-card-text>
				<v-divider></v-divider>
				<v-card-actions>
					<v-btn v-if="formatters.isNullOrEmpty(task.error)" :loading="task.running" @click="importData" color="primary" variant="text">
						{{ page.import.form.type === 'export_csv' ? 'Export Data' : 'Import Data' }}
					</v-btn>
					<v-btn @click="cancelTask">Cancel</v-btn>
				</v-card-actions>
			</v-card>
		</v-dialog>

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
	</div>
</template>