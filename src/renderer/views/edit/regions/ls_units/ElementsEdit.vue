<script setup lang="ts">
	import { reactive, onMounted, watch } from 'vue';
	import { useRoute } from 'vue-router';
	import { useHelpers } from '@/helpers';
	import ElementsForm from './ElementsForm.vue';

	const route = useRoute();
	const { api, currentProject, errors, utilities } = useHelpers();

	let data:any = reactive({
		paths: {
			data: 'regions/ls_units/elements'
		},
		page: {
			loading: false,
			error: null
		},
		item: <any>{},
		objTypes: <any[]>[]
	});

	async function get() {
		if (route.params.id === undefined) return;
		data.page.loading = true;
		data.page.error = null;

		try {
			const response = await api.get(`${data.paths.data}/${route.params.id}`, currentProject.getApiHeader());
			data.item = response.data;
			data.item.ls_unit_def_name = response.data.ls_unit_def !== null ? response.data.ls_unit_def.name : null;

			const response2 = await api.get(`definitions/codes/connect/obj_typ/${utilities.appPathUrl}`);
			data.objTypes = response2.data;
		} catch (error) {
			data.page.error = errors.logError(error, 'Unable to get project information from database.');
		}
			
		data.page.loading = false;
	}

	onMounted(async () => await get())
	watch(() => route.path, async () => await get())
</script>

<template>
	<project-container :loading="data.page.loading" :load-error="data.page.error">
		<file-header input-file="ls_unit.ele" docs-path="landscape-units/ls_unit.ele" use-io>
			<router-link to="/edit/regions/ls_units">Landscape Units</router-link> /
			<router-link to="/edit/regions/ls_units/elements">Elements</router-link>
			/ Edit
		</file-header>

		<elements-form is-update :item="data.item" :obj-types="data.objTypes"></elements-form>
	</project-container>
</template>
