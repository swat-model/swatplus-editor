<script setup lang="ts">
	import { useRoute } from 'vue-router';
	const route = useRoute();
</script>
<template>
	<project-container>
		<div v-if="route.name == 'ReservoirsNutrients'">
			<file-header input-file="nutrients.res" docs-path="reservoirs/nutrients.res" use-io>
				<router-link to="/edit/cons/reservoirs">Reservoirs</router-link> 
				/ Nutrients
			</file-header>

			<grid-view 
				api-url="reservoirs/nutrients"
				use-dynamic-headers 
				show-import-export default-csv-file="nutrients-res.csv" table-name="nut_res" />
		</div>
		<router-view></router-view>
	</project-container>
</template>
