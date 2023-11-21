<script setup lang="ts">
	import { useRoute } from 'vue-router';
	const route = useRoute();
</script>

<template>
	<project-container>
		<div v-if="$route.name == 'GrassedwwStr'">
			<file-header input-file="grassedww.str" docs-path="structural/grassedww.str" use-io>
				Grassed Waterways
			</file-header>

			<grid-view api-url="structural/grassedww"
					   use-dynamic-headers
					   show-import-export default-csv-file="grassedww.csv" table-name="grassedww_str" />
		</div>
		<router-view></router-view>
	</project-container>
</template>
