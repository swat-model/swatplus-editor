<script setup lang="ts">
	import { useRoute } from 'vue-router';
	const route = useRoute();
</script>

<template>
	<project-container>
		<div v-if="route.name === 'SoftCalibration'">
			<file-header input-file="codes.sft" docs-path="calibration" use-io>
				Soft Calibration
			</file-header>
			
			<p>
				The soft calibration requires 10-12 simulations and is a simple, heuristic, one-at-a-time procedure. 
				Each process has one or two parameters and each is looped through a couple of times. After the soft calibration is complete, 
				the hard (daily gage) calibration should only require some adjustments of the peaks and recessions.
			</p>

			<ul class="list-group">
				<li class="list-group-item bg-light"><router-link class="text-primary text-decoration-none" to="/edit/change/soft/wb">Water Balance</router-link></li>
				<li class="list-group-item bg-light"><router-link class="text-primary text-decoration-none" to="/edit/change/soft/plant">Plant Growth</router-link></li>
			</ul>
		</div>
		<router-view></router-view>
	</project-container>
</template>
