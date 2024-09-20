<script setup lang="ts">
	import { reactive } from 'vue';
	import { useHelpers } from '@/helpers';
	const { currentProject } = useHelpers();

	interface Props {
		decisionsTable: string,
		description: string
	}

	const props = withDefaults(defineProps<Props>(), {
		decisionsTable: '',
		description: ''
	});

	let page:any = reactive({
		tab: 'project'
	})
</script>

<template>
	<div>
		<file-header :input-file="decisionsTable" docs-path="decision-tables">
			Decision Tables / {{description}}
		</file-header>

		<p>
			If you want to create a new table, please select a similar table from the list below, and use the copy function. 
			You may then edit the copy to suit your needs.
			You may also modify or add decision tables offline and import them into SWAT+ Editor using the import/export button below.
			Please export first to get your existing tables, and adhere to the formatting of the file.
		</p>

		<v-alert v-if="decisionsTable==='lum.dtl' && !currentProject.isLte" type="warning" icon="$warning" variant="tonal" border="start" class="mb-4">
			This section is for advanced decision table management. 
			We recommend most users use the <router-link to="/edit/lum/mgt">management schedule builder</router-link>.
		</v-alert>
		<v-alert v-if="decisionsTable==='flo_con.dtl'" type="warning" icon="$warning" variant="tonal" border="start" class="mb-4">
			We recommend not using flow condition tables at this time unless you are an advanced user who has already been in touch with the SWAT+ model development team to discuss your needs.
		</v-alert>
		<v-alert v-if="decisionsTable==='scen_lu.dtl'" type="warning" icon="$warning" variant="tonal" border="start" class="mb-4">
			Support for scenario land use decision tables is planned for a <b>SWAT+ Editor 3.1 release</b>. In the interim, please add these tables and a scen_dtl.upd file outside of the interface. Contact the model development team for assistance.
		</v-alert>
		
		<v-card>
			<v-tabs v-model="page.tab" bg-color="primary">
				<v-tab value="project">Project Tables</v-tab>
				<v-tab value="datasets">Datasets Library</v-tab>
			</v-tabs>

			<v-card-item>
				<v-window v-model="page.tab">
					<v-window-item value="project">
						<p>
							The following tables are available in your project. 
							Click the datasets library tab to see additional examples you can copy to your project.
						</p>

						<grid-view 
							:api-url="`decision_table/tables/${decisionsTable}`" auto-height
							use-dynamic-headers hide-create hide-delete
							edit-path-prefix="/edit/decision-table/type/project/"
							show-import-export :default-csv-file="decisionsTable" :table-name="decisionsTable" import-export-description="text"></grid-view>
					</v-window-item>

					<v-window-item value="datasets">
						<p>
							The following tables are available in your datasets library.
							Select a table below to view it and copy to your project if desired.
						</p>

						<grid-view 
							:api-url="`decision_table/dataset-tables/${decisionsTable}`" auto-height
							use-dynamic-headers hide-create hide-delete
							edit-path-prefix="/edit/decision-table/type/datasets/"
							show-import-export :default-csv-file="decisionsTable" :table-name="decisionsTable" import-export-description="text"></grid-view>
					</v-window-item>
				</v-window>
			</v-card-item>
		</v-card>
	</div>
</template>
