import { createRouter, createWebHashHistory } from 'vue-router';
import NotFound from '../views/NotFound.vue';
import Setup from '../views/Setup.vue';
import Help from '../views/Help.vue';
import Edit from '../views/edit/Edit.vue';
import Run from '../views/Run.vue';
import TableBrowser from '../views/TableBrowser.vue';

import connect from './connect';
import basin from './basin';
import change from './change';
import climate from './climate';
import constituents from './constituents';
import decision_table from './decision_table';
import db from './db';
import hydrology from './hydrology';
import lum from './lum';
import regions from './regions';
import soils from './soils';
import structural from './structural';
import water_rights from './water_rights';

const editRoutes = connect.concat(basin, change, climate, constituents, decision_table, db, hydrology, lum, regions, soils, structural, water_rights);

export default createRouter({
	history: createWebHashHistory(),
	linkActiveClass: 'parent-active',
	linkExactActiveClass: 'active',
	routes: [
		{ 
			path: '/', name: 'Setup', component: Setup,
			children: [
				{ path: 'help', name: 'Help', component: Help },
				{ path: 'run', name: 'Run', component: Run },
				{ 
					path: 'edit', name: 'Edit', component: Edit,
					children: editRoutes
				}
			]
		},
		{ path: '/table-browser', name: 'TableBrowser', component: TableBrowser },
		{ path: '/:pathMatch(.*)*', name: 'NotFound', component: NotFound }
	],
})