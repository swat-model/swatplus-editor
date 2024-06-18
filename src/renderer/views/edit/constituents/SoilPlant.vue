<script setup lang="ts">
	import { useRoute } from 'vue-router';
	const route = useRoute();

	let table:any = {
		apiUrl: 'init/soil_plant',
		headers: [
			{ key: 'name', label: 'Name' },
			{ key: 'sw_frac', label: 'Soil Water Fraction', type: 'number', class: 'text-right' },
			{ key: 'nutrients', label: 'Nutrients', type: 'object', class: 'text-right', objectRoutePath: '/edit/soils/soil-nutrients/edit/' },
			{ key: 'pest', label: 'Pesticide', type: 'object', class: 'text-right', objectRoutePath: '/edit/constituents/pest/', ignoreObjectRouteId: true },
			{ key: 'path', label: 'Pathogen', type: 'object', class: 'text-right', objectRoutePath: '/edit/constituents/path/', ignoreObjectRouteId: true },
			//{ key: 'hmet', label: 'Heavy Metal', type: 'object', class: 'text-right' }, 
			{ key: 'salt_cs', label: 'Salt', type: 'object', class: 'text-right' }
		],
	};
</script>

<template>
	<project-container>
		<div v-if="$route.name == 'ConstituentsSoilPlant'">
			<file-header input-file="soil_plant.ini" docs-path="constituents/soil_plant.ini" use-io>
				Soil Plant
			</file-header>

			<grid-view :api-url="table.apiUrl" :headers="table.headers"></grid-view>
		</div>
		<router-view></router-view>
	</project-container>
</template>
