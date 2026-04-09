<script setup lang="ts">
	import { reactive, watch, onMounted, computed } from 'vue';
	import { useRoute } from 'vue-router';
	import { useHelpers } from '@/helpers';
	import SwatPlusToolboxButton from '../components/SwatPlusToolboxButton.vue';
	import SwatPlusIahrisButton from '../components/SwatPlusIahrisButton.vue';
	
	const route = useRoute();
	const { api, constants, errors, formatters, runProcess, utilities, currentProject } = useHelpers();

	let data = reactive({
		page: {
			loading: false,
			error: <string|null>null,
			tabIndex: 0,
			tabs: [
				"Information",
				"Hydrology",
                "Nutrients",
				"Sediment",
				"Plants",
			]
		},
		config: {
			input_files_dir: '',
			input_files_last_written: '',
			swat_last_run: '',
			output_last_imported: ''
		},
		check: <any>{
			info: {},
			basin: {},
			landuses: {},
			mgt: [],
		},
        simulationWarnings: <string[]>[]
	});

	const currentResultsPath = computed(() => {
		return runProcess.resultsPath(data.config.input_files_dir);
	});

	async function get() {
		data.page.loading = true;
		data.page.error = null;

		try {
			const response = await api.get(`setup/run-settings`, currentProject.getApiHeader());
			errors.log(response.data);
			data.config = response.data.config;

			if (!formatters.isNullOrEmpty(data.config.output_last_imported)) {
				let outputDb = runProcess.outputDbPath(data.config.input_files_dir);
				let formData = {
					'output_db': outputDb
				}
				const response2 = await api.put(`setup/swatplus-check-toolbox`, formData, currentProject.getApiHeader());
				errors.log(response2.data);

				if (response2.data.error) {
					data.page.error = response2.data.error;
				} else {
					data.check = response2.data;

					if (!response.data.has_observed_weather) {
						data.simulationWarnings.push('You are using simulated precipitation data; if you intend to calibrate, you should used measured precipitation data');
					}

					if (response.data.print.prt.nyskip < 1) {
						data.simulationWarnings.push('It is highly recomended that you use at least 1 year of model warmup; 2-5 years is better');
					}

					if (data.check.info.swatVersion === 'development') {
						data.check.info.swatVersion = constants.appSettings.swatplus;
					}
				}
			}
		} catch (error) {
			data.page.error = errors.logError(error, 'Unable to get SWAT+ Check data from database.');
		}
		
		data.page.loading = false;
	}

	function nextTab(position:number) {
		let maxTabPos = data.page.tabs.length - 1;
		data.page.tabIndex += position;

		if (data.page.tabIndex > maxTabPos)
			data.page.tabIndex = 0;
		if (data.page.tabIndex < 0)
			data.page.tabIndex = maxTabPos;
	}

	onMounted(async () => await get());
	watch(() => route.path, async () => await get())
</script>

<template>
    <project-container :loading="data.page.loading" add-error-frame>
        <v-main>
			<div class="py-3 px-6">
                <div v-if="currentProject.isLte">			
					<h1 class="text-h5 mb-6">SWAT+ Check Not Available</h1>

					<v-alert color="info" icon="$info" variant="tonal" border="start" class="my-4">
						SWAT+ Check is not available for SWAT+ lte models.					
					</v-alert>

					<v-btn @click="utilities.exit" variant="flat" color="primary">Exit SWAT+ Editor</v-btn>
				</div>
				<div v-else-if="!formatters.isNullOrEmpty(data.page.error)">
					<h1 class="text-h5 mb-6">There was an error loading SWAT+ Check for your project.</h1>
					<error-alert :text="data.page.error"></error-alert>
					<v-btn to="/run" variant="flat" color="primary">Re-Configure Model Run</v-btn>
				</div>
				<div v-else-if="formatters.isNullOrEmpty(data.config.output_last_imported)">
					<h1 class="text-h5 mb-6">Not ready to run SWAT+ Check</h1>

					<v-alert color="info" icon="$info" variant="tonal" border="start" class="my-4">
						You must run the model and analyze output before running SWAT+ Check.				
					</v-alert>

					<v-btn to="/run" variant="flat" color="primary">Configure Model Run</v-btn>
				</div>
				<div v-else>

                </div>
            </div>
        </v-main>
    </project-container>
</template>