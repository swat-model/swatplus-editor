<script setup lang="ts">
	import { useRoute } from 'vue-router';
	const route = useRoute();
</script>

<template>
	<project-container>
		<div v-if="route.name == 'ConstituentsSaltsAquIni'">
			<file-header input-file="constituents.cs" docs-path="constituents" use-io>
				<router-link to="/edit/constituents/salts">Salt Constituents</router-link>
				/ Aquifer Initial Conditions
			</file-header>

			<grid-view 
				api-url="salts/salt_aqu_ini"
				use-dynamic-headers
				show-import-export default-csv-file="salt_aqu_ini.csv" table-name="salt_aqu_ini" />
		</div>
		<router-view></router-view>
	</project-container>
</template>