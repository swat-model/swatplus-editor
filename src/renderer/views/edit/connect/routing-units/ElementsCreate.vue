<script setup lang="ts">
	import { reactive, onMounted } from 'vue';
	import { usePlugins } from '../../../../plugins';
	import ElementsForm from './ElementsForm.vue';

	const { api, currentProject, errors, utilities } = usePlugins();

	let data:any = reactive({
		page: {
			loading: false,
			error: null
		},
		item: {
			obj_typ: 'hru',
			hyd_typ: 'tot',
			frac: 0
		},
		objTypes: []
	});

	async function get() {
		data.page.loading = true;
		data.page.error = null;

		try {
			const response = await api.get(`definitions/codes/connect/obj_typ/${utilities.appPathUrl}`);
			data.objTypes = response.data;
		} catch (error) {
			data.page.error = errors.logError(error, 'Unable to get landscape unit from database.');
		}
			
		data.page.loading = false;
	}

	onMounted(async () => await get())
</script>

<template>
	<project-container :loading="data.page.loading" :load-error="data.page.error">
		<file-header input-file="rout_unit.ele" docs-path="connections/routing-units">
			<router-link to="/edit/cons/routing-units">Routing Units</router-link> / 
			<router-link to="/edit/cons/routing-units/elements">Elements</router-link>
			/ Create
		</file-header>

		<elements-form :item="data.item" :obj-types="data.objTypes"></elements-form>
	</project-container>
</template>