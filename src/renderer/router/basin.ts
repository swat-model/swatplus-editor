import BasinCodes from '../views/edit/basin/Codes.vue';
import BasinParameters from '../views/edit/basin/Parameters.vue';

export default [
	{ path: 'basin/codes', name: 'BasinCodes', component: BasinCodes, children: [] },
	{ path: 'basin/parameters', name: 'BasinParameters', component: BasinParameters, children: [] }
];