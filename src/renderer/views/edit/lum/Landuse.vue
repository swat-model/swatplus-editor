<script setup lang="ts">
	import { useRoute } from 'vue-router';
	const route = useRoute();

	let table:any = {
		apiUrl: 'lum/landuse',
		headers: [
			{ key: 'name', label: 'Name' },
			{ key: 'cal_group', label: 'Calibration Group' },
			{ key: 'plnt_com', label: 'Plant Comm.', type: 'object', objectRoutePath: '/edit/lum/plant/edit/' },
			{ key: 'mgt', label: 'Management Sch.', type: 'object', objectRoutePath: '/edit/lum/mgt/edit/' },
			{ key: 'cn2', label: 'CN2', type: 'object', objectRoutePath: '/edit/lum/cntable/edit/' },
			{ key: 'cons_prac', label: 'Cons. Prac.', type: 'object', objectRoutePath: '/edit/lum/conspractice/edit/' },
			{ key: 'urban', label: 'Urban', type: 'object', objectRoutePath: '/edit/db/urban/edit/' },
			{ key: 'urb_ro', label: 'Urban Runoff' },
			{ key: 'ov_mann', label: "Manning's n", type: 'object', objectRoutePath: '/edit/lum/ovntable/edit/' },
			{ key: 'tile', label: 'Tile Drain', type: 'object', objectRoutePath: '/edit/structural/tiledrain/edit/' },
			{ key: 'sep', label: 'Septic Tank', type: 'object', objectRoutePath: '/edit/structural/septic/edit/' },
			{ key: 'vfs', label: 'Filter Strip', type: 'object', objectRoutePath: '/edit/structural/filterstrip/edit/' },
			{ key: 'grww', label: 'Grassed Waterway', type: 'object', objectRoutePath: '/edit/structural/grassedww/edit/' },
			{ key: 'bmp', label: 'BMPs', type: 'object', objectRoutePath: '/edit/structural/bmpuser/edit/' },
			{ key: 'description', label: 'Description' }
		],
	};
</script>

<template>
	<project-container>
		<div v-if="route.name === 'Landuse'">
			<file-header input-file="landuse.lum" docs-path="land-use-management">
				Land Use Management
			</file-header>

			<grid-view :api-url="table.apiUrl" :headers="table.headers"></grid-view>
		</div>
		<router-view></router-view>
	</project-container>
</template>
