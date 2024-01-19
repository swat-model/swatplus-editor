<script setup lang="ts">
	import { reactive } from 'vue';
	import SoilsForm from './SoilsForm.vue';

	let item:any = reactive({
		name: null,
		hyd_grp: null,
		dp_tot: 0,
		anion_excl: 0,
		perc_crk: 0,
		texture: null,
		description: null
	});
</script>

<template>
	<project-container>
		<file-header input-file="soils.sol" docs-path="soils/soils.sol" use-io>
			<router-link to="/edit/soils/soils">Soils</router-link>
			/ Create
		</file-header>

		<soils-form :item="item"></soils-form>
	</project-container>
</template>
