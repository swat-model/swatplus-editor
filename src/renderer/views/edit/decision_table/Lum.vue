<script setup lang="ts">
	import DecisionsGrid from './DecisionsGrid.vue';
	import { useRoute } from 'vue-router';
	const route = useRoute();
</script>

<template>
	<project-container>
		<div v-if="$route.name == 'DecisionsLum'">
			<decisions-grid decisions-table="lum.dtl" description="Land Use Management"></decisions-grid>
		</div>
		<router-view></router-view>
	</project-container>
</template>
