import { createRouter, createWebHashHistory } from 'vue-router';
import NotFound from '../views/NotFound.vue';
import Setup from '../views/Setup.vue';
import Help from '../views/Help.vue';
import Edit from '../views/edit/Edit.vue';
import TableBrowser from '../views/TableBrowser.vue';

import connect from './connect';
import basin from './basin';
import climate from './climate';
import db from './db';
import regions from './regions';
import structural from './structural';

const editRoutes = connect.concat(basin, climate, db, regions, structural);

export default createRouter({
	history: createWebHashHistory(),
	linkActiveClass: 'parent-active',
	linkExactActiveClass: 'active',
	routes: [
		{ 
			path: '/', name: 'Setup', component: Setup,
			children: [
				{ path: 'help', name: 'Help', component: Help },
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