<script setup lang="ts">
	import { useRoute } from 'vue-router';
	const route = useRoute();

	let table:any = {
		apiUrl: 'lum/mgt_sch',
		headers: [
			{ key: 'name', label: 'Name' },
			{ key: 'num_ops', label: 'Number of operations' },
			{ key: 'num_auto', label: 'Number of auto schedules' }
		],
	};
</script>

<template>
	<project-container>
		<div v-if="$route.name === 'Management'">
			<file-header input-file="management.sch" docs-path="land-use-management#management-schedules">
				Management Schedules
			</file-header>

			<grid-view 
				:api-url="table.apiUrl" :headers="table.headers"
				show-import-export default-csv-file="management.sch" table-name="mgt_sch" import-export-description="text">
			</grid-view>
		</div>
		<router-view></router-view>
	</project-container>
</template>
