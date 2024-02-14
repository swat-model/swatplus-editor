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
			itemsLoading: false,
			saving: false,
			saveSuccess: false,
			showError: false,
			tab: 'balance',
			
		},
		enabled: false,
		plants: [],
		options: {
			tableFields: [
				{ key: 'edit', title: '', class: 'min' },
				{ key: 'name', title: 'Parameter', sortable: true },
				{ key: 'yld', title: 'Initial Value', sortable: true },
				{ key: 'delete', title: '', class: 'min' },
			],
			chgTypes: [
				{ value: 'absval', title: 'Change parameter value (absval)' },
				{ value: 'abschg', title: 'Change by an amount (abschg)' },
				{ value: 'pctchg', title: 'Change by a percent (pctchg)' }
			]
		},
		plant: {
			item: {
				name: '',
				yld: 0,
				params: []
			},
			param: {
				var: '',
				init: 0,
				chg_typ: '',
				neg: 0,
				pos: 0,
				lo: 0,
				up: 0
			},
			saving: false,
			error: null,
			show: false,
			isNew: true,
			editIndex: -1
		}
	});

	async function get() {
		data.page.loading = true;
		data.page.error = null;
		data.page.showError = false;

		try {
			const response = await api.get(`change/plant_growth`, currentProject.getApiHeader());
			errors.log(response.data);
			data.enabled = response.data.enabled;
			data.plants = response.data.plants;
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
		data.page.saveSuccess = false;

		try {
			let formData = {
				enabled: data.enabled,
				plants: data.plants,
			};

			await api.put(`change/plant_growth`, formData, currentProject.getApiHeader());
			data.page.saveSuccess = true;
		} catch (error) {
			data.page.error = errors.logError(error, 'Unable to save changes to database.');
		}

		data.page.saving = false;
		data.page.showError = data.page.error !== null;
	}

	function add() {
		data.plant.item = {
			name: '',
			yld: 0,
			params: [
				{ var: 'pest_stress', init: 0.01, chg_typ: 'abschg', neg: -0.1, pos: 0.1, lo: 0.01, up: 0.1 },
				{ var: 'epco', init: 1, chg_typ: 'abschg', neg: -1, pos: 1, lo: 0, up: 1 },
				{ var: 'lai_pot', init: 5, chg_typ: 'abschg', neg: -2, pos: 2, lo: 2, up: 6 },
				{ var: 'harv_idx', init: 0.5, chg_typ: 'abschg', neg: -0.15, pos: 0.5, lo: 0.2, up: 0.6 }
			]
		};
		data.plant.show = true;
		data.plant.error = null;
		data.plant.editIndex = -1;
		data.plant.isNew = true;
	}

	function edit(item:any) {
		data.plant.item = item;
		data.plant.show = true;
		data.plant.error = null;
		data.plant.editIndex = data.plants.indexOf(item);
		data.plant.isNew = false;
	}

	function remove(item:any) {
		data.plants.splice(data.plants.indexOf(item), 1);
	}

	async function saveItem() {
		data.plant.error = null;

		const { valid } = await plantForm.value.validate();
		if (!valid) {
			data.plant.error = 'Please enter a value for all fields.';
		} else {
			if (data.plant.isNew) {
				data.plants.push(data.plant.item);
			} else {
				data.plants[data.plant.editIndex] = data.plant.item;
			}
			data.plant.show = false;
		}		
	}

	const plantForm = ref();

	onMounted(async () => await get())
	watch(() => route.path, async () => await get())
</script>

<template>
	<project-container :loading="data.page.loading">
		<file-header input-file="water_balance.sft" docs-path="calibration" use-io>
			<router-link to="/edit/change/soft">Soft Calibration</router-link> 
			/ Plant Growth
		</file-header>
		
		<v-form @submit.prevent="save">
			<error-alert as-popup v-model="data.page.showError" :show="data.page.showError" :text="data.page.error" :timeout="-1"></error-alert>
			<success-alert v-model="data.page.saveSuccess" :show="data.page.saveSuccess"></success-alert>

			<div class="form-group mb-0">
				<v-checkbox label="Enable plant growth soft calibration" v-model="data.enabled" hide-details></v-checkbox>
			</div>

			<div v-if="data.enabled">
				<v-divider class="mb-4"></v-divider>
				<p class="mb-4">
					Select plants to calibrate, and enter the yield and parameter limits below. Selected plants should be modeled in your 
					<router-link to="/edit/lum/landuse" class="text-primary">land use management</router-link>.
					When you run the model, it will generate new a hydrology_cal.hyd file with new parameters for your HRUs.
					You can compare this to the values in your original hydrology.hyd, then choose which to use.
					If you choose to use your new hydrology_cal.hyd file, you will rename this to hydrology.hyd, turn off plant growth soft calibration, 
					and re-run the model with the new values.
				</p>

				<v-alert type="info" variant="tonal" v-if="!data.plants || data.plants.length < 1" class="my-3">
					You have not added any plants yet. 
					<a href="#" @click.prevent="add" class="text-primary pointer">Add now.</a>
				</v-alert>

				<v-card v-if="data.plants && data.plants.length > 0">
					<v-data-table class="data-table" density="compact"
						:items="data.plants" :items-per-page="-1"
						:headers="data.options.tableFields">
						<template v-slot:item.edit="{ item }">
							<a href="#" class="text-decoration-none text-primary" title="Edit" @click.prevent="edit(item)">
								<font-awesome-icon :icon="['fas', 'edit']"></font-awesome-icon>
							</a>
						</template>
						<template v-slot:item.delete="{ item }">
							<a href="#" class="text-decoration-none text-error" title="Delete" @click.prevent="remove(item)">
								<font-awesome-icon :icon="['fas', 'times']"></font-awesome-icon>
							</a>
						</template>
						<template v-slot:bottom></template>
					</v-data-table>
				</v-card>
			</div>
			
			<action-bar>
				<v-btn type="submit" :loading="data.page.saving" variant="flat" color="primary" class="mr-2">
					Save Changes
				</v-btn>
				<v-btn type="button" variant="flat" color="info" class="mr-2" @click="add">Add Plant</v-btn>
				<back-button></back-button>
			</action-bar>
		</v-form>

		<v-dialog v-model="data.plant.show">
			<v-card :title="`${data.plant.isNew ? 'Add' : 'Update'} Plant`">
				<v-card-text>
					<error-alert :text="data.plant.error"></error-alert>
					
					<v-form ref="plantForm">
						<div class="form-group">
							<auto-complete label="Select a crop" required
								v-model="data.plant.item.name" :value="data.plant.item.name"
								table-name="plant" route-name="PlantsEdit"
								section="Databases / Plants" help-file="plants.plt" help-db="plants_plt"
								api-url="db/plants"></auto-complete>
						</div>

						<div class="form-group">
							<v-text-field label="Crop yield - average annual t/ha dry weight" v-model.number="data.plant.item.yld" type="number" step="any" required></v-text-field>
						</div>

						<v-table class="table-editor" density="compact" v-if="!data.page.loading">
							<thead>
								<tr class="bg-surface">
									<th class="bg-secondary-tonal">Parameter</th>
									<th class="bg-secondary-tonal">Initial Value</th>
									<th class="bg-secondary-tonal">Type of Change</th>
									<th class="bg-secondary-tonal">Negative Limit</th>
									<th class="bg-secondary-tonal">Positive Limit</th>
									<th class="bg-secondary-tonal">Lower Limit</th>
									<th class="bg-secondary-tonal">Upper Limit</th>
								</tr>
							</thead>
							<tbody>
								<tr v-for="(item, index) in data.plant.item.params" :key="index">
									<td>
										{{ item.var }}
									</td>
									<td>
										<v-text-field v-model.number="item.init" type="number" step="any" hide-details density="compact" required></v-text-field>
									</td>
									<td>
										<v-select v-model="item.chg_typ" :items="data.options.chgTypes" hide-details density="compact" required></v-select>
									</td>
									<td>
										<v-text-field v-model.number="item.neg" type="number" step="any" hide-details density="compact" required></v-text-field>
									</td>
									<td>
										<v-text-field v-model.number="item.pos" type="number" step="any" hide-details density="compact" required></v-text-field>
									</td>
									<td>
										<v-text-field v-model.number="item.lo" type="number" step="any" hide-details density="compact" required></v-text-field>
									</td>
									<td>
										<v-text-field v-model.number="item.up" type="number" step="any" hide-details density="compact" required></v-text-field>
									</td>
								</tr>
							</tbody>
						</v-table>
					</v-form>
				</v-card-text>
				<v-divider></v-divider>
				<v-card-actions>
					<v-btn @click="saveItem" :loading="data.plant.saving" color="primary" variant="text">Save Changes</v-btn>
					<v-btn @click="data.plant.show = false">Cancel</v-btn>
				</v-card-actions>
			</v-card>
		</v-dialog>
	</project-container>
</template>
