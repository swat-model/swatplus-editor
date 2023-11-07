<script setup lang="ts">
	import { reactive, onMounted, watch } from 'vue';
	import { useRoute } from 'vue-router';
	import { useHelpers } from '@/helpers';
	import RecallForm from './RecallForm.vue';

	const route = useRoute();
	const { api, currentProject, errors, utilities } = useHelpers();

	let data:any = reactive({
		apiUrl: 'recall',
		page: {
			loading: false,
			error: null
		},
		item: {
			connect: {},
			props: {},
			outflow: []
		}
	});

	async function get() {
		if (route.params.id === undefined) return;
		data.page.loading = true;
		data.page.error = null;

		try {
			const response = await api.get(`${data.apiUrl}/items/${route.params.id}`, currentProject.getApiHeader());
			errors.log(response.data);

			data.item.connect = {
				id: response.data.id,
				name: response.data.name,
				area: response.data.area,
				lat: response.data.lat,
				lon: response.data.lon,
				elev: response.data.elev,
				wst_name: response.data.wst != null ? response.data.wst.name : ''
			};

			data.item.outflow = response.data.con_outs;

			const response2 = await api.get(`${data.apiUrl}/properties/${response.data.rec.id}`, currentProject.getApiHeader());

			data.item.props = {
				id: response2.data.id,
				name: response2.data.name,
				rec_typ: response2.data.rec_typ
			};
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
		<div v-if="$route.name == 'RecallEdit'">
			<file-header input-file="recall.con" docs-path="connections/recall">
				<router-link to="/edit/cons/recall">Point Source</router-link>
				/ Edit
			</file-header>

			<recall-form :item="data.item" :api-url="data.apiUrl" is-update allow-bulk-edit></recall-form>
		</div>
		<router-view></router-view>
	</project-container>
</template>