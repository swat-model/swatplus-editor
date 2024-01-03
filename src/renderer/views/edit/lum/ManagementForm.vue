<script setup lang="ts">
	import { reactive, onMounted, computed, watch } from 'vue';
	import { useRouter, useRoute } from 'vue-router';
	import { useHelpers } from '@/helpers';

	const router = useRouter();
	const route = useRoute();
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
		tabIndex: 0,
		form: {
			name: '',
			auto_ops: <any[]>[],
			operations: <any[]>[]
		},
		modal: {
			show: false,
			validate: false,
			saving: false,
			error: undefined,

			new: false,
			editIndex: 0,
			operation: {
				op_typ: 'plnt',
				mon: 0,
				day: 0,
				hu_sch: 0,
				op_data1: null,
				op_data2: null,
				op_data3: 0,
				order: 1
			}
		},
		reservedTableModal: {
			show: false,
			error: undefined
		}
	});

	let data:any = reactive({
		days: [
			{ value: 0, title: 'None (use heat units)' }
		],
		months: [
			{ value: 0, title: 'None (use heat units)' },
			{ value: 1, title: 'January' },
			{ value: 2, title: 'February' },
			{ value: 3, title: 'March' },
			{ value: 4, title: 'April' },
			{ value: 5, title: 'May' },
			{ value: 6, title: 'June' },
			{ value: 7, title: 'July' },
			{ value: 8, title: 'August' },
			{ value: 9, title: 'September' },
			{ value: 10, title: 'October' },
			{ value: 11, title: 'November' },
			{ value: 12, title: 'December' }
		],
		op_codes: [],
		new_auto_op: {
			name: '',
			plant1: '',
			plant2: ''
		},
		op_data1: {
			label: '',
			section: '',
			file: '',
			db: ''
		},
		op_data2: {
			label: '',
			section: '',
			file: '',
			db: ''
		},
		has_op_data3: ['fert', 'pest', 'graz', 'dwm'],
		reserved_d_tables: {
			summer1: 'pl_hv_summer1',
			summer2: 'pl_hv_summer2',
			winter1: 'pl_hv_winter1'
		},
		fertilizers: [],
		chem_apps: [],
		aquifers: [],
		channels: [],
		reservoirs: [],
		builder: {
			defaults: {},
			warning: null,
			selections: {
				type: null,
				table: null,
				description: null,
				irrigation: null,
				irrigation2: null
			},
			modal: {
				loading: false,
				show: false,
				validate: false,
				saving: false,
				error: undefined,

				new: false,
				editIndex: null,
				op: {
					name: null,
					description: null,
					plant1: null,
					plant2: null,
					table: null,
					saveAsNew: false
				}
			},
			typeOptions: [
				{ value: 'cropRotation', title: 'crop rotation' },
				{ value: 'tillage', title: 'tillage' },
				{ value: 'fertilizer', title: 'fertilizer' },
				{ value: 'irrigation', title: 'irrigation' },
				{ value: 'grazing', title: 'grazing' },
				{ value: 'hayForestCutting', title: 'hay and forest cutting' }
			],
			tables: {
				cropRotation: [
					{ value: 'pl_hv_summer1', title: 'plant and harvest for continuous summer crop' },
					{ value: 'pl_hv_summer2', title: 'plant and harvest for 2 year summer crop rotation' },
					{ value: 'pl_hv_winter1', title: 'plant and harvest for continuous winter crop' },
					{ value: 'pl_hv_ccsws', title: 'corn-corn-soybean-winter wheat-soybean rotation' }
				],
				tillage: [
					{ value: 'fall_plow', title: 'fall plow followed by field cultivator with spring field cultivator' },
					{ value: 'spring_plow', title: 'spring plow followed by field cultivator with fall field cultivator' },
					{ value: 'mulch_till_1', title: 'mulch tillage - disk before plant and chisel plow after harvest' },
					{ value: 'mulch_till_2', title: 'mulch tillage - chisel plow and disk before planting - no fall tillage' },
					{ value: 'no_till', title: 'no tillage - use zerotill in tillage.til to simulate a planter' }
				],
				fertilizer: [							
					{ value: 'fert_stess_test', title: 'fertilizer stress test' },
					{ value: 'fert_sprg_side', title: 'spring side dressing' }
				],
				irrigation: [
					{ value: 'waterStress', title: 'water stress' },
					{ value: 'irr_opt_sw_unlim', title: 'soil moisture deficit' }
				],
				grazing: [
					{ value: 'graze_winter', title: 'winter grazing' },
					{ value: 'graze_summer', title: 'summer grazing' }
				],
				hayForestCutting: [
					{ value: 'hay_cutting', title: 'hay cutting' },
					{ value: 'forest_cut', title: 'forest cutting' }
				]
			},
			irrWaterStressSources: [
				{ value: 'irr_str8_unlim', title: 'unlimited' },
				{ value: 'waterStressRes', title: 'reservoir' },
				{ value: 'waterStressAqu', title: 'aquifer' },
				{ value: 'irr_str8_cha', title: 'channel' }
			],
			irrWaterStressRes: [
				{ value: 'irr_str8_res', title: 'none' },
				{ value: 'irr_str8_r_a_u', title: 'aquifer backup (and unlimited backup to both)' },
				{ value: 'irr_str8_res_aqu', title: 'aquifer backup (no unlimited backup)' }
			],
			irrWaterStressAqu: [
				{ value: 'irr_str8_aqu', title: 'none' },
				{ value: 'irr_str8_a_r_u', title: 'reservoir backup (and unlimited backup to both)' },
				{ value: 'irr_str8_aqu_res', title: 'reservoir backup (no unlimited backup)' }
			],
			customDescriptions: {
				'fert_stess_test': 'fertilizer stress test',
				'fert_sprg_side': 'spring side dressing',
				'graze_winter': 'winter grazing',
				'graze_summer': 'summer grazing',
				'hay_cutting': 'hay cutting',
				'forest_cut': 'forest cutting',
				'irr_opt_sw_unlim': 'irrigate when there is a soil moisture deficit',
				'irr_str8_unlim': 'irrigate from an unlimited source when there is plant water stress',
				'irr_str8_res': 'irrigate from a reservoir when there is plant water stress',
				'irr_str8_aqu': 'irrigate from an aquifer when there is plant water stress',
				'irr_str8_cha': 'irrigate from a channel when there is plant water stress'
			}
		}
	});

	async function get() {
		page.loading = true;
		page.error = null;

		for (let i = 1; i <= 31; i++) {
			data.days.push({ value: i, title: i.toString() });
		}

		if (props.item !== undefined) {
			errors.log(props.item);
			page.form.name = props.item.name;

			if (props.item.auto_ops) {
				for (let i = 0; i < props.item.auto_ops.length; i++) {
					page.form.auto_ops.push({
						name: props.item.auto_ops[i].d_table.name,
						description: props.item.auto_ops[i].d_table.description,
						plant1: props.item.auto_ops[i].plant1,
						plant2: props.item.auto_ops[i].plant2
					});
				}
			}

			page.form.operations = props.item.operations;
			page.tabIndex = page.form.operations && page.form.operations.length > 0 ? 1 : 0;
		}

		try {
			const response = await api.get(`definitions/codes/management_sch/op_typ/${utilities.appPathUrl}`);
			errors.log(response.data);
			data.op_codes = response.data;

			const response2 = await api.get(`decision_table/dataset-builder`, currentProject.getApiHeader());
			let builder_data = response2.data;
			data.builder.defaults = builder_data.tables;
			data.builder.warning = builder_data.warning;
			data.fertilizers = builder_data.fertilizers;
			data.chem_apps = builder_data.chem_apps;
			data.reservoirs = builder_data.reservoirs;
			data.aquifers = builder_data.aquifers;
			data.channels = builder_data.channels;
		} catch (error) {
			page.error = errors.logError(error, 'Unable to load schedule data from database.');
		}
		
		page.loading = false;
	}

	function putDb(data:any) {
		if (props.isUpdate)
			return api.put(`lum/mgt_sch/${props.item.id}`, data, currentProject.getApiHeader());
		else
			return api.post(`lum/mgt_sch`, data, currentProject.getApiHeader());
	}

	async function save() {
		page.error = null;
		page.saving = true;
		page.saveSuccess = false;
		page.validated = true;
		
		let item = page.form;			
		item.name = formatters.toValidName(page.form.name);
		
		try {
			const response = await putDb(item);

			if (props.isUpdate)
				page.saveSuccess = true;
			else
				router.push({ name: 'Management'});
		} catch (error) {
			page.error = errors.logError(error, 'Unable to save changes to database.');
		}
			
		
		page.saving = false;
		page.validated = false;
	}

	function getNamesOpData1() {
		/*
		!! plnt; autoplnt - plant
		!! harv; autoharv - harvest only
		!! kill; autokill - kill
		!! hvkl; autohk - harvest and kill
		!! till; autotill - tillage
		!! irrm; autoirr - irrigation
		!! fert; autofert - fertlizer
		!! pest; pestauto - pesticide application
		!! graz; autograz - grazing
		!! burn; autoburn - burn
		!! swep; autoswep - street sweep
		!! prtp - print plant vars
		!! skip - skip to end of the year
		*/
		switch(page.modal.operation.op_typ) {
			case 'plnt':
			case 'harv':
			case 'kill':
			case 'hvkl':
				return 'plant';
			case 'till':
				return 'till';
			case 'irrm':
				return 'irr_ops';
			case 'fert':
				return 'fert';
			case 'pest':
				return 'pest';
			case 'graz':
				return 'graze_ops';
			case 'burn':
				return 'fire_ops';
			case 'swep':
				return 'sweep_ops';
			case 'prtp':
				break;
			case 'skip':
				break;
		}

		return null;
	}

	function getApiUrlOpData1() {
		switch(page.modal.operation.op_typ) {
			case 'plnt':
			case 'harv':
			case 'kill':
			case 'hvkl':
				return 'db/plants';
			case 'till':
				return 'db/tillage';
			case 'irrm':
				return 'ops/irrigation';
			case 'fert':
				return 'db/fertilizer';
			case 'pest':
				return 'db/pesticides';
			case 'graz':
				return 'ops/graze';
			case 'burn':
				return 'ops/fire';
			case 'swep':
				return 'ops/sweep';
			case 'prtp':
				break;
			case 'skip':
				break;
		}

		return null;
	}

	function getNamesOpData2() {
		switch(page.modal.operation.op_typ) {
			case 'plnt':
			case 'kill':
				break;
			case 'harv':
			case 'hvkl':
				return 'harv_ops';
			case 'till':
			case 'irrm':
				break;
			case 'fert':
			case 'pest':
				return 'chem_app_ops';
			case 'graz':
			case 'burn':
			case 'swep':
			case 'prtp':
			case 'skip':
				break;
		}

		return null;
	}

	function getApiUrlOpData2() {
		switch(page.modal.operation.op_typ) {
			case 'plnt':
			case 'kill':
				break;
			case 'harv':
			case 'hvkl':
				return 'ops/harvest';
			case 'till':
			case 'irrm':
				break;
			case 'fert':
			case 'pest':
				return 'ops/chemapp';
			case 'graz':
			case 'burn':
			case 'swep':
			case 'prtp':
			case 'skip':
				break;
		}

		return null;
	}

	function addAutoOp() {
		let resetAutoOp = {
			name: '',
			plant1: '',
			plant2: ''
		};
		let newName = data.new_auto_op.name;
		let matches = page.form.auto_ops.filter(function(el:any) { return el.name === newName; });
		let doesNotExist = matches === undefined || matches.length < 1;
		if (data.new_auto_op.name != '' && doesNotExist) {
			if ((newName === data.reserved_d_tables.summer1) ||
				(newName === data.reserved_d_tables.summer2) ||
				(newName === data.reserved_d_tables.winter1)) {
					page.reservedTableModal.show = true;
			} else {
				page.form.auto_ops.push(data.new_auto_op);
				data.new_auto_op = resetAutoOp;
			}
		}	
		
		if (!doesNotExist)
			data.new_auto_op = resetAutoOp;
	}

	function removeAutoOp(element:any) {
		page.form.auto_ops.splice(page.form.auto_ops.indexOf(element), 1);
	}

	function addReservedAutoOp() {
		if (formatters.isNullOrEmpty(data.new_auto_op.plant1) || 
			(data.new_auto_op.name === data.reserved_d_tables.summer2 && formatters.isNullOrEmpty(data.new_auto_op.plant2))) {
			page.reservedTableModal.error = 'Please enter a plant name.';
		} else {
			page.form.auto_ops.push(data.new_auto_op);
			cancelReservedAutoOp();
		}
	}

	function cancelReservedAutoOp() {
		data.new_auto_op = {
			name: '',
			plant1: '',
			plant2: ''
		};
		page.reservedTableModal.show = false;
	}

	function autoOpPlantLabel(op:any) {
		if (formatters.isNullOrEmpty(op.plant1)) return '';
		let str = `(${op.plant1}`;
		if (!formatters.isNullOrEmpty(op.plant2)) str += `, ${op.plant2}`;
		return str + ')';
	}

	function removeOp(element:any) {
		page.form.operations.splice(page.form.operations.indexOf(element), 1);
	}

	function editOp(op:any) {
		page.modal.operation = {
			op_typ: op.op_typ,
			mon: op.mon,
			day: op.day,
			hu_sch: op.hu_sch,
			op_data1: op.op_data1,
			op_data2: op.op_data2,
			op_data3: op.op_data3,
			order: op.order
		};
		page.modal.editIndex = page.form.operations.indexOf(op);
		page.modal.new = false;
		setLabels(op.op_typ);
		page.modal.show = true;
	}

	function addOp(op:any) {
		page.modal.editIndex = 0;
		page.modal.new = true;
		setLabels('plnt');
		page.modal.show = true;
	}

	function setLabels(name:string) {
		switch(name) {
			case 'plnt':
			case 'kill':
				data.op_data1.label = 'Plant name';
				data.op_data1.section = 'Databases / Plants';
				data.op_data1.file = 'plants.plt';
				data.op_data1.db = 'plants_plt';
				break;
			case 'harv':
			case 'hvkl':
				data.op_data1.label = 'Plant name';
				data.op_data1.section = 'Databases / Plants';
				data.op_data1.file = 'plants.plt';
				data.op_data1.db = 'plants_plt';
				data.op_data2.label = 'Harvest operation name';
				data.op_data2.section = 'Operations / Harvest';
				data.op_data2.file = 'harv.ops';
				data.op_data2.db = 'harv_ops';
				break;
			case 'till':
				data.op_data1.label = 'Tillage name';
				data.op_data1.section = 'Databases / Tillage';
				data.op_data1.file = 'tillage.til';
				data.op_data1.db = 'tillage_til';
				break;
			case 'irrm':
				data.op_data1.label = 'Irrigation operation name';
				data.op_data1.section = 'Operations / Irrigation';
				data.op_data1.file = 'irr.ops';
				data.op_data1.db = 'irr_ops';
				break;
			case 'fert':
				data.op_data1.label = 'Fertilizer name';
				data.op_data1.section = 'Databases / Fertilizer';
				data.op_data1.file = 'fertilizer.frt';
				data.op_data1.db = 'fertilizer_frt';
				data.op_data2.label = 'Chemical application name';
				data.op_data2.section = 'Operations / Chemical Application';
				data.op_data2.file = 'chem_app.ops';
				data.op_data2.db = 'chem_app_ops';
				break;
			case 'pest':
				data.op_data1.label = 'Pesticide name';
				data.op_data1.section = 'Databases / Pesticide';
				data.op_data1.file = 'pesticide.pes';
				data.op_data1.db = 'pesticide_pst';
				data.op_data2.label = 'Chemical application name';
				data.op_data2.section = 'Operations / Chemical Application';
				data.op_data2.file = 'chem_app.ops';
				data.op_data2.db = 'chem_app_ops';
				break;
			case 'graz':
				data.op_data1.label = 'Graze operation name';
				data.op_data1.section = 'Operations / Graze';
				data.op_data1.file = 'graze.ops';
				data.op_data1.db = 'graze_ops';
				break;
			case 'burn':
				data.op_data1.label = 'Fire operation name';
				data.op_data1.section = 'Operations / Fire';
				data.op_data1.file = 'fire.ops';
				data.op_data1.db = 'fire_ops';
				break;
			case 'swep':
				data.op_data1.label = 'Sweep operation name';
				data.op_data1.section = 'Operations / Sweep';
				data.op_data1.file = 'sweep.ops';
				data.op_data1.db = 'sweep_ops';
				break;
		}
	}

	function changeOp(event:string) {
		setLabels(event);

		page.modal.operation.op_data1 = null;
		page.modal.operation.op_data2 = null;
	}

	function saveOp() {
		var ot = page.modal.operation.op_typ;
		if (ot == 'prtp' || ot == 'skip') {
			page.modal.operation.op_data1 = null;
			page.modal.operation.op_data2 = null;
			page.modal.operation.op_data3 = 0;
		}
		if (!(ot == 'harv' || ot == 'hvkl' || ot == 'fert' || ot == 'pest')){
			page.modal.operation.op_data2 = null;
		}

		if (page.modal.new) {
			page.form.operations.push(page.modal.operation);
		} else {
			page.form.operations[page.modal.editIndex] = page.modal.operation;
		}

		resetOp();
		sortOps();
		page.modal.show = false;
	}

	function cancel() {
		page.modal.show = false;
		resetOp();
	}

	function resetOp() {
		page.modal.operation = {
			op_typ: 'plnt',
			mon: 0,
			day: 0,
			hu_sch: 0,
			op_data1: null,
			op_data2: null,
			op_data3: 0,
			order: 1
		};
		setLabels('plnt');
	}

	function sortOps() {
		function compare(a:any, b:any) {
			if (a.order < b.order)
				return -1;
			if (a.order > b.order)
				return 1;
			
			if (a.hu_sch == 0 && b.hu_sch > 0)
				return 1;
			if (a.hu_sch > 0 && b.hu_sch == 0)
				return -1;

			if (a.hu_sch < b.hu_sch)
				return -1;
			if (a.hu_sch > b.hu_sch)
				return 1;
			if (a.mon < b.mon)
				return -1;
			if (a.mon > b.mon)
				return 1;
			if (a.day < b.day)
				return -1;
			if (a.day > b.day)
				return 1;
			return 0;
		}

		return page.form.operations.sort(compare);
	}

	async function goToAutoOp(name:string) {
		try {
			const response = await utilities.getAutoCompleteId('dtl', name);
			let id = response.data.id;
			
			router.push({ name: 'DecisionsEdit', params: { id: id, dbtype: 'project' }});
		} catch (error) {
			page.error = errors.logError(error, 'Cannot find ' + name + ' in database.');
		}
	}

	function autoOpDescription(element:any) {
		if (element.name in data.builder.customDescriptions) return data.builder.customDescriptions[element.name];
		return formatters.isNullOrEmpty(element.description) ? element.name : element.description;
	}

	function configureBuilderTable() {
		data.builder.modal.error = undefined;
		let d = data.builder.selections;
		let tableName = d.table;
		if (d.table === 'waterStress') {
			if (['waterStressRes','waterStressAqu'].includes(d.irrigation)) {
				tableName = d.irrigation2;
			} else {
				tableName = d.irrigation;
			}
		}

		if (tableName in data.builder.defaults) {
			let defaultTable = data.builder.defaults[tableName];
			data.builder.modal.op = {
				name: tableName,
				description: autoOpDescription(defaultTable),
				plant1: null,
				plant2: null,
				table: defaultTable,
				saveAsNew: false
			};
		} else {
			data.builder.modal.error = `Cannot find table ${tableName} in your swatplus_datasets.sqlite. Make sure you have version 2.1.0 or greater copied to your project folder.`;
		}

		data.builder.modal.show = true;
	}

	async function getBuilderTable(element:any) {
		data.builder.modal.loading = true;
		data.builder.modal.show = true;
		data.builder.modal.error = undefined;

		try {
			const response = await api.get(`decision_table/name/lum.dtl/${element.name}`, currentProject.getApiHeader());
			let table = response.data;
			data.builder.modal.op = {
				name: table.name,
				description: autoOpDescription(table),
				plant1: element.plant1,
				plant2: element.plant2,
				table: table,
				saveAsNew: false
			};
			data.builder.modal.editIndex = page.form.auto_ops.indexOf(element);
			//this.removeAutoOp(element);
		} catch (error) {
			data.builder.modal.error = errors.logError(error, 'Cannot find ' + element.name + ' in database.');
		}

		data.builder.modal.loading = false;
	}

	async function saveBuilderTable(overwrite:boolean) {
		errors.log(data.builder.modal.op.table);
		data.builder.modal.saving = true;
		data.builder.modal.error = undefined;

		try {
			let op = data.builder.modal.op;
			let tableName = op.name;
			let autoOp = {
				name: tableName,
				description: op.description,
				plant1: null,
				plant2: null
			};

			if (reserved_d_table_array.value.includes(op.name)) {
				autoOp.plant1 = op.plant1;
				if (op.name === data.reserved_d_tables.summer2) {
					autoOp.plant2 = op.plant2;
				}
			}

			if (!reserved_d_table_array.value.includes(op.name) || op.saveAsNew) {
				if (reserved_d_table_array.value.includes(op.name)) {
					tableName = `${op.name}_${op.plant1}`;
					if (op.name === data.reserved_d_tables.summer2) {
						tableName += `_${op.plant2}`;
					}
				}

				let item = {
					overwrite: overwrite,
					name: tableName,
					description: op.description,
					file_name: 'lum.dtl',
					conditions: op.table.conditions,
					actions: op.table.actions
				};

				const dresp = await api.post(`decision_table/builder`, item, currentProject.getApiHeader());
				errors.log(dresp);
				tableName = dresp.data.name;
			} 

			autoOp.name = tableName;
			if (data.builder.modal.editIndex !== null) {
				page.form.auto_ops.splice(data.builder.modal.editIndex, 1);
				data.builder.modal.editIndex = null;
			}
			page.form.auto_ops.push(autoOp);

			data.builder.modal.show = false;
			resetBuilderOp();
		} catch (error) {
			data.builder.modal.error = errors.logError(error, 'Error saving table.');
		}

		data.builder.modal.saving = false;
	}

	function cancelBuilderTable() {
		data.builder.modal.show = false;
		resetBuilderOp();
	}
	
	function resetBuilderOp() {
		data.builder.modal.op = {
			name: null,
			description: null,
			plant1: null,
			plant2: null,
			table: null,
			saveAsNew: false
		};
	}

	function isBuilderTableIn(type:string) {
		let array = data.builder.tables[type];
		switch(type) {
			case 'irrWaterStressSources':
				array = data.builder.irrWaterStressSources;
				break;
			case 'irrWaterStressRes':
				array = data.builder.irrWaterStressRes;
				break;
			case 'irrWaterStressAqu':
				array = data.builder.irrWaterStressAqu;
				break;
			default:
				array = data.builder.tables[type];
				break;
		}
		let tableName = data.builder.modal.op.name;
		if (formatters.isNullOrEmpty(tableName)) return false;
		let matches = array.filter(function(el:any) { return tableName.startsWith(el.value); });
		return matches && matches.length > 0;
	}

	function setActionObjNumFromCond(value:any, obj:any) {
		let matches = data.builder.modal.op.table.actions.filter(function(el:any) { return el.obj === obj; });
		for (let m of matches) {
			m.obj_num = value;
		}
	}

	const sortedOperations = computed(() => {
		return sortOps();
	})

	const opData3Label = computed(() => {
		if (page.modal.operation.op_typ == 'fert' || page.modal.operation.op_typ == 'pest') return 'Amount applied (kg/ha)';
		if (page.modal.operation.op_typ == 'graz') return 'Number of days of grazing';
		if (page.modal.operation.op_typ == 'dwm') return 'Tile depth (mm)';
		return 'Operation data 3 (override)';
	})

	const builderTableOptions = computed(() => {
		let ops = [];
		switch(data.builder.selections.type) {
			case 'cropRotation':
				ops = data.builder.tables.cropRotation;
				break;
			case 'tillage':
				ops = data.builder.tables.tillage;
				break;
			case 'fertilizer':
				ops = data.builder.tables.fertilizer;
				break;
			case 'irrigation':
				ops = data.builder.tables.irrigation;
				break;
			case 'grazing':
				ops = data.builder.tables.grazing;
				break;
			case 'hayForestCutting':
				ops = data.builder.tables.hayForestCutting;
				break;
		}

		//ops.unshift({ value: null, title: `Select ${builderTableNullLabel.value}` });
		return ops;
	})

	const builderTableNullLabel = computed(() => {
		switch(data.builder.selections.type) {
			case 'cropRotation':
				return 'a crop rotation';
			case 'tillage':
				return 'tillage';
			case 'fertilizer':
				return 'fertilizer';
			case 'irrigation':
				return 'a trigger';
			case 'grazing':
				return 'grazing season';
			case 'hayForestCutting':
				return 'type of cutting';
		}

		return '';
	})

	const reserved_d_table_array = computed(() => {
		return [data.reserved_d_tables.summer1, data.reserved_d_tables.summer2, data.reserved_d_tables.winter1];
	})

	const validCropRotationConditions = computed(() => {
		return data.builder.modal.op.table.conditions.filter(function(el:any) { return ['phu_base0', 'phu_plant'].includes(el.var); });
	})

	const validIrrigationConditions = computed(() => {
		return data.builder.modal.op.table.conditions.filter(function(el:any) { return ['soil_water', 'w_stress', 'vol', 'aqu_dep'].includes(el.var); });
	})

	const validIrrigationActions = computed(() => {
		return data.builder.modal.op.table.actions.filter(function(el:any) { return ['irr_demand', 'irrigate'].includes(el.act_typ); });
	})

	const validFertilizerConditions = computed(() => {
		return data.builder.modal.op.table.conditions.filter(function(el:any) { return !['plant_gro'].includes(el.var); });
	})

	const validFertilizerActions = computed(() => {
		if (!formatters.isNullOrEmpty(data.builder.modal.op.name)) {
			if (data.builder.modal.op.name.startsWith('fert_stess_test')) {
				return [
					{ heading: 'fertilize when nitrogen stress < amount above and plant is growing', action: data.builder.modal.op.table.actions[0] },
					{ heading: 'fertilize when phosphorus stress < amount above and plant is growing', action: data.builder.modal.op.table.actions[1] }
				];
			} else if (data.builder.modal.op.name.startsWith('fert_sprg_side')) {
				return [
					{ heading: 'fertilize just before planting in rotation year', action: data.builder.modal.op.table.actions[0] },
					{ heading: 'fertilize when plant is growing in rotation year, before it reaches maturity', action: data.builder.modal.op.table.actions[1] },
					{ heading: 'fertilize when plant is growing before it reaches maturity', action: data.builder.modal.op.table.actions[2] }
				];
			}
		}

		return [];
	})

	onMounted(async () => await get())
	watch(() => route.name, async () => await get())
	watch(() => route.params.id, async () => await get())
