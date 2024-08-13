<script setup lang="ts">
	import { reactive, computed, onMounted } from 'vue';
	import { useVuelidate } from '@vuelidate/core';
	import { decimal, required, maxLength } from '@vuelidate/validators';
	import { useRouter } from 'vue-router';
	import { useHelpers } from '@/helpers';
	import TrVarEditor from '@/components/TrVarEditor.vue';

	const router = useRouter();
	const { api, constants, currentProject, errors, formatters, utilities } = useHelpers();

	interface Props {
		item: any,
		isUpdate?: boolean,
		vars: any
	}

	const props = withDefaults(defineProps<Props>(), {
		item: { id: 0, plants: [] },
		isUpdate: false,
		vars: () => {}
	});

	let data:any = reactive({
		page: {
			error: null,
			saving: false,
			saveSuccess: false
		},
		plants: {
			loading: false,
			sortBy: 'plnt_name',
			fields: [
				{ key: 'edit', title: '', class: 'min' },
				{ key: 'plnt_name', title: 'Plant', sortable: true },
				{ key: 'lc_status', title: 'Land Cover', sortable: true },
				{ key: 'lai_init', title: 'Init. LAI', sortable: true },
				{ key: 'bm_init', title: 'Init. Biomass', sortable: true },
				{ key: 'phu_init', title: 'Init. PHU Frac.', sortable: true },
				{ key: 'plnt_pop', title: 'Plant Pop.', sortable: true },
				{ key: 'yrs_init', title: 'Age (yrs)', sortable: true },
				{ key: 'rsd_init', title: 'Init. Residue Cover', sortable: true },
				{ key: 'delete', title: '' }
			],
			delete: {
				show: false,
				id: undefined,
				name: '',
				error: undefined,
				saving: false
			},
			form: {
				show: false,
				id: undefined,
				validated: false,
				error: undefined,
				saving: false,
				update: false
			},
			list: props.item.plants,
			obj: {
				plant_ini_id: props.item.id,
				plnt_name_id: null,
				lc_status: null,
				lai_init: null,
				bm_init: null,
				phu_init: null,
				plnt_pop: null,
				yrs_init: null,
				rsd_init: null
			},
			plnt_name: null
		}
	});

	const itemRules = computed(() => ({
		name: { required, maxLength: maxLength(constants.formNameMaxLength) },
		rot_yr_ini: { required, decimal },
		description: {}
	}))
	const v$ = useVuelidate(itemRules, props.item);

	function putDb(formData:any) {
		if (props.isUpdate)
			return api.put('init/plant_ini/' + props.item.id, formData, currentProject.getApiHeader());
		else
			return api.post('init/plant_ini', formData, currentProject.getApiHeader());
	}

	function getDb() {
		return api.get('init/plant_ini/' + props.item.id, currentProject.getApiHeader());
	}

	function postPlantDb(formData:any) {
		return api.post('init/plant_ini_item', formData, currentProject.getApiHeader());
	}

	function putPlantDb(id:any, formData:any) {
		return api.put('init/plant_ini_item/' + id, formData, currentProject.getApiHeader());
	}

	function deletePlantDb(id:any) {
		return api.delete('init/plant_ini_item/' + id, currentProject.getApiHeader());
	}

	async function getPlants() {
		data.plants.loading = true;

		try {
			const response = await getDb();
			data.plants.list = response.data.plants;
			setPlantNames();
		} catch (error) {
			data.page.error = errors.logError(error, 'Unable to get plants from database.');
		}

		data.plants.loading = false;
	}

	function setPlantNames() {
		if (props.isUpdate && data.plants.list) {
			for (let i = 0; i < data.plants.list.length; i++) {
				let p = data.plants.list[i].plnt_name;
				data.plants.list[i].plnt_name_name = p == null ? null : p.name;
			}
		}
	}
	
	function get() {
		setPlantNames();
	}

	async function save() {
		data.page.error = null;
		data.page.saving = true;
		data.page.saveSuccess = false;

		const valid = await v$.value.$validate();
		if (!valid) {
			data.page.error = 'Please fix the errors below and try again.';
		} else {
			let dataItem:any = {
				name: formatters.toValidName(props.item.name),
				description: props.item.description,
				rot_yr_ini: props.item.rot_yr_ini,
			};

			if (props.isUpdate) {
				dataItem.id = props.item.id;
			}
			
			try {
				const response = await putDb(dataItem);
				
				if (props.isUpdate)
					data.page.saveSuccess = true;
				else
					router.push({ name: 'PlantCommEdit', params: { id: response.data.id } });
			} catch (error) {
				data.page.error = errors.logError(error, 'Unable to save changes to database.');
			}
		}

		data.page.saving = false;
	}

	function add() {
		data.plants.form.validated=false;			
		data.plants.form.update = false;
		data.plants.form.id = null;
		data.plants.obj = {
			plant_ini_id: props.item.id,
			plnt_name_id: null,
			lc_status: null,
			lai_init: null,
			bm_init: null,
			phu_init: null,
			plnt_pop: null,
			yrs_init: null,
			rsd_init: null				
		};
		data.plants.plnt_name = null;
		data.plants.form.show = true;
	}
	
	function edit(item:any) {
		data.plants.form.update = true;
		data.plants.form.id = item.id;
		data.plants.obj = {
			id: item.id,
			plant_ini_id: props.item.id,
			plnt_name_id: item.plnt_name_id,
			lc_status: item.lc_status,
			lai_init: item.lai_init,
			bm_init: item.bm_init,
			phu_init: item.phu_init,
			plnt_pop: item.plnt_pop,
			yrs_init: item.yrs_init,
			rsd_init: item.rsd_init				
		};
		data.plants.plnt_name = item.plnt_name_name;
		data.plants.form.show = true;
	}

	function askDelete(item:any) {
		let id = item.id;
		let name = 'plant ' + item.plnt_name_name;
		data.plants.delete.id = id;
		data.plants.delete.name = name;
		data.plants.delete.show = true;
	}

	async function confirmDelete() {
		data.plants.delete.error = null;
		data.plants.delete.saving = true;

		try {
			await deletePlantDb(data.plants.delete.id);
			await getPlants();
			data.plants.delete.show = false;
		} catch (error) {
			data.plants.delete.error = errors.logError(error, 'Unable to delete from database.');
		}

		data.plants.delete.saving = false;
	}

	async function savePlant() {
		data.plants.form.error = null;
		data.plants.form.saving = true;
		data.plants.form.validated = true;

		if (validatePlant()) {
			try {
				const response = await utilities.getAutoCompleteId('plant', data.plants.plnt_name);
				data.plants.obj.plnt_name_id = response.data.id;
			} catch (error) {
				data.plants.form.error = errors.logError(error, 'Invalid plant name, ' + data.plants.plnt_name + '. Please make sure it exists in your database.');
			}

			if (formatters.isNullOrEmpty(data.plants.form.error)) {
				let action;
				if (data.plants.form.update) {
					action = putPlantDb(data.plants.form.id, data.plants.obj);
				} else {
					action = postPlantDb(data.plants.obj);
				}

				try {
					await action;
					await getPlants();
					data.plants.form.validated = false;
					data.plants.form.show = false;
				} catch (error) {
					data.plants.form.error = errors.logError(error, 'Unable to save plant to database.');
				}
			}			
		} else {
			data.plants.form.error = 'Please enter a value for all fields and try again.'
		}
		
		data.plants.form.saving = false;
	}

	function validatePlant() {
		let valid = true;
		valid = valid && !formatters.isNullOrEmpty(data.plants.plnt_name);
		valid = valid && !formatters.isNullOrEmpty(data.plants.obj.lc_status);
		valid = valid && !formatters.isNullOrEmpty(data.plants.obj.lai_init);
		valid = valid && !formatters.isNullOrEmpty(data.plants.obj.bm_init);
		valid = valid && !formatters.isNullOrEmpty(data.plants.obj.phu_init);
		valid = valid && !formatters.isNullOrEmpty(data.plants.obj.plnt_pop);
		valid = valid && !formatters.isNullOrEmpty(data.plants.obj.yrs_init);
		valid = valid && !formatters.isNullOrEmpty(data.plants.obj.rsd_init);
		return valid;
	}

	onMounted(() => get())
