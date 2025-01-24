<script setup lang="ts">
	import { useRoute } from 'vue-router';
	const route = useRoute();
</script>

<template>
	<project-container>
		<div v-if="route.name == 'ConstituentsSaltsChannelIni'">
			<file-header input-file="constituents.cs" docs-path="constituents" use-io>
				<router-link to="/edit/constituents/salts">Salt Constituents</router-link>
				/ Channel Initial Conditions
			</file-header>

			<grid-view 
				api-url="salts/salt_channel_ini"
				use-dynamic-headers
				show-import-export default-csv-file="salt_channel_ini.csv" table-name="salt_channel_ini" />
		</div>
		<router-view></router-view>
	</project-container>
</template>