<script setup lang="ts">
	import { reactive, computed } from 'vue';
	import { VSkeletonLoader } from 'vuetify/labs/VSkeletonLoader';
	import { useVuelidate } from '@vuelidate/core';
	import { numeric, required, maxLength } from '@vuelidate/validators';
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

	interface MonthlyValue {
		id: number|null,
		weather_wgn_cli_id: number,
		month: number,
		tmp_max_ave: number|null,
		tmp_min_ave: number|null,
		tmp_max_sd: number|null,
		tmp_min_sd: number|null,
		pcp_ave: number|null,
		pcp_sd: number|null,
		pcp_skew: number|null,
		wet_dry: number|null,
		wet_wet: number|null,
		pcp_days: number|null,
		pcp_hhr: number|null,
		slr_ave: number|null,
		dew_ave: number|null,
		wnd_ave: number|null
	}

	let page:any = reactive({
		loading: true,
		error: <string|null>null,
		saving: false,
		saveSuccess: false,
		values: {
			list: <any[]>(props.item.monthly_values || []),
			obj: <MonthlyValue>{
				weather_wgn_cli_id: props.item.id,
				month: 1,
				tmp_max_ave: null,
				tmp_min_ave: null,
				tmp_max_sd: null,
				tmp_min_sd: null,
				pcp_ave: null,
				pcp_sd: null,
				pcp_skew: null,
				wet_dry: null,
				wet_wet: null,
				pcp_days: null,
				pcp_hhr: null,
				slr_ave: null,
				dew_ave: null,
				wnd_ave: null
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
				{ key: 'month', label: 'Mon' },
				{ key: 'tmp_max_ave', label: 'Max tmp' },
				{ key: 'tmp_min_ave', label: 'Min tmp' },
				{ key: 'tmp_max_sd', label: 'Max tmp std' },
				{ key: 'tmp_min_sd', label: 'Min tmp std' },
				{ key: 'pcp_ave', label: 'Pcp avg' },
				{ key: 'pcp_sd', label: 'Pcp std' },
				{ key: 'pcp_skew', label: 'Pcp skew' },
				{ key: 'wet_dry', label: 'Prob. dry' },
				{ key: 'wet_wet', label: 'Prob. wet' },
				{ key: 'pcp_days', label: 'Pcp days' },
				{ key: 'pcp_hhr', label: 'Max rainfall' },
				{ key: 'slr_ave', label: 'Slr' },
				{ key: 'dew_ave', label: 'Dew' },
				{ key: 'wnd_ave', label: 'Wnd' }
			]
		}
	});

	const itemRules = computed(() => ({
		name: { required, maxLength: maxLength(constants.formNameMaxLength) },
		lat: { required, numeric },
		lon: { required, numeric },
		elev: { required, numeric },
		rain_yrs: { required, numeric }
	}))
	const v$ = useVuelidate(itemRules, props.item);

	const monthlyRules = computed(() => ({
		month: { required, numeric },
		tmp_max_ave: { required, numeric },
		tmp_min_ave: { required, numeric },
		tmp_max_sd: { required, numeric },
		tmp_min_sd: { required, numeric },
		pcp_ave: { required, numeric },
		pcp_sd: { required, numeric },
		pcp_skew: { required, numeric },
		wet_dry: { required, numeric },
		wet_wet: { required, numeric },
		pcp_days: { required, numeric },
		pcp_hhr: { required, numeric },
		slr_ave: { required, numeric },
		dew_ave: { required, numeric },
		wnd_ave: { required, numeric }
	}))
	const vm$ = useVuelidate(monthlyRules, page.values.obj);

	function putDb(data:any) {
		if (props.isUpdate)
			return api.put(`climate/wgn/${props.item.id}`, data, currentProject.getApiHeader());
		else
			return api.post(`climate/wgn`, data, currentProject.getApiHeader());
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
				lat: props.item.lat,
				lon: props.item.lon,
				elev: props.item.elev,
				rain_yrs: props.item.rain_yrs
			};
			
			try {
				const response = await putDb(data);
				
				if (props.isUpdate)
					page.saveSuccess = true;
				else
					router.push({ name: 'WgnEdit', params: { id: response.data.id } });
			} catch (error) {
				page.error = errors.logError(error, 'Unable to save changes to database.');
			}
		}

		page.saving = false;
	}

	const monthOptions = computed(() => {
		if (page.values.list.length < 1) return constants.monthSelectList;
		else {
			let usedMonths = <number[]>[];
			for (let v of page.values.list) {
				usedMonths.push(v.month);
			}

			return constants.monthSelectList.filter(function (el) { return !usedMonths.includes(el.value); })
		}
	})

	async function getValues() {
		page.values.loading = true;

		try {
			const response = await api.get(`climate/wgn/${props.item.id}`, currentProject.getApiHeader());
			page.values.list = response.data.monthly_values;
		} catch (error) {
			page.error = errors.logError(error, 'Unable to get wgn monthly values from database.');
		}	

		page.values.loading = false;
	}

	function add() {
		page.values.form.update = false;
		page.values.form.id = null;
		page.values.obj.weather_wgn_cli_id = props.item.id;
		page.values.obj.month = 1;
		page.values.obj.tmp_max_ave = null;
		page.values.obj.tmp_min_ave = null;
		page.values.obj.tmp_max_sd = null;
		page.values.obj.tmp_min_sd = null;
		page.values.obj.pcp_ave = null;
		page.values.obj.pcp_sd = null;
		page.values.obj.pcp_skew = null;
		page.values.obj.wet_dry = null;
		page.values.obj.wet_wet = null;
		page.values.obj.pcp_days = null;
		page.values.obj.pcp_hhr = null;
		page.values.obj.slr_ave = null;
		page.values.obj.dew_ave = null;
		page.values.obj.wnd_ave = null;

		if (page.values.list.length > 0 && monthOptions.value.length > 0) {
			page.values.obj.month = monthOptions.value[0].value;
		}

		page.values.form.show = true;
	}

	function edit(item:MonthlyValue) {
		page.values.form.update = true;
		page.values.form.id = item.id;
		page.values.obj = item;
		page.values.form.show = true;
	}

	async function saveValues() {
		page.values.form.error = null;
		page.values.form.saving = true;

		const valid = await vm$.value.$validate();
		if (!valid) {
			page.values.form.error = 'Please fix the errors below and try again.';
		} else {
			let action;
			if (page.values.form.update) {
				action = api.put(`climate/wgn/mon-value/${page.values.form.id}`, page.values.obj, currentProject.getApiHeader());
			} else {
				action = api.post(`climate/wgn/mon-table/${props.item.id}`, page.values.obj, currentProject.getApiHeader());
			}

			try {
				await action;
				await getValues();
				page.values.form.show = false;
				vm$.value.$reset();
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
			await api.delete(`climate/wgn/mon-value/${page.values.delete.id}`, currentProject.getApiHeader());
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

			<v-row>
				<v-col cols="12" md="6">
					<div class="form-group mb-0">
						<v-text-field v-model="item.lat" 
							label="Latitude" type="number" step="any"
							:error-messages="v$.lat.$errors.map(e => e.$message).join(', ')"
							@input="v$.lat.$touch" @blur="v$.lat.$touch"></v-text-field>
					</div>
				</v-col>
				<v-col cols="12" md="6">
					<div class="form-group mb-0">
						<v-text-field v-model="item.lon" 
							label="Longitude" type="number" step="any"
							:error-messages="v$.lon.$errors.map(e => e.$message).join(', ')"
							@input="v$.lon.$touch" @blur="v$.lon.$touch"></v-text-field>
					</div>
				</v-col>
			</v-row>

			<v-row>
				<v-col cols="12" md="6">
					<div class="form-group mb-0">
						<v-text-field v-model="item.elev" 
							label="Elevation (m)" type="number" step="any"
							:error-messages="v$.elev.$errors.map(e => e.$message).join(', ')"
							@input="v$.elev.$touch" @blur="v$.elev.$touch"></v-text-field>
					</div>
				</v-col>
				<v-col cols="12" md="6">
					<div class="form-group mb-0">
						<v-text-field v-model="item.rain_yrs" 
							label="Years of recorded max monthly 0.5h rainfall data" type="number" step="any"
							:error-messages="v$.rain_yrs.$errors.map(e => e.$message).join(', ')"
							@input="v$.rain_yrs.$touch" @blur="v$.rain_yrs.$touch"></v-text-field>
					</div>
				</v-col>
			</v-row>

			<div v-if="props.isUpdate">
				<h2 class="my-3">Monthly Values</h2>
				<div v-if="!page.values.list || page.values.list.length < 1" class="alert alert-primary">
					This weather generator does not have any monthly values. 
					<a href="#" @click.prevent="add">Add now.</a>
				</div>
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
										<span v-if="f.key === 'month'">{{ row[f.key] }}</span>
										<span v-else>{{ formatters.toNumberFormat(row[f.key], 3) }}</span>
									</td>
									<td class="min">
										<font-awesome-icon :icon="['fas', 'times']" class="text-error pointer" title="Delete" 
											@click="askDelete(row.id, row.name)"></font-awesome-icon>
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
					v-if="isUpdate && (!page.values.list || page.values.list.length < 12)" @click="add">Add Monthly Values</v-btn>
				<back-button></back-button>
			</action-bar>
		</v-form>

		<v-dialog v-model="page.values.form.show" :max-width="constants.dialogSizes.lg">
			<v-card :title="page.values.form.update ? 'Update monthly values' : 'Add monthly values'">
				<v-card-text>
					<error-alert :text="page.values.form.error"></error-alert>

					<div class="form-group mb-0">
						<v-select label="Month" v-model="page.values.obj.month" 
							:items="page.values.form.update ? constants.monthSelectList : monthOptions" 
							:disabled="page.values.form.update"
							:error-messages="vm$.month.$errors.map(e => e.$message).join(', ')"
							@input="vm$.month.$touch" @blur="vm$.month.$touch"></v-select>
					</div>

					<v-row>
						<v-col cols="12" md="6">
							<div class="form-group mb-0">
								<v-text-field v-model="page.values.obj.tmp_max_ave" 
									label="Avg max daily temperature (°C)" type="number" step="any"
									:error-messages="vm$.tmp_max_ave.$errors.map(e => e.$message).join(', ')"
									@input="vm$.tmp_max_ave.$touch" @blur="vm$.tmp_max_ave.$touch"></v-text-field>
							</div>
						</v-col>
						<v-col cols="12" md="6">
							<div class="form-group mb-0">
								<v-text-field v-model="page.values.obj.tmp_min_ave" 
									label="Avg min daily temperature (°C)" type="number" step="any"
									:error-messages="vm$.tmp_min_ave.$errors.map(e => e.$message).join(', ')"
									@input="vm$.tmp_min_ave.$touch" @blur="vm$.tmp_min_ave.$touch"></v-text-field>
							</div>
						</v-col>
					</v-row>

					<v-row>
						<v-col cols="12" md="6">
							<div class="form-group mb-0">
								<v-text-field v-model="page.values.obj.tmp_max_sd" 
									label="Std deviation for daily max temperature (°C)" type="number" step="any"
									:error-messages="vm$.tmp_max_sd.$errors.map(e => e.$message).join(', ')"
									@input="vm$.tmp_max_sd.$touch" @blur="vm$.tmp_max_sd.$touch"></v-text-field>
							</div>
						</v-col>
						<v-col cols="12" md="6">
							<div class="form-group mb-0">
								<v-text-field v-model="page.values.obj.tmp_min_sd" 
									label="Std deviation for daily min temperature (°C)" type="number" step="any"
									:error-messages="vm$.tmp_min_sd.$errors.map(e => e.$message).join(', ')"
									@input="vm$.tmp_min_sd.$touch" @blur="vm$.tmp_min_sd.$touch"></v-text-field>
							</div>
						</v-col>
					</v-row>

					<v-row>
						<v-col cols="12" md="6">
							<div class="form-group mb-0">
								<v-text-field v-model="page.values.obj.pcp_ave" 
									label="Avg total monthly precipitation (mm)" type="number" step="any"
									:error-messages="vm$.pcp_ave.$errors.map(e => e.$message).join(', ')"
									@input="vm$.pcp_ave.$touch" @blur="vm$.pcp_ave.$touch"></v-text-field>
							</div>
						</v-col>
						<v-col cols="12" md="6">
							<div class="form-group mb-0">
								<v-text-field v-model="page.values.obj.pcp_sd" 
									label="Std deviation for avg daily precipitation (mm/day)" type="number" step="any"
									:error-messages="vm$.pcp_sd.$errors.map(e => e.$message).join(', ')"
									@input="vm$.pcp_sd.$touch" @blur="vm$.pcp_sd.$touch"></v-text-field>
							</div>
						</v-col>
					</v-row>

					<v-row>
						<v-col cols="12" md="6">
							<div class="form-group mb-0">
								<v-text-field v-model="page.values.obj.pcp_skew" 
									label="Skew coefficient for avg daily precipitation (mm)" type="number" step="any"
									:error-messages="vm$.pcp_skew.$errors.map(e => e.$message).join(', ')"
									@input="vm$.pcp_skew.$touch" @blur="vm$.pcp_skew.$touch"></v-text-field>
							</div>
						</v-col>
						<v-col cols="12" md="6">
							<div class="form-group mb-0">
								<v-text-field v-model="page.values.obj.wet_dry" 
									label="Probability of a wet day after a dry day" type="number" step="any"
									:error-messages="vm$.wet_dry.$errors.map(e => e.$message).join(', ')"
									@input="vm$.wet_dry.$touch" @blur="vm$.wet_dry.$touch"></v-text-field>
							</div>
						</v-col>
					</v-row>

					<v-row>
						<v-col cols="12" md="6">
							<div class="form-group mb-0">
								<v-text-field v-model="page.values.obj.wet_wet" 
									label="Probability of a wet day after a wet day" type="number" step="any"
									:error-messages="vm$.wet_wet.$errors.map(e => e.$message).join(', ')"
									@input="vm$.wet_wet.$touch" @blur="vm$.wet_wet.$touch"></v-text-field>
							</div>
						</v-col>
						<v-col cols="12" md="6">
							<div class="form-group mb-0">
								<v-text-field v-model="page.values.obj.pcp_days" 
									label="Avg # of precipitation days in month" type="number" step="any"
									:error-messages="vm$.pcp_days.$errors.map(e => e.$message).join(', ')"
									@input="vm$.pcp_days.$touch" @blur="vm$.pcp_days.$touch"></v-text-field>
							</div>
						</v-col>
					</v-row>

					<v-row>
						<v-col cols="12" md="6">
							<div class="form-group mb-0">
								<v-text-field v-model="page.values.obj.pcp_hhr" 
									label="Max 0.5hr rainfall in entire period (mm)" type="number" step="any"
									:error-messages="vm$.pcp_hhr.$errors.map(e => e.$message).join(', ')"
									@input="vm$.pcp_hhr.$touch" @blur="vm$.pcp_hhr.$touch"></v-text-field>
							</div>
						</v-col>
						<v-col cols="12" md="6">
							<div class="form-group mb-0">
								<v-text-field v-model="page.values.obj.slr_ave" 
									label="Avg daily solar radiation (MJ/m2/day)" type="number" step="any"
									:error-messages="vm$.slr_ave.$errors.map(e => e.$message).join(', ')"
									@input="vm$.slr_ave.$touch" @blur="vm$.slr_ave.$touch"></v-text-field>
							</div>
						</v-col>
					</v-row>

					<v-row>
						<v-col cols="12" md="6">
							<div class="form-group mb-0">
								<v-text-field v-model="page.values.obj.dew_ave" 
									label="Avg daily dew point temperature (°C)" type="number" step="any"
									:error-messages="vm$.dew_ave.$errors.map(e => e.$message).join(', ')"
									@input="vm$.dew_ave.$touch" @blur="vm$.dew_ave.$touch"></v-text-field>
							</div>
						</v-col>
						<v-col cols="12" md="6">
							<div class="form-group mb-0">
								<v-text-field v-model="page.values.obj.wnd_ave" 
									label="Avg wind speed (m/s)" type="number" step="any"
									:error-messages="vm$.wnd_ave.$errors.map(e => e.$message).join(', ')"
									@input="vm$.wnd_ave.$touch" @blur="vm$.wnd_ave.$touch"></v-text-field>
							</div>
						</v-col>
					</v-row>
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