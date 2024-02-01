import CalParms from '../views/edit/change/hard/CalParms.vue';
import CalParmsEdit from '../views/edit/change/hard/CalParmsEdit.vue';

import Calibration from '../views/edit/change/hard/Calibration.vue';
import CalibrationEdit from '../views/edit/change/hard/CalibrationEdit.vue';
import CalibrationCreate from '../views/edit/change/hard/CalibrationCreate.vue';

import SoftCalibration from '../views/edit/change/soft/Calibration.vue';
import WaterBalance from '../views/edit/change/soft/WaterBalance.vue';
import PlantGrowth from '../views/edit/change/soft/PlantGrowth.vue';

export default [
	{ 
		path: 'change/hard', name: 'HardCalibration', component: Calibration,
		children: [
			{ path: 'edit/:id', name: 'HardCalibrationEdit', component: CalibrationEdit },
			{ path: 'create', name: 'HardCalibrationCreate', component: CalibrationCreate },
			{ 
				path: 'parms', name: 'HardCalibrationParms', component: CalParms,
				children: [
					{ path: 'edit/:id', name: 'HardCalibrationParmsEdit', component: CalParmsEdit }
				]  
			},
		]  
	},
	{
		path: 'change/soft', name: 'SoftCalibration', component: SoftCalibration,
		children: [
			{ path: 'wb', name: 'SoftCalibrationWaterBalance', component: WaterBalance },
			{ path: 'plant', name: 'SoftCalibrationPlantGrowth', component: PlantGrowth }
		]
	}
];