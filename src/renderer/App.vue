<script setup lang="ts">
	import { reactive, onMounted, onUnmounted, computed } from 'vue';
	import { useRoute, useRouter } from 'vue-router';
	import { useHelpers } from '@/helpers';
	const route = useRoute();
	const router = useRouter();
	const { formatters, runProcess } = useHelpers();

	onMounted(() => initRunProcessHandlers());	
	onUnmounted(() => removeRunProcessHandlers());

	let listeners:any = {
		loadFromContextMenu: undefined
	}

	function initRunProcessHandlers() {
		listeners.loadFromContextMenu = runProcess.loadFromContextMenu((stdData:any) => {
			router.push({ path: `/${stdData}` });
		});
	}

	function removeRunProcessHandlers() {
		if (listeners.loadFromContextMenu) listeners.loadFromContextMenu();
	}
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
