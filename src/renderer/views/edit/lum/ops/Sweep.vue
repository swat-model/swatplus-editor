<script setup lang="ts">
	import { useRoute } from 'vue-router';
	const route = useRoute();
</script>

<template>
	<project-container>
		<div v-if="route.name == 'OperationsSweep'">
			<file-header input-file="sweep.ops" docs-path="management-practices/sweep.ops" use-io>
				<router-link to="/edit/lum/ops">Operations</router-link> 
				/ Sweep
			</file-header>

			<grid-view 
				api-url="ops/sweep"
				use-dynamic-headers 
				show-import-export default-csv-file="sweep.ops" table-name="sweep_ops" />
		</div>
		<router-view></router-view>
	</project-container>
</template>
