<script setup lang="ts">
	import { useRoute } from 'vue-router';
	const route = useRoute();
</script>

<template>
	<project-container>
		<div v-if="$route.name == 'GwflowRescell'">
			<file-header input-file="gwflow.input" docs-path="modflow" use-io>
				<router-link to="/edit/cons/gwflow">Groundwater Flow</router-link>
				/ Reservoirs
			</file-header>
			
			<grid-view
				api-url="gwflow/rescell" :default-sort="['cell_id', 'asc']"
				use-dynamic-headers show-delete-all
				show-import-export default-csv-file="gwflow_rescells.csv" table-name="gwflow_rescell" import-primary-key="cell_id" />
		</div>
		<router-view></router-view>
	</project-container>
</template>
