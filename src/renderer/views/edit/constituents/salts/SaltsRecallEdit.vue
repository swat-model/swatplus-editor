<script setup lang="ts">
	import { reactive, onMounted, watch } from 'vue';
	import { useRoute } from 'vue-router';
	import { useHelpers } from '@/helpers';
	import SaltsRecallForm from './SaltsRecallForm.vue';

	const route = useRoute();
	const { api, currentProject, errors, utilities } = useHelpers();

	let data:any = reactive({
		apiUrl: 'salts/recall',
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
			const response = await api.get(`${data.apiUrl}/${route.params.id}`, currentProject.getApiHeader());
			errors.log(response.data);
			data.item = response.data;
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
		<div v-if="$route.name == 'ConstituentsSaltsRecallEdit'">
			<file-header input-file="constituents.cs" docs-path="constituents" use-io>
				<router-link to="/edit/constituents/salts">Salt Constituents</router-link>
				/ <router-link to="/edit/constituents/salts/recall">Point Source</router-link>
				/ Edit
			</file-header>

			<salts-recall-form v-if="!data.page.loading" :item="data.item" :api-url="data.apiUrl" is-update></salts-recall-form>
		</div>
		<router-view></router-view>
	</project-container>
</template>