<script setup lang="ts">
	import { reactive, onMounted } from 'vue';
	import { useHelpers } from '@/helpers';
	import EditForm from '@/components/EditForm.vue';

	const { api, errors, utilities } = useHelpers();

	let data: any = reactive({
		paths: {
			data: 'salts/salt_res_ini',
			vars: 'salt_res_ini'
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
		<file-header input-file="constituents.cs" docs-path="constituents" use-io>
			<router-link to="/edit/constituents/salts">Salt Constituents</router-link>
			/ <router-link to="/edit/constituents/salts/res">Reservoir Initial Conditions</router-link>
			/ Edit
		</file-header>

		<edit-form :item="data.item"
				   :vars="data.vars"
				   :api-url="data.paths.data"
				   redirect-route="ConstituentsSaltsResIni"></edit-form>
	</project-container>
</template>
