<script setup lang="ts">
	import { useRoute } from 'vue-router';
	const route = useRoute();

	let table:any = {
		apiUrl: 'regions/ls_units',
		headers: [
			{ key: 'name', label: 'Name' },
			{ key: 'area', label: 'Area', type: 'number', class: 'text-right' },
			{ key: 'num_elements', label: 'Number of elements', type: 'int', class: 'text-right' }
		]
	};
</script>

<template>
	<project-container>
		<div v-if="route.name === 'LandscapeUnits'">
			<file-header input-file="ls_unit.def" docs-path="landscape-units/ls_unit.def" use-io>
				Landscape Units
			</file-header>

			<grid-view :api-url="table.apiUrl" :headers="table.headers"></grid-view>
		</div>
		<router-view></router-view>
	</project-container>
</template>
