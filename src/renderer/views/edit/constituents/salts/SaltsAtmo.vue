<script setup lang="ts">
	import { reactive, ref, onMounted, onUnmounted, watch } from 'vue';
	import { useRoute } from 'vue-router';
	import { useHelpers } from '@/helpers';

	const route = useRoute();
	const { api, constants, errors, formatters, currentProject, utilities } = useHelpers();

	const recallGrid = ref();

	let table:any = {
		apiUrl: 'climate/atmo/stations',
		headers: [
			{ key: 'name', label: 'Name' }
		],
		total: 0
	};

	let data:any = reactive({
		page: {
			error: null,
			loading: false,
			saving: false,
			saveSuccess: false,
			showError: false,
			showGrid: false
		},
		form: {
			atmo: false,
			atmo_timestep: 'aa',
			has_atmo: false
		},
		options: [
			{ value: false, title: 'Disable salt atmospheric deposition' },
			{ value: true, title: 'Enable salt atmospheric deposition' }
		],
		delete: {
			show: false,
			error: <string|null>null,
			saving: false
		},
		createTemplates: {
			show: false,
			error: <string|null>null,
			saving: false,
			time_step: 'aa',
			options: {
				time_step: [
				{ title: 'Average Annual', value: 'aa' },
				{ title: 'Yearly', value: 'yr' },
				{ title: 'Monthly', value: 'mo' }
				]
			}
		}
	});

	function getTableTotal(total:any) {
		table.total = total;
	}

	async function get() {
		data.page.loading = true;
		data.page.error = null;
		data.page.showError = false;

		try {
			const response = await api.get(`salts/enable-atmo`, currentProject.getApiHeader());
			data.form = response.data;
			data.showGrid = data.form.atmo;
			data.createTemplates.time_step = data.form.atmo_timestep;
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
			const response = await api.put(`salts/enable-atmo`, data.form, currentProject.getApiHeader());

			data.showGrid = data.form.atmo;
			if (data.showGrid) await recallGrid?.value?.get(false);
		} catch (error) {
			data.page.error = errors.logError(error, 'Unable to save changes to database.');
		}

		data.page.saving = false;
		data.page.showError = data.page.error !== null;
	}
	
	async function confirmDelete() {
		data.delete.errors = [];
		data.delete.saving = true;

		try {
			const response = await api.delete(`salts/enable-atmo`, currentProject.getApiHeader());
			errors.log(response);
			data.delete.show = false;
			await recallGrid?.value?.get(false);
		} catch (error) {
			data.delete.error = errors.logError(error, 'Unable to delete from database.');
		}

		data.delete.saving = false;
	}

	async function createTemplates() {
		data.createTemplates.errors = [];
		data.createTemplates.saving = true;

		try {
			let formData = {
				time_step: data.createTemplates.time_step
			};
			const response = await api.post(`salts/enable-atmo`, formData, currentProject.getApiHeader());
			errors.log(response);
			data.createTemplates.show = false;
			data.form.atmo_timestep = data.createTemplates.time_step;
			await recallGrid?.value?.get(false);
		} catch (error) {
			data.createTemplates.error = errors.logError(error, 'Unable to create templates.');
		}

		data.createTemplates.saving = false;
	}

	onMounted(async () => await get())
	watch(() => route.path, async () => await get())
</script>

<template>
	<project-container :loading="data.page.loading">
		<div v-if="route.name == 'ConstituentsSaltsAtmo'">
			<file-header input-file="constituents.cs" docs-path="constituents" use-io>
				<router-link to="/edit/constituents/salts">Salt Constituents</router-link>
				/ Atmospheric Deposition
			</file-header>

			<p>
				For salt ion atmospheric deposition to be simulated, you must provide atmospheric deposition data in the 
				<router-link to="/edit/climate/stations/atmo" class="text-primary">Climate / Weather Stations / Atmospheric Deposition</router-link> section.
				<span v-if="data.form.has_atmo">We recommend using the Create Templates button below to create default data at the desired time step, then click Import/Export and 
				export your data to CSV. You may then edit the CSV on your own and import it back into the system. Alternatively, you may edit each station value 
				individualy by clicking on the row in the table below.</span>
			</p>
			
			<div v-if="data.form.has_atmo">			
				<v-form @submit.prevent="save">
					<error-alert as-popup v-model="data.page.showError" :show="data.page.showError" :text="data.page.error" :timeout="-1"></error-alert>
					<success-alert v-model="data.page.saveSuccess" :show="data.page.saveSuccess"></success-alert>

					<div class="form-group mb-0">
						<v-select label="Turn salt atmospheric deposition module on/off" v-model="data.form.atmo" :items="data.options"></v-select>
					</div>
					<div class="form-group mb-0" v-if="data.form.atmo">
						<v-select label="Set the timestep" v-model="data.form.atmo_timestep" :items="data.createTemplates.options.time_step" @update:model-value="data.createTemplates.time_step = data.form.atmo_timestep"></v-select>
					</div>
					<div>
						<v-btn type="submit" :loading="data.page.saving" variant="flat" color="primary">Save Changes</v-btn>
					</div>
				</v-form>

				<v-divider class="mt-6 mb-4"></v-divider>

				<grid-view v-if="data.showGrid" ref="recallGrid" :api-url="table.apiUrl" :headers="table.headers" @change="getTableTotal" hide-create hide-delete
					show-import-export default-csv-file="salt_atmo.csv" table-name="salt_atmo_cli">
					<template v-slot:actions>
						<v-btn variant="flat" color="info" @click="data.createTemplates.show = true" class="mr-2">Create Templates</v-btn>
						<v-btn v-if="table.total > 0" variant="flat" color="error" class="mr-2" @click="data.delete.show = true">Delete All</v-btn>
					</template>
				</grid-view>

				<v-dialog v-model="data.delete.show" :max-width="constants.dialogSizes.md">
					<v-card title="Confirm delete">
						<v-card-text>
							<error-alert :text="data.delete.error"></error-alert>

							<p>
								Are you sure you want to delete <strong>ALL</strong> salt atmo. data?
								This action is permanent and cannot be undone. 
							</p>
						</v-card-text>
						<v-divider></v-divider>
						<v-card-actions>
							<v-btn @click="confirmDelete" :loading="data.delete.saving" color="error" variant="text">Delete All</v-btn>
							<v-btn @click="data.delete.show = false">Cancel</v-btn>
						</v-card-actions>
					</v-card>
				</v-dialog>

				<v-dialog v-model="data.createTemplates.show" :max-width="constants.dialogSizes.md">
					<v-card title="Create Data Templates">
						<v-card-text>
							<error-alert :text="data.createTemplates.error"></error-alert>

							<p>
								Create salt atmo templates for the selected time step.
								<span class="text-error">WARNING:</span> This will replace any existing data. To change an individual station instead,
								click a row in the table and change the time step as needed. 
							</p>

							<v-select label="Time step" v-model="data.createTemplates.time_step" :items="data.createTemplates.options.time_step"></v-select>
						</v-card-text>
						<v-divider></v-divider>
						<v-card-actions>
							<v-btn @click="createTemplates" :loading="data.createTemplates.saving" color="primary" variant="text">Create Templates</v-btn>
							<v-btn @click="data.createTemplates.show = false">Cancel</v-btn>
						</v-card-actions>
					</v-card>
				</v-dialog>
			</div>
		</div>
		<router-view></router-view>
	</project-container>
</template>
