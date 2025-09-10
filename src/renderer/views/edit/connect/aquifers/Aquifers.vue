<script setup lang="ts">
	import { reactive, onMounted, watch } from 'vue';
	import { useRoute } from 'vue-router';
	import { useHelpers } from '@/helpers';
	const route = useRoute();
	const { api, currentProject, errors, utilities } = useHelpers();

	let table:any = {
		apiUrl: 'aquifers/items',
		headers: [
			{ key: 'name', label: 'Name' },
			{ key: 'area', label: 'Area (ha)', type: 'number', class: 'text-right' },
			{ key: 'lat', label: 'Lat', type: 'number', class: 'text-right' },
			{ key: 'lon', label: 'Lon', type: 'number', class: 'text-right' },
			{ key: 'elev', label: 'Elev (m)', type: 'number', class: 'text-right' },
			{ key: 'wst', label: 'Weather Station', type: 'object', class: 'text-right', objectRoutePath: '/edit/climate/stations/edit/' },
			{ key: 'init', label: 'Initial', type: 'object', class: 'text-right', objectRoutePath: '/edit/cons/aquifers/initial/edit/' },
			{ key: 'gw_flo', class: 'text-right', type: 'number' },
			{ key: 'dep_bot', class: 'text-right', type: 'number' },
			{ key: 'dep_wt', class: 'text-right', type: 'number' },
			{ key: 'no3_n', class: 'text-right', type: 'number' },
			{ key: 'sol_p', class: 'text-right', type: 'number' },
			{ key: 'carbon', class: 'text-right', type: 'number' },
			{ key: 'flo_dist', class: 'text-right', type: 'number' },
			{ key: 'bf_max', class: 'text-right', type: 'number' },
			{ key: 'alpha_bf', class: 'text-right', type: 'number' },
			{ key: 'revap', class: 'text-right', type: 'number' },
			{ key: 'rchg_dp', class: 'text-right', type: 'number' },
			{ key: 'spec_yld', class: 'text-right', type: 'number' },
			{ key: 'hl_no3n', class: 'text-right', type: 'number' },
			{ key: 'flo_min', class: 'text-right', type: 'number' },
			{ key: 'revap_min', class: 'text-right', type: 'number' },
			{ key: 'outflow', label: '# Outflow', class: 'text-right' }
		],
	};

	let data:any = reactive({
		page: {
			loading: false,
			error: null
		},
		use_gwflow: false,
	});

	async function get() {
		data.page.loading = true;
		data.page.error = null;

		try {
			const response = await api.get(`gwflow/enabled`, currentProject.getApiHeader());
			errors.log(response.data);

			data.use_gwflow = response.data.use_gwflow;
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
		<div v-if="route.name == 'Aquifers'">
			<file-header input-file="aquifer.con" docs-path="aquifers/aquifer.aqu" use-io>
				Aquifers
			</file-header>

			<v-alert v-if="data.use_gwflow" type="info" icon="$info" variant="tonal" border="start" class="mb-4">
				Groundwater flow is enabled. Aquifers will not be used in this simulation, but are still shown below.
			</v-alert>

			<grid-view :api-url="table.apiUrl" :headers="table.headers"></grid-view>
		</div>
		<router-view></router-view>
	</project-container>
</template>