<script setup lang="ts">
	import { reactive, watch, onMounted } from 'vue';
	import { RouteRecordName, useRoute } from 'vue-router';
	import { useHelpers } from '@/helpers';
	
	const route = useRoute();
	const { api, constants, errors, utilities, currentProject } = useHelpers();

	interface Page {
		loading: boolean,
		open: string[],
		subOpen: string[]
	}

	let page:Page = reactive({
		loading: false,
		open: route.name === 'Edit' ? ['Climate'] : [],
		subOpen: []
	});

	interface NavGroup {
		name: string,
		routeName: string,
		show: boolean,
		items: NavItem[]
	}

	interface NavItem {
		name: string,
		path: string,
		show: boolean,
		routeName: string,
		subItems: NavItem[],
	}

	let nav:NavGroup[] = reactive([
		{
			name: 'Climate', routeName: 'Climate', show: true,
			items: [
				{ name: 'Weather Generator', path: '/edit/climate/wgn', show: true, routeName: '', subItems: [] },
				{ 
					name: 'Weather Stations', path: '/edit/climate/stations', show: true, routeName: 'Stations', 
					subItems: [
						{ name: 'Atmospheric Deposition', path: '/edit/climate/stations/atmo', show: true, routeName: '', subItems: [] }
					]
				}
			]
		},
		{
			name: 'Connections', routeName: 'Cons', show: true,
			items: [
				{ 
					name: 'Channels', path: '/edit/cons/channels', show: true, routeName: 'Channels', 
					subItems: [
						{ name: 'Initial', path: '/edit/cons/channels/initial', show: true, routeName: '', subItems: [] },
						{ name: 'Hydrology & Sediment', path: '/edit/cons/channels/hydsed', show: true, routeName: '', subItems: [] },
						{ name: 'Nutrients', path: '/edit/cons/channels/nutrients', show: true, routeName: '', subItems: [] }
					]
				},
				{ name: 'HRUs', path: '/edit/cons/hrus', show: !currentProject.isLte, routeName: '', subItems: [] },
				{ name: 'HRUs', path: '/edit/cons/hrus-lte', show: currentProject.isLte, routeName: '', subItems: [] },
				{ 
					name: 'Routing Units', path: '/edit/cons/routing-units', show: !currentProject.isLte, routeName: 'RoutingUnits', 
					subItems: [
						{ name: 'Elements', path: '/edit/cons/routing-units/elements', show: true, routeName: '', subItems: [] }
					]
				},
				{ 
					name: 'Aquifers', path: '/edit/cons/aquifers', show: !currentProject.isLte, routeName: 'Aquifers', 
					subItems: [
						{ name: 'Initial', path: '/edit/cons/aquifers/initial', show: true, routeName: '', subItems: [] }
					]
				},
				{ 
					name: 'Reservoirs', path: '/edit/cons/reservoirs', show: !currentProject.isLte, routeName: 'Reservoirs', 
					subItems: [
						{ name: 'Reservoir Hydrology', path: '/edit/cons/reservoirs/hydrology', show: true, routeName: '', subItems: [] },
						{ name: 'Initial', path: '/edit/cons/reservoirs/initial', show: true, routeName: '', subItems: [] },
						{ name: 'Sediment', path: '/edit/cons/reservoirs/sediment', show: true, routeName: '', subItems: [] },
						{ name: 'Nutrients', path: '/edit/cons/reservoirs/nutrients', show: true, routeName: '', subItems: [] },
						{ name: 'Wetlands', path: '/edit/cons/reservoirs/wetlands', show: true, routeName: '', subItems: [] },
						{ name: 'Wetland Hydrology', path: '/edit/cons/reservoirs/wetlands_hydrology', show: true, routeName: '', subItems: [] }
					]
				},
				{ name: 'Point Sources / Inlets', path: '/edit/cons/recall', show: !currentProject.isLte, routeName: '', subItems: [] }
			]
		},
		{
			name: 'Basin', routeName: 'Basin', show: true,
			items: [
				{ name: 'Codes', path: '/edit/basin/codes', show: true, routeName: '', subItems: [] },
				{ name: 'Parameters', path: '/edit/basin/parameters', show: true, routeName: '', subItems: [] }
			]
		},
		{
			name: 'Regions', routeName: 'Regions', show: true,
			items: [
				{ 
					name: 'Landscape Units', path: '/edit/regions/ls_units', show: true, routeName: 'LandscapeUnits', 
					subItems: [
						{ name: 'Elements', path: '/edit/regions/ls_units/elements', show: true, routeName: '', subItems: [] }
					]
				}
			]
		},
		{
			name: 'Land Use Management', routeName: 'Lum', show: !currentProject.isLte,
			items: [
				{ name: 'Land Use Management', path: '/edit/lum/landuse', show: true, routeName: '', subItems: [] },
				{ name: 'Plant Communities', path: '/edit/lum/plant', show: true, routeName: '', subItems: [] },
				{ name: 'Management Schedules', path: '/edit/lum/mgt', show: true, routeName: '', subItems: [] },
				{ 
					name: 'Operations Databases', path: '/edit/lum/ops', show: true, routeName: 'Operations', 
					subItems: [
						{ name: 'Harvest', path: '/edit/lum/ops/harvest', show: true, routeName: '', subItems: [] },
						{ name: 'Graze', path: '/edit/lum/ops/graze', show: true, routeName: '', subItems: [] },
						{ name: 'Irrigation', path: '/edit/lum/ops/irrigation', show: true, routeName: '', subItems: [] },
						{ name: 'Chemical Applications', path: '/edit/lum/ops/chemapp', show: true, routeName: '', subItems: [] },
						{ name: 'Fire', path: '/edit/lum/ops/fire', show: true, routeName: '', subItems: [] },
						{ name: 'Sweep', path: '/edit/lum/ops/sweep', show: true, routeName: '', subItems: [] }
					]
				},
				{ name: 'Curve Numbers', path: '/edit/lum/cntable', show: true, routeName: '', subItems: [] },
				{ name: 'Conservation Practices', path: '/edit/lum/conspractice', show: true, routeName: '', subItems: [] },
				{ name: `Manning's n`, path: '/edit/lum/ovntable', show: true, routeName: '', subItems: [] }
			]
		},
		{
			name: 'Decision Tables', routeName: 'Dtl', show: true,
			items: [
				{ name: 'Land Use Management', path: '/edit/decision-table/lum', show: true, routeName: '', subItems: [] },
				{ name: 'Reservoir Release', path: '/edit/decision-table/res_rel', show: !currentProject.isLte, routeName: '', subItems: [] },
				{ name: 'Scenario Land Use', path: '/edit/decision-table/scen_lu', show: !currentProject.isLte, routeName: '', subItems: [] },
				{ name: 'Flow Conditions', path: '/edit/decision-table/flo_con', show: !currentProject.isLte, routeName: '', subItems: [] }
			]
		},
		{
			name: 'Calibration', routeName: 'Change', show: !currentProject.isLte,
			items: [
				{ 
					name: 'Hard Calibration', path: '/edit/change/hard', show: true, routeName: 'HardCalibration', 
					subItems: [
						{ name: 'Parameters', path: '/edit/change/hard/parms', show: true, routeName: '', subItems: [] }
					]
				},
				{ 
					name: 'Soft Calibration', path: '/edit/change/soft', show: true, routeName: 'SoftCalibration', 
					subItems: [
						{ name: 'Water Balance', path: '/edit/change/soft/wb', show: true, routeName: '', subItems: [] },
						{ name: 'Plant Growth', path: '/edit/change/soft/plant', show: true, routeName: '', subItems: [] }
					]
				}
			]
		},
		{
			name: 'Constituents', routeName: 'Constituents', show: true,
			items: [
				{ name: 'Soil Plant', path: '/edit/constituents/soil_plant', show: !currentProject.isLte, routeName: '', subItems: [] },
				{ name: 'Organic Mineral', path: '/edit/constituents/om_water', show: true, routeName: '', subItems: [] },
				{ name: 'Pesticides', path: '/edit/constituents/pest', show: !currentProject.isLte, routeName: '', subItems: [] },
				{ name: 'Pathogens', path: '/edit/constituents/path', show: !currentProject.isLte, routeName: '', subItems: [] },
				{ 
					name: 'Salts', path: '/edit/constituents/salt', show: false && !currentProject.isLte, routeName: 'Salts', 
					subItems: [
						{ name: 'Point Sources', path: '/edit/constituents/salt/recall', show: true, routeName: '', subItems: [] },
						{ name: 'Atmospheric Deposition', path: '/edit/constituents/salt/atmo', show: true, routeName: '', subItems: [] },
						{ name: 'Road Salt', path: '/edit/constituents/salt/road', show: true, routeName: '', subItems: [] },
						{ name: 'Fertilizer & Soil Amendments', path: '/edit/constituents/salt/fert', show: true, routeName: '', subItems: [] },
						{ name: 'Irrigation', path: '/edit/constituents/salt/irr', show: true, routeName: '', subItems: [] },
						{ name: 'Urban Runoff', path: '/edit/constituents/salt/urban', show: true, routeName: '', subItems: [] }
					]
				}
			]
		},
		{
			name: 'Hydrology', routeName: 'Hydrology', show: !currentProject.isLte,
			items: [
				{ name: 'Hydrology', path: '/edit/hydrology/hydrology', show: true, routeName: '', subItems: [] },
				{ name: 'Topography', path: '/edit/hydrology/topography', show: true, routeName: '', subItems: [] },
				{ name: 'Fields', path: '/edit/hydrology/fields', show: true, routeName: '', subItems: [] }
			]
		},
		{
			name: 'Soils', routeName: 'Soils', show: true,
			items: [
				{ name: 'Soils', path: '/edit/soils/soils', show: !currentProject.isLte, routeName: '', subItems: [] },
				{ name: 'Nutrients', path: '/edit/soils/soil-nutrients', show: !currentProject.isLte, routeName: '', subItems: [] },
				{ name: 'Soil Textures', path: '/edit/soils/soils-lte', show: currentProject.isLte, routeName: '', subItems: [] }
			]
		},
		{
			name: 'Databases', routeName: 'Db', show: true,
			items: [
				{ name: 'Plants', path: '/edit/db/plants', show: true, routeName: '', subItems: [] },
				{ name: 'Fertilizer', path: '/edit/db/fertilizer', show: !currentProject.isLte, routeName: '', subItems: [] },
				{ name: 'Tillage', path: '/edit/db/tillage', show: !currentProject.isLte, routeName: '', subItems: [] },
				{ name: 'Pesticides', path: '/edit/db/pesticides', show: !currentProject.isLte, routeName: '', subItems: [] },
				{ name: 'Pathogens', path: '/edit/db/pathogens', show: !currentProject.isLte, routeName: '', subItems: [] },
				{ name: 'Urban', path: '/edit/db/urban', show: true, routeName: '', subItems: [] },
				{ name: 'Septic', path: '/edit/db/septic', show: !currentProject.isLte, routeName: '', subItems: [] },
				{ name: 'Snow', path: '/edit/db/snow', show: !currentProject.isLte, routeName: '', subItems: [] }
			]
		},
		{
			name: 'Structural', routeName: 'Structural', show: !currentProject.isLte,
			items: [
				{ name: 'Tile Drains', path: '/edit/structural/tiledrain', show: true, routeName: '', subItems: [] },
				{ name: 'Septic Systems', path: '/edit/structural/septic', show: true, routeName: '', subItems: [] },
				{ name: 'Filter Strips', path: '/edit/structural/filterstrip', show: true, routeName: '', subItems: [] },
				{ name: 'Grassed Waterways', path: '/edit/structural/grassedww', show: true, routeName: '', subItems: [] },
				{ name: 'User BMPs', path: '/edit/structural/bmpuser', show: true, routeName: '', subItems: [] }
			]
		},
		{
			name: 'Water Rights', routeName: 'WaterRights', show: !currentProject.isLte,
			items: [
				{ name: 'Water Allocation', path: '/edit/water-rights/allocation', show: true, routeName: '', subItems: [] }
			]
		}
	])

	function shownNavItems(items:NavItem[]) {
		return items.filter((el:any) => { return el.show; })
	}

	function shownNavGroups(items:NavGroup[]) {
		return items.filter((el:any) => { return el.show; })
	}

	function processSubOpenItem(thisRoute:RouteRecordName|null|undefined, name:string) {
		if (thisRoute?.toString().includes(name)) page.subOpen.push(name);
		else {
			let idx = page.subOpen.indexOf(name);
			if (idx > -1) {
				page.subOpen.splice(idx, 1);
			}
		}
	}

	function processSubOpen(thisRoute:RouteRecordName|null|undefined) {
		let subOpenItems = [
			'Channels', 'Aquifers', 'Reservoirs', 'RoutingUnits', 
			'Stations', 'Operations', 'LandscapeUnits', 'HardCalibration', 'SoftCalibration', 'Constituents'
		];

		for (let item of subOpenItems) {
			processSubOpenItem(thisRoute, item);
		}
	}

	watch(() => route.name, (newRoute) => processSubOpen(newRoute))

	onMounted(() => processSubOpen(route.name));
