<script setup lang="ts">
	import { reactive, onMounted, watch } from 'vue';
	import { useRoute } from 'vue-router';
	import { usePlugins } from '../../../../plugins';
	import ReservoirsForm from './ReservoirsForm.vue';

	const route = useRoute();
	const { api, currentProject, errors, utilities } = usePlugins();

	let data:any = reactive({
		apiUrl: 'reservoirs',
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

			const response2 = await api.get(`${data.apiUrl}/properties/${response.data.res.id}`, currentProject.getApiHeader());

			data.item.props = {
				id: response2.data.id,
				name: response2.data.name,
				init_name: utilities.setToNameProp(response2.data.init),
				rel_name: utilities.setToNameProp(response2.data.rel),
				hyd_name: utilities.setToNameProp(response2.data.hyd),
				sed_name: utilities.setToNameProp(response2.data.sed),
				nut_name: utilities.setToNameProp(response2.data.nut),
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
		<file-header input-file="reservoir.con" docs-path="connections/reservoirs">
			<router-link to="/edit/cons/reservoirs">Reservoirs</router-link>
			/ Edit
		</file-header>

		<reservoirs-form :item="data.item" :api-url="data.apiUrl" is-update allow-bulk-edit></reservoirs-form>
	</project-container>
</template>