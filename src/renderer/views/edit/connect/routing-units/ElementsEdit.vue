<script setup lang="ts">
	import { reactive, onMounted, watch } from 'vue';
	import { useRoute } from 'vue-router';
	import { usePlugins } from '../../../../plugins';
	import ElementsForm from './ElementsForm.vue';

	const route = useRoute();
	const { api, currentProject, errors, utilities } = usePlugins();

	let data:any = reactive({
		page: {
			loading: false,
			error: null
		},
		item: {},
		objTypes: []
	});

	async function get() {
		if (route.params.id === undefined) return;
		data.page.loading = true;
		data.page.error = null;

		try {
			const response = await api.get(`routing-units/elements/${route.params.id}`, currentProject.getApiHeader());
			data.item = response.data;
			data.item.rtu_name = response.data.rtu != null ? response.data.rtu.name : '';
			data.item.dlr_name = response.data.dlr != null ? response.data.dlr.name : '';

			const response2 = await api.get(`definitions/codes/connect/obj_typ/${utilities.appPathUrl}`);
			data.objTypes = response2.data;
		} catch (error) {
			data.page.error = errors.logError(error, 'Unable to get project information from database.');
		}
		
		data.page.loading = false;
	}

	onMounted(async () => await get())
	watch(() => route.name, async () => await get())
	watch(() => route.params.id, async () => await get())
</script>

<template>
	<project-container :loading="data.page.loading" :load-error="data.page.error">
		<file-header input-file="rout_unit.ele" docs-path="connections/routing-units">
			<router-link to="/edit/cons/routing-units">Routing Units</router-link> / 
			<router-link to="/edit/cons/routing-units/elements">Elements</router-link>
			/ Edit
		</file-header>

		<elements-form is-update :item="data.item" :obj-types="data.objTypes"></elements-form>
	</project-container>
</template>