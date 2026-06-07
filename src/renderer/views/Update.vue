<script setup lang="ts">
import { onMounted, computed } from 'vue';
import { useUpdateManager } from '@/store/updateManager';
import { useAppUpdate } from '@/store/appUpdate';
import { useHelpers } from '@/helpers';
import { Converter } from 'showdown';

const updateManager = useUpdateManager();
const appUpdate = useAppUpdate();
const converter = new Converter();
const {runProcess, constants}  = useHelpers();

onMounted(() => updateManager.init());

const messageHtml = computed(() => converter.makeHtml(appUpdate.message));
</script>

<template>
	<v-main class="layout-fix">
		<div class="py-3 px-6">
			<v-card v-if="appUpdate.isAvailable && !updateManager.data.task.isDownloaded && !updateManager.data.task.isDownloading" class="pa-3">
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
					<v-btn @click="updateManager.download" color="primary" variant="flat">Download Update</v-btn>
					<v-btn to="/" color="secondary" variant="text">Skip this Version / Return to Project</v-btn>	
				</v-card-actions>
			</v-card>
			<v-card v-else-if="appUpdate.isAvailable && !updateManager.data.task.isDownloaded && updateManager.data.task.isDownloading" class="pa-3">
				<v-card-title>Update for SWAT+ Editor Downloading...</v-card-title>
				<v-card-text>
					<v-progress-linear :model-value="updateManager.data.task.progress.percent" color="primary" height="15" striped></v-progress-linear>
					<p>
						{{updateManager.data.task.progress.message}}
					</p>
				</v-card-text>
			</v-card>
			<v-card v-else-if="appUpdate.isAvailable && updateManager.data.task.isDownloaded" class="pa-3">
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

