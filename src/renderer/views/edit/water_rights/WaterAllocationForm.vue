<script setup lang="ts">
	import { reactive, computed, onMounted } from 'vue';
	import { useVuelidate } from '@vuelidate/core';
	import { numeric, required, maxLength } from '@vuelidate/validators';
	import { useRouter } from 'vue-router';
	import { useHelpers } from '@/helpers';

	const router = useRouter();
	const { api, constants, currentProject, errors, formatters, utilities } = useHelpers();

	interface Props {
		item: any,
		isUpdate?: boolean
	}

	const props = withDefaults(defineProps<Props>(), {
		item: { id: 0, layers: [] },
		isUpdate: false
	});

	let data:any = reactive({
		page: {
			error: <string|null>null,
			saving: false,
			saveSuccess: false
		},
		sources: {
			loading: false,
			sortBy: 'id',
			fields: [
				{ key: 'edit', title: '', class: 'min' },
				{ value: 'description', sortable: true },
				{ value: 'obj_typ', title: 'Type', sortable: true },
				{ value: 'obj_name', title: 'Object', sortable: true },
				{ value: 'limit_01', title: 'Jan', sortable: true, class: 'text-right' },
				{ value: 'limit_02', title: 'Feb', sortable: true, class: 'text-right' },
				{ value: 'limit_03', title: 'Mar', sortable: true, class: 'text-right' },
				{ value: 'limit_04', title: 'Apr', sortable: true, class: 'text-right' },
				{ value: 'limit_05', title: 'May', sortable: true, class: 'text-right' },
				{ value: 'limit_06', title: 'Jun', sortable: true, class: 'text-right' },
				{ value: 'limit_07', title: 'Jul', sortable: true, class: 'text-right' },
				{ value: 'limit_08', title: 'Aug', sortable: true, class: 'text-right' },
				{ value: 'limit_09', title: 'Sep', sortable: true, class: 'text-right' },
				{ value: 'limit_10', title: 'Oct', sortable: true, class: 'text-right' },
				{ value: 'limit_11', title: 'Nov', sortable: true, class: 'text-right' },
				{ value: 'limit_12', title: 'Dec', sortable: true, class: 'text-right' },
				{ key: 'delete', title: '' }
			],
			list: props.item.src_obs,
			delete: {
				show: false,
				id: null,
				name: null,
				error: null,
				saving: false
			},
			form: {
				show: false,
				id: null,
				validated: false,
				error: null,
				saving: false
			},
			obj: {
				water_allocation_id: props.item.id,
				description: null,
				obj_typ: 'cha',
				obj_id: 0,
				limit_01: 0,
				limit_02: 0,
				limit_03: 0,
				limit_04: 0,
				limit_05: 0,
				limit_06: 0,
				limit_07: 0,
				limit_08: 0,
				limit_09: 0,
				limit_10: 0,
				limit_11: 0,
				limit_12: 0
			},
			obj_name: null,
			obj_typs: [
				{ value: 'cha', text: 'Channel' },
				{ value: 'res', text: 'Reservoir' },
				{ value: 'aqu', text: 'Aquifer' },
				{ value: 'unl', text: 'Unlimited' }
			]
		},
		demands: {
			loading: false,
			sortBy: 'id',
			fields: [
				{ key: 'edit', title: '', class: 'min' },
				{ value: 'description', sortable: true },
				{ value: 'obj_typ', title: 'Type', sortable: true },
				{ value: 'obj_name', title: 'Object', sortable: true },
				{ value: 'obj_id', title: 'ID', sortable: true },
				{ value: 'withdr', title: 'Withdraw', sortable: true },
				{ value: 'amount', sortable: true, class: 'text-right' },
				{ value: 'right', title: 'Right', sortable: true },
				{ value: 'treat_typ', title: 'Treatment Type', sortable: true },
				{ value: 'treatment', sortable: true },
				{ value: 'rcv_obj', title: 'Rcv. Object Type', sortable: true },
				{ value: 'rcv_obj_name', title: 'Rcv. Object', sortable: true },
				{ value: 'rcv_dtl', title: 'Rcv. DTL', sortable: true },
				{ key: 'delete', title: '' }
			],
			list: props.item.dmd_obs,
			delete: {
				show: false,
				id: null,
				name: null,
				error: null,
				saving: false
			},
			form: {
				show: false,
				id: null,
				validated: false,
				error: null,
				saving: false
			},
			obj: {
				water_allocation_id: props.item.id,
				description: null,
				obj_typ: 'muni',
				obj_id: 0,
				withdr: 'ave_day',
				amount: 0,
				right: 'sr',
				treat_typ: null,
				treatment: null,
				rcv_obj: null,
				rcv_obj_id: 0,
				rcv_dtl: null
			},
			obj_name: null,
			rcv_obj_name: null,
			obj_typs: [
				{ value: 'hru', title: 'HRU' },
				{ value: 'muni', title: 'Municipal' },
				{ value: 'divert', title: 'Interbasin diversion' }
			],
			rcv_objs: [
				{ value: null, title: 'None' },
				{ value: 'cha', title: 'Channel' },
				{ value: 'res', title: 'Reservoir' },
				{ value: 'aqu', title: 'Aquifer' }
			],
			isEdit: false
		},
		demandSources: {
			loading: false,
			sortBy: 'id',
			fields: [
				{ key: 'edit', title: '', class: 'min' },
				{ key: 'src', title: 'Source', sortable: true },
				{ key: 'frac', sortable: true, class: 'text-right' },
				{ key: 'comp', sortable: true, class: 'text-right' },
				{ key: 'delete', title: '' }
			],
			list: [],
			delete: {
				show: false,
				id: null,
				name: null,
				error: null,
				saving: false
			},
			form: {
				show: false,
				id: null,
				validated: false,
				error: null,
				saving: false
			},
			obj: {
				water_allocation_dmd_ob_id: 0,
				src_id: null,
				frac: 0,
				comp: false
			}
		},
		objTypeToConWaterAllocation: {
			'hru': 'hru_con',
			'aqu': 'aqu_con',
			'cha': 'chandeg_con',
			'res': 'res_con',
			'unl': '',
			'muni': '',
			'divert': ''
		},
		objTypeRouteWaterAllocation: {
			'hru': { path: '/edit/hrus/edit/', name: 'HrusEdit' },
			'aqu': { path: '/edit/aquifers/edit/', name: 'AquifersEdit' },
			'cha': { path: '/edit/channels/edit/', name: 'ChannelsEdit' },
			'res': { path: '/edit/reservoirs/edit/', name: 'ReservoirsEdit' },
			'unl': { path: '#', name: '#' },
			'muni': { path: '#', name: '#' },
			'divert': { path: '#', name: '#' }
		}
	});

	const itemRules = computed(() => ({
		name: { required, maxLength: maxLength(constants.formNameMaxLength) },
		rule_typ: { required },
		cha_ob: {}
	}))
	const v$ = useVuelidate(itemRules, props.item);

	const sourceOptions = computed(() => {
		let options = [{ value: null, title: 'Select a source...' }];
		for (let src of data.sources.list) {
			options.push({ value: src.id, title: src.description })
		}
		return options;
	})

	function putDb(formData:any) {
		if (props.isUpdate)
			return api.put('water_rights/allocation/' + props.item.id, formData, currentProject.getApiHeader());
		else
			return api.post('water_rights/allocation/', formData, currentProject.getApiHeader());
	}

	function getDb() {
		return api.get('water_allocation/' + props.item.id, currentProject.getApiHeader());
	}
	
	function postSourceDb(formData:any) {
		return api.post('water_rights/source/', formData, currentProject.getApiHeader());
	}
	
	function putSourceDb(id:any, formData:any) {
		return api.put('water_rights/source/' + id, formData, currentProject.getApiHeader());
	}
	
	function deleteSourceDb(id:any) {
		return api.delete('water_rights/source/' + id, currentProject.getApiHeader());
	}
	
	function postDemandDb(formData:any) {
		return api.post('water_rights/demand/post/', formData, currentProject.getApiHeader());
	}
	
	function putDemandDb(id:any, formData:any) {
		return api.put('water_rights/demand/' + id, formData, currentProject.getApiHeader());
	}
	
	function deleteDemandDb(id:any) {
		return api.delete('water_rights/demand/' + id, currentProject.getApiHeader());
	}
	
	function postDemandSourceDb(formData:any) {
		return api.post('water_rights/demand-source/post/', formData, currentProject.getApiHeader());
	}
	
	function putDemandSourceDb(id:any, formData:any) {
		return api.put('water_rights/demand-source/' + id, formData, currentProject.getApiHeader());
	}
	
	function deleteDemandSourceDb(id:any) {
		return api.delete('water_rights/demand-source/' + id, currentProject.getApiHeader());
	}

	async function getData() {
		data.sources.loading = true;
		data.demands.loading = true;

		try {
			const response = await getDb();
			data.sources.list = response.data.src_obs;
			data.demands.list = response.data.dmd_obs;
		} catch (error) {
			data.page.error = errors.logError(error, 'Unable to get water allocation table data from database.');
		}

		data.sources.loading = false;
		data.demands.loading = false;
	}

	async function getDemand() {
		data.demandSources.loading = true;

		try {
			const response = await api.get('water_rights/demand/' + data.demands.form.id, currentProject.getApiHeader());
			data.demandSources.list = response.data.dmd_src_obs;
		} catch (error) {
			data.demandSources.error = errors.logError(error, 'Unable to get water allocation demand data from database.');
		}

		data.demandSources.loading = false;
	}

	function get() {
		data.sources.list = props.item.src_obs;
		data.demands.list = props.item.dmd_obs;
	}

	async function save() {
		data.page.error = null;
		data.page.saving = true;
		data.page.saveSuccess = false;

		const valid = await v$.value.$validate();
		if (!valid) {
			data.page.error = 'Please fix the errors below and try again.';
		} else {
			let formData:any = {
				name: formatters.toValidName(props.item.name),
				rule_typ: props.item.rule_typ,
				cha_ob: props.item.cha_ob
			};

			if (props.isUpdate) {
				formData.id = props.item.id;
			}
			
			try {
				let response = await putDb(data);
				errors.log(response.data);
				
				if (props.isUpdate)
					data.page.saveSuccess = true;
				else
					router.push({ name: 'WaterAllocationEdit', params: { id: response.data.id } });
			} catch (error) {
				data.page.error = errors.logError(error, 'Unable to save changes to database.');
			}
		}
		
		data.page.saving = false;
	}

	async function saveSource() {
		data.sources.form.error = null;
		data.sources.form.saving = true;
		data.sources.form.validated = true;

		if (validateSource()) {
			if (data.sources.obj.obj_typ !== 'unl') {
				try {
					const response = await utilities.getAutoCompleteId(data.objTypeToConWaterAllocation[data.sources.obj.obj_typ], data.sources.obj_name);
					data.sources.obj.obj_id = response.data.id;
				} catch (error) {
					data.sources.form.error = errors.logError(error, 'Invalid object name, ' + data.sources.obj_name + '. Please make sure the ' + data.sources.obj.obj_typ + ' exists in your database.');
				}
			}

			if (formatters.isNullOrEmpty(data.sources.form.error)) {
				let action;
				if (data.sources.form.update) {
					action = putSourceDb(data.sources.form.id, data.sources.obj);
				} else {
					action = postSourceDb(data.sources.obj);
				}

				try {
					await action;
					await getData();
					data.sources.form.validated = false;
					data.sources.form.show = false;
				} catch (error) {
					data.sources.form.error = errors.logError(error, 'Unable to save source object to database.');
				}
			}
		} 
		
		data.sources.form.saving = false;
	}

	function validateSource() {
		let valid = true;
		data.sources.obj.description = formatters.toValidName(data.sources.obj.description);
		if (data.sources.obj.obj_typ === 'unl') data.sources.obj.obj_id = 0;

		let keys = Object.keys(data.sources.obj);
		for (let k of keys) {
			valid = valid && !formatters.isNullOrEmpty(data.sources.obj[k]);
		}
		return valid;
	}

	function addSource() {
		data.sources.form.validated = false;			
		data.sources.form.update = false;
		data.sources.form.id = null;
		data.sources.obj = {
			water_allocation_id: props.item.id,
			description: null,
			obj_typ: 'cha',
			obj_id: 0,
			limit_01: 0,
			limit_02: 0,
			limit_03: 0,
			limit_04: 0,
			limit_05: 0,
			limit_06: 0,
			limit_07: 0,
			limit_08: 0,
			limit_09: 0,
			limit_10: 0,
			limit_11: 0,
			limit_12: 0
		};
		data.sources.form.show = true;
	}

	function editSource(item:any) {
		data.sources.form.update = true;
		data.sources.form.id = item.id;
		data.sources.obj = item;
		data.sources.obj.water_allocation_id = props.item.id;
		data.sources.obj_name = item.obj_name;
		data.sources.form.show = true;
	}

	function askSourceDelete(item:any) {
		data.sources.delete.id = item.id;
		data.sources.delete.name = 'source ' + item.description;
		data.sources.delete.show = true;
	}

	async function confirmDeleteSource() {
		data.sources.delete.error = null;
		data.sources.delete.saving = true;

		try {
			await deleteSourceDb(data.sources.delete.id);
			await getData();
			data.sources.delete.show = false;
		} catch (error) {
			data.sources.delete.error = errors.logError(error, 'Unable to delete from database.');
		}

		data.sources.delete.saving = false;
	}

	async function saveDemand() {
		data.demands.form.error = null;
		data.demands.form.saving = true;
		data.demands.form.validated = true;

		if (validateDemand()) {
			if (data.demands.obj.obj_typ === 'hru') {
				try {
					const response = await utilities.getAutoCompleteId(data.objTypeToConWaterAllocation[data.demands.obj.obj_typ], data.demands.obj_name);
					data.demands.obj.obj_id = response.data.id;
				} catch (error) {
					data.demands.form.error = errors.logError(error, 'Invalid object name, ' + data.demands.obj_name + '. Please make sure the ' + data.demands.obj.obj_typ + ' exists in your database.');
				}
			}
			if (data.demands.obj.rcv_obj !== null) {
				try {
					const response = await utilities.getAutoCompleteId(data.objTypeToConWaterAllocation[data.demands.obj.rcv_obj], data.demands.rcv_obj_name);
					data.demands.obj.rcv_obj_id = response.data.id;
				} catch (error) {
					data.demands.form.error = errors.logError(error, 'Invalid object name, ' + data.demands.rcv_obj_name + '. Please make sure the ' + data.demands.obj.rcv_obj + ' exists in your database.');
				}
			}

			if (formatters.isNullOrEmpty(data.demands.form.error)) {
				let action;
				if (data.demands.form.update) {
					action = putDemandDb(data.demands.form.id, data.demands.obj);
				} else {
					action = postDemandDb(data.demands.obj);
				}

				try {
					await action;
					await getData();
					data.demands.form.validated = false;
					data.demands.form.show = false;
				} catch (error) {
					data.demands.form.error = errors.logError(error, 'Unable to save demand object to database.');
				}
			}
		} 
		
		data.demands.form.saving = false;
	}
	
	function validateDemand() {
		var valid = true;
		data.demands.obj.description = formatters.toValidName(data.demands.obj.description);

		let keys = ['obj_typ', 'withdr', 'amount', 'right'];
		for (let k of keys) {
			valid = valid && !formatters.isNullOrEmpty(data.demands.obj[k]);
		}
		return valid;
	}
	
	function addDemand() {
		data.demands.form.validated = false;			
		data.demands.form.update = false;
		data.demands.form.id = null;
		data.demands.obj = {
			water_allocation_id: props.item.id,
			description: null,
			obj_typ: 'muni',
			obj_id: 0,
			withdr: 'ave_day',
			amount: 0,
			right: 'sr',
			treat_typ: null,
			treatment: null,
			rcv_obj: null,
			rcv_obj_id: 0,
			rcv_dtl: null
		};
		data.demands.isEdit = false;
		data.demandSources.list = [];
		data.demands.form.show = true;
	}
	
	function editDemand(item:any) {
		data.demands.form.update = true;
		data.demands.form.id = item.id;
		data.demands.obj = item;
		data.demands.obj.water_allocation_id = props.item.id;
		data.demands.obj_name = item.obj_name;
		data.demands.rcv_obj_name = item.rcv_obj_name;
		data.demands.isEdit = true;
		data.demandSources.list = item.dmd_src_obs;
		data.demands.form.show = true;
	}
	
	function askDemandDelete(item:any) {
		data.demands.delete.id = item.id;
		data.demands.delete.name = 'demand ' + item.description;
		data.demands.delete.show = true;
	}
	
	async function confirmDeleteDemand() {
		data.demands.delete.error = null;
		data.demands.delete.saving = true;

		try {
			await deleteDemandDb(data.demands.delete.id);
			await getData();
			data.demands.delete.show = false;
		} catch (error) {
			data.demands.delete.error = errors.logError(error, 'Unable to delete from database.');
		}

		data.demands.delete.saving = false;
	}
	
	async function saveDemandSource() {
		data.demandSources.form.error = null;
		data.demandSources.form.saving = true;
		data.demandSources.form.validated = true;

		if (validateDemandSource()) {
			let action;

			//Some kind of bug, I don't know why and don't have time to look into it.
			//data.demandSources.obj.frac = data.demandSources.obj.frac.toString();
			errors.log(data.demandSources.obj);

			if (data.demandSources.form.update) {
				action = putDemandSourceDb(data.demandSources.form.id, data.demandSources.obj);
			} else {
				action = postDemandSourceDb(data.demandSources.obj);
			}

			try {
				await action;
				await getDemand();
				data.demandSources.form.validated = false;
				data.demandSources.form.show = false;
			} catch (error) {
				data.demandSources.form.error = errors.logError(error, 'Unable to save demand source object to database.');
			}
		} 
		
		data.demandSources.form.saving = false;
	}
	
	function validateDemandSource() {
		let valid = true;

		let keys = ['src_id', 'frac', 'comp'];
		for (let k of keys) {
			valid = valid && !formatters.isNullOrEmpty(data.demandSources.obj[k]);
		}
		return valid;
	}
	
	function addDemandSource() {
		data.demandSources.form.validated = false;			
		data.demandSources.form.update = false;
		data.demandSources.form.id = null;
		data.demandSources.obj = {
			water_allocation_dmd_ob_id: data.demands.form.id,
			src_id: null,
			frac: 0,
			comp: false
		};
		data.demandSources.form.show = true;
	}
	
	function editDemandSource(item:any) {
		data.demandSources.form.update = true;
		data.demandSources.form.id = item.id;
		data.demandSources.obj = {
			id: item.id,
			water_allocation_dmd_ob_id: data.demands.form.id,
			src_id: item.src.id,
			frac: item.frac,
			comp: item.comp
		};
		data.demandSources.form.show = true;
	}
	
	function askDemandSourceDelete(item:any) {
		data.demandSources.delete.id = item.id;
		data.demandSources.delete.name = 'demand source';
		data.demandSources.delete.show = true;
	}
	
	async function confirmDeleteDemandSource() {
		data.demandSources.delete.error = null;
		data.demandSources.delete.saving = true;

		try {
			await deleteDemandSourceDb(data.demandSources.delete.id);
			await getDemand();
			data.demandSources.delete.show = false;
		} catch (error) {
			data.demandSources.delete.error = errors.logError(error, 'Unable to delete from database.');
		}

		data.demandSources.delete.saving = false;
	}

	onMounted(() => get())
