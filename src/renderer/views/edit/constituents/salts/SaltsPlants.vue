<script setup lang="ts">
	import { reactive, ref, onMounted, onUnmounted, watch } from 'vue';
	import { useRoute } from 'vue-router';
	import { useHelpers } from '@/helpers';

	const route = useRoute();
	const { api, constants, errors, formatters, currentProject, utilities } = useHelpers();

	const recallGrid = ref();

	let table:any = {
		apiUrl: 'db/plants',
		headers: [
			{ key: 'name', label: 'Name' },
			{ key: 'description', label: 'Description' }
		]
	};

	let data:any = reactive({
		page: {
			error: null,
			loading: false,
			saving: false,
			saveSuccess: false,
			showError: false,
			showGrid: true
		},
		form: {
			plants_uptake: false,
			enabled: 0,
			soil: 1,
			stress: 2,
			conversion_factor: 500
		},
		options: {
			plants_uptake: [
				{ value: false, title: 'Disable daily root uptake module' },
				{ value: true, title: 'Enable daily root uptake module' }
			],
			enabled: [
				{ value: 0, title: 'Disable plant salinity tolerance module' },
				{ value: 1, title: 'Enable plant salinity tolerance module' }
			],
			soil: [
				{ value: 1, title: 'CaSO4 soils' },
				{ value: 2, title: 'NaCl soils' }
			],
			stress: [
				{ value: 1, title: 'Salt stress applied after other stresses applied' },
				{ value: 2, title: 'Included with other stresses' }
			]
		}
	});

	async function get() {
		data.page.loading = true;
		data.page.error = null;
		data.page.showError = false;

		try {
			const response = await api.get(`salts/enable-plants`, currentProject.getApiHeader());
			data.form = response.data;
			//data.showGrid = data.form.urban;
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

		if (formatters.isNullOrEmpty(data.form.conversion_factor)) {
			data.form.conversion_factor = 500;
		}

		try {
			const response = await api.put(`salts/enable-plants`, data.form, currentProject.getApiHeader());

			//data.showGrid = true;
			if (data.showGrid) await recallGrid?.value?.get(false);
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
		<div v-if="$route.name == 'ConstituentsSaltsPlants'">
			<file-header input-file="constituents.cs" docs-path="constituents" use-io>
				<router-link to="/edit/constituents/salts">Salt Constituents</router-link>
				/ Plant Influence
			</file-header>
			
			<v-form @submit.prevent="save">
				<error-alert as-popup v-model="data.page.showError" :show="data.page.showError" :text="data.page.error" :timeout="-1"></error-alert>
				<success-alert v-model="data.page.saveSuccess" :show="data.page.saveSuccess"></success-alert>

				<div class="form-group mb-0">
					<v-select label="Turn daily root uptake module on/off" v-model="data.form.plants_uptake" :items="data.options.plants_uptake"></v-select>
				</div>
				<div class="form-group mb-0">
					<v-select label="Turn plant salinity tolerance module on/off" v-model="data.form.enabled" :items="data.options.enabled"></v-select>
				</div>
				<div class="form-group mb-0">
					<v-select label="Plant salinity tolerance soils option" v-model="data.form.soil" :items="data.options.soil"></v-select>
				</div>
				<div class="form-group mb-0">
					<v-select label="Plant salinity tolerance stress option" v-model="data.form.stress" :items="data.options.stress"></v-select>
				</div>
				<div class="form-group mb-0">
					<v-text-field v-model="data.form.conversion_factor" label="Conversion factor from TDS --> EC (EC=TDS/factor)" type="number" step="any" required></v-text-field>
				</div>
				<div>
					<v-btn type="submit" :loading="data.page.saving" variant="flat" color="primary">Save Changes</v-btn>
				</div>
			</v-form>

			<v-divider class="mt-6 mb-4"></v-divider>

			<grid-view ref="recallGrid" :api-url="table.apiUrl" :headers="table.headers" hide-create hide-delete
				show-import-export default-csv-file="salt_plants.csv" table-name="salt_plants">
			</grid-view>
		</div>
		<router-view></router-view>
	</project-container>
</template>
