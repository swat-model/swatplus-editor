<script setup lang="ts">
	import { reactive, onMounted, watch, computed } from 'vue';
	import { useRouter } from 'vue-router';
	import TrVarEditor from './TrVarEditor.vue';
	import { usePlugins } from '../plugins';

	const router = useRouter();
	const { api, constants, currentProject, errors, formatters, utilities } = usePlugins();

	interface Props {
		apiUrl: string,
		redirectRoute: string,
		redirectPath?: boolean,
		showDescription?: boolean,
		showRange?: boolean,
		isUpdate?: boolean,
		updateMany?: boolean,
		item: any,
		vars: any,
		getDatasetsRecord?: boolean,
		hideName?: boolean,
		noId?: boolean,
		allowBulkEdit?: boolean,
		isHru?: boolean,
		noGis?: boolean,
		table?: string,
		name?: string,
		includeHruOption?: boolean,
		hideCopy?: boolean
	}

	const props = withDefaults(defineProps<Props>(), {
		apiUrl: '',
		redirectRoute: '',
		redirectPath: false,
		showDescription: false,
		showRange: false,
		isUpdate: false,
		updateMany: false,
		item: {},
		vars: {},
		getDatasetsRecord: false,
		hideName: false,
		noId: false,
		allowBulkEdit: false,
		isHru: false,
		noGis: false,
		table: '',
		name: '',
		includeHruOption: false,
		hideCopy: false
	});

	const data:any = reactive({
		page: {
			loading: false,
			error: null,
			saving: false,
			saveSuccess: false,
			saveError: false,
			validated: false,
			checkAll: false,
			bulk: {
				show: false,
				error: null,
				saving: false
			},
			copy: {
				show: false,
				error: null,
				saving: false,
				saveSuccess: false,
				name: null
			}
		},
		selectedItems: [],
		selectedVars: [],
		datasetItem: {},
		hasDatasetItem: false,
		doHru: null
	})

	function putDb(formData:any) {
		if (data.page.bulk.show)
			return api.put(props.apiUrl + '/many', formData, currentProject.getApiHeader());
		else if (props.isUpdate)
			if (props.noId)
				return api.put(props.apiUrl, formData, currentProject.getApiHeader());
			else
				return api.put(props.apiUrl + '/' + props.item.id, formData, currentProject.getApiHeader());
		else
			return api.post(props.apiUrl , formData, currentProject.getApiHeader());
	}

	function getDatasetsDb(name:string) {
		return api.get(props.apiUrl + '/datasets/' + name, currentProject.getApiHeader());
	}

	async function get() {
		data.page.loading = true;
		data.selectedItems.push(props.item.id);

		if (props.getDatasetsRecord && props.item.name) {
			try {
				const response = await getDatasetsDb(props.item.name);
				data.datasetItem = response.data;
				data.hasDatasetItem = true;
			} catch (error) {
				data.hasDatasetItem = false;
			}
		}

		data.page.loading = false;
	}

	async function save() {
		data.page.error = null;
		data.page.saving = true;
		data.page.saveSuccess = false;
		data.page.saveError = false;
		data.page.validated = true;
		let val_error = false;

		let item:any = {};
		if (!data.page.bulk.show) {
			item = props.item;
			if (!props.hideName) item.name = formatters.toValidName(props.item.name);
			let emptyFields = validateForm(item);
			if (!formatters.isNullOrEmpty(emptyFields)) {
				val_error = true;
				data.page.error = `The following fields are required: ${emptyFields}.`;
				data.page.saveError = true;
			}
		} else {
			if (data.selectedItems.length < 1) {
				val_error = true;
				data.page.error = 'You must select at least one record to edit.';
				data.page.saveError = true;
			}
			else if (data.selectedVars.length < 1) {
				val_error = true;
				data.page.error = 'You must check at least one field to edit.';
				data.page.saveError = true;
			}
			else {
				item = {};
				item.selected_ids = data.selectedItems;
			
				for (let v of data.selectedVars) {
					item[v] = props.item[v];
				}
			}
		}

		errors.log(item);
		if (!val_error) {
			try {
				const response = await putDb(item);

				if (props.isUpdate || props.updateMany)
					data.page.saveSuccess = true;
				else {
					if (props.redirectPath) router.push({ path: props.redirectRoute});
					else router.push({ name: props.redirectRoute});
				}
			} catch (error) {
				data.page.error = errors.logError(error, 'Unable to save changes to database.');
				data.page.saveError = true;
			}
		}
		
		data.page.saving = false;
		data.page.validated = false;
	}

	function validateForm(item:any) {
		let emptyFields:string[] = [];
		for (let k of Object.keys(props.vars)) {
			let v = props.vars[k];
			if (formatters.isNullOrEmpty(item[v.name])) {
				emptyFields.push(v.name);
			}
		}

		if (emptyFields.length > 0) return emptyFields.join(', ');
		return null;
	}

	async function copy() {
		data.page.copy.error = null;
		data.page.copy.saving = true;
		data.page.copy.saveSuccess = false;

		if (formatters.isNullOrEmpty(data.page.copy.name)) {
			data.page.copy.error = 'Please enter a name.';
		} else {
			try {
				let item:any = props.item;
				item.id = null;
				item.name = formatters.toValidName(data.page.copy.name);

				await api.post(`${props.apiUrl}`, item, currentProject.getApiHeader());

				data.page.copy.saveSuccess = true;
				router.push({ name: props.redirectRoute});
			} catch (error) {
				data.page.copy.error = errors.logError(error, 'Unable to save changes to database.');
			}
		}
		
		data.page.copy.saving = false;
	}

	function bulkSelectionChange(selection:any) {
		data.selectedItems = selection;
	}

	function selectedVarChange(selection:any) {
		errors.log(selection);
		if (selection.value && !data.selectedVars.includes(selection.name)) {
			data.selectedVars.push(selection.name);
		}
		else if (!selection.value && data.selectedVars.includes(selection.name)) {
			data.selectedVars = data.selectedVars.filter(function(el:any) { return el !== selection.name });
		}
		errors.log(data.selectedVars);
	}

	const objectSelectorTable = computed(() => {
		return props.includeHruOption && data.doHru ? `${props.table}_hru` : props.table;
	})

	onMounted(async () => await get())
