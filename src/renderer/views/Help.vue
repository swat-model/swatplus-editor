<script setup lang="ts">
	import { reactive, onMounted } from 'vue';
	import { usePlugins } from '../plugins';

	const { api, constants, errors, utilities } = usePlugins();

	let page:any = reactive({
		loading: false,
		error: null
	});

	let apiCheck:any = reactive({
		editor: '',
		pythonVersion: 'N/A'
	});

	async function getHelp() {
		page.loading = true;
		page.error = null;

		try {
			const response = await api.get('/');
			apiCheck = response.data;
		} catch (error) {
			page.error = errors.logError(error, 'Unable to connect to SWAT+ API.');
			apiCheck.editor = 'API call unsuccessful';
		}
		
		page.loading = false;
	}

	onMounted(async () => await getHelp());
</script>

<template>
	<v-main>
		<div class="py-3 px-6">
			<v-row>
				<v-col cols="12" md="6">
					<v-card class="mb-6">
						<v-card-title>Help Using SWAT+ Editor</v-card-title>
						<v-card-text>
							<p class="text-medium-emphasis">
							SWAT+ Editor is an interface to SWAT+ that allows users to import a project from GIS, modify SWAT+ input, write the text files, and run the model.
							</p>
						</v-card-text>
					</v-card>

					<v-card class="mb-6">
						<v-card-title>Troubleshooting</v-card-title>
						<v-card-text>
							<p class="text-medium-emphasis mb-0">
								Please send the information below to the 
								<open-in-browser url="https://groups.google.com/d/forum/swatplus-editor" text="user group" class="text-primary"></open-in-browser>
								along with your error message.
							</p>
						</v-card-text>
						<v-table density="compact">
							<tbody>
								<tr><th class="min">SWAT+ Editor Version</th><td>{{ constants.appSettings.version }}</td></tr>
								<tr><th class="min">Platform</th><td>{{ constants.globals.platform }}</td></tr>
								<tr><th class="min">Python Mode</th><td>{{ constants.appSettings.python || constants.globals.dev_mode ? 'Yes' : 'Compiled' }}</td></tr>
								<tr><th class="min">Python Version</th><td>{{ apiCheck.pythonVersion }}</td></tr>
								<tr><th class="min">API Check</th><td>{{ apiCheck.editor }}</td></tr>
								<tr><th class="min">API Port</th><td>{{ constants.globals.api_port }}</td></tr>
								<tr><th class="min">Development Mode</th><td>{{ constants.globals.dev_mode ? 'Yes' : 'No' }}</td></tr>
							</tbody>
						</v-table>
					</v-card>

					<v-card class="mb-6">
						<v-card-title>About SWAT+</v-card-title>
						<v-card-text>
							<p class="text-medium-emphasis mb-0">
								The Soil and Water Assessment Tool Plus (SWAT+) is a public domain model jointly developed by the 
								USDA Agricultural Research Service (USDA-ARS) and Texas A&M AgriLife Research, part of The Texas A&M University System. 
								SWAT+ is a small watershed to river basin-scale model to simulate the quality and quantity of surface and ground water and predict 
								the environmental impact of land use, land management practices, and climate change. SWAT is widely used in assessing soil erosion 
								prevention and control, non-point source pollution control and regional management in watersheds.
							</p>
						</v-card-text>
					</v-card>

					<v-card class="mb-6">
						<v-card-title>Disclaimer</v-card-title>
						<v-card-text>
							<p class="text-medium-emphasis mb-0">
								The information contained within this software is offered as a public service. It is the responsibility of the user to verify the accuracy, 
								completeness, timeliness, quality, or suitability for a particular use of the information/ software provided. Neither Grassland, 
								Soil & Water Research Laboratory (GSWRL), Blackland Research Center (BRC), nor Texas A&M AgriLife Research (TALR) make any claims, 
								guarantees, or warranties about the accuracy, completeness, timeliness, quality, or suitability for a particular use of this software. 
								GSWRL, BRC, and TALR disclaim any and all liability for any claims or damages that may result from providing the website or the information/ 
								software contained within. The user of this software assumes all liability and waives any and all claims or causes of action against 
								GSWRL, BRC, and TALR for all uses of and reliance on the information/ software. GSWRL, BRC, and TALR do not endorse any commercial entities, 
								products, consultants, or documentation that may be referenced in this software. The information contained within this software is provided 
								for general information purposes, and is not intended to be a solicitation or an offer to sell in connection with any product or service. 
								Any reference to commercial entities, products, or consultants is for information purposes only.
							</p>
						</v-card-text>
					</v-card>
				</v-col>
				<v-col cols="12" md="6">
					<v-card class="mb-6">
						<v-list>
							<v-list-subheader class="text-uppercase">Docs</v-list-subheader>
							<v-list-item @click="utilities.openUrl('https://swatplus.gitbook.io/docs/')" border="t" class="text-primary">
								<template #prepend><v-icon class="text-medium-emphasis">fas fa-book</v-icon></template>
								SWAT+ Editor Documentation
							</v-list-item>
							<v-list-item @click="utilities.openUrl('https://swatplus.gitbook.io/swat+-documentation/')" border="t" class="text-primary">
								<template #prepend><v-icon class="text-medium-emphasis">fas fa-book</v-icon></template>
								SWAT+ Input/Output Documentation
							</v-list-item>
						</v-list>
					</v-card>

					<v-card class="mb-6">
						<v-list>
							<v-list-subheader class="text-uppercase">User Groups</v-list-subheader>
							<v-list-item @click="utilities.openUrl('https://groups.google.com/d/forum/swatplus-editor')" border="t" class="text-primary">
								<template #prepend><v-icon class="text-medium-emphasis">fas fa-users</v-icon></template>
								SWAT+ Editor user group (this interface)
							</v-list-item>
							<v-list-item @click="utilities.openUrl('https://groups.google.com/d/forum/swatplus')" border="t" class="text-primary">
								<template #prepend><v-icon class="text-medium-emphasis">fas fa-users</v-icon></template>
								SWAT+ Model user group (the model itself)
							</v-list-item>
							<v-list-item @click="utilities.openUrl('https://groups.google.com/d/forum/qswatplus')" border="t" class="text-primary">
								<template #prepend><v-icon class="text-medium-emphasis">fas fa-users</v-icon></template>
								QSWAT+ user group (GIS interface)
							</v-list-item>
						</v-list>
					</v-card>

					<v-card class="mb-6">
						<v-list>
							<v-list-subheader class="text-uppercase">Additional Resources</v-list-subheader>
							<v-list-item @click="utilities.openUrl('https://swat.tamu.edu/software/plus')" border="t" class="text-primary">
								<template #prepend><v-icon class="text-medium-emphasis">fas fa-globe</v-icon></template>
								SWAT+ Website
							</v-list-item>
							<v-list-item @click="utilities.openUrl('https://github.com/swat-model/swatplus-editor')" border="t" class="text-primary">
								<template #prepend><v-icon class="text-medium-emphasis">fab fa-github</v-icon></template>
								SWAT+ Editor source code repository
							</v-list-item>
							<v-list-item @click="utilities.openUrl('https://plus.swat.tamu.edu')" border="t" class="text-primary">
								<template #prepend><v-icon class="text-medium-emphasis">fas fa-box-archive</v-icon></template>
								SWAT+ Version Archive
							</v-list-item>
						</v-list>
					</v-card>
					
				</v-col>
			</v-row>
		</div>
	</v-main>
</template>