<script setup lang="ts">
	import { reactive, onMounted, watch, computed } from 'vue';
	import { useRoute } from 'vue-router';
	import { useHelpers } from '@/helpers';
	import { useVuelidate } from '@vuelidate/core';
	import { numeric, required } from '@vuelidate/validators';

	const route = useRoute();
	const { api, constants, currentProject, errors, formatters, utilities } = useHelpers();

	interface TimestepValue {
		id: number|null,
		sta_id: number,
		timestep: number,
		so4: number,
		ca: number,
		mg: number,
		na: number,
		k: number,
		cl: number,
		co3: number,
		hco3: number
	}

	let data:any = reactive({
		apiUrl: 'salts/road',
		page: {
			loading: false,
			error: null,
			values: {
				obj: <TimestepValue>{
					id: null,
					sta_id: Number(route.params.id),
					timestep: 0,
					so4: 0,
					ca: 0,
					mg: 0,
					na: 1,
					k: 0,
					cl: 1.55,
					co3: 0,
					hco3: 0
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
			{ key: 'so4', label: 'Sulfate' },
			{ key: 'ca', label: 'Calcium' },
			{ key: 'mg', label: 'Magnesium' },
			{ key: 'na', label: 'Sodium' },
			{ key: 'k', label: 'Potassium' },
			{ key: 'cl', label: 'Chlorine' },
			{ key: 'co3', label: 'Carbonate' },
			{ key: 'hco3', label: 'Hydrogen Carbonate' }
		]
	});

	const valueRules = computed(() => ({
		sta_id: { required },
		timestep: { required },
		so4: { required, numeric },
		ca: { required, numeric },
		mg: { required, numeric },
		na: { required, numeric },
		k: { required, numeric },
		cl: { required, numeric },
		co3: { required, numeric },
		hco3: { required, numeric }
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
		data.page.values.obj.so4 = 0;
		data.page.values.obj.ca = 0;
		data.page.values.obj.mg = 0;
		data.page.values.obj.na = 1;
		data.page.values.obj.k = 0;
		data.page.values.obj.cl = 1.55;
		data.page.values.obj.co3 = 0;
		data.page.values.obj.hco3 = 0;

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
				action = api.put(`salts/road-values/${data.page.values.form.id}`, data.page.values.obj, currentProject.getApiHeader());
			} else {
				action = api.post(`salts/road/${route.params.id}`, data.page.values.obj, currentProject.getApiHeader());
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
			await api.delete(`salts/road-values/${data.page.values.delete.id}`, currentProject.getApiHeader());
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
		<div v-if="$route.name == 'ConstituentsSaltsRoadEdit'">
			<file-header input-file="constituents.cs" docs-path="constituents" use-io>
				<router-link to="/edit/constituents/salts">Salt Constituents</router-link>
				/ <router-link to="/edit/constituents/salts/road">Road Salt</router-link>
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
							<v-col cols="12">
								<div class="form-group mb-0">
									<v-text-field v-model="data.page.values.obj.so4" 
										label="Sulfate (so4)" type="number" step="any" suffix="g/m3"
										:error-messages="v$.so4.$errors.map(e => e.$message).join(', ')"
										@input="v$.so4.$touch" @blur="v$.so4.$touch"></v-text-field>
								</div>
								<div class="form-group mb-0">
									<v-text-field v-model="data.page.values.obj.ca" 
										label="Calcium (ca)" type="number" step="any" suffix="g/m3"
										:error-messages="v$.ca.$errors.map(e => e.$message).join(', ')"
										@input="v$.ca.$touch" @blur="v$.ca.$touch"></v-text-field>
								</div>
								<div class="form-group mb-0">
									<v-text-field v-model="data.page.values.obj.mg" 
										label="Magnesium (mg)" type="number" step="any" suffix="g/m3"
										:error-messages="v$.mg.$errors.map(e => e.$message).join(', ')"
										@input="v$.mg.$touch" @blur="v$.mg.$touch"></v-text-field>
								</div>
								<div class="form-group mb-0">
									<v-text-field v-model="data.page.values.obj.na" 
										label="Sodium (na)" type="number" step="any" suffix="g/m3"
										:error-messages="v$.na.$errors.map(e => e.$message).join(', ')"
										@input="v$.na.$touch" @blur="v$.na.$touch"></v-text-field>
								</div>
								<div class="form-group mb-0">
									<v-text-field v-model="data.page.values.obj.k" 
										label="Potassium (k)" type="number" step="any" suffix="g/m3"
										:error-messages="v$.k.$errors.map(e => e.$message).join(', ')"
										@input="v$.k.$touch" @blur="v$.k.$touch"></v-text-field>
								</div>
								<div class="form-group mb-0">
									<v-text-field v-model="data.page.values.obj.cl" 
										label="Chlorine (cl)" type="number" step="any" suffix="g/m3"
										:error-messages="v$.cl.$errors.map(e => e.$message).join(', ')"
										@input="v$.cl.$touch" @blur="v$.cl.$touch"></v-text-field>
								</div>
								<div class="form-group mb-0">
									<v-text-field v-model="data.page.values.obj.co3" 
										label="Carbonate (co3)" type="number" step="any" suffix="g/m3"
										:error-messages="v$.co3.$errors.map(e => e.$message).join(', ')"
										@input="v$.co3.$touch" @blur="v$.co3.$touch"></v-text-field>
								</div>
								<div class="form-group mb-0">
									<v-text-field v-model="data.page.values.obj.hco3" 
										label="Hydrogen carbonate (hco3)" type="number" step="any" suffix="g/m3"
										:error-messages="v$.hco3.$errors.map(e => e.$message).join(', ')"
										@input="v$.hco3.$touch" @blur="v$.hco3.$touch"></v-text-field>
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