<script setup lang="ts">
	import DecisionsGrid from './DecisionsGrid.vue';
	import { useRoute } from 'vue-router';
	const route = useRoute();
</script>

<template>
	<project-container>
		<div v-if="route.name == 'DecisionsFloCon'">
			<decisions-grid decisions-table="flo_con.dtl" description="Flow Conditions"></decisions-grid>
		</div>
		<router-view></router-view>
	</project-container>
</template>
