<script setup lang="ts">
	import { useRoute } from 'vue-router';
	const route = useRoute();
</script>

<template>
	<project-container>
		<div v-if="route.name == 'Urban'">
			<file-header input-file="urban.urb" docs-path="databases/urban.urb" use-io>
				Urban
			</file-header>

			<grid-view 
				api-url="db/urban"
				use-dynamic-headers 
				show-import-export default-csv-file="urban.csv" table-name="urban" />
		</div>
		<router-view></router-view>
	</project-container>
</template>