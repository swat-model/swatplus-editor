import DecisionsLum from '../views/edit/decision_table/Lum.vue';
import DecisionsResRel from '../views/edit/decision_table/ResRel.vue';
import DecisionsFloCon from '../views/edit/decision_table/FloCon.vue';
import DecisionsScenLu from '../views/edit/decision_table/ScenLu.vue';
import DecisionsEdit from '../views/edit/decision_table/DecisionsEdit.vue';

export default [
	{ path: 'decision-table/type/:dbtype/edit/:id', name: 'DecisionsEdit', component: DecisionsEdit, children: [] },
	{ path: 'decision-table/lum', name: 'DecisionsLum', component: DecisionsLum, children: [] },
	{ path: 'decision-table/res_rel', name: 'DecisionsResRel', component: DecisionsResRel, children: [] },
	{ path: 'decision-table/flo_con', name: 'DecisionsFloCon', component: DecisionsFloCon, children: [] },
	{ path: 'decision-table/scen_lu', name: 'DecisionsScenLu', component: DecisionsScenLu, children: [] }
];