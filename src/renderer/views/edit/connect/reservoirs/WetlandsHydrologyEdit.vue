<script setup lang="ts">
	import { reactive, onMounted, watch } from 'vue';
	import { useRoute } from 'vue-router';
	import { useHelpers } from '@/helpers';
	import EditForm from '@/components/EditForm.vue';

	const route = useRoute();
	const { api, currentProject, errors, utilities } = useHelpers();

	let data:any = reactive({
		paths: {
			data: 'reservoirs/wetlands-hydrology',
			vars: 'hydrology_wet'
		},
		page: {
			loading: false,
			error: null
		},
		item: {},
		vars: []
	});

	async function get() {
		if (route.params.id === undefined) return;
		data.page.loading = true;
		data.page.error = null;

		try {
			const response = await api.get(`${data.paths.data}/${route.params.id}`, currentProject.getApiHeader());
			data.item = response.data;

			const response2 = await api.get(`definitions/vars/${data.paths.vars}/${utilities.appPathUrl}`);
			data.vars = response2.data;
		} catch (error) {
			data.page.error = errors.logError(error, 'Unable to get project information from database.');
		}
			
		data.page.loading = false;
	}

	onMounted(async () => await get())
	watch(() => route.name, async () => await get())
	watch(() => route.params.id, async () => await get())
</script>

<template>
	<project-container :loading="data.page.loading" :load-error="data.page.error">
		<file-header input-file="hydrology.wet" docs-path="wetlands/hydrology.wet" use-io>
			<router-link to="/edit/cons/reservoirs">Reservoirs</router-link> / 
			<router-link to="/edit/cons/reservoirs/wetlands_hydrology">Wetland Hydrology</router-link>
			/ Edit
		</file-header>

		<edit-form show-range is-update allow-bulk-edit
			name="Wetlands" table="hyd_wet" is-hru
			:item="data.item" 
			:vars="data.vars" 
			api-url="reservoirs/wetlands-hydrology"
			redirect-route="ReservoirsWetlandsHydrology"></edit-form>
	</project-container>
</template>
