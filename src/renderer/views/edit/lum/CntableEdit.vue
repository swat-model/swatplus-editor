<script setup lang="ts">
	import { reactive, onMounted, watch } from 'vue';
	import { useRoute } from 'vue-router';
	import { useHelpers } from '@/helpers';
	import EditForm from '@/components/EditForm.vue';

	const route = useRoute();
	const { api, currentProject, errors, utilities } = useHelpers();

	let data:any = reactive({
		paths: {
			data: 'lum/cntable',
			vars: 'cntable_lum'
		},
		page: {
			loading: false,
			error: null
		},
		item: {},
		vars: []
	});

	async function get() {
		if (route.params.id === undefined) return;
		data.page.loading = true;
		data.page.error = null;

		try {
			const response = await api.get(`${data.paths.data}/${route.params.id}`, currentProject.getApiHeader());
			data.item = response.data;

			const response2 = await api.get(`definitions/vars/${data.paths.vars}/${utilities.appPathUrl}`);
			data.vars = response2.data;
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
		<file-header input-file="cntable.lum" docs-path="/landuse-and-management/cntable.lum" use-io>
			<router-link to="/edit/lum/cntable">Curve Numbers</router-link>
			/ Edit
		</file-header>

		<edit-form show-description show-range is-update get-datasets-record allow-bulk-edit
			:item="data.item"
			name="CNs" table="cntable" no-gis
			:vars="data.vars" 
			api-url="lum/cntable"
			redirect-route="Cntable" />
	</project-container>
</template>
