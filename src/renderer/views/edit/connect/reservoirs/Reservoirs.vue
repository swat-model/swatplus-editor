<script setup lang="ts">
	import { useRoute } from 'vue-router';
	const route = useRoute();

	let table:any = {
		apiUrl: 'reservoirs/items',
		headers: [
			{ key: 'name', label: 'Name' },
			{ key: 'area', label: 'Area (ha)', type: 'number', class: 'text-right' },
			{ key: 'lat', label: 'Lat', type: 'number', class: 'text-right' },
			{ key: 'lon', label: 'Lon', type: 'number', class: 'text-right' },
			{ key: 'elev', label: 'Elev (m)', type: 'number', class: 'text-right' },
			{ key: 'wst', label: 'Weather Station', type: 'object', class: 'text-right', objectRoutePath: '/edit/climate/stations/edit/' },
			{ key: 'init', label: 'Initial', type: 'object', class: 'text-right', objectRoutePath: '/edit/cons/reservoirs/initial/edit/' },
			{ key: 'rel', label: 'Release', type: 'object', class: 'text-right', objectRoutePath: '/edit/decision-table/type/project/edit/' },
			{ key: 'hyd', label: 'Hydrology', type: 'object', class: 'text-right', objectRoutePath: '/edit/cons/reservoirs/hydrology/edit/' },
			{ key: 'sed', label: 'Sediment', type: 'object', class: 'text-right', objectRoutePath: '/edit/cons/reservoirs/sediment/edit/' },
			{ key: 'nut', label: 'Nutrients', type: 'object', class: 'text-right', objectRoutePath: '/edit/cons/reservoirs/nutrients/edit/' },
			{ key: 'outflow', label: '# Outflow', class: 'text-right' }
		],
	};
</script>

<template>
	<project-container>
		<div v-if="route.name == 'Reservoirs'">
			<file-header input-file="reservoir.con" docs-path="reservoirs/reservoir.res" use-io>
				Reservoirs
			</file-header>

			<grid-view :api-url="table.apiUrl" :headers="table.headers"></grid-view>
		</div>
		<router-view></router-view>
	</project-container>
</template>