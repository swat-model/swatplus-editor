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
		item: { id: 0 },
		isUpdate: false
	});

	let page:any = reactive({
		loading: true,
		error: null,
		validated: false,
		saving: false,
		saveSuccess: false,
		bulk: {
			show: false
		},
		propDefs: [
			{ name: 'init_name', label: 'Initial Properties', section: 'Reservoirs / Initial', file: 'initial.res', db: 'initial_res', tableName: 'init_res', routeName: 'ReservoirsInitialEdit', apiUrl: 'reservoirs/initial'},
			{ name: 'hyd_name', label: 'Wetland Hydrology Properties', section: 'Reservoirs / Wetland Hydrology', file: 'hydrology.wet', db: 'hydrology_wet', tableName: 'hyd_wet', routeName: 'ReservoirsWetlandsHydrologyEdit', apiUrl: 'reservoirs/wetlands-hydrology'},
			{ name: 'sed_name', label: 'Sediment Properties', section: 'Reservoirs / Sediment', file: 'sediment.res', db: 'sediment_res', tableName: 'sed_res', routeName: 'ReservoirsSedimentEdit', apiUrl: 'reservoirs/sediment'},
			{ name: 'nut_name', label: 'Nutrients Properties', section: 'Reservoirs / Nutrients', file: 'nutrients.res', db: 'nutrients_res', tableName: 'nut_res', routeName: 'ReservoirsNutrientsEdit', apiUrl: 'reservoirs/nutrients'},
			{ name: 'rel_name', label: 'Release Decision Table', section: 'Decision Tables / Reservoir Release', file: 'res_rel.dtl', db: 'd_table_dtl', tableName: 'res_rel.dtl', routeName: 'DecisionsEdit'}
		]
	});

	let selected:any = reactive({
		items: [],
		vars: []
	});

	function putDb(data:any) {
		if (page.bulk.show)
			return api.put('reservoirs/wetlands/many/', data, currentProject.getApiHeader());
		else if (props.isUpdate)
			return api.put(`reservoirs/wetlands/${props.item.id}`, data, currentProject.getApiHeader());
		else
			return api.post(`reservoirs/wetlands`, data, currentProject.getApiHeader());
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
					router.push({ name: 'ReservoirsWetlands'});
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
                <object-selector name="Wetlands" table="wet_res" is-hru @change="bulkSelectionChange"></object-selector>
            </div>

			<v-row>
				<v-col cols="12" md="6" v-for="p in page.propDefs" :key="p.name">
					<div class="form-group d-flex">
						<v-checkbox v-if="page.bulk.show" v-model="selected.vars" :value="p.name" class="flex-shrink-1 flex-grow-0"></v-checkbox>
						<auto-complete :label="p.label" class="flex-grow-1 flex-shrink-0"
							v-model="item[p.name]" :value="item[p.name]" :show-item-link="props.isUpdate"
							:table-name="p.tableName" :route-name="p.routeName"
							:section="p.section" :help-file="p.file" :help-db="p.db"
							:api-url="p.apiUrl"></auto-complete>
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