<script setup lang="ts">
	import { useRoute } from 'vue-router';
	const route = useRoute();
</script>

<template>
	<project-container>
		<div v-if="$route.name == 'BmpuserStr'">
			<file-header input-file="bmpuser.str" docs-path="structural/bmpuser.str" use-io>
				User Best Management Practices
			</file-header>

			<grid-view api-url="structural/bmpuser"
					   use-dynamic-headers
					   show-import-export default-csv-file="bmpuser.csv" table-name="bmpuser_str" />
		</div>
		<router-view></router-view>
	</project-container>
</template>
