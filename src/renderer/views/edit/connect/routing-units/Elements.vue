<script setup lang="ts">
	import { useRoute } from 'vue-router';
	const route = useRoute();

	let table:any = {
		apiUrl: 'routing-units/elements',
		headers: [
			{ key: 'name', label: 'Name' },
			{ key: 'obj_typ', label: 'Type' },
			{ key: 'obj_name', label: 'Object' },
			{ key: 'frac', label: 'Fraction', type: 'number', class: 'text-right' },
			{ key: 'rtu', label: 'Routing Unit', type: 'object', class: 'text-right', objectRoutePath: '/edit/cons/routing-units/edit/' }
		],
	};
</script>

<template>
	<project-container>
		<div v-if="$route.name == 'RoutingUnitsElements'">
			<file-header input-file="rout_unit.ele" docs-path="routing-units/untitled-2" use-io>
				<router-link to="/edit/cons/routing-units">Routing Units</router-link>
				/ Elements
			</file-header>

			<grid-view :api-url="table.apiUrl" :headers="table.headers"></grid-view>
		</div>
		<router-view></router-view>
	</project-container>
</template>