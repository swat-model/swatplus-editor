<script setup lang="ts">
	import { reactive, ref, onMounted, watch } from 'vue';
	import { useRoute } from 'vue-router';
	import { useHelpers } from '@/helpers';

	const route = useRoute();
	const { api, constants, currentProject, errors, formatters, utilities } = useHelpers();

	let data:any = reactive({
		page: {
			error: null,
			loading: false,
			saving: false,
			saveSuccess: false,
			showError: false
		},
		add: {
			path: null
		},
		constituents: {
			using: false,
			pests: [],
			paths: [],
			hmets: [],
			salts: []
		},
		enable_salts: 0,
		options: [
			{ value: 0, title: 'Disable salt constituents' },
			{ value: 1, title: 'Enable salt constituents' }
		]
	});

	async function get() {
		data.page.loading = true;
		data.page.error = null;
		data.page.showError = false;

		try {
			const response = await api.get(`init/constituents`, currentProject.getApiHeader());
			data.constituents = response.data;
			errors.log(data.constituents);
			data.enable_salts = data.constituents.salts && data.constituents.salts.length > 0 ? 1 : 0;
		} catch (error) {
			data.page.error = errors.logError(error, 'Unable to get project information from database.');
		}
			
		data.page.showError = data.page.error !== null;
		data.page.loading = false;
	}

	async function save() {
		data.page.error = null;
		data.page.saving = true;
		data.page.showError = false;

		try {
			let constituentsData = {
				enable_salts: data.enable_salts
			};
			const response = await api.put(`init/constituents`, constituentsData, currentProject.getApiHeader());
		} catch (error) {
			data.page.error = errors.logError(error, 'Unable to save changes to database.');
		}

		data.page.saving = false;
		data.page.showError = data.page.error !== null;
	}	

	onMounted(async () => await get())
	watch(() => route.path, async () => await get())
</script>

<template>
	<project-container :loading="data.page.loading">
		<div v-if="$route.name == 'ConstituentsSalts'">
			<file-header input-file="constituents.cs" docs-path="constituents" use-io>
				Salt Constituents
			</file-header>
			
			<v-form @submit.prevent="save">
				<error-alert as-popup v-model="data.page.showError" :show="data.page.showError" :text="data.page.error" :timeout="-1"></error-alert>
				<success-alert v-model="data.page.saveSuccess" :show="data.page.saveSuccess"></success-alert>

				<div class="form-group">
					<v-select label="Turn salt constituents module on/off" v-model="data.enable_salts" :items="data.options"></v-select>
				</div>

				<p>
					Turn the SWAT+ salinty module on or off using the dropdown above and click the "Save Changes" button. The salt ions used in the model
					are set: so4, ca, mg, na, k, cl, co3, and hco3. Use the navigation menu on the left to provide sources of salts in your model, initial conditions, and 
					the influence of salt on plants.
				</p>

				<action-bar>
					<v-btn type="submit" :loading="data.page.saving" variant="flat" color="primary" class="mr-2">
						Save Changes
					</v-btn>
					<back-button></back-button>
				</action-bar>
			</v-form>
		</div>
		<div v-else-if="data.enable_salts === 0">
			<v-alert type="info" icon="$info" variant="tonal" border="start" class="mb-4">
				Salt constituents are not enabled. <router-link class="text-primary" to="/edit/constituents/salt">Enable them here</router-link> to use this feature.
			</v-alert>
		</div>
		<router-view></router-view>
	</project-container>
</template>
