<script setup lang="ts">
	import { useRoute } from 'vue-router';
	const route = useRoute();

	let table:any = {
		headers: [
			{ key: 'name', label: 'Name' },
			{ key: 'fert', label: 'Fertilizer', type: 'object', class: 'text-right', objectRoutePath: '/edit/db/fertilizer/edit/' },
			{ key: 'bm_eat', label: 'Bm_eat', class: 'text-right', type: 'number' },
			{ key: 'bm_tramp', label: 'Bm_tramp', class: 'text-right', type: 'number' },
			{ key: 'man_amt', label: 'Man_amt', class: 'text-right', type: 'number' },
			{ key: 'grz_bm_min', label: 'Grz_bm_min', class: 'text-right', type: 'number' },
			{ key: 'description', label: 'Description' }
		],
	};
</script>

<template>
	<project-container>
		<div v-if="route.name == 'OperationsGraze'">
			<file-header input-file="graze.ops" docs-path="management-practices/graze.ops" use-io>
				<router-link to="/edit/lum/ops">Operations</router-link> 
				/ Graze
			</file-header>

			<grid-view 
				api-url="ops/graze" :headers="table.headers"></grid-view>
		</div>
		<router-view></router-view>
	</project-container>
</template>
