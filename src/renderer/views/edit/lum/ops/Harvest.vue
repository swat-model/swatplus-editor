<script setup lang="ts">
	import { useRoute } from 'vue-router';
	const route = useRoute();
</script>

<template>
	<project-container>
		<div v-if="$route.name == 'OperationsHarvest'">
			<file-header input-file="harv.ops" docs-path="management-practices/harv.ops" use-io>
				<router-link to="/edit/lum/ops">Operations</router-link> 
				/ Harvest
			</file-header>

			<grid-view 
				api-url="ops/harvest"
				use-dynamic-headers 
				show-import-export default-csv-file="harv.ops" table-name="harv_ops" />
		</div>
		<router-view></router-view>
	</project-container>
</template>
