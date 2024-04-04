import Channels from '../views/edit/connect/channels/Channels.vue';
import ChannelsEdit from '../views/edit/connect/channels/ChannelsEdit.vue';
import ChannelsCreate from '../views/edit/connect/channels/ChannelsCreate.vue';

import ChannelsInitial from '../views/edit/connect/channels/Initial.vue';
import ChannelsInitialEdit from '../views/edit/connect/channels/InitialEdit.vue';
import ChannelsInitialCreate from '../views/edit/connect/channels/InitialCreate.vue';

import ChannelsHydSedLte from '../views/edit/connect/channels/HydSedLte.vue';
import ChannelsHydSedLteEdit from '../views/edit/connect/channels/HydSedLteEdit.vue';
import ChannelsHydSedLteCreate from '../views/edit/connect/channels/HydSedLteCreate.vue';

import ChannelsNutrients from '../views/edit/connect/channels/Nutrients.vue';
import ChannelsNutrientsEdit from '../views/edit/connect/channels/NutrientsEdit.vue';
import ChannelsNutrientsCreate from '../views/edit/connect/channels/NutrientsCreate.vue'; 

import Hrus from '../views/edit/connect/hrus/Hrus.vue';
import HrusEdit from '../views/edit/connect/hrus/HrusEdit.vue';
import HrusCreate from '../views/edit/connect/hrus/HrusCreate.vue'; 

import HrusLte from '../views/edit/connect/hrus-lte/HrusLte.vue';
import HrusLteEdit from '../views/edit/connect/hrus-lte/HrusLteEdit.vue';
import HrusLteCreate from '../views/edit/connect/hrus-lte/HrusLteCreate.vue'; 

import RoutingUnits from '../views/edit/connect/routing-units/RoutingUnits.vue';
import RoutingUnitsEdit from '../views/edit/connect/routing-units/RoutingUnitsEdit.vue';
import RoutingUnitsCreate from '../views/edit/connect/routing-units/RoutingUnitsCreate.vue';

import RoutingUnitsElements from '../views/edit/connect/routing-units/Elements.vue';
import RoutingUnitsElementsEdit from '../views/edit/connect/routing-units/ElementsEdit.vue';
import RoutingUnitsElementsCreate from '../views/edit/connect/routing-units/ElementsCreate.vue';

import Aquifers from '../views/edit/connect/aquifers/Aquifers.vue';
import AquifersEdit from '../views/edit/connect/aquifers/AquifersEdit.vue';
import AquifersCreate from '../views/edit/connect/aquifers/AquifersCreate.vue';

import AquifersInitial from '../views/edit/connect/aquifers/Initial.vue';
import AquifersInitialEdit from '../views/edit/connect/aquifers/InitialEdit.vue';
import AquifersInitialCreate from '../views/edit/connect/aquifers/InitialCreate.vue';

import Gwflow from '../views/edit/connect/gwflow/Gwflow.vue';
import GwflowGrids from '../views/edit/connect/gwflow/GwflowGrids.vue';
import GwflowZone from '../views/edit/connect/gwflow/GwflowZone.vue';
import GwflowZoneEdit from '../views/edit/connect/gwflow/GwflowZoneEdit.vue';

import GwflowFpcell from '../views/edit/connect/gwflow/Fpcell.vue';
import GwflowFpcellEdit from '../views/edit/connect/gwflow/FpcellEdit.vue';
import GwflowFpcellCreate from '../views/edit/connect/gwflow/FpcellCreate.vue';

import GwflowRescell from '../views/edit/connect/gwflow/Rescell.vue';
import GwflowRescellEdit from '../views/edit/connect/gwflow/RescellEdit.vue';
import GwflowRescellCreate from '../views/edit/connect/gwflow/RescellCreate.vue';

import GwflowWetlands from '../views/edit/connect/gwflow/Wetlands.vue';
import GwflowWetlandsEdit from '../views/edit/connect/gwflow/WetlandsEdit.vue';
import GwflowWetlandsCreate from '../views/edit/connect/gwflow/WetlandsCreate.vue';

import Reservoirs from '../views/edit/connect/reservoirs/Reservoirs.vue';
import ReservoirsEdit from '../views/edit/connect/reservoirs/ReservoirsEdit.vue';
import ReservoirsCreate from '../views/edit/connect/reservoirs/ReservoirsCreate.vue';

import ReservoirsInitial from '../views/edit/connect/reservoirs/Initial.vue';
import ReservoirsInitialEdit from '../views/edit/connect/reservoirs/InitialEdit.vue';
import ReservoirsInitialCreate from '../views/edit/connect/reservoirs/InitialCreate.vue';

import ReservoirsHydrology from '../views/edit/connect/reservoirs/Hydrology.vue';
import ReservoirsHydrologyEdit from '../views/edit/connect/reservoirs/HydrologyEdit.vue';
import ReservoirsHydrologyCreate from '../views/edit/connect/reservoirs/HydrologyCreate.vue';

