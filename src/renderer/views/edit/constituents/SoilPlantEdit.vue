<script setup lang="ts">
	import { reactive, onMounted, watch } from 'vue';
	import { useRoute } from 'vue-router';
	import { useHelpers } from '@/helpers';
	import SoilPlantForm from './SoilPlantForm.vue';

	const route = useRoute();
	const { api, currentProject, errors } = useHelpers();

	let data:any = reactive({
		page: {
			loading: false,
			error: null
		},
		item: {}
	});

	async function get() {
		if (route.params.id === undefined) return;
		data.page.loading = true;
		data.page.error = null;

		try {
			const response = await api.get(`init/soil_plant/${route.params.id}`, currentProject.getApiHeader());
			errors.log(response.data);

			data.item = {
				id: response.data.id,
				name: response.data.name,
				sw_frac: response.data.sw_frac,
				nutrients_name: response.data.nutrients != null ? response.data.nutrients.name : null,
				pest_name: response.data.pest != null ? response.data.pest.name : '',
				path_name: response.data.path != null ? response.data.path.name : '',
				hmet_name: response.data.hmet != null ? response.data.hmet.name : '',
				salt_name: response.data.salt != null ? response.data.salt.name : ''
			};
		} catch (error) {
			data.page.error = errors.logError(error, 'Unable to get properties from database.');
		}
		
		data.page.loading = false;
	}

	onMounted(async () => await get())
	watch(() => route.name, async () => await get())
	watch(() => route.params.id, async () => await get())
</script>

<template>
	<project-container :loading="data.page.loading" :load-error="data.page.error">
		<file-header input-file="soil_plant.ini" docs-path="constituents/soil_plant.ini" use-io>
			<router-link to="/edit/constituents/soil_plant">Soil Plant</router-link>
			/ Edit
		</file-header>

		<soil-plant-form is-update :item="data.item" allow-bulk-edit></soil-plant-form>
	</project-container>
</template>
