<script setup lang="ts">
	import { useRoute } from 'vue-router';
	const route = useRoute();
</script>

<template>
	<project-container>
		<div v-if="route.name == 'OperationsFire'">
			<file-header input-file="fire.ops" docs-path="management-practices/fire.ops" use-io>
				<router-link to="/edit/lum/ops">Operations</router-link> 
				/ Fire
			</file-header>

			<grid-view 
				api-url="ops/fire"
				use-dynamic-headers
				show-import-export default-csv-file="fire.ops" table-name="fire_ops" />
		</div>
		<router-view></router-view>
	</project-container>
</template>
