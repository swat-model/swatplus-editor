<script setup lang="ts">
	import { useRoute } from 'vue-router';
	const route = useRoute();

	let table:any = {
		apiUrl: 'regions/ls_units/elements',
		headers: [
			{ key: 'name', label: 'Name' },
			{ key: 'obj_typ', label: 'Type' },
			{ key: 'obj_name', label: 'Object', type: 'variable-object' },
			{ key: 'bsn_frac', label: 'Basin Fraction', type: 'number', decimals: 6, class: 'text-right' },
			{ key: 'sub_frac', label: 'Subbasin Fraction', type: 'number', decimals: 6, class: 'text-right' },
			{ key: 'reg_frac', label: 'Region Fraction', type: 'number', decimals: 6, class: 'text-right' },
			{ key: 'ls_unit_def', label: 'Landscape Unit', type: 'object', class: 'text-right', objectRoutePath: '/edit/regions/ls_units/edit/' }
		]
	};
</script>

<template>
	<project-container>
		<div v-if="$route.name === 'LandscapeUnitsElements'">
			<file-header input-file="ls_unit.ele" docs-path="landscape-units/ls_unit.ele" use-io>
				<router-link to="/edit/regions/ls_units">Landscape Units</router-link> 
				/ Elements
			</file-header>

			<grid-view :api-url="table.apiUrl" :headers="table.headers"></grid-view>
		</div>
		<router-view></router-view>
	</project-container>
</template>
