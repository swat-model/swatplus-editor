<script setup lang="ts">
	import DecisionsGrid from './DecisionsGrid.vue';
	import { useRoute } from 'vue-router';
	const route = useRoute();
</script>

<template>
	<project-container>
		<div v-if="$route.name == 'DecisionsResRel'">
			<decisions-grid decisions-table="res_rel.dtl" description="Reservoir Release"></decisions-grid>
		</div>
		<router-view></router-view>
	</project-container>
</template>
