<script setup lang="ts">
	import { reactive, computed } from 'vue';
	import { useVuelidate } from '@vuelidate/core';
	import { decimal, required } from '@vuelidate/validators';
	import { useRouter } from 'vue-router';
	import { useHelpers } from '@/helpers';

	const router = useRouter();
	const { api, constants, currentProject, errors, formatters, utilities } = useHelpers();

	interface Props {
		item: any,
		isUpdate?: boolean
	}

	const props = withDefaults(defineProps<Props>(), {
		item: { id: 0 },
		isUpdate: false
	});

	interface TimestepValue {
		id: number|null,
		sta_id: number,
		timestep: number,
		nh4_wet: number,
		no3_wet: number,
		nh4_dry: number,
		no3_dry: number
	}

	let page:any = reactive({
		loading: true,
		error: <string|null>null,
		saving: false,
		saveSuccess: false,
		values: {
			list: <any[]>(props.item.values || []),
			obj: <TimestepValue>{
				id: null,
				sta_id: props.item.id,
				timestep: 0,
				nh4_wet: 0,
				no3_wet: 0,
				nh4_dry: 0,
				no3_dry: 0
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
			},
			fields: [
				{ key: 'timestep', label: 'Timestep' },
				{ key: 'nh4_wet', label: 'NH4 RF' },
				{ key: 'no3_wet', label: 'NO3 RF' },
				{ key: 'nh4_dry', label: 'NH4 Dry' },
				{ key: 'no3_dry', label: 'NO3 Dry' }
			]
		}
	});

	const itemRules = computed(() => ({
		name: { required }
	}))
	const v$ = useVuelidate(itemRules, props.item);

	const valueRules = computed(() => ({
		sta_id: { required },
		timestep: { required },
		nh4_wet: { required, decimal },
		no3_wet: { required, decimal },
		nh4_dry: { required, decimal },
		no3_dry: { required, decimal }
	}))
	const vo$ = useVuelidate(valueRules, page.values.obj);

	function putDb(data:any) {
		if (props.isUpdate)
			return api.put(`climate/atmo/stations/${props.item.id}`, data, currentProject.getApiHeader());
		else
			return api.post(`climate/atmo/stations`, data, currentProject.getApiHeader());
	}

	async function save() {
		page.error = null;
		page.saving = true;
		page.saveSuccess = false;

		const valid = await v$.value.$validate();
		if (!valid) {
			page.error = 'Please fix the errors below and try again.';
		} else {
			let data = {
				name: formatters.toValidName(props.item.name),
				atmo_cli_id: props.item.atmo_cli_id
			};
			
			try {
				const response = await putDb(data);
				
				if (props.isUpdate)
					page.saveSuccess = true;
				else
					router.push({ name: 'StationsAtmoEdit', params: { id: response.data.id } });
			} catch (error) {
				page.error = errors.logError(error, 'Unable to save changes to database.');
			}
		}

		page.saving = false;
	}

	async function getValues() {
		page.values.loading = true;

		try {
			const response = await api.get(`climate/atmo/stations/${props.item.id}`, currentProject.getApiHeader());
			page.values.list = response.data.values;
		} catch (error) {
			page.error = errors.logError(error, 'Unable to get atmo. station values from database.');
		}	

		page.values.loading = false;
	}

	function add() {
		page.values.form.update = false;
		page.values.form.id = null;
		page.values.obj.id = null;
		page.values.obj.sta_id = props.item.id;
		page.values.obj.timestep = 0;
		page.values.obj.nh4_wet = 0;
		page.values.obj.no3_wet = 0;
		page.values.obj.nh4_dry = 0;
		page.values.obj.no3_dry = 0;

		page.values.form.show = true;
	}

	function edit(item:TimestepValue) {
		page.values.form.update = true;
		page.values.form.id = item.id;
		page.values.obj = item;
		page.values.form.show = true;
	}

	async function saveValues() {
		page.values.form.error = null;
		page.values.form.saving = true;

		const valid = await vo$.value.$validate();
		if (!valid) {
			page.values.form.error = 'Please fix the errors below and try again.';
		} else {
			let action;
			if (page.values.form.update) {
				action = api.put(`climate/atmo/values/${page.values.form.id}`, page.values.obj, currentProject.getApiHeader());
			} else {
				action = api.post(`climate/atmo/values`, page.values.obj, currentProject.getApiHeader());
			}

			try {
				await action;
				await getValues();
				page.values.form.show = false;
				vo$.value.$reset();
			} catch (error) {
				page.values.form.error = errors.logError(error, 'Unable to save values to database.');
			}
		}

		page.values.form.saving = false;
	}

	function askDelete(id:any, name:any) {
		page.values.delete.id = id;
		page.values.delete.name = name;
		page.values.delete.show = true;
	}

	async function confirmDelete() {
		page.values.delete.error = null;
		page.values.delete.saving = true;

		try {
			await api.delete(`climate/atmo/values/${page.values.delete.id}`, currentProject.getApiHeader());
			await getValues();
			page.values.delete.show = false;
		} catch (error) {
			page.values.delete.error = errors.logError(error, 'Unable to delete from database.');
		}

		page.values.delete.saving = false;
	}
</script>

