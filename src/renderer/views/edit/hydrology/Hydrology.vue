<script setup lang="ts">
	import { useRoute } from 'vue-router';
	const route = useRoute();
</script>

<template>
	<project-container>
		<div v-if="$route.name == 'Hydrology'">
			<file-header input-file="hydrology.hyd" docs-path="hydrology/hydrology.hyd" use-io>
				Hydrology
			</file-header>
			
			<grid-view
				api-url="hydrology/hydrology"
				use-dynamic-headers 
				show-import-export default-csv-file="hydrology.csv" table-name="hyd" />
		</div>
		<router-view></router-view>
	</project-container>
</template>
