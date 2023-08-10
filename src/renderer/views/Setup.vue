<script setup lang="ts">
	import { reactive, ref, onMounted, watch } from 'vue';
	import { useRoute } from 'vue-router';
	import { useTheme } from 'vuetify';
	import { useApi, useConstants, useErrorHandling, useFormatters, useProjectStore, useRunProcess, useUtilities } from '../plugins';
	import '../plugins/interfaces';
	import SwatPlusToolboxButton from '../components/SwatPlusToolboxButton.vue';

	const route = useRoute();
	const theme = useTheme();
	const api = useApi();
	const constants = useConstants();
	const errors = useErrorHandling();
	const formatters = useFormatters();
	const currentProject = useProjectStore();
	const runProcess = useRunProcess();
	const utilities = useUtilities();
	
	let page:any = reactive({
		error: null,
		loading: false,
		colorTheme: 'light',
		open: {
			loading: false,
			error: null,
			show: false,
			projectDb: null
		},
		edit: {
			saving: false,
			error: null,
			show: false,
			name: null,
			description: null
		},
		create: {
			loading: false,
			error: null,
			show: false,
			name: null,
			description: null,
			projectFolder: null,
			datasetsDb: null,
			isLte: false
		},
		close: {
			show: false,
			removeFromRecent: false
		},
		import: {
			show: false,
			error: null,
			project: {
				projectDb: null,
				datasetsDb: null,
				name: null,
				description: null,
				version: null,
				isLte: false
			}
		},
		openConfirm: {
			show: false,
			error: null,
			project: {},
			reimportMessage: false
		},
		loadScenario: {
			show: false,
			error: null,
			running: false,
			scenario: {}
		},
		noProject: {
			show: false
		},
		update: {
			show: false,
			error: null,
			running: false
		}
	})

	let recentProjects:any[] = reactive([])
	let versionSupport:any = reactive({})
	let loadTries = 0;

	let info:any = reactive({
		name: '',
		description: '',
		file_path: '',
		last_modified: Date.now(),
		is_lte: false,
		status: {
			imported_weather: false,
			wrote_inputs: false,
			ran_swat: false,
			imported_output: false,
			using_gis: false
		},
		simulation: {},
		total_area: 0,
		totals: {},
		editor_version: '',
		gis_version: '',
		charts: {
			landuse: []
		},
		scenarios: []
	})

	let charts:any = reactive({
		landuse: {}
	})

	async function init() {
		if (route.path === '/') {
			getColorTheme();
			recentProjects = utilities.getRecentProjects();

			let commandLineDb = currentProject.hasLoadedCommandLine ? '' : constants.globals.project_db;
			if (!formatters.isNullOrEmpty(commandLineDb)) {
				page.loading = true;
				page.open.projectDb = commandLineDb;
				await openProject();
				page.loading = false;
			} else {
				let hasProject = currentProject.hasCurrentProject && utilities.pathExists(currentProject.projectDb||'');
				if (!hasProject) {
					let project = utilities.getMostRecentProject();
					if (project !== undefined && utilities.pathExists(project.projectDb)) {
						currentProject.setCurrentProject(project);
						hasProject = true;
					}
				}

				utilities.setWindowTitle();

				if (hasProject) {
					await getInfo();
				}
			}
		}		
	}

	async function openProject() {
		page.open.loading = true;
		page.open.error = null;

		try {
			const response = await api.get(`setup/config`, currentProject.getTempApiHeader(page.open.projectDb));
			errors.log(response.data);

			let project:ProjectSettings = {
				projectDb: page.open.projectDb,
				datasetsDb: response.data.reference_db,
				name: response.data.project_name,
				description: response.data.project_description,
				version: response.data.editor_version,
				isLte: response.data.is_lte
			}

			if (formatters.isNullOrEmpty(response.data.gis_version)) {
				await loadProject(project);
			} else if (response.data.imported_gis) {
				page.openConfirm.project = project;
				page.openConfirm.show = true;
			} else {
				project.version = constants.appSettings.version;
				page.import.project = project;
				page.import.show = true;
			}

			page.open.show = false;
			loadTries = 0;
		} catch (error) {
			if (loadTries < 10) {
				loadTries++;
				await sleep(2000);
				await openProject();
			} else {
				page.open.error = errors.logError(error, 'Unable to get project information from database.');
				loadTries = 0;
			}
		}

		page.open.loading = false;
	}

	async function confirmOpen() {
		page.openConfirm.show = false;
		await loadProject(page.openConfirm.project);
	}

	async function loadProject(project:ProjectSettings) {
		if (utilities.pathExists(project.projectDb||'')) {
			currentProject.setCurrentProject(project);
			utilities.pushRecentProject(project);
			recentProjects = utilities.getRecentProjects();
			utilities.setWindowTitle();
			versionSupport = utilities.getVersionSupport(project.version||'');
			await getInfo();
			currentProject.setHasLoadedCommandLine(true);
		} else {
			page.noProject.show = true;
		}
	}

	async function getInfo() {
		page.loading = true;
		page.error = null;

		try {
			const response = await api.get(`setup/info`, currentProject.getApiHeader());
			errors.log(response.data);
			info = response.data;
			charts.landuse = getPieChart('Land use distribution', info.charts.landuse);
			versionSupport = utilities.getVersionSupport(currentProject.version||'');
		} catch (error) {
			errors.log(error);
		}
		
		page.loading = false;
	}

	function getPieChart(title:string, data:any, seriesLabel = 'Area') {
		return {
			plotOptions: { pie: { dataLabels: { enabled: false }, showInLegend: true } },
			title: { text: title },
			tooltip: { pointFormat: '{series.name}: <b>{point.percentage:,.1f}% ({point.y:,.1f} ha)</b>' },
			series: [{ data: data, name: seriesLabel, type: 'pie' }]
		};
	}

	function removeProject(project:ProjectSettings) {
		if (currentProject.projectDb === project.projectDb) {
			page.close.removeFromRecent = true;
			page.close.show = true;
		} else {
			utilities.deleteRecentProject(project);
			recentProjects = utilities.getRecentProjects();
		}
	}

	function closeCurrentProject() {
		if (page.close.removeFromRecent) {
			utilities.deleteRecentProject(currentProject.getObject());
			recentProjects = utilities.getRecentProjects();
		}

		currentProject.setCurrentProject({
			projectDb: null,
			datasetsDb: null,
			name: null,
			version: null,
			isLte: false
		});
		versionSupport = {};
		page.close.show = false;
	}

	function openEditProject() {
		page.edit.name = currentProject.name;
		page.edit.description = currentProject.description;
		page.edit.show = true;
	}

	async function editProject() {
		page.edit.saving = true;
		page.edit.error = null;

		try {
			let data = {
				'name': formatters.toValidName(page.edit.name),
				'description': formatters.toValidName(page.edit.description)
			};

			const response = await api.put(`setup/config`, data, currentProject.getApiHeader());
			errors.log(response.data);
			currentProject.name = data.name;
			currentProject.description = data.description;
			page.edit.show = false;
			await loadProject(currentProject.getObject());
		} catch (error) {
			page.edit.error = errors.logError(error, 'Unable to save changes.');
		}
		
		page.edit.saving = false;
	}

	//Calls to swatplus_api.py

	function createProject() {
		page.create.loading = true;
		page.create.error = null;

		if (formatters.isNullOrEmpty(page.create.name))
			page.create.error = 'Please enter a name for your project.';
		else if (formatters.isNullOrEmpty(page.create.projectFolder))
			page.create.error = 'Please select a project folder.';
		else if (formatters.isNullOrEmpty(page.create.datasetsDb))
			page.create.error = 'Please select a datasets SQLite file.';
		else {
			let fileName = formatters.toValidFileName(page.create.name).toLowerCase();
			let project = {
				projectDb: utilities.joinPaths([page.create.projectFolder, fileName + '.sqlite']),
				datasetsDb: page.create.datasetsDb,
				name: formatters.toValidName(page.create.name),
				description: formatters.toValidName(page.create.description),
				version: constants.appSettings.version,
				isLte: page.create.isLte
			};
			let lte = project.isLte ? 'y' : 'n';

			let args = [
				'setup_project', 
				'--project_db_file='+ project.projectDb,
				'--datasets_db_file='+ project.datasetsDb, 
				'--project_name='+ project.name,
				'--editor_version='+ constants.appSettings.version,
				'--is_lte=' + lte, 
				'--project_description='+ project.description
			];

			runTask(args, project);
		}

		page.create.loading = false;
	}

	function importProject() {
		page.import.error = null;

		if (formatters.isNullOrEmpty(page.import.project.name)) {
			page.import.error = 'Please give your project a name in the text box below.';
		} else {
			let project = page.import.project;
			let lte = project.isLte ? 'y' : 'n';

			let args = [
				'setup_project', 
				'--project_db_file='+ project.projectDb, 
				'--project_name='+ formatters.toValidName(project.name),
				'--editor_version='+ constants.appSettings.version,
				'--is_lte=' + lte, 
				'--project_description='+ formatters.toValidName(project.description)
			];

			runTask(args, project);
		}
	}

	async function reimportGis() {
		page.open.projectDb = currentProject.projectDb;
		page.openConfirm.reimportMessage = true;
		await openProject();
	}

	function reImportProject() {
		let project = page.openConfirm.project;
		let lte = project.isLte ? 'y' : 'n';
		page.update.running = true;

		let args = [
			'reimport_gis', 
			'--project_db_file='+ project.projectDb, 
			'--project_name='+ project.name,
			'--editor_version='+ constants.appSettings.version,
			'--is_lte=' + lte
		];

		runTask(args, project);
	}

	function updateProject() {
		page.update.error = null;
		page.update.show = true;
		page.update.running = true;
		
		let args = [
			'update_project', 
			'--project_db_file='+ currentProject.projectDb, 
			'--editor_version='+ constants.appSettings.version,
			'--update_project_values=n',
			'--reimport_gis=n'
		];

		runTask(args, currentProject.getObject());
	}

	function askLoadScenario(scenario:any) {
		page.loadScenario.scenario = scenario;
		page.loadScenario.show = true;
	}

	function loadScenario() {
		page.loadScenario.error = null;
		page.loadScenario.running = true;
		
		let args = [
			'load_scenario', 
			'--project_db_file='+ currentProject.projectDb,
			'--project_name='+ page.loadScenario.scenario.name
		];

		runTask(args, currentProject.getObject());
	}

	//Task processing to handle calls and feedback from swatplus_api.py

	let task:any = reactive({
		progress: {
			percent: 0,
			message: null
		},
		process: null,
		error: null,
		running: false,
		currentPid: null,
		currentProject: null
	})

	function runTask(args:string[], project:ProjectSettings) {
		task.error = null;
		task.running = true;
		task.progress = {
			percent: 0,
			message: null
		};
		task.currentProject = project;

		task.currentPid = runProcess.runApiProc('swatplus_api', args);
	}

	runProcess.processStdout((_event:any, data:any) => {
		task.progress = runProcess.getApiOutput(data);
	});
	
	runProcess.processStderr((_event:any, data:any) => {
		console.log(`stderr: ${data}`);
		task.error = data;
		task.running = false;
	});
	
	runProcess.processClose(async (_event:any, code:any) => {
		let project = task.currentProject;
		if (formatters.isNullOrEmpty(task.error)) {
			if (page.loadScenario.running) {
				page.open.projectDb = project.projectDb;
				await openProject();
				task.running = false;
				closeTaskModals();
			} else {
				if (page.update.running) {
					project.version = constants.appSettings.version;
				}
				await loadProject(project);
				task.running = false;
				closeTaskModals();
			}
		}
	});

	function cancelTask() {
		task.error = null;
		runProcess.killProcess(task.currentPid);
		
		task.running = false;
		closeTaskModals();
	}

	function closeTaskModals() {
		page.import.show = false;
		page.loadScenario.show = false;
		page.loadScenario.running = false;
		page.create.show = false;
		page.openConfirm.show = false;
		page.update.show = false;
	}

	//Color theme

	function getColorTheme():void {
		let colorTheme = localStorage.getItem('colorTheme');
		setColorTheme(colorTheme);
		console.log(theme.current.value.colors)
	}

	function setColorTheme(colorTheme:string|null):void {
		if (colorTheme === null) colorTheme = 'light';
		page.colorTheme = colorTheme;
		theme.global.name.value = colorTheme;
		utilities.setColorTheme(colorTheme);
		localStorage.setItem('colorTheme', colorTheme);
	}

	function toggleColorTheme():void {
		if (page.colorTheme === 'light') setColorTheme('dark');
		else setColorTheme('light');
	}

	//Lifecycle hooks

	onMounted(async () => await init());

	watch(
		() => route,
		async () => await init()
	)

	async function sleep(ms:number|undefined) {
		return new Promise(resolve => setTimeout(resolve, ms));
	}
