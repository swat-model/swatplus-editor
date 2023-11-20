import LandscapeUnits from '../views/edit/regions/ls_units/LandscapeUnits.vue';
import LandscapeUnitsEdit from '../views/edit/regions/ls_units/LandscapeUnitsEdit.vue';
import LandscapeUnitsCreate from '../views/edit/regions/ls_units/LandscapeUnitsCreate.vue';

import LandscapeUnitsElements from '../views/edit/regions/ls_units/Elements.vue';
import LandscapeUnitsElementsEdit from '../views/edit/regions/ls_units/ElementsEdit.vue';
import LandscapeUnitsElementsCreate from '../views/edit/regions/ls_units/ElementsCreate.vue';

export default [
	{ 
		path: 'regions/ls_units', name: 'LandscapeUnits', component: LandscapeUnits,
		children: [
			{ path: 'edit/:id', name: 'LandscapeUnitsEdit', component: LandscapeUnitsEdit },
			{ path: 'create', name: 'LandscapeUnitsCreate', component: LandscapeUnitsCreate },
			{ 
				path: 'elements', name: 'LandscapeUnitsElements', component: LandscapeUnitsElements,
				children: [
					{ path: 'edit/:id', name: 'LandscapeUnitsElementsEdit', component: LandscapeUnitsElementsEdit },
					{ path: 'create', name: 'LandscapeUnitsElementsCreate', component: LandscapeUnitsElementsCreate }
				]  
			}
		] 
	}
];