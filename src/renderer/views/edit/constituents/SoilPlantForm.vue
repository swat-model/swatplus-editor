<script setup lang="ts">
	import { reactive, onMounted, computed, watch } from 'vue';
	import { useRouter } from 'vue-router';
	import { useHelpers } from '@/helpers';

	const router = useRouter();
	const { api, constants, currentProject, errors, formatters, utilities } = useHelpers();

	interface Props {
		item: any,
		isUpdate?: boolean,
		allowBulkEdit?: boolean
	}

	const props = withDefaults(defineProps<Props>(), {
		item: { id: 0 },
		isUpdate: false,
		allowBulkEdit: false
	});

	let page:any = reactive({
		loading: true,
		error: null,
		validated: false,
		saving: false,
		saveSuccess: false,
		bulk: {
			show: false
		}
	});

	let selected:any = reactive({
		items: [],
		vars: []
	});

	function putDb(data:any) {
		if (page.bulk.show)
			return api.put('init/soil_plant/many', data, currentProject.getApiHeader());
		else if (props.isUpdate)
			return api.put(`init/soil_plant/${props.item.id}`, data, currentProject.getApiHeader());
		else
			return api.post(`init/soil_plant`, data, currentProject.getApiHeader());
	}

	async function save() {
		page.error = null;
		page.saving = true;
		page.saveSuccess = false;
		page.validated = true;
		let val_error = false;

		let item:any = {};
		if (!page.bulk.show) {
			item = props.item;
			item.name = formatters.toValidName(props.item.name);
		} else {
			if (selected.items.length < 1) {
				val_error = true;
				page.error = 'You must select at least one record to edit.';
			}
			else if (selected.vars.length < 1) {
				val_error = true;
				page.error = 'You must check at least one field to edit.';
			}
			else {
				item = {};
				item.selected_ids = selected.items;
			
				for (let v of selected.vars) {
					item[v] = props.item[v];
				}
			}
		}
		
		if (!val_error) {
			try {
				const response = await putDb(item);

				if (props.isUpdate)
					page.saveSuccess = true;
				else
					router.push({ name: 'ConstituentsSoilPlantEdit', params: { id: response.data.id }});
			} catch (error) {
				page.error = errors.logError(error, 'Unable to save changes to database.');
			}
		}
		
		page.saving = false;
		page.validated = false;
	}

	function bulkSelectionChange(selection:any) {
		selected.items = selection;
	}
</script>

