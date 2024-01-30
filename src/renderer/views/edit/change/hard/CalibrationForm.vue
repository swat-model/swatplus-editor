<script setup lang="ts">
	import { reactive, onMounted, computed, watch } from 'vue';
	import { useRouter } from 'vue-router';
	import { useVuelidate } from '@vuelidate/core';
	import { numeric, required, requiredIf, helpers } from '@vuelidate/validators';
	import { useHelpers } from '@/helpers';

	const router = useRouter();
	const { api, constants, currentProject, errors, formatters, utilities } = useHelpers();

	interface Props {
		item: any,
		isUpdate?: boolean,
		initObjs?: any[],
		initConds?: any[],
		initialSelection?: any
	}

	const props = withDefaults(defineProps<Props>(), {
		item: { id: 0 },
		isUpdate: false,
		initObjs: () => <any[]>[],
		initConds: () => <any[]>[],
		initialSelection: {
			subbasins: [],
			landuse: [],
			soils: [],
			objects: [],
		}
	});

	const itemRules = computed(() => ({
		chg_typ: { required },
		chg_val: { required, numeric },
		soil_lyr1: { numeric, required: helpers.withMessage('Value is required', requiredIf(() => { return data.parmTypes.sol.includes(props.item.cal_parm_name) })) },
		soil_lyr2: { numeric, required: helpers.withMessage('Value is required', requiredIf(() => { return data.parmTypes.sol.includes(props.item.cal_parm_name) })) },
		yr1: { numeric, required: helpers.withMessage('Value is required', requiredIf(() => { return data.parmTypes.cli.includes(props.item.cal_parm_name) })) },
		yr2: { numeric, required: helpers.withMessage('Value is required', requiredIf(() => { return data.parmTypes.cli.includes(props.item.cal_parm_name) })) },
		day1: { numeric, required: helpers.withMessage('Value is required', requiredIf(() => { return data.parmTypes.cli.includes(props.item.cal_parm_name) })) },
		day2: { numeric, required: helpers.withMessage('Value is required', requiredIf(() => { return data.parmTypes.cli.includes(props.item.cal_parm_name) })) },
	}))
	const v$ = useVuelidate(itemRules, props.item);

	let data:any = reactive({
		page: {
			loading: true,
			error: null,
			saving: false,
			saveSuccess: false,
		},
		chgTypeOptions: [
			{ value: 'absval', title: 'Change the value of the parameter (absval)' },
			{ value: 'abschg', title: 'Change the value by the specified amount (abschg)' },
			{ value: 'pctchg', title: 'Change the value by the specified percent (pctchg)' }
		],
		conditionTypeOptions: [
			{ value: 'hsg', title: 'Hydrologic soil group' },
			{ value: 'texture', title: 'Texture' },
			{ value: 'landuse', title: 'Land use' },
			{ value: 'region', title: 'Region' }
		],
		conditionOperatorOptions: [
			{ value: '=', title: '=' },
			{ value: '>', title: '>' },
			{ value: '<', title: '<' }
		],
		parmTypes: {
			sol: [],
			cli: []
		},
		calObjects: props.initObjs,
		conditions: props.initConds,
		modal: {
			show: false,
			validate: false,
			saving: false,
			error: undefined,

			new: false,
			editIndex: 0,
			condition: {
				calibration_cal_id: props.item.id,
				cond_typ: 'landuse',
				cond_op: '=',
				cond_val: null,
				cond_val_text: null
			}
		}
	});

	function putDb(formData:any) {
		if (props.isUpdate)
			return api.put(`change/calibration/${props.item.id}`, formData, currentProject.getApiHeader());
		else
			return api.post(`change/calibration`, formData, currentProject.getApiHeader());
	}

	async function get() {
		data.page.loading = true;
		data.page.error = null;

		try {
			const response = await api.get(`change/cal_parms/types`, currentProject.getApiHeader());
			data.parmTypes = response.data;
		} catch (error) {
			data.page.error = errors.logError(error, 'Unable to load calibration parameters from database.');
		}

		data.page.loading = false;
	}

	async function save() {
		data.page.error = null;
		data.page.saving = true;
		data.page.saveSuccess = false;

		const valid = await v$.value.$validate();
		if (!valid) {
			data.page.error = 'Please fix the errors below and try again.';
		} else {
			let cal_parm_id = 0;			
			try {
				const response = await utilities.getAutoCompleteId('cal_parms', props.item.cal_parm_name);
				cal_parm_id = response.data.id;
			} catch (error) {
				data.page.error = errors.logError(error, 'Invalid parameter name, ' + props.item.cal_parm_name + '. Please make sure the calibration parameter exists in your database.');
			}

			if (formatters.isNullOrEmpty(data.page.error)) {
				let is_sol = data.parmTypes.sol.includes(props.item.cal_parm_name);
				let is_cli = data.parmTypes.cli.includes(props.item.cal_parm_name);
				let item:any = {
					cal_parm_id: cal_parm_id,
					chg_typ: props.item.chg_typ,
					chg_val: props.item.chg_val,
					soil_lyr1: is_sol ? props.item.soil_lyr1 : 0,
					soil_lyr2: is_sol ? props.item.soil_lyr2 : 0,
					yr1: is_cli ? props.item.yr1 : 0,
					yr2: is_cli ? props.item.yr2 : 0,
					day1: is_cli ? props.item.day1 : 0,
					day2: is_cli ? props.item.day2 : 0
				};

				if (props.isUpdate) {
					item.id = props.item.id;
					item.elements = data.calObjects;
					item.conditions = data.conditions;
				}

				try {
					const response = await putDb(item);
					data.page.validated = false;

					if (props.isUpdate)
						data.page.saveSuccess = true;
					else
						router.push({ name: 'HardCalibrationEdit', params: { id: response.data.id }});
				} catch (error) {
					data.page.error = errors.logError(error, 'Unable to save changes to database.');
				}
			}
		}

		data.page.saving = false;
	}

	function addCond() {
		data.modal.condition = {
			calibration_cal_id: props.item.id,
			cond_typ: 'landuse',
			cond_op: '=',
			cond_val: null,
			cond_val_text: null
		}
		data.modal.editIndex = 0;
		data.modal.new = true;
		data.modal.show = true;
	}
	
	function editCond(cond:any) {
		data.modal.condition = {
			calibration_cal_id: props.item.id,
			cond_typ: cond.cond_typ,
			cond_op: cond.cond_op,
			cond_val: cond.cond_val,
			cond_val_text: cond.cond_val_text
		}
		data.modal.editIndex = data.conditions.indexOf(cond);
		data.modal.new = false;
		data.modal.show = true;
	}
	
	function removeCond(cond:any) {
		data.conditions.splice(data.conditions.indexOf(cond), 1);
	}
	
	function saveCond() {
		if (data.modal.condition.cond_typ != 'region') {
			data.modal.condition.cond_val = null;
		} else {
			data.modal.condition.cond_val_text = null;
		}

		if (data.modal.new) {
			data.conditions.push(data.modal.condition);
		} else {
			data.conditions[data.modal.editIndex] = data.modal.condition;
		}

		data.modal.show = false;
	}

	const objTable = computed(() => {
		if (!props.isUpdate || !props.item.cal_parm || !props.item.cal_parm.obj_typ) return '';

		switch(props.item.cal_parm.obj_typ) {
			case 'hru': 
			case 'sol':
				return 'hru_con';
			case 'hlt':
				return 'hru_lte_con';
			case 'swq':
			case 'rte':
				return 'chandeg_con';
			case 'res':
				return 'res_con';
			case 'gw':
				return 'aqu_con';
			case 'cli':
				return 'wst';
			default: 
				return '';
		}
	});

	const objTableIsHru = computed(() => {
		if (!props.isUpdate || !props.item.cal_parm || !props.item.cal_parm.obj_typ) return false;

		switch(props.item.cal_parm.obj_typ) {
			case 'hru': 
			case 'sol':
			case 'hlt':
				return true;
			default: 
				return false;
		}
	});

	const objTableIsGis = computed(() => {
		if (!props.isUpdate || !props.item.cal_parm || !props.item.cal_parm.obj_typ) return false;

		switch(props.item.cal_parm.obj_typ) {
			case 'hru': 
			case 'sol':
			case 'hlt':
			case 'swq':
			case 'rte':
			case 'res':
			case 'gw':
				return true;
			default: 
				return false;
		}
	});

	function objectSelectionChange(selection:any) {
		data.calObjects = selection;
	}

	onMounted(async () => await get())
