<script setup lang="ts">
	import { reactive, onMounted, computed, watch } from 'vue';
	import { useRoute, useRouter } from 'vue-router';
	import { useHelpers } from '@/helpers';

	const route = useRoute();
	const router = useRouter();
	const { api, constants, currentProject, errors, formatters, utilities } = useHelpers();

	let page:any = reactive({
		loading: true,
		error: null,
		validated: false,
		saving: false,
		saveSuccess: false,
		saveError: null,
		tab: 'basic',
		copy: {
			show: false,
			error: null,
			saving: false,
			name: null
		},
		delete: {
			show: false,
			error: null,
			saving: false
		},
		item: {},
		reservedTables: ['pl_hv_summer1', 'pl_hv_summer2', 'pl_hv_winter1'],
		tabularItem: '',
		linkBack: null,
		descriptions: [],
		conditionsFields: [
			{ value: 'var', title: 'var' },
			{ value: 'obj', title: 'obj' },
			{ value: 'obj_num', title: 'obj_num' },
			{ value: 'lim_var', title: 'lim_var' },
			{ value: 'lim_op', title: 'lim_op' },
			{ value: 'lim_const', title: 'lim_const' },
			{ value: 'alts', title: 'alts' },
		],
		actionsFields: [
			{ value: 'act_typ', title: 'act_typ' },
			{ value: 'obj', title: 'obj' },
			{ value: 'obj_num', title: 'obj_num' },
			{ value: 'name', title: 'name' },
			{ value: 'option', title: 'option' },
			{ value: 'const', title: 'const' },
			{ value: 'const2', title: 'const2' },
			{ value: 'fp', title: 'fp' },
			{ value: 'outcomes', title: 'outcomes' },
		],
		definitions: {
			conditions: {
				'w_stress': 'water stress',
				'n_stress': 'nitrogen stress',
				'phu_plant': 'potential heat units (plant based)',
				'phu_base0': 'potential heat units (base zero)',
				'plant_gro': 'plants growing',
				'days_harv': 'days since last harvest',
				'day_start': 'days since last harvest',
				'soil_water': 'soil water',
				'jday': 'julian day',
				'month': 'month',
				'year_rot': 'rotation year',
				'year_gro': 'growth year of perennials',
				'year_cal': 'calendar year',
				'year_seq': 'sequential year of simulation',
				'prob': 'probability',
				'tile_flo': 'tile flow',
				'aqu_dep': 'aquifer depth below surface',
				'land_use': 'land use and management',
				'ch_use': 'channel management',
				'vol': 'reservoir volume',
				'vol_wet': 'wetland volume (stored on an hru)'
			},
			actions: {
				'harvest': 'harvest',
				'harvest_kill': 'harvest and kill',
				'till': 'tillage',
				'irrigate': 'irrigate',
				'fertilize': 'fertilize',
				'pest_apply': 'apply pesticide',
				'burn': 'burn',
				'release': 'release',
				'lu_change': 'land use change',
				'plant': 'plant',
				'kill': 'kill',
				'rot_reset': 'reset rotation year',
				'grow_init': 'initiate growing season for hru_lte',
				'grow_end': 'end growing season for hru_lte',
				'drain_control': 'drainage water management',
				'flow_control': 'tile flow control for saturated buffers',
				'chan_change': 'channel change',
				'graze': 'graze'
			}
		}
	});

	async function get() {
		if (route.params.id === undefined) return;
		//if (route.params.dbtype === undefined) return;
		page.loading = true;
		page.error = null;
		let tableId = route.params.id;
		let dbType = route.params.dbtype === undefined ? 'project' : route.params.dbtype;
		console.log(route.params.id)

		try {
			let apiUrl = `decision_table/table/${tableId}`;
			if (dbType === 'datasets') apiUrl = `decision_table/dataset-table/${tableId}`;

			const response = await api.get(apiUrl, currentProject.getApiHeader());
			errors.log(response.data);
			page.item = response.data;

			page.linkBack = page.item.file_name.split('.')[0];

			if (dbType === 'datasets') page.copy.name = page.item.name;
			else page.copy.name = page.item.name + '_copy';

			setTabularItem();

			if (page.item.conditions.length > 0) {
				for (let c of page.item.conditions) {
					for (let i = 0; i < c.alts.length; i++) {
						if (i >= page.descriptions.length) {
							page.descriptions.push({conditions: [], actions: []});
						}

						if (c.alts[i].alt != '-') {
							let varText = c.var;
							if (c.var in page.definitions.conditions) {
								varText = page.definitions.conditions[c.var];
							}

							let item = varText + ' ' + c.alts[i].alt + ' ';
							if (!formatters.isNullOrEmpty(c.lim_var, true)) {
								item += c.lim_var + ' ';
								if (c.lim_op != '-') {
									item += c.lim_op + ' ' + c.lim_const;
								} else if (c.lim_const != 0) {
									item += ' ' + c.lim_const;
								}
							}
							else {
								item += c.lim_const;
							}

							page.descriptions[i].conditions.push(item);
						}
					}
				}

				for (let a of page.item.actions) {
					for (let i = 0; i < a.outcomes.length; i++) {
						if (a.outcomes[i].outcome) {
							let varText = a.act_typ;
							if (a.act_typ in page.definitions.actions) {
								varText = page.definitions.actions[a.act_typ];
							}

							let item = varText + ' ';
							if (!formatters.isNullOrEmpty(a.option, true)) {
								item += a.option + ' ';
							}
							item += '(' + a.name + ')';

							if (i < page.descriptions.length) {
								page.descriptions[i].actions.push(item);
							}							
						}
					}
				}
			}
		} catch (error) {
			page.error = errors.logError(error, 'Unable to get decision table from database.');
		}
		
		page.loading = false;
	}

	function setTabularItem() {
		let int_pad = 10;
		let str_pad = 18;
		let flo_pad = 14;

		let tableDescription = formatters.isNullOrEmpty(page.item.description) ? '' : `     !${page.item.description}`;

		page.tabularItem = 'name'.padEnd(str_pad, ' ')
			+ 'conds'.padStart(int_pad, ' ')
			+ 'alts'.padStart(int_pad, ' ')
			+ 'acts'.padStart(int_pad, ' ') + tableDescription + '\n';

		let numAlts = page.item.conditions.length > 0 ? page.item.conditions[0].alts.length : 0;

		page.tabularItem += page.item.name.padEnd(str_pad, ' ')
			+ `${page.item.conditions.length}`.padStart(int_pad, ' ')
			+ `${numAlts}`.padStart(int_pad, ' ')
			+ `${page.item.actions.length}`.padStart(int_pad, ' ') + '\n';

			page.tabularItem += 'var'.padEnd(str_pad, ' ')
			+ 'obj'.padStart(int_pad, ' ')
			+ 'obj_num'.padStart(int_pad, ' ')
			+ 'lim_var'.padStart(str_pad, ' ')
			+ 'lim_op'.padStart(str_pad, ' ')
			+ 'lim_const'.padStart(flo_pad, ' ');

		for (let i = 0; i < numAlts; i++) {
			page.tabularItem += `alt${i+1}`.padStart(int_pad, ' ');
		}
		page.tabularItem += '\n';

		for (let c of page.item.conditions) {
			page.tabularItem += `${c.var}`.padEnd(str_pad, ' ')
				+ `${c.obj}`.padStart(int_pad, ' ')
				+ `${c.obj_num}`.padStart(int_pad, ' ')
				+ `${c.lim_var}`.padStart(str_pad, ' ')
				+ `${c.lim_op}`.padStart(str_pad, ' ')
				+ `${c.lim_const}`.padStart(flo_pad, ' ');

			for (let a of c.alts) {
				page.tabularItem += `${a.alt}`.padStart(int_pad, ' ');
			}

			let cd = formatters.isNullOrEmpty(c.description) ? '' : `     !${c.description}`;
			page.tabularItem += cd + '\n';
		}

		page.tabularItem += 'act_typ'.padEnd(str_pad, ' ')
			+ 'obj'.padStart(int_pad, ' ')
			+ 'obj_num'.padStart(int_pad, ' ')
			+ 'name'.padStart(str_pad, ' ')
			+ 'option'.padStart(str_pad, ' ')
			+ 'const'.padStart(flo_pad, ' ')
			+ 'const2'.padStart(flo_pad, ' ')
			+ 'fp'.padStart(str_pad, ' ')
			+ 'outcome'.padStart(9, ' ') + '\n';

		for (let a of page.item.actions) {
			page.tabularItem += `${a.act_typ}`.padEnd(str_pad, ' ')
				+ `${a.obj}`.padStart(int_pad, ' ')
				+ `${a.obj_num}`.padStart(int_pad, ' ')
				+ `${a.name}`.padStart(str_pad, ' ')
				+ `${a.option}`.padStart(str_pad, ' ')
				+ `${a.const}`.padStart(flo_pad, ' ')
				+ `${a.const2}`.padStart(flo_pad, ' ')
				+ `${a.fp}`.padStart(str_pad, ' ');

			for (let o of a.outcomes) {
				let ostr = o.outcome ? 'y' : 'n'
				page.tabularItem += `${ostr}`.padStart(3, ' ');
			}

			page.tabularItem += '\n';
		}
	}

	async function save() {
		page.saveError = null;
		page.saving = true;
		page.saveSuccess = false;

		if (formatters.isNullOrEmpty(page.item.name)) {
			page.saveError = 'Please enter a name.';
		} else {
			try {
				if (page.tab === 'advanced') { //Tabular
					let data = {
						name: formatters.toValidName(page.item.name),
						description: page.item.description,
						file_name: page.item.file_name,
						text: page.tabularItem
					};

					const response = await api.put(`decision_table/table/${route.params.id}`, data, currentProject.getApiHeader());
					errors.log(response);
					page.saveSuccess = true;
				}
			} catch (error) {
				page.saveError = errors.logError(error, 'Unable to save changes to database.');
			}
		}

		page.saving = false;
	}

	async function copy() {
		page.copy.error = null;
		page.copy.saving = true;

		if (formatters.isNullOrEmpty(page.copy.name)) {
			page.copy.error = 'Please enter a name.';
		} else {
			try {
				let item = page.item;
				item.id = null;
				item.name = formatters.toValidName(page.copy.name);

				const response = await api.post(`decision_table/table`, item, currentProject.getApiHeader());
				errors.log(response);
				router.push({ name: 'DecisionsEdit', params: { id: response.data.id, dbtype: 'project' } });
				page.copy.show = false;
			} catch (error) {
				page.copy.error = errors.logError(error, 'Unable to save changes to database.');
			}
		}
		
		page.copy.saving = false;
	}

	async function confirmDelete() {
		page.delete.error = null;
		page.delete.saving = true;

		if (notEditable.value) {
			page.delete.error = 'This table cannot be deleted.';
		} else {
			try {
				const response = await api.delete(`decision_table/table/${route.params.id}`, currentProject.getApiHeader());
				errors.log(response);
				page.delete.show = false;
				router.push({ path: '/edit/decision-table/' + page.linkBack });
			} catch (error) {
				page.delete.error = errors.logError(error, 'Unable to delete from database.');
			}
		}

		page.delete.saving = false;
	}

	const notEditable = computed(() => {
		return page.reservedTables.includes(page.item.name) || route.params.dbtype === 'datasets';
	})

	const isUsed = computed(() => {
		return (page.item.management_sch_auto_set && page.item.management_sch_auto_set.length > 0) ||
			(page.item.reservoir_res_set && page.item.reservoir_res_set.length > 0) ||
			(page.item.wetland_wet_set && page.item.wetland_wet_set.length > 0) ||
			(page.item.hru_lte_hru_set && page.item.hru_lte_hru_set.length > 0);
	})

	onMounted(async () => await get())
	watch(() => route.name, async () => await get())
	watch(() => route.params, async () => await get())
