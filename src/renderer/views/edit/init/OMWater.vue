<script setup lang="ts">
	import { useRoute } from 'vue-router';
	const route = useRoute();
</script>

<template>
	<project-container>
		<div v-if="$route.name == 'InitOMWater'">
			<file-header input-file="om_water.ini" docs-path="constituents/om_water.ini" use-io>
				Organic Mineral Water
			</file-header>

			<grid-view 
				api-url="init/om_water"
				use-dynamic-headers
				show-import-export default-csv-file="om_water_ini.csv" table-name="om_water_ini" />
		</div>
		<router-view></router-view>
	</project-container>
</template>
