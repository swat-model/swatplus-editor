<script setup lang="ts">
	import { useRoute } from 'vue-router';
	const route = useRoute();
</script>

<template>
	<project-container>
		<div v-if="route.name == 'TiledrainStr'">
			<file-header input-file="tiledrain.str" docs-path="structural-practices/tiledrain.str" use-io>
				Tile Drains
			</file-header>

			<grid-view api-url="structural/tiledrain"
					   use-dynamic-headers
					   show-import-export default-csv-file="tiledrain.csv" table-name="tiledrain_str" />
		</div>
		<router-view></router-view>
	</project-container>
</template>
