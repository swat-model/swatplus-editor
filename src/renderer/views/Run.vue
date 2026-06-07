<script setup lang="ts">
import { reactive, computed, onMounted, onUnmounted, watch } from 'vue';
import { useRoute } from 'vue-router';
import { useHelpers } from '@/helpers';
import { storeToRefs } from 'pinia';
import {useTaskStore} from '@/store/task';
import SwatPlusToolboxButton from '../components/SwatPlusToolboxButton.vue';
import SwatPlusIahrisButton from '../components/SwatPlusIahrisButton.vue';
import moment from 'moment';

const route = useRoute();
const taskStore = useTaskStore();
const { task } = storeToRefs(taskStore);
const { api, constants, errors, formatters, currentProject, runProcess, utilities } = useHelpers();

const requiredForCheckMessage = 'Some smaller output files are used in SWAT+ Check and unselecting them is disabled.'

let data: any = reactive({
	page: {
		loading: false,
		error: null,
		validated: false,
		submitted: false,
		saving: false,
		saveError: null,
		run: {
			show: false
		},
		completed: {
			show: false
		},
		saveScenario: {
			show: false,
			name: null,
			error: null
		},
		savedScenario: {
			show: false
		},
		inputs: {
			show: false,
			maxCols: 20
		},
		forceRerunForOutput: false,
		outputSkip: {
			show: false,
			files: ''
		},
		exeCustomization: {
			show: false
		},
	},
	hasImportedWeather: false,
	hasObservedWeather: false,
	config: {
		swat_last_run: null,
		input_files_dir: null,
		input_files_last_written: null,
		swat_exe_filename: null
	},
	timeDisplay: {
		startDate: null,
		endDate: null
	},
	time: {
		day_start: 0,
		yrc_start: 1980,
		day_end: 0,
		yrc_end: 1985,
		step: 0
	},
	printDisplay: {
		startDate: null,
		endDate: null
	},
	print: {
		prt: {
			nyskip: 1,
			day_start: 0,
			yrc_start: 0,
			day_end: 0,
			yrc_end: 0,
			interval: 1,
			crop_yld: false,
			mgtout: false,
			hydcon: false,
			fdcout: false,
			csvout: false
		},
		objects: []
	},
	file_cio: [],
	inputs: {
		ignore_files: [],
		ignore_cio_files: [],
		custom_cio_files: []
	},
	check: {
		required_tables: [],
		opt_tables: []
	},
	options: {
		timeSteps: [
			{ value: 0, title: 'Daily' },
			{ value: 1, title: 'Increment' },
			{ value: 24, title: 'Hourly' },
			{ value: 96, title: '15 Minutes' },
			{ value: 1440, title: '1 Minute' }
		],
		printAll: {
			daily: false,
			monthly: false,
			yearly: false,
			avann: false
		},
		cropYldFiles: [
			{ value: 'b', title: 'Print both yearly and average annual files (recommended)' },
			{ value: 'y', title: 'Print yearly file only' },
			{ value: 'n', title: 'Do not print' }
		]
	},
	// task: {
	// 	progress: {
	// 		percent: 0,
	// 		message: null
	// 	},
	// 	process: null,
	// 	error: null,
	// 	running: false,
	// 	modelMessages: [],
	// 	modelYear: -1,
	// 	currentPids: [],
	// 	killMode: true,
	// 	hasCorrectOutput: false,
	// },
	status: {
		inputs: false,
		model: false,
		output: false,
		saveScenario: false
	},
	selection: {
		inputs: true,
		model: true,
		output: true,
		exeFile: '',
		swatCheckOnly: false
	},
	printGroups: {
		model: {
			'channel': 'Channel',
			'channel_sd': 'Channel',
			'aquifer': 'Aquifer',
			'reservoir': 'Reservoir',
			'recall': 'Point Source (Recall)',
			'ru': 'Routing Unit',
			'hyd': 'Hydrology',
			'water_allo': 'Water Allocation'
		},
		modelBasin: {
			'basin_cha': 'Channel',
			'basin_sd_cha': 'Channel',
			'basin_aqu': 'Aquifer',
			'basin_res': 'Reservoir',
			'basin_psc': 'Point Source (Recall)'
		},
		modelRegion: {
			'region_sd_cha': 'Channel',
			'region_aqu': 'Aquifer',
			'region_res': 'Reservoir',
			'region_psc': 'Point Source (Recall)'
		},
		nutrients: {
			'basin_nb': 'Basin',
			'lsunit_nb': 'Landscape Unit',
			'hru_nb': 'HRU',
			'hru-lte_nb': 'HRU-LTE',
			'region_nb': 'Region',
		},
		water: {
			'basin_wb': 'Basin',
			'lsunit_wb': 'Landscape Unit',
			'hru_wb': 'HRU',
			'hru-lte_wb': 'HRU-LTE',
			'region_wb': 'Region',
		},
		plant: {
			'basin_pw': 'Basin',
			'lsunit_pw': 'Landscape Unit',
			'hru_pw': 'HRU',
			'hru-lte_pw': 'HRU-LTE',
			'region_pw': 'Region',
		},
		losses: {
			'basin_ls': 'Basin',
			'lsunit_ls': 'Landscape Unit',
			'hru_ls': 'HRU',
			'hru-lte_ls': 'HRU-LTE',
			'region_ls': 'Region',
		},
		salts: {
			'basin_salt': 'Basin',
			'hru_salt': 'HRU',
			'ru_salt': 'Routing Unit',
			'aqu_salt': 'Aquifer',
			'channel_salt': 'Channel',
			'res_salt': 'Reservoir',
			'wetland_salt': 'Wetland',
		},
		cs: {
			'basin_cs': 'Basin',
			'hru_cs': 'HRU',
			'ru_cs': 'Routing Unit',
			'aqu_cs': 'Aquifer',
			'channel_cs': 'Channel',
			'res_cs': 'Reservoir',
			'wetland_cs': 'Wetland',
		}
	},
	printConfig: {
		inactive: [
			'region_wb',
			'region_nb',
			'region_ls',
			'region_pw',
			'region_aqu',
			'region_res',
			'region_cha',
			'region_sd_cha',
			'region_psc',
			'basin_cha',
			'channel'
		],
		hru: ['hru_wb', 'hru_nb', 'hru_ls', 'hru_pw'],
		hru_lte: ['hru-lte_wb', 'hru-lte_nb', 'hru-lte_ls', 'hru-lte_pw'],
		showInactive: false,
		changedObjects: []
	},
	exeOptions: [
		{ fileName: '', description: '', isDefault: true }
	]
});

let modelIssues: any = reactive({
	wgn: {
		is_invalid: false,
		data: <any[]>[],
		error: <string | null>null,
		saving: false
	}
});

async function validateWgn() {
	modelIssues.wgn.loading = true;
	modelIssues.wgn.error = null;

	try {
		const response = await api.get(`climate/wgn/validate`, currentProject.getApiHeader());
		errors.log(response.data);
		modelIssues.wgn.is_invalid = response.data.is_invalid;
		modelIssues.wgn.data = response.data.data;
	} catch (error) {
		modelIssues.wgn.error = errors.logError(error, 'Unable to get project information from database.');
	}

	modelIssues.wgn.loading = false;
}

const noneSelected = computed(() => {
	return !(data.selection.inputs || data.selection.model || data.selection.output);
});

const totalProgress = computed(() => {
	// if (!data.task.running) return 0;
	if (!task.value.running) return 0;

	let numTasks = 3;
	let eachTaskPer = 100 / numTasks;
	let thisTaskPer = eachTaskPer * task.value.progress.percent / 100;
	if (data.status.inputs) return thisTaskPer;
	if (data.status.model) return eachTaskPer + thisTaskPer;
	if (data.status.output) return eachTaskPer * 2 + thisTaskPer;

	return 0;
});

const modalTitle = computed(() => {
	if (data.status.inputs) return 'Menulis File Input SWAT+';
	else if (data.status.model) return `Running SWAT+ ${selectedExeDescription.value}`;
	else if (data.status.output) return 'Membaca File Output SWAT+';
	return 'Running SWAT+';
})

const errorTitle = computed(() => {
	if (data.status.inputs) return 'Terjadi kesalahan saat menulis file input Anda.';
	else if (data.status.output) return 'Terjadi kesalahan saat memproses file output Anda.';
	return 'SWAT+ Editor mengalami kesalahan.';
})

const currentResultsPath = computed(() => {
	return runProcess.resultsPath(data.config.input_files_dir);
});

const newScenarioPath = computed(() => {
	if (formatters.isNullOrEmpty(data.page.saveScenario.name)) return '';
	let scenPath = utilities.joinPaths([currentProject.projectPath, 'Scenarios']);
	return utilities.joinPaths([scenPath, formatters.toValidFileName(data.page.saveScenario.name)]);
});

