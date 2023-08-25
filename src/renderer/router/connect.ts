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
];