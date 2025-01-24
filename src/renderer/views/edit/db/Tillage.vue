<script setup lang="ts">
	import { useRoute } from 'vue-router';
	const route = useRoute();
</script>

<template>
	<project-container>
		<div v-if="route.name == 'Tillage'">
			<file-header input-file="tillage.til" docs-path="databases/tillage.til" use-io>
				Tillage
			</file-header>

			<grid-view 
				api-url="db/tillage"
				use-dynamic-headers
				show-import-export default-csv-file="tillage.csv" table-name="till" />
		</div>
		<router-view></router-view>
	</project-container>
</template>