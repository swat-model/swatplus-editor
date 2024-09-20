<script setup lang="ts">
	import { reactive, onMounted, onUnmounted, computed } from 'vue';
	import { useRoute } from 'vue-router';
	import { useHelpers } from '@/helpers';
	import { Converter } from 'showdown';

	const route = useRoute();
	const { api, constants, errors, formatters, currentProject, runProcess, utilities, appUpdate } = useHelpers();
	const converter = new Converter();
	
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
			isDownloading: false,
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
		appUpdateDownloading: undefined,
		appUpdateDownloaded: undefined,
		appUpdateStatus: undefined,
	}

	function initRunProcessHandlers() {
		listeners.appUpdateDownloading = runProcess.appUpdateDownloading((stdData:any) => {
			data.task.progress = runProcess.getApiOutput(stdData);
		});

		listeners.appUpdateDownloaded = runProcess.appUpdateDownloaded((stdData:any) => {
			data.task.isDownloaded = true;
			data.task.isDownloading = false;
		});

		listeners.appUpdateStatus = runProcess.appUpdateStatus((stdData:any) => {
			console.log(`Update status received: ${stdData}`);
			let status:any = runProcess.getApiOutput(stdData);
			appUpdate.setStatus(status.message, status.isAvailable);
		});
	}

	function downloadUpdate() {
		data.task.isDownloading = true;
		runProcess.downloadUpdate();
	}

	function removeRunProcessHandlers() {
		if (listeners.appUpdateDownloading) listeners.appUpdateDownloading();
		if (listeners.appUpdateDownloaded) listeners.appUpdateDownloaded();
		if (listeners.appUpdateStatus) listeners.appUpdateStatus();
	}

	const messageHtml = computed(() => {
		return converter.makeHtml(appUpdate.message);
	});
</script>

<template>
	<v-main>
		<div class="py-3 px-6">
			<v-card v-if="appUpdate.isAvailable && !data.task.isDownloaded && !data.task.isDownloading" class="pa-3">
				<v-card-title>New Update Available</v-card-title>
				<v-divider></v-divider>
				<v-card-text>
					<div v-html="messageHtml"></div>

					<p>
						See <open-in-browser url="https://swatplus.gitbook.io/docs/release-notes" text="software release notes" class="text-primary"></open-in-browser>
						for a full history of changes
					</p>
				</v-card-text>
				<v-card-actions class="pb-3">
					<v-btn @click="downloadUpdate" color="primary" variant="flat">Download Update</v-btn>
					<v-btn to="/" color="secondary" variant="text">Skip this Version / Return to Project</v-btn>	
				</v-card-actions>
			</v-card>
			<v-card v-else-if="appUpdate.isAvailable && !data.task.isDownloaded && data.task.isDownloading" class="pa-3">
				<v-card-title>Update for SWAT+ Editor Downloading...</v-card-title>
				<v-card-text>
					<v-progress-linear :model-value="data.task.progress.percent" color="primary" height="15" striped></v-progress-linear>
					<p>
						{{data.task.progress.message}}
					</p>
				</v-card-text>
			</v-card>
			<v-card v-else-if="appUpdate.isAvailable && data.task.isDownloaded" class="pa-3">
				<v-card-title>Update for SWAT+ Editor Ready to Install</v-card-title>
				<v-card-text>
					<p>
						Click below to quit SWAT+ Editor and install the update.
						You may also return to your project and the update will install automatically when you close the editor.
					</p>
					<p>
						If you have another other instances of the editor open, be sure to manually close them first or you may encounter
						an installation error.
					</p>
				</v-card-text>
				<v-card-actions class="pb-3">
					<v-btn @click="runProcess.quitAndInstallUpdate" color="primary" variant="flat">Quit and Install Update</v-btn>	
					<v-btn to="/" color="secondary" variant="text">Return to Project (Will Install on Close)</v-btn>
				</v-card-actions>
			</v-card>
			<v-card v-else class="pa-3">
				<v-card-title>
					{{ appUpdate.message || 'No automatic update available at this time' }}
				</v-card-title>
				<v-card-text>
					<p>
						<strong v-if="constants.globals.platform !== 'win32'">
							Automatic updates are only available on Windows.
						</strong>
						See the <open-in-browser url="https://github.com/swat-model/swatplus-editor/releases" text="SWAT+ Editor Github release page" class="text-primary"></open-in-browser>
						for all releases.
					</p>
				</v-card-text>
				<v-card-actions class="pb-3">
					<v-btn @click="runProcess.manualUpdateCheck" color="primary" variant="flat"><v-icon class="mr-1">fa-arrows-rotate</v-icon> Check Again</v-btn>	
					<v-btn to="/" color="secondary" variant="text">Return to Project</v-btn>
				</v-card-actions>
			</v-card>
		</div>
	</v-main>
</template>