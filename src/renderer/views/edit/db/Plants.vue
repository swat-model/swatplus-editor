<script setup lang="ts">
	import { useRoute } from 'vue-router';
	const route = useRoute();
</script>

<template>
	<project-container>
		<div v-if="route.name === 'Plants'">
			<file-header input-file="plants.plt" docs-path="databases/plants.plt" use-io>
				Plants
			</file-header>

			<grid-view 
				api-url="db/plants"
				use-dynamic-headers 
				show-import-export default-csv-file="plants.csv" table-name="plant" />
		</div>
		<router-view></router-view>
	</project-container>
</template>
