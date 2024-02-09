<script setup lang="ts">
	import { useRoute } from 'vue-router';
	const route = useRoute();

	let table:any = {
		apiUrl: 'reservoirs/wetlands',
		headers: [
			{ key: 'name', label: 'Name' },
			{ key: 'init', label: 'Initial', type: 'object', class: 'text-right', objectRoutePath: '/edit/cons/reservoirs/initial/edit/' },
			{ key: 'rel', label: 'Release', type: 'object', class: 'text-right', objectRoutePath: '/edit/decision-table/type/project/edit/' },
			{ key: 'hyd', label: 'Wetlands Hydrology', type: 'object', class: 'text-right', objectRoutePath: '/edit/cons/reservoirs/wetlands_hydrology/edit/' },
			{ key: 'sed', label: 'Sediment', type: 'object', class: 'text-right', objectRoutePath: '/edit/cons/reservoirs/sediment/edit/' },
			{ key: 'nut', label: 'Nutrients', type: 'object', class: 'text-right', objectRoutePath: '/edit/cons/reservoirs/nutrients/edit/' },
			{ key: 'description', label: 'Description' }
		],
	};
</script>

<template>
	<project-container>
		<div v-if="$route.name == 'ReservoirsWetlands'">
			<file-header input-file="wetlands.wet" docs-path="wetlands/wetland.wet" use-io>
				<router-link to="/edit/cons/reservoirs">Reservoirs</router-link> 
				/ Wetlands
			</file-header>

			<grid-view :api-url="table.apiUrl" :headers="table.headers"></grid-view>
		</div>
		<router-view></router-view>
	</project-container>
</template>