</script>

<template>
	<div>
		<error-alert :text="page.error"></error-alert>
		<success-alert v-model="page.saveSuccess" :show="page.saveSuccess"></success-alert>

		<page-loading :loading="page.loading"></page-loading>
		<v-form @submit.prevent="save" v-if="!page.loading">
			<div class="form-group">
				<v-text-field v-model="page.form.name" :rules="[constants.formRules.required, constants.formRules.longNameLength]" 
					label="Schedule name" hint="Must be unique"></v-text-field>
			</div>

			<v-card>
				<v-tabs v-model="page.tabIndex" bg-color="primary">
					<v-tab :value="0">Schedule Builder</v-tab>
					<v-tab :value="1">Advanced</v-tab>
				</v-tabs>

				<v-card-item>
					<v-window v-model="page.tabIndex">
						<v-window-item :value="0">
							<v-alert v-if="!formatters.isNullOrEmpty(data.builder.warning)" type="warning" icon="$warning" variant="tonal" border="start" class="mb-4">
								{{data.builder.warning}}
							</v-alert>
							<div v-else class="py-3">
								<p>
									Use the schedule builder below to apply land use decision tables built by the SWAT+ development 
									team. These tables are designed cover most use cases, but if you have a complex need, please 
									<open-in-browser url="https://swat.tamu.edu/contact/" text="contact us directly" class="text-primary"></open-in-browser>
									and we can work with you to build a custom table.
								</p>

								<v-alert v-if="page.form.operations.length > 0" type="warning" icon="$warning" variant="tonal" border="start" class="mb-4">
									You have manual operations defined for this schedule and should use the advanced tab to modify them.
								</v-alert>

								<h3 class="text-h5 mb-3">Decision tables used in this management schedule</h3>
								<div class="mb-6">
									<ul class="list-group">
										<li class="list-group-item bg-light d-flex align-items-center" v-for="element in page.form.auto_ops" :key="element.name">
											
											<a @click.prevent="getBuilderTable(element)"><font-awesome-icon :icon="['fas', 'edit']" class="mr-2 text-primary pointer"><v-tooltip activator="parent">{{ constants.commonMessages.leaveWarning }}</v-tooltip></font-awesome-icon></a> 
											<div>{{autoOpDescription(element)}} {{autoOpPlantLabel(element)}}</div>
											<a @click.prevent="removeAutoOp(element)" class="ml-auto"><font-awesome-icon :icon="['fas', 'times']" class="text-error pointer"><v-tooltip activator="parent">Delete</v-tooltip></font-awesome-icon></a>
										</li>
									</ul>
								</div>

								<h3 class="text-h5 mb-3">Add a decision table</h3>
								<div class="mb-3">
									<v-select v-model="data.builder.selections.type" label="Select the type of operation..." :items="data.builder.typeOptions" @update:model-value="data.builder.selections.table=null"></v-select>
								</div>
								<div v-if="!formatters.isNullOrEmpty(data.builder.selections.type)">
									<v-select v-model="data.builder.selections.table" :items="builderTableOptions" :label="`Select ${builderTableNullLabel}`"></v-select>

									<div class="my-3" v-if="data.builder.selections.table === 'waterStress'">
										<v-select v-model="data.builder.selections.irrigation" label="Select primary source..." 
											:items="data.builder.irrWaterStressSources" @update:model-value="data.builder.selections.irrigation2 = null">
										</v-select>

										<div class="my-3" v-if="['waterStressRes','waterStressAqu'].includes(data.builder.selections.irrigation)">
											<v-select v-model="data.builder.selections.irrigation2" label="Select backup source..." 
												:items="data.builder.selections.irrigation === 'waterStressRes' ? data.builder.irrWaterStressRes : data.builder.irrWaterStressAqu">
											</v-select>
										</div>

										<div class="mt-3" v-if="!formatters.isNullOrEmpty(data.builder.selections.irrigation2) || ['irr_str8_unlim','irr_str8_cha'].includes(data.builder.selections.irrigation)">
											<v-btn variant="flat" color="primary" @click="configureBuilderTable">Configure &amp; Add</v-btn>
										</div>
									</div>
									<div class="my-3" v-else-if="!formatters.isNullOrEmpty(data.builder.selections.table)">
										<v-btn variant="flat" color="primary" @click="configureBuilderTable">Configure &amp; Add</v-btn>
									</div>
								</div>

								<v-dialog v-model="data.builder.modal.show" :max-width="constants.dialogSizes.lg" persistent>
									<v-card :title="data.builder.modal.loading ? 'Loading...' : `Configure: ${data.builder.modal.op.description}`">
										<v-card-text>
											<page-loading :loading="data.builder.modal.loading"></page-loading>
											<div v-if="!data.builder.modal.loading">
												<error-alert :text="data.builder.modal.error"></error-alert>

												<div style="min-height:300px">
													<div v-if="!formatters.isNullOrEmpty(data.builder.modal.op.name) && data.builder.modal.op.name.startsWith('pl_hv_')">
														<div v-if="reserved_d_table_array.includes(data.builder.modal.op.name)">
															<div class="form-group mb-0">
																<auto-complete label="Plant"
																	v-model="data.builder.modal.op.plant1" :value="data.builder.modal.op.plant1"
																	table-name="plant" route-name="PlantsEdit"
																	section="Databases / Plants" help-file="plants.plt" help-db="plants_plt"
																	api-url="db/plants"></auto-complete>
															</div>

															<div class="form-group mb-0" v-if="data.builder.modal.op.name === data.reserved_d_tables.summer2">
																<auto-complete label="Plant 2"
																	v-model="data.builder.modal.op.plant2" :value="data.builder.modal.op.plant2"
																	table-name="plant" route-name="PlantsEdit"
																	section="Databases / Plants" help-file="plants.plt" help-db="plants_plt"
																	api-url="db/plants"></auto-complete>
															</div>

															<v-checkbox v-model="data.builder.modal.op.saveAsNew" label="Edit heat units?" hide-details></v-checkbox>
															<div v-if="data.builder.modal.op.saveAsNew">
																<v-table class="table-editor mb-4" density="compact">
																	<thead>
																		<tr class="bg-surface">
																			<th colspan="2" class="bg-secondary-tonal">Conditions to trigger table</th>
																		</tr>
																	</thead>
																	<tbody>
																		<tr v-for="cond in validCropRotationConditions" :key="cond.id">
																			<td class="field">
																				<v-text-field density="compact" :rules="[constants.formRules.required]" v-model.number="cond.lim_const" type="number" step="any" hide-details="auto"></v-text-field>
																			</td>
																			<td>{{cond.description}}</td>
																		</tr>
																	</tbody>
																</v-table>
															</div>
														</div>
													</div>

													<div v-else-if="isBuilderTableIn('irrigation') || isBuilderTableIn('irrWaterStressSources') || isBuilderTableIn('irrWaterStressRes') || isBuilderTableIn('irrWaterStressAqu')">
														<v-table class="table-editor" density="compact">
															<thead>
																<tr class="bg-surface">
																	<th colspan="2" class="bg-secondary-tonal">Conditions to trigger table</th>
																</tr>
															</thead>
															<tbody>
																<tr v-for="cond in validIrrigationConditions" :key="cond.id">
																	<td class="field">
																		<v-select v-if="['aqu', 'res', 'cha'].includes(cond.obj)" hide-details
																			v-model="cond.obj_num" label="Select..."
																			:items="cond.obj === 'aqu' ? data.aquifers : (cond.obj === 'res' ? data.reservoirs : data.channels)"
																			@update:model-value="setActionObjNumFromCond(cond.obj_num,cond.obj)"></v-select>
																		<v-text-field density="compact" :rules="[constants.formRules.required]" v-model.number="cond.lim_const" type="number" step="any" hide-details="auto"></v-text-field>
																	</td>
																	<td>
																		{{cond.description}}
																		<div class="text-error" v-if="cond.obj === 'res' && data.reservoirs.length < 1">
																			Your project does not contain any reservoirs. You should select a different table.
																		</div>
																	</td>
																</tr>
															</tbody>
														</v-table>

														<v-table class="table-editor" density="compact" v-for="act in validIrrigationActions" :key="act.id">
															<thead>
																<tr class="bg-surface">
																	<th colspan="2" class="bg-secondary-tonal">{{act.obj === 'aqu' ? 'Aquifer' : (act.obj === 'res' ? 'Reservoir' : (act.obj === 'cha' ? 'Channel' : 'Unlimited'))}} source action values</th>
																</tr>
															</thead>
															<tbody>
																<tr v-if="['aqu', 'res', 'cha'].includes(act.obj)">
																	<td class="field">
																		<v-select v-model="act.obj_num" label="Select..." hide-details
																			:items="act.obj === 'aqu' ? data.aquifers : (act.obj === 'res' ? data.reservoirs : data.channels)">
																		</v-select>
																	</td>
																	<td>
																		{{act.obj === 'aqu' ? 'aquifer' : (act.obj === 'res' ? 'reservoir' : 'channel')}}
																		<div class="text-danger" v-if="act.obj === 'res' && data.reservoirs.length < 1">
																			Your project does not contain any reservoirs. You should select a different table.
																		</div>
																	</td>
																</tr>
																<tr>
																	<td class="field">
																		<v-text-field density="compact" :rules="[constants.formRules.required]" v-model.number="act.const" type="number" step="any" hide-details="auto"></v-text-field>
																	</td>
																	<td>irrigation amount (mm)</td>
																</tr>
																<tr>
																	<td class="field">
																		<v-text-field density="compact" :rules="[constants.formRules.required]" v-model.number="act.const2" type="number" step="any" hide-details="auto"></v-text-field>
																	</td>
																	<td>maximum times per year to irrigate using sprinkler</td>
																</tr>
															</tbody>
														</v-table>
													</div>

													<div v-else-if="isBuilderTableIn('fertilizer')">
														<v-table class="table-editor" density="compact">
															<thead>
																<tr class="bg-surface">
																	<th colspan="2" class="bg-secondary-tonal">Conditions to trigger table</th>
																</tr>
															</thead>
															<tbody>
																<tr v-for="cond in validFertilizerConditions" :key="cond.id">
																	<td class="field">
																		<v-text-field density="compact" :rules="[constants.formRules.required]" v-model.number="cond.lim_const" type="number" step="any" hide-details="auto"></v-text-field>
																	</td>
																	<td>{{cond.description}}</td>
																</tr>
															</tbody>
														</v-table>

														<v-table class="table-editor" density="compact" v-for="(act, a) in validFertilizerActions" :key="act.heading">
															<thead>
																<tr class="bg-surface">
																	<th colspan="2" class="bg-secondary-tonal">Action: {{act.heading}}</th>
																</tr>
															</thead>
															<tbody>
																<tr>
																	<td class="field">
																		<v-select v-model="act.action.option" :items="data.fertilizers" hide-details></v-select>
																	</td>
																	<td>
																		fertilizer
																		<reference-popup section="Databases / Fertilizer" help-file="fertilizer.frt" help-db="fertilizer_frt" api-url="db/fertilizer"></reference-popup>
																	</td>
																</tr>
																<tr>
																	<td class="field">
																		<v-text-field density="compact" :rules="[constants.formRules.required]" v-model.number="act.action.const" type="number" step="any" hide-details="auto"></v-text-field>
																	</td>
																	<td>fertilizer amount (kg/ha)</td>
																</tr>
																<tr>
																	<td class="field">
																		<v-text-field density="compact" :rules="[constants.formRules.required]" v-model.number="act.action.const2" type="number" step="any" hide-details="auto"></v-text-field>
																	</td>
																	<td>maximum times per year to fertilize</td>
																</tr>
																<tr>
																	<td class="field">
																		<v-select v-model="act.action.fp" :items="data.chem_apps" hide-details></v-select>
																	</td>
																	<td>
																		application
																		<reference-popup section="Operations / Chemical Applications" help-file="chem_app.ops" help-db="chem_app_ops" api-url="ops/chemapp"></reference-popup>
																	</td>
																</tr>
															</tbody>
														</v-table>
													</div>

													<div v-else-if="!formatters.isNullOrEmpty(data.builder.modal.op.table)">
														<v-table class="table-editor" density="compact">
															<thead>
																<tr class="bg-surface">
																	<th colspan="2" class="bg-secondary-tonal">Conditions to trigger table</th>
																</tr>
															</thead>
															<tbody>
																<tr v-for="cond in data.builder.modal.op.table.conditions" :key="cond.id">
																	<td class="field">
																		<v-text-field density="compact" :rules="[constants.formRules.required]" v-model.number="cond.lim_const" type="number" step="any" hide-details="auto"></v-text-field>
																	</td>
																	<td>{{cond.description}}</td>
																</tr>
															</tbody>
														</v-table>
													</div>
												</div>
											</div>
										</v-card-text>
										<v-divider></v-divider>
										<v-card-actions>
											<v-btn v-if="formatters.isNullOrEmpty(data.builder.modal.error) && !formatters.isNullOrEmpty(data.builder.modal.op.name) && data.builder.modal.op.name.startsWith('pl_hv_') && !data.builder.modal.op.saveAsNew" 
												type="button" color="primary" variant="text" @click="saveBuilderTable(true)" 
												:loading="data.builder.modal.saving" :disabled="data.builder.modal.saving">
												Save
											</v-btn>
											<v-btn v-else-if="formatters.isNullOrEmpty(data.builder.modal.error)" color="primary" variant="text" :disabled="data.builder.modal.saving">
												Save...
												<v-menu activator="parent">
													<v-list>
														<v-list-item @click="saveBuilderTable(true)">Save changes for all uses of this table</v-list-item>
														<v-list-item @click="saveBuilderTable(false)">Save changes for only this schedule (makes a new copy)</v-list-item>
													</v-list>
												</v-menu>
											</v-btn>
											<v-btn @click="cancelBuilderTable">Cancel</v-btn>
										</v-card-actions>
									</v-card>
								</v-dialog>
							</div>
						</v-window-item>

						<v-window-item :value="1">
							<p>
								For most users we recommend using the schedule builder tab to select from decision tables
								built and tested by the model team. Advanced users can select automatic schedules below or enter 
								manual operations.
							</p>

							<v-row>
								<v-col cols="12" md="5">
									<h3 class="text-h5 mb-3">Automatic schedules</h3>

									<div v-if="page.form.auto_ops.length > 0">
										<div>
											<ul class="list-group">
												<li class="list-group-item bg-light d-flex justify-content-between align-items-center" v-for="element in page.form.auto_ops" :key="element.name">
													<a @click.prevent="goToAutoOp(element.name)"><font-awesome-icon :icon="['fas', 'edit']" class="mr-2 text-primary pointer" :title="constants.commonMessages.leaveWarning" /></a>
													<div>{{element.name}} {{autoOpPlantLabel(element)}}</div>
													<a @click.prevent="removeAutoOp(element)" class="ml-auto"><font-awesome-icon :icon="['fas', 'times']" class="text-error pointer" title="Delete" /></a>
												</li>
											</ul>
										</div>
									</div>

									<v-divider class="mt-6 mb-4"></v-divider>

									<div class="form-group mb-0">
										<auto-complete label="Add an automatic schedule"
											v-model="data.new_auto_op.name" :value="data.new_auto_op.name"
											table-name="lum.dtl"
											section="Decision Tables / Land Use Management" help-file="lum.dtl" help-db="d_table_dtl"
											api-url="decision_table/tables/lum.dtl"></auto-complete>
									</div>
									<div class="mb-4">
										<v-btn variant="flat" color="primary" class="wide ml-1" :disabled="formatters.isNullOrEmpty(data.new_auto_op.name)" @click="addAutoOp">Add</v-btn>
									</div>
									
									<v-dialog v-model="page.reservedTableModal.show" :max-width="constants.dialogSizes.lg" persistent>
										<v-card :title="'Specify plant for ' + data.new_auto_op.name">
											<v-card-text>
												<error-alert :text="page.reservedTableModal.error"></error-alert>

												<div class="form-group mb-0">
													<auto-complete label="Plant"
														v-model="data.new_auto_op.plant1" :value="data.new_auto_op.plant1"
														table-name="plant" route-name="PlantsEdit"
														section="Databases / Plants" help-file="plants.plt" help-db="plants_plt"
														api-url="db/plants"></auto-complete>
												</div>

												<div class="form-group mb-0" v-if="data.new_auto_op.name === data.reserved_d_tables.summer2">
													<auto-complete label="Plant 2"
														v-model="data.new_auto_op.plant2" :value="data.new_auto_op.plant2"
														table-name="plant" route-name="PlantsEdit"
														section="Databases / Plants" help-file="plants.plt" help-db="plants_plt"
														api-url="db/plants"></auto-complete>
												</div>
											</v-card-text>
											<v-divider></v-divider>
											<v-card-actions>
												<v-btn type="button" color="primary" variant="text" @click="addReservedAutoOp">
													Save
												</v-btn>
												<v-btn @click="cancelReservedAutoOp">Cancel</v-btn>
											</v-card-actions>
										</v-card>
									</v-dialog>
								</v-col>

								<v-col cols="12" md="6" offset-md="1">
									<h3 class="text-h5 mb-3">Operations</h3>

									<div v-if="page.form.operations.length > 0">				
										<v-table class="data-table">
											<thead>
												<tr class="bg-surface">
													<th class="bg-secondary-tonal min"></th>
													<th class="bg-secondary-tonal">Operation</th>
													<th class="bg-secondary-tonal">Year</th>
													<th class="bg-secondary-tonal">Month</th>
													<th class="bg-secondary-tonal">Day</th>
													<th class="bg-secondary-tonal" title="Heat Units">HU</th>
													<th class="bg-secondary-tonal" colspan="3">Data</th>
													<th class="bg-secondary-tonal min"></th>
												</tr>
											</thead>
											<tbody>
												<tr v-for="(op, i) in sortedOperations" :key="i">
													<td><a @click.prevent="editOp(op)"><font-awesome-icon :icon="['fas', 'edit']" class="text-primary pointer" title="Edit" /></a></td>
													<td>{{op.op_typ}}</td>
													<td>{{op.order}}</td>
													<td>{{op.mon}}</td>
													<td>{{op.day}}</td>
													<td>{{op.hu_sch}}</td>
													<td>{{op.op_data1}}</td>
													<td>{{op.op_data2}}</td>
													<td>{{op.op_data3}}</td>
													<td><a @click.prevent="removeOp(op)"><font-awesome-icon :icon="['fas', 'times']" class="text-error pointer" title="Delete" /></a></td>
												</tr>
											</tbody>
										</v-table>

										<p>
											Operation sorting is done by year of rotation followed by heat units, then month/day if heat units = 0.
										</p>
									</div>
									<div>
										<v-btn variant="flat" color="primary" @click="addOp">Add an operation</v-btn>
									</div>

									<v-dialog v-model="page.modal.show" :max-width="constants.dialogSizes.lg" persistent>
										<v-card :title="(page.modal.new ? 'Add' : 'Edit') + ' Operation'">
											<v-card-text>
												<error-alert :text="page.modal.error"></error-alert>

												<div>
													<v-select label="Operation" v-model="page.modal.operation.op_typ" :items="data.op_codes" 
														item-title="text" item-value="value"
														@update:model-value="changeOp"></v-select>
												</div>

												<v-divider class="my-3"></v-divider>

												<div>
													Operations can be scheduled by month/day or heat units. If no month/day, heat units should be > 0. 
												</div>

												<div v-if="page.modal.operation.op_typ == 'skip'">
													In order to sort your skip operation properly, enter a month/day or heat units accordingly. These values are not used in the model for skips and are for sorting only.
												</div>

												<v-row>
													<v-col cols="12" md="3">
														<v-text-field label="Year of Rotation" v-model.number="page.modal.operation.order" type="number"></v-text-field>
													</v-col>
													<v-col cols="12" md="3">
														<v-select label="Month" v-model="page.modal.operation.mon" :items="data.months"></v-select>
													</v-col>
													<v-col cols="12" md="3">
														<v-select label="Day" v-model="page.modal.operation.day" :items="data.days"></v-select>
													</v-col>
													<v-col cols="12" md="3">
														<v-text-field label="Heat Units Fraction" v-model.number="page.modal.operation.hu_sch" type="number" step="any" min="0" max="1"></v-text-field>
													</v-col>
												</v-row>

												<v-divider class="my-3"></v-divider>

												<v-row v-if="page.modal.operation.op_typ != 'prtp' && page.modal.operation.op_typ != 'skip'">
													<v-col cols="12" md="6">
														<div class="form-group mb-0">
															<auto-complete :label="data.op_data1.label"
																v-model="page.modal.operation.op_data1" :value="page.modal.operation.op_data1"
																:table-name="getNamesOpData1()"
																:section="data.op_data1.section" :help-file="data.op_data1.file" :help-db="data.op_data1.db"
																:api-url="getApiUrlOpData1()"></auto-complete>
														</div>
													</v-col>
													<v-col cols="12" md="6" v-if="page.modal.operation.op_typ == 'harv' || page.modal.operation.op_typ == 'hvkl' || page.modal.operation.op_typ == 'fert' || page.modal.operation.op_typ == 'pest'">
														<div class="form-group mb-0">
															<auto-complete :label="data.op_data2.label"
																v-model="page.modal.operation.op_data2" :value="page.modal.operation.op_data2"
																:table-name="getNamesOpData2()"
																:section="data.op_data2.section" :help-file="data.op_data2.file" :help-db="data.op_data2.db"
																:api-url="getApiUrlOpData2()"></auto-complete>
														</div>
													</v-col>
													<v-col cols="12" md="6" v-if="data.has_op_data3.includes(page.modal.operation.op_typ)">
														<v-text-field :label="opData3Label" v-model.number="page.modal.operation.op_data3" type="number" step="any"></v-text-field>
													</v-col>
												</v-row>
											</v-card-text>
											<v-divider></v-divider>
											<v-card-actions>
												<v-btn type="button" color="primary" variant="text" @click="saveOp" :disabled="page.modal.saving" :loading="page.modal.saving">
													Save
												</v-btn>
												<v-btn @click="cancel">Cancel</v-btn>
											</v-card-actions>
										</v-card>
									</v-dialog>
								</v-col>
							</v-row>
						</v-window-item>
					</v-window>
				</v-card-item>
			</v-card>

			<action-bar>
				<v-btn type="submit" :loading="page.saving" variant="flat" color="primary" class="mr-2">Save Changes</v-btn>
				<back-button></back-button>
			</action-bar>
		</v-form>
	</div>
</template>

<style>
	.list-group-item {
		cursor: pointer;
	}
</style>
