<script setup lang="ts">
	import { useRoute } from 'vue-router';
	const route = useRoute();
</script>

<template>
	<project-container>
		<div v-if="route.name == 'GwflowCells'">
			<file-header input-file="cells.gw" docs-path="modflow" use-io>
				<router-link to="/edit/cons/gwflow">Groundwater Flow</router-link>
				/ Cells
			</file-header>

			<p>
				You cannot add or remove cells because they are set in QSWAT+, however you may edit the cell properties.
			</p>
			
			<grid-view
				api-url="gwflow/cells" :default-sort="['cell_id', 'asc']"
				use-dynamic-headers hide-create hide-delete
				show-import-export default-csv-file="gwflow_cells.csv" table-name="gwflow_cell" import-primary-key="cell_id" />
		</div>
		<router-view></router-view>
	</project-container>
</template>
