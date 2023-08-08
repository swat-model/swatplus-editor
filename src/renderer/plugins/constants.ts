export function useConstants() {
	const objTypeRouteTable:{[key:string]:{path:string,name:string}} = {
		'hru': { path: '/edit/hrus/edit/', name: 'HrusEdit' },
		'hlt': { path: '/edit/hrus-lte/edit/', name: 'HrusLteEdit' },
		'ru': { path: '/edit/routing_unit/edit/', name: 'RoutingUnitEdit' },
		'aqu': { path: '/edit/aquifers/edit/', name: 'AquifersEdit' },
		'cha': { path: '/edit/channels/edit/', name: 'ChannelsEdit' },
		'res': { path: '/edit/reservoirs/edit/', name: 'ReservoirsEdit' },
		'rec': { path: '/edit/recall/edit/', name: 'RecallEdit' },
		'exc': { path: '/edit/exco/edit/', name: 'ExcoEdit' },
		'dr': { path: '/edit/dr/edit/', name: 'DelratioEdit' },
		'out': { path: '#', name: '#' },
		'mfl': { path: '#', name: '#' },
		'sdc': { path: '/edit/channels/edit/', name: 'ChannelsEdit' }
	};

	const noObjTypeRoutes = [
		'hlt', 'rec', 'out', 'mfl'
	];

	const objTypeToConTable = {
		'hru': 'hru_con',
		'hlt': 'hru_lte_con',
		'ru': 'rtu_con',
		'aqu': 'aqu_con',
		'cha': 'cha_con',
		'res': 'res_con',
		'rec': 'rec_con',
		'exc': 'exco_con',
		'dr': 'dr_con',
		'out': 'out_con',
		'mfl': 'modflow_con',
		'sdc': 'chandeg_con'
	};

	const commonMessages = {
		leaveWarning: 'Click to view details. Warning: any unsaved changes on this page will be lost!'
	};

	const electron = window.electronApi;
	const globals = electron.getGlobals();
	const appSettings = electron.getAppSettings();

	return {
		objTypeRouteTable,
		noObjTypeRoutes,
		objTypeToConTable,
		commonMessages,
		globals,
		appSettings
	}
}