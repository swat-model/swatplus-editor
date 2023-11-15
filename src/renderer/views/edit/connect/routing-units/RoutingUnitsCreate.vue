<script setup lang="ts">
	import { reactive } from 'vue';
	import RoutingUnitsForm from './RoutingUnitsForm.vue';

	let data:any = reactive({
		apiUrl: 'routing-units',
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
		<file-header input-file="rout_unit.con" docs-path="routing-units/untitled" use-io>
			<router-link to="/edit/cons/routing-units">Routing Units</router-link>
			/ Create
		</file-header>

		<routing-units-form :item="data.item" :api-url="data.apiUrl"></routing-units-form>
	</project-container>
</template>