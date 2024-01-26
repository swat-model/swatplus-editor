<script setup lang="ts">
	import { reactive } from 'vue';
	import PlantCommForm from './PlantCommForm.vue';

	let item:any = reactive({
		name: null,
		description: null,
		rot_yr_ini: 1
	});
</script>

<template>
	<project-container>
		<file-header input-file="plant.ini" docs-path="landuse-and-management/plant.ini" use-io>
			<router-link to="/edit/lum/plant">Plant Communities</router-link>
			/ Create
		</file-header>

		<plant-comm-form :item="item"></plant-comm-form>
	</project-container>
</template>
