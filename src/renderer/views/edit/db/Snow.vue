<script setup lang="ts">
	import { useRoute } from 'vue-router';
	const route = useRoute();
</script>

<template>
	<project-container>
		<div v-if="route.name == 'Snow'">
			<file-header input-file="snow.sno" docs-path="databases/snow.sno">
				Snow
			</file-header>

			<grid-view api-url="db/snow"
					   use-dynamic-headers
					   show-import-export default-csv-file="snow.csv" table-name="snow" />
		</div>
		<router-view></router-view>
	</project-container>
</template>
