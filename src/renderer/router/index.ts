import { createRouter, createWebHistory } from 'vue-router';
import NotFound from '../views/NotFound.vue';
import Setup from '../views/Setup.vue';
import Help from '../views/Help.vue';
import Edit from '../views/edit/Edit.vue';
import TableBrowser from '../views/TableBrowser.vue';

import basin from './basin';
import connect from './connect';

const editRoutes = connect.concat(basin);

export default createRouter({
	history: createWebHistory(),
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