<script setup lang="ts">
	import { reactive, onMounted } from 'vue';
	import { useRoute } from 'vue-router';
	import { usePlugins } from '../../../../plugins';
	import EditForm from '../../../../components/EditForm.vue';

	const route = useRoute();
	const { api, currentProject, errors, utilities } = usePlugins();

	let data:any = reactive({
		paths: {
			vars: 'sediment_res'
		},
		page: {
			loading: true,
			error: null
		},
		item: {
			name: null,
			description: null
		},
		vars: [],
		rec: {
			name: null,
			rec_typ: null,
			rec_typ_name: null
		}
	});

	async function get() {
		data.page.loading = true;
		data.page.error = null;

		try {
			const response1 = await api.get(`recall/${route.params.id}`, currentProject.getApiHeader());
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

			const response12 = await api.get(`recall/data/${response1.data.rec.id}`, currentProject.getApiHeader());
			item.props = {
				id: response12.data.id,
				name: response12.data.name,
				rec_typ: response12.data.rec_typ
			};

			data.rec.name = item.connect.name;
			data.rec.rec_typ = item.props.rec_typ;
			data.rec.rec_typ_name = utilities.getRecTypDescription(data.rec.rec_typ);

			const response = await api.get(`definitions/vars/${data.paths.vars}/${utilities.appPathUrl}`);
			data.vars = response.data;
			data.item = utilities.setVars(data.item, data.vars);
			data.item.recall_rec_id = route.params.id;
		} catch (error) {
			data.page.error = errors.logError(error, 'Unable to get table metadata from database.');
		}
			
		data.page.loading = false;
	}

	onMounted(async () => await get())
</script>

<template>
	<project-container :loading="data.page.loading" :load-error="data.page.error">
		<file-header input-file="recall.con" docs-path="connections/recall">
			<router-link to="/edit/cons/recall">Point Source</router-link>
			/ <router-link :to="`/edit/cons/recall/edit/${$route.params.id}`">{{data.rec.name}}</router-link>
			/ Create
		</file-header>

		<edit-form show-range hide-name
			:item="data.item" 
			:vars="data.vars" 
			api-url="recall/data"
			:redirect-route="`/edit/recall/edit/${$route.params.id}`" redirect-path></edit-form>
	</project-container>
</template>
