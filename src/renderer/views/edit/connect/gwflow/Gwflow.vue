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
			ini: {}
		},
		can_enable: false,
		vars: [
			{ name: 'cell_size', description: 'Grid cell size (m)', default: 200, disabled: true, type: 'number', items: [] },
			{ name: 'boundary_conditions', description: 'Boundary conditions (1 = constant head; 2 = no flow)', default: 1, disabled: false, type: 'select', items: [{value: 1, title:'1 = constant head'},{value: 2, title:'2 = no flow'}] },
			{ name: 'recharge', description: 'Recharge connection type (1 = HRU-cell, 2 = LSU-cell, 3 = both)', default: 2, disabled: true, type: 'select', items: [] },
			{ name: 'soil_transfer', description: 'Groundwater --> soil transfer is simulated (0 = no; 1 = yes)', default: 1, disabled: false, type: 'select', items: [{value: 0, title:'0 = no'},{value: 1, title:'1 = yes'}] },
			{ name: 'saturation_excess', description: 'Saturation excess flow is simulated (0 = no; 1 = yes)', default: 1, disabled: false, type: 'select', items: [{value: 0, title:'0 = no'},{value: 1, title:'1 = yes'}] },
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
				const response2 = await api.get(`gwflow/ini`, currentProject.getApiHeader());
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
			const response = await api.put(`gwflow/ini`, currentProject.getApiHeader());
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
		<file-header input-file="gwflow.input" docs-path="modflow" use-io>
			Groundwater Flow
		</file-header>

		<v-alert v-if="!data.can_enable" type="info" icon="$info" variant="tonal" border="start" class="mb-4">
			Groundwater flow must be setup through Step 2, HRUs tab in QSWAT+ in order to use it through the editor.
		</v-alert>
		<div v-else>
			<error-alert as-popup v-model="data.page.saveError" :show="data.page.saveError" :text="data.page.error" :timeout="-1"></error-alert>
			<success-alert v-model="data.page.saveSuccess" :show="data.page.saveSuccess"></success-alert>

			<p>
				Any disabled rows below denote values used during gwflow setup in QSWAT+ and are not editable through SWAT+ editor.
			</p>
			
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
					<tr v-for="v in data.vars" :key="v.name" :class="v.disabled ? 'text-medium-emphasis' : ''">
						<td v-if="v.disabled" class="field">{{ data.item.ini[v.name] }}</td>
						<td v-else class="field">
							<v-select v-if="v.type === 'select'" density="compact" hide-details="auto" 
								v-model="data.item.ini[v.name]"
								:items="v.items"></v-select>
						</td>
						<td>{{ v.description }}</td>
						<td>{{ v.default }}</td>
						<td><font-awesome-icon v-if="v.disabled" :icon="['fas', 'check']"></font-awesome-icon></td>
					</tr>
				</tbody>
			</v-table>
		</div>
	</project-container>
</template>