import ReservoirsSediment from '../views/edit/connect/reservoirs/Sediment.vue';
import ReservoirsSedimentEdit from '../views/edit/connect/reservoirs/SedimentEdit.vue';
import ReservoirsSedimentCreate from '../views/edit/connect/reservoirs/SedimentCreate.vue';

import ReservoirsNutrients from '../views/edit/connect/reservoirs/Nutrients.vue';
import ReservoirsNutrientsEdit from '../views/edit/connect/reservoirs/NutrientsEdit.vue';
import ReservoirsNutrientsCreate from '../views/edit/connect/reservoirs/NutrientsCreate.vue';

import ReservoirsWetlands from '../views/edit/connect/reservoirs/Wetlands.vue';
import ReservoirsWetlandsEdit from '../views/edit/connect/reservoirs/WetlandsEdit.vue';
import ReservoirsWetlandsCreate from '../views/edit/connect/reservoirs/WetlandsCreate.vue';

import ReservoirsWetlandsHydrology from '../views/edit/connect/reservoirs/WetlandsHydrology.vue';
import ReservoirsWetlandsHydrologyEdit from '../views/edit/connect/reservoirs/WetlandsHydrologyEdit.vue';
import ReservoirsWetlandsHydrologyCreate from '../views/edit/connect/reservoirs/WetlandsHydrologyCreate.vue';

import Recall from '../views/edit/connect/recall/Recall.vue';
import RecallEdit from '../views/edit/connect/recall/RecallEdit.vue';
import RecallCreate from '../views/edit/connect/recall/RecallCreate.vue';
import RecallDataEdit from '../views/edit/connect/recall/DataEdit.vue';
import RecallDataCreate from '../views/edit/connect/recall/DataCreate.vue';

