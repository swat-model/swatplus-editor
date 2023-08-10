import { createRouter, createWebHashHistory } from 'vue-router';
import Setup from '../views/Setup.vue';

export default createRouter({
	history: createWebHashHistory(),
	linkActiveClass: 'active',
	routes: [
		{ 
			path: '/', name: 'Setup', component: Setup
		},
		{ path: '/:pathMatch(.*)*', name: 'Setup', component: Setup }
	],
})