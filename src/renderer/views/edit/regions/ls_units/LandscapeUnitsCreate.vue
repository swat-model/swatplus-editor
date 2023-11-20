<script setup lang="ts">
	import { reactive } from 'vue';
	import LandscapeUnitsForm from './LandscapeUnitsForm.vue';

	let data:any = reactive({
		name: <string|null>null,
		area: <number>0,
		elements: <any[]>[]
	});
</script>

<template>
	<project-container>
		<file-header input-file="ls_unit.def" docs-path="landscape-units/ls_unit.def" use-io>
			<router-link to="/edit/regions/ls_units">Landscape Units</router-link>
			/ Create
		</file-header>

		<landscape-units-form :item="data"></landscape-units-form>
	</project-container>
</template>
