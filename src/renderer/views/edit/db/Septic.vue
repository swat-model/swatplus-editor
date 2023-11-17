<script setup lang="ts">
	import { useRoute } from 'vue-router';
	const route = useRoute();
</script>

<template>
	<project-container>
		<div v-if="$route.name == 'Septic'">
			<file-header input-file="septic.sep" docs-path="databases/septic.sep" use-io>
				Septic
			</file-header>

			<grid-view api-url="db/septic"
					   use-dynamic-headers
					   show-import-export default-csv-file="septic.csv" table-name="sep" />
		</div>
		<router-view></router-view>
	</project-container>
</template>
