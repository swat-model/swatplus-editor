<script setup lang="ts">
	import { useRoute } from 'vue-router';
	const route = useRoute();

	let table:any = {
		apiUrl: 'routing-units/items',
		headers: [
			{ key: 'name', label: 'Name' },
			{ key: 'area', label: 'Area (ha)', type: 'number', class: 'text-right' },
			{ key: 'lat', label: 'Lat', type: 'number', class: 'text-right' },
			{ key: 'lon', label: 'Lon', type: 'number', class: 'text-right' },
			{ key: 'elev', label: 'Elev (m)', type: 'number', class: 'text-right' },
			{ key: 'wst', label: 'Weather Station', type: 'object', class: 'text-right', objectRoutePath: '/edit/climate/stations/edit/' },
			{ key: 'topo', label: 'Topography', type: 'object', class: 'text-right', objectRoutePath: '/edit/hydrology/topography/edit/' },
			{ key: 'field', label: 'Field', type: 'object', class: 'text-right', objectRoutePath: '/edit/hydrology/fields/edit/' },
			{ key: 'outflow', label: '# Outflow', class: 'text-right' }
		],
	};
</script>

<template>
	<project-container>
		<div v-if="$route.name == 'RoutingUnits'">
			<file-header input-file="rout_unit.con" docs-path="routing-units/untitled" use-io>
				Routing Units
			</file-header>

			<grid-view :api-url="table.apiUrl" :headers="table.headers"></grid-view>
		</div>
		<router-view></router-view>
	</project-container>
</template>