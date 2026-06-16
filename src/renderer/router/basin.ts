import BasinCodes from '../views/edit/basin/Codes.vue';
import BasinParameters from '../views/edit/basin/Parameters.vue';
import BasinCarbon from '../views/edit/basin/Carbon.vue';

import BasinCarbonLayers from '../views/edit/basin/CarbonLayers.vue';
import BasinCarbonLayersCreate from '../views/edit/basin/CarbonLayersCreate.vue';
import BasinCarbonLayersEdit from '../views/edit/basin/CarbonLayersEdit.vue';

export default [
	{ path: 'basin/codes', name: 'BasinCodes', component: BasinCodes, children: [] },
	{ path: 'basin/parameters', name: 'BasinParameters', component: BasinParameters, children: [] },
	{ path: 'basin/carbon', name: 'BasinCarbon', component: BasinCarbon, children: [
		{ 
			path: 'layers', name: 'BasinCarbonLayers', component: BasinCarbonLayers,
			children: [
				{ path: 'edit/:id', name: 'BasinCarbonLayersEdit', component: BasinCarbonLayersEdit },
				{ path: 'create', name: 'BasinCarbonLayersCreate', component: BasinCarbonLayersCreate }
			] 
		},
	] },
		
];