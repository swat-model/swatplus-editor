<script setup lang="ts">
	import { useRoute } from 'vue-router';
	const route = useRoute();
</script>

<template>
	<project-container>
		<div v-if="$route.name == 'Fertilizer'">
			<file-header input-file="fertilizer.frt" docs-path="databases/fertilzer.frt" use-io>
				Fertilizer
			</file-header>

			<grid-view 
				api-url="db/fertilizer"
				use-dynamic-headers
				show-import-export default-csv-file="fertilizer.csv" table-name="fert" />
		</div>
		<router-view></router-view>
	</project-container>
</template>