</script>

<template>
	<project-container :loading="data.page.loading">
		<error-alert :text="data.page.error"></error-alert>
		<success-alert v-model="data.page.saveSuccess" :show="data.page.saveSuccess"></success-alert>

		<v-form @submit.prevent="save">
			<div class="form-group">
				<auto-complete :label="`Calibration Parameter` + (props.isUpdate ? ' (Cannot Modify)' : '')" :disabled="props.isUpdate"
					v-model="item.cal_parm_name" :value="item.cal_parm_name" :show-item-link="props.isUpdate"
					table-name="cal_parms" route-name="HardCalibrationParmsEdit"
					section="Change / Calibration Parameters" help-file="cal_parms.cal" help-db="cal_parms_cal"
					api-url="change/cal_parms"></auto-complete>
			</div>

			<v-row>
				<v-col cols="12" md="6">
					<v-select label="Type of Change" 
						v-model="item.chg_typ" :items="data.chgTypeOptions"
						:error-messages="v$.chg_typ.$errors.map(e => e.$message).join(', ')"
						@input="v$.chg_typ.$touch" @blur="v$.chg_typ.$touch"></v-select>
				</v-col>
				<v-col cols="12" md="6">
					<v-text-field label="Value of Change"
						v-model.number="item.chg_val" type="number" step="any"
						:error-messages="v$.chg_val.$errors.map(e => e.$message).join(', ')"
						@input="v$.chg_val.$touch" @blur="v$.chg_val.$touch"></v-text-field>
				</v-col>
			</v-row>

			<v-row v-if="data.parmTypes.sol.includes(item.cal_parm_name)">
				<v-col cols="12" md="6">
					<v-text-field label="First Soil Layer to Apply Change"
						v-model.number="item.soil_lyr1" type="number" step="any"
						:error-messages="v$.soil_lyr1.$errors.map(e => e.$message).join(', ')"
						@input="v$.soil_lyr1.$touch" @blur="v$.soil_lyr1.$touch"></v-text-field>
				</v-col>
				<v-col cols="12" md="6">
					<v-text-field label="Last Soil Layer to Apply Change"
						v-model.number="item.soil_lyr2" type="number" step="any"
						:error-messages="v$.soil_lyr2.$errors.map(e => e.$message).join(', ')"
						@input="v$.soil_lyr2.$touch" @blur="v$.soil_lyr2.$touch"></v-text-field>
				</v-col>
			</v-row>

			<v-row v-if="data.parmTypes.cli.includes(item.cal_parm_name)">
				<v-col cols="12" md="3">
					<v-text-field label="First Year to Apply Change"
						v-model.number="item.yr1" type="number" 
						:error-messages="v$.yr1.$errors.map(e => e.$message).join(', ')"
						@input="v$.yr1.$touch" @blur="v$.yr1.$touch"></v-text-field>
				</v-col>
				<v-col cols="12" md="3">
					<v-text-field label="Last Year to Apply Change"
						v-model.number="item.yr2" type="number" 
						:error-messages="v$.yr2.$errors.map(e => e.$message).join(', ')"
						@input="v$.yr2.$touch" @blur="v$.yr2.$touch"></v-text-field>
				</v-col>
				<v-col cols="12" md="3">
					<v-text-field label="First Day to Apply Change"
						v-model.number="item.day1" type="number" min="1" max="366" 
						:error-messages="v$.day1.$errors.map(e => e.$message).join(', ')"
						@input="v$.day1.$touch" @blur="v$.day1.$touch"></v-text-field>
				</v-col>
				<v-col cols="12" md="3">
					<v-text-field label="Last Day to Apply Change"
						v-model.number="item.day2" type="number" min="1" max="366" 
						:error-messages="v$.day2.$errors.map(e => e.$message).join(', ')"
						@input="v$.day2.$touch" @blur="v$.day2.$touch"></v-text-field>
				</v-col>
			</v-row>

			<div v-if="isUpdate">
				<div v-if="item?.cal_parm?.obj_typ !== 'bsn'">
					<div>Select Objects to Calibrate</div>
					<object-selector v-if="!formatters.isNullOrEmpty(objTable)" hide-alert
						name="Objects" :table="objTable" :is-hru="objTableIsHru" :no-gis="!objTableIsGis" :initial-selection="props.initialSelection"
						@change="objectSelectionChange"></object-selector>
				</div>
				
				<div>Calibration Conditions</div>
				<v-alert type="info" variant="tonal" v-if="data.conditions.length < 1" class="my-3">
					This calibration does not have any conditions. 
					<a href="#" @click.prevent="addCond" class="text-primary pointer">Add now.</a>
				</v-alert>
				<v-card v-if="data.conditions.length > 0" class="my-3">				
					<v-table class="data-table" density="compact">
						<thead>
							<tr>
								<th class="min"></th>
								<th>Type</th>
								<th>Operator</th>
								<th>Value</th>
								<th class="min"></th>
							</tr>
						</thead>
						<tbody>
							<tr v-for="cond in data.conditions" :key="cond.calibration_cal_id">
								<td class="min"><a @click.prevent="editCond(cond)"><font-awesome-icon :icon="['fas', 'edit']" class="text-primary pointer" title="Edit" /></a></td>
								<td>{{cond.cond_typ}}</td>
								<td>{{cond.cond_op}}</td>
								<td>{{cond.cond_val == null ? cond.cond_val_text : cond.cond_val}}</td>
								<td class="min"><a @click.prevent="removeCond(cond)"><font-awesome-icon :icon="['fas', 'times']" class="text-error pointer" title="Delete" /></a></td>
							</tr>
						</tbody>
					</v-table>
				</v-card>
			</div>

			<div class="mt-3" v-if="!isUpdate">
				You will be able to set conditions and objects to which to apply the calibration after clicking save changes below.
			</div>

			<action-bar>
				<v-btn type="submit" :loading="data.page.saving" variant="flat" color="primary" class="mr-2">
					Save Changes
				</v-btn>
				<v-btn type="button" variant="flat" color="info" class="mr-2" v-if="isUpdate" @click="addCond">Add Condition</v-btn>
				<back-button></back-button>
			</action-bar>
		</v-form>

		<v-dialog v-model="data.modal.show" :max-width="constants.dialogSizes.lg">
			<v-card :title="(data.modal.new ? 'Add' : 'Edit') + ' Condition'">
				<v-card-text>
					<error-alert :text="data.modal.error"></error-alert>

					<div class="form-group">
						<v-select label="Type of Condition" v-model="data.modal.condition.cond_typ" :items="data.conditionTypeOptions"></v-select>
					</div>

					<div class="form-group">
						<v-select label="Condition Operator" v-model="data.modal.condition.cond_op" :items="data.conditionOperatorOptions"></v-select>
					</div>

					<div class="form-group">
						<v-text-field label="Value" v-if="data.modal.condition.cond_typ == 'region'" v-model.number="data.modal.condition.cond_val" type="number" step="any"></v-text-field>
						<v-text-field label="Value" v-else v-model="data.modal.condition.cond_val_text"></v-text-field>
					</div>
				</v-card-text>
				<v-divider></v-divider>
				<v-card-actions>
					<v-btn @click="saveCond" :loading="data.modal.saving" color="primary" variant="text">Save Changes</v-btn>
					<v-btn @click="data.modal.show = false">Cancel</v-btn>
				</v-card-actions>
			</v-card>
		</v-dialog>
	</project-container>
</template>