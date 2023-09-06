<script setup lang="ts">
	import { reactive, onMounted, watch } from 'vue';
	import { useRoute } from 'vue-router';
	import { usePlugins } from '../../../plugins';
	import EditForm from '../../../components/EditForm.vue';

	const route = useRoute();
	const { api, currentProject, errors, utilities } = usePlugins();

	let data:any = reactive({
		page: {
			loading: false,
			error: null
		},
		item: {},
		vars: []
	});

	async function get() {
		data.page.loading = true;
		data.page.error = null;

		try {
			const response = await api.get(`basin/parms`, currentProject.getApiHeader());
			data.item = response.data;

			const response2 = await api.get(`definitions/vars/parameters_bsn/${utilities.appPathUrl}`);
			data.vars = response2.data;
		} catch (error) {
			data.page.error = errors.logError(error, 'Unable to get project information from database.');
		}
			
		data.page.loading = false;
	}

	onMounted(async () => await get())
	watch(() => route.name, async () => await get())
</script>

<template>
	<project-container :loading="data.page.loading" :load-error="data.page.error">
		<file-header input-file="parameters.bsn" docs-path="basin">
			Basin Parameters
		</file-header>

		<edit-form show-range is-update hide-name no-id hide-copy
			:item="data.item" 
			:vars="data.vars" 
			api-url="basin/parms"
			redirect-route="BasinParameters"></edit-form>
	</project-container>
</template>