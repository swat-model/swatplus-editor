<script setup lang="ts">
	import { reactive, onMounted, watch } from 'vue';
	import { useHelpers } from '@/helpers';
	const { api, constants, currentProject, errors, formatters, utilities } = useHelpers();

	interface Props {
		apiUrl: string,
		item: any,
		outflowConIdField: string,
		isUpdate?: boolean,
		isBulkMode?: boolean,
		itemOutflow: object[]
	}

	const props = withDefaults(defineProps<Props>(), {
		apiUrl: '',
		item: { id: 0 },
		outflowConIdField: '',
		isUpdate: false,
		isBulkMode: false,
		itemOutflow: () => [{id: 0}]
	});

	const emit = defineEmits(['change', 'loaded']);

	let page:any = reactive({
		loading: false,
		error: null
	});

	let selected:any = reactive({
		vars: []
	});

	let outflow:any = reactive({
		loading: false,
		error: null,
		fields: [
			{ key: 'edit', label: '', class: 'min' },
			{ key: 'order' },
			{ key: 'obj_typ', label: 'Type' },
			{ key: 'obj_name', label: 'Name' },
			{ key: 'hyd_typ', label: 'Hyd.' },
			{ key: 'frac', label: 'Frac.' },
			{ key: 'delete', label: '', class: 'min' }
		],
		delete: {
			show: false,
			id: null,
			name: null,
			error: null,
			saving: false
		},
		form: {
			show: false,
			id: null,
			validated: false,
			error: null,
			saving: false
		},
		obj: {
			order: null,
			obj_typ: 'sdc',
			obj_id: null,
			hyd_typ: null,
			frac: null
		},
		obj_name: null,
		obj_typs: [],
		hyd_typs: [],
		list: props.itemOutflow
	});

	function getCodesDb(type:string) {
		return api.get(`definitions/codes/connect/${type}/${utilities.appPathUrl}`);
	}

	async function get() {
		page.loading = true;
		page.error = null;

		try {
			const response = await getCodesDb('obj_typ');
			outflow.obj_typs = response.data;

			const response2 = await getCodesDb('hyd_typ');
			outflow.hyd_typs = response2.data;
		} catch (error) {
			page.error = errors.logError(error, 'Unable to get outflow codes from database.');
		}
		
		page.loading = false;
		emit('loaded', true);
	}

	function add() {
		outflow.form.update = false;
		outflow.form.id = null;
		outflow.obj = {
			order: outflow.list.length + 1,
			obj_typ: 'sdc',
			obj_id: undefined,
			hyd_typ: undefined,
			frac: undefined
		};
		outflow.obj[props.outflowConIdField] = props.item.id;
		outflow.obj_name = undefined;
		outflow.form.show = true;
	}

	function edit(item:any) {
		outflow.form.update = true;
		outflow.form.id = item.id;
		outflow.obj = {
			order: item.order,
			obj_typ: item.obj_typ,
			obj_id: item.obj_id,
			hyd_typ: item.hyd_typ,
			frac: item.frac
		};
		outflow.obj[props.outflowConIdField] = props.item.id;
		outflow.obj_name = item.obj_name;
		outflow.form.show = true;
	}

	async function saveOutflow() {
		outflow.form.error = null;
		outflow.form.saving = true;
		outflow.form.validated = true;

		errors.log(outflow.obj);
		errors.log(outflow.obj_name);
		if (validateOutflow()) {
			errors.log('validated')
			try {
				const response = await utilities.getAutoCompleteId(constants.objTypeToConTable[outflow.obj.obj_typ], outflow.obj_name);
				outflow.obj.obj_id = response.data.id;
			} catch (error) {
				outflow.form.error = errors.logError(error, `Invalid object name, ${outflow.obj_name}. Please make sure the ${outflow.obj.obj_typ} exists in your database.`);
			}

			if (formatters.isNullOrEmpty(outflow.form.error)) {
				var action;
				if (outflow.form.update) {
					action = api.put(`${props.apiUrl}/out/${outflow.form.id}`, outflow.obj, currentProject.getApiHeader());
				} else {
					action = api.post(`${props.apiUrl}/out`, outflow.obj, currentProject.getApiHeader());
				}

				try {
					const response = await action;
					outflow.form.validated = false;
					outflow.form.show = false;
					await getOutflow();
				} catch (error) {
					outflow.form.error = errors.logError(error, 'Unable to save outflow to database.');
				}
			}
		} 
		
		outflow.form.saving = false;
	}

	function validateOutflow () {
		let valid = true;
		valid = valid && !formatters.isNullOrEmpty(outflow.obj.order);
		valid = valid && !formatters.isNullOrEmpty(outflow.obj.obj_typ);
		valid = valid && !formatters.isNullOrEmpty(outflow.obj_name);
		valid = valid && !formatters.isNullOrEmpty(outflow.obj.hyd_typ);
		valid = valid && !formatters.isNullOrEmpty(outflow.obj.frac);
		return valid;
	}

	function askDelete(id:any, name:any) {
		outflow.delete.id = id;
		outflow.delete.name = name;
		outflow.delete.show = true;
	}

	async function confirmDelete() {
		outflow.delete.error = undefined;
		outflow.delete.saving = true;

		try {
			const response = await api.delete(`${props.apiUrl}/out/${outflow.delete.id}`, currentProject.getApiHeader());
			outflow.delete.saving = false;
			outflow.delete.show = false;
			await getOutflow();
		} catch (error) {
			outflow.delete.error = errors.logError(error, 'Unable to delete from database.');
			outflow.delete.saving = false;
		}
	}

	async function getOutflow() {
		outflow.loading = true;
		outflow.error = null;

		try {
			const response = await api.get(`${props.apiUrl}/items/${props.item.id}`, currentProject.getApiHeader());
			outflow.list = response.data.con_outs;
		} catch (error) {
			outflow.error = errors.logError(error, 'Unable to get object from database.');
		}
			
		outflow.loading = false;
	}

	watch(() => selected.vars, async () => {
		emit('change', selected.vars);
	})

	onMounted(async () => await get());
