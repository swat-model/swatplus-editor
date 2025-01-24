<script setup lang="ts">
	import { useRoute } from 'vue-router';
	const route = useRoute();
</script>

<template>
	<project-container>
		<div v-if="route.name == 'SoilNutrients'">
			<file-header input-file="nutrients.sol" docs-path="soils/nutrients.sol" use-io>
				Soil Nutrients
			</file-header>

			<grid-view 
				api-url="soils/nutrients"
				use-dynamic-headers 
				show-import-export default-csv-file="nutrients_sol.csv" table-name="soil_nut" />
		</div>
		<router-view></router-view>
	</project-container>
</template>
