<script setup lang="ts">
	import { reactive } from 'vue';
	import { useRouter } from 'vue-router';
	import { usePlugins } from '../../../../plugins';
	import ConnectForm from '../../../../components/ConnectForm.vue';
	const router = useRouter();
	const { api, constants, currentProject, errors, formatters, utilities } = usePlugins();

	interface Props {
		apiUrl: string,
		item: any,
		isUpdate?: boolean,
		allowBulkEdit?: boolean
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
		},
		redirectRoute: 'HrusEdit',
		propCol: 'hru',
		propFields: [
			'topo_name', 'hyd_name', 'soil_name', 'lu_mgt_name', 'soil_plant_init_name', 'surf_stor', 'snow_name', 'field_name'
		],
		propDefs: [
			{ name: 'topo_name', label: 'Topography Properties', section: 'Hydrology / Topography', file: 'topography.hyd', db: 'topography_hyd', tableName: 'topo', routeName: 'TopographyEdit', apiUrl: 'hydrology/topography'},
			{ name: 'hyd_name', label: 'Hydrology Properties', section: 'Hydrology', file: 'hydrology.hyd', db: 'hydrology_hyd', tableName: 'hyd', routeName: 'HydrologyEdit', apiUrl: 'hydrology/hydrology'},
			{ name: 'soil_name', label: 'Soil Properties', section: 'Soils', file: 'soils.sol', db: 'soils_sol', tableName: 'soil', routeName: 'SoilsEdit', apiUrl: 'soils/soils'},
			{ name: 'lu_mgt_name', label: 'Land Use Management Properties', section: 'Land Use Management', file: 'landuse.lum', db: 'landuse_lum', tableName: 'lu_mgt', routeName: 'LanduseEdit', apiUrl: 'lum/landuse'},
			{ name: 'soil_plant_init_name', label: 'Soil Plant Properties', section: 'Initialization Data / Soil Plant', file: 'soil_plant.ini', db: 'soil_plant_ini', tableName: 'soil_plant_ini', routeName: 'InitSoilPlantEdit', apiUrl: 'init/soil_plant'},
			{ name: 'surf_stor', label: 'Surface Storage Properties', section: 'Connections / Reservoirs / Wetlands', file: 'wetlands.wet', db: 'wetlands_wet', tableName: 'wet_res', routeName: 'ReservoirsWetlandsEdit', apiUrl: 'reservoirs/wetlands'},
			{ name: 'snow_name', label: 'Snow Properties', section: 'Databases / Snow', file: 'snow.sno', db: 'snow_sno', tableName: 'snow', routeName: 'SnowEdit', apiUrl: 'db/snow'},
			{ name: 'field_name', label: 'Field Properties', section: 'Hydrology / Fields', file: 'field.fld', db: 'field_fld', tableName: 'fld', routeName: 'FieldsEdit', apiUrl: 'hydrology/fields'}
		]
	});

	let selected:any = reactive({
		items: [],
		vars: [],
		connectVars: []
	});

	function putConnectDb(data:any) {
		if (props.isUpdate)
			return api.put(`${props.apiUrl}/items/${props.item.connect.id}`, data, currentProject.getApiHeader());
		else
			return api.post(`${props.apiUrl}/items`, data, currentProject.getApiHeader());
	}

	function putPropsDb(data:any) {
		if (props.isUpdate)
			return api.put(`${props.apiUrl}/properties/${props.item.props.id}`, data, currentProject.getApiHeader());
		else
			return api.post(`${props.apiUrl}/properties`, data, currentProject.getApiHeader());
	}

	async function save() {
		page.error = null;
		page.saving = true;
		page.saveSuccess = false;
		page.validated = true;

		if (props.item.connect.elev === '') props.item.connect.elev = null;
		if (props.item.connect.wst_name === '') props.item.connect.wst_name = null;
		for (let field of page.propFields) {
			if (props.item.props[field] === '') props.item.props[field] = null;
		}

		if (!page.bulk.show) {
			let name = formatters.toValidName(props.item.connect.name);
			props.item.props.name = name;
			props.item.connect.name = name;

			if (props.isUpdate)
				props.item.connect[`${page.propCol}_id`] = props.item.props.id;

			try {
				const response = await putPropsDb(props.item.props);
				if (!props.isUpdate)
					props.item.connect[`${page.propCol}_id`] = response.data.id;
					
				const response2 = await putConnectDb(props.item.connect);
				page.validated = false;
				
				if (props.isUpdate)
				page.saveSuccess = true;
				else
					router.push({ name: page.redirectRoute, params: { id: response2.data.id } });
			} catch (error) {
				page.error = errors.logError(error, 'Unable to save changes to database.');
			}
		} else {
			let selectedVars = selected.connectVars.concat(selected.vars);
			if (selected.items.length < 1) {
				page.error = 'You must select at least one record to edit.';
			}
			else if (selectedVars.length < 1) {
				page.error = 'You must check at least one field to edit.';
			}
			else {
				let item:any = {};
				item.selected_ids = selected.items;
			
				for (let v of selected.connectVars) {
					item[v] = props.item.connect[v];
				}

				console.log(props.item);
				for (let v of selected.vars) {
					item[v] = props.item.props[v];
				}
				
				try {
					const response = await api.put(`${props.apiUrl}/properties/many`, item, currentProject.getApiHeader());
					page.validated = false;
					page.saveSuccess = true;
				} catch (error) {
					page.error = errors.logError(error, 'Unable to save changes to database.');
				}
			}
		}
		
		page.saving = false;
	}

	function bulkSelectionChange(selection:any) {
		selected.items = selection;
	}

	function connectVarsChange(selection:any) {
		selected.connectVars = selection;
	}
</script>

<template>
	<div>
		<error-alert :text="page.error"></error-alert>
		<success-alert v-model="page.saveSuccess" :show="page.saveSuccess"></success-alert>

		<v-form @submit.prevent="save">
			<div v-if="page.bulk.show">
				<object-selector name="HRUs" table="hru_con" @change="bulkSelectionChange" is-hru></object-selector>
			</div>
			
			<connect-form
				:item="item.connect" :item-outflow="item.outflow" :api-url="props.apiUrl" outflow-con-id-field="hru_con_id"
				:is-update="props.isUpdate" @change="connectVarsChange" @loaded="page.loading=false"
				:is-bulk-mode="page.bulk.show"></connect-form>

			<div v-if="!page.loading">
				<v-divider class="mb-6"></v-divider>

				<v-row>
					<v-col cols="12" md="6" v-for="p in page.propDefs" :key="p.name">
						<div class="form-group d-flex">
							<v-checkbox v-if="page.bulk.show" v-model="selected.vars" :value="p.name" class="flex-shrink-1 flex-grow-0"></v-checkbox>
							<auto-complete :label="p.label" class="flex-grow-1 flex-shrink-0"
								v-model="item.props[p.name]" :value="item.props[p.name]" :show-item-link="props.isUpdate"
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
					<div v-if="props.allowBulkEdit" class="ml-auto">
						<v-checkbox v-model="page.bulk.show" hide-details label="Edit multiple rows"></v-checkbox>
					</div>
				</action-bar>
			</div>
		</v-form>
	</div>
</template>