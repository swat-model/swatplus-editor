<script setup lang="ts">
	import { reactive, onMounted, computed, watch } from 'vue';
	import { usePlugins } from '../plugins';
	const { api, constants, currentProject, errors, formatters, utilities } = usePlugins();

	interface Props {
		apiUrl: string,
		item: any,
		outflowConIdField: string,
		isUpdate?: boolean,
		isBulkMode?: boolean,
		itemOutflow: object[]
	}

	const props = withDefaults(defineProps<Props>(), {
		apiUrl: '',
		item: { id: 0 },
		outflowConIdField: '',
		isUpdate: false,
		isBulkMode: false,
		itemOutflow: () => [{id: 0}]
	});

	let page:any = reactive({
		loading: false,
		error: null
	});

	let selectedVars:string[] = reactive([]);

	let outflow:any = reactive({
		loading: false,
		error: null,
		fields: [
			{ key: 'edit', label: '', class: 'min' },
			{ key: 'order' },
			{ key: 'obj_typ', label: 'Type' },
			{ key: 'obj_name', label: 'Name' },
			{ key: 'hyd_typ', label: 'Hydrograph' },
			{ key: 'frac', label: 'Fraction' },
			{ key: 'delete', label: '', class: 'min' }
		],
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
			order: null,
			obj_typ: 'sdc',
			obj_id: null,
			hyd_typ: null,
			frac: null
		},
		obj_name: null,
		obj_typs: [],
		hyd_typs: [],
		list: props.itemOutflow
	});

	function getCodesDb(type:string) {
		return api.get(`definitions/codes/connect/${type}/${utilities.appPath}`);
	}

	async function get() {
		page.loading = true;
		page.error = null;

		try {
			const response = await getCodesDb('obj_typ');
			outflow.obj_typs = response.data;

			const response2 = await getCodesDb('hyd_typ');
			outflow.hyd_typs = response2.data;
		} catch (error) {
			page.error = errors.logError(error, 'Unable to get outflow codes from database.');
		}
		
		page.loading = false;
	}

	function add() {
		outflow.form.update = false;
		outflow.form.id = null;
		outflow.obj = {
			order: outflow.list.length + 1,
			obj_typ: 'sdc',
			obj_id: undefined,
			hyd_typ: undefined,
			frac: undefined
		};
		outflow.obj[props.outflowConIdField] = props.item.id;
		outflow.obj_name = undefined;
		outflow.form.show = true;
	}

	function edit(item:any) {
		outflow.form.update = true;
		outflow.form.id = item.id;
		outflow.obj = {
			order: item.order,
			obj_typ: item.obj_typ,
			obj_id: item.obj_id,
			hyd_typ: item.hyd_typ,
			frac: item.frac
		};
		outflow.obj[props.outflowConIdField] = props.item.id;
		outflow.obj_name = item.obj_name;
		outflow.form.show = true;
	}

	async function saveOutflow() {
		outflow.form.error = null;
		outflow.form.saving = true;
		outflow.form.validated = true;

		if (validateOutflow()) {
			try {
				const response = await utilities.getAutoCompleteId(constants.objTypeToConTable[outflow.obj.obj_typ], outflow.obj_name);
				outflow.obj.obj_id = response.data.id;
			} catch (error) {
				outflow.form.error = errors.logError(error, `Invalid object name, ${outflow.obj_name}. Please make sure the ${outflow.obj.obj_typ} exists in your database.`);
			}

			if (formatters.isNullOrEmpty(outflow.form.error)) {
				var action;
				if (outflow.form.update) {
					action = api.put(`${props.apiUrl}/out/${outflow.form.id}`, outflow.obj, currentProject.getApiHeader());
				} else {
					action = api.post(`${props.apiUrl}/out`, outflow.obj, currentProject.getApiHeader());
				}

				try {
					const response = await action;
					outflow.form.validated = false;
					outflow.form.show = false;
					await getOutflow();
				} catch (error) {
					outflow.form.error = errors.logError(error, 'Unable to save outflow to database.');
				}
			}
		} 
		
		outflow.form.saving = false;
	}

	function validateOutflow () {
		let valid = true;
		valid = valid && !formatters.isNullOrEmpty(outflow.obj.order);
		valid = valid && !formatters.isNullOrEmpty(outflow.obj.obj_typ);
		valid = valid && !formatters.isNullOrEmpty(outflow.obj_name);
		valid = valid && !formatters.isNullOrEmpty(outflow.obj.hyd_typ);
		valid = valid && !formatters.isNullOrEmpty(outflow.obj.frac);
		return valid;
	}

	function askDelete(id:any, name:any) {
		outflow.delete.id = id;
		outflow.delete.name = name;
		outflow.delete.show = true;
	}

	async function confirmDelete() {
		outflow.delete.error = undefined;
		outflow.delete.saving = true;

		try {
			const response = await api.delete(`${props.apiUrl}/out/${outflow.delete.id}`, currentProject.getApiHeader());
			outflow.delete.saving = false;
			outflow.delete.show = false;
			await getOutflow();
		} catch (error) {
			outflow.delete.error = errors.logError(error, 'Unable to delete from database.');
			outflow.delete.saving = false;
		}
	}

	async function getOutflow() {
		outflow.loading = true;
		outflow.error = null;

		try {
			const response = await api.get(`${props.apiUrl}/${props.item.id}`, currentProject.getApiHeader());
			outflow.list = response.data.con_outs;
		} catch (error) {
			outflow.error = errors.logError(error, 'Unable to get object from database.');
		}
			
		outflow.loading = false;
	}

	const emit = defineEmits(['change'])

	watch(selectedVars, async () => {
		emit('change', selectedVars);
	})

	onMounted(async () => await get());
</script>

<template>
	<div>{{ page.error }}</div>
	<project-container :loading="page.loading" :load-error="page.error">
		<v-row>
			<v-col cols="12" :md="isUpdate && !isBulkMode ? 7 : 12">
				<div class="form-group">
					<v-text-field v-model="item.name" :rules="[constants.formRules.required, constants.formRules.nameLength]" 
						label="Name" hint="Must be unique"></v-text-field>
				</div>

				<div class="form-group">
					<auto-complete label="Weather Station"
						v-model="item.wst_name" :value="item.wst_name" :show-item-link="props.isUpdate"
						table-name="wst" route-name="StationsEdit"
						section="Climate / Weather Stations" help-file="weather-sta.cli" help-db="weather_sta_cli"
						api-url="climate/stations"></auto-complete>
				</div>
			</v-col>
		</v-row>
	</project-container>
</template>