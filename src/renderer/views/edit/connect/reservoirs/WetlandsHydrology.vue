<template>
	<project-container>
		<div v-if="route.name == 'ReservoirsWetlandsHydrology'">
			<file-header input-file="hydrology.wet" docs-path="wetlands/hydrology.wet" use-io>
				<router-link to="/edit/cons/reservoirs">Reservoirs</router-link> 
				/ Wetlands Hydrology
			</file-header>

			<grid-view 
				api-url="reservoirs/wetlands-hydrology"
				use-dynamic-headers 
				show-import-export default-csv-file="hydrology-wet.csv" table-name="hyd_wet"></grid-view>
			
		</div>
		<router-view></router-view>
	</project-container>
</template>

