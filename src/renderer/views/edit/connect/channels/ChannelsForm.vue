<script setup lang="ts">
	import { reactive, onMounted, computed, watch } from 'vue';
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
					item[v] = item.connect[v];
				}
				for (let v of selected.vars) {
					item[v] = item.props[v];
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
		<v-snackbar v-model="page.saveSuccess" :timeout="2000">
			Changes saved!
			<template v-slot:actions>
				<v-btn color="primary" variant="text" @click="page.saveSuccess = false">Close</v-btn>
			</template>
		</v-snackbar>

		<v-form @submit.prevent="save">
			<connect-form
				:item="item.connect" :item-outflow="item.outflow" :api-url="props.apiUrl" outflow-con-id-field="chandeg_con_id"
				:is-update="props.isUpdate" @change="connectVarsChange"
				:is-bulk-mode="page.bulk.show"></connect-form>

			<auto-complete label="Initial Properties"
				v-model="item.props.init_name" :value="item.props.init_name" :show-item-link="props.isUpdate"
				table-name="init_cha" route-name="ChannelsInitialEdit"
				section="Channels / Initial" help-file="initial.cha" help-db="initial_cha"
				api-url="channels/initial"></auto-complete>
		</v-form>
	</div>
</template>