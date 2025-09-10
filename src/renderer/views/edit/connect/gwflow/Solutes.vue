<script setup lang="ts">
	import { reactive, onMounted, watch } from 'vue';
	import { useRoute } from 'vue-router';
	import { useHelpers } from '@/helpers';
	const route = useRoute();

	const { api, currentProject, errors, constants } = useHelpers();

	let data:any = reactive({
		page: {
			loading: false,
			error: null,
			saving: false,
			saveSuccess: false,
			saveError: null
		},
		item: {}
	});

	async function get() {
		if (route.name !== 'GwflowSolutes') return;
		data.page.loading = true;
		data.page.error = null;

		try {
			const response = await api.get(`gwflow/solutes-default`, currentProject.getApiHeader());
			errors.log(response.data);

			data.item = response.data;
		} catch (error) {
			data.page.error = errors.logError(error, 'Unable to get solutes properties from database.');
		}
		
		data.page.loading = false;
	}

	async function save() {
		data.page.saveError = null;
		data.page.saving = true;
		data.page.saveSuccess = false;
		
		try {
			await api.put(`gwflow/solutes-default`, data.item, currentProject.getApiHeader());
			data.page.saveSuccess = true;
		} catch (error) {
			data.page.saveError = errors.logError(error, 'Unable to save changes to database.');
		}
		
		data.page.saving = false;
	}

	onMounted(async () => await get())
	watch(() => route.name, async () => await get())
</script>

<template>
	<project-container :loading="data.page.loading" :load-error="data.page.error">
		<div v-if="route.name == 'GwflowSolutes'">
			<file-header input-file="gwflow.solutes" docs-path="modflow" use-io>
				<router-link to="/edit/cons/gwflow">Groundwater Flow</router-link>
				/ Solutes
			</file-header>

			<error-alert :text="data.page.error"></error-alert>
			<success-alert v-model="data.page.saveSuccess" :show="data.page.saveSuccess"></success-alert>

			<v-form @submit.prevent="save">
				<div>
					<v-text-field v-model.number="data.item.transport_steps" :rules="[constants.formRules.required]" 
						label="Number of transport time steps for flow time step" type="number" step="any"></v-text-field>
				</div>

				<div>
					<v-text-field v-model.number="data.item.disp_coef" :rules="[constants.formRules.required]" 
						label="Dispersion coefficient (m2/day)" type="number" step="any"></v-text-field>
				</div>

				<div class="mb-6">
					<v-btn type="submit" :loading="data.page.saving" variant="flat" color="primary">Save Changes</v-btn>
				</div>
			</v-form>
			
			<grid-view auto-height
				api-url="gwflow/solutes" :default-sort="['solute_name', 'asc']"
				use-dynamic-headers hide-create hide-delete
				table-name="gwflow_solutes" import-primary-key="solute_name" />
		</div>
		<router-view></router-view>
	</project-container>
</template>
