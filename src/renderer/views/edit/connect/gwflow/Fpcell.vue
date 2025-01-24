<script setup lang="ts">
	import { useRoute } from 'vue-router';
	const route = useRoute();
</script>

<template>
	<project-container>
		<div v-if="route.name == 'GwflowFpcell'">
			<file-header input-file="gwflow.floodplain" docs-path="modflow" use-io>
				<router-link to="/edit/cons/gwflow">Groundwater Flow</router-link>
				/ Floodplain
			</file-header>
			
			<grid-view
				api-url="gwflow/fpcell" :default-sort="['cell_id', 'asc']"
				use-dynamic-headers show-delete-all
				show-import-export default-csv-file="gwflow_floodplain.csv" table-name="gwflow_fpcell" import-primary-key="cell_id" />
		</div>
		<router-view></router-view>
	</project-container>
</template>
