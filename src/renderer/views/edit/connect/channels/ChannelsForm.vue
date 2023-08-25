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
		}
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
		let item = props.item;
		
		if (item.connect.elev === '') item.connect.elev = null;
		if (item.connect.wst_name === '') item.connect.wst_name = null;
		if (item.props.init_name === '') item.props.init_name = null;
		if (item.props.hyd_name === '') item.props.hyd_name = null;
		if (item.props.nut_name === '') item.props.nut_name = null;

		if (!page.bulk.show) {
			let name = formatters.toValidName(item.connect.name);
			item.props.name = name;
			item.connect.name = name;

			if (props.isUpdate)
				item.connect.lcha_id = item.props.id;

			try {
				const response = await putPropsDb(item.props);
				if (!props.isUpdate)
					item.connect.lcha_id = response.data.id;
					
				const response2 = await putConnectDb(item.connect);
				page.validated = false;
				
				if (props.isUpdate)
					page.saveSuccess = true;
				else
					router.push({ name: 'ChannelsEdit', params: { id: response2.data.id } });
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
				for (let v of selected.vars) {
					item[v] = props.item.props[v];
				}
				
				try {
					errors.log(item);
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
				<object-selector name="Channels" table="chandeg_con" @change="bulkSelectionChange"></object-selector>
			</div>
			
			<connect-form
				:item="item.connect" :item-outflow="item.outflow" :api-url="props.apiUrl" outflow-con-id-field="chandeg_con_id"
				:is-update="props.isUpdate" @change="connectVarsChange" @loaded="page.loading=false"
				:is-bulk-mode="page.bulk.show"></connect-form>

			<div v-if="!page.loading">
				<v-divider class="mb-6"></v-divider>

				<v-row>
					<v-col cols="12" md="6">
						<div class="form-group d-flex">
							<v-checkbox v-if="page.bulk.show" v-model="selected.vars" value="init_name" class="flex-shrink-1 flex-grow-0"></v-checkbox>
							<auto-complete label="Initial Properties" class="flex-grow-1 flex-shrink-0"
								v-model="item.props.init_name" :value="item.props.init_name" :show-item-link="props.isUpdate"
								table-name="init_cha" route-name="ChannelsInitialEdit"
								section="Channels / Initial" help-file="initial.cha" help-db="initial_cha"
								api-url="channels/initial"></auto-complete>
						</div>
					</v-col>
					<v-col cols="12" md="6">
						<div class="form-group d-flex">
							<v-checkbox v-if="page.bulk.show" v-model="selected.vars" value="hyd_name" class="flex-shrink-1 flex-grow-0"></v-checkbox>
							<auto-complete label="Hydrology/Sediment Properties" class="flex-grow-1 flex-shrink-0"
								v-model="item.props.hyd_name" :value="item.props.hyd_name" :show-item-link="props.isUpdate"
								table-name="hyd_sed_lte_cha" route-name="ChannelsHydSedLteEdit"
								section="Hydrology &amp; Sediment" help-file="hyd-sed-lte.cha" help-db="hyd_sed_lte_cha"
								api-url="channels/hydsed"></auto-complete>
						</div>
					</v-col>
				</v-row>
				<v-row>
					<v-col cols="12" md="6">
						<div class="form-group d-flex">
							<v-checkbox v-if="page.bulk.show" v-model="selected.vars" value="nut_name" class="flex-shrink-1 flex-grow-0"></v-checkbox>
							<auto-complete label="Nutrients Properties" class="flex-grow-1 flex-shrink-0"
								v-model="item.props.nut_name" :value="item.props.nut_name" :show-item-link="props.isUpdate"
								table-name="nut_cha" route-name="ChannelsNutrientsEdit"
								section="Channels / Nutrients" help-file="nutrients.cha" help-db="nutrients_cha"
								api-url="channels/nutrients"></auto-complete>
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