const selectedExeDescription = computed(() => {
	let selected = data.exeOptions.find((x: any) => x.fileName === data.selection.exeFile);
	if (selected) return selected.description.split('(')[0].trim();
	return '';
});

async function refreshExeOptions() {
	data.exeOptions = await runProcess.getSwatExeOptions();
	if (data.exeOptions === null || data.exeOptions.length === 0) {
		data.page.error = 'Tidak ditemukan opsi eksekusi SWAT+. Ada kemungkinan instalasi Anda rusak. Silakan coba instal ulang aplikasi.';
	}

	if (!data.exeOptions.some((x: any) => x.fileName === data.selection.exeFile)) {
		data.selection.exeFile = data.exeOptions.find((x: any) => x.fileName === data.config.swat_exe_filename)?.fileName
			|| data.exeOptions.find((x: any) => x.isDefault)?.fileName || data.exeOptions[0]?.fileName || '';
	}
}

async function get() {

	if (!currentProject.projectDb || currentProject.projectDb === null) {
        console.log("API request aborted: projectDb is not loaded yet.");
        return;
    }

	data.page.loading = true;
	data.page.error = null;

	try {
		const response = await api.get(`setup/run-settings`, currentProject.getApiHeader());
		errors.log(response.data);
		data.config = response.data.config;
		data.time = response.data.time;
		data.print = response.data.print;
		data.hasImportedWeather = response.data.imported_weather;
		data.hasObservedWeather = response.data.has_observed_weather;
		data.file_cio = response.data.file_cio;
		data.inputs = response.data.inputs;
		data.check = response.data.check;

		data.exeOptions = await runProcess.getSwatExeOptions();
		if (data.exeOptions === null || data.exeOptions.length === 0) {
			throw new Error('Tidak ditemukan opsi eksekusi SWAT+. Ada kemungkinan instalasi Anda rusak. Silakan coba instal ulang aplikasi.');
		}
		data.selection.exeFile = data.exeOptions.find((x: any) => x.fileName === data.config.swat_exe_filename)?.fileName
			|| data.exeOptions.find((x: any) => x.isDefault)?.fileName || data.exeOptions[0]?.fileName || '';

		data.page.forceRerunForOutput = false;
		if (!response.data.print.prt.csvout && !formatters.isNullOrEmpty(response.data.config.swat_last_run)) {
			data.page.forceRerunForOutput = true;
		}
		data.print.prt.csvout = true;

		let cols = 0;
		for (let cat of data.file_cio) {
			if (cat.files.length > cols) cols = cat.files.length;
		}
		data.page.inputs.maxCols = cols;

		data.timeDisplay.startDate = getDateStringFromTime(data.time.day_start, data.time.yrc_start);
		data.timeDisplay.endDate = getDateStringFromTime(data.time.day_end, data.time.yrc_end, true);
		data.printDisplay.startDate = getDateStringFromTime(data.print.prt.day_start, data.print.prt.yrc_start);
		data.printDisplay.endDate = getDateStringFromTime(data.print.prt.day_end, data.print.prt.yrc_end, true);

		if (currentProject.isLte) {
			data.printConfig.inactive = data.printConfig.inactive.concat(data.printConfig.hru);
		} else {
			data.printConfig.inactive = data.printConfig.inactive.concat(data.printConfig.hru_lte);
		}

		if (formatters.isNullOrEmpty(data.config.input_files_dir)) {
			data.config.input_files_dir = currentProject.txtInOutPath;
		}

		await validateWgn();
	} catch (error) {
		data.page.error = errors.logError(error, 'Tidak dapat memperoleh informasi proyek dari basis data.');
	}

	data.page.loading = false;
}

onMounted(async () => {
	data.page.loading = true;
	// initRunProcessHandlers();
	await get();
	data.page.loading = false;
});

onUnmounted(() => {
	if (taskStore.task.running) {
        taskStore.cancelTask();
    }
});

watch(() => route.path, async () => await get())

async function runSelected() {
	data.page.saving = true;
	data.page.saveError = null;
	data.page.showError = false;
	data.page.submitted = true;
	task.value.killMode = false;
	task.value.hasCorrectOutput = false;

	if (noneSelected.value) {
		data.page.saveError = 'Silakan pilih setidaknya satu tugas untuk dijalankan';
	} else {
		try {
			let startTimeUpdate = getDayYearFromDateString(data.timeDisplay.startDate);
			let endTimeUpdate = getDayYearFromDateString(data.timeDisplay.endDate, true);
			data.time.day_start = startTimeUpdate.day;
			data.time.yrc_start = startTimeUpdate.year;
			data.time.day_end = endTimeUpdate.day;
			data.time.yrc_end = endTimeUpdate.year;

			let startPrintUpdate = getDayYearFromDateString(data.printDisplay.startDate);
			let endPrintUpdate = getDayYearFromDateString(data.printDisplay.endDate, true);
			data.print.prt.day_start = startPrintUpdate.day;
			data.print.prt.yrc_start = startPrintUpdate.year;
			data.print.prt.day_end = endPrintUpdate.day;
			data.print.prt.yrc_end = endPrintUpdate.year;

			currentProject.setSwatVersion(selectedExeDescription.value);
			utilities.pushRecentProject(currentProject.getObject());
			utilities.setWindowTitle();

			let infoData = {
				input_files_dir: data.config.input_files_dir.replace(/\\/g, "/"),
				swat_exe_filename: data.selection.exeFile,
				time: data.time,
				print: data.print.prt,
				print_objects: data.print.objects,
				inputs: data.inputs
			};
			await api.put(`setup/run-settings`, infoData, currentProject.getApiHeader());
			data.page.validated = false;

			if (data.selection.inputs) {
				data.page.run.show = true;
				runInputs();
			} else if (data.selection.model) {
				if (formatters.isNullOrEmpty(data.config.input_files_last_written))
					data.page.saveError = 'Anda harus menulis file input sebelum menjalankan model.';
				else {
					data.page.run.show = true;
					runModel();
				}
			} else if (data.selection.output) {
				if (formatters.isNullOrEmpty(data.config.swat_last_run))
					data.page.saveError = 'Anda harus menjalankan SWAT+ sebelum menganalisis output.';
				else {
					data.page.run.show = true;
					runOutput();
				}
			}
		} catch (error) {
			console.log(error);
			data.page.saveError = errors.logError(error, 'Tidak dapat memperbarui direktori file input.');
		}
	}

	data.page.saving = false;
	data.page.submitted = false;
	data.page.showError = data.page.saveError !== null;
}

// function runInputs() {
// 	data.status.inputs = true;
// 	data.status.model = false;
// 	data.status.output = false;
// 	data.status.saveScenario = false;

// 	let args = [
// 		'write_files',
// 		'--project_db_file=' + currentProject.projectDb,
// 		'--swat_version=' + selectedExeDescription.value
// 	];

// 	if (data.inputs.ignore_files.length > 0) args.push(`--ignore_files=${data.inputs.ignore_files.join(',')}`);
// 	if (data.inputs.ignore_cio_files.length > 0) args.push(`--ignore_cio_files=${data.inputs.ignore_cio_files.join(',')}`);
// 	if (data.inputs.custom_cio_files.length > 0) args.push(`--custom_cio_files=${data.inputs.custom_cio_files.join(',')}`);

