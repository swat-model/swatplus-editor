<script setup lang="ts">
	
</script>

<template>
	<project-container>
		<div v-if="$route.name == 'ChannelsHydSedLte'">
			<file-header input-file="hyd-sed-lte.cha" docs-path="connections/channels">
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
