<script setup lang="ts">
	import { reactive, onMounted } from 'vue';
	import { useRoute } from 'vue-router';
	import { usePlugins } from '../plugins';
	const { api, constants, currentProject, errors, formatters, utilities } = usePlugins();	
	const route = useRoute();

	let page:any = reactive({
		loading: false,
		error: null
	})

	async function get() {
		page.loading = true;
		page.error = null;

		try {
			const response = await api.get(`setup/config`, currentProject.getTempApiHeader(route.query.projectDb));
			errors.log(response.data);

			let data = response.data;
			let project = {
				projectDb: route.query.projectDb,
				datasetsDb: data.reference_db,
				name: data.project_name,
				description: data.project_description,
				version: data.editor_version,
				isLte: data.is_lte
			};

			currentProject.setCurrentProject(project);
		} catch (error) {
			page.error = errors.logError(error, 'Unable to load data.');
		}
		
		page.loading = false;
	}

	onMounted(async () => await get())
</script>

<template>
	<v-main>
		<div class="py-3 px-6">
			<page-loading :loading="page.loading"></page-loading>
			<div v-if="!page.loading">
				<h1 class="text-h5 mb-2">
					{{route.query.section}}
				</h1>

				<grid-view 
					:api-url="route.query.apiUrl" 
					hide-edit hide-create hide-delete :items-per-page="100" use-dynamic-headers full-width-action-bar />
			</div>
		</div>
	</v-main>
</template>