// 	taskStore.runTask(args, { 
//         proc_name: 'runmodel', 
//         script_name: 'swatplus_api',
// 		routePath: route.path
//    	}, () => {
//         // Logika workflow dipindahkan ke sini
//         if (data.status.inputs && data.selection.model) {
//             runModel(); 
//         } else {
//             // Logika penyelesaian akhir
//             data.page.completed.show = true;
//         }
// 	});
// }
function runInputs() {
	// 1. Atur status indikator pemrosesan UI lokal
	data.status.inputs = true;
	data.status.model = false;
	data.status.output = false;
	data.status.saveScenario = false;

	// 2. Susun argumen CLI untuk dikirim ke skrip Python API
	let args = [
		'write_files',
		'--project_db_file=' + currentProject.projectDb,
		'--swat_version=' + selectedExeDescription.value
	];

	if (data.inputs.ignore_files.length > 0) args.push(`--ignore_files=${data.inputs.ignore_files.join(',')}`);
	if (data.inputs.ignore_cio_files.length > 0) args.push(`--ignore_cio_files=${data.inputs.ignore_cio_files.join(',')}`);
	if (data.inputs.custom_cio_files.length > 0) args.push(`--custom_cio_files=${data.inputs.custom_cio_files.join(',')}`);

	// 3. Jalankan melalui taskStore dengan menyisipkan alur Callback Pipeline
	taskStore.runTask(args, { 
		proc_name: 'runmodel', 
		script_name: 'swatplus_api',
		routePath: route.path,
		project: currentProject
	}, async () => { // Gunakan async karena di dalam 'else' kita memanggil 'await get()'
		errors.log('Done inputs');

		// --- LOGIKA PIPELINE SEKUENSIAL (PENGGANTI LISTENERS.CLOSE ASLI) ---
		
		if (data.selection.model) {
			// Jika pengguna mencentang "Run Model", langsung oper ke tahap berikutnya
			errors.log('Lanjut ke run model...');
			runModel(); 
		} else if (data.selection.output) {
			// Jika model dilewati tetapi pengguna mencentang "Read Output"
			errors.log('Model dilewati, langsung membaca output...');
			runOutput();
		} else {
			// Jika HANYA menulis file input saja tanpa kelanjutan tugas lain
			errors.log('Semua tugas selesai dijalankan.');
			
			taskStore.task.running = false; // Matikan loading state di store
			closeTaskModals();              // Tutup modal popup pemrosesan
			await get();                    // Refresh data komponen agar tanggal "Last Written" terbarui
			data.page.completed.show = true; // Tampilkan dialog sukses selesai
			taskStore.task.currentPids = []; // Bersihkan sisa PID dari memori store
		}
	});
}

// function runModel() {
// 	if (task.value.killMode) return;
// 	data.status.inputs = false;
// 	data.status.model = true;
// 	data.status.output = false;
// 	data.status.saveScenario = false;

// 	// runTask(true, null, data.config.input_files_dir, data.selection.exeFile);
// 	taskStore.runSwatTask(
//         data.config.input_files_dir, 
//         data.selection.exeFile,
// 		{ project: currentProject, routePath: route.path },
//         () => {
//             // LOGIKA WORKFLOW SETELAH SWAT SELESAI
//             if (data.selection.output) {
//                 runOutput(); // Panggil fungsi runOutput yang sudah ada di Run.vue
//             } else {
//                 // Selesaikan semua proses
//                 task.value.running = false;
//                 closeTaskModals();
//                 data.page.completed.show = true;
//                 // ... update data/get API lainnya
//             }
//         }
//     );
// }

function runModel() {
	if (task.value.killMode) return;
	data.status.inputs = false;
	data.status.model = true;
	data.status.output = false;
	data.status.saveScenario = false;

	taskStore.runSwatTask(
        data.config.input_files_dir, 
        data.selection.exeFile,
		{ project: currentProject, routePath: route.path, timeStart: data.time.yrc_start, timeEnd: data.time.yrc_end },
        async () => { // Tambahkan async di sini
            errors.log('Done model');
            
            try {
                // WAJIB: Simpan status keberhasilan simulasi model ke database
                await api.put(`setup/save-model-run`, {}, currentProject.getApiHeader());
            } catch (err) {
                console.error("Gagal menyimpan riwayat run model ke DB:", err);
            }

            // Lanjut ke langkah berikutnya
            if (data.selection.output) {
                runOutput(); 
            } else {
                task.value.running = false;
                closeTaskModals();
                await get(); // Selalu refresh data lokal agar UI sinkron
                data.page.completed.show = true;
            }
        }
    );
}

// function runOutput() {
// 	if (task.value.killMode) return;
// 	data.status.inputs = false;
// 	data.status.model = false;
// 	data.status.output = true;
// 	data.status.saveScenario = false;

// 	let args = [
// 		'read_output',
// 		'--output_files_dir=' + data.config.input_files_dir.replace(/\\/g, "/"),
// 		'--output_db_file=' + runProcess.outputDbPath(data.config.input_files_dir),
// 		'--swat_version=' + selectedExeDescription.value,
// 		'--editor_version=' + constants.appSettings.version,
// 		'--project_name=' + currentProject.name,
// 		'--only_read_swatcheck=' + (data.selection.swatCheckOnly ? 'y' : 'n')
// 	];

// 	if (!formatters.isNullOrEmpty(data.page.outputSkip.files)) {
// 		args.push(`--skip_files=${data.page.outputSkip.files}`);
// 	}

// 	taskStore.runTask(args, {
//         proc_name: 'runmodel', // Tetap gunakan proc_name yang sesuai agar listener menangkap output
//         script_name: 'swatplus_api',
//         project: currentProject,
//         routePath: route.path
//     }, async () => {
//         // --- LOGIKA WORKFLOW SETELAH READ_OUTPUT SELESAI ---
//         errors.log('Done output');
        
//         // Simpan status output ke database
//         await api.put(`setup/save-output-read`, {}, currentProject.getApiHeader());
        
//         // Reset state dan tampilkan hasil
//         task.value.running = false;
//         closeTaskModals();
//         await get(); // Refresh data
//         data.page.completed.show = true;
//         task.value.currentPids = [];
//     });
// }

function runOutput() {
	if (task.value.killMode) return;
	data.status.inputs = false;
	data.status.model = false;
	data.status.output = true;
	data.status.saveScenario = false;

	let args = [
		'read_output',
		'--output_files_dir=' + data.config.input_files_dir.replace(/\\/g, "/"),
		'--output_db_file=' + runProcess.outputDbPath(data.config.input_files_dir),
		'--swat_version=' + selectedExeDescription.value,
		'--editor_version=' + constants.appSettings.version,
		'--project_name=' + currentProject.name,
		'--only_read_swatcheck=' + (data.selection.swatCheckOnly ? 'y' : 'n')
	];

	if (!formatters.isNullOrEmpty(data.page.outputSkip.files)) {
		args.push(`--skip_files=${data.page.outputSkip.files}`);
	}

	taskStore.runTask(args, {
		proc_name: 'runmodel', 
		script_name: 'swatplus_api',
		project: currentProject,
		routePath: route.path
	}, async () => {
		// --- LOGIKA WORKFLOW SETELAH READ_OUTPUT SELESAI ---
		errors.log('Done output');
		
		try {
			// Simpan status output ke database melalui API HTTP
			await api.put(`setup/save-output-read`, {}, currentProject.getApiHeader());
		} catch (err) {
			console.error("Gagal menyimpan status output read ke database:", err);
		}
		
		// Reset state internal store terlebih dahulu
		task.value.running = false;
		task.value.currentPids = [];

		// Jalankan fungsi refresh data & manipulasi UI lokal di Run.vue
		closeTaskModals();
		await get(); // Refresh data halaman Run
		data.page.completed.show = true;
	});
}


function saveScenario() {
	data.page.saveScenario.error = null;

	if (formatters.isNullOrEmpty(data.page.saveScenario.name)) {
		data.page.saveScenario.error = 'Silakan masukkan nama untuk scenario.';
	} else {
		data.status.inputs = false;
		data.status.model = false;
		data.status.output = false;
		data.status.saveScenario = true;

		let args = [
			'save_scenario',
			'--project_db_file=' + currentProject.projectDb,
			'--input_files_dir=' + data.config.input_files_dir,
			'--output_files_dir=' + currentResultsPath.value,
			'--project_name=' + formatters.toValidFileName(data.page.saveScenario.name)
		];

		taskStore.runTask(args, {
            proc_name: 'runmodel', // Gunakan proc_name yang sesuai agar API menangani request ini
            script_name: 'swatplus_api',
            project: currentProject,
            routePath: route.path
        }, () => {
            // --- LOGIKA WORKFLOW SETELAH SAVE SELESAI ---
            task.value.running = false;
            closeTaskModals();
            
            // Tampilkan notifikasi bahwa skenario berhasil disimpan
            data.page.savedScenario.show = true;
            data.status.saveScenario = false;
            
            // Reset PID list
            task.value.currentPids = [];
        });
	}
}


function cancelTask() {
	taskStore.cancelTask();
    data.status.inputs = false;
	data.status.model = false;
	data.status.output = false;
	data.status.saveScenario = false;
    // Panggil fungsi UI lokal Anda untuk menutup modal
    closeTaskModals();
}

function closeTaskModals() {
	data.page.run.show = false;
	data.page.saveScenario.show = false;
}

function getDateStringFromTime(day: any, year: any, isEnd = false) {
	if (year === 0) return null;
	if (isEnd && day === 0) return `${year}-12-31`;
	let d = moment(`${year}-01-01`);
	if (day !== 0) d.add(day - 1, 'days');
	return d.format('YYYY-MM-DD');
}

function getDayYearFromDateString(value: any, isEnd = false) {
	if (formatters.isNullOrEmpty(value)) {
		return {
			day: 0,
			year: 0
		};
	}

	let d = moment(String(value));
	let day = d.dayOfYear();

	if (!isEnd && day === 1) day = 0;
	else if (isEnd && d.month() === 11 && d.date() === 31) day = 0;

	return {
		day: day,
		year: d.year()
	};
}

