import Plants from '../views/edit/db/Plants.vue';
import PlantsEdit from '../views/edit/db/PlantsEdit.vue';
import PlantsCreate from '../views/edit/db/PlantsCreate.vue';

import Fertilizer from '../views/edit/db/Fertilizer.vue';
import FertilizerEdit from '../views/edit/db/FertilizerEdit.vue';
import FertilizerCreate from '../views/edit/db/FertilizerCreate.vue';


import Pesticides from '../views/edit/db/Pesticides.vue';
import PesticidesEdit from '../views/edit/db/PesticidesEdit.vue';
import PesticidesCreate from '../views/edit/db/PesticidesCreate.vue';

import Pathogens from '../views/edit/db/Pathogens.vue';
import PathogensEdit from '../views/edit/db/PathogensEdit.vue';
import PathogensCreate from '../views/edit/db/PathogensCreate.vue';

import Septic from '../views/edit/db/Septic.vue';
import SepticEdit from '../views/edit/db/SepticEdit.vue';
import SepticCreate from '../views/edit/db/SepticCreate.vue';

import Snow from '../views/edit/db/Snow.vue';
import SnowEdit from '../views/edit/db/SnowEdit.vue';
import SnowCreate from '../views/edit/db/SnowCreate.vue';

import Tillage from '../views/edit/db/Tillage.vue';
import TillageEdit from '../views/edit/db/TillageEdit.vue';
import TillageCreate from '../views/edit/db/TillageCreate.vue';

import Urban from '../views/edit/db/Urban.vue';
import UrbanEdit from '../views/edit/db/UrbanEdit.vue';
import UrbanCreate from '../views/edit/db/UrbanCreate.vue';

export default [
	{ 
		path: 'db/plants', name: 'Plants', component: Plants,
		children: [
			{ path: 'edit/:id', name: 'PlantsEdit', component: PlantsEdit },
			{ path: 'create', name: 'PlantsCreate', component: PlantsCreate }
		]
	},
	{ 
		path: 'db/fertilizer', name: 'Fertilizer', component: Fertilizer,
		children: [
			{ path: 'edit/:id', name: 'FertilizerEdit', component: FertilizerEdit },
			{ path: 'create', name: 'FertilizerCreate', component: FertilizerCreate }
		] 
	},
	
	{ 
		path: 'db/pesticides', name: 'Pesticides', component: Pesticides ,
		children: [
			{ path: 'edit/:id', name: 'PesticidesEdit', component: PesticidesEdit },
			{ path: 'create', name: 'PesticidesCreate', component: PesticidesCreate }
		] 
	},

	{ 
		path: 'db/pathogens', name: 'Pathogens', component: Pathogens ,
		children: [
			{ path: 'edit/:id', name: 'PathogensEdit', component: PathogensEdit },
			{ path: 'create', name: 'PathogensCreate', component: PathogensCreate }
		] 
	},

	{ 
		path: 'db/septic', name: 'Septic', component: Septic ,
		children: [
			{ path: 'edit/:id', name: 'SepticEdit', component: SepticEdit },
			{ path: 'create', name: 'SepticCreate', component: SepticCreate }
		] 
	},
	{ 
		path: 'db/snow', name: 'Snow', component: Snow,
		children: [
			{ path: 'edit/:id', name: 'SnowEdit', component: SnowEdit },
			{ path: 'create', name: 'SnowCreate', component: SnowCreate }
		]  
	},
	{ 
		path: 'db/tillage', name: 'Tillage', component: Tillage,
		children: [
			{ path: 'edit/:id', name: 'TillageEdit', component: TillageEdit },
			{ path: 'create', name: 'TillageCreate', component: TillageCreate }
		]  
	},
	{ 
		path: 'db/urban', name: 'Urban', component: Urban,
		children: [
			{ path: 'edit/:id', name: 'UrbanEdit', component: UrbanEdit },
			{ path: 'create', name: 'UrbanCreate', component: UrbanCreate }
		]  
	}
];
