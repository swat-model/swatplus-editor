<script setup lang="ts">
	import { reactive } from 'vue';
	import CalibrationForm from './CalibrationForm.vue';

	let data:any = reactive({
		item: {
			chg_typ: 'absval'
		},
		objOptions: []
	});
</script>

<template>
	<project-container>
		<file-header input-file="calibration.cal" docs-path="calibration/calibration.cal" use-io>
			<router-link to="/edit/change/hard">Hard Calibration</router-link>
			/ Create
		</file-header>

		<calibration-form :item="data.item" :obj-options="data.objOptions" />
	</project-container>
</template>
