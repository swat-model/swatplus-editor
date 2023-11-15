<script setup lang="ts">
	import { reactive, onMounted, watch } from 'vue';
	import { useRoute } from 'vue-router';
	import { useHelpers } from '@/helpers';
	import AquifersForm from './AquifersForm.vue';

	const route = useRoute();
	const { api, currentProject, errors, utilities } = useHelpers();

	let data:any = reactive({
		apiUrl: 'aquifers',
		paths: {
			vars: 'aquifer_aqu'
		},
		page: {
			loading: false,
			error: null
		},
		item: {
			connect: {},
			props: {},
			outflow: []
		},
		vars: []
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

			const response2 = await api.get(`${data.apiUrl}/properties/${response.data.aqu.id}`, currentProject.getApiHeader());
			data.item.props = response2.data;

			const response3 = await api.get(`definitions/vars/${data.paths.vars}/${utilities.appPathUrl}`);
			data.vars = response3.data;
		} catch (error) {
			console.log(error);
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
		<file-header input-file="aquifer.con" docs-path="aquifers/aquifer.aqu" use-io>
			<router-link to="/edit/cons/aquifers">Aquifers</router-link>
			/ Edit
		</file-header>

		<aquifers-form :item="data.item" :api-url="data.apiUrl" is-update allow-bulk-edit :vars="data.vars"></aquifers-form>
	</project-container>
</template>