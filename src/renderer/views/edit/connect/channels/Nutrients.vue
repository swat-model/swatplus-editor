<script setup lang="ts">
	
</script>

<template>
	<project-container>
		<div v-if="$route.name == 'ChannelsNutrients'">
			<file-header input-file="nutrients.cha" docs-path="connections/channels">
				<router-link to="/edit/cons/channels">Channels</router-link> 
				/ Nutrients
			</file-header>

			<grid-view 
				api-url="channels/nutrients"
				use-dynamic-headers 
				show-import-export default-csv-file="nutrients-cha.csv" table-name="nut_cha" />
		</div>
		<router-view></router-view>
	</project-container>
</template>
