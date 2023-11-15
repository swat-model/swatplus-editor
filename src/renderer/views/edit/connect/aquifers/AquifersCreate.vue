<script setup lang="ts">
	import { reactive, onMounted } from 'vue';
	import { useHelpers } from '@/helpers';
	import AquifersForm from './AquifersForm.vue';

	const { api, errors, utilities } = useHelpers();

	let data:any = reactive({
		apiUrl: 'aquifers',
		paths: {
			vars: 'aquifer_aqu'
		},
		page: {
			loading: true,
			error: null
		},
		item: {
			connect: {
				name: null,
				area: 0,
				lat: 0,
				lon: 0,
				elev: null,
				wst_name: null
			},
			props: {},
			outflow: []
		},
		vars: []
	});

	async function get() {
		data.page.loading = true;
		data.page.error = null;

		try {
			const response = await api.get(`definitions/vars/${data.paths.vars}/${utilities.appPathUrl}`);
			data.vars = response.data;
			data.item.props = utilities.setVars(data.item.props, data.vars);
			data.item.props.init = { id: 1 };
		} catch (error) {
			data.page.error = errors.logError(error, 'Unable to get table metadata from database.');
		}
			
		data.page.loading = false;
	}

	onMounted(async () => await get())
</script>

<template>
	<project-container :loading="data.page.loading" :load-error="data.page.error">
		<file-header input-file="aquifer.con" docs-path="aquifers/aquifer.aqu" use-io>
			<router-link to="/edit/cons/aquifers">Aquifers</router-link>
			/ Create
		</file-header>

		<aquifers-form :item="data.item" :api-url="data.apiUrl" :vars="data.vars"></aquifers-form>
	</project-container>
</template>