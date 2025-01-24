<script setup lang="ts">
	import { useRoute } from 'vue-router';
	const route = useRoute();
</script>

<template>
	<project-container>
		<div v-if="route.name == 'Soils'">
			<file-header input-file="soils.sol" docs-path="soils/soils.sol" use-io>
				Soils
			</file-header>

			<grid-view 
				api-url="soils/items"
				use-dynamic-headers></grid-view>
		</div>
		<router-view></router-view>
	</project-container>
</template>
