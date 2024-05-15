<script setup lang="ts">
	import { useRoute } from 'vue-router';
	const route = useRoute();
</script>

<template>
	<project-container>
		<div v-if="$route.name == 'ConstituentsSaltsHruIni'">
			<file-header input-file="constituents.cs" docs-path="constituents" use-io>
				<router-link to="/edit/constituents/salts">Salt Constituents</router-link>
				/ HRU Initial Conditions
			</file-header>

			<grid-view 
				api-url="salts/salt_hru_ini_cs"
				use-dynamic-headers
				show-import-export default-csv-file="salt_hru_ini_cs.csv" table-name="salt_hru_ini_cs" />
		</div>
		<router-view></router-view>
	</project-container>
</template>