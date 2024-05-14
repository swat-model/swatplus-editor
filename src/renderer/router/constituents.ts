import ConstituentsSoilPlant from '../views/edit/constituents/SoilPlant.vue';
import ConstituentsSoilPlantEdit from '../views/edit/constituents/SoilPlantEdit.vue';
import ConstituentsSoilPlantCreate from '../views/edit/constituents/SoilPlantCreate.vue';

import ConstituentsOMWater from '../views/edit/constituents/OMWater.vue';
import ConstituentsOMWaterEdit from '../views/edit/constituents/OMWaterEdit.vue';
import ConstituentsOMWaterCreate from '../views/edit/constituents/OMWaterCreate.vue';

import ConstituentsPesticides from '../views/edit/constituents/Pesticides.vue';
import ConstituentsPathogens from '../views/edit/constituents/Pathogens.vue';

import ConstituentsSalts from '../views/edit/constituents/salts/Salts.vue';

import ConstituentsSaltsRecall from '../views/edit/constituents/salts/SaltsRecall.vue';
import ConstituentsSaltsRecallEdit from '../views/edit/constituents/salts/SaltsRecallEdit.vue';
import ConstituentsSaltsRecallCreate from '../views/edit/constituents/salts/SaltsRecallCreate.vue';
import ConstituentsSaltsRecallDataEdit from '../views/edit/constituents/salts/SaltsRecallDataEdit.vue';
import ConstituentsSaltsRecallDataCreate from '../views/edit/constituents/salts/SaltsRecallDataCreate.vue';

import ConstituentsSaltsAtmo from '../views/edit/constituents/salts/SaltsAtmo.vue';
import ConstituentsSaltsAtmoEdit from '../views/edit/constituents/salts/SaltsAtmoEdit.vue';

export default [
	{ 
		path: 'constituents/soil_plant', name: 'ConstituentsSoilPlant', component: ConstituentsSoilPlant, 
		children: [
			{ path: 'edit/:id', name: 'ConstituentsSoilPlantEdit', component: ConstituentsSoilPlantEdit },
			{ path: 'create', name: 'ConstituentsSoilPlantCreate', component: ConstituentsSoilPlantCreate }
		]
	},
	{ 
		path: 'constituents/om_water', name: 'ConstituentsOMWater', component: ConstituentsOMWater, 
		children: [
			{ path: 'edit/:id', name: 'ConstituentsOMWaterEdit', component: ConstituentsOMWaterEdit },
			{ path: 'create', name: 'ConstituentsOMWaterCreate', component: ConstituentsOMWaterCreate }
		] 
	},
	{ 
		path: 'constituents/pest', name: 'ConstituentsPesticides', component: ConstituentsPesticides,
		children: []
	},
	{ 
		path: 'constituents/path', name: 'ConstituentsPathogens', component: ConstituentsPathogens,
		children: []
	},
	{ 
		path: 'constituents/salts', name: 'ConstituentsSalts', component: ConstituentsSalts,
		children: [
			{ 
				path: 'recall', name: 'ConstituentsSaltsRecall', component: ConstituentsSaltsRecall,
				children: [
					{ 
						path: 'edit/:id', name: 'ConstituentsSaltsRecallEdit', component: ConstituentsSaltsRecallEdit,
						children: [
							{ path: 'edit/:dataId', name: 'ConstituentsSaltsRecallDataEdit', component: ConstituentsSaltsRecallDataEdit },
							{ path: 'create', name: 'ConstituentsSaltsRecallDataCreate', component: ConstituentsSaltsRecallDataCreate }
						]
					},
					{ path: 'create', name: 'ConstituentsSaltsRecallCreate', component: ConstituentsSaltsRecallCreate }
				] 
			},
			{ 
				path: 'atmo', name: 'ConstituentsSaltsAtmo', component: ConstituentsSaltsAtmo,
				children: [
					{ path: 'edit/:id', name: 'ConstituentsSaltsAtmoEdit', component: ConstituentsSaltsAtmoEdit }
				] 
			}
		]
	},
];