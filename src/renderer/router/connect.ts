import Channels from '../views/edit/connect/channels/Channels.vue';
import ChannelsEdit from '../views/edit/connect/channels/ChannelsEdit.vue';
import ChannelsCreate from '../views/edit/connect/channels/ChannelsCreate.vue';

import ChannelsInitial from '../views/edit/connect/channels/Initial.vue';
import ChannelsInitialEdit from '../views/edit/connect/channels/InitialEdit.vue';
import ChannelsInitialCreate from '../views/edit/connect/channels/InitialCreate.vue';

import ChannelsHydSedLte from '../views/edit/connect/channels/HydSedLte.vue';
import ChannelsHydSedLteEdit from '../views/edit/connect/channels/HydSedLteEdit.vue';
import ChannelsHydSedLteCreate from '../views/edit/connect/channels/HydSedLteCreate.vue';

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
			}
		]
	}
];