</script>

<template>
	<div>
		<error-alert :text="data.page.error"></error-alert>
		<success-alert v-model="data.page.saveSuccess" :show="data.page.saveSuccess"></success-alert>
		
		<v-form @submit.prevent="save">
			<div class="form-group">
				<v-text-field v-model="item.name" 
					label="Name" hint="Must be unique"
					:error-messages="v$.name.$errors.map(e => e.$message).join(', ')"
					@input="v$.name.$touch" @blur="v$.name.$touch"></v-text-field>
			</div>

			<div class="form-group">
				<v-text-field v-model="item.rule_typ" 
					label="Rule type to allocate water"
					:error-messages="v$.rule_typ.$errors.map(e => e.$message).join(', ')"
					@input="v$.rule_typ.$touch" @blur="v$.rule_typ.$touch"></v-text-field>
			</div>

			<div class="my-3">
				<v-checkbox v-model="item.cha_ob" label="Is there a channel object?" hide-details></v-checkbox>
			</div>

			<div v-if="isUpdate">
				<h2 class="text-h5 my-3">Source Objects</h2>
				<div v-if="!data.sources.list || data.sources.list.length < 1" class="alert alert-primary">
					This table does not have any sources defined.  
					<a href="#" @click.prevent="addSource">Add now.</a>
				</div>
				<div v-if="data.sources.list && data.sources.list.length > 0">
					<v-card>
						<v-data-table class="data-table" density="compact"
							:items="data.sources.list" :items-per-page="-1"
							:headers="data.sources.fields">
							<template v-slot:item.edit="{ item }">
								<a href="#" class="text-decoration-none text-primary" title="Edit" @click.prevent="editSource(item)">
									<font-awesome-icon :icon="['fas', 'edit']"></font-awesome-icon>
								</a>
							</template>
							<template v-slot:item.delete="{ item }">
								<font-awesome-icon :icon="['fas', 'times']" class="text-error pointer" title="Delete" 
											@click="askSourceDelete(item)"></font-awesome-icon>
							</template>
							<template v-slot:bottom></template>
						</v-data-table>
					</v-card>
				</div>

				<h2 class="text-h5 my-3">Demand Objects</h2>
				<v-row>
					<v-col cols="12" md="6">
						<p>
							<strong>Demand.</strong> Demand can be irrigation demand from an hru, municipal demand, or demand to transfer to another source object (channel, reservoir, aquifer). For irrigation demand, the hru number, decision table for triggering irrigation, and irrigation depth (mm) are input. For municipal demand, a muni number is input. The user then has the option to input an average daily demand or a recall name that can be daily, monthly, or annual. For transfer demand, the trans number is input and the user can input an average daily demand or a decision table to specify demand.
						</p>
						<p>
							<strong>Treatment.</strong> Treatment is designed for municipal treatment plants or industrial plants that treat or change the water chemistry. There are 2 options – 1) recall where you can specify the amount of return flow and 2) delivery where you can specify the change in flow and chemistry.
						</p>
					</v-col>
					<v-col cols="12" md="6">
						<p>
							<strong>Receiving.</strong> This can be used to return the treated municipal water (point sources) or to transfer (divert) water to other objects. The simple option is the input the return object and number. Or a decision table can be input to condition the diversions to multiple objects. Inputting “lost” assumes the water is diverted out of the basin.
						</p>
						<p>
							<strong>Source Allocation.</strong> The sources are listed in order of selection and the fraction from each source is input. The other input is compensation – if other sources are not available, the current source may be allowed to compensate for the demand. The model goes through all sources in the order listed and allocates based on the fractions. The model loops through the sources again, checking to see if compensation is allowed.
						</p>
					</v-col>
				</v-row>

				<div v-if="!data.demands.list || data.demands.list.length < 1" class="alert alert-primary">
					This table does not have any demands defined.  
					<a href="#" @click.prevent="addSource">Add now.</a>
				</div>
				<div v-if="data.demands.list && data.demands.list.length > 0">
					<v-card>
						<v-data-table class="data-table" density="compact"
							:items="data.demands.list" :items-per-page="-1"
							:headers="data.demands.fields">
							<template v-slot:item.edit="{ item }">
								<a href="#" class="text-decoration-none text-primary" title="Edit" @click.prevent="editDemand(item)">
									<font-awesome-icon :icon="['fas', 'edit']"></font-awesome-icon>
								</a>
							</template>
							<template v-slot:item.delete="{ item }">
								<font-awesome-icon :icon="['fas', 'times']" class="text-error pointer" title="Delete" 
											@click="askDemandDelete(item)"></font-awesome-icon>
							</template>
							<template v-slot:bottom></template>
						</v-data-table>
					</v-card>
				</div>
			</div>

			<action-bar>
				<v-btn type="submit" :loading="data.page.saving" variant="flat" color="primary" class="mr-2">
					Save Changes
				</v-btn>
				<v-btn type="button" variant="flat" color="info" class="mr-2" v-if="isUpdate" @click="addSource">Add Source Object</v-btn>
				<v-btn type="button" variant="flat" color="info" class="mr-2" v-if="isUpdate" @click="addDemand">Add Demand Object</v-btn>
				<back-button></back-button>
			</action-bar>
		</v-form>

		<v-dialog v-model="data.sources.form.show" :max-width="constants.dialogSizes.lg">
			<v-card :title="(data.sources.form.update ? 'Update' : 'Add') + ' Source Object'">
				<v-card-text>
					<error-alert :text="data.sources.form.error"></error-alert>
					
					<v-form :validated="data.sources.form.validated">
						<div class="form-group">
							<v-text-field v-model="data.sources.obj.description" label="Name/Description of source object" required></v-text-field>
						</div>

						<v-row>
							<v-col cols="12" md="6">
								<div class="form-group">
									<v-select label="Object type" 
										v-model="data.sources.obj.obj_typ" :items="data.sources.obj_typs" 
										required @update:model-value="data.sources.obj_name = null"></v-select>
								</div>
							</v-col>
							<v-col cols="12" md="6">
								<div class="form-group" v-show="data.sources.obj.obj_typ !== 'unl'">
									<auto-complete label="Object name" class="flex-grow-1 flex-shrink-0"
										v-model="data.sources.obj_name" :value="data.sources.obj_name" :show-item-link="false" :required="data.sources.obj.obj_typ !== 'unl'"
										:table-name="constants.objTypeToConTable[data.sources.obj.obj_typ]" :route-name="constants.objTypeRouteTable[data.sources.obj.obj_typ].name"></auto-complete>
								</div>
							</v-col>
						</v-row>

						<v-divider class="my-3"></v-divider>

						<p class="mb-0">
							Minimum monthly values for object type:
						</p>
						<ul>
							<li>channel flow (m3/s)</li>
							<li>minimum reservoir level (fraction principal)</li>
							<li>maximum aquifer depth (m)</li>
						</ul>

						<v-row>
							<v-col>
								<div>
									<v-text-field label="January" type="number" step="any" v-model="data.sources.obj.limit_01" required></v-text-field>
								</div>
							</v-col>
							<v-col>
								<div>
									<v-text-field label="February" type="number" step="any" v-model="data.sources.obj.limit_02" required></v-text-field>
								</div>
							</v-col>
							<v-col>
								<div>
									<v-text-field label="March" type="number" step="any" v-model="data.sources.obj.limit_03" required></v-text-field>
								</div>
							</v-col>
							<v-col>
								<div>
									<v-text-field label="April" type="number" step="any" v-model="data.sources.obj.limit_04" required></v-text-field>
								</div>
							</v-col>
						</v-row>
						<v-row>
							<v-col>
								<div>
									<v-text-field label="May" type="number" step="any" v-model="data.sources.obj.limit_05" required></v-text-field>
								</div>
							</v-col>
							<v-col>
								<div>
									<v-text-field label="June" type="number" step="any" v-model="data.sources.obj.limit_06" required></v-text-field>
								</div>
							</v-col>
							<v-col>
								<div>
									<v-text-field label="July" type="number" step="any" v-model="data.sources.obj.limit_07" required></v-text-field>
								</div>
							</v-col>
							<v-col>
								<div>
									<v-text-field label="August" type="number" step="any" v-model="data.sources.obj.limit_08" required></v-text-field>
								</div>
							</v-col>
						</v-row>
						<v-row>
							<v-col>
								<div>
									<v-text-field label="September" type="number" step="any" v-model="data.sources.obj.limit_09" required></v-text-field>
								</div>
							</v-col>
							<v-col>
								<div>
									<v-text-field label="October" type="number" step="any" v-model="data.sources.obj.limit_10" required></v-text-field>
								</div>
							</v-col>
							<v-col>
								<div>
									<v-text-field label="November" type="number" step="any" v-model="data.sources.obj.limit_11" required></v-text-field>
								</div>
							</v-col>
							<v-col>
								<div>
									<v-text-field label="Descember" type="number" step="any" v-model="data.sources.obj.limit_12" required></v-text-field>
								</div>
							</v-col>
						</v-row>
					</v-form>
				</v-card-text>
				<v-divider></v-divider>
				<v-card-actions>
					<v-btn @click="saveSource" :loading="data.sources.form.saving" color="primary" variant="text">Save Changes</v-btn>
					<v-btn @click="data.sources.form.show = false">Cancel</v-btn>
				</v-card-actions>
			</v-card>
		</v-dialog>

		<v-dialog v-model="data.sources.delete.show" :max-width="constants.dialogSizes.md">
			<v-card title="Confirm delete">
				<v-card-text>
					<error-alert :text="data.sources.delete.error"></error-alert>

					<p>
						Are you sure you want to delete <strong>{{data.sources.delete.name}}</strong>?
						This action is permanent and cannot be undone. 
					</p>
				</v-card-text>
				<v-divider></v-divider>
				<v-card-actions>
					<v-btn @click="confirmDeleteSource" :loading="data.sources.delete.saving" color="error" variant="text">Delete</v-btn>
					<v-btn @click="data.sources.delete.show = false">Cancel</v-btn>
				</v-card-actions>
			</v-card>
		</v-dialog>

		<v-dialog v-model="data.demands.form.show" :max-width="constants.dialogSizes.lg">
			<v-card :title="(data.demands.form.update ? 'Update' : 'Add') + ' Demand Object'">
				<v-card-text>
					<error-alert :text="data.demands.form.error"></error-alert>
					
					<v-form :validated="data.demands.form.validated">
						<div class="form-group">
							<v-text-field v-model="data.demands.obj.description" label="Name/Description of demand object" required></v-text-field>
						</div>

						<v-row>
							<v-col cols="12" md="6">
								<div class="form-group">
									<v-select label="Object type" 
										v-model="data.demands.obj.obj_typ" :items="data.demands.obj_typs" 
										required @update:model-value="data.demands.obj_name = null"></v-select>
								</div>
							</v-col>
							<v-col cols="12" md="6">
								<div class="form-group" v-show="data.demands.obj.obj_typ === 'hru'">
									<auto-complete label="Object name" class="flex-grow-1 flex-shrink-0"
										v-model="data.demands.obj_name" :value="data.demands.obj_name" :show-item-link="false" :required="data.demands.obj.obj_typ === 'hru'"
										:table-name="constants.objTypeToConTable[data.demands.obj.obj_typ]" :route-name="constants.objTypeRouteTable[data.demands.obj.obj_typ].name"></auto-complete>
								</div>
								<div class="form-group" v-show="data.demands.obj.obj_typ === 'hru'">
									<v-text-field type="number" v-model="data.demands.obj.obj_id" :required="data.demands.obj.obj_typ !== 'hru'"></v-text-field>
								</div>
							</v-col>
						</v-row>

						<v-divider class="my-3"></v-divider>
					</v-form>
				</v-card-text>
				<v-divider></v-divider>
				<v-card-actions>
					<v-btn @click="saveDemand" :loading="data.demands.form.saving" color="primary" variant="text">Save Changes</v-btn>
					<v-btn @click="data.demands.form.show = false">Cancel</v-btn>
				</v-card-actions>
			</v-card>
		</v-dialog>

		<v-dialog v-model="data.demands.delete.show" :max-width="constants.dialogSizes.md">
			<v-card title="Confirm delete">
				<v-card-text>
					<error-alert :text="data.demands.delete.error"></error-alert>

					<p>
						Are you sure you want to delete <strong>{{data.demands.delete.name}}</strong>?
						This action is permanent and cannot be undone. 
					</p>
				</v-card-text>
				<v-divider></v-divider>
				<v-card-actions>
					<v-btn @click="confirmDeleteDemand" :loading="data.demands.delete.saving" color="error" variant="text">Delete</v-btn>
					<v-btn @click="data.demands.delete.show = false">Cancel</v-btn>
				</v-card-actions>
			</v-card>
		</v-dialog>

		<v-dialog v-model="data.demandSources.form.show" :max-width="constants.dialogSizes.lg">
			<v-card :title="(data.demandSources.form.update ? 'Update' : 'Add') + ' Demand Source Object'">
				<v-card-text>
					<error-alert :text="data.demandSources.form.error"></error-alert>
					
					<v-form :validated="data.demandSources.form.validated">
						
					</v-form>
				</v-card-text>
				<v-divider></v-divider>
				<v-card-actions>
					<v-btn @click="saveDemandSource" :loading="data.demandSources.form.saving" color="primary" variant="text">Save Changes</v-btn>
					<v-btn @click="data.demandSources.form.show = false">Cancel</v-btn>
				</v-card-actions>
			</v-card>
		</v-dialog>

		<v-dialog v-model="data.demandSources.delete.show" :max-width="constants.dialogSizes.md">
			<v-card title="Confirm delete">
				<v-card-text>
					<error-alert :text="data.demandSources.delete.error"></error-alert>

					<p>
						Are you sure you want to delete <strong>{{data.demandSources.delete.name}}</strong>?
						This action is permanent and cannot be undone. 
					</p>
				</v-card-text>
				<v-divider></v-divider>
				<v-card-actions>
					<v-btn @click="confirmDeleteDemandSource" :loading="data.demandSources.delete.saving" color="error" variant="text">Delete</v-btn>
					<v-btn @click="data.demandSources.delete.show = false">Cancel</v-btn>
				</v-card-actions>
			</v-card>
		</v-dialog>
	</div>
</template>
