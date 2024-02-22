<script setup lang="ts">
	import { reactive } from 'vue';
	import StationsForm from './StationsForm.vue';

	let data:any = reactive({
		name: <string|null>null,
		lat: <number|null>null,
		lon: <number|null>null,
		wgn: <string|null>null,
		pcp: <string|null>'sim',
		tmp: <string|null>'sim',
		slr: <string|null>'sim',
		hmd: <string|null>'sim',
		wnd: <string|null>'sim',
		pet: <string|null>null,
		atmo_dep: <string|null>null
	});
</script>

<template>
	<project-container>
		<file-header input-file="weather-sta.cli" docs-path="climate">
			<router-link to="/edit/climate/stations">Weather Stations</router-link>
			/ Create
		</file-header>

		<stations-form :item="data"></stations-form>
	</project-container>
</template>