</script>

<template>
	<project-container :loading="page.loading" :load-error="page.error">
		<file-header :input-file="page.item.file_name" docs-path="decision-tables">
			<router-link :to="'/edit/decision-table/' + page.linkBack">Decision Tables</router-link>
			/ Edit
		</file-header>

		<error-alert :text="page.error"></error-alert>
		<error-alert :text="page.saveError"></error-alert>
		<success-alert v-model="page.saveSuccess" :show="page.saveSuccess"></success-alert>
		
		<v-form :validated="page.validated" @submit.prevent="save">
			<div class="form-group">
				<v-text-field v-model="page.item.name" :rules="[constants.formRules.required, constants.formRules.nameLength]" 
					label="Name" hint="Must be unique" :readonly="notEditable"></v-text-field>
			</div>

			<div class="form-group">
				<v-text-field v-model="page.item.description" label="Description" :readonly="notEditable"></v-text-field>
			</div>

			<v-alert v-if="notEditable && route.params.dbtype === 'project'" type="info" icon="$info" variant="tonal" border="start" class="mb-4">
				This decision table is reserved in the model and cannot be modified. 
				<br />To change any values in this table, we recommend making a copy and editing the copy instead.
			</v-alert>
			<v-alert v-if="notEditable && route.params.dbtype === 'datasets'" type="info" icon="$info" variant="tonal" border="start" class="mb-4">
				This decision table is located in your datasets library. Make a copy to add it to your project.
			</v-alert>

			<v-card>
				<v-tabs v-model="page.tab" bg-color="primary">
					<v-tab value="basic">Description</v-tab>
					<v-tab value="advanced">{{ notEditable ? 'Plain Text' : 'Advanced Editing' }}</v-tab>
				</v-tabs>

				<v-card-item>
					<v-window v-model="page.tab">
						<v-window-item value="basic">
							<ul class="list-group">
								<li class="list-group-item bg-light" v-for="(d, i) in page.descriptions" :key="i">
									If {{d.conditions.join(' and ')}} then {{d.actions.join(' and ')}}
								</li>
							</ul>

							<v-divider class="my-4"></v-divider>

							<div v-if="page.item.management_sch_auto_set && page.item.management_sch_auto_set.length > 0">
								<p class="mb-0">
									We recommend editing this table using the <router-link to="/edit/lum/mgt">management schedule builder</router-link>. 
									This table is used in the following management schedules:
								</p>
								<ul v-for="sch in page.item.management_sch_auto_set" :key="sch.id">
									<li><router-link :to="`/edit/lum/mgt/edit/${sch.management_sch.id}`">{{sch.management_sch.name}}</router-link></li>
								</ul>
							</div>
							<div v-else-if="page.item.reservoir_res_set && page.item.reservoir_res_set.length > 0">
								<p class="mb-0">This table is used in the following reservoirs:</p>
								<ul v-for="res in page.item.reservoir_res_set" :key="res.id">
									<li><router-link :to="`/edit/cons/reservoirs/edit/${res.id}`">{{res.name}}</router-link></li>
								</ul>
							</div>
							<div v-else-if="page.item.wetland_wet_set && page.item.wetland_wet_set.length > 0">
								<p class="mb-0">This table is used in the following wetlands:</p>
								<ul v-for="res in page.item.wetland_wet_set" :key="res.id">
									<li><router-link :to="`/edit/cons/reservoirs/wetlands/edit/${res.id}`">{{res.name}}</router-link></li>
								</ul>
							</div>
							<div v-else-if="page.item.hru_lte_hru_set && page.item.hru_lte_hru_set.length > 0">
								<p class="mb-0">This table is used in the following HRUs:</p>
								<ul v-for="hru in page.item.hru_lte_hru_set" :key="hru.id">
									<li><router-link :to="`/edit/cons/hrus-lte/edit/${hru.id}`">{{hru.name}}</router-link></li>
								</ul>
							</div>
							<div v-else>
								<p>
									This table isn't being using in your project. 
									<span v-if="page.item.file_name === 'lum.dtl'">
										Use the <router-link to="/edit/lum/mgt">management schedule builder</router-link> to include and/or edit this table.
									</span>
								</p>
							</div>
						</v-window-item>

						<v-window-item value="advanced">
							

							<v-alert v-if="!notEditable" type="warning" icon="$warning" variant="tonal" border="start" class="mb-4">
								Warning: advanced users only.
								If you are comfortable with the decision table format, you may edit in plain text below.
							</v-alert>

							<div v-if="notEditable">
								<div>Conditions</div>
								<v-data-table class="data-table" density="compact"
									:items="page.item.conditions" :items-per-page="-1"
									:headers="page.conditionsFields">
									<template v-slot:item.alts="{ value }">
										<span class="pr-3" v-for="(a, i) in value" :key="i">{{a.alt}}</span>
									</template>
									<template v-slot:bottom></template>
								</v-data-table>

								<div class="mt-5">Actions</div>
								<v-data-table class="data-table" density="compact"
									:items="page.item.actions" :items-per-page="-1"
									:headers="page.actionsFields">
									<template v-slot:item.outcomes="{ value }">
										<span class="pr-3" v-for="(o, i) in value" :key="i">{{o.outcome ? 'y': 'n'}}</span>
									</template>
									<template v-slot:bottom></template>
								</v-data-table>
							</div>
							<div v-else>
								<v-textarea v-model="page.tabularItem" rows="15" class="code"></v-textarea>
							</div>
						</v-window-item>
					</v-window>
				</v-card-item>
			</v-card>					

			<action-bar>
				<v-btn v-if="!notEditable" type="submit" :loading="page.saving" variant="flat" color="primary" class="mr-2">Save Changes</v-btn>
				<back-button></back-button>
				<v-btn type="button" variant="flat" color="info" class="ml-auto" @click="page.copy.show = true">Copy</v-btn>
				<v-btn v-if="!notEditable && !isUsed" type="button" variant="flat" color="error" class="ml-1" @click="page.delete.show = true">Delete</v-btn>
			</action-bar>
		</v-form>

		<v-dialog v-model="page.copy.show" size="lg" title="Copy Decision Table" :max-width="constants.dialogSizes.md">
			<v-card title="">
				<v-card-text>
					<error-alert :text="page.copy.error"></error-alert>	

					<p>
						Would you like to make a copy of this table? Enter a name for the copy below. 
						<br /><span class="text-danger">CAUTION:</span> If the table name entered already exists in your project it will be overwritten.
					</p>

					<div class="form-group">
						<v-text-field v-model="page.copy.name" :rules="[constants.formRules.required, constants.formRules.nameLength]" 
							label="Name" hint="Must be unique"></v-text-field>
					</div>
				</v-card-text>
				<v-divider></v-divider>
				<v-card-actions>
					<v-btn @click="copy" :loading="page.copy.saving" color="primary" variant="text">Copy</v-btn>
					<v-btn @click="page.copy.show = false">Cancel</v-btn>
				</v-card-actions>
			</v-card>
		</v-dialog>

		<v-dialog v-model="page.delete.show" :max-width="constants.dialogSizes.md">
			<v-card title="Confirm delete">
				<v-card-text>
					<error-alert :text="page.delete.error"></error-alert>

					<p>
						Are you sure you want to delete <strong>{{page.item.name}}</strong>?
						This action is permanent and cannot be undone. 
					</p>
				</v-card-text>
				<v-divider></v-divider>
				<v-card-actions>
					<v-btn @click="confirmDelete" :loading="page.delete.saving" color="error" variant="text">Delete</v-btn>
					<v-btn @click="page.delete.show = false">Cancel</v-btn>
				</v-card-actions>
			</v-card>
		</v-dialog>
	</project-container>
</template>
