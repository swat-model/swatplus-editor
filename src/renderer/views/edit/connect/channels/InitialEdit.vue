<script setup lang="ts">
	import { reactive, onMounted, watch } from 'vue';
	import { useRoute } from 'vue-router';
	import { useHelpers } from '@/helpers';
	import InitialForm from './InitialForm.vue';

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
			const response = await api.get(`channels/initial/${route.params.id}`, currentProject.getApiHeader());
			errors.log(response.data);

			data.item = {
				id: response.data.id,
				name: response.data.name,
				org_min_name: response.data.org_min != null ? response.data.org_min.name : '',
				pest_name: response.data.pest != null ? response.data.pest.name : '',
				path_name: response.data.path != null ? response.data.path.name : '',
				hmet_name: response.data.hmet != null ? response.data.hmet.name : '',
				salt_name: response.data.salt_cs != null ? response.data.salt_cs.name : '',
				description: response.data.description
			};
		} catch (error) {
			data.page.error = errors.logError(error, 'Unable to get channel properties from database.');
		}
		
		data.page.loading = false;
	}

	onMounted(async () => await get())
	watch(() => route.name, async () => await get())
	watch(() => route.params.id, async () => await get())
</script>

<template>
	<project-container :loading="data.page.loading" :load-error="data.page.error">
		<file-header input-file="initial.cha" docs-path="channels/initial.cha" use-io>
			<router-link to="/edit/cons/channels">Channels</router-link> / 
			<router-link to="/edit/cons/channels/initial">Initial</router-link>
			/ Edit
		</file-header>

		<initial-form is-update :item="data.item"></initial-form>
	</project-container>
</template>