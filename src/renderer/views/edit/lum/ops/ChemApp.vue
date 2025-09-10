<script setup lang="ts">
	import { useRoute } from 'vue-router';
	const route = useRoute();
</script>

<template>
	<project-container>
		<div v-if="route.name == 'OperationsChemApp'">
			<file-header input-file="chem_app.ops" docs-path="management-practices/chem_app.ops" use-io>
				<router-link to="/edit/lum/ops">Operations</router-link> 
				/ Chemical Applications
			</file-header>

			<grid-view 
				api-url="ops/chemapp"
				use-dynamic-headers
				show-import-export default-csv-file="chem_app.ops" table-name="chem_app_ops" />
		</div>
		<router-view></router-view>
	</project-container>
</template>
