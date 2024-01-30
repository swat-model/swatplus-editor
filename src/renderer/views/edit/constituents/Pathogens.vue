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
		hru: {
			items: [],
			constituents: []
		},
		water: {
			items: [],
			constituents: []
		}
	});

	async function add() {
		if (!formatters.isNullOrEmpty(data.add.path) && !data.constituents.paths.includes(data.add.path)) data.constituents.paths.push(data.add.path);
		data.add.path = null;
		await saveConstituents();
	}

	async function remove(name:string) {
		data.constituents.paths.splice(data.constituents.paths.indexOf(name), 1);
		await saveConstituents();
	}

	async function get() {
		data.page.loading = true;
		data.page.error = null;
		data.page.showError = false;

		try {
			const response = await api.get(`init/constituents`, currentProject.getApiHeader());
			data.constituents = response.data;
			errors.log(data.constituents);

			await getItems();
		} catch (error) {
			data.page.error = errors.logError(error, 'Unable to get project information from database.');
		}
			
		data.page.showError = data.page.error !== null;
		data.page.loading = false;
	}

	async function getItems() {
		data.page.error = null;
		data.page.showError = false;

		try {
			const response2 = await api.get(`init/constituents/path-hru`, currentProject.getApiHeader());
			data.hru.constituents = response2.data.constituents;
			checkHruItems(response2.data.items);
			if (data.hru.items.length < 1) addHruItem();

			const response3 = await api.get(`init/constituents/path-water`, currentProject.getApiHeader());
			data.water.constituents = response2.data.constituents;
			checkWaterItems(response3.data.items);
			if (data.water.items.length < 1) addWaterItem();
		} catch (error) {
			data.page.error = errors.logError(error, 'Unable to get project information from database.');
		}

		data.page.showError = data.page.error !== null;
	}

	async function saveConstituents() {
		data.page.error = null;
		data.page.saving = true;
		data.page.itemsLoading = true;
		data.page.showError = false;

		try {
			await saveItems(false);

			let constituentsData = {
				paths: data.constituents.paths
			};
			const response = await api.put(`init/constituents`, constituentsData, currentProject.getApiHeader());
			
			await getItems();
		} catch (error) {
			data.page.error = errors.logError(error, 'Unable to save changes to database.');
		}

		data.page.saving = false;
		data.page.itemsLoading = false;
		data.page.showError = data.page.error !== null;
	}

	async function saveItems(showSaveSuccess:boolean = true) {
		data.page.error = null;
		data.page.saving = true;
		data.page.saveSuccess = false;
		data.page.showError = false;

		const { valid } = await form.value.validate();
		if (!valid) {
			data.page.error = 'Please fix all errors before saving. Enter a name for each initialization.';
		} else {
			try {
				let hruItems = data.hru.items.filter(function(el:any) { return !formatters.isNullOrEmpty(el.name) });
				for (let item of hruItems) {
					item.name = formatters.toValidName(item.name);
				}
				await api.put(`init/constituents/path-hru`, { 'items': hruItems }, currentProject.getApiHeader());

				let waterItems = data.water.items.filter(function(el:any) { return !formatters.isNullOrEmpty(el.name) });
				for (let item of waterItems) {
					item.name = formatters.toValidName(item.name);
				}
				await api.put(`init/constituents/path-water`, { 'items': waterItems }, currentProject.getApiHeader());
				
				if (showSaveSuccess) data.page.saveSuccess = true;
			} catch (error) {
				data.page.error = errors.logError(error, 'Unable to save changes to database.');
			}
		}

		data.page.saving = false;
		data.page.showError = data.page.error !== null;
	}

	function addHruItem() {
		let item = {
			name: null,
			rows: []
		};
		item = addHruEmptyRows(item);
		data.hru.items.push(item);
	}
	
	function addHruEmptyRows(item:any) {
		item.rows = [];
		for (let c of data.hru.constituents) {
			item.rows.push({
				name_id: c.id,
				plant: 0,
				soil: 0
			});
		}
		return item;
	}

	function removeHruItem(item:any) {
		data.hru.items.splice(data.hru.items.indexOf(item), 1);
		if (data.hru.items.length < 1) addHruItem();
	}

	function checkHruItems(items:any[]) {
		let relatedKey = 'path_hrus';
		data.hru.items = [];
		for (let item of items) {
			let newItem:any = {
				name: item.name,
				rows: []
			}

			if (item[relatedKey].length < 1) {
				newItem = addHruEmptyRows(newItem);
			} else {
				for (let row of item[relatedKey]) {
					newItem.rows.push({
						name_id: row.name,
						plant: row.plant,
						soil: row.soil
					});
				}

				let i = 0;
				for (let c of data.hru.constituents) {
					let matches = newItem.rows.filter(function(el:any) { return el.name_id === c.id });
					if (matches.length < 1) {
						let newRow = {
							name_id: c.id,
							plant: 0,
							soil: 0
						};

						newItem.rows.splice(i, 0, newRow);
					}
					i++;
				}
			}

			data.hru.items.push(newItem);
		}
	}

	function addWaterItem() {
		let item = {
			name: null,
			rows: []
		};
		item = addWaterEmptyRows(item);
		data.water.items.push(item);
	}

	function addWaterEmptyRows(item:any) {
		item.rows = [];
		for (let c of data.water.constituents) {
			item.rows.push({
				name_id: c.id,
				water: 0,
				benthic: 0
			});
		}
		return item;
	}

	function removeWaterItem(item:any) {
		data.water.items.splice(data.water.items.indexOf(item), 1);
		if (data.water.items.length < 1) addWaterItem();
	}

	function checkWaterItems(items:any[]) {
		let relatedKey = 'path_waters';
		data.water.items = [];
		for (let item of items) {
			let newItem:any = {
				name: item.name,
				rows: []
			}

			if (item[relatedKey].length < 1) {
				newItem = addWaterEmptyRows(newItem);
			} else {
				for (let row of item[relatedKey]) {
					newItem.rows.push({
						name_id: row.name,
						water: row.water,
						benthic: row.benthic
					});
				}

				let i = 0;
				for (let c of data.water.constituents) {
					let matches = newItem.rows.filter(function(el:any) { return el.name_id === c.id });
					if (matches.length < 1) {
						let newRow = {
							name_id: c.id,
							water: 0,
							benthic: 0
						};

						newItem.rows.splice(i, 0, newRow);
					}
					i++;
				}
			}

			data.water.items.push(newItem);
		}
	}

	const hruFormRules = {
		required: (index:any, value:string) => {
			if (!formatters.isNullOrEmpty(value)) return true;
			for (let row of data.hru.items[index].rows) {
				if (row.plant !== 0 || row.soil !== 0) return 'Name is required';
			}

			return true;
		}
	}

	const waterFormRules = {
		required: (index:any, value:string) => {
			if (!formatters.isNullOrEmpty(value)) return true;
			for (let row of data.water.items[index].rows) {
				if (row.water !== 0 || row.benthic !== 0) return 'Name is required';
			}

			return true;
		}
	}

	const form = ref();

	onMounted(async () => await get())
	watch(() => route.path, async () => await get())
