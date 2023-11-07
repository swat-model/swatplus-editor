<script setup lang="ts">
	import { reactive, onMounted } from 'vue';
	import { useHelpers } from '@/helpers';
	import HrusLteForm from './HrusLteForm.vue';

	const { api, errors, utilities } = useHelpers();

	let data:any = reactive({
		apiUrl: 'hrus-lte',
		paths: {
			vars: 'hru_lte_hru'
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
			
			let keys = Object.keys(data.vars);
			for (let k of keys) {
				let v = data.vars[k];
				data.item.props[k] = v.type == 'string' ? v.default_text : v.default_value;
			}
		} catch (error) {
			data.page.error = errors.logError(error, 'Unable to get table metadata from database.');
		}
			
		data.page.loading = false;
	}

	onMounted(async () => await get())
</script>

<template>
	<project-container :loading="data.page.loading" :load-error="data.page.error">
		<file-header input-file="hru-lte.con" docs-path="connections/hrus">
			<router-link to="/edit/cons/hrus-lte">HRUs</router-link>
			/ Create
		</file-header>

		<hrus-lte-form :item="data.item" :api-url="data.apiUrl" :vars="data.vars"></hrus-lte-form>
	</project-container>
</template>