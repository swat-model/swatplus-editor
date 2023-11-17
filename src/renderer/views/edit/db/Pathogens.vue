<script setup lang="ts">
	import { useRoute } from 'vue-router';
	const route = useRoute();
</script>

<template>
	<project-container>
		<div v-if="$route.name == 'Pathogens'">
			<file-header input-file="pathogens.pth" docs-path="databases/pathogens.pth" use-io>
				Pathogens
			</file-header>

			<grid-view api-url="db/pathogens"
					   use-dynamic-headers
					   show-import-export default-csv-file="pathogens.csv" table-name="path" />
		</div>
		<router-view></router-view>
	</project-container>
</template>
