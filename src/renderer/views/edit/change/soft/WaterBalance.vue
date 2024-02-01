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
		enabled: 'n',
		params: [],
		balance: {
			surq_rto: 0,
			latq_rto: 0,
			perc_rto: 0,
			et_rto: 0,
			tileq_rto: 0,
			pet: 0,
			sed: 0,
			wyr: 0,
			bfr: 0,
			solp: 0
		},
		options: {
			enabled: [
				{ title: 'Do not calibrate hydrologic balance', value: 'n' },
				{ title: 'Calibrate all hydrologic balance processes for HRU by land use', value: 'a' },
				{ title: 'Calibrate baseflow and total runoff for HRU by land use', value: 'b' }
			],
			paramFields: [
				{ key: 'edit', title: '', class: 'min' },
				{ key: 'name', title: 'Name', sortable: true },
				{ key: 'chg_typ', title: 'Type of Change', sortable: true },
				{ key: 'neg', title: 'Negative Limit', sortable: true },
				{ key: 'pos', title: 'Positive Limit', sortable: true },
				{ key: 'lo', title: 'Lower Limit', sortable: true },
				{ key: 'up', title: 'Upper Limit', sortable: true },
			],
			chgTypes: [
				{ value: 'absval', title: 'Change the value of the parameter (absval)' },
				{ value: 'abschg', title: 'Change the value by the specified amount (abschg)' },
				{ value: 'pctchg', title: 'Change the value by the specified percent (pctchg)' }
			]
		},
		param: {
			item: {
				id: 0,
				name: '',
				chg_typ: '',
				neg: 0,
				pos: 0,
				lo: 0,
				up: 0
			},
			saving: false,
			error: null,
			show: false
		}
	});

	async function get() {
		data.page.loading = true;
		data.page.error = null;
		data.page.showError = false;

		try {
			const response = await api.get(`change/water_balance`, currentProject.getApiHeader());
			errors.log(response.data);
			data.enabled = response.data.enabled;
			data.balance = response.data.balance;
			data.params = response.data.params;
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
			let formData = {
				enabled: data.enabled,
				balance: data.balance,
			};

			await api.put(`change/water_balance`, formData, currentProject.getApiHeader());
		} catch (error) {
			data.page.error = errors.logError(error, 'Unable to save changes to database.');
		}

		data.page.saving = false;
		data.page.showError = data.page.error !== null;
	}

	function edit(item:any) {
		data.param.item = item;
		data.param.show = true;
		data.param.error = null;
	}

	async function saveParam() {
		data.param.error = null;
		data.param.saving = true;

		try {
			await api.put(`change/water_balance/parms/${data.param.item.id}`, data.param.item, currentProject.getApiHeader());
		} catch (error) {
			data.param.error = errors.logError(error, 'Unable to save changes to database.');
		}

		data.param.saving = false;
		data.param.show = false;
	}

	onMounted(async () => await get())
	watch(() => route.path, async () => await get())
</script>

