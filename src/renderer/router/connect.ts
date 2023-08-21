import Channels from '../views/edit/connect/channels/Channels.vue';
import ChannelsEdit from '../views/edit/connect/channels/ChannelsEdit.vue';
import ChannelsCreate from '../views/edit/connect/channels/ChannelsCreate.vue';

export default [
	{ 
		path: 'cons/channels', name: 'Channels', component: Channels,
		children: [
			{ path: 'edit/:id', name: 'ChannelsEdit', component: ChannelsEdit },
			{ path: 'create', name: 'ChannelsCreate', component: ChannelsCreate }
		]
	}
];