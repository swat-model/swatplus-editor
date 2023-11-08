import Wgn from '../views/edit/climate/Wgn.vue';
import WgnEdit from '../views/edit/climate/WgnEdit.vue';
import WgnCreate from '../views/edit/climate/WgnCreate.vue';

/*import Stations from '../views/edit/climate/Stations.vue';
import StationsEdit from '../views/edit/climate/StationsEdit.vue';
import StationsCreate from '../views/edit/climate/StationsCreate.vue';

import Atmo from '../views/edit/climate/Atmo.vue';
import AtmoEdit from '../views/edit/climate/AtmoEdit.vue';
import AtmoCreate from '../views/edit/climate/AtmoCreate.vue';*/

export default [
	{ 
		path: 'climate/wgn', name: 'Wgn', component: Wgn,
		children: [
			{ path: 'edit/:id', name: 'WgnEdit', component: WgnEdit },
			{ path: 'create', name: 'WgnCreate', component: WgnCreate }
		]
	},
	/*{ 
		path: 'climate/stations', name: 'Stations', component: Stations,
		children: [
			{ path: 'edit/:id', name: 'StationsEdit', component: StationsEdit },
			{ path: 'create', name: 'StationsCreate', component: StationsCreate },
			{ 
				path: 'atmo', name: 'StationsAtmo', component: Atmo,
				children: [
					{ path: 'edit/:id', name: 'StationsAtmoEdit', component: AtmoEdit },
					{ path: 'create', name: 'StationsAtmoCreate', component: AtmoCreate }
				]
			}
		]
	}*/
];