function checkAllDaily() {
	//data.options.printAll.daily = !data.options.printAll.daily;
	for (let i = 0; i < data.print.objects.length; i++) {
		data.print.objects[i].daily = data.options.printAll.daily;
		pushChg(i);
	}
}

function checkAllMonthly() {
	//data.options.printAll.monthly = !data.options.printAll.monthly;
	for (let i = 0; i < data.print.objects.length; i++) {
		data.print.objects[i].monthly = data.options.printAll.monthly;
		pushChg(i);
	}
}

function checkAllYearly() {
	//data.options.printAll.yearly = !data.options.printAll.yearly;
	for (let i = 0; i < data.print.objects.length; i++) {
		if (requiredForCheck(`${data.print.objects[i].name}_yr`)) continue;
		data.print.objects[i].yearly = data.options.printAll.yearly;
		pushChg(i);
	}
}

function checkAllAvann() {
	//data.options.printAll.avann = !data.options.printAll.avann;
	for (let i = 0; i < data.print.objects.length; i++) {
		if (requiredForCheck(`${data.print.objects[i].name}_aa`)) continue;
		data.print.objects[i].avann = data.options.printAll.avann;
		pushChg(i);
	}
}

function requiredForCheck(nameFormat: any) {
	return data.check.required_tables.includes(nameFormat) || data.check.opt_tables.includes(nameFormat);
}

function pushChg(i: number) {
	if (data.printConfig.changedObjects.indexOf(i) == -1) {
		data.printConfig.changedObjects.push(i);
	}
}

function printIndex(name: any) {
	return data.print.objects.findIndex((x: any) => { return x.name === name });
}

function inputCustomizationColor(name: any) {
	return data.inputs.ignore_files.includes(name) || data.inputs.ignore_cio_files.includes(name) || data.inputs.custom_cio_files.includes(name) ? 'primary' : undefined;
}

const outputLogFile = computed(() => {
	if (formatters.isNullOrEmpty(data.config.output_last_imported)) return null;
	if (formatters.isNullOrEmpty(data.config.input_files_dir)) return null;
	let f = utilities.joinPaths([data.config.input_files_dir, 'output_db_log.txt']);
	if (utilities.pathExists(f)) return f;
	return null;
});
</script>