</script>

<template>
	<div>{{ page.error }}</div>
	<project-container :loading="page.loading" :load-error="page.error">
		<v-row>
			<v-col cols="12" :md="props.isUpdate && !props.isBulkMode ? 7 : 12">
				<div class="form-group" v-if="!props.isBulkMode">
					<v-text-field v-model="item.name" :rules="[constants.formRules.required, constants.formRules.nameLength]" 
						label="Name" hint="Must be unique"></v-text-field>
				</div>

				<div class="form-group d-flex">
					<v-checkbox v-if="props.isBulkMode" v-model="selected.vars" value="wst_name" class="flex-shrink-1 flex-grow-0"></v-checkbox>
					<auto-complete label="Weather Station" class="flex-grow-1 flex-shrink-0"
						v-model="item.wst_name" :value="item.wst_name" :show-item-link="props.isUpdate"
						table-name="wst" route-name="StationsEdit"
						section="Climate / Weather Stations" help-file="weather-sta.cli" help-db="weather_sta_cli"
						api-url="climate/stations"></auto-complete>
				</div>

				<v-row v-if="!props.isBulkMode">
					<v-col cols="12" md="6">
						<div class="form-group mb-0">
							<v-text-field v-model="item.lat" :rules="[constants.formRules.required]" 
								label="Latitude" type="number" step="any"></v-text-field>
						</div>
					</v-col>
					<v-col cols="12" md="6">
						<div class="form-group mb-0">
							<v-text-field v-model="item.lon" :rules="[constants.formRules.required]" 
								label="Longitude" type="number" step="any"></v-text-field>
						</div>
					</v-col>
				</v-row>

				<v-row class="mt-0">
					<v-col cols="12" md="6" v-if="!props.isBulkMode">
						<div class="form-group">
							<v-text-field v-model="item.area" :rules="[constants.formRules.required]" 
								label="Area" suffix="ha" type="number" step="any"></v-text-field>
						</div>
					</v-col>
					<v-col cols="12" :md="!props.isBulkMode ? 6 : 12">
						<div class="form-group d-flex">
							<v-checkbox v-if="props.isBulkMode" v-model="selected.vars" value="elev" class="flex-shrink-1 flex-grow-0"></v-checkbox>
							<v-text-field v-model="item.elev" class="flex-grow-1 flex-shrink-0" 
								label="Elevation" suffix="m" type="number" step="any"></v-text-field>
						</div>
					</v-col>
				</v-row>
			</v-col>
			<v-col cols="12" v-if="props.isUpdate && !props.isBulkMode" :md="props.isUpdate && !props.isBulkMode ? 5 : 12">
				<v-card>
					<v-card-title>Outflow</v-card-title>
					<v-card-text v-if="outflow.list.length < 1">
						This object does not have any outflow
					</v-card-text>
					<v-card-text v-else>
						<v-table class="data-table" density="compact">
							<thead>
								<tr class="bg-surface">
									<th v-for="header in outflow.fields" :key="header.key" :class="`${header.class} bg-secondary-tonal`">
										{{ header.label }}
									</th>
								</tr>
							</thead>
							<tbody>
								<tr v-for="(item, i) in outflow.list" :key="i">
									<td v-for="header in outflow.fields" :key="header.key" :class="header.class">
										<div v-if="header.key==='edit'">
											<font-awesome-icon :icon="['fas', 'edit']" class="pointer text-primary" @click="edit(item)"></font-awesome-icon>
										</div>
										<div v-else-if="header.key==='delete'">
											<font-awesome-icon :icon="['fas', 'times']" class="pointer text-error" @click="askDelete(item.id, 'outflow')"></font-awesome-icon>
										</div>
										<div v-else-if="header.key==='obj_name'">
											<div v-if="item.obj_name != null">
												<router-link v-if="utilities.getObjTypeRoute(item) != '#'" 
													class="text-primary text-decoration-none"
													:to="utilities.getObjTypeRoute(item)">{{ item.obj_name }}</router-link>
												<div v-else>{{ item.obj_name }}</div>
											</div>
										</div>
										<div v-else>{{ item[header.key] }}</div>
									</td>
								</tr>
							</tbody>
						</v-table>
					</v-card-text>

					<v-card-actions>
						<v-btn @click="add" color="primary">Add Outflow</v-btn>
					</v-card-actions>
				</v-card>
			</v-col>
		</v-row>

		<v-dialog v-model="outflow.form.show" :max-width="constants.dialogSizes.lg">
			<v-card :title="outflow.form.update ? 'Update outflow' : 'Add outflow'">
				<v-card-text>
					<error-alert :text="outflow.form.error"></error-alert>

					<v-row>
						<v-col cols="12" md="6">
							<div class="form-group">
								<v-select label="Object type" v-model="outflow.obj.obj_typ" :items="outflow.obj_typs" item-title="text" item-value="value" required @change="outflow.obj_name = null"></v-select>
							</div>
						</v-col>
						<v-col cols="12" md="6">
							<div class="form-group">
								<auto-complete label="Object name" class="flex-grow-1 flex-shrink-0"
									v-model="outflow.obj_name" :value="outflow.obj_name" :show-item-link="false"
									:table-name="constants.objTypeToConTable[outflow.obj.obj_typ]" :route-name="constants.objTypeRouteTable[outflow.obj.obj_typ].name"></auto-complete>
							</div>
						</v-col>
					</v-row>
					<v-row>
						<v-col cols="12" md="6">
							<div class="form-group">
								<v-select label="Hydrograph type" v-model="outflow.obj.hyd_typ" :items="outflow.hyd_typs" item-title="text" item-value="value" required></v-select>
							</div>
						</v-col>
						<v-col cols="12" md="6">
							<div class="form-group">
								<v-text-field v-model="outflow.obj.frac" :rules="[constants.formRules.required]" label="Fraction" type="number" step="any"></v-text-field>
							</div>
						</v-col>
					</v-row>
					<v-row>
						<v-col cols="12" md="6">
							<div class="form-group">
								<v-text-field v-model="outflow.obj.order" :rules="[constants.formRules.required]" label="Order" type="number" step="1"></v-text-field>
							</div>
						</v-col>
					</v-row>
				</v-card-text>
				<v-divider></v-divider>
				<v-card-actions>
					<v-btn @click="saveOutflow" :loading="outflow.form.saving" color="primary" variant="text">Save</v-btn>
					<v-btn @click="outflow.form.show = false">Cancel</v-btn>
				</v-card-actions>
			</v-card>
		</v-dialog>

		<v-dialog v-model="outflow.delete.show" :max-width="constants.dialogSizes.md">
			<v-card title="Confirm delete">
				<v-card-text>
					<error-alert :text="outflow.delete.error"></error-alert>
		
					<p>
						Are you sure you want to delete <strong>{{outflow.delete.name}}</strong>?
						This action is permanent and cannot be undone. 
					</p>
				</v-card-text>
				<v-divider></v-divider>
				<v-card-actions>
					<v-btn :loading="outflow.delete.saving" @click="confirmDelete" color="error" variant="text">Delete</v-btn>
					<v-btn @click="outflow.delete.show = false">Cancel</v-btn>
				</v-card-actions>
			</v-card>
		</v-dialog>
	</project-container>
</template>