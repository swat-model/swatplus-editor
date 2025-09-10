<script setup lang="ts">
	import { useRoute } from 'vue-router';
	const route = useRoute();

	let table:any = {
		apiUrl: 'change/calibration',
		headers: [
			{ key: 'cal_parm', type: 'object', objectRoutePath: '/edit/change/hard/parms/edit/' },
			{ key: 'chg_typ' },
			{ key: 'chg_val', type: 'number', class: 'text-right' },
			{ key: 'soil_lyr1', type: 'number', class: 'text-right' },
			{ key: 'soil_lyr2', type: 'number', class: 'text-right' },
			{ key: 'yr1', type: 'number', class: 'text-right' },
			{ key: 'yr2', type: 'number', class: 'text-right' },
			{ key: 'day1', type: 'number', class: 'text-right' },
			{ key: 'day2', type: 'number', class: 'text-right' },
			{ key: 'conditions', type: 'number', class: 'text-right' },
			{ key: 'obj_tot', type: 'number', class: 'text-right' },
		],
	};
</script>

<template>
	<project-container>
		<div v-if="route.name == 'HardCalibration'">
			<file-header input-file="calibration.cal" docs-path="calibration/calibration.cal" use-io>
				Hard Calibration
			</file-header>

			<grid-view :api-url="table.apiUrl" :headers="table.headers" :default-sort="['id','asc']"></grid-view>
		</div>
		<router-view></router-view>
	</project-container>
</template>
