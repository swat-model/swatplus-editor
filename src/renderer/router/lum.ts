import Landuse from '../views/edit/lum/Landuse.vue';
import LanduseEdit from '../views/edit/lum/LanduseEdit.vue';
import LanduseCreate from '../views/edit/lum/LanduseCreate.vue';

import Management from '../views/edit/lum/Management.vue';
import ManagementEdit from '../views/edit/lum/ManagementEdit.vue';
import ManagementCreate from '../views/edit/lum/ManagementCreate.vue';

/*import Cntable from '../views/edit/lum/Cntable.vue';
import CntableEdit from '../views/edit/lum/CntableEdit.vue';
import CntableCreate from '../views/edit/lum/CntableCreate.vue';

import Ovntable from '../views/edit/lum/Ovntable.vue';
import OvntableEdit from '../views/edit/lum/OvntableEdit.vue';
import OvntableCreate from '../views/edit/lum/OvntableCreate.vue';

import ConsPractice from '../views/edit/lum/ConsPractice.vue';
import ConsPracticeEdit from '../views/edit/lum/ConsPracticeEdit.vue';
import ConsPracticeCreate from '../views/edit/lum/ConsPracticeCreate.vue';*/

import Operations from '../views/edit/lum/ops/Operations.vue';

/*import OperationsChemApp from '../views/edit/lum/ops/ChemApp.vue';
import OperationsChemAppEdit from '../views/edit/lum/ops/ChemAppEdit.vue';
import OperationsChemAppCreate from '../views/edit/lum/ops/ChemAppCreate.vue';

import OperationsFire from '../views/edit/lum/ops/Fire.vue';
import OperationsFireEdit from '../views/edit/lum/ops/FireEdit.vue';
import OperationsFireCreate from '../views/edit/lum/ops/FireCreate.vue';

import OperationsGraze from '../views/edit/lum/ops/Graze.vue';
import OperationsGrazeEdit from '../views/edit/lum/ops/GrazeEdit.vue';
import OperationsGrazeCreate from '../views/edit/lum/ops/GrazeCreate.vue';

import OperationsHarvest from '../views/edit/lum/ops/Harvest.vue';
import OperationsHarvestEdit from '../views/edit/lum/ops/HarvestEdit.vue';
import OperationsHarvestCreate from '../views/edit/lum/ops/HarvestCreate.vue';

import OperationsIrrigation from '../views/edit/lum/ops/Irrigation.vue';
import OperationsIrrigationEdit from '../views/edit/lum/ops/IrrigationEdit.vue';
import OperationsIrrigationCreate from '../views/edit/lum/ops/IrrigationCreate.vue';

import OperationsSweep from '../views/edit/lum/ops/Sweep.vue';
import OperationsSweepEdit from '../views/edit/lum/ops/SweepEdit.vue';
import OperationsSweepCreate from '../views/edit/lum/ops/SweepCreate.vue';*/

export default [
	{ 
		path: 'lum/landuse', name: 'Landuse', component: Landuse,
		children: [
			{ path: 'edit/:id', name: 'LanduseEdit', component: LanduseEdit },
			{ path: 'create', name: 'LanduseCreate', component: LanduseCreate }
		]  
	},
	{ 
		path: 'lum/mgt', name: 'Management', component: Management,
		children: [
			{ path: 'edit/:id', name: 'ManagementEdit', component: ManagementEdit },
			{ path: 'create', name: 'ManagementCreate', component: ManagementCreate }
		]
	},
	{ 
		path: 'lum/ops', name: 'Operations', component: Operations,
		/*children: [
			{ path: 'chemapp', name: 'OperationsChemApp', component: OperationsChemApp,
				children: [
					{ path: 'edit/:id', name: 'OperationsChemAppEdit', component: OperationsChemAppEdit },
					{ path: 'create', name: 'OperationsChemAppCreate', component: OperationsChemAppCreate }
				] 
			},
			{ path: 'fire', name: 'OperationsFire', component: OperationsFire,
				children: [
					{ path: 'edit/:id', name: 'OperationsFireEdit', component: OperationsFireEdit },
					{ path: 'create', name: 'OperationsFireCreate', component: OperationsFireCreate }
				] 
			},
			{ 
				path: 'graze', name: 'OperationsGraze', component: OperationsGraze,
				children: [
					{ path: 'edit/:id', name: 'OperationsGrazeEdit', component: OperationsGrazeEdit },
					{ path: 'create', name: 'OperationsGrazeCreate', component: OperationsGrazeCreate }
				] 
			},
			{ path: 'harvest', name: 'OperationsHarvest', component: OperationsHarvest,
				children: [
					{ path: 'edit/:id', name: 'OperationsHarvestEdit', component: OperationsHarvestEdit },
					{ path: 'create', name: 'OperationsHarvestCreate', component: OperationsHarvestCreate }
				] 
			},
			{ path: 'irrigation', name: 'OperationsIrrigation', component: OperationsIrrigation,
				children: [
					{ path: 'edit/:id', name: 'OperationsIrrigationEdit', component: OperationsIrrigationEdit },
					{ path: 'create', name: 'OperationsIrrigationCreate', component: OperationsIrrigationCreate }
				] 
			},
			{ path: 'sweep', name: 'OperationsSweep', component: OperationsSweep,
				children: [
					{ path: 'edit/:id', name: 'OperationsSweepEdit', component: OperationsSweepEdit },
					{ path: 'create', name: 'OperationsSweepCreate', component: OperationsSweepCreate }
				] 
			}
		]*/
	},
	/*{ 
		path: 'lum/cntable', name: 'Cntable', component: Cntable,
		children: [
			{ path: 'edit/:id', name: 'CntableEdit', component: CntableEdit },
			{ path: 'create', name: 'CntableCreate', component: CntableCreate }
		]   
	},
	{ 
		path: 'lum/ovntable', name: 'Ovntable', component: Ovntable,
		children: [
			{ path: 'edit/:id', name: 'OvntableEdit', component: OvntableEdit },
			{ path: 'create', name: 'OvntableCreate', component: OvntableCreate }
		] 
	},
	{ 
		path: 'lum/conspractice', name: 'ConsPractice', component: ConsPractice,
		children: [
			{ path: 'edit/:id', name: 'ConsPracticeEdit', component: ConsPracticeEdit },
			{ path: 'create', name: 'ConsPracticeCreate', component: ConsPracticeCreate }
		] 
	}*/
];