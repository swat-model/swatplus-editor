<script setup lang="ts">
	import { reactive, onMounted, watch } from 'vue';
	import { useRoute } from 'vue-router';
	import { useHelpers } from '@/helpers';
	import EditForm from '@/components/EditForm.vue';

	const route = useRoute();
	const { api, currentProject, errors, utilities } = useHelpers();

	let data:any = reactive({
		paths: {
			data: 'recall/data',
			vars: 'recall_dat'
		},
		page: {
			loading: false,
			error: null
		},
		item: {},
		vars: [],
		rec: {
			name: null,
			rec_typ: null,
			rec_typ_name: null
		}
	});

	async function get() {
		if (route.params.id === undefined) return;
		data.page.loading = true;
		data.page.error = null;

		try {
			const response1 = await api.get(`recall/items/${route.params.id}`, currentProject.getApiHeader());
			errors.log(response1.data);
			let item:any = {
				connect: {
					id: response1.data.id,
					name: response1.data.name,
					area: response1.data.area,
					lat: response1.data.lat,
					lon: response1.data.lon,
					elev: response1.data.elev,
					wst_name: response1.data.wst != null ? response1.data.wst.name : ''
				},
				props: {}
			}

			const response12 = await api.get(`recall/properties/${response1.data.rec.id}`, currentProject.getApiHeader());
			item.props = {
				id: response12.data.id,
				name: response12.data.name,
				rec_typ: response12.data.rec_typ
			};

			data.rec.name = item.connect.name;
			data.rec.rec_typ = item.props.rec_typ;
			data.rec.rec_typ_name = utilities.getRecTypDescription(data.rec.rec_typ);

			const response = await api.get(`${data.paths.data}/${route.params.dataId}`, currentProject.getApiHeader());
			data.item = response.data;
			data.item.recall_rec_id = data.item.recall_rec;

			const response2 = await api.get(`definitions/vars/${data.paths.vars}/${utilities.appPathUrl}`);
			data.vars = response2.data;
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
		<file-header input-file="recall.con" docs-path="connections/recall">
			<router-link to="/edit/cons/recall">Point Source</router-link>
			/ <router-link :to="`/edit/cons/recall/edit/${$route.params.id}`">{{data.rec.name}}</router-link>
			/ Edit
		</file-header>

		<edit-form show-range is-update hide-name hide-copy
			:item="data.item" 
			:vars="data.vars" 
			api-url="recall/data"
			:redirect-route="`/edit/recall/edit/${$route.params.id}`" redirect-path></edit-form>
	</project-container>
</template>