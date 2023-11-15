<script setup lang="ts">
	import { reactive, onMounted, watch } from 'vue';
	import { useRoute } from 'vue-router';
	import { useHelpers } from '@/helpers';
	import AtmoForm from './AtmoForm.vue';

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
			const response = await api.get(`climate/atmo/stations/${route.params.id}`, currentProject.getApiHeader());
			errors.log(response.data);
			data.item = response.data;
		} catch (error) {
			data.page.error = errors.logError(error, 'Unable to get atmo. station from database.');
		}
		
		data.page.loading = false;
	}

	onMounted(async () => await get())
	watch(() => route.name, async () => await get())
	watch(() => route.params.id, async () => await get())
</script>

<template>
	<project-container :loading="data.page.loading" :load-error="data.page.error">
		<file-header input-file="atmo.cli" docs-path="climate/atmo.cli" use-io>
			<router-link to="/edit/climate/stations">Weather Stations</router-link>
			/ <router-link to="/edit/climate/stations/atmo">Atmospheric Deposition</router-link>
			/ Edit
		</file-header>

		<atmo-form is-update :item="data.item"></atmo-form>
	</project-container>
</template>
