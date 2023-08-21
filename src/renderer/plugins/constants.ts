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

	let objTypeToConTable:any = {};
	objTypeToConTable['hru'] = 'hru_con';
	objTypeToConTable['hlt'] = 'hru_lte_con';
	objTypeToConTable['ru'] = 'rtu_con';
	objTypeToConTable['aqu'] = 'aqu_con';
	objTypeToConTable['cha'] = 'cha_con';
	objTypeToConTable['res'] = 'res_con';
	objTypeToConTable['rec'] = 'rec_con';
	objTypeToConTable['exc'] = 'exco_con';
	objTypeToConTable['dr'] = 'dr_con';
	objTypeToConTable['out'] = 'out_con';
	objTypeToConTable['mfl'] = 'modflow_con';
	objTypeToConTable['sdc'] = 'chandeg_con';

	const commonMessages = {
		leaveWarning: 'Click to view details. Warning: any unsaved changes on this page will be lost!'
	};

	const electron = window.electronApi;
	const globals = electron.getGlobals();
	const appSettings = electron.getAppSettings();

	const dialogSizes = {
		xs: '300px',
		sm: '500px',
		md: '800px',
		lg: '1000px'
	}

	const formRules = {
		required: (value:string) => !!value || 'Required',
		max: (numChars:number, value:string) => (value || '').length <= numChars || `Maximum ${numChars} characters`,
		nameLength: (value:string) => (value || '').length <= 16 || `Maximum 16 characters`,
		longNameLength: (value:string) => (value || '').length <= 40 || `Maximum 40 characters`,
		email: (value:string) => {
			const pattern = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/
			return pattern.test(value) || 'Invalid e-mail.'
		}
	}

	return {
		objTypeRouteTable,
		noObjTypeRoutes,
		objTypeToConTable,
		commonMessages,
		globals,
		appSettings,
		dialogSizes,
		formRules
	}
}