<template>
	<div>
		<error-alert :text="page.error"></error-alert>
		<success-alert v-model="page.saveSuccess" :show="page.saveSuccess"></success-alert>

		<v-form @submit.prevent="save">
			<div class="form-group">
				<v-text-field v-model="item.name" 
					label="Name" hint="Must be unique"
					:error-messages="v$.name.$errors.map(e => e.$message).join(', ')"
					@input="v$.name.$touch" @blur="v$.name.$touch"></v-text-field>
			</div>

			<div v-if="props.isUpdate">
				<h2 class="text-h5 my-3">Values</h2>
				<v-alert v-if="!page.values.list || page.values.list.length < 1" variant="tonal" type="info">
					This station does not have any values. 
					<a href="#" @click.prevent="add" class="text-primary">Add now.</a>
				</v-alert>
				<div v-if="page.values.list && page.values.list.length > 0">
					<v-card>
						<v-table class="data-table" fixed-header density="compact">
							<thead>
								<tr class="bg-surface">
									<th class="bg-secondary-tonal min"></th>
									<th class="bg-secondary-tonal text-right" v-for="f in page.values.fields" :key="f.key">
										{{ formatters.isNullOrEmpty(f.label) ? f.key : f.label }}
									</th>
									<th class="bg-secondary-tonal min"></th>
								</tr>
							</thead>
							<tbody v-if="page.values.loading">
								<tr v-for="(v, i) in Array.from(Array(12))" :key="i">
									<td class="min"></td>
									<td v-for="f in page.values.fields" :key="f.key"><v-skeleton-loader type="text" max-width="150"></v-skeleton-loader></td>
									<td class="min"></td>
								</tr>
							</tbody>
							<tbody v-else>
								<tr v-for="(row, j) in page.values.list" :key="j">
									<td class="min">
										<a href="#" class="text-decoration-none text-primary" title="Edit" @click.prevent="edit(row)">
											<font-awesome-icon :icon="['fas', 'edit']"></font-awesome-icon>
										</a>
									</td>
									<td v-for="f in page.values.fields" :key="f.key" class="text-right">
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
			</div>

			<action-bar>
				<v-btn type="submit" :loading="page.saving" variant="flat" color="primary" class="mr-2">
					Save Changes
				</v-btn>
				<v-btn type="button" variant="flat" color="info" class="mr-2"
					v-if="isUpdate" @click="add">Add Values</v-btn>
				<back-button></back-button>
			</action-bar>
		</v-form>

		<v-dialog v-model="page.values.form.show" :max-width="constants.dialogSizes.lg">
			<v-card :title="page.values.form.update ? 'Update values' : 'Add values'">
				<v-card-text>
					<error-alert :text="page.values.form.error"></error-alert>

					<div class="form-group">
						<v-text-field v-model="page.values.obj.timestep" 
							label="Timestep" type="number"
							:error-messages="vo$.timestep.$errors.map(e => e.$message).join(', ')"
							@input="vo$.timestep.$touch" @blur="vo$.timestep.$touch"
							hint="Average Annual = 0; Yearly = YYYY; Monthly = YYYYMM" persistent-hint></v-text-field>
					</div>

					<div class="form-group mb-0">
						<v-text-field v-model="page.values.obj.nh4_wet" 
							label="Wet deposition of ammonia nitrogen (NH4)" type="number" step="any" suffix="mg/l"
							:error-messages="vo$.nh4_wet.$errors.map(e => e.$message).join(', ')"
							@input="vo$.nh4_wet.$touch" @blur="vo$.nh4_wet.$touch"></v-text-field>
					</div>

					<div class="form-group mb-0">
						<v-text-field v-model="page.values.obj.no3_wet" 
							label="Wet deposition of nitrate nitrogen (NO3)" type="number" step="any" suffix="mg/l"
							:error-messages="vo$.no3_wet.$errors.map(e => e.$message).join(', ')"
							@input="vo$.no3_wet.$touch" @blur="vo$.no3_wet.$touch"></v-text-field>
					</div>

					<div class="form-group mb-0">
						<v-text-field v-model="page.values.obj.nh4_dry" 
							label="Dry deposition of ammonia nitrogen (NH4)" type="number" step="any" suffix="kg/ha/yr"
							:error-messages="vo$.nh4_dry.$errors.map(e => e.$message).join(', ')"
							@input="vo$.nh4_dry.$touch" @blur="vo$.nh4_dry.$touch"></v-text-field>
					</div>

					<div class="form-group mb-0">
						<v-text-field v-model="page.values.obj.no3_dry" 
							label="Dry deposition of nitrate nitrogen (NO3)" type="number" step="any" suffix="kg/ha/yr"
							:error-messages="vo$.no3_dry.$errors.map(e => e.$message).join(', ')"
							@input="vo$.no3_dry.$touch" @blur="vo$.no3_dry.$touch"></v-text-field>
					</div>
				</v-card-text>
				<v-divider></v-divider>
				<v-card-actions>
					<v-btn @click="saveValues" :loading="page.values.form.saving" color="primary" variant="text">Save Changes</v-btn>
					<v-btn @click="page.values.form.show = false">Cancel</v-btn>
				</v-card-actions>
			</v-card>
		</v-dialog>
		
		<v-dialog v-model="page.values.delete.show" :max-width="constants.dialogSizes.md">
			<v-card title="Confirm delete">
				<v-card-text>
					<error-alert :text="page.values.delete.error"></error-alert>

					<p>
						Are you sure you want to delete <strong>{{page.values.delete.name}}</strong>?
						This action is permanent and cannot be undone. 
					</p>
				</v-card-text>
				<v-divider></v-divider>
				<v-card-actions>
					<v-btn @click="confirmDelete" :loading="page.values.delete.saving" color="error" variant="text">Delete</v-btn>
					<v-btn @click="page.values.delete.show = false">Cancel</v-btn>
				</v-card-actions>
			</v-card>
		</v-dialog>
	</div>
</template>