</script>

<template>
	<project-container :loading="data.page.loading">
		<file-header input-file="pest_water/hru.ini" docs-path="constituents" use-io>
			Pathogen Constituents
		</file-header>
		
		<v-form @submit.prevent="saveItems(true)" ref="form">
			<error-alert as-popup v-model="data.page.showError" :show="data.page.showError" :text="data.page.error" :timeout="-1"></error-alert>
			<success-alert v-model="data.page.saveSuccess" :show="data.page.saveSuccess"></success-alert>

			<h2 class="text-h5 my-3">1) Add Pathogens</h2>

			<div class="my-4" v-if="data.constituents.paths.length > 0">
				<v-chip-group>
					<v-chip v-for="d in data.constituents.paths" :key="d" closable @click:close="remove(d)">{{ d }}</v-chip>
				</v-chip-group>
			</div>

			<div class="form-group mb-0">
				<auto-complete label="Add a pathogen"
					v-model="data.add.path" :value="data.add.path"
					table-name="path"
					section="Databases / Pathogens" help-file="pathogen.pth" help-db="pathogens_pth"
					api-url="db/pathogens"></auto-complete>
			</div>
			<div class="mb-4">
				<v-btn variant="flat" color="primary" class="wide ml-1" :disabled="formatters.isNullOrEmpty(data.add.path)" @click="add">Add Pathogen</v-btn>
			</div>

			<page-loading :loading="data.page.itemsLoading"></page-loading>
			<div v-if="!data.page.itemsLoading && data.constituents.paths.length > 0">
				<v-divider class="my-4"></v-divider>

				<p>
					Add HRU and water initialization values for each pathogen.
					Initializations must be given a name in order to be saved.
				</p>

				<h2 class="text-h5 my-3">2) HRU Initializations</h2>

				<v-table class="table-editor" density="compact">
					<thead class="thead-light">
						<tr class="bg-surface">
							<th class="bg-secondary-tonal"></th>
							<th class="bg-secondary-tonal" v-for="c in data.hru.constituents" :key="c.id">{{c.name}}</th>
							<th class="bg-secondary-tonal"></th>
						</tr>
					</thead>
					<tbody v-for="(item, i) in data.hru.items" :key="i">
						<tr>
							<td>
								<v-text-field v-model="item.name" :rules="[constants.formRules.nameLength,hruFormRules.required(i,item.name)]" 
									placeholder="Enter a name for the initialization..." hide-details="auto" density="compact"></v-text-field>
							</td>
							<td v-for="c in data.hru.constituents" :key="c.id"></td>
							<td>
								<font-awesome-icon :icon="['fas', 'times']" class="text-error pointer" title="Delete" @click="removeHruItem(item)"></font-awesome-icon>
							</td>
						</tr>
						<tr>
							<td>Amount of pathogen on plant at start of simulation (kg/ha)</td>
							<td v-for="(c, j) in data.hru.constituents" :key="j">
								<v-text-field type="number" step="any" v-model.number="data.hru.items[i].rows[j].plant" hide-details="auto" density="compact"></v-text-field>
							</td>
							<td></td>
						</tr>
						<tr>
							<td>Amount of pathogen in soil at start of simulation (kg/ha)</td>
							<td v-for="(c, j) in data.hru.constituents" :key="j">
								<v-text-field type="number" step="any" v-model.number="data.hru.items[i].rows[j].soil" hide-details="auto" density="compact"></v-text-field>
							</td>
							<td></td>
						</tr>
					</tbody>
				</v-table>
				<div class="mt-2">
					<v-btn type="button" variant="flat" color="info" @click="addHruItem">Add Row</v-btn>
				</div>

				<v-divider class="my-4"></v-divider>

				<h2 class="text-h5 my-3">3) Water Initializations</h2>

				<v-table class="table-editor" density="compact">
					<thead class="thead-light">
						<tr class="bg-surface">
							<th class="bg-secondary-tonal"></th>
							<th class="bg-secondary-tonal" v-for="c in data.water.constituents" :key="c.id">{{c.name}}</th>
							<th class="bg-secondary-tonal"></th>
						</tr>
					</thead>
					<tbody v-for="(item, i) in data.water.items" :key="i">
						<tr>
							<td>
								<v-text-field v-model="item.name" :rules="[constants.formRules.nameLength,waterFormRules.required(i,item.name)]" 
									placeholder="Enter a name for the initialization..." hide-details="auto" density="compact"></v-text-field>
							</td>
							<td v-for="c in data.water.constituents" :key="c.id"></td>
							<td>
								<font-awesome-icon :icon="['fas', 'times']" class="text-error pointer" title="Delete" @click="removeWaterItem(item)"></font-awesome-icon>
							</td>
						</tr>
						<tr>
							<td>Amount of pathogen in water at start of simulation (kg/ha)</td>
							<td v-for="(c, j) in data.water.constituents" :key="j">
								<v-text-field type="number" step="any" v-model.number="data.water.items[i].rows[j].water" hide-details="auto" density="compact"></v-text-field>
							</td>
							<td></td>
						</tr>
						<tr>
							<td>Amount of pathogen in the benthic zone at start of simulation (kg/ha)</td>
							<td v-for="(c, j) in data.water.constituents" :key="j">
								<v-text-field type="number" step="any" v-model.number="data.water.items[i].rows[j].benthic" hide-details="auto" density="compact"></v-text-field>
							</td>
							<td></td>
						</tr>
					</tbody>
				</v-table>
				<div class="mt-2">
					<v-btn type="button" variant="flat" color="info" @click="addWaterItem">Add Row</v-btn>
				</div>
			</div>

			<action-bar>
				<v-btn type="submit" :loading="data.page.saving" variant="flat" color="primary" class="mr-2">
					Save Changes
				</v-btn>
				<back-button></back-button>
			</action-bar>
		</v-form>
	</project-container>
</template>
