<script setup lang="ts">
	import { useRoute } from 'vue-router';
	const route = useRoute();

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
</script>

<template>
	<project-container>
		<div v-if="$route.name == 'Aquifers'">
			<file-header input-file="aquifer.con" docs-path="connections/aquifers">
				Aquifers
			</file-header>

			<grid-view :api-url="table.apiUrl" :headers="table.headers"></grid-view>
		</div>
		<router-view></router-view>
	</project-container>
</template>