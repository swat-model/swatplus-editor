<script setup lang="ts">
	import { reactive } from 'vue';
	import HrusForm from './HrusForm.vue';

	let data:any = reactive({
		apiUrl: 'hrus',
		item: {
			connect: {
				name: null,
				area: 0,
				lat: 0,
				lon: 0,
				elev: null,
				wst_name: null
			},
			props: {},
			outflow: []
		}
	});
</script>

<template>
	<project-container>
		<file-header input-file="hru.con" docs-path="hydrologic-response-units/hru-data.hru" use-io>
			<router-link to="/edit/cons/hrus">HRUs</router-link>
			/ Create
		</file-header>

		<hrus-form :item="data.item" :api-url="data.apiUrl"></hrus-form>
	</project-container>
</template>