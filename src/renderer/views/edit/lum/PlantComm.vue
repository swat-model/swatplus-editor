<script setup lang="ts">
	import { useRoute } from 'vue-router';
	const route = useRoute();

	let table:any = {
		apiUrl: 'init/plant_ini',
		headers: [
			{ key: 'name', label: 'Name' },
			{ key: 'rot_yr_ini', label: 'Initial rotation year', type: 'number' },
			{ key: 'num_plants', label: 'Number of plants', type: 'number' },
			{ key: 'description', label: 'Description' }
		],
	};
</script>

<template>
	<project-container>
		<div v-if="$route.name == 'PlantComm'">
			<file-header input-file="plant.ini" docs-path="landuse-and-management/plant.ini" use-io>
				Plant Communities
			</file-header>

			<grid-view :api-url="table.apiUrl" :headers="table.headers"></grid-view>
		</div>
		<router-view></router-view>
	</project-container>
</template>
