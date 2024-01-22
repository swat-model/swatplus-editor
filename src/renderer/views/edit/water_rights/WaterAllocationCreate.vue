<script setup lang="ts">
	import { reactive } from 'vue';
	import WaterAllocationForm from './WaterAllocationForm.vue';

	let item:any = reactive({
		name: null,
		rule_typ: null,
		cha_ob: false
	});
</script>

<template>
	<project-container>
		<file-header input-file="water_allocation.wro" docs-path="water-allocation/water_allocation.wro" use-io>
			<router-link to="/edit/water-rights/allocation">Water Allocation</router-link>
			/ Create
		</file-header>

		<water-allocation-form :item="item"></water-allocation-form>
	</project-container>
</template>