<script setup lang="ts">
	import { reactive } from 'vue';
	import { useRouter } from 'vue-router';
	import { usePlugins } from '../../../../plugins';
	import ConnectForm from '../../../../components/ConnectForm.vue';
	const router = useRouter();
	const { api, constants, currentProject, errors, formatters, utilities } = usePlugins();

	interface Props {
		apiUrl: string,
		item: any,
		isUpdate?: boolean,
		allowBulkEdit?: boolean
	}

	const props = withDefaults(defineProps<Props>(), {
		apiUrl: '',
		item: { id: 0 },
		isUpdate: false,
		allowBulkEdit: false
	});

	let page:any = reactive({
		loading: true,
		error: null,
		validated: false,
		saving: false,
		saveSuccess: false,
		bulk: {
			show: false
		},
		redirectRoute: 'ReservoirsEdit',
		propCol: 'res',
		propFields: [
			'init_name', 'rel_name', 'hyd_name', 'sed_name', 'nut_name'
		],
		propDefs: [
			{ name: 'init_name', label: 'Initial Properties', section: 'Reservoirs / Initial', file: 'initial.res', db: 'initial_res', tableName: 'init_res', routeName: 'ReservoirsInitialEdit', apiUrl: 'reservoirs/initial'},
			{ name: 'hyd_name', label: 'Hydrology Properties', section: 'Reservoirs / Hydrology', file: 'hydrology.res', db: 'hydrology_res', tableName: 'hyd_res', routeName: 'ReservoirsHydrologyEdit', apiUrl: 'reservoirs/hydrology'},
			{ name: 'sed_name', label: 'Sediment Properties', section: 'Reservoirs / Sediment', file: 'sediment.res', db: 'sediment_res', tableName: 'sed_res', routeName: 'ReservoirsSedimentEdit', apiUrl: 'reservoirs/sediment'},
			{ name: 'nut_name', label: 'Nutrients Properties', section: 'Reservoirs / Nutrients', file: 'nutrients.res', db: 'nutrients_res', tableName: 'nut_res', routeName: 'ReservoirsNutrientsEdit', apiUrl: 'reservoirs/nutrients'},
			{ name: 'rel_name', label: 'Release Decision Table', section: 'Decision Tables / Reservoir Release', file: 'res_rel.dtl', db: 'd_table_dtl', tableName: 'res_rel.dtl', routeName: 'DecisionsEdit'}
		]
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
		page.saving = true;
		page.saveSuccess = false;
		page.validated = true;

		if (props.item.connect.elev === '') props.item.connect.elev = null;
		if (props.item.connect.wst_name === '') props.item.connect.wst_name = null;
		for (let field of page.propFields) {
			if (props.item.props[field] === '') props.item.props[field] = null;
		}

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
			}
		} else {
			let selectedVars = selected.connectVars.concat(selected.vars);
			if (selected.items.length < 1) {
				page.error = 'You must select at least one record to edit.';
			}
			else if (selectedVars.length < 1) {
				page.error = 'You must check at least one field to edit.';
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
</script>

<template>
	<div>
		<error-alert :text="page.error"></error-alert>
		<success-alert v-model="page.saveSuccess" :show="page.saveSuccess"></success-alert>

		<v-form @submit.prevent="save">
			<div v-if="page.bulk.show">
				<object-selector name="Reservoirs" table="res_con" @change="bulkSelectionChange"></object-selector>
			</div>
			
			<connect-form
				:item="item.connect" :item-outflow="item.outflow" :api-url="props.apiUrl" outflow-con-id-field="reservoir_con_id"
				:is-update="props.isUpdate" @change="connectVarsChange" @loaded="page.loading=false"
				:is-bulk-mode="page.bulk.show"></connect-form>

			<div v-if="!page.loading">
				<v-divider class="mb-6"></v-divider>

				<v-row>
					<v-col cols="12" md="6" v-for="p in page.propDefs" :key="p.name">
						<div class="form-group d-flex">
							<v-checkbox v-if="page.bulk.show" v-model="selected.vars" :value="p.name" class="flex-shrink-1 flex-grow-0"></v-checkbox>
							<auto-complete :label="p.label" class="flex-grow-1 flex-shrink-0"
								v-model="item.props[p.name]" :value="item.props[p.name]" :show-item-link="props.isUpdate"
								:table-name="p.tableName" :route-name="p.routeName"
								:section="p.section" :help-file="p.file" :help-db="p.db"
								:api-url="p.apiUrl"></auto-complete>
						</div>
					</v-col>
				</v-row>

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