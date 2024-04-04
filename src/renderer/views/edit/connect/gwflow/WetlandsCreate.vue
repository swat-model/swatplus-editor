<script setup lang="ts">
	import { reactive } from 'vue';
	import WetlandsForm from './WetlandsForm.vue';

	let data:any = reactive({
		wet_id: null,
		wet_name: '',
		thickness: 0,
	});

	
</script>

<template>
	<project-container>
		<file-header input-file="gwflow.wetland" docs-path="modflow" use-io>
			<router-link to="/edit/cons/gwflow">Groundwater Flow</router-link>
			/ <router-link to="/edit/cons/gwflow/wetlands">Wetlands</router-link>
			/ Create
		</file-header>

		<wetlands-form :item="data"></wetlands-form>
	</project-container>
</template>