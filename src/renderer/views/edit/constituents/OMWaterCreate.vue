<script setup lang="ts">
	import { reactive, onMounted } from 'vue';
	import { useHelpers } from '@/helpers';
	import EditForm from '@/components/EditForm.vue';

	const { api, errors, utilities } = useHelpers();

	let data:any = reactive({
		paths: {
			vars: 'om_water_ini'
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
			data.item = utilities.setVars(data.item, data.vars);
		} catch (error) {
			data.page.error = errors.logError(error, 'Unable to get table metadata from database.');
		}
			
		data.page.loading = false;
	}

	onMounted(async () => await get())
</script>

<template>
	<project-container :loading="data.page.loading" :load-error="data.page.error">
		<file-header input-file="om_water.ini" docs-path="constituents/om_water.ini" use-io>
			<router-link to="/edit/constituents/om_water">Organic Mineral Water</router-link>
			/ Create
		</file-header>

		<edit-form show-range
			:item="data.item" 
			:vars="data.vars" 
			api-url="init/om_water"
			redirect-route="ConstituentsOMWater" />
	</project-container>
</template>
