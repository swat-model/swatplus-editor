<script setup lang="ts">
	import { reactive } from 'vue';
	import { useRouter } from 'vue-router';
	import { useHelpers } from '@/helpers';
	import TrVarEditor from '@/components/TrVarEditor.vue';
	import ConnectForm from '@/components/ConnectForm.vue';
	const router = useRouter();
	const { api, constants, currentProject, errors, formatters, utilities } = useHelpers();

	interface Props {
		apiUrl: string,
		item: any,
		isUpdate?: boolean,
		allowBulkEdit?: boolean,
		vars: any
	}

	const props = withDefaults(defineProps<Props>(), {
		apiUrl: '',
		item: { id: 0 },
		isUpdate: false,
		allowBulkEdit: false,
		vars: {}
	});

	let page:any = reactive({
		loading: true,
		error: null,
		validated: false,
		saving: false,
		saveSuccess: false,
		saveError: false,
		bulk: {
			show: false
		},
		redirectRoute: 'HrusLteEdit',
		propCol: 'lhru'
	});

	let selected:any = reactive({
		items: [],
		vars: [],
		connectVars: []
	});

	function putConnectDb(data:any) {
		if (props.isUpdate)
			return api.put(`${props.apiUrl}/items/${props.item.connect.id}`, data, currentProject.getApiHeader());
		else
			return api.post(`${props.apiUrl}/items`, data, currentProject.getApiHeader());
	}

	function putPropsDb(data:any) {
		if (props.isUpdate)
			return api.put(`${props.apiUrl}/properties/${props.item.props.id}`, data, currentProject.getApiHeader());
		else
			return api.post(`${props.apiUrl}/properties`, data, currentProject.getApiHeader());
	}

	async function save() {
		page.error = null;
		page.saveError = false;
		page.saveSuccess = false;
		page.saving = true;
		page.validated = true;

		if (props.item.connect.elev === '') props.item.connect.elev = null;
		if (props.item.connect.wst_name === '') props.item.connect.wst_name = null;

		if (!page.bulk.show) {
			let name = formatters.toValidName(props.item.connect.name);
			props.item.props.name = name;
			props.item.connect.name = name;

			if (props.isUpdate)
				props.item.connect[`${page.propCol}_id`] = props.item.props.id;

			try {
				const response = await putPropsDb(props.item.props);
				if (!props.isUpdate)
					props.item.connect[`${page.propCol}_id`] = response.data.id;
					
				const response2 = await putConnectDb(props.item.connect);
				page.validated = false;
				
				if (props.isUpdate)
				page.saveSuccess = true;
				else
					router.push({ name: page.redirectRoute, params: { id: response2.data.id } });
			} catch (error) {
				page.error = errors.logError(error, 'Unable to save changes to database.');
				page.saveError = true;
			}
		} else {
			let selectedVars = selected.connectVars.concat(selected.vars);
			if (selected.items.length < 1) {
				page.error = 'You must select at least one record to edit.';
				page.saveError = true;
			}
			else if (selectedVars.length < 1) {
				page.error = 'You must check at least one field to edit.';
				page.saveError = true;
			}
			else {
				let item:any = {};
				item.selected_ids = selected.items;
			
				for (let v of selected.connectVars) {
					item[v] = props.item.connect[v];
				}

				console.log(props.item);
				for (let v of selected.vars) {
					item[v] = props.item.props[v];
				}
				
				try {
					const response = await api.put(`${props.apiUrl}/properties/many`, item, currentProject.getApiHeader());
					page.validated = false;
					page.saveSuccess = true;
				} catch (error) {
					page.error = errors.logError(error, 'Unable to save changes to database.');
					page.saveError = true;
				}
			}
		}
		
		page.saving = false;
	}

	function bulkSelectionChange(selection:any) {
		selected.items = selection;
	}

	function connectVarsChange(selection:any) {
		selected.connectVars = selection;
	}

	function selectedVarChange(selection:any) {
		if (selection.value && !selected.vars.includes(selection.name)) {
			selected.vars.push(selection.name);
		}
		else if (!selection.value && selected.vars.includes(selection.name)) {
			selected.vars = selected.vars.filter(function(el:any) { return el !== selection.name });
		}
	}
</script>

<template>
	<div>
		<error-alert as-popup v-model="page.saveError" :show="page.saveError" :text="page.error" :timeout="-1"></error-alert>
		<success-alert v-model="page.saveSuccess" :show="page.saveSuccess"></success-alert>

		<v-form @submit.prevent="save">
			<div v-if="page.bulk.show">
				<object-selector name="HRUs" table="hru_lte_con" @change="bulkSelectionChange" is-hru></object-selector>
			</div>
			
			<connect-form
				:item="item.connect" :item-outflow="item.outflow" :api-url="props.apiUrl" outflow-con-id-field="hru_lte_con_id"
				:is-update="props.isUpdate" @change="connectVarsChange" @loaded="page.loading=false"
				:is-bulk-mode="page.bulk.show"></connect-form>

			<div v-if="!page.loading">
				<v-divider class="mb-6"></v-divider>

				<v-table class="table-editor" density="compact">
					<thead>
						<tr class="bg-surface">
							<th v-if="page.bulk.show" class="bg-secondary-tonal">
								Apply
								<v-tooltip text="Check to apply changes to this field to the selected objects above">
									<template v-slot:activator="{ props }">
										<font-awesome-icon v-bind="props" :icon="['fas', 'question-circle']" class="text-muted"></font-awesome-icon>
									</template>
								</v-tooltip>
							</th>
							<th class="bg-secondary-tonal">Value</th>
							<th class="bg-secondary-tonal">Description</th>
							<th class="bg-secondary-tonal">SWAT+ Variable</th>
							<th class="bg-secondary-tonal">Default</th>
							<th class="bg-secondary-tonal">Recommended Range</th>
						</tr>
					</thead>
					<tbody>
						<tr-var-editor v-for="(v, i) in props.vars" :key="i" :bulk-mode="page.bulk.show" @change="selectedVarChange"
							:id="'item_' + v.name" :required="!page.bulk.show" show-range
							v-model="item.props[v.name]" :value="item.props[v.name]"
							:var-def="v"></tr-var-editor>
					</tbody>
				</v-table>

				<error-alert :text="page.error" class="mt-4"></error-alert>

				<action-bar>
					<v-btn type="submit" :loading="page.saving" variant="flat" color="primary" class="mr-2">
						{{ page.bulk.show ? 'Save Bulk Changes' : 'Save Changes' }}
					</v-btn>
					<back-button></back-button>
					<div v-if="props.allowBulkEdit" class="ml-auto">
						<v-checkbox v-model="page.bulk.show" hide-details label="Edit multiple rows"></v-checkbox>
					</div>
				</action-bar>
			</div>
		</v-form>
	</div>
</template>