</script>

<template>
	<div>
		<error-alert :text="data.page.error"></error-alert>
		<success-alert v-model="data.page.saveSuccess" :show="data.page.saveSuccess"></success-alert>
		
		<v-form @submit.prevent="save">
			<div class="form-group">
				<v-text-field v-model="item.name" 
					label="Name" hint="Must be unique"
					:error-messages="v$.name.$errors.map(e => e.$message).join(', ')"
					@input="v$.name.$touch" @blur="v$.name.$touch"></v-text-field>
			</div>

			<div class="form-group">
				<v-text-field v-model.number="item.rot_yr_ini" type="number"
					label="Initial Rotation Year"
					:error-messages="v$.rot_yr_ini.$errors.map(e => e.$message).join(', ')"
					@input="v$.rot_yr_ini.$touch" @blur="v$.rot_yr_ini.$touch"></v-text-field>
			</div>

			<div class="form-group">
				<v-text-field v-model="item.description" 
					label="Description (optional)"
					:error-messages="v$.description.$errors.map(e => e.$message).join(', ')"
					@input="v$.description.$touch" @blur="v$.description.$touch"></v-text-field>
			</div>

			<div v-if="isUpdate">
				<h2 class="text-h5 my-3">Plants</h2>
				<v-alert type="info" variant="tonal" class="mb-4" v-if="!data.plants.list || data.plants.list.length < 1">
					This community does not have any plants. 
					<a href="#" @click.prevent="add">Add now.</a>
				</v-alert>
				<div v-if="data.plants.list && data.plants.list.length > 0">
					<v-card>
						<v-data-table class="data-table" density="compact"
							:items="data.plants.list" :items-per-page="-1"
							:headers="data.plants.fields">
							<template v-slot:item.edit="{ item }">
								<a href="#" class="text-decoration-none text-primary" title="Edit" @click.prevent="edit(item)">
									<font-awesome-icon :icon="['fas', 'edit']"></font-awesome-icon>
								</a>
							</template>
							<template v-slot:item.delete="{ item }">
								<font-awesome-icon :icon="['fas', 'times']" class="text-error pointer" title="Delete" 
											@click="askDelete(item)"></font-awesome-icon>
							</template>
							<template v-slot:item.lc_status="{ value }">
								{{ value ? 'Yes' : 'No' }}
							</template>							
							<template v-slot:item.plnt_name="{ value }">
								<router-link v-if="!formatters.isNullOrEmpty(value)" :to="`/edit/db/plants/edit/${value.id}`" class="text-primary text-decoration-none">{{ value.name }}</router-link>
								<span v-else>-</span>
							</template>
							<template v-slot:bottom></template>
						</v-data-table>
					</v-card>
				</div>
			</div>

			<action-bar>
				<v-btn type="submit" :loading="data.page.saving" variant="flat" color="primary" class="mr-2">
					Save Changes
				</v-btn>
				<v-btn type="button" variant="flat" color="info" class="mr-2" v-if="isUpdate" @click="add">Add Plant to Community</v-btn>
				<back-button></back-button>
			</action-bar>
		</v-form>

		<v-dialog v-model="data.plants.form.show" :max-width="constants.dialogSizes.lg">
			<v-card :title="(data.plants.form.update ? 'Update' : 'Add') + ' Soil Layer'">
				<v-card-text>
					<error-alert :text="data.plants.form.error"></error-alert>
					
					<v-form :validated="data.plants.form.validated">
						<div class="form-group">
							<auto-complete label="Plant"
								v-model="data.plants.plnt_name" :value="data.plants.plnt_name" :show-item-link="data.plants.form.update"
								table-name="plant" route-name="PlantsEdit"
								section="Databases / Plants" help-file="plants.plt" help-db="plants_plt"
								api-url="db/plants"></auto-complete>
						</div>

						<v-table class="table-editor" density="compact">
							<thead class="thead-light">
								<tr class="bg-surface">
									<th class="bg-secondary-tonal">Value</th>
									<th class="bg-secondary-tonal">Description</th>
									<th class="bg-secondary-tonal">SWAT+ Variable</th>
									<th class="bg-secondary-tonal">Default</th>
									<th class="bg-secondary-tonal">Recommended Range</th>
								</tr>
							</thead>
							<tbody>
								<tr-var-editor v-for="(v, i) in props.vars" :key="i"
									:id="'item_' + v.name" required show-range
									v-model="data.plants.obj[v.name]" :value="data.plants.obj[v.name]"
									:var-def="v"></tr-var-editor>
							</tbody>
						</v-table>
					</v-form>
				</v-card-text>
				<v-divider></v-divider>
				<v-card-actions>
					<v-btn @click="savePlant" :loading="data.plants.form.saving" color="primary" variant="text">Save Changes</v-btn>
					<v-btn @click="data.plants.form.show = false">Cancel</v-btn>
				</v-card-actions>
			</v-card>
		</v-dialog>

		<v-dialog v-model="data.plants.delete.show" :max-width="constants.dialogSizes.md">
			<v-card title="Confirm delete">
				<v-card-text>
					<error-alert :text="data.plants.delete.error"></error-alert>

					<p>
						Are you sure you want to delete <strong>{{data.plants.delete.name}}</strong>?
						This action is permanent and cannot be undone. 
					</p>
				</v-card-text>
				<v-divider></v-divider>
				<v-card-actions>
					<v-btn @click="confirmDelete" :loading="data.plants.delete.saving" color="error" variant="text">Delete</v-btn>
					<v-btn @click="data.plants.delete.show = false">Cancel</v-btn>
				</v-card-actions>
			</v-card>
		</v-dialog>
	</div>
</template>
