<script setup lang="ts">
	import { useRoute } from 'vue-router';
	const route = useRoute();

	let table:any = {
		apiUrl: 'hrus/items',
		headers: [
			{ key: 'name', label: 'Name' },
			{ key: 'area', label: 'Area (ha)', type: 'number', class: 'text-right' },
			{ key: 'lat', label: 'Lat', type: 'number', class: 'text-right' },
			{ key: 'lon', label: 'Lon', type: 'number', class: 'text-right' },
			{ key: 'elev', label: 'Elev (m)', type: 'number', class: 'text-right' },
			{ key: 'wst', label: 'Weather Station', type: 'object', class: 'text-right', objectRoutePath: '/edit/climate/stations/edit/' },
			{ key: 'topo', label: 'Topography', type: 'object', class: 'text-right', objectRoutePath: '/edit/hydrology/topography/edit/' },
			{ key: 'hydro', label: 'Hydrology', type: 'object', class: 'text-right', objectRoutePath: '/edit/hydrology/edit/' },
			{ key: 'soil', label: 'Soils', type: 'object', class: 'text-right', objectRoutePath: '/edit/soils/soils/edit/' },
			{ key: 'lu_mgt', label: 'Landuse', type: 'object', class: 'text-right', objectRoutePath: '/edit/lum/landuse/edit/' },
			{ key: 'soil_plant_init', label: 'Soil Plant', type: 'object', class: 'text-right', objectRoutePath: '/edit/constituents/soil_plant/edit/' },
			{ key: 'surf_stor', label: 'Surface Storage', type: 'object', class: 'text-right', objectRoutePath: '/edit/reservoirs/wetlands/edit/' },				
			{ key: 'snow', label: 'Snow', type: 'object', class: 'text-right', objectRoutePath: '/edit/db/snow/edit/' },
			{ key: 'field', label: 'Field', type: 'object', class: 'text-right', objectRoutePath: '/edit/hydrology/fields/edit/' },
			{ key: 'outflow', label: '# Outflow', class: 'text-right' }
		],
	};
</script>

<template>
	<project-container>
		<div v-if="$route.name == 'Hrus'">
			<file-header input-file="hru.con" docs-path="hydrologic-response-units/hru-data.hru" use-io>
				HRUs
			</file-header>

			<grid-view :api-url="table.apiUrl" :headers="table.headers"></grid-view>
		</div>
		<router-view></router-view>
	</project-container>
</template>