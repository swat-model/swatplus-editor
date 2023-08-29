<script setup lang="ts">
	import { reactive, computed } from 'vue';
	import { useRouter } from 'vue-router';
	import { usePlugins } from '../../../../plugins';
	const router = useRouter();
	const { api, constants, currentProject, errors, formatters, utilities } = usePlugins();

	interface Props {
		item: any,
		isUpdate?: boolean,
		objTypes?: []
	}

	const props = withDefaults(defineProps<Props>(), {
		item: { id: 0 },
		isUpdate: false,
		objTypes: () => []
	});

	let page:any = reactive({
		loading: true,
		error: null,
		validated: false,
		saving: false,
		saveSuccess: false
	});

	function putDb(data:any) {
		if (props.isUpdate)
			return api.put(`routing-units/elements/${props.item.id}`, data, currentProject.getApiHeader());
		else
			return api.post(`routing-units/elements`, data, currentProject.getApiHeader());
	}

	async function save() {
		page.error = null;
		page.saving = true;
		page.saveSuccess = false;
		page.validated = true;

		try {
			const response = await utilities.getAutoCompleteId(constants.objTypeToConTable[props.item.obj_typ], props.item.obj_name);
			props.item.obj_id = response.data.id;
		} catch (error) {
			page.error = errors.logError(error, 'Invalid object name, ' + props.item.obj_name + '. Please make sure the ' + props.item.obj_typ + ' exists in your database.');
		}

		try {
			const response = await utilities.getAutoCompleteId('rtu', props.item.rtu_name);
			props.item.rtu_id = response.data.id;
		} catch (error) {
			page.error = errors.logError(error, 'Invalid routing unit name, ' + props.item.rtu_name + '. Please make sure it exists in your database.');
		}

		if (!formatters.isNullOrEmpty(props.item.dlr_name)) {
			try {
				const response = await utilities.getAutoCompleteId('dlr', props.item.dlr_name);
				props.item.dlr_id = response.data.id;
			} catch (error) {
				page.error = errors.logError(error, 'Invalid delivery ratio name, ' + props.item.dlr_name + '. Please make sure it exists in your database.');
			}
		}

		if (formatters.isNullOrEmpty(page.error)) {
			let item:any = {
				name: formatters.toValidName(props.item.name),
				obj_typ: props.item.obj_typ,
				obj_id: props.item.obj_id,
				rtu_id: props.item.rtu_id,
				dlr_id: props.item.dlr_id,
				frac: props.item.frac
			};

			if (props.isUpdate) {
				item.id = props.item.id;
			}
			
			try {
				const response = await putDb(item);
				page.validated = false;

				if (props.isUpdate)
					page.saveSuccess = true;
				else
					router.push({ name: 'RoutingUnitsElements'});
			} catch (error) {
				page.error = errors.logError(error, 'Unable to save changes to database.');
			}
		}
		
		page.saving = false;
	}

	const objTable = computed(() => {
		if (formatters.isNullOrEmpty(props.item.obj_typ)) return '';
		if (props.item.obj_typ in constants.objTypeToConTable) return constants.objTypeToConTable[props.item.obj_typ];
		return '';
	})

	const objRoute = computed(() => {
		if (formatters.isNullOrEmpty(props.item.obj_typ)) return '';
		if (props.item.obj_typ in constants.objTypeRouteTable) return constants.objTypeRouteTable[props.item.obj_typ].name;
		return '';
	})
</script>

<template>
	<div>
		<error-alert :text="page.error"></error-alert>
		<success-alert v-model="page.saveSuccess" :show="page.saveSuccess"></success-alert>

		<v-form @submit.prevent="save">
			<div class="form-group">
				<v-text-field v-model="item.name" :rules="[constants.formRules.required, constants.formRules.nameLength]" 
					label="Name" hint="Must be unique"></v-text-field>
			</div>

			<div class="form-group">
				<auto-complete label="Assign to Routing Unit"
					v-model="item.rtu_name" :value="item.rtu_name" :show-item-link="props.isUpdate"
					table-name="rtu" route-name="RoutingUnitsEdit"
					section="Routing Units" help-file="rout_unit.con" help-db="rout_unit_con"
					api-url="routing-units/items"></auto-complete>
			</div>

			<v-row>
				<v-col cols="12" md="6">
					<div class="form-group">
						<v-select label="Object type" v-model="item.obj_typ" :items="objTypes" item-title="text" item-value="value" required @change="item.obj_name = null"></v-select>
					</div>
				</v-col>
				<v-col cols="12" md="6">
					<div class="form-group">
						<auto-complete label="Object name"
							v-model="item.obj_name" :value="item.obj_name" :show-item-link="false"
							:table-name="objTable" :route-name="objRoute"></auto-complete>
					</div>
				</v-col>
			</v-row>

			<div class="form-group">
				<v-text-field v-model="item.frac" :rules="[constants.formRules.required]" label="Fraction" type="number" step="any"></v-text-field>
			</div>

			<action-bar>
				<v-btn type="submit" :loading="page.saving" variant="flat" color="primary" class="mr-2">Save Changes</v-btn>
				<back-button></back-button>
			</action-bar>
		</v-form>
	</div>
</template>