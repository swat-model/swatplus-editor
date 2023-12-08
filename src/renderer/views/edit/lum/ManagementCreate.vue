<script setup lang="ts">
	import { reactive } from 'vue';
	import ManagementForm from './ManagementForm.vue';

	let data:any = reactive({
		id: null,
		name: null,
		auto_ops: [],
		operations: []
	});
</script>

<template>
	<project-container>
		<file-header input-file="management.sch" docs-path="land-use-management#management-schedules">
			<router-link to="/edit/lum/mgt">Management Schedules</router-link>
			/ Create
		</file-header>

		<management-form :item="data.item"></management-form>
	</project-container>
</template>
