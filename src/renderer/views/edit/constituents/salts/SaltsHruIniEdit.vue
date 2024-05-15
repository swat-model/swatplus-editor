<script setup lang="ts">
	import { reactive, onMounted, watch } from 'vue';
	import { useRoute } from 'vue-router';
	import { useHelpers } from '@/helpers';
	import EditForm from '@/components/EditForm.vue';

	const route = useRoute();
	const { api, currentProject, errors, utilities } = useHelpers();

	let data: any = reactive({
		paths: {
			data: 'salts/salt_hru_ini_cs',
			vars: 'salt_hru_ini_cs'
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
		<file-header input-file="constituents.cs" docs-path="constituents" use-io>
			<router-link to="/edit/constituents/salts">Salt Constituents</router-link>
			/ <router-link to="/edit/constituents/salts/hru">HRU Initial Conditions</router-link>
			/ Edit
		</file-header>

		<edit-form is-update allow-bulk-edit
				   :item="data.item"
				   name="HRU Initial Conditions" :table="data.paths.vars" no-gis
				   :vars="data.vars"
				   :api-url="data.paths.data"
				   redirect-route="ConstituentsSaltsHruIni">
			<template #actions>
				<v-btn to="/edit/constituents/soil_plant" type="button" variant="flat" color="info" class="mr-2">Assign to Soil Plant</v-btn>
			</template>
		</edit-form>
	</project-container>
</template>
