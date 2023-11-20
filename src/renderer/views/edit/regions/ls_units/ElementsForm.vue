<script setup lang="ts">
	import { reactive, computed } from 'vue';
	import { useVuelidate } from '@vuelidate/core';
	import { numeric, required } from '@vuelidate/validators';
	import { useRouter } from 'vue-router';
	import { useHelpers } from '@/helpers';

	const router = useRouter();
	const { api, constants, currentProject, errors, formatters, utilities } = useHelpers();

	interface Props {
		item: any,
		isUpdate?: boolean,
		objTypes: any[]
	}

	const props = withDefaults(defineProps<Props>(), {
		item: { id: 0 },
		isUpdate: false,
		objTypes: () => []
	});

	let page:any = reactive({
		loading: true,
		error: <string|null>null,
		saving: false,
		saveSuccess: false,
		
	});

	const itemRules = computed(() => ({
		name: { required },
		ls_unit_def_name: { required },
		obj_typ: { required },
		obj_name: { required },
		bsn_frac: { required, numeric },
		sub_frac: { required, numeric },
		reg_frac: { required, numeric }
	}))
	const v$ = useVuelidate(itemRules, props.item);

	function putDb(data:any) {
		if (props.isUpdate)
			return api.put(`regions/ls_units/elements/${props.item.id}`, data, currentProject.getApiHeader());
		else
			return api.post(`regions/ls_units/elements`, data, currentProject.getApiHeader());
	}

	async function save() {
		page.error = null;
		page.saving = true;
		page.saveSuccess = false;

		const valid = await v$.value.$validate();
		if (!valid) {
			page.error = 'Please enter a value for all fields and try again.';
		} else {
			try {
				const response = await utilities.getAutoCompleteId(constants.objTypeToConTable[props.item.obj_typ], props.item.obj_name);
				props.item.obj_typ_no = response.data.id;
			} catch (error) {
				page.error = errors.logError(error, 'Invalid object name, ' + props.item.obj_name + '. Please make sure the ' + props.item.obj_typ + ' exists in your database.');
			}

			if (formatters.isNullOrEmpty(page.error)) {
				try {
					const response = await utilities.getAutoCompleteId('ls_unit_def', props.item.ls_unit_def_name);
					props.item.ls_unit_def_id = response.data.id;
				} catch (error) {
					page.error = errors.logError(error, 'Invalid landscape unit name, ' + props.item.ls_unit_def_name + '. Please make sure it exists in your database.');
				}
			}

			if (formatters.isNullOrEmpty(page.error)) {
				let data:any = {
					name: formatters.toValidName(props.item.name),
					obj_typ: props.item.obj_typ,
					obj_typ_no: props.item.obj_typ_no,
					ls_unit_def_id: props.item.ls_unit_def_id,
					bsn_frac: props.item.bsn_frac,
					sub_frac: props.item.sub_frac,
					reg_frac: props.item.reg_frac
				};

				if (props.isUpdate) {
					data.id = props.item.id;
				}
				
				try {
					const response = await putDb(data);
					
					if (props.isUpdate)
						page.saveSuccess = true;
					else
						router.push({ name: 'LandscapeUnitsElementsEdit', params: { id: response.data.id } });
				} catch (error) {
					page.error = errors.logError(error, 'Unable to save changes to database.');
				}
			}
		}

		page.saving = false;
	}
</script>

<template>
	<div>
		<error-alert :text="page.error"></error-alert>
		<success-alert v-model="page.saveSuccess" :show="page.saveSuccess"></success-alert>
		
		<v-form @submit.prevent="save">
			<v-row>
				<v-col cols="12" md="6">
					<div class="form-group">
						<v-text-field v-model="item.name" 
							label="Name" hint="Must be unique"
							:error-messages="v$.name.$errors.map(e => e.$message).join(', ')"
							@input="v$.name.$touch" @blur="v$.name.$touch"></v-text-field>
					</div>
				</v-col>
				<v-col cols="12" md="6">
					<div class="form-group">
						<auto-complete label="Assign to Landscape Unit"
							v-model="item.ls_unit_def_name" :value="item.ls_unit_def_name" :show-item-link="props.isUpdate"
							table-name="ls_unit_def" route-name="LandscapeUnitsEdit"
							section="Regions / Landscape Units" help-file="ls_unit.def" help-db="ls_unit_def"
							api-url="regions/ls_units"></auto-complete>
					</div>
				</v-col>
			</v-row>

			<v-row>
				<v-col cols="12" md="6">
					<div class="form-group">
						<v-select label="Object Type" v-model="item.obj_typ" :items="objTypes" 
							item-title="text" item-value="value" required
							:error-messages="v$.obj_typ.$errors.map(e => e.$message).join(', ')"
							@input="v$.obj_typ.$touch" @blur="v$.obj_typ.$touch"></v-select>
					</div>
				</v-col>
				<v-col cols="12" md="6">
					<div class="form-group">
						<auto-complete :label="formatters.toUpperFirstLetter(item.obj_typ) + ' object name'"
							v-model="item.obj_name" :value="item.obj_name"
							:table-name="constants.objTypeToConTable[item.obj_typ]"></auto-complete>
					</div>
				</v-col>
			</v-row>

			<v-row>
				<v-col cols="12" md="4">
					<div class="form-group">
						<v-text-field v-model.number="item.bsn_frac" type="number" step="any" min="0" max="1"
							label="Basin Fraction"
							:error-messages="v$.bsn_frac.$errors.map(e => e.$message).join(', ')"
							@input="v$.bsn_frac.$touch" @blur="v$.bsn_frac.$touch"></v-text-field>
					</div>
				</v-col>
				<v-col cols="12" md="4">
					<div class="form-group">
						<v-text-field v-model.number="item.sub_frac" type="number" step="any" min="0" max="1"
							label="Subbasin Fraction"
							:error-messages="v$.sub_frac.$errors.map(e => e.$message).join(', ')"
							@input="v$.sub_frac.$touch" @blur="v$.sub_frac.$touch"></v-text-field>
					</div>
				</v-col>
				<v-col cols="12" md="4">
					<div class="form-group">
						<v-text-field v-model.number="item.reg_frac" type="number" step="any" min="0" max="1"
							label="Region Fraction"
							:error-messages="v$.reg_frac.$errors.map(e => e.$message).join(', ')"
							@input="v$.reg_frac.$touch" @blur="v$.reg_frac.$touch"></v-text-field>
					</div>
				</v-col>
			</v-row>

			<action-bar>
				<v-btn type="submit" :loading="page.saving" variant="flat" color="primary" class="mr-2">
					Save Changes
				</v-btn>
				<back-button />
			</action-bar>
		</v-form>
	</div>
</template>
