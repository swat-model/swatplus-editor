<script setup lang="ts">
	import DecisionsGrid from './DecisionsGrid.vue';
	import { useRoute } from 'vue-router';
	const route = useRoute();
</script>

<template>
	<project-container>
		<div v-if="route.name == 'DecisionsScenLu'">
			<decisions-grid decisions-table="scen_lu.dtl" description="Scenario Land Use"></decisions-grid>
		</div>
		<router-view></router-view>
	</project-container>
</template>
