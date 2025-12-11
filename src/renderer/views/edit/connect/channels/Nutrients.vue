<script setup lang="ts">
	import { useRoute } from 'vue-router';
	const route = useRoute();
</script>

<template>
	<project-container>
		<div v-if="route.name == 'ChannelsNutrients'">
			<file-header input-file="nutrients.cha" docs-path="channels/nutrients.cha" use-io>
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
