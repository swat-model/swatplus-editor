<script setup lang="ts">
	import { reactive, onMounted } from 'vue';
	import { useHelpers } from '@/helpers';
	import EditForm from '@/components/EditForm.vue';

	const { api, errors, utilities } = useHelpers();

	let data:any = reactive({
		paths: {
			vars: 'nutrients_cha'
		},
		page: {
			loading: true,
			error: null
		},
		item: {
			name: null,
			description: null
		},
		vars: []
	});

	async function get() {
		data.page.loading = true;
		data.page.error = null;

		try {
			const response = await api.get(`definitions/vars/${data.paths.vars}/${utilities.appPathUrl}`);
			data.vars = response.data;
			
			let keys = Object.keys(data.vars);
			for (let k of keys) {
				let v = data.vars[k];
				data.item[k] = v.type == 'string' ? v.default_text : v.default_value;
			}
		} catch (error) {
			data.page.error = errors.logError(error, 'Unable to get table metadata from database.');
		}
			
		data.page.loading = false;
	}

	onMounted(async () => await get())
</script>

<template>
	<project-container :loading="data.page.loading" :load-error="data.page.error">
		<file-header input-file="nutrients.cha" docs-path="channels/nutrients.cha" use-io>
			<router-link to="/edit/cons/channels">Channels</router-link> / 
			<router-link to="/edit/cons/channels/nutrients">Nutrients</router-link>
			/ Create
		</file-header>

		<edit-form show-description show-range
			:item="data.item" 
			:vars="data.vars" 
			api-url="channels/nutrients"
			redirect-route="ChannelsNutrients" />
	</project-container>
</template>
