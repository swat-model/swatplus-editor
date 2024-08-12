<script setup lang="ts">
	import { reactive, onMounted, onUnmounted, watch } from 'vue';
	import { useRoute } from 'vue-router';
	import { useTheme, useDisplay } from 'vuetify';
	import { useHelpers } from '@/helpers';
	import SwatPlusToolboxButton from '../components/SwatPlusToolboxButton.vue';
	import { ProjectSettings } from '@/typings';

	const route = useRoute();
	const theme = useTheme();
	const { mobile } = useDisplay();
	const { api, constants, errors, formatters, currentProject, runProcess, utilities } = useHelpers();
	
	let page:any = reactive({
		error: null,
		loading: false,
		colorTheme: 'light',
		secondaryNav: !mobile.value,
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
			datasetsDb: utilities.getDatabaseInstallPath(),
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
		getColorTheme();
		if (route.path === '/') {
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
			chart: { styledMode: true },
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

		if (formatters.isNullOrEmpty(page.edit.name)) {
			page.edit.error = 'Please enter a name for your project.';
		} else {
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
				'--project_description='+ project.description,
				'--copy_datasets_db=y'
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

		task.currentPid = runProcess.runApiProc('setup', 'swatplus_api', args);
	}

	let listeners:any = {
		stdout: undefined,
		stderr: undefined,
		close: undefined
	}

	function initRunProcessHandlers() {
		listeners.stdout = runProcess.processStdout('setup', (data:any) => {
			task.progress = runProcess.getApiOutput(data);
		});
		
		listeners.stderr = runProcess.processStderr('setup', (data:any) => {
			console.log(`stderr: ${data}`);
			task.error = data;
			task.running = false;
		});
		
		listeners.close = runProcess.processClose('setup', async (code:any) => {
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
	}

	function removeRunProcessHandlers() {
		if (listeners.stdout) listeners.stdout();
		if (listeners.stderr) listeners.stderr();
		if (listeners.close) listeners.close();
	}

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
		if (colorTheme === null) colorTheme = utilities.getColorTheme();
		setColorTheme(colorTheme);
		//console.log(theme.current.value.colors)
	}

	function setColorTheme(colorTheme:string|null):void {
		if (colorTheme === null || colorTheme === 'system') colorTheme = 'light';
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

	onMounted(async () => {
		initRunProcessHandlers();
		await init();
	});
	onUnmounted(() => removeRunProcessHandlers());

	watch(
		() => route.name,
		async () => await init()
	)

	async function sleep(ms:number|undefined) {
		return new Promise(resolve => setTimeout(resolve, ms));
	}
</script>

<template>
	<div>
		<v-navigation-drawer theme="dark" rail permanent>
			<div class="px-2">
				<v-tooltip location="end" text="Expand menu">
					<template v-slot:activator="{ props }">
						<v-app-bar-nav-icon v-bind="props" v-if="mobile && route.path === '/' && formatters.isNullOrEmpty(page.error) && currentProject.hasCurrentProject" 
							rounded="0" variant="text" @click.stop="page.secondaryNav = !page.secondaryNav"></v-app-bar-nav-icon>
					</template>
				</v-tooltip>
			</div>
			<v-list density="compact" nav>
				<v-list-item prepend-icon="fas fa-folder-open" to="/" :active="route.path === '/'">
					<v-tooltip activator="parent" location="end">Project setup and information</v-tooltip>
				</v-list-item>
				<v-list-item prepend-icon="fas fa-pencil-alt" to="/edit">
					<v-tooltip activator="parent" location="end">Edit SWAT+ inputs</v-tooltip>
				</v-list-item>
				<v-list-item prepend-icon="fas fa-play" to="/run">
					<v-tooltip activator="parent" location="end">Run SWAT+</v-tooltip>
				</v-list-item>
				<v-list-item prepend-icon="fas fa-check" to="/check">
					<v-tooltip activator="parent" location="end">SWAT+ Output Check</v-tooltip>
				</v-list-item>
			</v-list>

			<template #append>
				<v-list density="compact" nav>
					<v-list-item prepend-icon="fas fa-circle-info" v-if="currentProject.hasCurrentProject" class="pointer">
						<v-menu activator="parent" location="end" open-on-hover>
							<v-list density="compact">
								<v-list-subheader>SWAT+ Editor {{ constants.appSettings.version }}</v-list-subheader>
								<v-list-item>{{currentProject.name}}</v-list-item>
								<v-list-item><open-file :file-path="info.file_path" class="text-primary text-decoration-none">Open project directory</open-file></v-list-item>
							</v-list>
						</v-menu>
					</v-list-item>
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
				<div class="py-3 px-6">
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
				</div>
			</v-main>
			<div v-else-if="!currentProject.hasCurrentProject">
				<v-main>
					<div class="py-3 px-6">
						<v-sheet elevation="2" max-width="800" rounded="lg" width="100%" class="my-4 pa-4 text-center mx-auto">
							<h2 class="text-h5 mb-6">Welcome to SWAT+ Editor {{constants.appSettings.version}}</h2>

							<p class="mb-4 text-medium-emphasis">
								<open-in-browser url="https://swatplus.gitbook.io/docs/release-notes"  text="Read our release notes" /> to learn more about this release.
							</p>

							<div v-if="recentProjects.length > 0" class="my-5">
								<h2 class="text-h6 text-center">Recent Projects</h2>
								<ul class="plain-border">
									<li v-for="(project, i) in recentProjects" :key="i" class="d-flex">
										<a href="#" :title="project.projectDb" :class="project.projectDb === currentProject.projectDb ? 'font-italic text-primary' : 'text-primary'"
											@click.prevent="loadProject(project)">{{project.name}}</a>
										<a class="ml-auto text-medium icon" href="#"
											@click.prevent="removeProject(project)"
											:title="'Remove ' + project.name + ' from recent projects list'">
											<font-awesome-icon :icon="['fas', 'times']" /></a>
									</li>
								</ul>
							</div>

							<div>
								<v-btn class="text-none mr-2" color="primary" rounded variant="flat" @click="page.open.show = true">Open a project</v-btn>
								<v-btn class="text-none" color="secondary" rounded variant="tonal" @click="page.create.show = true">Create a new project</v-btn>
							</div>
						</v-sheet>
					</div>
				</v-main>
			</div>
			<div v-else>
				<v-navigation-drawer v-model="page.secondaryNav" id="secondary-nav">
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
									<a href="#" :title="project.projectDb" :class="project.projectDb === currentProject.projectDb ? 'font-italic text-primary' : 'text-primary'"
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
					<div class="py-3 px-6">
						<v-card class="mb-6">
							<v-card-title>{{currentProject.name}}</v-card-title>
							<v-card-subtitle v-if="!formatters.isNullOrEmpty(currentProject.description)">{{formatters.toReadable(currentProject.description||'')}}</v-card-subtitle>
							<v-card-actions>
								<open-file button :file-path="info.file_path" variant="text" size="small" icon="fas fa-folder-open"></open-file>
								<v-btn v-if="versionSupport.supported" @click="openEditProject" variant="text" size="small" icon="fas fa-pen-to-square" title="Change name/description"></v-btn>
								<v-spacer></v-spacer>
								<open-file button :file-path="info.file_path" variant="text" size="small" color="surface-variant"><code style="text-transform: none !important;">{{info.file_path}}</code></open-file>
							</v-card-actions>
						</v-card>

						<v-alert type="error" v-if="!formatters.isNullOrEmpty(versionSupport.error)" class="mb-6">
							{{ versionSupport.error }}
						</v-alert>

						<div v-if="versionSupport.supported">
							<v-row v-if="info.status.imported_weather || info.status.wrote_inputs">
								<v-col :md="info.scenarios.length > 0 ? 6 : 12" cols="12">
									<v-card>
										<v-list density="compact">
											<v-list-subheader class="text-uppercase">Project Status</v-list-subheader>
											<v-list-item to="/edit/climate/stations">
												<template #prepend>
													<v-icon :color="info.status.imported_weather ? 'success' : 'plain'">{{ info.status.imported_weather ? 'fas fa-check' : 'fas fa-minus' }}</v-icon>
												</template>
												Set up weather stations and weather generators
											</v-list-item>
											<v-list-item to="/run">
												<template #prepend>
													<v-icon :color="info.status.wrote_inputs ? 'success' : 'plain'">{{ info.status.wrote_inputs ? 'fas fa-check' : 'fas fa-minus' }}</v-icon>
												</template>
												Wrote SWAT+ input files
											</v-list-item>
											<v-list-item to="/run">
												<template #prepend>
													<v-icon :color="info.status.ran_swat ? 'success' : 'plain'">{{ info.status.ran_swat ? 'fas fa-check' : 'fas fa-minus' }}</v-icon>
												</template>
												Ran SWAT+
											</v-list-item>
											<v-list-item to="/run">
												<template #prepend>
													<v-icon :color="info.status.imported_output ? 'success' : 'plain'">{{ info.status.imported_output ? 'fas fa-check' : 'fas fa-minus' }}</v-icon>
												</template>
												Imported SWAT+ output into a database for analysis
											</v-list-item>
										</v-list>
									</v-card>
								</v-col>
								<v-col v-if="info.scenarios.length > 0" md="6">
									<v-card>
										<v-list density="compact">
											<v-list-subheader class="text-uppercase">Saved Scenarios</v-list-subheader>
											<v-list-item v-for="(s, i) in info.scenarios" :key="i" @click="askLoadScenario(s)">{{ s.name }}</v-list-item>
										</v-list>
									</v-card>
								</v-col>
							</v-row>

							<h2 class="mt-6 mb-4 dash-heading">SWAT+ Project Information</h2>

							<v-row>
								<v-col cols="12" md="6">
									<v-card>
										<v-table>
											<tbody>
												<tr>
													<th>Total area</th>
													<td>{{formatters.toNumberFormat(info.total_area, 2)}} ha</td>
												</tr>
												<tr>
													<th>Simulation period</th>
													<td>
														{{info.simulation.yrc_start}}
														{{info.simulation.day_start > 0 ? 'day ' + info.simulation.day_start : ''}}
														- 
														{{info.simulation.yrc_end}}
														{{info.simulation.day_end > 0 ? 'day ' + info.simulation.day_end : ''}}
													</td>
												</tr>
											</tbody>
										</v-table>
									</v-card>
								</v-col>
								<v-col cols="12" md="6">
									<v-card>
										<v-table>
											<tbody>
												<tr>
													<th>Software</th>
													<td>SWAT+ Editor {{info.editor_version}}<span v-if="info.status.using_gis">, {{info.gis_version}}</span></td>
												</tr>
												<tr>
													<th>Last saved</th>
													<td>{{formatters.toDate(info.last_modified)}}</td>
												</tr>
											</tbody>
										</v-table>
									</v-card>
								</v-col>
							</v-row>

							<v-row>
								<v-col cols="12" md="6">
									<v-card>
										<v-card-subtitle class="text-uppercase mt-3">Object totals</v-card-subtitle>
										<v-table density="comfortable" class="mt-1 mb-11">
											<tbody>
												<tr v-if="info.status.using_gis">
													<td class="text-right min">{{info.totals.subs}}</td>
													<td>Subbasins</td>
												</tr>
												<tr v-if="info.totals.lhru > 0">
													<td class="text-right min">{{info.totals.lhru}}</td>
													<td><router-link class="text-primary" to="/edit/cons/hrus-lte">HRUs</router-link></td>
												</tr>
												<tr v-else>
													<td class="text-right min">{{info.totals.hru}}</td>
													<td><router-link class="text-primary" to="/edit/cons/hrus">HRUs</router-link></td>
												</tr>
												<tr>
													<td class="text-right min">{{info.totals.cha > 0 ? info.totals.cha : info.totals.lcha}}</td>
													<td><router-link class="text-primary" to="/edit/cons/channels">Channels</router-link></td>
												</tr>
												<tr v-if="!info.is_lte">
													<td class="text-right min">{{info.totals.aqu}}</td>
													<td><router-link class="text-primary" to="/edit/cons/aquifers">Aquifers</router-link></td>
												</tr>
												<tr v-if="!info.is_lte">
													<td class="text-right min">{{info.totals.res}}</td>
													<td><router-link class="text-primary" to="/edit/cons/reservoirs">Reservoirs</router-link></td>
												</tr>
												<tr v-if="!info.is_lte">
													<td class="text-right min">{{info.totals.rtu}}</td>
													<td><router-link class="text-primary" to="/edit/cons/routing-units">Routing Units</router-link></td>
												</tr>
												<tr>
													<td class="text-right min">{{info.totals.lsus}}</td>
													<td><router-link class="text-primary" to="/edit/regions/ls_units">Landscape Units</router-link></td>
												</tr>
												<tr v-if="!info.is_lte">
													<td class="text-right min">{{info.totals.rec}}</td>
													<td><router-link class="text-primary" to="/edit/cons/recall">Point Sources / Inlets</router-link></td>
												</tr>
											</tbody>
										</v-table>
									</v-card>
								</v-col>
								<v-col cols="12" md="6">
									<v-card>
										<v-card-text class="py-4 highcharts-dashboards-dark"><highcharts :options="charts.landuse"></highcharts></v-card-text>
									</v-card>
								</v-col>
							</v-row>
						</div>
						<v-card v-else-if="versionSupport.updatable">
							<v-card-item>
								<p class="mt-3">
									You must update your project to continue using it in this version of SWAT+ Editor.
									If you do not wish to update your project, please uninstall this version of the editor and
									<open-in-browser url="https://swatplus.gitbook.io/docs/installation"  text="install a compatible earlier version" class="text-primary" />.
								</p>
								<p>
									Your project database may be modified during the upgrade. We will make a backup of the database and store it in the Backups folder 
									within your project directory. There may be changes to the model inputs, so we recommend you <open-in-browser url="https://swatplus.gitbook.io/docs/release-notes"  text="read our full release notes" class="text-primary" />
									to see what has changed <strong>before</strong> upgrading your project.
								</p>
								<p>
									<v-btn @click="updateProject" variant="flat" color="primary" size="large">
										Update Project
									</v-btn>
								</p>
							</v-card-item>
						</v-card>
					</div>					

					<v-bottom-navigation id="action-bar" elevation="0" border="t" grow>
						<v-btn v-if="versionSupport.supported && info.status.imported_weather && !mobile" to="/run" :active="false">
							<v-icon>fas fa-play</v-icon> Run Model
						</v-btn>
						<v-btn v-else-if="versionSupport.supported && !mobile" to="/edit" :active="false">
							<v-icon>fas fa-pencil-alt</v-icon> Get Started
						</v-btn>
						<v-btn v-else-if="versionSupport.updatable" @click="updateProject" :active="false">
							<v-icon>fas fa-circle-up</v-icon> Update Project
						</v-btn>

						<swat-plus-toolbox-button v-if="versionSupport.supported && !info.is_lte" text="SWAT+ Toolbox" :ran-swat="info.status.ran_swat"></swat-plus-toolbox-button>

						<v-btn v-if="versionSupport.supported" @click="openEditProject" :active="false">
							<v-icon>fas fa-pen-to-square</v-icon> Change Name
						</v-btn>
						<v-btn v-if="versionSupport.supported && info.status.using_gis" @click="reimportGis" :active="false">
							<v-icon>fas fa-globe</v-icon> Re-import from GIS
						</v-btn>
						<v-btn @click="page.close.removeFromRecent=false; page.close.show=true" :active="false">
							<v-icon>fas fa-circle-xmark</v-icon> Close Project
						</v-btn>
						<v-btn v-if="!mobile" @click="utilities.exit" :active="false">
							<v-icon>fas fa-arrow-right-from-bracket</v-icon> Quit
						</v-btn>
					</v-bottom-navigation>
				</v-main>
			</div>

			<v-dialog v-model="page.open.show" :max-width="constants.dialogSizes.md">
				<v-card title="Open Project">
					<v-card-text>
						<select-file-input v-model="page.open.projectDb" :value="page.open.projectDb" label="Select your project/GIS SQLite database file" file-type="sqlite" required invalid-feedback="Select a SQLite database file"></select-file-input>
					</v-card-text>
					<v-divider></v-divider>
					<v-card-actions>
						<v-btn :loading="page.open.loading" @click="openProject" color="primary" variant="text">Open</v-btn>
						<v-btn @click="page.open.show = false">Cancel</v-btn>
					</v-card-actions>
				</v-card>
			</v-dialog>

			<v-dialog v-model="page.close.show" :max-width="constants.dialogSizes.md">
				<v-card title="Close Current Project?">
					<v-card-text>
						<p>
							This will close the project currently open, <strong>{{currentProject.name}}</strong>. Are you sure?
						</p>
					</v-card-text>
					<v-divider></v-divider>
					<v-card-actions>
						<v-btn @click="closeCurrentProject" color="primary" variant="text">Yes</v-btn>
						<v-btn @click="page.close.show = false">No</v-btn>
					</v-card-actions>
				</v-card>
			</v-dialog>

			<v-dialog v-model="page.edit.show" :max-width="constants.dialogSizes.md">
				<v-card title="Update Project Name and Description">
					<v-card-text>
						<error-alert :text="page.edit.error"></error-alert>

						<v-text-field v-model="page.edit.name" :rules="[constants.formRules.required]"
							label="Project display name"></v-text-field>

						<v-text-field v-model="page.edit.description" :rules="[constants.formRules.max(25, page.edit.description)]"
							label="Briefly describe your project location (main river, country)" 
							hint="25 character limit; spaces will be converted to underscores"></v-text-field>
					</v-card-text>
					<v-divider></v-divider>
					<v-card-actions>
						<v-btn @click="editProject" :loading="page.edit.saving" color="primary" variant="text">Save</v-btn>
						<v-btn @click="page.edit.show = false">Cancel</v-btn>
					</v-card-actions>
				</v-card>
			</v-dialog>

			<v-dialog v-model="page.import.show" :max-width="constants.dialogSizes.md" persistent>
				<v-card title="Start SWAT+ Editor Project from QSWAT+">
					<v-card-text>
						<error-alert :text="page.open.error"></error-alert>			
						<error-alert :text="page.import.error"></error-alert>
						<stack-trace-error v-if="!formatters.isNullOrEmpty(task.error)" error-title="There was an error importing your GIS data." :stack-trace="task.error.toString()" />
						
						<div v-if="task.running">
							<v-progress-linear :model-value="task.progress.percent" color="primary" height="15" striped></v-progress-linear>
							<p>
								{{task.progress.message}}
							</p>
						</div>
						<div v-else-if="formatters.isNullOrEmpty(task.error)">
							<p>
								This is the first time opening your QSWAT+ project in SWAT+ Editor. We need to import your GIS data into SWAT+ objects.
								This may take a few seconds to several minutes depending on the size of your project.
							</p>

							<v-form>
								<v-text-field v-model="page.import.project.name" :rules="[constants.formRules.required]"
									label="Project display name"></v-text-field>

								<v-text-field v-model="page.import.project.description" :rules="[constants.formRules.max(25, page.edit.description)]"
									label="Briefly describe your project location (main river, country)" 
									hint="25 character limit; spaces will be converted to underscores"></v-text-field>

								<v-checkbox v-model="page.import.project.isLte" class="mt-4">
									<template #label>
										Use SWAT+ lte? This is a lite version of the model that greatly simplifies hydrology and plant growth and 
										does not simulate nutrients, concentrating on gully formation and stream degradation.
									</template>
								</v-checkbox>
							</v-form>
						</div>
					</v-card-text>
					<v-divider></v-divider>
					<v-card-actions>
						<v-btn v-if="formatters.isNullOrEmpty(task.error)" :loading="task.running" @click="importProject" color="primary" variant="text">Start</v-btn>
						<v-btn @click="cancelTask">Cancel</v-btn>
					</v-card-actions>
				</v-card>
			</v-dialog>

			<v-dialog v-model="page.loadScenario.show" :max-width="constants.dialogSizes.md" persistent>
				<v-card title="Load Scenario">
					<v-card-text>
						<error-alert :text="page.loadScenario.error"></error-alert>
						<stack-trace-error v-if="!formatters.isNullOrEmpty(task.error)" error-title="There was an error loading your scenario." :stack-trace="task.error.toString()" />
						
						<div v-if="task.running">
							<v-progress-linear :model-value="task.progress.percent" color="primary" height="15" striped></v-progress-linear>
							<p>
								{{task.progress.message}}
							</p>
						</div>
						<div v-else-if="formatters.isNullOrEmpty(task.error)">
							<p>
								Are you sure you want to load the scenario, <strong>{{page.loadScenario.scenario.name}}</strong>?
								Loading the scenario will <strong class="text-error">replace</strong> everything currently loaded 
								in the editor (the default scenario), so please make sure any changes are saved as a new scenario if you wish 
								to keep them. Scenarios can be saved from the <router-link to="/run" class="text-primary">run model screen</router-link>.
							</p>
							<p>
								<strong class="text-error">WARNING:</strong> if you have QGIS open, you may need to completely close it first
								because it locks some of the files we need to replace. Make sure QGIS is not open, then open just SWAT+ Editor on its 
								own before loading the scenario. SWAT+ Editor can be launched in Windows by searching "SWAT+ Editor" in the search bar.
							</p>
						</div>
					</v-card-text>
					<v-divider></v-divider>
					<v-card-actions>
						<v-btn v-if="formatters.isNullOrEmpty(task.error)" :loading="task.running" @click="loadScenario" color="primary" variant="text">Load Scenario</v-btn>
						<v-btn @click="cancelTask">Cancel</v-btn>
					</v-card-actions>
				</v-card>
			</v-dialog>

			<v-dialog v-model="page.create.show" :max-width="constants.dialogSizes.lg" persistent>
				<v-card title="Create a New SWAT+ Editor Project">
					<v-card-text>
						<stack-trace-error v-if="!formatters.isNullOrEmpty(task.error)" error-title="There was an error creating your project." :stack-trace="task.error.toString()" />
						
						<div v-if="task.running">
							<v-progress-linear :model-value="task.progress.percent" color="primary" height="15" striped></v-progress-linear>
							<p>
								{{task.progress.message}}
							</p>
						</div>
						<div v-else-if="formatters.isNullOrEmpty(task.error)">
							<p>
								It is strongly recommended to start your new SWAT+ project from within the QSWAT+ interface.
								QSWAT+ will set up your watershed and direct you to the editor after HRU delineation. For help using QSWAT+,
								please <open-in-browser url="https://swat.tamu.edu/software/plus/"  text="visit our website" />.
							</p>
							<p>
								However, it is not required to use GIS to start your project. Complete the form below to start a SWAT+ Editor project from scratch.
								A project database will be created for you and you will need to input your spatial connections manually. If you already have
								a project database, click cancel below and choose the open project button instead.
							</p>

							<error-alert :text="page.create.error"></error-alert>

							<v-form>
								<v-text-field v-model="page.create.name" :rules="[constants.formRules.required]" class="mb-3"
									label="Project display name"></v-text-field>

								<v-text-field v-model="page.create.description" :rules="[constants.formRules.max(25, page.edit.description)]" class="mb-3"
									label="Briefly describe your project location (main river, country)" 
									hint="25 character limit; spaces will be converted to underscores"></v-text-field>

								<select-folder-input v-model="page.create.projectFolder" :value="page.create.projectFolder" class="mb-3"
									label="Select your project folder"
									hint="This will be where we create your project SQLite database file" persistent-hint
									required invalidFeedback="Please select a folder"></select-folder-input>

								<select-file-input v-model="page.create.datasetsDb" :value="page.create.datasetsDb" class="mb-3"
									label="Select your SWAT+ datasets SQLite database file"
									hint="This will be copied to your project folder above" persistent-hint
									fileType="sqlite" required 
									invalidFeedback="Please select a SQLite database file"></select-file-input>

								<v-checkbox v-model="page.create.isLte" class="mt-4">
									<template #label>
										Use SWAT+ lte? This is a lite version of the model that greatly simplifies hydrology and plant growth and 
										does not simulate nutrients, concentrating on gully formation and stream degradation. 
									</template>
								</v-checkbox>
							</v-form>
						</div>
					</v-card-text>
					<v-divider></v-divider>
					<v-card-actions>
						<v-btn v-if="formatters.isNullOrEmpty(task.error)" :loading="page.create.loading || task.running" @click="createProject" color="primary" variant="text">Create</v-btn>
						<v-btn @click="cancelTask">Cancel</v-btn>
					</v-card-actions>
				</v-card>
			</v-dialog>

			<v-dialog v-model="page.openConfirm.show" :max-width="constants.dialogSizes.md" persistent>
				<v-card title="Has your watershed changed?">
					<v-card-text>
						<stack-trace-error v-if="!formatters.isNullOrEmpty(task.error)" error-title="There was an error re-importing your project GIS data." :stack-trace="task.error.toString()" />
						
						<div v-if="task.running">
							<v-progress-linear :model-value="task.progress.percent" color="primary" height="15" striped></v-progress-linear>
							<p>
								{{task.progress.message}}
							</p>
						</div>
						<div v-else-if="formatters.isNullOrEmpty(task.error)">
							<p v-if="!page.openConfirm.reimportMessage">
								Did you run steps 1 or 2 of QSWAT+ since last opening SWAT+ Editor?
								If so, we'll need to re-import your watershed data. 
							</p>
							<p v-else>
								Did you run steps 1 or 2 of QSWAT+ since last opening SWAT+ Editor, 
								or would you like to start over or switch between full SWAT+ and SWAT+ lte?
								If so, we'll need to re-import your watershed data.
								Warning: you may lose any changes you've made in the editor so far.
							</p>

							<v-checkbox v-model="page.openConfirm.project.isLte" class="mt-4">
								<template #label>
									Use SWAT+ lte? This is a lite version of the model that greatly simplifies hydrology and plant growth and 
									does not simulate nutrients, concentrating on gully formation and stream degradation. 
								</template>
							</v-checkbox>
						</div>
					</v-card-text>
					<v-divider></v-divider>
					<v-card-actions>
						<v-btn @click="confirmOpen" color="primary" variant="text">No, continue to editor</v-btn>
						<v-btn v-if="formatters.isNullOrEmpty(task.error)" :loading="task.running" @click="reImportProject" color="primary" variant="text">Yes, import new watershed</v-btn>
						<v-btn v-if="task.running || !formatters.isNullOrEmpty(task.error)" @click="cancelTask">Cancel</v-btn>
					</v-card-actions>
				</v-card>
			</v-dialog>

			<v-dialog v-model="page.update.show" :max-width="constants.dialogSizes.md" persistent>
				<v-card title="Updating Project">
					<v-card-text>
						<error-alert :text="page.update.error"></error-alert>
						<stack-trace-error v-if="!formatters.isNullOrEmpty(task.error)" error-title="There was an error updating your project." :stack-trace="task.error.toString()" />
						
						<div v-if="task.running">
							<v-progress-linear :model-value="task.progress.percent" color="primary" height="15" striped></v-progress-linear>
							<p>
								{{task.progress.message}}
							</p>
						</div>
					</v-card-text>
					<v-divider></v-divider>
					<v-card-actions>
						<v-btn @click="cancelTask">Cancel</v-btn>
					</v-card-actions>
				</v-card>
			</v-dialog>

			<v-dialog v-model="page.noProject.show" :max-width="constants.dialogSizes.md">
				<v-card title="Project Not Found">
					<v-card-text>
						<p>
							The project's files cannot be found. Please use the open project button to select the project database file.
						</p>
					</v-card-text>
					<v-divider></v-divider>
					<v-card-actions>
						<v-btn @click="page.noProject.show = false">OK</v-btn>
					</v-card-actions>
				</v-card>
			</v-dialog>
		</div>
		
		<router-view></router-view>
	</div>
</template>
