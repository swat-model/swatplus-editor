<script setup lang="ts">
	import { reactive, onMounted, watch } from 'vue';
	import { useRoute } from 'vue-router';
	import { useHelpers } from '@/helpers';

	const route = useRoute();
	const { api, currentProject, errors, utilities } = useHelpers();

	let data:any = reactive({
		page: {
			loading: false,
			loadingError: null,
			error: null,
			saving: false,
			saveSuccess: false,
			saveError: false
		},
		item: {
			use_gwflow: false,
			base: {}
		},
		can_enable: false,
		vars: [
			{ name: 'cell_size', description: 'Grid cell size (m)', default: 200, disabled: true, type: 'int', items: [] },
			{ name: 'boundary_conditions', description: 'Boundary conditions (1 = constant head; 2 = no flow)', default: 1, disabled: false, type: 'select', items: [{value: 1, title:'1 = constant head'},{value: 2, title:'2 = no flow'}] },
			{ name: 'recharge', description: 'Recharge connection type (1 = HRU-cell, 2 = LSU-cell, 3 = both)', default: 2, disabled: true, type: 'select', items: [] },
			{ name: 'soil_transfer', description: 'Groundwater --> soil transfer is simulated (0 = no; 1 = yes)', default: 1, disabled: false, type: 'select', items: [{value: 0, title:'0 = no'},{value: 1, title:'1 = yes'}] },
			{ name: 'saturation_excess', description: 'Saturation excess flow is simulated (0 = no; 1 = yes)', default: 1, disabled: false, type: 'select', items: [{value: 0, title:'0 = no'},{value: 1, title:'1 = yes'}] },
			{ name: 'external_pumping', description: 'External groundwater pumping (0 = off; 1 = on)', default: 0, disabled: false, type: 'select', items: [{value: 0, title:'0 = off'},{value: 1, title:'1 = on'}] },
			{ name: 'tile_drainage', description: 'Groundwater tile drainage (0 = off; 1 = on)', default: 0, disabled: true, type: 'select', items: [] },
			{ name: 'reservoir_exchange', description: 'Groundwater-reservoir exchange (0 = off; 1 = on)', default: 1, disabled: false, type: 'select', items: [{value: 0, title:'0 = off'},{value: 1, title:'1 = on'}] },
			{ name: 'wetland_exchange', description: 'Groundwater-wetland exchange (0 = off; 1 = on)', default: 1, disabled: false, type: 'select', items: [{value: 0, title:'0 = off'},{value: 1, title:'1 = on'}] },
			{ name: 'floodplain_exchange', description: 'Groundwater-floodplain exchange (0 = off; 1 = on)', default: 1, disabled: false, type: 'select', items: [{value: 0, title:'0 = off'},{value: 1, title:'1 = on'}] },
			{ name: 'canal_seepage', description: 'Canal seepage to groundwater (0 = off; 1 = on)', default: 0, disabled: false, type: 'select', items: [{value: 0, title:'0 = off'},{value: 1, title:'1 = on'}] },
			{ name: 'solute_transport', description: 'Groundwater solute transport (0 = off; 1 = on)', default: 1, disabled: false, type: 'select', items: [{value: 0, title:'0 = off'},{value: 1, title:'1 = on'}] },
			{ name: 'timestep_balance', description: 'Time step (days) to solve groundwater balance equation', default: 1, disabled: false, type: 'float', items: [] },
			{ name: 'daily_output', description: 'Daily groundwater balance output (0 = off; 1 = on)', default: 1, disabled: false, type: 'select', items: [{value: 0, title:'0 = off'},{value: 1, title:'1 = on'}] },
			{ name: 'annual_output', description: 'Annual groundwater balance output (0 = off; 1 = on)', default: 1, disabled: false, type: 'select', items: [{value: 0, title:'0 = off'},{value: 1, title:'1 = on'}] },
			{ name: 'aa_output', description: 'Average annual groundwater balance output (0 = off; 1 = on)', default: 1, disabled: false, type: 'select', items: [{value: 0, title:'0 = off'},{value: 1, title:'1 = on'}] },
			{ name: 'daily_output_row', description: 'Cell row for detailed sources/sink output (0 means not used)', default: 0, disabled: false, type: 'int', items: [] },
			{ name: 'daily_output_col', description: 'Cell column for detailed sources/sink output (0 means not used)', default: 0, disabled: false, type: 'int', items: [] },
			{ name: 'river_depth', description: 'Vertical distance (m) of streambed below the DEM value', default: 5, disabled: false, type: 'float', items: [] },
			//{ name: '', description: '', default: 1, disabled: false, type: 'select', items: [{value: 0, title:'0 = no'},{value: 1, title:'1 = yes'}] },
		]
	});

	async function get() {
		data.page.loading = true;
		data.page.error = null;

		try {
			const response = await api.get(`gwflow/enabled`, currentProject.getApiHeader());
			data.can_enable = response.data.can_enable;

			if (data.can_enable) {
				const response2 = await api.get(`gwflow/base`, currentProject.getApiHeader());
				data.item = response2.data;
			}
		} catch (error) {
			data.page.loadingError = errors.logError(error, 'Unable to get project information from database.');
		}
			
		data.page.loading = false;
	}

	async function save() {
		data.page.error = null;
		data.page.saving = true;
		data.page.saveSuccess = false;
		data.page.saveError = false;

		try {
			const response = await api.put(`gwflow/base`, data.item, currentProject.getApiHeader());
			data.page.saveSuccess = true;
		} catch (error) {
			data.page.error = errors.logError(error, 'Unable to save changes to database.');
			data.page.saveError = true;
		}
		
		data.page.saving = false;
	}

	onMounted(async () => await get())
	watch(() => route.name, async () => await get())