export default [
	{ 
		path: 'cons/channels', name: 'Channels', component: Channels,
		children: [
			{ path: 'edit/:id', name: 'ChannelsEdit', component: ChannelsEdit },
			{ path: 'create', name: 'ChannelsCreate', component: ChannelsCreate },
			{ 
				path: 'initial', name: 'ChannelsInitial', component: ChannelsInitial,
				children: [
					{ path: 'edit/:id', name: 'ChannelsInitialEdit', component: ChannelsInitialEdit },
					{ path: 'create', name: 'ChannelsInitialCreate', component: ChannelsInitialCreate }
				] 
			},
			{ 
				path: 'hydsed', name: 'ChannelsHydSedLte', component: ChannelsHydSedLte,
				children: [
					{ path: 'edit/:id', name: 'ChannelsHydSedLteEdit', component: ChannelsHydSedLteEdit },
					{ path: 'create', name: 'ChannelsHydSedLteCreate', component: ChannelsHydSedLteCreate }
				] 
			},
			{ 
				path: 'nutrients', name: 'ChannelsNutrients', component: ChannelsNutrients,
				children: [
					{ path: 'edit/:id', name: 'ChannelsNutrientsEdit', component: ChannelsNutrientsEdit },
					{ path: 'create', name: 'ChannelsNutrientsCreate', component: ChannelsNutrientsCreate }
				] 
			}
		]
	},
	{ 
		path: 'cons/hrus', name: 'Hrus', component: Hrus, 
			children: [
				{ path: 'edit/:id', name: 'HrusEdit', component: HrusEdit },
				{ path: 'create', name: 'HrusCreate', component: HrusCreate }
			] 	 			
	},
	{ 
		path: 'cons/hrus-lte', name: 'HrusLte', component: HrusLte, 
			children: [
				{ path: 'edit/:id', name: 'HrusLteEdit', component: HrusLteEdit },
				{ path: 'create', name: 'HrusLteCreate', component: HrusLteCreate }
			] 	 			
	},
	{ 
		path: 'cons/routing-units', name: 'RoutingUnits', component: RoutingUnits, 		
			children: [
				{ path: 'edit/:id', name: 'RoutingUnitsEdit', component: RoutingUnitsEdit },
				{ path: 'create', name: 'RoutingUnitsCreate', component: RoutingUnitsCreate },
				{ 
					path: 'elements', name: 'RoutingUnitsElements', component: RoutingUnitsElements,
					children: [
						{ path: 'edit/:id', name: 'RoutingUnitsElementsEdit', component: RoutingUnitsElementsEdit },
						{ path: 'create', name: 'RoutingUnitsElementsCreate', component: RoutingUnitsElementsCreate }
					]
				}
			] 	  	
	},
	{ 
		path: 'cons/aquifers', name: 'Aquifers', component: Aquifers, 
			children: [
				{ path: 'edit/:id', name: 'AquifersEdit', component: AquifersEdit },
				{ path: 'create', name: 'AquifersCreate', component: AquifersCreate },
				{ 
					path: 'initial', name: 'AquifersInitial', component: AquifersInitial,
					children: [
						{ path: 'edit/:id', name: 'AquifersInitialEdit', component: AquifersInitialEdit },
						{ path: 'create', name: 'AquifersInitialCreate', component: AquifersInitialCreate }
					] 
				},		
			] 					
	},
	{ 
		path: 'cons/gwflow', name: 'Gwflow', component: Gwflow, 
			children: [
				{ path: 'grids', name: 'GwflowGrids', component: GwflowGrids },
				{ 
					path: 'zones', name: 'GwflowZone', component: GwflowZone,
					children: [
						{ path: 'edit/:id', name: 'GwflowZoneEdit', component: GwflowZoneEdit },
					] 
				},
				{ 
					path: 'fpcell', name: 'GwflowFpcell', component: GwflowFpcell,
					children: [
						{ path: 'edit/:id', name: 'GwflowFpcellEdit', component: GwflowFpcellEdit },
						{ path: 'create', name: 'GwflowFpcellCreate', component: GwflowFpcellCreate }
					] 
				},
				{ 
					path: 'rescell', name: 'GwflowRescell', component: GwflowRescell,
					children: [
						{ path: 'edit/:id', name: 'GwflowRescellEdit', component: GwflowRescellEdit },
						{ path: 'create', name: 'GwflowRescellCreate', component: GwflowRescellCreate }
					] 
				},
				{ 
					path: 'wetlands', name: 'GwflowWetlands', component: GwflowWetlands,
					children: [
						{ path: 'edit/:id', name: 'GwflowWetlandsEdit', component: GwflowWetlandsEdit },
						{ path: 'create', name: 'GwflowWetlandsCreate', component: GwflowWetlandsCreate }
					] 
				},
			] 					
	},
	{ 
		path: 'cons/reservoirs', name: 'Reservoirs', component: Reservoirs, 
		children: [
			{ path: 'edit/:id', name: 'ReservoirsEdit', component: ReservoirsEdit },
			{ path: 'create', name: 'ReservoirsCreate', component: ReservoirsCreate },
			{ 
				path: 'initial', name: 'ReservoirsInitial', component: ReservoirsInitial,
				children: [
					{ path: 'edit/:id', name: 'ReservoirsInitialEdit', component: ReservoirsInitialEdit },
					{ path: 'create', name: 'ReservoirsInitialCreate', component: ReservoirsInitialCreate }
				] 
			},
			{ 
				path: 'hydrology', name: 'ReservoirsHydrology', component: ReservoirsHydrology,
				children: [
					{ path: 'edit/:id', name: 'ReservoirsHydrologyEdit', component: ReservoirsHydrologyEdit },
					{ path: 'create', name: 'ReservoirsHydrologyCreate', component: ReservoirsHydrologyCreate }
				]  
			},
			{ 
				path: 'sediment', name: 'ReservoirsSediment', component: ReservoirsSediment,
				children: [
					{ path: 'edit/:id', name: 'ReservoirsSedimentEdit', component: ReservoirsSedimentEdit },
					{ path: 'create', name: 'ReservoirsSedimentCreate', component: ReservoirsSedimentCreate }
				] 
			},
			{ 
				path: 'nutrients', name: 'ReservoirsNutrients', component: ReservoirsNutrients,
				children: [
					{ path: 'edit/:id', name: 'ReservoirsNutrientsEdit', component: ReservoirsNutrientsEdit },
					{ path: 'create', name: 'ReservoirsNutrientsCreate', component: ReservoirsNutrientsCreate }
				] 
			},
			{ 
				path: 'wetlands', name: 'ReservoirsWetlands', component: ReservoirsWetlands,
				children: [
					{ path: 'edit/:id', name: 'ReservoirsWetlandsEdit', component: ReservoirsWetlandsEdit },
					{ path: 'create', name: 'ReservoirsWetlandsCreate', component: ReservoirsWetlandsCreate }
				] 
			},
			{ 
				path: 'wetlands_hydrology', name: 'ReservoirsWetlandsHydrology', component: ReservoirsWetlandsHydrology,
				children: [
					{ path: 'edit/:id', name: 'ReservoirsWetlandsHydrologyEdit', component: ReservoirsWetlandsHydrologyEdit },
					{ path: 'create', name: 'ReservoirsWetlandsHydrologyCreate', component: ReservoirsWetlandsHydrologyCreate }
				] 
			},
		]
	},
	{ 
		path: 'cons/recall', name: 'Recall', component: Recall, 
		children: [
			{ 
				path: 'edit/:id', name: 'RecallEdit', component: RecallEdit,
				children: [
					{ path: 'edit/:dataId', name: 'RecallDataEdit', component: RecallDataEdit },
					{ path: 'create', name: 'RecallDataCreate', component: RecallDataCreate }
				]
			},
			{ path: 'create', name: 'RecallCreate', component: RecallCreate }
		] 					
	}
];