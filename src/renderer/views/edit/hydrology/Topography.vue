<script setup lang="ts">
	import { useRoute } from 'vue-router';
	import { useHelpers } from '@/helpers';
	const route = useRoute();
	const { formatters } = useHelpers();

	let table:any = {
		headers: [
			{ key: 'name', label: 'Name' },
			{ key: 'slp', label: 'slp', type: 'number', decimals: 5 },
			{ key: 'slp_len', label: 'slp_len', type: 'number' },
			{ key: 'lat_len', label: 'lat_len', type: 'number' },
			{ key: 'dist_cha', label: 'dist_cha', type: 'number' },
			{ key: 'depos', label: 'depos', type: 'number' }
		],
	};
</script>

<template>
	<project-container>
		<div v-if="route.name == 'Topography'">
			<file-header input-file="topography.hyd" docs-path="hydrology/topography.hyd" use-io>
				Topography
			</file-header>

			<grid-view
				api-url="hydrology/topography"
				:headers="table.headers" 
				show-import-export default-csv-file="topography.csv" table-name="topo"  />
		</div>
		<router-view></router-view>
	</project-container>
</template>
