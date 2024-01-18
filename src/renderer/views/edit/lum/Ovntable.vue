<script setup lang="ts">
	import { useRoute } from 'vue-router';
	const route = useRoute();
</script>

<template>
	<project-container>
		<div v-if="$route.name == 'Ovntable'">
			<file-header input-file="ovn_table.lum" docs-path="/landuse-and-management/ovn_table.lum" use-io>
				Manning's n Tables
			</file-header>

			<grid-view 
				api-url="lum/ovntable"
				use-dynamic-headers 
				show-import-export default-csv-file="ovn_table.csv" table-name="ovntable" />
		</div>
		<router-view></router-view>
	</project-container>
</template>
