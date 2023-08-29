<script setup lang="ts">
	import { reactive } from 'vue';
	import WetlandsForm from './WetlandsForm.vue';

	let data:any = reactive({
		name: null,
		description: null,
		org_min_name: null,
		pest_name: null,
		path_name: null,
		hmet_name: null,
		salt_name: null
	});
</script>

<template>
	<project-container>
		<file-header input-file="wetland.wet" docs-path="connections/reservoirs">
			<router-link to="/edit/cons/reservoirs">Reservoirs</router-link> / 
			<router-link to="/edit/cons/reservoirs/wetlands">Wetlands</router-link>
			/ Create
		</file-header>

		<wetlands-form :item="data.item"></wetlands-form>
	</project-container>
</template>
