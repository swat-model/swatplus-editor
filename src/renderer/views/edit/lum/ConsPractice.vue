<script setup lang="ts">
	import { useRoute } from 'vue-router';
	const route = useRoute();
</script>

<template>
	<project-container>
		<div v-if="route.name == 'ConsPractice'">
			<file-header input-file="cons_practice.lum" docs-path="/landuse-and-management/cons_practice.lum" use-io>
				Conservation Practices
			</file-header>

			<grid-view 
				api-url="lum/cons_prac"
				use-dynamic-headers 
				show-import-export default-csv-file="cons_practice.csv" table-name="cons_prac" />
		</div>
		<router-view></router-view>
	</project-container>
</template>
