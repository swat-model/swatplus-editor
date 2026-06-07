<script setup lang="ts">
// import djiImage from '../assets/dji.png'; // Import gambar sebagai variabel
import { onMounted, onUnmounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useHelpers } from '@/helpers';
import { useHeaderStore } from '@/store/header';


const route = useRoute();
const router = useRouter();
const { formatters, runProcess } = useHelpers();
const headerStore = useHeaderStore();

onMounted(() => {
  initRunProcessHandlers();

});
onUnmounted(() => removeRunProcessHandlers()

);

let listeners: any = {
	loadFromContextMenu: undefined
}

function initRunProcessHandlers() {
	listeners.loadFromContextMenu = runProcess.loadFromContextMenu((stdData: any) => {
		router.push({ path: `/${stdData}` });
	});
}

function removeRunProcessHandlers() {
	if (listeners.loadFromContextMenu) listeners.loadFromContextMenu();
}

// Cek apakah route saat ini adalah MapView
const isMapView = computed(() => route.name?.toString().includes('MapView'));
</script>

<template>
	<div id="app">
		<v-app id="mainContainer">
			<v-main>
				<header class="app-header">
					<img :src="headerStore.headerImage" class="header-image" />
				</header>
				<main class="app-content">
					<div v-if="route.path === '/map'" class="is-map-page">
						<router-view></router-view>
					</div>
					
					<div v-else-if="route.name?.toString().includes('TableBrowser')" class="table-container">
						<router-view></router-view>
					</div>
					
					<div v-else>
						<router-view></router-view>
					</div>
				</main>
			</v-main>
		</v-app>
	</div>
</template>

<style scoped>
#mainContainer {
    height: 100vh;
    display: flex;
    flex-direction: column;
	/* display: grid; */
    /* Baris pertama header (150px),  */
    /* grid-template-rows: 150px 1fr; */
    /* overflow: hidden;  */
}

/* Memaksa v-main untuk mengisi sisa ruang setelah header (jika ada header lain) */
:deep(.v-main), :deep(.v-main__wrap) {
    flex: 1;
    display: flex;
    flex-direction: column;
	/* v-main mengisi grid area kedua */
    /* display: grid; */
    /* grid-template-rows: 1fr; */
    /* overflow: hidden; */
	min-height: 0;
}

.app-header {
    width: 100%;
    height: 150px; /* Tinggi tetap */
    flex-shrink: 0; /* Header tidak akan mengecil */
    z-index: 10;
    background-color: #f5f5f5;
}

.header-image {
	width: 100%;
	height: 100%;
	object-fit: fill;
}

.app-content {
    flex: 1; 
    display: flex;
    flex-direction: column;
    overflow-y: auto; 
	/* display: grid; */
    /* grid-template-rows: 1fr; */
    /* overflow-x: hidden; */
	min-height: 0;
}

.is-map-page {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    height: 100%;
}

.is-map-page > div { /* Target langsung ke elemen di dalam router-view */
    flex: 1;
    display: flex;
    flex-direction: column;
}

/* Pastikan router-view mengisi penuh .app-content */
/* .app-content > div { */
    /* flex: 1; */
    /* display: flex; */
    /* flex-direction: column; */
	/* overflow: hidden; */
/* } */
</style>