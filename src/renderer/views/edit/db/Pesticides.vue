<script setup lang="ts">
	import { useRoute } from 'vue-router';
	const route = useRoute();
</script>

<template>
	<project-container>
		<div v-if="$route.name == 'Pesticides'">
			<file-header input-file="pesticide.pes" docs-path="databases/pesticide.pes">
				Pesticides
			</file-header>

			<grid-view api-url="db/pesticides"
					   use-dynamic-headers
					   show-import-export default-csv-file="pesticides.csv" table-name="pest" />
		</div>
		<router-view></router-view>
	</project-container>
</template>