</script>

<template>
	<project-container :loading="data.page.loading" :load-error="data.page.loadingError">
		<v-alert v-if="!data.can_enable" type="info" icon="$info" variant="tonal" border="start" class="mb-4">
			Groundwater flow must be setup through Step 2, HRUs tab in QSWAT+ in order to use it through the editor.
		</v-alert>
		<div v-else-if="$route.name == 'Gwflow'">
			<file-header input-file="gwflow.input" docs-path="modflow" use-io>
				Groundwater Flow
			</file-header>

			<div>
				<error-alert as-popup v-model="data.page.saveError" :show="data.page.saveError" :text="data.page.error" :timeout="-1"></error-alert>
				<success-alert v-model="data.page.saveSuccess" :show="data.page.saveSuccess"></success-alert>

				<p>
					Any disabled rows below denote values used during gwflow setup in QSWAT+ and are not editable through SWAT+ editor.
				</p>
				
				<v-form @submit.prevent="save">
					<v-table class="table-editor" density="compact">
						<thead>
							<tr class="bg-surface">
								<th class="bg-secondary-tonal">Value</th>
								<th class="bg-secondary-tonal">Description</th>
								<th class="bg-secondary-tonal">Default</th>
								<th class="bg-secondary-tonal">QSWAT+ Only</th>
							</tr>
						</thead>
						<tbody>
							<tr>
								<td class="field">
									<v-select density="compact" hide-details="auto" 
										v-model="data.item.use_gwflow"
										:items="[{ value: false, title: 'Disabled'}, {value: true, title: 'Enabled'}]"></v-select>
								</td>
								<td>Enable or disable the groundwater flow module for this simulation</td>
								<td></td>
								<td></td>
							</tr>
							<tr v-for="v in data.vars" :key="v.name" :class="v.disabled ? 'text-medium-emphasis' : ''">
								<td v-if="v.disabled" class="field">{{ data.item.base[v.name] }}</td>
								<td v-else class="field">
									<v-select v-if="v.type === 'select'" density="compact" hide-details="auto" 
										v-model="data.item.base[v.name]"
										:items="v.items"></v-select>
									<v-text-field density="compact" v-else-if="v.type === 'float'" 
										v-model.number="data.item.base[v.name]" type="number" step="any" hide-details="auto">
									</v-text-field>
									<v-text-field density="compact" v-else-if="v.type === 'int'" 
										v-model.number="data.item.base[v.name]" type="number" hide-details="auto">
									</v-text-field>
								</td>
								<td>{{ v.description }}</td>
								<td>{{ v.default }}</td>
								<td><font-awesome-icon v-if="v.disabled" :icon="['fas', 'check']"></font-awesome-icon></td>
							</tr>
						</tbody>
					</v-table>

					<action-bar>
						<v-btn type="submit" :loading="data.page.saving" variant="flat" color="primary" class="mr-2">Save Changes</v-btn>
						<back-button></back-button>
					</action-bar>
				</v-form>
			</div>
		</div>
		<router-view v-else></router-view>
	</project-container>
</template>