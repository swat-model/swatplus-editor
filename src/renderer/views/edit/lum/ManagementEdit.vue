<script setup lang="ts">
	import { reactive, onMounted, watch } from 'vue';
	import { useRoute } from 'vue-router';
	import { useHelpers } from '@/helpers';
	import ManagementForm from './ManagementForm.vue';

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
			const response = await api.get(`lum/mgt_sch/${route.params.id}`, currentProject.getApiHeader());
			errors.log(response.data);
			data.item = response.data;
		} catch (error) {
			data.page.error = errors.logError(error, 'Unable to get management schedule from database.');
		}
		
		data.page.loading = false;
	}

	onMounted(async () => await get())
	watch(() => route.name, async () => await get())
	watch(() => route.params.id, async () => await get())
</script>

<template>
	<project-container :loading="data.page.loading" :load-error="data.page.error">
		<file-header input-file="management.sch" docs-path="land-use-management#management-schedules">
			<router-link to="/edit/lum/mgt">Management Schedules</router-link>
			/ Edit
		</file-header>

		<management-form is-update :item="data.item"></management-form>
	</project-container>
</template>
