<script setup lang="ts">
	import { useRoute } from 'vue-router';
	const route = useRoute();
</script>

<template>
	<project-container>
		<div v-if="$route.name == 'SoilsLte'">
			<file-header input-file="soils_lte.sol" docs-path="soils/soils-lte.sol" use-io>
				Soil Textures
			</file-header>

			<grid-view 
				api-url="soils/lte"
				use-dynamic-headers
				show-import-export default-csv-file="soils_lte.csv" table-name="soil_lte" />
		</div>
		<router-view></router-view>
	</project-container>
</template>
