<script setup lang="ts">
	import { useRoute } from 'vue-router';
	const route = useRoute();
</script>

<template>
	<project-container>
		<div v-if="route.name == 'GwflowZone'">
			<file-header input-file="gwflow.input" docs-path="modflow" use-io>
				<router-link to="/edit/cons/gwflow">Groundwater Flow</router-link>
				/ Zones
			</file-header>

			<p>
				You cannot add or remove zones because they are set in QSWAT+, however you may edit the aquifer and streambed values.
			</p>
			
			<grid-view
				api-url="gwflow/zones" :default-sort="['zone_id', 'asc']"
				use-dynamic-headers hide-create hide-delete
				show-import-export default-csv-file="gwflow_zones.csv" table-name="gwflow_zone" import-primary-key="zone_id" />
		</div>
		<router-view></router-view>
	</project-container>
</template>
