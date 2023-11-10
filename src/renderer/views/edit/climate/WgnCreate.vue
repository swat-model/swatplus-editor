<script setup lang="ts">
	import { reactive } from 'vue';
	import WgnForm from './WgnForm.vue';

	let data:any = reactive({
		name: <string|null>null,
		lat: <number|null>null,
		lon: <number|null>null,
		elev: <number|null>null,
		rain_yrs: <number|null>null,
		monthly_values: <any[]>[]
	});
</script>

<template>
	<project-container>
		<file-header input-file="weather-wgn.cli" docs-path="climate">
			<router-link to="/edit/climate/wgn">Weather Generator</router-link>
			/ Create
		</file-header>

		<wgn-form :item="data"></wgn-form>
	</project-container>
</template>