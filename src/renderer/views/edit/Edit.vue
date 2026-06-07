<script setup lang="ts">
import { reactive, watch, onMounted } from 'vue';
import { RouteRecordName, useRoute } from 'vue-router';
import { useHelpers } from '@/helpers';
// import { useTaskStore } from '@/store/task';
// import { storeToRefs } from 'pinia';

const route = useRoute();
const { currentProject } = useHelpers();
// const taskStore = useTaskStore();
// const { task } = storeToRefs(taskStore);

interface Page {
	loading: boolean,
	open: string[],
	subOpen: string[]
}

let page: Page = reactive({
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

let nav: NavGroup[] = reactive([
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
			{ name: 'Point Sources / Inlets', path: '/edit/cons/recall', show: !currentProject.isLte, routeName: '', subItems: [] },
			{
				name: 'Groundwater Flow', path: '/edit/cons/gwflow', show: !currentProject.isLte, routeName: 'Gwflow',
				subItems: [
					{ name: 'Zones', path: '/edit/cons/gwflow/zones', show: true, routeName: '', subItems: [] },
					{ name: 'Grid Data', path: '/edit/cons/gwflow/grids', show: true, routeName: '', subItems: [] },
					{ name: 'Reservoirs', path: '/edit/cons/gwflow/rescell', show: true, routeName: '', subItems: [] },
					{ name: 'Floodplain', path: '/edit/cons/gwflow/fpcell', show: true, routeName: '', subItems: [] },
					{ name: 'Wetlands', path: '/edit/cons/gwflow/wetlands', show: true, routeName: '', subItems: [] },
					{ name: 'Solutes', path: '/edit/cons/gwflow/solutes', show: true, routeName: '', subItems: [] },
				]
			},
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
				name: 'Salts', path: '/edit/constituents/salts', show: !currentProject.isLte, routeName: 'Salts',
				subItems: [
					{ name: 'Point Sources', path: '/edit/constituents/salts/recall', show: true, routeName: '', subItems: [] },
					{ name: 'Atmospheric Deposition', path: '/edit/constituents/salts/atmo', show: true, routeName: '', subItems: [] },
					{ name: 'Road Salt', path: '/edit/constituents/salts/road', show: true, routeName: '', subItems: [] },
					{ name: 'Fertilizer & Soil Amendments', path: '/edit/constituents/salts/fert', show: true, routeName: '', subItems: [] },
					{ name: 'Urban Runoff', path: '/edit/constituents/salts/urban', show: true, routeName: '', subItems: [] },
					{ name: 'Plant Influence', path: '/edit/constituents/salts/plants', show: true, routeName: '', subItems: [] },
					{ name: 'Aquifer Initial Conditions', path: '/edit/constituents/salts/aqu', show: true, routeName: '', subItems: [] },
					{ name: 'Channel Initial Conditions', path: '/edit/constituents/salts/cha', show: true, routeName: '', subItems: [] },
					{ name: 'Reservoir Initial Conditions', path: '/edit/constituents/salts/res', show: true, routeName: '', subItems: [] },
					{ name: 'HRU Initial Conditions', path: '/edit/constituents/salts/hru', show: true, routeName: '', subItems: [] },
					{ name: 'Irrigation', path: '/edit/constituents/salts/irr', show: true, routeName: '', subItems: [] }
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
	/*{
		name: 'Water Rights', routeName: 'WaterRights', show: !currentProject.isLte,
		items: [
			{ name: 'Water Allocation', path: '/edit/water-rights/allocation', show: true, routeName: '', subItems: [] }
		]
	}*/
])

function shownNavItems(items: NavItem[]) {
	return items.filter((el: any) => { return el.show; })
}

function shownNavGroups(items: NavGroup[]) {
	return items.filter((el: any) => { return el.show; })
}

function processSubOpenItem(thisRoute: RouteRecordName | null | undefined, name: string) {
	if (thisRoute?.toString().includes(name)) page.subOpen.push(name);
	else {
		let idx = page.subOpen.indexOf(name);
		if (idx > -1) {
			page.subOpen.splice(idx, 1);
		}
	}
}

function processSubOpen(thisRoute: RouteRecordName | null | undefined) {
	let subOpenItems = [
		'Channels', 'Aquifers', 'Reservoirs', 'RoutingUnits', 'Gwflow',
		'Stations', 'Operations', 'LandscapeUnits', 'HardCalibration', 'SoftCalibration', 'Constituents', 'Salts'
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
				<v-list-group v-for="navGroup in shownNavGroups(nav)" :key="navGroup.name" :value="navGroup.routeName"
					expand-icon="fas fa-angle-left" collapse-icon="fas fa-angle-down" class="fa-2xs">
					<template #activator="{ props }">
						<v-list-item v-bind="props" :title="navGroup.name" color="primary"
							variant="tonal"></v-list-item>
					</template>
					<v-list-item v-for="navItem in shownNavItems(navGroup.items)" :key="navItem.name" :to="navItem.path"
						:title="navItem.name" color="secondary"
						:class="navItem.subItems.length > 0 && page.subOpen.includes(navItem.routeName) ? 'sub-open' : ''">
						<v-list v-if="navItem.subItems.length > 0 && page.subOpen.includes(navItem.routeName)"
							:lines="false" density="compact" nav>
							<v-list-item v-for="navSubItem in shownNavItems(navItem.subItems)" :key="navSubItem.name"
								:to="navSubItem.path" :title="navSubItem.name"></v-list-item>
						</v-list>
					</v-list-item>
				</v-list-group>
			</v-list>
		</v-navigation-drawer>
		<v-main class="layout-fix">
			<div class="py-3 px-6">
				<div v-if="route.path == '/edit'">
					<h1 class="text-h5 mb-3 font-weight-bold tracking-tight judul">Edit SWAT+ inputs</h1>

					<p class="isi">
						Gunakan menu di sebelah kiri untuk mengedit data input SWAT+. Kami sarankan untuk memulai di
						bagian
						iklim, dan mengimpor generator cuaca dan data cuaca yang Anda amati.
						Jika Anda berasal dari GIS, saat Anda mengimpor generator cuaca atau data yang diamati, sistem
						akan
						membuat stasiun cuaca dan mencocokkannya dengan objek spasial Anda secara otomatis.
					</p>

					<h2 class="text-h5 mb-3 mt-4 judul">Help</h2>
					<p class="isi">
						Di sudut kanan atas dari setiap bagian editor yang terhubung dari menu kiri adalah ikon buku
						<font-awesome-icon :icon="['fas', 'book']" /> yang dapat Anda klik
						untuk melihat situs web dokumentasi kami untuk bagian tersebut. Dokumentasi masih dalam proses
						pengembangan.

						Sebagai tambahan, klik <router-link to="/help" class="text-primary"><font-awesome-icon
								:icon="['fas', 'question-circle']" /></router-link> di sudut kiri bawah jendela ini
						untuk tautan ke sumber daya yang akan membantu Anda dengan SWAT+ dan editor. Kelompok pengguna
						tersedia di	mana Anda dapat mengajukan pertanyaan jika Anda mengalami kesulitan.
					</p>

					<v-divider class="my-6"></v-divider>

					<p class="isi">
						Fitur SWAT+ apa pun yang tidak tersedia melalui editor dapat dimodifikasi secara manual melalui
						file input teks.
						Edit data Anda sesuai kebutuhan melalui editor, lalu lanjutkan ke bagian <router-link to="/run"
							class="text-primary">Run SWAT+</router-link>.
						Setelah file awal Anda ditulis, Anda dapat memodifikasinya atau menambahkan file input SWAT+
						tambahan ke	model Anda.
						Buat salinan perubahan apa pun sebelum kembali ke Editor SWAT+, karena editor dapat menimpanya.
					</p>
				</div>
				<router-view></router-view>
			</div>
		</v-main>
	</project-container>
</template>

<style scoped>

#secondary-nav {
	width: 250px;
	/* border-right: 1px solid rgba(250, 171, 0, 0.05); */
}

.sub-open {
	background-color: rgba(var(--v-secondary-focus), 0.08);
}

.judul {
	animation: slideInFromTop 0.3s ease-out;
	/* color: rgb(var(--v-theme-on-surface)); */
}

.isi {
	animation: slideInFromLeft 0.5s ease-out forwards;
}

/* .v-list-group {
	transition: all 0.3s ease;
} */

/* .v-list-item--active {
	background: linear-gradient(90deg, rgba(var(--v-theme-primary), 0.1) 0%, transparent 100%) !important;
	font-weight: bold;
} */

@keyframes slideInFromTop {
	from {
		opacity: 0;
		transform: translateY(-10px);
	}

	to {
		opacity: 1;
		transform: translateY(0);
	}
}

@keyframes slideInFromLeft {
	from {
		opacity: 0;
		transform: translateX(-20px);
	}

	to {
		opacity: 1;
		transform: translateX(0);
	}
}

@keyframes expand {
	from {
		width: 0;
	}

	to {
		width: 40px;
		/* Sesuai lebar akhir yang diinginkan */
	}
}
</style>