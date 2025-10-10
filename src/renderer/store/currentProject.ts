import { defineStore } from 'pinia';
import { ref, computed, reactive } from 'vue';
import { useUtilities } from '../helpers/utilities';
import { ProjectSettings } from 'typings';

export const useCurrentProject = defineStore('project', () => {
	const electron = window.electronApi;
	const utilities = useUtilities();

	const projectDb = ref<string|null>(null);
	const datasetsDb = ref<string|null>(null);
	const name = ref<string|null>(null);
	const description = ref<string|null>(null);
	const version = ref<string|null>(null);
	const isLte = ref<boolean>(false);
	const hasLoadedCommandLine = ref<boolean>(false);

	const hasCurrentProject = computed(() => !!projectDb.value)
	const isSupported = computed(() => {
		if (!hasCurrentProject) return false;
		let versionSupport = utilities.getVersionSupport(version.value||'');
        return versionSupport.supported;
	})

	const projectPath = computed(() => {
		return electron.pathDirectoryName(projectDb.value||'');
	})

	const projectDbUrl = computed(() => {
		return encodeURIComponent(projectDb.value||'');
	})

	const txtInOutPath = computed(() => {
		let pp = electron.pathDirectoryName(projectDb.value||'');
		let txtinout = electron.joinPaths([pp, 'Scenarios', 'Default', 'TxtInOut']);

		if (!electron.pathExists(txtinout))
			txtinout = pp;

		return txtinout;
	})

	const scenariosPath = computed(() => {
		let pp = electron.pathDirectoryName(projectDb.value||'');
		let scenarios = electron.joinPaths([pp, 'Scenarios']);

		if (!electron.pathExists(scenarios))
			scenarios = pp;

		return scenarios;
	})

	function setHasLoadedCommandLine(loaded:boolean):void {
		hasLoadedCommandLine.value = loaded;
	}

	function getObject():ProjectSettings {
		let project:ProjectSettings = {
			projectDb: projectDb.value,
			datasetsDb: datasetsDb.value,
			name: name.value,
			description: description.value,
			version: version.value,
			isLte: isLte.value,
		};
		return project;
	}

	function setCurrentProject(project:any):void {
		projectDb.value = project.projectDb;
		datasetsDb.value = project.datasetsDb;
		name.value = project.name;
		description.value = project.description;
		version.value = project.version;
		isLte.value = project.isLte;
	}

	function getApiHeader() {
		let headerDict:any = {};
		if (projectDb.value !== null) headerDict['Project-Db'] = projectDb.value;
		if (datasetsDb.value !== null) headerDict['Datasets-Db'] = datasetsDb.value;
		return { headers: headerDict };
	}

	function getTempApiHeader(customProjectDb:any) {
		return { headers: { 'Project-Db': customProjectDb }}
	}

	return {
		projectDb, datasetsDb, name, description, version, isLte, hasLoadedCommandLine,
		hasCurrentProject, projectPath, txtInOutPath, scenariosPath, projectDbUrl,
		setHasLoadedCommandLine, getObject, setCurrentProject, getApiHeader, getTempApiHeader, isSupported
	}
})