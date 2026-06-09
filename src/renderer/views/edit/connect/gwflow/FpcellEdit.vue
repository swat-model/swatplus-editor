<script setup lang="ts">
	import { reactive, onMounted, watch } from 'vue';
	import { useRoute } from 'vue-router';
	import { useHelpers } from '@/helpers';
	import FpcellForm from './FpcellForm.vue';

	const route = useRoute();
	const { api, currentProject, errors } = useHelpers();

	let data:any = reactive({
		page: {
			loading: false,
			error: null
		},
		item: {}
	});

	async function get() {
		if (route.params.id === undefined || route.params.comp_id === undefined) return;
		data.page.loading = true;
		data.page.error = null;

		try {
			const response = await api.get(`gwflow/fpcell/${route.params.id}/${route.params.comp_id}`, currentProject.getApiHeader());
			errors.log(response.data);

			data.item = response.data;
		} catch (error) {
			data.page.error = errors.logError(error, 'Unable to get floodplain cell properties from database.');
		}
		
		data.page.loading = false;
	}

	onMounted(async () => await get())
	watch(() => route.name, async () => await get())
	watch(() => route.params.id, async () => await get())
	watch(() => route.params.comp_id, async () => await get())
</script>

<template>
	<project-container :loading="data.page.loading" :load-error="data.page.error">
		<file-header input-file="floodplain.gw" docs-path="modflow" use-io>
			<router-link to="/edit/cons/gwflow">Groundwater Flow</router-link>
			/ <router-link to="/edit/cons/gwflow/fpcell">Floodplain</router-link>
			/ Edit
		</file-header>

		<fpcell-form is-update :item="data.item"></fpcell-form>
	</project-container>
</template>