<script setup lang="ts">
	import { reactive, onMounted, watch, computed } from 'vue';
	import { useRoute } from 'vue-router';
	import { useHelpers } from '@/helpers';
	import { useVuelidate } from '@vuelidate/core';
	import { decimal, required } from '@vuelidate/validators';

	const route = useRoute();
	const { api, constants, currentProject, errors, formatters, utilities } = useHelpers();

	interface TimestepValue {
		id: number|null,
		sta_id: number,
		timestep: number,
		so4_wet: number,
		ca_wet: number,
		mg_wet: number,
		na_wet: number,
		k_wet: number,
		cl_wet: number,
		co3_wet: number,
		hco3_wet: number,
		so4_dry: number,
		ca_dry: number,
		mg_dry: number,
		na_dry: number,
		k_dry: number,
		cl_dry: number,
		co3_dry: number,
		hco3_dry: number
	}

	let data:any = reactive({
		apiUrl: 'salts/atmo',
		page: {
			loading: false,
			error: null,
			values: {
				obj: <TimestepValue>{
					id: null,
					sta_id: Number(route.params.id),
					timestep: 0,
					so4_wet: 5,
					ca_wet: 2,
					mg_wet: 0.5,
					na_wet: 0.75,
					k_wet: 0.1,
					cl_wet: 1,
					co3_wet: 0,
					hco3_wet: 3,
					so4_dry: 0,
					ca_dry: 0,
					mg_dry: 0,
					na_dry: 0,
					k_dry: 0,
					cl_dry: 0,
					co3_dry: 0,
					hco3_dry: 0
				},
				loading: false,
				delete: {
					show: false,
					id: <number|null>null,
					name: '',
					error: <string|null>null,
					saving: false
				},
				form: {
					show: false,
					id: <number|null>null,
					update: false,
					error: <string|null>null,
					saving: false
				}
			}
		},
		item: {},
		fields: [
			{ key: 'timestep', label: 'Timestep' },
			{ key: 'so4_wet', label: 'Sulfate Wet (Rainfall)' },
			{ key: 'ca_wet', label: 'Calcium Wet (Rainfall)' },
			{ key: 'mg_wet', label: 'Magnesium Wet (Rainfall)' },
			{ key: 'na_wet', label: 'Sodium Wet (Rainfall)' },
			{ key: 'k_wet', label: 'Potassium Wet (Rainfall)' },
			{ key: 'cl_wet', label: 'Chlorine Wet (Rainfall)' },
			{ key: 'co3_wet', label: 'Carbonate Wet (Rainfall)' },
			{ key: 'hco3_wet', label: 'Hydrogen Carbonate Wet (Rainfall)' },
			{ key: 'so4_dry', label: 'Sulfate Dry' },
			{ key: 'ca_dry', label: 'Calcium Dry' },
			{ key: 'mg_dry', label: 'Magnesium Dry' },
			{ key: 'na_dry', label: 'Sodium Dry' },
			{ key: 'k_dry', label: 'Potassium Dry' },
			{ key: 'cl_dry', label: 'Chlorine Dry' },
			{ key: 'co3_dry', label: 'Carbonate Dry' },
			{ key: 'hco3_dry', label: 'Hydrogen Carbonate Dry' },
		]
	});

	const valueRules = computed(() => ({
		sta_id: { required },
		timestep: { required },
		so4_wet: { required, decimal },
		ca_wet: { required, decimal },
		mg_wet: { required, decimal },
		na_wet: { required, decimal },
		k_wet: { required, decimal },
		cl_wet: { required, decimal },
		co3_wet: { required, decimal },
		hco3_wet: { required, decimal },
		so4_dry: { required, decimal },
		ca_dry: { required, decimal },
		mg_dry: { required, decimal },
		na_dry: { required, decimal },
		k_dry: { required, decimal },
		cl_dry: { required, decimal },
		co3_dry: { required, decimal },
		hco3_dry: { required, decimal }
	}))
	const v$ = useVuelidate(valueRules, data.page.values.obj);

	async function get() {
		if (route.params.id === undefined) return;
		data.page.loading = true;
		await getValues();
		data.page.loading = false;
	}

	async function getValues() {
		data.page.values.loading = true;
		data.page.error = null;

		try {
			const response = await api.get(`${data.apiUrl}/${route.params.id}`, currentProject.getApiHeader());
			errors.log(response.data);
			data.item = response.data;
		} catch (error) {
			data.page.error = errors.logError(error, 'Unable to get project information from database.');
		}

		data.page.values.loading = false;
	}

	function add() {
		data.page.values.form.update = false;
		data.page.values.form.id = null;
		data.page.values.obj.id = null;
		data.page.values.obj.sta_id = Number(route.params.id);
		data.page.values.obj.timestep = 0;
		data.page.values.obj.so4_wet = 5;
		data.page.values.obj.ca_wet = 4;
		data.page.values.obj.mg_wet = 0.5;
		data.page.values.obj.na_wet = 0.75;
		data.page.values.obj.k_wet = 0.1;
		data.page.values.obj.cl_wet = 1;
		data.page.values.obj.co3_wet = 0;
		data.page.values.obj.hco3_wet = 3;
		data.page.values.obj.so4_dry = 0;
		data.page.values.obj.ca_dry = 0;
		data.page.values.obj.mg_dry = 0;
		data.page.values.obj.na_dry = 0;
		data.page.values.obj.k_dry = 0;
		data.page.values.obj.cl_dry = 0;
		data.page.values.obj.co3_dry = 0;
		data.page.values.obj.hco3_dry = 0;

		data.page.values.form.show = true;
	}

	function edit(item:TimestepValue) {
		data.page.values.form.update = true;
		data.page.values.form.id = item.id;
		data.page.values.obj = item;
		data.page.values.form.show = true;
	}

	async function saveValues() {
		data.page.values.form.error = null;
		data.page.values.form.saving = true;

		const valid = await v$.value.$validate();
		if (!valid) {
			data.page.values.form.error = 'Please fix the errors below and try again.';
		} else {
			let action;
			if (data.page.values.form.update) {
				action = api.put(`salts/atmo-values/${data.page.values.form.id}`, data.page.values.obj, currentProject.getApiHeader());
			} else {
				action = api.post(`salts/atmo/${route.params.id}`, data.page.values.obj, currentProject.getApiHeader());
			}

			try {
				await action;
				await getValues();
				data.page.values.form.show = false;
				v$.value.$reset();
			} catch (error) {
				data.page.values.form.error = errors.logError(error, 'Unable to save values to database.');
			}
		}

		data.page.values.form.saving = false;
	}

	function askDelete(id:any, name:any) {
		data.page.values.delete.id = id;
		data.page.values.delete.name = name;
		data.page.values.delete.show = true;
	}

	async function confirmDelete() {
		data.page.values.delete.error = null;
		data.page.values.delete.saving = true;

		try {
			await api.delete(`salts/atmo-values/${data.page.values.delete.id}`, currentProject.getApiHeader());
			await getValues();
			data.page.values.delete.show = false;
		} catch (error) {
			data.page.values.delete.error = errors.logError(error, 'Unable to delete from database.');
		}

		data.page.values.delete.saving = false;
	}

	onMounted(async () => await get())
	watch(() => route.name, async () => await get())
	watch(() => route.params.id, async () => await get())
