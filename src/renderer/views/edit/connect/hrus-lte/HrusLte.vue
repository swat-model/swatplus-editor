<script setup lang="ts">
	import { useRoute } from 'vue-router';
	const route = useRoute();

	let table:any = {
		apiUrl: 'hrus-lte/items',
		headers: [
			{ key: 'name', label: 'Name' },
			{ key: 'area', label: 'Area (ha)', type: 'number', class: 'text-right' },
			{ key: 'lat', label: 'Lat', type: 'number', class: 'text-right' },
			{ key: 'lon', label: 'Lon', type: 'number', class: 'text-right' },
			{ key: 'elev', label: 'Elev (m)', type: 'number', class: 'text-right' },
			{ key: 'wst', label: 'Weather Station', type: 'object', class: 'text-right', objectRoutePath: '/edit/climate/stations/edit/' },
			{ key: 'soil_text', label: 'Soil', type: 'object', class: 'text-right', objectRoutePath: '/edit/soils/soils-lte/edit/' },
			{ key: 'grow_start', label: 'Grow Start', type: 'object', class: 'text-right', objectRoutePath: '/edit/decision_table/edit/' },
			{ key: 'grow_end', label: 'Grow End', type: 'object', class: 'text-right', objectRoutePath: '/edit/decision_table/edit/' },
			{ key: 'plnt_typ', label: 'Plant', type: 'object', class: 'text-right', objectRoutePath: '/edit/db/plants/edit/' },
			{ key: 'outflow', label: '# Outflow', class: 'text-right' }
		],
	};
</script>

<template>
	<project-container>
		<div v-if="$route.name == 'HrusLte'">
			<file-header input-file="hru-lte.con" docs-path="hydrologic-response-units/hru-lte.hru" use-io>
				HRUs
			</file-header>

			<grid-view :api-url="table.apiUrl" :headers="table.headers"></grid-view>
		</div>
		<router-view></router-view>
	</project-container>
</template>