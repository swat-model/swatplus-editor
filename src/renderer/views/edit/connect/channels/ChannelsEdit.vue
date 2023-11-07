<script setup lang="ts">
	import { reactive, onMounted, watch } from 'vue';
	import { useRoute } from 'vue-router';
	import { useHelpers } from '@/helpers';
	import ChannelsForm from './ChannelsForm.vue';

	const route = useRoute();
	const { api, currentProject, errors } = useHelpers();

	let data:any = reactive({
		apiUrl: 'channels',
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

			const response2 = await api.get(`${data.apiUrl}/properties/${response.data.lcha.id}`, currentProject.getApiHeader());

			data.item.props = {
				id: response2.data.id,
				name: response2.data.name,
				init_name: response2.data.init != null ? response2.data.init.name : '',
				hyd_name: response2.data.hyd != null ? response2.data.hyd.name : '',
				nut_name: response2.data.nut != null ? response2.data.nut.name : '',
				description: response2.data.description
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
		<file-header input-file="chandeg.con" docs-path="connections/channels">
			<router-link to="/edit/cons/channels">Channels</router-link>
			/ Edit
		</file-header>

		<channels-form :item="data.item" :api-url="data.apiUrl" is-update allow-bulk-edit></channels-form>
	</project-container>
</template>