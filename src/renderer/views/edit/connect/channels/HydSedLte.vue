<script setup lang="ts">
	import { useRoute } from 'vue-router';
	const route = useRoute();
</script>

<template>
	<project-container>
		<div v-if="route.name == 'ChannelsHydSedLte'">
			<file-header input-file="hyd-sed-lte.cha" docs-path="channels/hyd-sed-lte.cha" use-io>
				<router-link to="/edit/cons/channels">Channels</router-link> 
				/ Hydrology &amp; Sediment
			</file-header>

			<grid-view 
				api-url="channels/hydsed"
				use-dynamic-headers 
				show-import-export default-csv-file="hyd-sed-lte-cha.csv" table-name="hyd_sed_lte_cha" />
		</div>
		<router-view></router-view>
	</project-container>
</template>
