<script setup lang="ts">
	import { useRoute } from 'vue-router';
	const route = useRoute();
</script>

<template>
	<project-container>
		<div v-if="route.name == 'WaterAllocation'">
			<file-header input-file="water_allocation.wro" docs-path="water-allocation/water_allocation.wro" use-io>
				Water Allocation
			</file-header>

			<v-alert type="info" icon="$info" variant="tonal" border="start" class="mb-4">
				Water allocation tables are very specific to the watershed and new feature in SWAT+.
				We recommend working with the model development team if you are unsure.
				Because this is a new addition, the interface is still limited if you're trying to build a large table with many source and demand objects.
			</v-alert>

			<grid-view 
				api-url="water_rights/allocation"
				use-dynamic-headers></grid-view>
		</div>
		<router-view></router-view>
	</project-container>
</template>
