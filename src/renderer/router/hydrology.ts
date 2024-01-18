import Hydrology from '../views/edit/hydrology/Hydrology.vue';
import HydrologyEdit from '../views/edit/hydrology/HydrologyEdit.vue';
import HydrologyCreate from '../views/edit/hydrology/HydrologyCreate.vue';

import Topography from '../views/edit/hydrology/Topography.vue';
import TopographyEdit from '../views/edit/hydrology/TopographyEdit.vue';
import TopographyCreate from '../views/edit/hydrology/TopographyCreate.vue';

import Fields from '../views/edit/hydrology/Fields.vue';
import FieldsEdit from '../views/edit/hydrology/FieldsEdit.vue';
import FieldsCreate from '../views/edit/hydrology/FieldsCreate.vue';

export default [
	{ 
		path: 'hydrology/hydrology', name: 'Hydrology', component: Hydrology, 
		children: [
			{ path: 'edit/:id', name: 'HydrologyEdit', component: HydrologyEdit },
			{ path: 'create', name: 'HydrologyCreate', component: HydrologyCreate }
		]  
	},
	{ 
		path: 'hydrology/topography', name: 'Topography', component: Topography, 
		children: [
			{ path: 'edit/:id', name: 'TopographyEdit', component: TopographyEdit },
			{ path: 'create', name: 'TopographyCreate', component: TopographyCreate }
		]  
	},
	{ 
		path: 'hydrology/fields', name: 'Fields', component: Fields, 
		children: [
			{ path: 'edit/:id', name: 'FieldsEdit', component: FieldsEdit },
			{ path: 'create', name: 'FieldsCreate', component: FieldsCreate }
		]   
	}
];