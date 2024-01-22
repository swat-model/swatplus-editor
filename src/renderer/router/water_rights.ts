import WaterAllocation from '../views/edit/water_rights/WaterAllocation.vue';
import WaterAllocationEdit from '../views/edit/water_rights/WaterAllocationEdit.vue';
import WaterAllocationCreate from '../views/edit/water_rights/WaterAllocationCreate.vue';

export default [
	{ 
		path: 'water-rights/allocation', name: 'WaterAllocation', component: WaterAllocation,
		children: [
			{ path: 'edit/:id', name: 'WaterAllocationEdit', component: WaterAllocationEdit },
			{ path: 'create', name: 'WaterAllocationCreate', component: WaterAllocationCreate }
		]  
	}
];