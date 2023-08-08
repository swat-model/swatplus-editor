import { useApi } from './api';
import { useProjectStore } from './projectStore';
import { useFormatters } from './formatters';
import { useConstants } from './constants';

export function useUtilities() {
	const electron = window.electronApi;
	const api = useApi();
	const currentProject = useProjectStore();
	const formatters = useFormatters();
	const constants = useConstants();

	const appPath = electron.getAppPath().replace('app.asar', 'app.asar.unpacked');

	function pathExists(path:string) {
		return electron.pathExists(path);
	}

	function joinPaths(paths:[]) {
		return electron.joinPaths(paths);
	}

	function getAutoComplete(type:string, name:any) {
		if (formatters.isNullOrEmpty(name))
			return api.get(`autocomplete-np/${type}`, currentProject.getApiHeader());
		return api.get(`autocomplete/${type}/${name}`, currentProject.getApiHeader());
	}

	function getAutoCompleteId(type:string, name:any) {
		return api.get(`autocomplete/id/${type}/${name}`, currentProject.getApiHeader());
	}

	function getVersionSupport(version:string) {
		let support = {
			supported: false,
			updatable: false,
			error: ''
		};

		if (constants.appSettings.version === null) {
			support.error = 'Software version is not set.';
		}
		else if (constants.appSettings.version === version) {
			support.supported = true;
		}
		else {
			let softwareMajor = Number(constants.appSettings.version.substring(0, 3));
			let myMajor = Number(version.substring(0, 3));

			if (softwareMajor > myMajor) {
				support.updatable = true;
				support.error = `Your project was made using an earlier version of SWAT+ Editor. Your project is version ${version} and the editor is version ${constants.appSettings.version}.`;
			} else if (softwareMajor < myMajor) {
				support.supported = true;
				support.error = `Your project was made using a version of SWAT+ Editor that is greater than the current version. Your project is version ${version} and the editor is version ${constants.appSettings.version}. You may encounter errors if the model has changed. Proceed at your own risk.`;
			} else {
				support.supported = true;
			}
		}
		
		return support;
	}

	function addSetting(key:string, value:any) {
		electron.addToStore(key, JSON.stringify(value));
	};

	function getSetting(key:string) {
		try {
			return JSON.parse(electron.getStoreSetting(key));
		} catch (error) {
			deleteSetting(key);
			return undefined;
		}
	};

	function deleteSetting(key:string) {
		electron.deleteFromStore(key);
	};

	function getMostRecentProject() {
		let recent = getSetting('recentProjects');
		if (recent === undefined || recent.length < 1) return undefined;
		return recent[0];
	}

	function getRecentProjects() {
		let recent = getSetting('recentProjects');
		if (recent === undefined) recent = [];
		return recent;
	}

	function pushRecentProject(project:any) {
		let recent = getSetting('recentProjects');
		if (recent === undefined) recent = [];

		let exists = recent.filter(function(el:any) { return el.projectDb === project.projectDb; })[0];
		if (exists) {
			let newProjects = recent.filter(function(el:any) { return el.projectDb !== project.projectDb; });
			newProjects.unshift(project);

			if (newProjects.length > 4)
				newProjects.pop();

			addSetting('recentProjects', newProjects);
		}

		if (exists === undefined) {
			recent.unshift(project);

			if (recent.length > 4)
				recent.pop();

			addSetting('recentProjects', recent);
		}
	}

	function deleteRecentProject(project:any) {
		let recent = getSetting('recentProjects');
		if (recent === undefined) recent = [];

		let filtered = recent.filter(function(el:any) { return el.projectDb !== project.projectDb; });
		addSetting('recentProjects', filtered);
		return filtered;
	}

	function getObjTypeRoute(item:any) {
		let route = constants.objTypeRouteTable[item.obj_typ].path;
		if (route === '#')
			return route;

		if ('obj_id' in item)
			return route + item.obj_id;
		else if ('obj_typ_no' in item)
			return route + item.obj_typ_no;

		return '#';
	}

	function getMeta(field:any, item:any) {
		let label = field[0].toUpperCase() + field.substring(1);
		let css = 'text-right';
		let frm = (value:any) => { return Number.isInteger(Number(value)) ? value : Number(value).toFixed(3) }
		let hasFrm = true;

		let textFields = [
			'name',
			'description'
		];

		if (textFields.includes(field) || isNaN(item)) {
			css = 'text-left';
			hasFrm = false;
		}

		return {
			label: label,
			css: css,
			formatter: hasFrm ? frm : undefined
		};
	}

	function setToNameProp(item:any) {
		if (formatters.isNullOrEmpty(item)) return '';
		return item['name'];
	}

	function setVars(item:any, vars:any) {
		let keys = Object.keys(vars);
		for (let k of keys) {
			let v = vars[k];
			item[k] = v.type == 'string' ? v.default_text : v.default_value;
		}
		return item;
	}

	async function exit() {
		electron.quitApp();
	}

	return {
		appPath, pathExists, joinPaths,
		getAutoComplete, getAutoCompleteId,
		getVersionSupport,
		getMostRecentProject, getRecentProjects, pushRecentProject, deleteRecentProject,
		getObjTypeRoute, getMeta, setToNameProp, setVars,
		exit
	}
}