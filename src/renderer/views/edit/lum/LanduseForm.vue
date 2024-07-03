<script setup lang="ts">
	import { reactive, onMounted, computed, watch } from 'vue';
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

	let page:any = reactive({
		loading: true,
		error: null,
		validated: false,
		saving: false,
		saveSuccess: false,
		bulk: {
			show: false
		},
		urb_ro_options: [
			{ value: null, title: 'not applicable' },
			{ value: 'buildup_washoff', title: 'buildup_washoff' },
			{ value: 'usgs_reg', title: 'usgs_reg' }
		]
	});

	let selected:any = reactive({
		items: [],
		vars: []
	});

	function putDb(data:any) {
		if (page.bulk.show)
			return api.put('lum/landuse-many', data, currentProject.getApiHeader());
		else if (props.isUpdate)
			return api.put(`lum/landuse/${props.item.id}`, data, currentProject.getApiHeader());
		else
			return api.post(`lum/landuse`, data, currentProject.getApiHeader());
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
					router.push({ name: 'Landuse'});
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
                <object-selector name="Land Use Management" table="lu_mgt" no-gis @change="bulkSelectionChange"></object-selector>
            </div>

			<v-row>
				<v-col cols="12" md="6">
					<div class="form-group d-flex">
						<v-checkbox v-if="page.bulk.show" v-model="selected.vars" value="cal_group" class="flex-shrink-1 flex-grow-0"></v-checkbox>
						<v-text-field v-model="item.cal_group" label="Calibration Group" class="flex-grow-1 flex-shrink-0"></v-text-field>
					</div>
				</v-col>
				<v-col cols="12" md="6">
					<div class="form-group d-flex">
						<v-checkbox v-if="page.bulk.show" v-model="selected.vars" value="plnt_com_name" class="flex-shrink-1 flex-grow-0"></v-checkbox>
						<auto-complete label="Plant Community" class="flex-grow-1 flex-shrink-0"
							v-model="item.plnt_com_name" :value="item.plnt_com_name" :show-item-link="props.isUpdate"
							table-name="plant_ini" route-name="PlantCommEdit"
							section="Land Use Management / Plant Communities" help-file="plant.ini" help-db="plant_ini"
							api-url="init/plant_ini"></auto-complete>
					</div>
				</v-col>
			</v-row>

			<v-row>
				<v-col cols="12" md="6">
					<div class="form-group d-flex">
						<v-checkbox v-if="page.bulk.show" v-model="selected.vars" value="mgt_name" class="flex-shrink-1 flex-grow-0"></v-checkbox>
						<auto-complete label="Management Schedule" class="flex-grow-1 flex-shrink-0"
							v-model="item.mgt_name" :value="item.mgt_name" :show-item-link="props.isUpdate"
							table-name="mgt_sch" route-name="ManagementEdit"
							section="Land Use Management / Management Schedules" help-file="management.sch" help-db="management_sch"
							api-url="lum/mgt_sch"></auto-complete>
					</div>
				</v-col>
				<v-col cols="12" md="6">
					<div class="form-group d-flex">
						<v-checkbox v-if="page.bulk.show" v-model="selected.vars" value="cn2_name" class="flex-shrink-1 flex-grow-0"></v-checkbox>
						<auto-complete label="Curve Number" class="flex-grow-1 flex-shrink-0"
							v-model="item.cn2_name" :value="item.cn2_name" :show-item-link="props.isUpdate"
							table-name="cntable" route-name="CntableEdit"
							section="Land Use Management / Curve Numbers" help-file="cntable.lum" help-db="cntable_lum"
							api-url="lum/cntable"></auto-complete>
					</div>
				</v-col>
			</v-row>

			<v-row>
				<v-col cols="12" md="6">
					<div class="form-group d-flex">
						<v-checkbox v-if="page.bulk.show" v-model="selected.vars" value="urban_name" class="flex-shrink-1 flex-grow-0"></v-checkbox>
						<auto-complete label="Urban Land Use" class="flex-grow-1 flex-shrink-0"
							v-model="item.urban_name" :value="item.urban_name" :show-item-link="props.isUpdate"
							table-name="urban" route-name="UrbanEdit"
							section="Databases / Urban" help-file="urban.urb" help-db="urban_urb"
							api-url="db/urban"></auto-complete>
					</div>
				</v-col>
				<v-col cols="12" md="6">
					<div class="form-group d-flex">
						<v-checkbox v-if="page.bulk.show" v-model="selected.vars" value="urb_ro" class="flex-shrink-1 flex-grow-0"></v-checkbox>
						<v-select label="Urban Runoff" v-model="item.urb_ro" :items="page.urb_ro_options" class="flex-grow-1 flex-shrink-0"></v-select>
					</div>
				</v-col>
			</v-row>

			<v-row>
				<v-col cols="12" md="6">
					<div class="form-group d-flex">
						<v-checkbox v-if="page.bulk.show" v-model="selected.vars" value="cons_prac_name" class="flex-shrink-1 flex-grow-0"></v-checkbox>
						<auto-complete label="Conservation Practices" class="flex-grow-1 flex-shrink-0"
							v-model="item.cons_prac_name" :value="item.cons_prac_name" :show-item-link="props.isUpdate"
							table-name="cons_prac" route-name="ConsPracticeEdit"
							section="Land Use Management / Conservation Practices" help-file="cons_prac.lum" help-db="cons_prac_lum"
							api-url="lum/cons_prac"></auto-complete>
					</div>
				</v-col>
				<v-col cols="12" md="6">
					<div class="form-group d-flex">
						<v-checkbox v-if="page.bulk.show" v-model="selected.vars" value="ov_mann_name" class="flex-shrink-1 flex-grow-0"></v-checkbox>
						<auto-complete label="Overland Flow Manning's n" class="flex-grow-1 flex-shrink-0"
							v-model="item.ov_mann_name" :value="item.ov_mann_name" :show-item-link="props.isUpdate"
							table-name="ovntable" route-name="OvntableEdit"
							section="Land Use Management / Overland Flow Manning's n" help-file="ovn_table.lum" help-db="ovn_table_lum"
							api-url="lum/ovntable"></auto-complete>
					</div>
				</v-col>
			</v-row>

			<v-row>
				<v-col cols="12" md="6">
					<div class="form-group d-flex">
						<v-checkbox v-if="page.bulk.show" v-model="selected.vars" value="tile_name" class="flex-shrink-1 flex-grow-0"></v-checkbox>
						<auto-complete label="Tile Drain" class="flex-grow-1 flex-shrink-0"
							v-model="item.tile_name" :value="item.tile_name" :show-item-link="props.isUpdate"
							table-name="tiledrain_str" route-name="TiledrainStrEdit"
							section="Structural / Tile Drains" help-file="tiledrain.str" help-db="tiledrain_str"
							api-url="structural/tiledrain"></auto-complete>
					</div>
				</v-col>
				<v-col cols="12" md="6">
					<div class="form-group d-flex">
						<v-checkbox v-if="page.bulk.show" v-model="selected.vars" value="sep_name" class="flex-shrink-1 flex-grow-0"></v-checkbox>
						<auto-complete label="Septic Tank" class="flex-grow-1 flex-shrink-0"
							v-model="item.sep_name" :value="item.sep_name" :show-item-link="props.isUpdate"
							table-name="septic_str" route-name="SepticStrEdit"
							section="Structural / Septic Tanks" help-file="septic.str" help-db="septic_str"
							api-url="structural/septic"></auto-complete>
					</div>
				</v-col>
			</v-row>

			<v-row>
				<v-col cols="12" md="6">
					<div class="form-group d-flex">
						<v-checkbox v-if="page.bulk.show" v-model="selected.vars" value="vfs_name" class="flex-shrink-1 flex-grow-0"></v-checkbox>
						<auto-complete label="Filter Strip" class="flex-grow-1 flex-shrink-0"
							v-model="item.vfs_name" :value="item.vfs_name" :show-item-link="props.isUpdate"
							table-name="filterstrip_str" route-name="FilterstripStrEdit"
							section="Structural / Filter Strips" help-file="filterstrip.str" help-db="filterstrip_str"
							api-url="structural/filterstrip"></auto-complete>
					</div>
				</v-col>
				<v-col cols="12" md="6">
					<div class="form-group d-flex">
						<v-checkbox v-if="page.bulk.show" v-model="selected.vars" value="grww_name" class="flex-shrink-1 flex-grow-0"></v-checkbox>
						<auto-complete label="Grassed Waterway" class="flex-grow-1 flex-shrink-0"
							v-model="item.grww_name" :value="item.grww_name" :show-item-link="props.isUpdate"
							table-name="grassedww_str" route-name="GrassedwwStrEdit"
							section="Structural / Grassed Waterways" help-file="grassedww.str" help-db="grassedww_str"
							api-url="structural/grassedww"></auto-complete>
					</div>
				</v-col>
			</v-row>

			<v-row>
				<v-col cols="12" md="6">
					<div class="form-group d-flex">
						<v-checkbox v-if="page.bulk.show" v-model="selected.vars" value="bmp_name" class="flex-shrink-1 flex-grow-0"></v-checkbox>
						<auto-complete label="Best Management Practices" class="flex-grow-1 flex-shrink-0"
							v-model="item.bmp_name" :value="item.bmp_name" :show-item-link="props.isUpdate"
							table-name="bmpuser_str" route-name="BmpuserStrEdit"
							section="Structural / Best Management Practices" help-file="bmpuser.str" help-db="bmpuser_str"
							api-url="structural/bmpuser"></auto-complete>
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