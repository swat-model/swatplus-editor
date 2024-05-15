<script setup lang="ts">
	import { useRoute } from 'vue-router';
	const route = useRoute();
</script>

<template>
	<project-container>
		<div v-if="$route.name == 'ConstituentsSaltsResIni'">
			<file-header input-file="constituents.cs" docs-path="constituents" use-io>
				<router-link to="/edit/constituents/salts">Salt Constituents</router-link>
				/ Reservoir Initial Conditions
			</file-header>

			<grid-view 
				api-url="salts/salt_res_ini"
				use-dynamic-headers
				show-import-export default-csv-file="salt_res_ini.csv" table-name="salt_res_ini" />
		</div>
		<router-view></router-view>
	</project-container>
</template>