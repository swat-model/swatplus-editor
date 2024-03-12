<script setup lang="ts">
	import { reactive, onMounted, watch } from 'vue';
	import { useRoute } from 'vue-router';
	import { useHelpers } from '@/helpers';
	import RoutingUnitsForm from './RoutingUnitsForm.vue';

	const route = useRoute();
	const { api, currentProject, errors, utilities } = useHelpers();

	let data:any = reactive({
		apiUrl: 'routing-units',
		page: {
			loading: false,
			error: null
		},
		item: {
			connect: {},
			props: {},
			outflow: []
		},
		use_gwflow: false
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

			const response2 = await api.get(`${data.apiUrl}/properties/${response.data.rtu.id}`, currentProject.getApiHeader());

			data.item.props = {
				id: response2.data.id,
				name: response2.data.name,
				topo_name: utilities.setToNameProp(response2.data.topo),
				field_name: utilities.setToNameProp(response2.data.field),
				description: response2.data.description
			};

			const responseGwflow = await api.get(`gwflow/enabled`, currentProject.getApiHeader());
			errors.log(responseGwflow.data);

			data.use_gwflow = responseGwflow.data.use_gwflow;
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
		<file-header input-file="rout_unit.con" docs-path="routing-units/untitled" use-io>
			<router-link to="/edit/cons/routing-units">Routing Units</router-link>
			/ Edit
		</file-header>

		<routing-units-form :item="data.item" :api-url="data.apiUrl" is-update allow-bulk-edit :use-gwflow="data.use_gwflow"></routing-units-form>
	</project-container>
</template>