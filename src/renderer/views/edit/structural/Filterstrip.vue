<script setup lang="ts">
	import { useRoute } from 'vue-router';
	const route = useRoute();
</script>

<template>
	<project-container>
		<div v-if="route.name == 'FilterstripStr'">
			<file-header input-file="filterstrip.str" docs-path="structural-practices/filterstrip.str" use-io>
				Filter Strips
			</file-header>

			<grid-view 
				api-url="structural/filterstrip"
				use-dynamic-headers
				show-import-export default-csv-file="filterstrip.csv" table-name="filterstrip_str" />
		</div>
		<router-view></router-view>
	</project-container>
</template>