</script>

<template>
	<div>
		<v-navigation-drawer theme="dark" rail permanent>
			<v-list density="compact" nav>
				<v-list-item prepend-icon="fas fa-folder-open" to="/">
					<v-tooltip activator="parent" location="end">Project setup and information</v-tooltip>
				</v-list-item>
				<v-list-item prepend-icon="fas fa-pencil-alt" to="/edit">
					<v-tooltip activator="parent" location="end">Edit SWAT+ inputs</v-tooltip>
				</v-list-item>
				<v-list-item prepend-icon="fas fa-play" to="/run">
					<v-tooltip activator="parent" location="end">Run SWAT+</v-tooltip>
				</v-list-item>
				<v-list-item prepend-icon="fas fa-check" to="/output">
					<v-tooltip activator="parent" location="end">SWAT+ Output Check</v-tooltip>
				</v-list-item>
			</v-list>

			<template #append>
				<v-list density="compact" nav>
					<v-list-item prepend-icon="fas fa-circle-question" to="/help">
						<v-tooltip activator="parent" location="end">Help</v-tooltip>
					</v-list-item>
					<v-list-item :prepend-icon="page.colorTheme === 'light' ? 'fas fa-sun' : 'fas fa-moon'" @click="toggleColorTheme">
						<v-tooltip activator="parent" location="end">Toggle color theme</v-tooltip>
					</v-list-item>
				</v-list>
			</template>
		</v-navigation-drawer>

		<div v-if="route.path === '/'">
			<v-main v-if="page.loading">
				<page-loading :loading="page.loading"></page-loading>
			</v-main>
			<v-main v-else-if="!formatters.isNullOrEmpty(page.error)">
				<h1>SWAT+ Editor {{ constants.appSettings.version }}</h1>
				<v-alert color="info" icon="$info">
					<template #text>
						<p>SWAT+ Editor encountered an error: {{page.error}}</p>
						<p>
							Check to make sure SWAT+ Editor is working properly by checking the Help page and scrolling to the bottom.
							Contact the developer if needed. First, you might try reloading in case your computer is slow to open the APIs:
						</p>
						<v-btn @click="getInfo" :loading="page.loading">Reload SWAT+ Editor</v-btn>
					</template>
				</v-alert>
			</v-main>
			<div v-else-if="!currentProject.hasCurrentProject">

			</div>
			<div v-else>
				<v-navigation-drawer permanent id="secondary-nav">
					<div class="pa-3">
						<h1 class="mb-2 text-h6">SWAT+ Editor {{ constants.appSettings.version }}</h1>
						<p class="mb-5">
							<open-in-browser class="text-primary" url="https://swatplus.gitbook.io/docs/release-notes" text="Read our release notes" />
							to learn more about this release.
						</p>

						<div class="mb-7">
							<v-btn variant="flat" color="primary" block @click="page.open.show = true" class="mb-2">Open another project</v-btn>
							<v-btn variant="tonal" color="primary" block @click="page.create.show = true">Create a new project</v-btn>
						</div>

						<div v-if="recentProjects.length > 0" class="mt-4">
							<h2 class="mb-2 text-h6">Recent Projects</h2>
							<ul class="plain-border text-body-2">
								<li v-for="(project, i) in recentProjects" :key="i" class="d-flex">
									<a href="#" :title="project.projectDb" :class="project.projectDb === currentProject.projectDb ? 'font-italic' : null"
										@click.prevent="loadProject(project)">{{project.name}}</a>
									<a class="ml-auto text-medium icon" href="#"
										@click.prevent="removeProject(project)"
										:title="'Remove ' + project.name + ' from recent projects list'">
										<font-awesome-icon :icon="['fas', 'times']" /></a>
								</li>
							</ul>
						</div>
					</div>
				</v-navigation-drawer>

				<v-main>

					<v-bottom-navigation id="action-bar" elevation="0" border="t" grow>
						<v-btn to="/run" :active="false">
							<v-icon>fas fa-play</v-icon> Run Model
						</v-btn>
						<swat-plus-toolbox-button text="SWAT+ Toolbox" :ran-swat="info.status.ran_swat"></swat-plus-toolbox-button>
						<v-btn @click="openEditProject" :active="false">
							<v-icon>fas fa-pen-to-square</v-icon> Change Name
						</v-btn>
						<v-btn @click="page.close.removeFromRecent=false; page.close.show=true" :active="false">
							<v-icon>fas fa-circle-xmark</v-icon> Close Project
						</v-btn>
						<v-btn @click="utilities.exit" :active="false">
							<v-icon>fas fa-arrow-right-from-bracket</v-icon> Quit
						</v-btn>
					</v-bottom-navigation>
				</v-main>
			</div>
		</div>
		<router-view></router-view>
	</div>
</template>