<template>
	<project-container :loading="data.page.loading">
		<file-header input-file="water_balance.sft" docs-path="calibration" use-io>
			<router-link to="/edit/change/soft">Soft Calibration</router-link> 
			/ Water Balance
		</file-header>
		
		<v-form @submit.prevent="save">
			<error-alert as-popup v-model="data.page.showError" :show="data.page.showError" :text="data.page.error" :timeout="-1"></error-alert>
			<success-alert v-model="data.page.saveSuccess" :show="data.page.saveSuccess"></success-alert>

			<div class="form-group mb-0">
				<v-select label="Enable or disable water balance soft calibration" 
					v-model="data.enabled" :items="data.options.enabled"></v-select>
			</div>

			<div v-if="data.enabled !== 'n'">
				<p class="mb-4">
					Enter your water balance adjustments below and save your changes.
					When you run the model, it will generate new a hydrology_cal.hyd file with new parameters for your HRUs.
					You can compare this to the values in your original hydrology.hyd, then choose which to use.
					If you choose to use your new hydrology_cal.hyd file, you will rename this to hydrology.hyd, turn off water balance soft calibration, 
					and re-run the model with the new values.
				</p>

				<v-card>
					<v-tabs v-model="data.page.tab" bg-color="primary">
						<v-tab value="balance">Water Balance</v-tab>
						<v-tab value="params">Parameters</v-tab>
					</v-tabs>

					<v-card-text>
						<v-window v-model="data.page.tab">
							<v-window-item value="balance">
								<v-table class="table-editor" density="compact" v-if="!data.page.loading">
									<thead>
										<tr class="bg-surface">
											<th class="bg-secondary-tonal">Value</th>
											<th class="bg-secondary-tonal">Units</th>
											<th class="bg-secondary-tonal">Description</th>
											<th class="bg-secondary-tonal">SWAT+ Variable</th>
										</tr>
									</thead>
									<tbody>
										<tr v-if="data.enabled === 'a'">
											<td>
												<v-text-field v-model.number="data.balance.surq_rto" type="number" step="any" density="compact" hide-details="auto"></v-text-field>
											</td>
											<td>- or m<sup>3</sup></td>
											<td>Surface runoff ratio</td>
											<td><code>surq_rto</code></td>
										</tr>
										<tr v-if="data.enabled === 'a'">
											<td>
												<v-text-field v-model.number="data.balance.latq_rto" type="number" step="any" density="compact" hide-details="auto"></v-text-field>
											</td>
											<td>- or m<sup>3</sup></td>
											<td>Lateral flow ratio</td>
											<td><code>latq_rto</code></td>
										</tr>
										<tr v-if="data.enabled === 'a'">
											<td>
												<v-text-field v-model.number="data.balance.perc_rto" type="number" step="any" density="compact" hide-details="auto"></v-text-field>
											</td>
											<td>- or m<sup>3</sup></td>
											<td>Percolation ratio</td>
											<td><code>perc_rto</code></td>
										</tr>
										<tr v-if="data.enabled === 'a'">
											<td>
												<v-text-field v-model.number="data.balance.et_rto" type="number" step="any" density="compact" hide-details="auto"></v-text-field>
											</td>
											<td>- or m<sup>3</sup></td>
											<td>Evapotranspiration ratio</td>
											<td><code>et_rto</code></td>
										</tr>
										<tr v-if="data.enabled === 'a'">
											<td>
												<v-text-field v-model.number="data.balance.tileq_rto" type="number" step="any" density="compact" hide-details="auto"></v-text-field>
											</td>
											<td>- or m<sup>3</sup></td>
											<td>Tile flow ratio</td>
											<td><code>tileq_rto</code></td>
										</tr>
										<tr v-if="data.enabled === 'a'">
											<td>
												<v-text-field v-model.number="data.balance.pet" type="number" step="any" density="compact" hide-details="auto"></v-text-field>
											</td>
											<td>- or m<sup>3</sup></td>
											<td>Potential evapotranspiration</td>
											<td><code>pet</code></td>
										</tr>

										<tr v-if="data.enabled === 'b'">
											<td>
												<v-text-field v-model.number="data.balance.wyr" type="number" step="any" density="compact" hide-details="auto"></v-text-field>
											</td>
											<td>- or m<sup>3</sup></td>
											<td>Water yield ratio - total water yield/precipitation</td>
											<td><code>wyr</code></td>
										</tr>
										<tr v-if="data.enabled === 'b'">
											<td>
												<v-text-field v-model.number="data.balance.bfr" type="number" step="any" density="compact" hide-details="auto"></v-text-field>
											</td>
											<td>- or m<sup>3</sup></td>
											<td>Base flow ratio - base flow/precipitation - lat+prec+tile</td>
											<td><code>bfr</code></td>
										</tr>
									</tbody>
								</v-table>
							</v-window-item>

							<v-window-item value="params">
								<p>
									All parameters that can be used with max/min ranges and max/min absolute values. 
									The parameters are fixed in the code, however you can adjust the limits if needed.
								</p>
								<v-card>
									<v-data-table class="data-table" density="compact"
										:items="data.params" :items-per-page="-1"
										:headers="data.options.paramFields">
										<template v-slot:item.edit="{ item }">
											<a href="#" class="text-decoration-none text-primary" title="Edit" @click.prevent="edit(item)">
												<font-awesome-icon :icon="['fas', 'edit']"></font-awesome-icon>
											</a>
										</template>
										<template v-slot:bottom></template>
									</v-data-table>
								</v-card>
							</v-window-item>
						</v-window>
					</v-card-text>
				</v-card>
			</div>
			
			<action-bar>
				<v-btn type="submit" :loading="data.page.saving" variant="flat" color="primary" class="mr-2">
					Save Changes
				</v-btn>
				<back-button></back-button>
			</action-bar>
		</v-form>

		<v-dialog v-model="data.param.show" :max-width="constants.dialogSizes.lg">
			<v-card title="Update parameter">
				<v-card-text>
					<error-alert :text="data.param.error"></error-alert>
					
					<v-form>
						<div class="form-group">
							<v-select label="Type of change" v-model="data.param.item.chg_typ" :items="data.options.chgTypes"></v-select>
						</div>

						<v-row>
							<v-col cols="12" md="6">
								<v-text-field label="Negative limit of change" v-model.number="data.param.item.neg" type="number" step="any"></v-text-field>
							</v-col>
							<v-col cols="12" md="6">
								<v-text-field label="Positive limit of change" v-model.number="data.param.item.pos" type="number" step="any"></v-text-field>
							</v-col>
						</v-row>

						<v-row>
							<v-col cols="12" md="6">
								<v-text-field label="Lower limit of change" v-model.number="data.param.item.lo" type="number" step="any"></v-text-field>
							</v-col>
							<v-col cols="12" md="6">
								<v-text-field label="Upper limit of change" v-model.number="data.param.item.up" type="number" step="any"></v-text-field>
							</v-col>
						</v-row>
					</v-form>
				</v-card-text>
				<v-divider></v-divider>
				<v-card-actions>
					<v-btn @click="saveParam" :loading="data.param.saving" color="primary" variant="text">Save Changes</v-btn>
					<v-btn @click="data.param.show = false">Cancel</v-btn>
				</v-card-actions>
			</v-card>
		</v-dialog>
	</project-container>
</template>