<template>
	<div>
		<error-alert :text="page.error"></error-alert>
		<success-alert v-model="page.saveSuccess" :show="page.saveSuccess"></success-alert>

		<v-form @submit.prevent="save">
			<div v-if="!page.bulk.show">
                <div class="form-group">
					<v-text-field v-model="item.name" :rules="[constants.formRules.required, constants.formRules.nameLength]" 
						label="Name" hint="Must be unique"></v-text-field>
				</div>

				<div class="form-group">
					<v-text-field v-model="item.description" label="Description (optional)"></v-text-field>
				</div>
            </div>
            <div v-else>
                <object-selector name="Soil Plant" table="soil_plant_ini" @change="bulkSelectionChange"></object-selector>
            </div>

			<div class="form-group d-flex">
				<v-checkbox v-if="page.bulk.show" v-model="selected.vars" value="sw_frac" class="flex-shrink-1 flex-grow-0"></v-checkbox>
				<v-text-field v-model.number="item.sw_frac" label="Soil Water Fraction" type="number" step="any" class="flex-grow-1 flex-shrink-0"></v-text-field>
			</div>

			<div class="form-group d-flex">
				<v-checkbox v-if="page.bulk.show" v-model="selected.vars" value="nutrients_name" class="flex-shrink-1 flex-grow-0"></v-checkbox>
				<auto-complete label="Nutrients" class="flex-grow-1 flex-shrink-0"
					v-model="item.nutrients_name" :value="item.nutrients_name" :show-item-link="props.isUpdate"
					table-name="soil_nut" route-name="SoilNutrientsEdit"
					section="Soils / Nutrients" help-file="nutrients.sol" help-db="nutrients_sol"
					api-url="soils/nutrients"></auto-complete>
			</div>

			<v-alert type="info" variant="tonal" class="mb-4">
				For the fields below, you must enable and set up your data in the <b>Constituents</b> section.
			</v-alert>

			<v-row>
				<v-col cols="12" md="6">
					<div class="form-group d-flex">
						<v-checkbox v-if="page.bulk.show" v-model="selected.vars" value="pest_name" class="flex-shrink-1 flex-grow-0"></v-checkbox>
						<auto-complete label="Pesticide Properties" class="flex-grow-1 flex-shrink-0"
							v-model="item.pest_name" :value="item.pest_name" :show-item-link="props.isUpdate"
							table-name="pest_water_ini" route-name="ConstituentsPesticides" no-route-id
							section="Constituents / Pesticides" help-file="pest_water.ini" help-db="pest_water_ini"
							api-url="init/constituents/pest-water"></auto-complete>
					</div>
				</v-col>
				<v-col cols="12" md="6">
					<div class="form-group d-flex">
						<v-checkbox v-if="page.bulk.show" v-model="selected.vars" value="path_name" class="flex-shrink-1 flex-grow-0"></v-checkbox>
						<auto-complete label="Pathogen Properties" class="flex-grow-1 flex-shrink-0"
							v-model="item.path_name" :value="item.path_name" :show-item-link="props.isUpdate"
							table-name="path_water_ini" route-name="ConstituentsPathogens" no-route-id
							section="Constituents / Pathogens" help-file="path_water.ini" help-db="path_water_ini"
							api-url="init/constituents/path-water"></auto-complete>
					</div>
				</v-col>
			</v-row>

			<v-row>
				<v-col v-if="false" cols="12" md="6">
					<!--Not currently active!-->
					<div class="form-group d-flex">
						<v-checkbox v-if="page.bulk.show" v-model="selected.vars" value="hmet_name" class="flex-shrink-1 flex-grow-0"></v-checkbox>
						<auto-complete label="Heavy Metal Properties" class="flex-grow-1 flex-shrink-0"
							v-model="item.hmet_name" :value="item.hmet_name" :show-item-link="props.isUpdate"
							table-name="hmet_water_ini" route-name="InitHmetWaterEdit"
							section="Constituents / Heavy Metals" help-file="hmet_water.ini" help-db="hmet_water_ini"
							api-url="init/constituents/hmet-water"></auto-complete>
					</div>
				</v-col>
				<v-col cols="12" md="6">
					<div class="form-group d-flex">
						<v-checkbox v-if="page.bulk.show" v-model="selected.vars" value="salt_name" class="flex-shrink-1 flex-grow-0"></v-checkbox>
						<auto-complete label="Salt Properties" class="flex-grow-1 flex-shrink-0"
							v-model="item.salt_name" :value="item.salt_name" :show-item-link="props.isUpdate"
							table-name="salt_hru_ini" route-name="ConstituentsSaltsHruIni"
							section="Constituents / Salts / HRU Initialization" help-file="salt_hru.ini" helpdb="salt_hru_ini"
							api-url="salts/salt_hru_ini"></auto-complete>
					</div>
				</v-col>
			</v-row>

			<action-bar>
				<v-btn type="submit" :loading="page.saving" variant="flat" color="primary" class="mr-2">
					{{ page.bulk.show ? 'Save Bulk Changes' : 'Save Changes' }}
				</v-btn>
				<back-button></back-button>
				<div class="ml-auto">
					<v-checkbox v-model="page.bulk.show" hide-details label="Edit multiple rows"></v-checkbox>
				</div>
			</action-bar>
		</v-form>
	</div>
</template>