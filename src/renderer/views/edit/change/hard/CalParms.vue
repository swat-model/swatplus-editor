<script setup lang="ts">
	import { useRoute } from 'vue-router';
	const route = useRoute();
</script>

<template>
	<project-container>
		<div v-if="route.name == 'HardCalibrationParms'">
			<file-header input-file="cal_parms.cal" docs-path="calibration/cal_parms.cal" use-io>
				<router-link to="/edit/change/hard">Hard Calibration</router-link>
				/ Parameters
			</file-header>

			<p>
				You cannot add new parameters because they are determined by the model; however, you may edit the 
				absolute minimum and maximum values by selecting a row below.
			</p>

			<grid-view 
				api-url="change/cal_parms"
				use-dynamic-headers
				:default-sort="['obj_typ','asc']"
				hide-create hide-delete />
		</div>
		<router-view></router-view>
	</project-container>
</template>
