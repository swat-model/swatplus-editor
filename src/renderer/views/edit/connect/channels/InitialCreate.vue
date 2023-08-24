<script setup lang="ts">
	import { reactive } from 'vue';
	import InitialForm from './InitialForm.vue';

	let data:any = reactive({
		name: null,
		description: null,
		org_min_name: null,
		pest_name: null,
		path_name: null,
		hmet_name: null,
		salt_name: null
	});

	
</script>

<template>
	<project-container>
		<file-header input-file="initial.cha" docs-path="connections/channels">
			<router-link to="/edit/cons/channels">Channels</router-link> / 
			<router-link to="/edit/cons/channels/initial">Initial</router-link>
			/ Create
		</file-header>

		<initial-form :item="data"></initial-form>
	</project-container>
</template>