<script setup lang="ts">
	import { reactive, onMounted, onUnmounted } from 'vue';
	import { useRoute } from 'vue-router';
	import { useHelpers } from '@/helpers';

	const route = useRoute();
	const { api, constants, errors, formatters, currentProject, runProcess, utilities } = useHelpers();
	
	let data:any = reactive({
		page: {
			loading: false,
			error: null
		},
		task: {
			progress: {
				percent: 0,
				message: null
			},
			status: {
				isAvailable: false,
				message: null
			},
			isDownloaded: false,
		}
	});

	onMounted(async () => {
		data.page.loading = true;
		initRunProcessHandlers();
		data.page.loading = false;
	});
	
	onUnmounted(() => removeRunProcessHandlers());

	let listeners:any = {
		appUpdateStatus: undefined,
		appUpdateDownloading: undefined,
		appUpdateDownloaded: undefined
	}

	function initRunProcessHandlers() {
		listeners.appUpdateStatus = runProcess.appUpdateStatus((stdData:any) => {
			data.task.status = runProcess.getApiOutput(stdData);
		});

		listeners.appUpdateDownloading = runProcess.appUpdateDownloading((stdData:any) => {
			data.task.progress = runProcess.getApiOutput(stdData);
		});

		listeners.appUpdateDownloaded = runProcess.appUpdateDownloaded((stdData:any) => {
			data.task.isDownloaded = true;
		});
	}

	function removeRunProcessHandlers() {
		if (listeners.appUpdateStatus) listeners.appUpdateStatus();
		if (listeners.appUpdateDownloading) listeners.appUpdateDownloading();
		if (listeners.appUpdateDownloaded) listeners.appUpdateDownloaded();
	}
</script>

<template>
	<v-main>
		<div class="py-3 px-6">
			<v-card class="mb-6">
				<v-card-title>Help Using SWAT+ Editor</v-card-title>
				<v-card-text>
					<p class="text-medium-emphasis">
					SWAT+ Editor is an interface to SWAT+ that allows users to import a project from GIS, modify SWAT+ input, write the text files, and run the model.
					</p>
				</v-card-text>
			</v-card>
		</div>
	</v-main>
</template>