<template>
	<project-container :loading="data.page.loading" add-error-frame>
		<v-main class="layout-fix">
			<div class="py-3 px-6">
				<div v-if="!data.hasImportedWeather">
					<h1 class="text-h5">Not ready to run the model</h1>

					<v-alert color="red" icon="$info" variant="tonal" border="start" class="my-4">
						Anda harus menambahkan generator dan stasiun cuaca sebelum menulis input dan menjalankan model.
					</v-alert>

					<v-btn to="/edit/climate/wgn" variant="flat" color="primary">Add Now</v-btn>
				</div>

				<v-form v-else @submit.prevent="runSelected">
					<error-alert as-popup v-model="data.page.showError" :show="data.page.showError"
						:text="data.page.saveError" :timeout="-1"></error-alert>

					<h1 class="text-h5 mb-6">Confirm Simulation Settings</h1>

					<v-expansion-panels variant="accordion">
						<v-expansion-panel>
							<v-expansion-panel-title>
								<v-row no-gutters>
									<v-col cols="12" md="4" class="d-flex justify-start font-weight-bold">Choose where
										to write your input files</v-col>
									<v-col cols="8"
										class="text-right pr-6 text-secondary d-none d-md-block">{{ data.config.input_files_dir }}</v-col>
								</v-row>
							</v-expansion-panel-title>
							<v-expansion-panel-text>
								<div class="mt-5">
									<select-folder-input v-model="data.config.input_files_dir"
										:value="data.config.input_files_dir" label="Directory to write your input files"
										required invalidFeedback="Please select a folder"></select-folder-input>
								</div>
								<div>
									<v-btn @click="data.page.inputs.show = true" variant="flat" class="border">Advanced:
										Customize files to write...</v-btn>
								</div>
							</v-expansion-panel-text>
						</v-expansion-panel>
						<v-expansion-panel>
							<v-expansion-panel-title>
								<v-row no-gutters>
									<v-col cols="12" md="4" class="d-flex justify-start font-weight-bold">Set your
										simulation period</v-col>
									<v-col cols="8"
										class="text-right pr-6 text-secondary d-none d-md-block">{{ data.time.yrc_start }}
										- {{ data.time.yrc_end }}</v-col>
								</v-row>
							</v-expansion-panel-title>
							<v-expansion-panel-text>
								<div class="mt-5">
									<p v-if="data.hasObservedWeather">
										Pastikan tanggal simulasi Anda berada dalam rentang tanggal yang tercantum dalam
										<router-link to="/edit/climate/stations" class="text-primary">observed weather
											files</router-link>.
										Tanggal simulasi di luar rentang ini akan menghasilkan simulasi cuaca.
									</p>

									<div class="form-group mb-5">
										<v-text-field v-model="data.timeDisplay.startDate"
											label="Starting date of simulation" required type="date"
											:hint="formatters.toDate(data.timeDisplay.startDate, 'MMMM D, YYYY') || ''"
											persistent-hint></v-text-field>
									</div>
									<div class="form-group">
										<v-text-field v-model="data.timeDisplay.endDate"
											label="Ending date of simulation" required type="date"
											:hint="formatters.toDate(data.timeDisplay.endDate, 'MMMM D, YYYY') || ''"
											persistent-hint></v-text-field>
									</div>

									<v-expansion-panels variant="inset" class="my-5">
										<v-expansion-panel title="Advanced Options...">
											<v-expansion-panel-text>
												<div class="mt-5">
													<v-select v-model="data.time.step" :items="data.options.timeSteps"
														label="Time steps in a day for rainfall, runoff and routing"
														required></v-select>
												</div>
											</v-expansion-panel-text>
										</v-expansion-panel>
									</v-expansion-panels>
								</div>
							</v-expansion-panel-text>
						</v-expansion-panel>
						<v-expansion-panel>
							<v-expansion-panel-title>
								<v-row no-gutters>
									<v-col cols="12" md="4" class="d-flex justify-start font-weight-bold">Choose output
										to print</v-col>
									<v-col cols="8" class="text-right pr-6 text-secondary d-none d-md-block"></v-col>
								</v-row>
							</v-expansion-panel-title>
							<v-expansion-panel-text>
								<v-row class="mt-5">
									<v-col cols="12" lg="6">
										<div class="form-group mb-5">
											<v-text-field type="number" min="0" required
												v-model.number="data.print.prt.nyskip" label="Warm-up period"
												hint="Number of years to skip printing output"
												persistent-hint></v-text-field>
										</div>

										<div class="text-body-2 mb-1">
											<em>{{ requiredForCheckMessage }}</em>
										</div>

										<v-table class="table-editor" density="compact">
											<thead>
												<tr class="bg-surface">
													<th class="bg-secondary-tonal"></th>
													<th class="bg-secondary-tonal">Daily</th>
													<th class="bg-secondary-tonal">Monthly</th>
													<th class="bg-secondary-tonal">Yearly</th>
													<th class="bg-secondary-tonal">Average</th>
													<th class="bg-secondary-tonal" title="SWAT+ Output File/Table">
														Outputs</th>
												</tr>
												<tr>
													<th></th>
													<th class="text-center mx-auto"><v-checkbox density="compact"
															hide-details v-model="data.options.printAll.daily"
															@update:model-value="checkAllDaily"></v-checkbox></th>
													<th class="text-center"><v-checkbox density="compact" hide-details
															v-model="data.options.printAll.monthly"
															@update:model-value="checkAllMonthly"></v-checkbox></th>
													<th class="text-center"><v-checkbox density="compact" hide-details
															v-model="data.options.printAll.yearly"
															@update:model-value="checkAllYearly"></v-checkbox></th>
													<th class="text-center"><v-checkbox density="compact" hide-details
															v-model="data.options.printAll.avann"
															@update:model-value="checkAllAvann"></v-checkbox></th>
													<th></th>
												</tr>
											</thead>
											<tbody>
												<tr class="bg-secondary-tonal">
													<th colspan="6">Model Components</th>
												</tr>
												<tr v-for="([k, v], i) in Object.entries(data.printGroups.model)"
													:key="i"
													v-show="!data.printConfig.inactive.includes(k) || data.printConfig.showInactive">
													<td>{{ v }}</td>
													<td class="text-center"><v-checkbox density="compact" hide-details
															v-model="data.print.objects[printIndex(k)].daily" /></td>
													<td class="text-center"><v-checkbox density="compact" hide-details
															v-model="data.print.objects[printIndex(k)].monthly" /></td>
													<td class="text-center"><v-checkbox density="compact" hide-details
															v-model="data.print.objects[printIndex(k)].yearly"
															:disabled="requiredForCheck(`${data.print.objects[printIndex(k)].name}_yr`)" />
													</td>
													<td class="text-center"><v-checkbox density="compact" hide-details
															v-model="data.print.objects[printIndex(k)].avann"
															:disabled="requiredForCheck(`${data.print.objects[printIndex(k)].name}_aa`)" />
													</td>
													<td class="code text-muted">
														{{ k }}
														<div v-if="k === 'channel_sd'">channel_sdmorph</div>
													</td>
												</tr>
												<tr class="bg-secondary-tonal">
													<th colspan="6">Basin Model Components</th>
												</tr>
												<tr v-for="([k, v], i) in Object.entries(data.printGroups.modelBasin)"
													:key="i"
													v-show="!data.printConfig.inactive.includes(k) || data.printConfig.showInactive">
													<td>{{ v }}</td>
													<td class="text-center"><v-checkbox density="compact" hide-details
															v-model="data.print.objects[printIndex(k)].daily" /></td>
													<td class="text-center"><v-checkbox density="compact" hide-details
															v-model="data.print.objects[printIndex(k)].monthly" /></td>
													<td class="text-center"><v-checkbox density="compact" hide-details
															v-model="data.print.objects[printIndex(k)].yearly" /></td>
													<td class="text-center"><v-checkbox density="compact" hide-details
															v-model="data.print.objects[printIndex(k)].avann"
															:disabled="requiredForCheck(`${data.print.objects[printIndex(k)].name}_aa`)" />
													</td>
													<td class="code text-muted">
														{{ k }}
														<div v-if="k === 'basin_sd_cha'">basin_sd_chamorph</div>
													</td>
												</tr>
												<tr class="bg-secondary-tonal" v-show="data.printConfig.showInactive">
													<th colspan="6">Region Model Components</th>
												</tr>
												<tr v-for="([k, v], i) in Object.entries(data.printGroups.modelRegion)"
													:key="i"
													v-show="!data.printConfig.inactive.includes(k) || data.printConfig.showInactive">
													<td>{{ v }}</td>
													<td class="text-center"><v-checkbox density="compact" hide-details
															v-model="data.print.objects[printIndex(k)].daily" /></td>
													<td class="text-center"><v-checkbox density="compact" hide-details
															v-model="data.print.objects[printIndex(k)].monthly" /></td>
													<td class="text-center"><v-checkbox density="compact" hide-details
															v-model="data.print.objects[printIndex(k)].yearly" /></td>
													<td class="text-center"><v-checkbox density="compact" hide-details
															v-model="data.print.objects[printIndex(k)].avann"
															:disabled="requiredForCheck(`${data.print.objects[printIndex(k)].name}_aa`)" />
													</td>
													<td class="code text-muted">{{ k }}</td>
												</tr>
												<tr class="bg-secondary-tonal">
													<th colspan="6">Nutrient Balance</th>
												</tr>
												<tr v-for="([k, v], i) in Object.entries(data.printGroups.nutrients)"
													:key="i"
													v-show="!data.printConfig.inactive.includes(k) || data.printConfig.showInactive">
													<td>{{ v }}</td>
													<td class="text-center"><v-checkbox density="compact" hide-details
															v-model="data.print.objects[printIndex(k)].daily" /></td>
													<td class="text-center"><v-checkbox density="compact" hide-details
															v-model="data.print.objects[printIndex(k)].monthly" /></td>
													<td class="text-center"><v-checkbox density="compact" hide-details
															v-model="data.print.objects[printIndex(k)].yearly" /></td>
													<td class="text-center"><v-checkbox density="compact" hide-details
															v-model="data.print.objects[printIndex(k)].avann"
															:disabled="requiredForCheck(`${data.print.objects[printIndex(k)].name}_aa`)" />
													</td>
													<td class="code text-muted">{{ k }}</td>
												</tr>
												<tr class="bg-secondary-tonal">
													<th colspan="6">Water Balance</th>
												</tr>
												<tr v-for="([k, v], i) in Object.entries(data.printGroups.water)"
													:key="i"
													v-show="!data.printConfig.inactive.includes(k) || data.printConfig.showInactive">
													<td>{{ v }}</td>
													<td class="text-center"><v-checkbox density="compact" hide-details
															v-model="data.print.objects[printIndex(k)].daily" /></td>
													<td class="text-center"><v-checkbox density="compact" hide-details
															v-model="data.print.objects[printIndex(k)].monthly" /></td>
													<td class="text-center"><v-checkbox density="compact" hide-details
															v-model="data.print.objects[printIndex(k)].yearly" /></td>
													<td class="text-center"><v-checkbox density="compact" hide-details
															v-model="data.print.objects[printIndex(k)].avann"
															:disabled="requiredForCheck(`${data.print.objects[printIndex(k)].name}_aa`)" />
													</td>
													<td class="code text-muted">{{ k }}</td>
												</tr>
												<tr class="bg-secondary-tonal">
													<th colspan="6">Plant Weather</th>
												</tr>
												<tr v-for="([k, v], i) in Object.entries(data.printGroups.plant)"
													:key="i"
													v-show="!data.printConfig.inactive.includes(k) || data.printConfig.showInactive">
													<td>{{ v }}</td>
													<td class="text-center"><v-checkbox density="compact" hide-details
															v-model="data.print.objects[printIndex(k)].daily" /></td>
													<td class="text-center"><v-checkbox density="compact" hide-details
															v-model="data.print.objects[printIndex(k)].monthly" /></td>
													<td class="text-center"><v-checkbox density="compact" hide-details
															v-model="data.print.objects[printIndex(k)].yearly" /></td>
													<td class="text-center"><v-checkbox density="compact" hide-details
															v-model="data.print.objects[printIndex(k)].avann"
															:disabled="requiredForCheck(`${data.print.objects[printIndex(k)].name}_aa`)" />
													</td>
													<td class="code text-muted">{{ k }}</td>
												</tr>
												<tr class="bg-secondary-tonal">
													<th colspan="6">Losses</th>
												</tr>
												<tr v-for="([k, v], i) in Object.entries(data.printGroups.losses)"
													:key="i"
													v-show="!data.printConfig.inactive.includes(k) || data.printConfig.showInactive">
													<td>{{ v }}</td>
													<td class="text-center"><v-checkbox density="compact" hide-details
															v-model="data.print.objects[printIndex(k)].daily" /></td>
													<td class="text-center"><v-checkbox density="compact" hide-details
															v-model="data.print.objects[printIndex(k)].monthly" /></td>
													<td class="text-center"><v-checkbox density="compact" hide-details
															v-model="data.print.objects[printIndex(k)].yearly" /></td>
													<td class="text-center"><v-checkbox density="compact" hide-details
															v-model="data.print.objects[printIndex(k)].avann"
															:disabled="requiredForCheck(`${data.print.objects[printIndex(k)].name}_aa`)" />
													</td>
													<td class="code text-muted">{{ k }}</td>
												</tr>
												<tr class="bg-secondary-tonal">
													<th colspan="6">Salts</th>
												</tr>
												<tr v-for="([k, v], i) in Object.entries(data.printGroups.salts)"
													:key="i"
													v-show="!data.printConfig.inactive.includes(k) || data.printConfig.showInactive">
													<td>{{ v }}</td>
													<td class="text-center"><v-checkbox density="compact" hide-details
															v-model="data.print.objects[printIndex(k)].daily" /></td>
													<td class="text-center"><v-checkbox density="compact" hide-details
															v-model="data.print.objects[printIndex(k)].monthly" /></td>
													<td class="text-center"><v-checkbox density="compact" hide-details
															v-model="data.print.objects[printIndex(k)].yearly" /></td>
													<td class="text-center"><v-checkbox density="compact" hide-details
															v-model="data.print.objects[printIndex(k)].avann"
															:disabled="requiredForCheck(`${data.print.objects[printIndex(k)].name}_aa`)" />
													</td>
													<td class="code text-muted">{{ k }}</td>
												</tr>
												<tr class="bg-secondary-tonal">
													<th colspan="6">Constituents</th>
												</tr>
												<tr v-for="([k, v], i) in Object.entries(data.printGroups.cs)" :key="i"
													v-show="!data.printConfig.inactive.includes(k) || data.printConfig.showInactive">
													<td>{{ v }}</td>
													<td class="text-center"><v-checkbox density="compact" hide-details
															v-model="data.print.objects[printIndex(k)].daily" /></td>
													<td class="text-center"><v-checkbox density="compact" hide-details
															v-model="data.print.objects[printIndex(k)].monthly" /></td>
													<td class="text-center"><v-checkbox density="compact" hide-details
															v-model="data.print.objects[printIndex(k)].yearly" /></td>
													<td class="text-center"><v-checkbox density="compact" hide-details
															v-model="data.print.objects[printIndex(k)].avann"
															:disabled="requiredForCheck(`${data.print.objects[printIndex(k)].name}_aa`)" />
													</td>
													<td class="code text-muted">{{ k }}</td>
												</tr>
											</tbody>
										</v-table>

										<p class="mb-0 mt-3">
											<v-checkbox hide-details v-model="data.printConfig.showInactive">
												<template v-slot:label>Show all print objects? Leave unchecked to hide
													print objects that are not relevant for this project.</template>
											</v-checkbox>
										</p>
									</v-col>
									<v-col cols="12" lg="6">
										<v-expansion-panels variant="inset">
											<v-expansion-panel title="Advanced Options...">
												<v-expansion-panel-text>
													<div class="my-5">
														<v-select v-model="data.print.prt.crop_yld"
															:items="data.options.cropYldFiles"
															label="Print crop yield output files" required
															hint="Crop yield files are required for SWAT+ Check, so we recommend printing."
															persistent-hint></v-select>
													</div>

													<div class="d-flex">
														<div class="pr-3">
															<v-checkbox density="comfortable" hide-details
																v-model="data.print.prt.hydcon"
																label="Hydrograph connect output file"></v-checkbox>
															<div class="d-flex align-center">
																<v-checkbox density="comfortable" hide-details
																	v-model="data.print.prt.csvout"
																	label="Print output files in CSV format"
																	disabled></v-checkbox>
																<v-tooltip location="bottom">
																	<template v-slot:activator="{ props }">
																		<font-awesome-icon v-bind="props"
																			:icon="['fas', 'fa-info-circle']"
																			class="ml-1 text-secondary"></font-awesome-icon>
																	</template>
																	Printing to CSV format is now required to process
																	output files more efficiently with
																	fewer errors.
																</v-tooltip>
															</div>

														</div>
														<div>
															<div class="d-flex align-center">
																<v-checkbox density="comfortable" hide-details
																	v-model="data.print.prt.mgtout"
																	label="Management output file"></v-checkbox>
																<v-tooltip location="bottom">
																	<template v-slot:activator="{ props }">
																		<font-awesome-icon v-bind="props"
																			:icon="['fas', 'fa-info-circle']"
																			class="ml-1 text-secondary"></font-awesome-icon>
																	</template>
																	Disarankan untuk tetap memilih opsi ini jika Anda
																	ingin melihat pratinjau operasi
																	manajemen Anda di SWAT+ Check.
																</v-tooltip>
															</div>

															<v-checkbox density="comfortable" hide-details
																v-model="data.print.prt.fdcout"
																label="Flow duration curve output file"></v-checkbox>
														</div>
													</div>

													<v-divider class="my-4"></v-divider>

													<div class="form-group mb-5">
														<v-text-field v-model="data.printDisplay.startDate"
															label="Date to start printing output" required type="date"
															:hint="formatters.toDate(data.printDisplay.startDate, 'MMMM D, YYYY') || 'Leave blank to print entire simulation period'"
															persistent-hint></v-text-field>
													</div>
													<div class="form-group mb-5">
														<v-text-field v-model="data.printDisplay.endDate"
															label="Date to stop printing output" required type="date"
															:hint="formatters.toDate(data.printDisplay.endDate, 'MMMM D, YYYY') || 'Leave blank to print entire simulation period'"
															persistent-hint></v-text-field>
													</div>

													<div>
														<v-text-field v-model="data.print.prt.interval"
															label="Daily print within the period (e.g., interval=2 will print every other day)"
															required type="number" min="0"></v-text-field>
													</div>
												</v-expansion-panel-text>
											</v-expansion-panel>
										</v-expansion-panels>
									</v-col>
								</v-row>
							</v-expansion-panel-text>
						</v-expansion-panel>
					</v-expansion-panels>

					<v-divider class="my-6"></v-divider>

					<error-alert :text="modelIssues.wgn.error"></error-alert>
					<page-loading :loading="modelIssues.wgn.loading"></page-loading>
					<div v-if="!modelIssues.wgn.loading && modelIssues.wgn.is_invalid">
						<h1 class="text-h5 mb-4">Model Issues</h1>
						<v-alert type="warning" icon="$warning" variant="tonal" border="start" class="mb-4">
							<p>
								Anda punya <router-link class="text-warning" to="/edit/climate/wgn">weather
									generators</router-link> Dalam
								model Anda yang tidak memiliki nilai bulanan yang sesuai.
								Nilai bulanan bukan nol untuk setiap statistik diperlukan agar SWAT+ dapat berjalan.
								Silakan gunakan fungsi impor dengan basis data SWAT+ WGN jika Anda tidak yakin, atau
								lihat dokumentasi
								SWAT+.Stasiun dengan data yang hilang tercantum di bawah ini.
							</p>
							<ul>
								<li v-for="station in modelIssues.wgn.data">
									Station <router-link class="text-warning"
										:to="`/edit/climate/wgn/edit/${station.id}`">{{ station.name
										}}</router-link> has <b>{{ station.months }}</b> months of data; 12 are
									required.
								</li>
							</ul>
						</v-alert>
					</div>

					<h1 class="text-h5 mb-4">Run SWAT+</h1>

					<p>
						Sebelum menjalankan model, kita harus menulis file input yang digunakan oleh model.
						Jika Anda telah memodifikasi input Anda melalui bagian edit sejak terakhir menjalankan model,
						pastikan untuk tetap
						mencentang kotak ini.
						Centang kotak ketiga untuk membaca file output Anda ke dalam basis data SQLite.
						Ini akan digunakan oleh alat visualisasi di QSWAT+. Jika Anda tidak bermaksud menggunakan fitur
						ini,
						Anda dapat menghapus centang pada kotak ini untuk menghemat waktu.
					</p>

					<v-card>
						<v-card-item>
							<div class="d-flex align-start my-3">
								<div class="mr-4">
									<v-checkbox density="compact" hide-details v-model="data.selection.inputs"
										id="select_inputs"></v-checkbox>
								</div>
								<div class="pt-1">
									<label for="select_inputs"><b>Write input files</b></label>
									<span class="text-secondary"
										v-if="!formatters.isNullOrEmpty(data.config.input_files_last_written)">
										<br>Last written {{ formatters.toDate(data.config.input_files_last_written) }}
									</span>
								</div>
							</div>
						</v-card-item>

						<v-divider></v-divider>

						<v-card-item>
							<div class="d-flex align-start my-3">
								<div class="mr-4">
									<v-checkbox density="compact" hide-details v-model="data.selection.model"
										id="select_model"></v-checkbox>
								</div>
								<div class="pt-0">
									<div class="d-flex align-center">
										<label for="select_model">
											<b>Run SWAT+</b>
										</label>
										<v-select v-model="data.selection.exeFile" :items="data.exeOptions"
											item-title="description" item-value="fileName" class="ml-2"
											density="compact" hide-details></v-select>
										<v-tooltip>
											<template v-slot:activator="{ props }">
												<font-awesome-icon v-bind="props" :icon="['fas', 'fa-gear']"
													class="ml-2 text-secondary pointer"
													@click.prevent="data.page.exeCustomization.show = true"></font-awesome-icon>
											</template>
											Advanced: provide your own executables
										</v-tooltip>
									</div>

									<div class="text-secondary mt-1"
										v-if="!formatters.isNullOrEmpty(data.config.swat_last_run)">
										Last run {{ formatters.toDate(data.config.swat_last_run) }}
									</div>
									<div class="mt-1"
										v-if="false && data.selection.model && constants.globals.platform == 'win32'">
										<v-checkbox density="compact" hide-details v-model="data.selection.debug"
											label="Use debug version?"></v-checkbox>
									</div>
								</div>
							</div>
						</v-card-item>

						<v-divider></v-divider>

						<v-card-item>
							<div class="d-flex align-start my-3">
								<div class="mr-4">
									<v-checkbox density="compact" hide-details v-model="data.selection.output"
										id="select_output"
										@update:model-value="data.selection.swatCheckOnly = false"></v-checkbox>
								</div>
								<div class="pt-1">
									<label for="select_output">
										<b>Analyze output for visualization</b>
										<v-tooltip>
											<template v-slot:activator="{ props }">
												<font-awesome-icon v-bind="props" :icon="['fas', 'fa-gear']"
													class="ml-2 text-secondary pointer"
													@click.prevent="data.page.outputSkip.show = true"></font-awesome-icon>
											</template>
											Advanced: specify output files to skip in analysis
										</v-tooltip>
									</label>
									<span class="text-secondary"
										v-if="!formatters.isNullOrEmpty(data.config.output_last_imported)">
										<br>Last analyzed {{ formatters.toDate(data.config.output_last_imported) }}
									</span>
									<span class="text-warning" v-if="data.page.forceRerunForOutput">
										<br>Dalam pembaruan terbaru, kami mengubah cara file output diproses.
										Jika Anda tetap mencentang kotak ini, pastikan Anda juga mencentang kotak untuk
										<b>re-run the
											model</b>.
									</span>

									<div>
										<div class="d-flex align-start my-3">
											<div class="mr-2">
												<v-checkbox density="compact" hide-details
													v-model="data.selection.swatCheckOnly" id="swatcheck_only"
													:disabled="!data.selection.output"></v-checkbox>
											</div>
											<div class="pt-1">
												<label for="swatcheck_only">
													<b>Optional: only read files required by SWAT+ Check</b>
												</label>
												<div class="text-secondary">
													Memiliki model besar dan mencetak file output harian atau bulanan
													tetapi tidak berencana
													menggunakan visualisasi?
													<br>Centang kotak ini untuk menghemat waktu dan hanya membaca file
													output yang
													diperlukan untuk Pemeriksaan SWAT+.
												</div>
											</div>
										</div>
									</div>
								</div>
							</div>
						</v-card-item>
					</v-card>

					<v-alert v-if="currentProject.isLte" color="info" icon="$info" variant="tonal" border="start"
						class="my-4">
						Looking for <strong>SWAT+ Check</strong>? SWAT+ Check is not available in SWAT+ lte.
						You must run the full version of SWAT+ to get the checker functionality.
					</v-alert>

					<action-bar full-width>
						<v-btn type="submit" :loading="data.page.saving" :disabled="data.page.saving || noneSelected"
							variant="flat" color="primary" class="mr-2">
							Save Settings &amp; Run Selected
						</v-btn>
						<v-menu>
							<template v-slot:activator="{ props }">
								<v-btn type="button" variant="flat" color="primary" class="mr-2" v-bind="props">More
									Actions...</v-btn>
							</template>
							<v-list>
								<v-list-item
									v-if="!formatters.isNullOrEmpty(data.config.output_last_imported) && !currentProject.isLte"
									to="/check"><v-list-item-title>Run SWAT+ Check</v-list-item-title></v-list-item>
								<swat-plus-toolbox-button
									v-if="!formatters.isNullOrEmpty(data.config.input_files_last_written) && !currentProject.isLte"
									:ran-swat="!formatters.isNullOrEmpty(data.config.input_files_last_written)"
									as-list-item text="Open SWAT+ Toolbox"></swat-plus-toolbox-button>
								<swat-plus-iahris-button
									v-if="!formatters.isNullOrEmpty(data.config.swat_last_run) && !currentProject.isLte"
									:ran-swat="!formatters.isNullOrEmpty(data.config.swat_last_run)" as-list-item
									text="Open SWAT+ IAHRIS"></swat-plus-iahris-button>
								<v-list-item
									@click="data.page.completed.show = false; data.page.saveScenario.show = true"><v-list-item-title>Save
										Scenario</v-list-item-title></v-list-item>
								<open-file as-list-item :file-path="currentResultsPath">Open Results
									Directory</open-file>
								<open-file v-if="!formatters.isNullOrEmpty(outputLogFile)" as-list-item
									:file-path="outputLogFile">Review
									Output Analysis Log File</open-file>
							</v-list>
						</v-menu>
						<v-btn type="button" variant="flat" color="secondary" @click="utilities.exit"
							class="ml-auto">Exit SWAT+
							Editor</v-btn>
					</action-bar>
				</v-form>

				<v-dialog v-model="data.page.run.show" :max-width="constants.dialogSizes.lg" persistent>
					<v-card :title="modalTitle">
						<v-card-text>
							<error-alert :text="data.page.run.error"></error-alert>
							<stack-trace-error v-if="!formatters.isNullOrEmpty(task.error) && !data.status.model"
								:error-title="errorTitle" :stack-trace="task.error ? task.error.toString() : ''"  />

							<v-alert variant="tonal" type="error" icon="$error" border="start"
								v-if="!formatters.isNullOrEmpty(task.error) && data.status.model" class="mb-4">
								{{ task.error }}
								<span v-if="false && !data.selection.debug">Please run the model in debug mode to get a
									detailed error
									report.</span>
								<span v-else>
									Jika Anda tidak dapat menentukan penyebab kesalahan, silakan salin dan tempel log
									output di bawah
									ini ke
									<open-in-browser url="https://groups.google.com/d/forum/swatplus"
										text="SWAT+ model user group" />.
								</span>
							</v-alert>

							<div v-if="task.running">
								<v-progress-linear :model-value="task.progress.percent" color="primary" height="15"
									striped></v-progress-linear>
								<p>
									{{ task.progress.message }}
								</p>
							</div>
							<div v-if="data.status.model && !formatters.isNullOrEmpty(task.error)"
								class="scroll-bottom mt-2">
								<pre>
					<div v-for="(message, i) in task.modelMessages" :key="i">{{ message }}</div>
				</pre>
							</div>
						</v-card-text>
						<v-divider></v-divider>
						<v-card-actions>
							<v-btn @click="cancelTask">Cancel</v-btn>
						</v-card-actions>
					</v-card>
				</v-dialog>

				<v-dialog v-model="data.page.completed.show" :max-width="constants.dialogSizes.sm">
					<v-card title="All selected tasks have completed">
						<v-card-item>
							<div class="mb-8">
								<v-btn
									v-if="!formatters.isNullOrEmpty(data.config.output_last_imported) && !currentProject.isLte"
									type="button" variant="flat" color="primary" size="large" rounded="xl" to="/check"
									block class="my-2">Run SWAT+ Check</v-btn>
								<swat-plus-toolbox-button
									v-if="!formatters.isNullOrEmpty(data.config.input_files_last_written) && !currentProject.isLte"
									:ran-swat="!formatters.isNullOrEmpty(data.config.input_files_last_written)"
									variant="flat" color="primary" size="large" rounded="xl" block class="my-2" no-icon
									text="Open SWAT+ Toolbox"></swat-plus-toolbox-button>
								<swat-plus-iahris-button
									v-if="!formatters.isNullOrEmpty(data.config.swat_last_run) && !currentProject.isLte"
									:ran-swat="!formatters.isNullOrEmpty(data.config.swat_last_run)" variant="flat"
									color="primary" size="large" rounded="xl" block class="my-2" no-icon
									text="Open SWAT+ IAHRIS"></swat-plus-iahris-button>
								<v-btn type="button" block variant="flat" color="primary" size="large" rounded="xl"
									@click="data.page.completed.show = false; data.page.saveScenario.show = true"
									class="my-2">Save
									Scenario</v-btn>
								<open-file button block variant="flat" color="primary" size="large" rounded="xl"
									:file-path="currentResultsPath" class="my-2">Open Results Directory</open-file>
								<div class="my-2">
									<open-file v-if="!formatters.isNullOrEmpty(outputLogFile)" button block
										variant="flat" color="primary" size="large" rounded="xl"
										:file-path="outputLogFile">Review Output Analysis Log
										File</open-file>
								</div>
								<v-row class="mt-2" no-gutters>
									<v-col md class="mr-2"><v-btn type="button" variant="flat" color="secondary"
											size="large" rounded="xl" @click="data.page.completed.show = false" block
											class="mr-1">Back to
											Editor</v-btn></v-col>
									<v-col md><v-btn type="button" variant="flat" color="secondary" size="large"
											rounded="xl" @click="utilities.exit" block>Exit SWAT+ Editor</v-btn></v-col>
								</v-row>
							</div>
						</v-card-item>
					</v-card>
				</v-dialog>

				<v-dialog v-model="data.page.exeCustomization.show" :max-width="constants.dialogSizes.md">
					<v-card title="Advanced: Customize SWAT+ Model Executables">
						<v-card-item>
							<p>
								Secara default, kami biasanya mengirimkan SWAT+ Editor dengan tiga versi model: rilis
								stabil resmi,
								versi pengembangan terbaru, dan versi rilis model sebelumnya.
								Anda dapat memilih salah satu dari ketiga versi ini dari menu tarik-turun.
							</p>
							<p>
								Jika Anda ingin menyediakan versi model SWAT+ Anda sendiri, Anda dapat melakukannya
								dengan terlebih
								dahulu membuka
								<open-file :file-path="constants.globals.swat_path" class="text-primary">this folder
									<font-awesome-icon :icon="['fas', 'fa-folder-open']"
										class="ml-2"></font-awesome-icon></open-file>
								containing the executables.
								Salin file executable Anda ke folder ini, lalu buka file exe-options.csv dan tambahkan
								baris baru dengan
								deskripsi dan nama file executable kustom Anda.
								Terakhir, segarkan daftar di editor dengan <a href="#"
									@click.prevent="refreshExeOptions" class="text-primary">clicking here</a>.
							</p>
							<p>
								Perhatian: menyediakan file eksekusi Anda sendiri dapat menyebabkan kesalahan jika tidak
								kompatibel
								dengan versi rilis resmi default editor.
								Perubahan format file input atau output antar versi model dapat menyebabkan kesalahan.
							</p>
						</v-card-item>
						<v-divider></v-divider>
						<v-card-actions>
							<open-file :file-path="constants.globals.swat_path" button color="primary"
								variant="text">Open SWAT+ Exec.
								Folder</open-file>
							<v-btn @click="refreshExeOptions(); data.page.exeCustomization.show = false"
								color="primary">Refresh
								Options</v-btn>
							<v-btn @click="data.page.exeCustomization.show = false">Close</v-btn>
						</v-card-actions>
					</v-card>
				</v-dialog>

				<v-dialog v-model="data.page.outputSkip.show" :max-width="constants.dialogSizes.md">
					<v-card title="Advanced: Skip Output Files in Analysis">
						<v-card-item>
							<p>
								Secara umum, kami menyarankan memilih output yang akan dicetak dalam model itu sendiri
								dan membiarkan
								editor membaca semua file output.
								Namun, jika Anda menjalankan model dengan jumlah file output yang besar atau memiliki
								ruang disk yang
								terbatas, Anda dapat memilih untuk melewatkan pembacaan beberapa file output ke database
								editor.
							</p>
							<p>
								File yang dilewati akan tetap tercetak dalam format .txt/.csv sesuai dengan pengaturan
								pencetakan model
								Anda, tetapi editor akan mengabaikannya saat mengimpor output.
								Masukkan nama file output yang ingin Anda lewati di bawah ini. Pastikan untuk memasukkan
								nama file yang
								persis sama seperti yang muncul di direktori output Anda, termasuk ekstensi file.
								Pisahkan beberapa nama file dengan koma.
							</p>
							<div class="form-group">
								<v-text-field v-model="data.page.outputSkip.files"
									label="Output files to skip (comma-separated)" type="text"
									hint="Enter the exact names of output files to skip, separated by commas. Example: output1.csv,output2.csv"
									persistent-hint></v-text-field>
							</div>
						</v-card-item>
						<v-divider></v-divider>
						<v-card-actions>
							<v-btn @click="data.page.outputSkip.show = false">Close</v-btn>
						</v-card-actions>
					</v-card>
				</v-dialog>

				<v-dialog v-model="data.page.saveScenario.show" :max-width="constants.dialogSizes.lg" persistent>
					<v-card :title="modalTitle">
						<v-card-text>
							<error-alert :text="data.page.saveScenario.error"></error-alert>
							<stack-trace-error v-if="!formatters.isNullOrEmpty(task.error)"
								error-title="There was an error saving your scenario"
								:stack-trace="task.error ? task.error.toString() : ''"  />

							<div v-if="task.running">
								<v-progress-linear :model-value="task.progress.percent" color="primary" height="15"
									striped></v-progress-linear>
								<p>
									{{ task.progress.message }}
								</p>
							</div>
							<div v-else>
								<p>
									Menyimpan skenario akan membuat salinan basis data proyek Anda serta semua file teks
									input dan
									output model.
									Kami menyarankan untuk menjalankan model sebelum menyimpan skenario Anda. Setelah
									penyimpanan
									selesai, perubahan
									tambahan apa pun yang dilakukan pada proyek Anda tidak akan memengaruhi skenario
									yang tersimpan.
									Anda dapat memuat kembali skenario yang tersimpan ke editor dari
									<router-link to="/">project setup screen</router-link>.
								</p>

								<div class="form-group">
									<v-text-field type="text" required v-model="data.page.saveScenario.name"
										label="Give your scenario a unique name"
										hint="Will create a new folder with this name under your project's Scenarios directory. Cannot be the same name as an existing scenario."
										persistent-hint></v-text-field>
								</div>
							</div>

						</v-card-text>
						<v-divider></v-divider>
						<v-card-actions>
							<v-btn v-if="formatters.isNullOrEmpty(task.error)" :loading="task.running"
								@click="saveScenario" color="primary" variant="text">
								Save Scenario
							</v-btn>
							<v-btn @click="cancelTask">Cancel</v-btn>
						</v-card-actions>
					</v-card>
				</v-dialog>

				<v-dialog v-model="data.page.savedScenario.show" :max-width="constants.dialogSizes.sm">
					<v-card title="Scenario Saved">
						<v-card-text>
							<p>
								<b>Skenario Anda telah disimpan.</b>
								Perubahan tambahan apa pun yang dilakukan pada proyek Anda tidak akan memengaruhi
								skenario yang telah
								disimpan.
								Anda dapat memuat kembali skenario yang tersimpan ke editor dari <router-link
									to="/">project setup
									screen</router-link>.
							</p>
						</v-card-text>
						<v-divider></v-divider>
						<v-card-actions>
							<open-file button color="primary" variant="text" :file-path="newScenarioPath">Open Scenario
								Directory</open-file>
							<v-btn @click="data.page.savedScenario.show = false">Close</v-btn>
						</v-card-actions>
					</v-card>
				</v-dialog>

				<v-dialog v-model="data.page.inputs.show" scrollable>
					<v-card title="Customize input files to write">
						<v-card-text>
							<p>
								Secara default, editor akan menulis semua file input SWAT+ yang ditentukan oleh
								pengaturan model Anda.
								Jika Anda memodifikasi file apa pun di luar editor, Anda dapat memilih untuk melewatkan
								penulisan file
								tersebut di bawah ini.
								Pastikan file tersebut masih ada di direktori file input Anda, jika tidak, model akan
								mengalami crash.
								Anda juga dapat memilih untuk mengabaikan file input sepenuhnya dengan memilih untuk
								tidak menulis ke
								file.cio.
								Opsi ini tidak disarankan untuk pengguna pemula dan dapat merusak model Anda.
							</p>

							<v-table small density="compact">
								<thead>
									<tr class="bg-secondary-tonal">
										<th>Category</th>
										<th :colspan="data.page.inputs.maxCols">Files</th>
									</tr>
								</thead>
								<tbody>
									<tr v-for="cat in data.file_cio" :key="cat.category">
										<td><b>{{ cat.category }}</b></td>
										<td v-for="f in cat.files" :key="f.name" style="white-space: nowrap;">
											<v-btn variant="text" append-icon="fas fa-angle-down" class="plain-button"
												:color="inputCustomizationColor(f.name)">
												{{ f.available ? f.name : 'none' }}
												<v-menu activator="parent">
													<v-card>
														<v-card-item>
															<label class="d-flex align-center" v-if="f.available">
																<div style="width:30px"><v-checkbox hide-details
																		v-model="data.inputs.ignore_files"
																		:value="f.name" density="compact"></v-checkbox>
																</div>
																<div>provide my own {{ f.name }}</div>
															</label>
															<label class="d-flex align-center" v-if="f.available">
																<div style="width:30px"><v-checkbox hide-details
																		v-model="data.inputs.ignore_cio_files"
																		:value="f.name" density="compact"></v-checkbox>
																</div>
																<div>exclude {{ f.name }} from file.cio</div>
															</label>
															<label class="d-flex align-center" v-if="!f.available">
																<div style="width:30px"><v-checkbox hide-details
																		v-model="data.inputs.custom_cio_files"
																		:value="f.name" density="compact"></v-checkbox>
																</div>
																<div>provide my own {{ f.name }}</div>
															</label>
														</v-card-item>
													</v-card>

												</v-menu>
											</v-btn>
										</td>
										<td v-if="cat.files.length < data.page.inputs.maxCols"
											:colspan="data.page.inputs.maxCols - cat.files.length"></td>
									</tr>
								</tbody>
							</v-table>
						</v-card-text>
						<v-divider></v-divider>
						<v-card-actions>
							<v-btn @click="data.page.inputs.show = false" color="primary">Save &amp; Close</v-btn>
						</v-card-actions>
					</v-card>
				</v-dialog>
			</div>
		</v-main>
	</project-container>
</template>

<style scoped>


.scroll-bottom {
	width: 100%;
	height: 350px;
	border: 1px solid #ccc;
	overflow: auto;
	padding: 5px;
	font-size: 0.8rem;
}

.plain-button {
	text-transform: lowercase;
	letter-spacing: normal;
}
</style>