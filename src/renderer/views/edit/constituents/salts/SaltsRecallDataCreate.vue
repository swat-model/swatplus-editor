<script setup lang="ts">
	import { reactive, onMounted } from 'vue';
	import { useRoute } from 'vue-router';
	import { useHelpers } from '@/helpers';
	import EditForm from '@/components/EditForm.vue';

	const route = useRoute();
	const { api, currentProject, errors, utilities } = useHelpers();

	let data:any = reactive({
		paths: {
			vars: 'salts_recall_dat'
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
			const response1 = await api.get(`salts/recall/${route.params.id}`, currentProject.getApiHeader());
			errors.log(response1.data);
			let item = response1.data;

			data.rec.name = item.name;
			data.rec.rec_typ = item.rec_typ;
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
		<file-header input-file="constituents.cs" docs-path="constituents" use-io>
			<router-link to="/edit/constituents/salts">Salt Constituents</router-link>
			/ <router-link to="/edit/constituents/salts/recall">Point Source</router-link>
			/ <router-link :to="`/edit/constituents/salts/recall/edit/${$route.params.id}`">{{data.rec.name}}</router-link>
			/ Create
		</file-header>

		<edit-form show-range hide-name
			:item="data.item" 
			:vars="data.vars" 
			api-url="salts/recall-data"
			:redirect-route="`/edit/constituents/salts/recall/edit/${$route.params.id}`" redirect-path></edit-form>
	</project-container>
</template>
