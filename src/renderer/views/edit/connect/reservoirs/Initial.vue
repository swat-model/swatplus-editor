<script setup lang="ts">
	import { useRoute } from 'vue-router';
	const route = useRoute();

	let table:any = {
		apiUrl: 'reservoirs/initial',
		headers: [
			{ key: 'name', label: 'Name' },
			{ key: 'org_min', label: 'Organic Mineral', type: 'object', class: 'text-right', objectRoutePath: '/edit/constituents/om_water/edit/' },
			{ key: 'pest', label: 'Pesticide', type: 'object', class: 'text-right', objectRoutePath: '/edit/constituents/pest/', ignoreObjectRouteId: true },
			{ key: 'path', label: 'Pathogen', type: 'object', class: 'text-right', objectRoutePath: '/edit/constituents/path/', ignoreObjectRouteId: true },
			//{ key: 'hmet', label: 'Heavy Metal', type: 'object', class: 'text-right' }, 
			{ key: 'salt_cs', label: 'Salt', type: 'object', class: 'text-right' }, 
			{ key: 'description', label: 'Description' }
		],
	};
</script>

<template>
	<project-container>
		<div v-if="$route.name == 'ReservoirsInitial'">
			<file-header input-file="initial.res" docs-path="reservoirs/initial.res" use-io>
				<router-link to="/edit/cons/reservoirs">Reservoirs</router-link> 
				/ Initial
			</file-header>

			<grid-view :api-url="table.apiUrl" :headers="table.headers"></grid-view>
		</div>
		<router-view></router-view>
	</project-container>
</template>