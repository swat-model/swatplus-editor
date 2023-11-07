<script setup lang="ts">
	import { useRoute } from 'vue-router';
	import { useFormatters } from '@/helpers/formatters';
	const route = useRoute();
	const formatters = useFormatters();
</script>

<template>
	<div id="app">
		<v-app id="mainContainer">
			<div v-if="!formatters.isNullOrEmpty(route.name) && route.name?.toString().includes('TableBrowser')">
				<router-view></router-view>
			</div>
			<div v-else>
				<router-view></router-view>
			</div>
		</v-app>
	</div>
</template>
