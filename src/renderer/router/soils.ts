import Soils from '../views/edit/soils/Soils.vue';
import SoilsEdit from '../views/edit/soils/SoilsEdit.vue';
import SoilsCreate from '../views/edit/soils/SoilsCreate.vue';

import SoilNutrients from '../views/edit/soils/Nutrients.vue';
import SoilNutrientsEdit from '../views/edit/soils/NutrientsEdit.vue';
import SoilNutrientsCreate from '../views/edit/soils/NutrientsCreate.vue';

import SoilsLte from '../views/edit/soils/SoilsLte.vue';
import SoilsLteEdit from '../views/edit/soils/SoilsLteEdit.vue';
import SoilsLteCreate from '../views/edit/soils/SoilsLteCreate.vue';

export default [
	{ 
		path: 'soils/soils', name: 'Soils', component: Soils,
		children: [
			{ path: 'edit/:id', name: 'SoilsEdit', component: SoilsEdit },
			{ path: 'create', name: 'SoilsCreate', component: SoilsCreate }
		]  
	},
	{ 
		path: 'soils/soil-nutrients', name: 'SoilNutrients', component: SoilNutrients,
		children: [
			{ path: 'edit/:id', name: 'SoilNutrientsEdit', component: SoilNutrientsEdit },
			{ path: 'create', name: 'SoilNutrientsCreate', component: SoilNutrientsCreate }
		]   
	},
	{ 
		path: 'soils/soils-lte', name: 'SoilsLte', component: SoilsLte,
		children: [
			{ path: 'edit/:id', name: 'SoilsLteEdit', component: SoilsLteEdit },
			{ path: 'create', name: 'SoilsLteCreate', component: SoilsLteCreate }
		]   
	}
];