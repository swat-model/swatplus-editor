import ConstituentsSoilPlant from '../views/edit/constituents/SoilPlant.vue';
import ConstituentsSoilPlantEdit from '../views/edit/constituents/SoilPlantEdit.vue';
import ConstituentsSoilPlantCreate from '../views/edit/constituents/SoilPlantCreate.vue';

import ConstituentsOMWater from '../views/edit/constituents/OMWater.vue';
import ConstituentsOMWaterEdit from '../views/edit/constituents/OMWaterEdit.vue';
import ConstituentsOMWaterCreate from '../views/edit/constituents/OMWaterCreate.vue';

import ConstituentsPesticides from '../views/edit/constituents/Pesticides.vue';
import ConstituentsPathogens from '../views/edit/constituents/Pathogens.vue';

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
];