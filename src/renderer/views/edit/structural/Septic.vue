<script setup lang="ts">
	import { useRoute } from 'vue-router';
	const route = useRoute();
</script>

<template>
	<project-container>
		<div v-if="$route.name == 'SepticStr'">
			<file-header input-file="septic.str" docs-path="structural/septic.str" use-io>
				Septic Systems
			</file-header>

			<grid-view api-url="structural/septic"
					   use-dynamic-headers
					   show-import-export default-csv-file="septic.csv" table-name="septic_str" />
		</div>
		<router-view></router-view>
	</project-container>
</template>
