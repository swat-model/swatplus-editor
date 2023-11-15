<script setup lang="ts">
	import { reactive, onMounted, watch } from 'vue';
	import { useRoute } from 'vue-router';
	import { useHelpers } from '@/helpers';
	import HrusForm from './HrusForm.vue';

	const route = useRoute();
	const { api, currentProject, errors, utilities } = useHelpers();

	let data:any = reactive({
		apiUrl: 'hrus',
		page: {
			loading: false,
			error: null
		},
		item: {
			connect: {},
			props: {},
			outflow: []
		}
	});

	async function get() {
		if (route.params.id === undefined) return;
		data.page.loading = true;
		data.page.error = null;

		try {
			const response = await api.get(`${data.apiUrl}/items/${route.params.id}`, currentProject.getApiHeader());
			errors.log(response.data);

			data.item.connect = {
				id: response.data.id,
				name: response.data.name,
				area: response.data.area,
				lat: response.data.lat,
				lon: response.data.lon,
				elev: response.data.elev,
				wst_name: response.data.wst != null ? response.data.wst.name : ''
			};

			data.item.outflow = response.data.con_outs;

			const response2 = await api.get(`${data.apiUrl}/properties/${response.data.hru.id}`, currentProject.getApiHeader());

			data.item.props = {
				id: response2.data.id,
				name: response2.data.name,
				topo_name: utilities.setToNameProp(response2.data.topo),
				hyd_name: utilities.setToNameProp(response2.data.hydro),
				soil_name: utilities.setToNameProp(response2.data.soil),
				lu_mgt_name: utilities.setToNameProp(response2.data.lu_mgt),
				soil_plant_init_name: utilities.setToNameProp(response2.data.soil_plant_init),
				surf_stor: utilities.setToNameProp(response2.data.surf_stor),
				snow_name: utilities.setToNameProp(response2.data.snow),
				field_name: utilities.setToNameProp(response2.data.field),
				description: response2.data.description
			};
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
		<file-header input-file="hru.con" docs-path="hydrologic-response-units/hru-data.hru" use-io>
			<router-link to="/edit/cons/hrus">HRUs</router-link>
			/ Edit
		</file-header>

		<hrus-form :item="data.item" :api-url="data.apiUrl" is-update allow-bulk-edit></hrus-form>
	</project-container>
</template>