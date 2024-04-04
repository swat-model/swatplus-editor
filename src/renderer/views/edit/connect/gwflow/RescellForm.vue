<script setup lang="ts">
	import { reactive, onMounted, computed, watch } from 'vue';
	import { useRouter } from 'vue-router';
	import { useHelpers } from '@/helpers';

	const router = useRouter();
	const { api, constants, currentProject, errors, formatters, utilities } = useHelpers();

	interface Props {
		item: any,
		isUpdate?: boolean
	}

	const props = withDefaults(defineProps<Props>(), {
		apiUrl: '',
		item: { cell_id: 0 },
		isUpdate: false
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
			return api.put(`gwflow/rescell/${props.item.cell_id}`, data, currentProject.getApiHeader());
		else
			return api.post(`gwflow/rescell`, data, currentProject.getApiHeader());
	}

	async function save() {
		page.error = null;
		page.saving = true;
		page.saveSuccess = false;
		page.validated = true;
		let val_error = false;
		
		if (!val_error) {
			try {
				const response = await putDb(props.item);

				if (props.isUpdate)
					page.saveSuccess = true;
				else
					router.push({ name: 'GwflowRescell' });
			} catch (error) {
				page.error = errors.logError(error, 'Unable to save changes to database.');
			}
		}
		
		page.saving = false;
		page.validated = false;
	}
</script>

<template>
	<div>
		<error-alert :text="page.error"></error-alert>
		<success-alert v-model="page.saveSuccess" :show="page.saveSuccess"></success-alert>

		<v-form @submit.prevent="save">
			<div class="form-group">
				<v-text-field v-model.number="item.cell_id" :rules="[constants.formRules.required]" :readonly="props.isUpdate"
					label="Cell ID #" type="number" :hint="`Cell must be active or it will be ignored. ${props.isUpdate ? 'Cell ID cannot be modified. Delete and recreate if ID changes.' : ''}`" persistent-hint></v-text-field>
			</div>

			<div class="form-group">
				<auto-complete label="Reservoir"
					v-model="item.res_name" :value="item.res_name" :show-item-link="props.isUpdate"
					table-name="reservoir_con" route-name="ReservoirsEdit" required
					section="Connections / Reservoirs" help-file="reservoir.con" help-db="reservoir_con"
					api-url="reservoirs/items"></auto-complete>
			</div>

			<div class="form-group">
				<v-text-field v-model.number="item.res_stage" :rules="[constants.formRules.required]" 
					label="Reservoir Stage (m)" type="number" step="any"></v-text-field>
			</div>

			<action-bar>
				<v-btn type="submit" :loading="page.saving" variant="flat" color="primary" class="mr-2">Save Changes</v-btn>
				<back-button></back-button>
			</action-bar>
		</v-form>
	</div>
</template>