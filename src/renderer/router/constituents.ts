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
import ConstituentsSaltsRoad from '../views/edit/constituents/salts/SaltsRoad.vue';
import ConstituentsSaltsRoadEdit from '../views/edit/constituents/salts/SaltsRoadEdit.vue';

import ConstituentsSaltsFert from '../views/edit/constituents/salts/SaltsFert.vue';
import ConstituentsSaltsFertEdit from '../views/edit/constituents/salts/SaltsFertEdit.vue';
import ConstituentsSaltsUrban from '../views/edit/constituents/salts/SaltsUrban.vue';
import ConstituentsSaltsUrbanEdit from '../views/edit/constituents/salts/SaltsUrbanEdit.vue';
import ConstituentsSaltsPlants from '../views/edit/constituents/salts/SaltsPlants.vue';
import ConstituentsSaltsPlantsEdit from '../views/edit/constituents/salts/SaltsPlantsEdit.vue';

import ConstituentsSaltsAquIni from '../views/edit/constituents/salts/SaltsAquIni.vue';
import ConstituentsSaltsAquIniEdit from '../views/edit/constituents/salts/SaltsAquIniEdit.vue';
import ConstituentsSaltsAquIniCreate from '../views/edit/constituents/salts/SaltsAquIniCreate.vue';

import ConstituentsSaltsChannelIni from '../views/edit/constituents/salts/SaltsChannelIni.vue';
import ConstituentsSaltsChannelIniEdit from '../views/edit/constituents/salts/SaltsChannelIniEdit.vue';
import ConstituentsSaltsChannelIniCreate from '../views/edit/constituents/salts/SaltsChannelIniCreate.vue';

import ConstituentsSaltsResIni from '../views/edit/constituents/salts/SaltsResIni.vue';
import ConstituentsSaltsResIniEdit from '../views/edit/constituents/salts/SaltsResIniEdit.vue';
import ConstituentsSaltsResIniCreate from '../views/edit/constituents/salts/SaltsResIniCreate.vue';

import ConstituentsSaltsHruIni from '../views/edit/constituents/salts/SaltsHruIni.vue';
import ConstituentsSaltsHruIniEdit from '../views/edit/constituents/salts/SaltsHruIniEdit.vue';
import ConstituentsSaltsHruIniCreate from '../views/edit/constituents/salts/SaltsHruIniCreate.vue';

import ConstituentsSaltsIrrigation from '../views/edit/constituents/salts/SaltsIrrigation.vue';
import ConstituentsSaltsIrrigationEdit from '../views/edit/constituents/salts/SaltsIrrigationEdit.vue';

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
			},
			{ 
				path: 'road', name: 'ConstituentsSaltsRoad', component: ConstituentsSaltsRoad,
				children: [
					{ path: 'edit/:id', name: 'ConstituentsSaltsRoadEdit', component: ConstituentsSaltsRoadEdit }
				] 
			},
			{ 
				path: 'fert', name: 'ConstituentsSaltsFert', component: ConstituentsSaltsFert,
				children: [
					{ path: 'edit/:id', name: 'ConstituentsSaltsFertEdit', component: ConstituentsSaltsFertEdit }
				] 
			},
			{ 
				path: 'urban', name: 'ConstituentsSaltsUrban', component: ConstituentsSaltsUrban,
				children: [
					{ path: 'edit/:id', name: 'ConstituentsSaltsUrbanEdit', component: ConstituentsSaltsUrbanEdit }
				] 
			},
			{ 
				path: 'plants', name: 'ConstituentsSaltsPlants', component: ConstituentsSaltsPlants,
				children: [
					{ path: 'edit/:id', name: 'ConstituentsSaltsPlantsEdit', component: ConstituentsSaltsPlantsEdit }
				] 
			},
			{ 
				path: 'aqu', name: 'ConstituentsSaltsAquIni', component: ConstituentsSaltsAquIni,
				children: [
					{ path: 'edit/:id', name: 'ConstituentsSaltsAquIniEdit', component: ConstituentsSaltsAquIniEdit },
					{ path: 'create', name: 'ConstituentsSaltsAquIniCreate', component: ConstituentsSaltsAquIniCreate }
				] 
			},
			{ 
				path: 'cha', name: 'ConstituentsSaltsChannelIni', component: ConstituentsSaltsChannelIni,
				children: [
					{ path: 'edit/:id', name: 'ConstituentsSaltsChannelIniEdit', component: ConstituentsSaltsChannelIniEdit },
					{ path: 'create', name: 'ConstituentsSaltsChannelIniCreate', component: ConstituentsSaltsChannelIniCreate }
				] 
			},
			{ 
				path: 'res', name: 'ConstituentsSaltsResIni', component: ConstituentsSaltsResIni,
				children: [
					{ path: 'edit/:id', name: 'ConstituentsSaltsResIniEdit', component: ConstituentsSaltsResIniEdit },
					{ path: 'create', name: 'ConstituentsSaltsResIniCreate', component: ConstituentsSaltsResIniCreate }
				] 
			},
			{ 
				path: 'hru', name: 'ConstituentsSaltsHruIni', component: ConstituentsSaltsHruIni,
				children: [
					{ path: 'edit/:id', name: 'ConstituentsSaltsHruIniEdit', component: ConstituentsSaltsHruIniEdit },
					{ path: 'create', name: 'ConstituentsSaltsHruIniCreate', component: ConstituentsSaltsHruIniCreate }
				] 
			},
			{ 
				path: 'irr', name: 'ConstituentsSaltsIrrigation', component: ConstituentsSaltsIrrigation,
				children: [
					{ path: 'edit/:id', name: 'ConstituentsSaltsIrrigationEdit', component: ConstituentsSaltsIrrigationEdit }
				] 
			}
		]
	},
];