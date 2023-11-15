<template>
	<project-container>
		<div v-if="$route.name == 'ReservoirsSediment'">
			<file-header input-file="sediment.res" docs-path="reservoirs/sediment.res" use-io>
				<router-link to="/edit/reservoirs">Reservoirs</router-link> 
				/ Sediment
			</file-header>

			<grid-view 
				api-url="reservoirs/sediment"
				use-dynamic-headers 
				show-import-export default-csv-file="sediment-res.csv" table-name="sed_res" />
		</div>
		<router-view></router-view>
	</project-container>
</template>

