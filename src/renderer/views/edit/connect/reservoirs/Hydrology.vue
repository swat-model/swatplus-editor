<template>
	<project-container>
		<div v-if="route.name == 'ReservoirsHydrology'">
			<file-header input-file="hydrology.res" docs-path="reservoirs/hydrology.res" use-io>
				<router-link to="/edit/cons/reservoirs">Reservoirs</router-link> 
				/ Hydrology
			</file-header>

			<grid-view 
				api-url="reservoirs/hydrology"
				use-dynamic-headers 
				show-import-export default-csv-file="hydrology-res.csv" table-name="hyd_res" />
		</div>
		<router-view></router-view>
	</project-container>
</template>
