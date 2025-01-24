<script setup lang="ts">
	import { useRoute } from 'vue-router';
	const route = useRoute();
</script>

<template>
	<project-container>
		<div v-if="route.name == 'Fields'">
			<file-header input-file="field.fld" docs-path="hydrology/field.fld" use-io>
				Fields
			</file-header>

			<grid-view
				api-url="hydrology/fields"
				use-dynamic-headers 
				show-import-export default-csv-file="fields.csv" table-name="fld"  />
		</div>
		<router-view></router-view>
	</project-container>
</template>
