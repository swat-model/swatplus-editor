<script setup lang="ts">
	import { reactive, onMounted, watch } from 'vue';
	import { useRoute } from 'vue-router';
	import { useHelpers } from '@/helpers';
	import EditForm from '@/components/EditForm.vue';

	const route = useRoute();
	const { api, currentProject, errors, utilities } = useHelpers();

	let data:any = reactive({
		paths: {
			data: 'gwflow/cells',
			vars: 'gwflow_cell'
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

			const response2 = await api.get(`definitions/vars/${data.paths.vars}`, utilities.getAppPathHeader());
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
		<file-header input-file="cells.gw" docs-path="modflow" use-io>
			<router-link to="/edit/cons/gwflow">Groundwater Flow</router-link>
			/ <router-link to="/edit/cons/gwflow/cells">Cells</router-link>
			/ Edit
		</file-header>

		<edit-form is-update hide-name primary-key="cell_id"
			:item="data.item"
			name="Cell" :table="data.paths.vars" no-gis
			:vars="data.vars" 
			:api-url="data.paths.data"
			redirect-route="GwflowCells"
            :nullable-fields="['row','col','initial_head','streambed_k','streambed_thickness','bc_type','tile_depth','tile_area','tile_k','init_temp','gis_id']" />
	</project-container>
</template>
