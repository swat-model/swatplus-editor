<script setup lang="ts">
	import { reactive } from 'vue';
	import FpcellForm from './FpcellForm.vue';

	let data:any = reactive({
		cell_id: 1,
		channel_name: null,
		area_m2: 0,
		conductivity: 0,
	});

	
</script>

<template>
	<project-container>
		<file-header input-file="gwflow.floodplain" docs-path="modflow" use-io>
			<router-link to="/edit/cons/gwflow">Groundwater Flow</router-link>
			/ <router-link to="/edit/cons/gwflow/fpcell">Floodplain</router-link>
			/ Create
		</file-header>

		<fpcell-form :item="data"></fpcell-form>
	</project-container>
</template>