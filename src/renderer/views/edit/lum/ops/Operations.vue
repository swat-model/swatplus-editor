<script setup lang="ts">
	import { useRoute } from 'vue-router';
	const route = useRoute();
</script>

<template>
	<project-container>
		<div v-if="route.name === 'Operations'">
			<h1 class="file-header text-h5 d-flex align-end mb-6">
				Operations Databases
			</h1>

			<ul class="list-group">
				<li class="list-group-item bg-light"><router-link class="text-primary text-decoration-none" to="/edit/lum/ops/harvest">Harvest Operations</router-link></li>
				<li class="list-group-item bg-light"><router-link class="text-primary text-decoration-none" to="/edit/lum/ops/graze">Graze Operations</router-link></li>
				<li class="list-group-item bg-light"><router-link class="text-primary text-decoration-none" to="/edit/lum/ops/irrigation">Irrigation Operations</router-link></li>
				<li class="list-group-item bg-light"><router-link class="text-primary text-decoration-none" to="/edit/lum/ops/chemapp">Chemical Application Operations</router-link></li>
				<li class="list-group-item bg-light"><router-link class="text-primary text-decoration-none" to="/edit/lum/ops/fire">Fire Operations</router-link></li>
				<li class="list-group-item bg-light"><router-link class="text-primary text-decoration-none" to="/edit/lum/ops/sweep">Sweep Operations</router-link></li>
			</ul>
		</div>
		<router-view></router-view>
	</project-container>
</template>
