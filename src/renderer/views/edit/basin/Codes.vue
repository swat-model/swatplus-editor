<script setup lang="ts">
	import { reactive, onMounted, watch } from 'vue';
	import { useRoute } from 'vue-router';
	import { useHelpers } from '@/helpers';
	import EditForm from '@/components/EditForm.vue';

	const route = useRoute();
	const { api, currentProject, errors, utilities } = useHelpers();

	let data:any = reactive({
		page: {
			loading: false,
			error: null
		},
		item: {},
		vars: []
	});

	async function get() {
		data.page.loading = true;
		data.page.error = null;

		try {
			const response = await api.get(`basin/codes`, currentProject.getApiHeader());
			errors.log(response.data);
			data.item = response.data;

			const response2 = await api.get(`definitions/vars/codes_bsn/${utilities.appPathUrl}`);
			errors.log(response2.data);
			data.vars = response2.data;
		} catch (error) {
			data.page.error = errors.logError(error, 'Unable to get project information from database.');
		}
			
		data.page.loading = false;
	}

	onMounted(async () => await get())
	watch(() => route.name, async () => await get())
</script>

<template>
	<project-container :loading="data.page.loading" :load-error="data.page.error">
		<file-header input-file="codes.bsn" docs-path="basin-1/codes.bsn" use-io>
			Basin Codes
		</file-header>

		<edit-form is-update hide-name no-id hide-copy
			:item="data.item" 
			:vars="data.vars" :nullable-fields="['pet_file']"
			api-url="basin/codes"
			redirect-route="BasinCodes"></edit-form>
	</project-container>
</template>