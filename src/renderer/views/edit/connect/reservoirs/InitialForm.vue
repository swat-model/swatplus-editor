<script setup lang="ts">
	import { reactive, onMounted, computed, watch } from 'vue';
	import { useRouter } from 'vue-router';
	import { usePlugins } from '../../../../plugins';

	const router = useRouter();
	const { api, constants, currentProject, errors, formatters, utilities } = usePlugins();

	interface Props {
		item: any,
		isUpdate?: boolean
	}

	const props = withDefaults(defineProps<Props>(), {
		apiUrl: '',
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
			return api.put('reservoirs/initial/many/', data, currentProject.getApiHeader());
		else if (props.isUpdate)
			return api.put(`reservoirs/initial/${props.item.id}`, data, currentProject.getApiHeader());
		else
			return api.post(`reservoirs/initial`, data, currentProject.getApiHeader());
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
					router.push({ name: 'ReservoirsInitial'});
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
                <object-selector name="Reservoirs" table="init_res" @change="bulkSelectionChange"></object-selector>
            </div>

			<div class="form-group d-flex">
				<v-checkbox v-if="page.bulk.show" v-model="selected.vars" value="org_min_name" class="flex-shrink-1 flex-grow-0"></v-checkbox>
				<auto-complete label="Organic Mineral Properties" class="flex-grow-1 flex-shrink-0"
					v-model="item.org_min_name" :value="item.org_min_name" :show-item-link="props.isUpdate"
					table-name="om_water_ini" route-name="InitOMWaterEdit"
					section="Initialization Data / Organic Mineral" help-file="om_water.ini" help-db="om_water_ini"
					api-url="init/om_water"></auto-complete>
			</div>

			<v-alert type="info" variant="tonal" class="mb-4">
				For the fields below, you must enable and set up your data in the 
				<router-link to="/edit/init/constituents" class="text-primary">Initialization / Constituents</router-link> section.
			</v-alert>

			<v-row>
				<v-col cols="12" md="6">
					<div class="form-group d-flex">
						<v-checkbox v-if="page.bulk.show" v-model="selected.vars" value="pest_name" class="flex-shrink-1 flex-grow-0"></v-checkbox>
						<auto-complete label="Pesticide Properties" class="flex-grow-1 flex-shrink-0"
							v-model="item.pest_name" :value="item.pest_name" :show-item-link="props.isUpdate"
							table-name="pest_water_ini" route-name="InitPestWaterEdit"
							section="Initialization Data / Pesticides Water" help-file="pest_water.ini" help-db="pest_water_ini"
							api-url="init/constituents/pest-water"></auto-complete>
					</div>
				</v-col>
				<v-col cols="12" md="6">
					<div class="form-group d-flex">
						<v-checkbox v-if="page.bulk.show" v-model="selected.vars" value="path_name" class="flex-shrink-1 flex-grow-0"></v-checkbox>
						<auto-complete label="Pathogen Properties" class="flex-grow-1 flex-shrink-0"
							v-model="item.path_name" :value="item.path_name" :show-item-link="props.isUpdate"
							table-name="path_water_ini" route-name="InitPathWaterEdit"
							section="Initialization Data / Pathogens Water" help-file="path_water.ini" help-db="path_water_ini"
							api-url="init/constituents/path-water"></auto-complete>
					</div>
				</v-col>
			</v-row>

			<!--Not currently active!-->
			<v-row v-if="false">
				<v-col cols="12" md="6">
					<div class="form-group d-flex">
						<v-checkbox v-if="page.bulk.show" v-model="selected.vars" value="hmet_name" class="flex-shrink-1 flex-grow-0"></v-checkbox>
						<auto-complete label="Heavy Metal Properties" class="flex-grow-1 flex-shrink-0"
							v-model="item.hmet_name" :value="item.hmet_name" :show-item-link="props.isUpdate"
							table-name="hmet_water_ini" route-name="InitHmetWaterEdit"
							section="Initialization Data / Heavy Metals Water" help-file="hmet_water.ini" help-db="hmet_water_ini"
							api-url="init/constituents/hmet-water"></auto-complete>
					</div>
				</v-col>
				<v-col cols="12" md="6">
					<div class="form-group d-flex">
						<v-checkbox v-if="page.bulk.show" v-model="selected.vars" value="salt_name" class="flex-shrink-1 flex-grow-0"></v-checkbox>
						<auto-complete label="Pathogen Properties" class="flex-grow-1 flex-shrink-0"
							v-model="item.salt_name" :value="item.salt_name" :show-item-link="props.isUpdate"
							table-name="salt_water_ini" route-name="InitSaltWaterEdit"
							section="Initialization Data / Salt Water" help-file="salt_water.ini" helpdb="salt_water_ini"
							api-url="init/constituents/salt-water"></auto-complete>
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