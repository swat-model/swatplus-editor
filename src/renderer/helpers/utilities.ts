import { useRoute } from 'vue-router';
import { useApi } from './api';
import { useCurrentProject } from '../store/currentProject';
import { useFormatters } from './formatters';
import { useConstants } from './constants';

export function useUtilities() {
	const electron = window.electronApi;
	const route = useRoute();
	const api = useApi();
	const currentProject = useCurrentProject();
	const formatters = useFormatters();
	const constants = useConstants();

	const appPath = electron.getAppPath().replace('app.asar', 'app.asar.unpacked');
	const appPathUrl = encodeURIComponent(appPath||'');

	const publicPath = constants.globals.dev_mode ? '' : electron.getAppPath().replace('static', 'renderer');

	function appendRoute(pathToAppend:string) {
		return route.path + (route.path.endsWith('/') ? '' : '/') + pathToAppend
	}

	function pathExists(path:string) {
		return electron.pathExists(path);
	}

	function joinPaths(paths:any[]) {
		return electron.joinPaths(paths);
	}

	function getAutoComplete(type:string, name:any) {
		if (formatters.isNullOrEmpty(name))
			return api.get(`auto_complete/all/${type}`, currentProject.getApiHeader());
		return api.get(`auto_complete/match/${type}/${name}`, currentProject.getApiHeader());
	}

	function getAutoCompleteId(type:string, name:any) {
		return api.get(`auto_complete/item-id/${type}/${name}`, currentProject.getApiHeader());
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

	function getDatabaseInstallPath(database_file:string='swatplus_datasets.sqlite') {
		let installPath = electron.joinPaths([appPath, '../../../Databases/' + database_file]);
		let installPathMac = electron.joinPaths([appPath, '../../../../../Databases/' + database_file]);
		let searchPaths = [
			installPath,
			installPathMac,
			'C:/SWAT/SWATPlus/Databases/' + database_file
		];

		for (let p of searchPaths) {
			if (pathExists(p)) return p;
		}

		return null;
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

	function getRecTypDescription(rec_typ:any) {
		switch (rec_typ) {
			case 1: return 'Daily';
			case 2: return 'Monthly';
			case 3: return 'Yearly';
			default: return 'Constant';
		}
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

	function openUrl(href:string) {
		electron.openUrl(href);
	}

	function setColorTheme(colorTheme:string):void {
		electron.setColorTheme(colorTheme);
	}

	function getColorTheme():string {
		return electron.getColorTheme();
	}

	function setWindowTitle() {
		let title = `SWAT+ Editor ${constants.appSettings.version} / SWAT+ rev. ${constants.appSettings.swatplus}`;
		if (!formatters.isNullOrEmpty(currentProject.name))  title += ' / ' + currentProject.name;
		electron.setWindowTitle(title);
	}

	async function exit() {
		electron.quitApp();
	}

	//Vuelidate doesn't like if you replace the entire object received from the API
	//This function loops each property of the reactive object and assigns it to the same propery from the object received from the API
	function assignReactiveObject(assignTo:any, assignFrom:any) {
		for (let key of Object.keys(assignTo)) {
			assignTo[key] = assignFrom[key];
		}
	}

	return {
		appPath, appPathUrl, publicPath, appendRoute, pathExists, joinPaths,
		getAutoComplete, getAutoCompleteId,
		getVersionSupport,
		getMostRecentProject, getRecentProjects, pushRecentProject, deleteRecentProject,
		getDatabaseInstallPath,
		getObjTypeRoute, getMeta, getRecTypDescription, setToNameProp, setVars, openUrl,
		setColorTheme, getColorTheme, setWindowTitle,
		exit,
		assignReactiveObject
	}
}