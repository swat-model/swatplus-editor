<script setup lang="ts">
	import { reactive, computed, onMounted } from 'vue';
	import { useRoute } from 'vue-router';
	import { VDataTable } from 'vuetify/labs/VDataTable'
	import { usePlugins } from '../../../../plugins';

	const route = useRoute();
	const { api, currentProject, errors } = usePlugins();

	let page:any = reactive({
		loading: false,
		error: null
	});

	let table:any = reactive({
		loading: false,
		error: null,
		itemsPerPage: 50,
		page: 1,
		sortBy: [
			{ key: 'name', order: 'asc' }
		],
		fields: [
			{ key: 'name', title: 'Name' }
		]
	});

	let data:any = reactive({
		total: 0,
		matches: 0,
		items: []
	});

	async function get() {
		table.loading = true;
		table.error = null;

		try {
			let qPage = table.page;
			let qSort = '';
			let qRev = 'n';
			let qPerPage = table.itemsPerPage;

			if (table.sortBy.length) {
				qSort = table.sortBy[0].key;
				qRev = table.sortBy[0].order === 'desc' ? 'y' : 'n';
			}

			let query = `?sort=${qSort}&reverse=${qRev}&page=${qPage}&per_page=${qPerPage}`;
			
			const response = await api.get(`channels/items${query}`, currentProject.getApiHeader());
			errors.log(response.data);
			data = response.data;
		} catch (error) {
			errors.log(error);
		}
		
		table.loading = false;
	}

	async function doSort(newSortBy) {
		table.sortBy = newSortBy;
		await get();
	}

	onMounted(async () => {
		page.loading = true;
		await get();
		page.loading = false;
	});
</script>

<template>
	<project-container :loading="page.loading">
		<div v-if="$route.name == 'Channels'">
			<file-header input-file="chandeg.con" docs-path="connections/channels">
				Channels
			</file-header>

			<v-data-table
				v-model:items-per-page="table.itemsPerPage" :sortBy="table.sortBy"
				:page="table.page" hide-default-footer
				:headers="table.fields"
				:items-length="data.total"
				:items="data.items"
				:loading="table.loading"
				@update:sortBy="doSort"
				class="elevation-1">
				<template #bottom>
					
				</template>
			</v-data-table>

			<action-bar>
				<v-btn variant="flat" color="primary">Create Record</v-btn>
				<v-pagination v-model="table.page" @update:modelValue="get" :total-visible="Math.ceil(data.total / table.itemsPerPage)"
					:length="Math.ceil(data.total / table.itemsPerPage)" class="ml-auto" size="small"></v-pagination>
			</action-bar>
		</div>
		<router-view></router-view>
	</project-container>
</template>