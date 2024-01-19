<script setup lang="ts">
	import { reactive, computed, onMounted } from 'vue';
	import { useVuelidate } from '@vuelidate/core';
	import { numeric, required, maxLength } from '@vuelidate/validators';
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
		item: { id: 0, layers: [] },
		isUpdate: false,
		vars: () => {}
	});

	let data:any = reactive({
		page: {
			error: <string|null>null,
			saving: false,
			saveSuccess: false
		},
		hydGrpOptions: [
			{ value: 'A', title: 'A' },
			{ value: 'B', title: 'B' },
			{ value: 'C', title: 'C' },
			{ value: 'D', title: 'D' }
		],
		layers: {
			loading: false,
			sortBy: 'layer_num',
			fields: [],
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
				saving: false
			},
			list: props.item.layers,
			obj: {
				soil_id: props.item.id,
				layer_num: null,
				dp: null,
				bd: null,
				awc: null,
				soil_k: null,
				carbon: null,
				clay: null,
				silt: null,
				sand: null,
				rock: null,
				alb: null,
				usle_k: null,
				ec: null,
				caco3: null,
				ph: null
			}
		}
	});

	const itemRules = computed(() => ({
		name: { required, maxLength: maxLength(constants.formNameMaxLength) },
		hyd_grp: { required },
		dp_tot: { required, numeric },
		anion_excl: { required, numeric },
		perc_crk: { required, numeric },
		texture: {},
		description: {}
	}))
	const v$ = useVuelidate(itemRules, props.item);

	function putDb(formData:any) {
		if (props.isUpdate)
			return api.put('soils/items/' + props.item.id, formData, currentProject.getApiHeader());
		else
			return api.post('soils/items', formData, currentProject.getApiHeader());
	}

	function getDb() {
		return api.get('soils/items/' + props.item.id, currentProject.getApiHeader());
	}

	function postLayerDb(formData:any) {
		return api.post('soils/layer', formData, currentProject.getApiHeader());
	}

	function putLayerDb(id:any, formData:any) {
		return api.put('soils/layer/' + id, formData, currentProject.getApiHeader());
	}

	function deleteLayerDb(id:any) {
		return api.delete('soils/layer/' + id, currentProject.getApiHeader());
	}

	async function getLayers() {
		data.layers.loading = true;

		try {
			const response = await getDb();
			data.layers.list = response.data.layers;
		} catch (error) {
			data.page.error = errors.logError(error, 'Unable to get soil layers from database.');
		}

		data.layers.loading = false;
	}
	
	function get() {
		if (props.isUpdate && props.item.layers && props.item.layers.length > 0) {
			getTableFields();
		}
	}
	
	function getTableFields() {
		data.layers.fields = [];
		let keys = Object.keys(props.item.layers[0]);

		for (let i = 0; i < keys.length; i++) {
			if (keys[i] != 'id' && keys[i] != 'soil_id') {
				let meta = utilities.getMeta(keys[i], props.item.layers[0][keys[i]]);
				data.layers.fields.push({ value: keys[i], title: meta.label, sortable: true, 'class': meta.css, formatter: meta.formatter });
			}
		}

		data.layers.fields.unshift({ key: 'edit', title: '', class: 'min' });
		data.layers.fields.push({ key: 'delete', title: '' });
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
				texture: props.item.texture,
				hyd_grp: props.item.hyd_grp,
				dp_tot: props.item.dp_tot,
				anion_excl: props.item.anion_excl,
				perc_crk: props.item.perc_crk
			};

			if (props.isUpdate) {
				dataItem.id = props.item.id;
			}
			
			try {
				const response = await putDb(dataItem);
				
				if (props.isUpdate)
					data.page.saveSuccess = true;
				else
					router.push({ name: 'Soils', params: { id: response.data.id } });
			} catch (error) {
				data.page.error = errors.logError(error, 'Unable to save changes to database.');
			}
		}

		data.page.saving = false;
	}

	function add() {
		data.layers.form.validated = false;			
		data.layers.form.update = false;
		data.layers.form.id = null;
		data.layers.obj = {
			soil_id: props.item.id,
			layer_num: data.layers.list.length + 1,
			dp: 0,
			bd: 0.9,
			awc: 0,
			soil_k: 0,
			carbon: 0.05,
			clay: 0,
			silt: 0,
			sand: 0,
			rock: 0,
			alb: 0,
			usle_k: 0,
			ec: 0,
			caco3: 0,
			ph: 3				
		};
		data.layers.form.show = true;
	}
	
	function edit(item:any) {
		console.log(item);
		data.layers.form.update = true;
		data.layers.form.id = item.id;
		data.layers.obj = item;
		data.layers.obj.soil_id = props.item.id;
		data.layers.form.show = true;
	}

	function askDelete(item:any) {
		let id = item.id;
		let name = 'soil layer ' + item.layer_num;
		data.layers.delete.id = id;
		data.layers.delete.name = name;
		data.layers.delete.show = true;
	}

	async function confirmDelete() {
		data.layers.delete.error = null;
		data.layers.delete.saving = true;

		try {
			await deleteLayerDb(data.layers.delete.id);
			await getLayers();
			data.layers.delete.show = false;
		} catch (error) {
			data.layers.delete.error = errors.logError(error, 'Unable to delete from database.');
		}

		data.layers.delete.saving = false;
	}

	async function saveLayer() {
		data.layers.form.error = null;
		data.layers.form.saving = true;
		data.layers.form.validated = true;

		if (validateLayer()) {
			let action;
			if (data.layers.form.update) {
				action = putLayerDb(data.layers.form.id, data.layers.obj);
			} else {
				action = postLayerDb(data.layers.obj);
			}

			try {
				await action;
				await getLayers();
				//this.getTableFields();
				data.layers.form.validated = false;
				data.layers.form.show = false;
			} catch (error) {
				data.layers.form.error = errors.logError(error, 'Unable to save layer to database.');
			}
		} else {
			data.layers.form.error = 'Please enter a value for all fields and try again.'
		}
		
		data.layers.form.saving = false;
	}

	function validateLayer() {
		let valid = true;
		valid = valid && !formatters.isNullOrEmpty(data.layers.obj.layer_num);
		valid = valid && !formatters.isNullOrEmpty(data.layers.obj.dp);
		valid = valid && !formatters.isNullOrEmpty(data.layers.obj.bd);
		valid = valid && !formatters.isNullOrEmpty(data.layers.obj.awc);
		valid = valid && !formatters.isNullOrEmpty(data.layers.obj.soil_k);
		valid = valid && !formatters.isNullOrEmpty(data.layers.obj.carbon);
		valid = valid && !formatters.isNullOrEmpty(data.layers.obj.clay);
		valid = valid && !formatters.isNullOrEmpty(data.layers.obj.silt);
		valid = valid && !formatters.isNullOrEmpty(data.layers.obj.sand);
		valid = valid && !formatters.isNullOrEmpty(data.layers.obj.rock);
		valid = valid && !formatters.isNullOrEmpty(data.layers.obj.alb);
		valid = valid && !formatters.isNullOrEmpty(data.layers.obj.usle_k);
		valid = valid && !formatters.isNullOrEmpty(data.layers.obj.ec);
		valid = valid && !formatters.isNullOrEmpty(data.layers.obj.caco3);
		valid = valid && !formatters.isNullOrEmpty(data.layers.obj.ph);
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
				<v-text-field v-model="item.texture" 
					label="Texture (optional)"
					:error-messages="v$.texture.$errors.map(e => e.$message).join(', ')"
					@input="v$.texture.$touch" @blur="v$.texture.$touch"></v-text-field>
			</div>

			<div class="form-group">
				<v-text-field v-model="item.description" 
					label="Description (optional)"
					:error-messages="v$.description.$errors.map(e => e.$message).join(', ')"
					@input="v$.description.$touch" @blur="v$.description.$touch"></v-text-field>
			</div>

			<v-row>
				<v-col cols="12" md="6">
					<div class="form-group mb-0">
						<v-select label="Hydrologic group" v-model="item.hyd_grp" 
							:items="data.hydGrpOptions"
							:error-messages="v$.hyd_grp.$errors.map(e => e.$message).join(', ')"
							@input="v$.hyd_grp.$touch" @blur="v$.hyd_grp.$touch"></v-select>
					</div>
				</v-col>
				<v-col cols="12" md="6">
					<div class="form-group mb-0">
						<v-text-field v-model.number.trim="item.dp_tot" 
							label="Maximum rooting depth of soil profile (mm)" type="number" step="any"
							:error-messages="v$.dp_tot.$errors.map(e => e.$message).join(', ')"
							@input="v$.dp_tot.$touch" @blur="v$.dp_tot.$touch"></v-text-field>
					</div>
				</v-col>
			</v-row>

			<v-row>
				<v-col cols="12" md="6">
					<div class="form-group mb-0">
						<v-text-field v-model.number.trim="item.anion_excl" 
							label="Fraction of porosity (void space) from which anions are excluded" type="number" step="any"
							:error-messages="v$.anion_excl.$errors.map(e => e.$message).join(', ')"
							@input="v$.anion_excl.$touch" @blur="v$.anion_excl.$touch"></v-text-field>
					</div>
				</v-col>
				<v-col cols="12" md="6">
					<div class="form-group mb-0">
						<v-text-field v-model.number.trim="item.perc_crk" 
							label="Potential or maximum crack volume of the soil profile expressed as a fraction of the total soil volume" type="number" step="any"
							:error-messages="v$.perc_crk.$errors.map(e => e.$message).join(', ')"
							@input="v$.perc_crk.$touch" @blur="v$.perc_crk.$touch"></v-text-field>
					</div>
				</v-col>
			</v-row>

			<div v-if="isUpdate">
				<h2 class="text-h5 my-3">Soil Layers</h2>
				<div v-if="!data.layers.list || data.layers.list.length < 1" class="alert alert-primary">
					This soil does not have any layers. 
					<a href="#" @click.prevent="add">Add now.</a>
				</div>
				<div v-if="data.layers.list && data.layers.list.length > 0">
					<v-card>
						<v-data-table class="data-table" density="compact"
							:items="data.layers.list" :items-per-page="-1"
							:headers="data.layers.fields">
							<template v-slot:item.edit="{ item }">
								<a href="#" class="text-decoration-none text-primary" title="Edit" @click.prevent="edit(item)">
									<font-awesome-icon :icon="['fas', 'edit']"></font-awesome-icon>
								</a>
							</template>
							<template v-slot:item.delete="{ item }">
								<font-awesome-icon :icon="['fas', 'times']" class="text-error pointer" title="Delete" 
											@click="askDelete(item)"></font-awesome-icon>
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
				<v-btn type="button" variant="flat" color="info" class="mr-2" v-if="isUpdate" @click="add">Add Soil Layer</v-btn>
				<back-button></back-button>
			</action-bar>
		</v-form>

		<v-dialog v-model="data.layers.form.show" :max-width="constants.dialogSizes.lg">
			<v-card :title="(data.layers.form.update ? 'Update' : 'Add') + ' Soil Layer'">
				<v-card-text>
					<error-alert :text="data.layers.form.error"></error-alert>
					
					<v-form :validated="data.layers.form.validated">
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
									v-model="data.layers.obj[v.name]" :value="data.layers.obj[v.name]"
									:var-def="v"></tr-var-editor>
							</tbody>
						</v-table>
					</v-form>
				</v-card-text>
				<v-divider></v-divider>
				<v-card-actions>
					<v-btn @click="saveLayer" :loading="data.layers.form.saving" color="primary" variant="text">Save Changes</v-btn>
					<v-btn @click="data.layers.form.show = false">Cancel</v-btn>
				</v-card-actions>
			</v-card>
		</v-dialog>

		<v-dialog v-model="data.layers.delete.show" :max-width="constants.dialogSizes.md">
			<v-card title="Confirm delete">
				<v-card-text>
					<error-alert :text="data.layers.delete.error"></error-alert>

					<p>
						Are you sure you want to delete <strong>{{data.layers.delete.name}}</strong>?
						This action is permanent and cannot be undone. 
					</p>
				</v-card-text>
				<v-divider></v-divider>
				<v-card-actions>
					<v-btn @click="confirmDelete" :loading="data.layers.delete.saving" color="error" variant="text">Delete</v-btn>
					<v-btn @click="data.layers.delete.show = false">Cancel</v-btn>
				</v-card-actions>
			</v-card>
		</v-dialog>
	</div>
</template>
