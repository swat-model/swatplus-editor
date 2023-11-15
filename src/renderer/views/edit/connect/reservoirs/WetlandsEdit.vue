<script setup lang="ts">
	import { reactive, onMounted, watch } from 'vue';
	import { useRoute } from 'vue-router';
	import { useHelpers } from '@/helpers';
	import WetlandsForm from './WetlandsForm.vue';

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
		if (route.params.id === undefined) return;
		data.page.loading = true;
		data.page.error = null;

		try {
			const response = await api.get(`reservoirs/wetlands/${route.params.id}`, currentProject.getApiHeader());
			errors.log(response.data);

			data.item = {
				id: response.data.id,
				name: response.data.name,
				init_name: response.data.init != null ? response.data.init.name : '',
				rel_name: response.data.rel != null ? response.data.rel.name : '',
				hyd_name: response.data.hyd != null ? response.data.hyd.name : '',
				sed_name: response.data.sed != null ? response.data.sed.name : '',
				nut_name: response.data.nut != null ? response.data.nut.name : '',
				description: response.data.description
			};
		} catch (error) {
			data.page.error = errors.logError(error, 'Unable to get properties from database.');
		}
		
		data.page.loading = false;
	}

	onMounted(async () => await get())
	watch(() => route.name, async () => await get())
	watch(() => route.params.id, async () => await get())
</script>

<template>
	<project-container :loading="data.page.loading" :load-error="data.page.error">
		<file-header input-file="wetland.wet" docs-path="wetlands/wetland.wet" use-io>
			<router-link to="/edit/cons/reservoirs">Reservoirs</router-link> / 
			<router-link to="/edit/cons/reservoirs/wetlands">Wetlands</router-link>
			/ Edit
		</file-header>

		<wetlands-form is-update :item="data.item"></wetlands-form>
	</project-container>
</template>
