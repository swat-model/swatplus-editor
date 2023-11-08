<script setup lang="ts">
	import { useRoute } from 'vue-router';
	const route = useRoute();

	let table:any = {
		apiUrl: 'climate/wgn',
		headers: [
			{ key: 'name', label: 'Name' },
			{ key: 'lat', label: 'Lat', type: 'number', class: 'text-right' },
			{ key: 'lon', label: 'Lon', type: 'number', class: 'text-right' },
			{ key: 'elev', label: 'Elev (m)', type: 'number', class: 'text-right' },
			{ key: 'rain_yrs', label: 'Rain years', type: 'number', class: 'text-right' }
		],
	};
</script>

<template>
	<project-container>
		<div v-if="$route.name == 'Wgn'">
			<file-header input-file="weather-wgn.cli" docs-path="climate">
				Weather Generator
			</file-header>

			<grid-view :api-url="table.apiUrl" :headers="table.headers"></grid-view>
		</div>
		<router-view></router-view>
	</project-container>
</template>