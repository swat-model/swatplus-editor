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
		if (route.name !== 'GwflowWetlands') return;
		data.page.loading = true;
		data.page.error = null;

		try {
			const response = await api.get(`gwflow/wetland-default`, currentProject.getApiHeader());
			errors.log(response.data);

			data.item = response.data;
		} catch (error) {
			data.page.error = errors.logError(error, 'Unable to get wetland properties from database.');
		}
		
		data.page.loading = false;
	}

	async function save() {
		data.page.saveError = null;
		data.page.saving = true;
		data.page.saveSuccess = false;
		
		try {
			await api.put(`gwflow/wetland-default`, data.item, currentProject.getApiHeader());
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
		<div v-if="$route.name == 'GwflowWetlands'">
			<file-header input-file="gwflow.wetland" docs-path="modflow" use-io>
				<router-link to="/edit/cons/gwflow">Groundwater Flow</router-link>
				/ Wetlands
			</file-header>

			<error-alert :text="data.page.error"></error-alert>
			<success-alert v-model="data.page.saveSuccess" :show="data.page.saveSuccess"></success-alert>

			<v-form @submit.prevent="save">
				<div class="form-group">
					<v-text-field v-model.number="data.item.wet_thickness" :rules="[constants.formRules.required]" 
						label="Default thickness of wetland bottom material (m)" type="number" step="any" 
						hint="Will be used for any wetlands not included in the table below.">
						<template v-slot:append>
							<v-btn type="submit" :loading="data.page.saving" variant="flat" color="primary">Save Changes</v-btn>
						</template>
					</v-text-field>
				</div>
			</v-form>
			
			<grid-view
				api-url="gwflow/wetland" :default-sort="['wet_id', 'asc']"
				use-dynamic-headers show-delete-all
				show-import-export default-csv-file="gwflow_wetlands.csv" table-name="gwflow_wetland" import-primary-key="wet_id">
			</grid-view>
		</div>
		<router-view></router-view>
	</project-container>
</template>
