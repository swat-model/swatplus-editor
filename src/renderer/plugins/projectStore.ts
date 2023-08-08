import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

export const useProjectStore = defineStore('project', () => {
	const electron = window.electronApi;

	const projectDb = ref<string|null>(null);
	const datasetsDb = ref<string|null>(null);
	const name = ref<string|null>(null);
	const description = ref<string|null>(null);
	const version = ref<string|null>(null);
	const isLte = ref<boolean>(false);

	const hasCurrentProject = computed(() => !!projectDb.value)

	const projectPath = computed(() => {
		if (!!projectDb.value) return null;
		return electron.pathDirectoryName(projectDb.value||'');
	})

	const txtInOutPath = computed(() => {
		if (!!projectDb.value) return null;
		let pp = electron.pathDirectoryName(projectDb.value||'');
		let txtinout = electron.joinPaths([pp, 'Scenarios', 'Default', 'TxtInOut']);

		if (!electron.pathExists(txtinout))
			txtinout = pp;

		return txtinout;
	})

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
		if (projectDb.value !== null) headerDict['project_db'] = projectDb.value;
		if (datasetsDb.value !== null) headerDict['datasets_db'] = datasetsDb.value;
		return { headers: headerDict };
	}

	return {
		projectDb, datasetsDb, name, description, version, isLte,
		hasCurrentProject, projectPath, txtInOutPath,
		setCurrentProject, getApiHeader
	}
})