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
		item: { wet_id: 0 },
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
			return api.put(`gwflow/wetland/${props.item.wet_id}`, data, currentProject.getApiHeader());
		else
			return api.post(`gwflow/wetland`, data, currentProject.getApiHeader());
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
					router.push({ name: 'GwflowWetlands' });
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
				<auto-complete label="Wetland" :disabled="props.isUpdate"
					:hint="props.isUpdate ? 'Wetland cannot be modified. Delete and recreate if wetland changes.' : ''"
					:persistant-hint="props.isUpdate"
					v-model="item.wet_name" :value="item.wet_name" :show-item-link="props.isUpdate"
					table-name="wet_res" route-name="ReservoirsWetlandsEdit" required
					section="Connections / Reservoirs / Wetlands" help-file="wetlands.wet" help-db="wetlands_wet"
					api-url="reservoirs/wetlands"></auto-complete>
			</div>

			<div class="form-group">
				<v-text-field v-model.number="item.thickness" :rules="[constants.formRules.required]" 
					label="Thickness of wetland bottom material (m)" type="number" step="any"></v-text-field>
			</div>

			<action-bar>
				<v-btn type="submit" :loading="page.saving" variant="flat" color="primary" class="mr-2">Save Changes</v-btn>
				<back-button></back-button>
			</action-bar>
		</v-form>
	</div>
</template>