<script setup lang="ts">
	import { reactive } from 'vue';
	import SoilPlantForm from './SoilPlantForm.vue';

	let data:any = reactive({
		id: null,
		name: null,
		sw_frac: 0,
		nutrients_name: null,
		pest_name: null,
		path_name: null,
		hmet_name: null,
		salt_name: null
	});
</script>

<template>
	<project-container>
		<file-header input-file="soil_plant.ini" docs-path="constituents/soil_plant.ini" use-io>
			<router-link to="/edit/constituents/soil_plant">Soil Plant</router-link>
			/ Create
		</file-header>

		<soil-plant-form :item="data"></soil-plant-form>
	</project-container>
</template>
