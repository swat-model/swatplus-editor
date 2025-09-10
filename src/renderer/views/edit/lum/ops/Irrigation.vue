<script setup lang="ts">
	import { useRoute } from 'vue-router';
	const route = useRoute();
</script>

<template>
	<project-container>
		<div v-if="route.name == 'OperationsIrrigation'">
			<file-header input-file="irr.ops" docs-path="management-practices/irr.ops" use-io>
				<router-link to="/edit/lum/ops">Operations</router-link> 
				/ Irrigation
			</file-header>

			<grid-view 
				api-url="ops/irrigation"
				use-dynamic-headers 
				show-import-export default-csv-file="irr.ops" table-name="irr_ops" />
		</div>
		<router-view></router-view>
	</project-container>
</template>
