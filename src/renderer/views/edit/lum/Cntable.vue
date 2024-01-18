<script setup lang="ts">
	import { useRoute } from 'vue-router';
	const route = useRoute();
</script>

<template>
	<project-container>
		<div v-if="$route.name == 'Cntable'">
			<file-header input-file="cntable.lum" docs-path="/landuse-and-management/cntable.lum" use-io>
				Curve Numbers
			</file-header>

			<grid-view 
				api-url="lum/cntable"
				use-dynamic-headers 
				show-import-export default-csv-file="cntable.csv" table-name="cntable" />
		</div>
		<router-view></router-view>
	</project-container>
</template>
