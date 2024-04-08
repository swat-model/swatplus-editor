<script setup lang="ts">
	import { reactive } from 'vue';
	import RescellForm from './RescellForm.vue';

	let data:any = reactive({
		cell_id: 1,
		res_name: null,
		res_stage: 0,
	});

	
</script>

<template>
	<project-container>
		<file-header input-file="gwflow.rescells" docs-path="modflow" use-io>
			<router-link to="/edit/cons/gwflow">Groundwater Flow</router-link>
			/ <router-link to="/edit/cons/gwflow/rescell">Reservoirs</router-link>
			/ Create
		</file-header>

		<rescell-form :item="data"></rescell-form>
	</project-container>
</template>