</script>

<template>
	<project-container :loading="page.loading" add-error-frame>
		<v-navigation-drawer permanent id="secondary-nav">
			<v-list v-model:opened="page.open" :lines="false" density="compact" nav>
				<v-list-group v-for="navGroup in shownNavGroups(nav)" :key="navGroup.name"
					:value="navGroup.routeName" expand-icon="fas fa-angle-left" collapse-icon="fas fa-angle-down" class="fa-2xs">
					<template #activator="{ props }">
						<v-list-item v-bind="props" :title="navGroup.name" color="primary" variant="tonal"></v-list-item>
					</template>
					<v-list-item v-for="navItem in shownNavItems(navGroup.items)" :key="navItem.name"
						:to="navItem.path" :title="navItem.name" color="secondary"
						:class="navItem.subItems.length > 0 && page.subOpen.includes(navItem.routeName) ? 'sub-open' : ''">
						<v-list v-if="navItem.subItems.length > 0 && page.subOpen.includes(navItem.routeName)" :lines="false" density="compact" nav>
							<v-list-item v-for="navSubItem in shownNavItems(navItem.subItems)" :key="navSubItem.name" 
								:to="navSubItem.path" :title="navSubItem.name"></v-list-item>
						</v-list>
					</v-list-item>
				</v-list-group>
			</v-list>
		</v-navigation-drawer>
		<v-main>
			<div class="py-3 px-6">
				<div v-if="$route.path == '/edit'">
					<h1 class="text-h5 mb-3">Edit SWAT+ inputs</h1>

					<p>
						Use the menu on the left to edit SWAT+ input data. We recommend starting in the climate section, and importing your weather generators and observed weather data.
						If you're coming from GIS, when you import weather generators or observed data, it will create weather stations and match them to your spatial objects automatically.
					</p>

					<h2 class="text-h5 mb-3 mt-4">Help</h2>
					<p>
						In the upper right corner of each editor section linked from the left menu is a book icon <font-awesome-icon :icon="['fas', 'book']" /> you may click
						to see our documentation website for that section. Documentation is still a work in progress.
					
						In addition, click the <router-link to="/help" class="text-primary"><font-awesome-icon :icon="['fas', 'question-circle']" /></router-link> in the lower left corner of this window for 
						links to resources to help you with SWAT+ and the editor. User groups are available where you can ask questions if you get stuck.
					</p>

					<v-divider class="my-6"></v-divider>

					<p>
						Any SWAT+ features not available through the editor can be modified manually through the text input files.
						Edit your data as needed through the editor, then proceed to the <router-link to="/runall" class="text-primary">Run SWAT+</router-link> section. 
						After your initial files are written, you can modify them or add additional SWAT+ input files to your model.
						Make a copy of any changes before returning to SWAT+ Editor, as the editor may overwrite them.
					</p>
				</div>
				<router-view></router-view>
			</div>
		</v-main>
	</project-container>
</template>