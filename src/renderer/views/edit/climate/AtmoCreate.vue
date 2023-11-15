<script setup lang="ts">
	import { reactive } from 'vue';
	import AtmoForm from './AtmoForm.vue';

	let data:any = reactive({
		atmo_cli_id: 1,
		name: <string|null>null,
		values: <any[]>[]
	});
</script>

<template>
	<project-container>
		<file-header input-file="atmo.cli" docs-path="climate/atmo.cli" use-io>
			<router-link to="/edit/climate/stations">Weather Stations</router-link>
			/ <router-link to="/edit/climate/stations/atmo">Atmospheric Deposition</router-link>
			/ Create
		</file-header>

		<atmo-form :item="data"></atmo-form>
	</project-container>
</template>