</script>

<template>
	<div>
		<error-alert as-popup v-model="data.page.saveError" :show="data.page.saveError" :text="data.page.error" :timeout="-1"></error-alert>
		<success-alert v-model="data.page.saveSuccess" :show="data.page.saveSuccess"></success-alert>
		<success-alert v-model="data.page.copy.saveSuccess" :show="data.page.copy.saveSuccess" text="Your item has been copied."></success-alert>

		<v-form @submit.prevent="save">
			<div v-if="!data.page.bulk.show">
                <div class="form-group" v-if="!hideName">
					<v-text-field v-model="item.name" :rules="[constants.formRules.required, constants.formRules.nameLength]" 
						label="Name" hint="Must be unique"></v-text-field>
				</div>

				<div class="form-group" v-if="showDescription">
					<v-text-field v-model="item.description" label="Description (optional)"></v-text-field>
				</div>
            </div>
            <div v-else>
				<v-card v-if="includeHruOption">
					<v-card-text>
						<div class="mb-1">
							{{name}} objects can be associated with either routing units or HRUs.
							Only one type may be edited in bulk mode at a time.
						</div>
						<v-select v-model="data.doHru" 
							:items="[{value:null, text:'Choose a type...'},{value:false, text:'Find objects applied to routing units'},{value:true, text:'Find objects applied to HRUs'}]"
							item-title="text"
							item-value="value"></v-select>
					</v-card-text>
				</v-card>

                <object-selector v-if="!includeHruOption || data.doHru !== null"
                    :name="name" :table="objectSelectorTable" :is-hru="isHru || (includeHruOption && data.doHru)" :no-gis="noGis"
                    @change="bulkSelectionChange"></object-selector>
            </div>

			<page-loading :loading="data.page.loading"></page-loading>
            <v-table class="table-editor" density="compact" v-if="!data.page.loading">
				<thead>
					<tr class="bg-surface">
                        <th v-if="data.page.bulk.show" class="bg-secondary-tonal">
                            Apply
							<v-tooltip text="Check to apply changes to this field to the selected objects above">
								<template v-slot:activator="{ props }">
									<font-awesome-icon v-bind="props" :icon="['fas', 'question-circle']" class="text-muted"></font-awesome-icon>
								</template>
							</v-tooltip>
                        </th>
						<th v-if="data.hasDatasetItem" class="bg-secondary-tonal">
                            Dataset Value 
							<v-tooltip text="The value from your swatplus_datasets database for this record is shown in this column for comparison">
								<template v-slot:activator="{ props }">
									<font-awesome-icon v-bind="props" :icon="['fas', 'question-circle']" class="text-muted"></font-awesome-icon>
								</template>
							</v-tooltip>
                        </th>
						<th v-if="data.hasDatasetItem" class="bg-secondary-tonal">Your Value</th>
						<th v-else class="bg-secondary-tonal">Value</th>
                        <th class="bg-secondary-tonal">Description</th>
						<th class="bg-secondary-tonal">SWAT+ Variable</th>
						<th class="bg-secondary-tonal" v-if="!data.hasDatasetItem">Default</th>
						<th class="bg-secondary-tonal" v-if="showRange">Recommended Range</th>
					</tr>
				</thead>
				<tbody>
					<tr-var-editor v-for="(v, i) in props.vars" :key="i" :bulk-mode="data.page.bulk.show" @change="selectedVarChange"
						:id="'item_' + v.name" :required="!data.page.bulk.show" :show-range="showRange"
						v-model="item[v.name]" :value="item[v.name]"
						:var-def="v"
                        :show-datasets="data.hasDatasetItem" :dataset-value="data.hasDatasetItem ? data.datasetItem[v.name] : null"></tr-var-editor>
				</tbody>
			</v-table>

			<action-bar>
				<v-btn type="submit" :loading="data.page.saving" variant="flat" color="primary" class="mr-2">
					{{ data.page.bulk.show ? 'Save Bulk Changes' : 'Save Changes' }}
				</v-btn>
				<v-btn v-if="!hideCopy && isUpdate && !data.page.bulk.show" 
					@click="data.page.copy.show = true"
					type="button" variant="flat" color="info" class="mr-2">Copy</v-btn>
				<back-button></back-button>
				<div v-if="allowBulkEdit" class="ml-auto">
					<v-checkbox v-model="data.page.bulk.show" hide-details label="Edit multiple rows"></v-checkbox>
				</div>
			</action-bar>
		</v-form>

		<v-dialog v-model="data.page.copy.show" :max-width="constants.dialogSizes.md">
			<v-card title="Copy Item">
				<v-card-text>
					<error-alert :text="data.page.copy.error"></error-alert>	

					<p>
						Would you like to make a copy of this entry? Enter a name for the copy below. Once copied, you'll be redirected to the list of items.
					</p>

					<div class="form-group">
						<v-text-field v-model="data.page.copy.name" :rules="[constants.formRules.required, constants.formRules.nameLength]" 
							label="Name of item copy" hint="Must be unique"></v-text-field>
					</div>
				</v-card-text>
				<v-divider></v-divider>
				<v-card-actions>
					<v-btn :loading="data.page.copy.saving" @click="copy" color="primary" variant="text">Copy</v-btn>
					<v-btn @click="data.page.copy.show = false">Cancel</v-btn>
				</v-card-actions>
			</v-card>
		</v-dialog>
	</div>
</template>