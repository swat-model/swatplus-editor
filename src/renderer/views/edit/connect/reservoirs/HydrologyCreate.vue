<script setup lang="ts">
	import { reactive, onMounted } from 'vue';
	import { usePlugins } from '../../../../plugins';
	import EditForm from '../../../../components/EditForm.vue';

	const { api, errors, utilities } = usePlugins();

	let data:any = reactive({
		paths: {
			vars: 'hydrology_res'
		},
		page: {
			loading: true,
			error: null
		},
		item: {
			name: null,
			description: null
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
				data.item[k] = v.type == 'string' ? v.default_text : v.default_value;
			}
		} catch (error) {
			data.page.error = errors.logError(error, 'Unable to get table metadata from database.');
		}
			
		data.page.loading = false;
	}

	onMounted(async () => await get())
</script>

<template>
	<project-container>
		<file-header input-file="hydrology.res" docs-path="connections/reservoirs">
			<router-link to="/edit/cons/reservoirs">Reservoirs</router-link> / 
			<router-link to="/edit/cons/reservoirs/hydrology">Hydrology</router-link>
			/ Create
		</file-header>

		<edit-form show-range
			:item="data.item" 
			:vars="data.vars" 
			api-url="reservoirs/hydrology"
			redirect-route="ReservoirsHydrology"></edit-form>
	</project-container>
</template>
