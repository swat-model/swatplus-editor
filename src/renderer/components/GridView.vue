<script setup lang="ts">
	import { reactive, onMounted, onUnmounted, computed, watch } from 'vue';
	import { useRoute } from 'vue-router';
	import { useDisplay } from 'vuetify';
	// @ts-ignore
	import _ from 'underscore';
	import { useHelpers } from '@/helpers';
	import { GridViewHeader } from '@/typings';

	const route = useRoute();
	const { height } = useDisplay();
	const { api, constants, currentProject, errors, formatters, runProcess, utilities } = useHelpers();

	const tableHeight = computed(() => {
		if (height.value < 730) return '60vh';
		if (height.value < 900) return '70vh';
		if (height.value < 1050) return '75vh';
		return '78vh';
	})

	const emit = defineEmits(['change'])

	interface Props {
		apiUrl: string,
		deleteApiUrl?: string | null
		headers?: GridViewHeader[],
		useDynamicHeaders?: boolean,
		noActionBar?: boolean,
		fullWidthActionBar?: boolean,
		fullestWidthActionBar?: boolean,
		hideSummary?: boolean,
		hideFilter?: boolean,
		hideCreate?: boolean,
		hideEdit?: boolean,
		hideDelete?: boolean,
		itemsPerPage?: number,
		defaultSort?: [string,string], //[sort key, asc or desc]
		hideFields?: string[],
		showImportExport?: boolean,
		defaultCsvFile?: string,
		tableName?: string,
		importExportRelatedId?: number|null,
		importExportDescription?: string,
		importExportNotes?: string,
		importExportDeleteExisting?: boolean,
		importPrimaryKey?: string,
		autoHeight?: boolean,
		editPathPrefix?: string,
		hideBackButton?: boolean
	}

	const props = withDefaults(defineProps<Props>(), {
		apiUrl: '',
		deleteApiUrl: null,
		headers: () => <GridViewHeader[]>[],
		useDynamicHeaders: false,
		noActionBar: false,
		fullWidthActionBar: false,
		fullestWidthActionBar: false,
		hideSummary: false,
		hideFilter: false,
		hideCreate: false,
		hideEdit: false,
		hideDelete: false,
		itemsPerPage: 50,
		defaultSort: () => ['name', 'asc'],
		hideFields: () => ['id'],
		showImportExport: false,
		defaultCsvFile: '',
		tableName: '',
		importExportRelatedId: null,
		importExportDescription: 'CSV',
		importExportNotes: '',
		importExportDeleteExisting: false,
		importPrimaryKey: '',
		autoHeight: false,
		editPathPrefix: '',
		hideBackButton: false
	});

	const loaderArray = computed(() => {
		let arr:number[] = [];
		for(let i = 0; i < props.itemsPerPage; i++) {
			arr.push(i);
		}
		return arr;
	});

	const showFirst = computed(() => {
		if (data.total < 1) return 0;
		return (table.page-1) * table.itemsPerPage + 1
	});

	const showLast = computed(() => {
		var max = (table.page-1) * table.itemsPerPage + table.itemsPerPage
		return max > data.matches ? data.matches : max;
	});

	const headerCount = computed(() => {
		let c = table.headers.length;
		if (!props.hideEdit) c++;
		if (!props.hideDelete) c++;
		return c;
	})

	let page:any = reactive({
		loading: false,
		error: null,
		delete: {
			show: false,
			id: null,
			name: '',
			error: null,
			saving: false
		},
		import: {
			form: {
				fileName: null,
				type: 'export_csv'
			},
			options: {
				types: [
					{ text: 'Import', value: 'import_csv' },
					{ text: 'Export', value: 'export_csv' }
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

	let table:any = reactive({
		loading: false,
		error: null,
		itemsPerPage: props.itemsPerPage,
		page: 1,
		sortBy: props.defaultSort,
		headers: props.headers,
		filter: null
	});

	let data:any = reactive({
		total: 0,
		matches: 0,
		items: []
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

	async function get(init = false) {
		table.loading = true;
		table.error = null;

		try {
			let qPage = table.page;
			let qSort = '';
			let qRev = 'n';
			let qPerPage = table.itemsPerPage;

			if (table.sortBy.length) {
				qSort = table.sortBy[0];
				qRev = table.sortBy[1] === 'desc' ? 'y' : 'n';
			}

			let filter = !props.hideFilter && table.filter !== null ? `&filter=${encodeURIComponent(table.filter)}` : '';

			let query = `?sort=${qSort}&reverse=${qRev}&page=${qPage}&per_page=${qPerPage}${filter}`;
			
			const response = await api.get(`${props.apiUrl}${query}`, currentProject.getApiHeader());
			errors.log(response.data);
			data.total = response.data.total;
			data.matches = response.data.matches;
			data.items = response.data.items;
			emit('change', data.total);

			if (init) {
				getDynamicHeaders();
			}
		} catch (error) {
			errors.log(error);
		}
		
		table.loading = false;
	}

	function getDynamicHeaders() {
		if (props.useDynamicHeaders && data.items.length > 0) {
			let item = data.items[0];
			let keys = Object.keys(item);

			for (let key of keys) {
				if (!props.hideFields.includes(key) && !Array.isArray(item[key])) {
					let header:GridViewHeader = <GridViewHeader>{
						key: key,
						type: item[key] == null ? 'string' : typeof(item[key]),
						decimals: typeof(item[key]) == 'number' ? 2 : 0,
						class: typeof(item[key]) == 'number' ? 'text-right' : ''
					};
					
					if (key == 'name') table.headers.unshift(header);
					else table.headers.push(header);
				}
			}
		}
	}

	async function doSort(newSortByKey:string) {
		let dir = table.sortBy[1] === 'asc' ? 'desc' : 'asc';
		table.sortBy = [newSortByKey, dir];
		await get(false);
	}

	function getNumPages() {
		return Math.ceil(data.total / table.itemsPerPage);
	}

	async function filterChange() {
		table.page = 1;
		_.debounce(await get(false), 500);
	}

	function askDelete(id:any, name:any) {
		page.delete.id = id;
		page.delete.name = name;
		page.delete.show = true;
	}

	async function confirmDelete() {
		page.delete.errors = [];
		page.delete.saving = true;

		try {
			let url = formatters.isNullOrEmpty(props.deleteApiUrl) ? props.apiUrl : props.deleteApiUrl;
			const response = await api.delete(`${url}/${page.delete.id}`, currentProject.getApiHeader());
			errors.log(response);
			page.delete.show = false;
			table.currentPage = 1;
			await get(false);
		} catch (error) {
			page.delete.error = errors.logError(error, 'Unable to delete from database.');
		}

		page.delete.saving = false;
	}

	function importData() {
		page.import.error = null;
		page.import.saving = true;

		if (formatters.isNullOrEmpty(page.import.form.fileName)) {
			page.import.error = 'Please select a file below.';
		} else {
			let args = [page.import.form.type, 
					'--db_file='+ currentProject.projectDb,
					'--file_name='+ page.import.form.fileName,
					'--table_name='+ props.tableName];

			if (!formatters.isNullOrEmpty(props.importExportRelatedId)) args.push('--related_id=' + props.importExportRelatedId);
			if (props.importExportDeleteExisting) args.push('--delete_existing=y');
			if (!formatters.isNullOrEmpty(props.importPrimaryKey)) args.push('--column_name=' + props.importPrimaryKey);

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
		task.currentPid = runProcess.runApiProc('gridview', 'swatplus_api', args);
	}

	let listeners:any = {
		stdout: undefined,
		stderr: undefined,
		close: undefined
	}

	function initRunProcessHandlers() {
		listeners.stdout = runProcess.processStdout('gridview', (data:any) => {
			console.log(`stdout: ${data}`);
			task.progress = runProcess.getApiOutput(data);
		});
		
		listeners.stderr = runProcess.processStderr('gridview', (data:any) => {
			console.log(`stderr: ${data}`);
			task.error = data;
			task.running = false;
		});
		
		listeners.close = runProcess.processClose('gridview', async (code:any) => {
			errors.log(`close: ${code}`);
			if (formatters.isNullOrEmpty(task.error)) {
				if (page.import.form.type === 'export_csv') {
					task.running = false;
					closeTaskModals();
					page.exported.show = true;
				} else {
					await get(false);
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

	function getEditRoute(item:any) {
		let pk = item.id;
		if (!formatters.isNullOrEmpty(props.importPrimaryKey)) pk = item[props.importPrimaryKey];
		return formatters.isNullOrEmpty(props.editPathPrefix) ? utilities.appendRoute(`edit/${pk}`) : `${props.editPathPrefix}edit/${pk}`
	}

	onMounted(async () => {
		page.loading = true;
		initRunProcessHandlers();
		await get(true);
		page.loading = false;
	});
	
	onUnmounted(() => removeRunProcessHandlers());

	watch(() => route.path, async () => await get(true))

	defineExpose({
		get
	})
</script>

<template>
	<project-container :loading="page.loading">
		<div class="d-flex align-end mb-4">
			<div>
				<v-text-field density="compact" variant="solo" append-inner-icon="fas fa-magnifying-glass" single-line hide-details
					class="mb-0" style="width:300px"
					label="Search..." v-model="table.filter" @input="filterChange"></v-text-field>
				
			</div>
			<slot name="header"></slot>
			<div v-if="!props.hideSummary" class="ml-auto text-right text-body-2">
				Showing {{showFirst}} - {{showLast}} of {{data.matches}} {{formatters.isNullOrEmpty(table.filter) ? 'rows' : 'matches'}}
			</div>
		</div>
		<v-card>
			<v-table class="data-table" fixed-header :height="autoHeight ? 'auto' : tableHeight" density="compact">
				<thead>
					<tr class="bg-surface">
						<th v-if="!props.hideEdit" class="bg-secondary-tonal min"></th>
						<th v-for="header in table.headers" :key="header.key" :class="`${header.class} pointer bg-secondary-tonal`" @click="doSort(header.key)">
							{{ formatters.isNullOrEmpty(header.label) ? header.key : header.label }}
							<v-icon v-if="!header.noSort && table.sortBy[0] === header.key && table.sortBy[1] === 'asc'" class="fa-xs ms-2">fas fa-arrow-up</v-icon>
							<v-icon v-if="!header.noSort && table.sortBy[0] === header.key && table.sortBy[1] === 'desc'" class="fa-xs ms-2">fas fa-arrow-down</v-icon>
						</th>
						<th v-if="!props.hideDelete" class="bg-secondary-tonal min"></th>
					</tr>
				</thead>
				<tbody v-if="table.loading">
					<tr v-for="i in loaderArray" :key="i">
						<td v-if="!props.hideEdit" class="min"></td>
						<td v-for="header in table.headers" :key="header.key"><v-skeleton-loader type="text" max-width="150"></v-skeleton-loader></td>
						<td v-if="!props.hideDelete" class="min"></td>
					</tr>
				</tbody>
				<tbody v-else>
					<tr v-if="!data.items || data.items.length < 1">
						<td :colspan="headerCount" class="text-center text-medium-emphasis py-6">
							<em>No data available. {{ !props.hideCreate && formatters.isNullOrEmpty(table.filter) ? 'Use the button at the bottom of this page to create a new record.' : '' }}</em>
						</td>
					</tr>
					<tr v-for="item in data.items">
						<td v-if="!props.hideEdit" class="min">
							<router-link :to="getEditRoute(item)" class="text-decoration-none text-primary" 
								:title="`Edit/View (${getEditRoute(item)})`">
								<font-awesome-icon :icon="['fas', 'edit']"></font-awesome-icon>
							</router-link>
						</td>
						<td v-for="header in table.headers" :key="header.key" :class="header.class">
							<div v-if="header.type === 'number'">
								{{ formatters.toNumberFormat(item[header.key], header.decimals||2, '', '-', ['yr','year'].includes(header.key)) }}
							</div>
							<div v-else-if="header.type === 'boolean'">
								{{ item[header.key] ? 'Y' : 'N' }}
							</div>
							<div v-else-if="header.type === 'object'">
								<span v-if="formatters.isNullOrEmpty(item[header.key])">-</span>
								<router-link v-else-if="!formatters.isNullOrEmpty(header.objectRoutePath)" class="text-primary text-decoration-none" 
									:to="`${header.objectRoutePath}${header.ignoreObjectRouteId ? '' : item[header.key][header.objectValueField||'id']}`">
									{{ item[header.key][header.objectTextField||'name'] }}
								</router-link>
								<span v-else>
									{{ item[header.key][header.objectTextField||'name'] }}
								</span>
							</div>
							<div v-else-if="header.type === 'file'">
								<span v-if="formatters.isNullOrEmpty(item[header.key])">{{ header.defaultIfNull }}</span>
								<span v-else>
									<open-file :file-path="`${header.filePath}\\${item[header.key]}`" class="text-primary text-decoration-none">{{ item[header.key] }}</open-file>
								</span>
							</div>
							<div v-else-if="header.type === 'variable-object'">
								<span v-if="formatters.isNullOrEmpty(item[header.key])">-</span>
								<router-link v-else-if="utilities.getObjTypeRoute(item) !== '#'" class="text-primary text-decoration-none" 
									:to="utilities.getObjTypeRoute(item)">
									{{ item[header.key] }}
								</router-link>
								<span v-else>
									{{ item[header.key] }}
								</span>
							</div>
							<div v-else-if="header.formatter !== undefined">
								{{ header.formatter(item[header.key]) }}
							</div>
							<div v-else>
								{{ formatters.isNullOrEmpty(item[header.key]) ? '-' : item[header.key] }}
							</div>	
						</td>
						<td v-if="!props.hideDelete" class="min">
							<font-awesome-icon :icon="['fas', 'times']" class="text-error pointer" title="Delete" @click="askDelete(item.id, item.name)"></font-awesome-icon>
						</td>
					</tr>
				</tbody>
			</v-table>
		</v-card>
		<action-bar v-if="!props.noActionBar" :full-width="props.fullWidthActionBar" :fullest-width="props.fullestWidthActionBar">
			<v-btn v-if="!props.hideCreate" variant="flat" color="primary" class="mr-2" :to="utilities.appendRoute('create')">Create Record</v-btn>
			<v-btn v-if="props.showImportExport" variant="flat" color="info" class="mr-2" @click="page.import.show = true">Import/Export</v-btn>
			<slot name="actions"></slot>
			<back-button v-if="!hideBackButton"></back-button>
			<v-pagination v-model="table.page" @update:modelValue="get(false)" :total-visible="6"
				:length="getNumPages()" class="ml-auto" size="small"></v-pagination>
		</action-bar>
		<div v-else class="d-flex align-center mt-3">
			<v-btn v-if="!props.hideCreate" variant="flat" color="primary" class="mr-2" :to="utilities.appendRoute('create')">Create Record</v-btn>
			<v-btn v-if="props.showImportExport" variant="flat" color="info" class="mr-2" @click="page.import.show = true">Import/Export</v-btn>
			<slot name="actions"></slot>
			<v-pagination v-model="table.page" @update:modelValue="get(false)" :total-visible="6"
				:length="getNumPages()" class="ml-auto" size="small"></v-pagination>
		</div>

		<v-dialog v-model="page.delete.show" :max-width="constants.dialogSizes.md">
			<v-card title="Confirm delete">
				<v-card-text>
					<error-alert :text="page.delete.error"></error-alert>

					<p>
						Are you sure you want to delete <strong>{{page.delete.name}}</strong>?
						This action is permanent and cannot be undone. 
					</p>
				</v-card-text>
				<v-divider></v-divider>
				<v-card-actions>
					<v-btn @click="confirmDelete" :loading="page.delete.saving" color="error" variant="text">Delete</v-btn>
					<v-btn @click="page.delete.show = false">Cancel</v-btn>
				</v-card-actions>
			</v-card>
		</v-dialog>

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
						<p>
							Export your existing data to {{importExportDescription}} or import a {{importExportDescription}} file of new values. 
							Any existing values in the table with the same name will be updated to match your {{importExportDescription}} data.
							Export data first to get a template with the correct columns.
						</p>

						<v-alert v-if="!formatters.isNullOrEmpty(importExportNotes)" type="info" icon="$info" variant="tonal" border="start" class="mb-4">
							{{importExportNotes}}
						</v-alert>

						<v-btn-toggle v-model="page.import.form.type" color="primary" variant="outlined" mandatory class="mb-4">
							<v-btn value="import_csv">Import</v-btn>
							<v-btn value="export_csv">Export</v-btn>
						</v-btn-toggle>

						<select-file-input v-model="page.import.form.fileName" :value="page.import.form.fileName" class="mb-3"
							:label="page.import.form.type == 'import_csv' ? `Select a ${importExportDescription} file to import` : `Select where to save your ${importExportDescription} file`"
							:fileType="importExportDescription.toLowerCase()" required :default-file-name="defaultCsvFile" :save-dialog="page.import.form.type == 'export_csv'"
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
						Your data has been exported to a {{importExportDescription}} file. 
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