<template>
	<project-container>
		<div v-if="$route.name == 'HrusLte'">
			<file-header input-file="hru-lte.con" docs-path="connections/hrus">
				HRUs
			</file-header>

			<connect-grid-view
				api-url="hrus-lte"
				collection-description="HRUs"
				:fields="fields" :router-link-fields="routerLinkFields" />
		</div>
		<router-view></router-view>
	</project-container>
</template>

<script>
export default {
	name: 'HrusLte',
	data() {
		return {
			fields: [
				{ key: 'soil_text', label: 'Soil', sortable: true, class: 'text-right' },
				{ key: 'grow_start', label: 'Grow Start', sortable: true, class: 'text-right' },
				{ key: 'grow_end', label: 'Grow End', sortable: true, class: 'text-right' },
				{ key: 'plnt_typ', label: 'Plant', sortable: true, class: 'text-right' }
			],
			routerLinkFields: [
				{ key: 'soil_text', route: '/edit/soils-lte/edit/' },
				{ key: 'grow_start', route: '/edit/decision_table/edit/' },
				{ key: 'grow_end', route: '/edit/decision_table/edit/' },
				{ key: 'plnt_typ', route: '/edit/db/plants/edit/' }
			]
		}
	}
}
</script>