</script>

<template>
	<project-container :loading="data.page.loading" :load-error="data.page.error">
		<div v-if="$route.name == 'ConstituentsSaltsAtmoEdit'">
			<file-header input-file="constituents.cs" docs-path="constituents" use-io>
				<router-link to="/edit/constituents/salts">Salt Constituents</router-link>
				/ <router-link to="/edit/constituents/salts/atmo">Atmospheric Deposition</router-link>
				/ Edit
			</file-header>

			<div class="form-group">
				<v-text-field v-model="data.item.name" label="Name" readonly hint="Name cannot be modified. Matches one of your existing atmospheric deposition stations."></v-text-field>
			</div>

			<h2 class="text-h5 my-3">Values</h2>
			<v-alert v-if="!data.item.values || data.item.values.length < 1" variant="tonal" type="info">
				This station does not have any values. 
				<a href="#" @click.prevent="add" class="text-primary">Add now.</a>
			</v-alert>
			<div v-if="data.item.values && data.item.values.length > 0">
				<v-card>
					<v-table class="data-table" fixed-header density="compact">
						<thead>
							<tr class="bg-surface">
								<th class="bg-secondary-tonal min"></th>
								<th class="bg-secondary-tonal text-right" v-for="f in data.fields" :key="f.key">
									{{ f.key }}
								</th>
								<th class="bg-secondary-tonal min"></th>
							</tr>
						</thead>
						<tbody v-if="data.page.values.loading">
							<tr v-for="(v, i) in Array.from(Array(12))" :key="i">
								<td class="min"></td>
								<td v-for="f in data.fields" :key="f.key"><v-skeleton-loader type="text" max-width="150"></v-skeleton-loader></td>
								<td class="min"></td>
							</tr>
						</tbody>
						<tbody v-else>
							<tr v-for="(row, j) in data.item.values" :key="j">
								<td class="min">
									<a href="#" class="text-decoration-none text-primary" title="Edit" @click.prevent="edit(row)">
										<font-awesome-icon :icon="['fas', 'edit']"></font-awesome-icon>
									</a>
								</td>
								<td v-for="f in data.fields" :key="f.key" class="text-right">
									<span v-if="f.key === 'timestep'">{{ row[f.key] }}</span>
									<span v-else>{{ formatters.toNumberFormat(row[f.key], 3) }}</span>
								</td>
								<td class="min">
									<font-awesome-icon :icon="['fas', 'times']" class="text-error pointer" title="Delete" 
										@click="askDelete(row.id, 'values for timestep ' + row.timestep)"></font-awesome-icon>
								</td>
							</tr>
						</tbody>
					</v-table>
				</v-card>
			</div>

			<action-bar>
				<v-btn type="button" variant="flat" color="info" class="mr-2" @click="add">Add Values</v-btn>
				<back-button></back-button>
			</action-bar>

			<v-dialog v-model="data.page.values.form.show" :max-width="constants.dialogSizes.lg">
				<v-card :title="data.page.values.form.update ? 'Update values' : 'Add values'">
					<v-card-text>
						<error-alert :text="data.page.values.form.error"></error-alert>

						<div class="form-group">
							<v-text-field v-model="data.page.values.obj.timestep" 
								label="Timestep" type="number"
								:error-messages="v$.timestep.$errors.map(e => e.$message).join(', ')"
								@input="v$.timestep.$touch" @blur="v$.timestep.$touch"
								hint="Average Annual = 0; Yearly = YYYY; Monthly = YYYYMM" persistent-hint></v-text-field>
						</div>

						<v-row>
							<v-col cols="12" md="6">
								<div class="form-group mb-0">
									<v-text-field v-model="data.page.values.obj.so4_wet" 
										label="Wet deposition of sulfate (so4)" type="number" step="any" suffix="g/m3"
										:error-messages="v$.so4_wet.$errors.map(e => e.$message).join(', ')"
										@input="v$.so4_wet.$touch" @blur="v$.so4_wet.$touch"></v-text-field>
								</div>
								<div class="form-group mb-0">
									<v-text-field v-model="data.page.values.obj.ca_wet" 
										label="Wet deposition of calcium (ca)" type="number" step="any" suffix="g/m3"
										:error-messages="v$.ca_wet.$errors.map(e => e.$message).join(', ')"
										@input="v$.ca_wet.$touch" @blur="v$.ca_wet.$touch"></v-text-field>
								</div>
								<div class="form-group mb-0">
									<v-text-field v-model="data.page.values.obj.mg_wet" 
										label="Wet deposition of magnesium (mg)" type="number" step="any" suffix="g/m3"
										:error-messages="v$.mg_wet.$errors.map(e => e.$message).join(', ')"
										@input="v$.mg_wet.$touch" @blur="v$.mg_wet.$touch"></v-text-field>
								</div>
								<div class="form-group mb-0">
									<v-text-field v-model="data.page.values.obj.na_wet" 
										label="Wet deposition of sodium (na)" type="number" step="any" suffix="g/m3"
										:error-messages="v$.na_wet.$errors.map(e => e.$message).join(', ')"
										@input="v$.na_wet.$touch" @blur="v$.na_wet.$touch"></v-text-field>
								</div>
								<div class="form-group mb-0">
									<v-text-field v-model="data.page.values.obj.k_wet" 
										label="Wet deposition of potassium (k)" type="number" step="any" suffix="g/m3"
										:error-messages="v$.k_wet.$errors.map(e => e.$message).join(', ')"
										@input="v$.k_wet.$touch" @blur="v$.k_wet.$touch"></v-text-field>
								</div>
								<div class="form-group mb-0">
									<v-text-field v-model="data.page.values.obj.cl_wet" 
										label="Wet deposition of chlorine (cl)" type="number" step="any" suffix="g/m3"
										:error-messages="v$.cl_wet.$errors.map(e => e.$message).join(', ')"
										@input="v$.cl_wet.$touch" @blur="v$.cl_wet.$touch"></v-text-field>
								</div>
								<div class="form-group mb-0">
									<v-text-field v-model="data.page.values.obj.co3_wet" 
										label="Wet deposition of carbonate (co3)" type="number" step="any" suffix="g/m3"
										:error-messages="v$.co3_wet.$errors.map(e => e.$message).join(', ')"
										@input="v$.co3_wet.$touch" @blur="v$.co3_wet.$touch"></v-text-field>
								</div>
								<div class="form-group mb-0">
									<v-text-field v-model="data.page.values.obj.hco3_wet" 
										label="Wet deposition of hydrogen carbonate (hco3)" type="number" step="any" suffix="g/m3"
										:error-messages="v$.hco3_wet.$errors.map(e => e.$message).join(', ')"
										@input="v$.hco3_wet.$touch" @blur="v$.hco3_wet.$touch"></v-text-field>
								</div>
							</v-col>	
							<v-col cols="12" md="6">
								<div class="form-group mb-0">
									<v-text-field v-model="data.page.values.obj.so4_dry" 
										label="Dry deposition of sulfate (so4)" type="number" step="any" suffix="kg/ha"
										:error-messages="v$.so4_dry.$errors.map(e => e.$message).join(', ')"
										@input="v$.so4_dry.$touch" @blur="v$.so4_dry.$touch"></v-text-field>
								</div>
								<div class="form-group mb-0">
									<v-text-field v-model="data.page.values.obj.ca_dry" 
										label="Dry deposition of calcium (ca)" type="number" step="any" suffix="kg/ha"
										:error-messages="v$.ca_dry.$errors.map(e => e.$message).join(', ')"
										@input="v$.ca_dry.$touch" @blur="v$.ca_dry.$touch"></v-text-field>
								</div>
								<div class="form-group mb-0">
									<v-text-field v-model="data.page.values.obj.mg_dry" 
										label="Dry deposition of magnesium (mg)" type="number" step="any" suffix="kg/ha"
										:error-messages="v$.mg_dry.$errors.map(e => e.$message).join(', ')"
										@input="v$.mg_dry.$touch" @blur="v$.mg_dry.$touch"></v-text-field>
								</div>
								<div class="form-group mb-0">
									<v-text-field v-model="data.page.values.obj.na_dry" 
										label="Dry deposition of sodium (na)" type="number" step="any" suffix="kg/ha"
										:error-messages="v$.na_dry.$errors.map(e => e.$message).join(', ')"
										@input="v$.na_dry.$touch" @blur="v$.na_dry.$touch"></v-text-field>
								</div>
								<div class="form-group mb-0">
									<v-text-field v-model="data.page.values.obj.k_dry" 
										label="Dry deposition of potassium (k)" type="number" step="any" suffix="kg/ha"
										:error-messages="v$.k_dry.$errors.map(e => e.$message).join(', ')"
										@input="v$.k_dry.$touch" @blur="v$.k_dry.$touch"></v-text-field>
								</div>
								<div class="form-group mb-0">
									<v-text-field v-model="data.page.values.obj.cl_dry" 
										label="Dry deposition of chlorine (cl)" type="number" step="any" suffix="kg/ha"
										:error-messages="v$.cl_dry.$errors.map(e => e.$message).join(', ')"
										@input="v$.cl_dry.$touch" @blur="v$.cl_dry.$touch"></v-text-field>
								</div>
								<div class="form-group mb-0">
									<v-text-field v-model="data.page.values.obj.co3_dry" 
										label="Dry deposition of carbonate (co3)" type="number" step="any" suffix="kg/ha"
										:error-messages="v$.co3_dry.$errors.map(e => e.$message).join(', ')"
										@input="v$.co3_dry.$touch" @blur="v$.co3_dry.$touch"></v-text-field>
								</div>
								<div class="form-group mb-0">
									<v-text-field v-model="data.page.values.obj.hco3_dry" 
										label="Dry deposition of hydrogen carbonate (hco3)" type="number" step="any" suffix="kg/ha"
										:error-messages="v$.hco3_dry.$errors.map(e => e.$message).join(', ')"
										@input="v$.hco3_dry.$touch" @blur="v$.hco3_dry.$touch"></v-text-field>
								</div>
							</v-col>
						</v-row>
						
					</v-card-text>
					<v-divider></v-divider>
					<v-card-actions>
						<v-btn @click="saveValues" :loading="data.page.values.form.saving" color="primary" variant="text">Save Changes</v-btn>
						<v-btn @click="data.page.values.form.show = false">Cancel</v-btn>
					</v-card-actions>
				</v-card>
			</v-dialog>
			
			<v-dialog v-model="data.page.values.delete.show" :max-width="constants.dialogSizes.md">
				<v-card title="Confirm delete">
					<v-card-text>
						<error-alert :text="data.page.values.delete.error"></error-alert>

						<p>
							Are you sure you want to delete <strong>{{data.page.values.delete.name}}</strong>?
							This action is permanent and cannot be undone. 
						</p>
					</v-card-text>
					<v-divider></v-divider>
					<v-card-actions>
						<v-btn @click="confirmDelete" :loading="data.page.values.delete.saving" color="error" variant="text">Delete</v-btn>
						<v-btn @click="data.page.values.delete.show = false">Cancel</v-btn>
					</v-card-actions>
				</v-card>
			</v-dialog>
		</div>
		<router-view></router-view>
	</project-container>
</template>