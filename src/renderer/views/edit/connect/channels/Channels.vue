<script setup lang="ts">
	import { useRoute } from 'vue-router';
	const route = useRoute();

	let table:any = {
		apiUrl: 'channels/items',
		headers: [
			{ key: 'name', label: 'Name' },
			{ key: 'area', label: 'Area (ha)', type: 'number', class: 'text-right' },
			{ key: 'lat', label: 'Lat', type: 'number', class: 'text-right' },
			{ key: 'lon', label: 'Lon', type: 'number', class: 'text-right' },
			{ key: 'elev', label: 'Elev (m)', type: 'number', class: 'text-right' },
			{ key: 'wst', label: 'Weather Station', type: 'object', class: 'text-right', objectRoutePath: '/edit/climate/stations/edit/' },
			{ key: 'init', label: 'Initial', type: 'object', class: 'text-right', objectRoutePath: '/edit/cons/channels/initial/edit/' },
			{ key: 'hyd', label: 'Hyd./Sed.', type: 'object', class: 'text-right', objectRoutePath: '/edit/cons/channels/hydsed/edit/' },
			{ key: 'nut', label: 'Nutrients', type: 'object', class: 'text-right', objectRoutePath: '/edit/cons/channels/nutrients/edit/' },
			{ key: 'outflow', label: '# Outflow', class: 'text-right' }
		],
	};
</script>

<template>
	<project-container>
		<div v-if="$route.name == 'Channels'">
			<file-header input-file="chandeg.con" docs-path="connections/channels">
				Channels
			</file-header>

			<grid-view :api-url="table.apiUrl" :headers="table.headers"></grid-view>
		</div>
		<router-view></router-view>
	</project-container>
</template>