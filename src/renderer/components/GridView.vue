<script setup lang="ts">
	import { reactive, onMounted, computed, watch } from 'vue';
	import { useRoute } from 'vue-router';
	import { useDisplay } from 'vuetify';
	import { VSkeletonLoader } from 'vuetify/labs/VSkeletonLoader';
	// @ts-ignore
	import _ from 'underscore';
	import { usePlugins } from '../plugins';

	const route = useRoute();
	const { height } = useDisplay();
	const { api, currentProject, errors, formatters, utilities } = usePlugins();

	const tableHeight = computed(() => {
		if (height.value < 730) return '60vh';
		if (height.value < 900) return '70vh';
		if (height.value < 1050) return '75vh';
		return '78vh';
	})

	interface Props {
		apiUrl: string,
		deleteApiUrl?: string | null
		headers?: GridViewHeader[],
		useDynamicHeaders?: boolean,
		noActionBar?: boolean,
		fullWidthActionBar?: boolean,
		hideSummary?: boolean,
		hideFilter?: boolean,
		hideCreate?: boolean,
		hideEdit?: boolean,
		hideDelete?: boolean,
		itemsPerPage?: number,
		defaultSort?: [string,string], //[sort key, asc or desc]
		hideFields?: string[],
		showImportExport?: boolean,
		defaultCsvFile?: string,
		tableName?: string
	}

	const props = withDefaults(defineProps<Props>(), {
		apiUrl: '',
		deleteApiUrl: null,
		headers: () => <GridViewHeader[]>[],
		useDynamicHeaders: false,
		noActionBar: false,
		fullWidthActionBar: false,
		hideSummary: false,
		hideFilter: false,
		hideCreate: false,
		hideEdit: false,
		hideDelete: false,
		itemsPerPage: 50,
		defaultSort: () => ['name', 'asc'],
		hideFields: () => ['id'],
		showImportExport: false,
		defaultCsvFile: '',
		tableName: ''
	});

	const loaderArray = computed(() => {
		let arr:number[] = [];
		for(let i = 0; i < props.itemsPerPage; i++) {
			arr.push(i);
		}
		return arr;
	});

	const showFirst = computed(() => {
		if (data.total < 1) return 0;
		return (table.page-1) * table.itemsPerPage + 1
	});

	const showLast = computed(() => {
		var max = (table.page-1) * table.itemsPerPage + table.itemsPerPage
		return max > data.matches ? data.matches : max;
	});

	let page:any = reactive({
		loading: false,
		error: null
	});

	let table:any = reactive({
		loading: false,
		error: null,
		itemsPerPage: props.itemsPerPage,
		page: 1,
		sortBy: props.defaultSort,
		headers: props.headers,
		filter: null
	});

	let data:any = reactive({
		total: 0,
		matches: 0,
		items: []
	});

	async function get(init = false) {
		table.loading = true;
		table.error = null;

		try {
			let qPage = table.page;
			let qSort = '';
			let qRev = 'n';
			let qPerPage = table.itemsPerPage;

			if (table.sortBy.length) {
				qSort = table.sortBy[0];
				qRev = table.sortBy[1] === 'desc' ? 'y' : 'n';
			}

			let filter = !props.hideFilter && table.filter !== null ? `&filter=${encodeURIComponent(table.filter)}` : '';

			let query = `?sort=${qSort}&reverse=${qRev}&page=${qPage}&per_page=${qPerPage}${filter}`;
			
			const response = await api.get(`${props.apiUrl}${query}`, currentProject.getApiHeader());
			errors.log(response.data);
			data.total = response.data.total;
			data.matches = response.data.matches;
			data.items = response.data.items;

			if (init) {
				getDynamicHeaders();
			}
		} catch (error) {
			errors.log(error);
		}
		
		table.loading = false;
	}

	function getDynamicHeaders() {
		if (props.useDynamicHeaders && data.items.length > 0) {
			let item = data.items[0];
			let keys = Object.keys(item);

			for (let key of keys) {
				if (!props.hideFields.includes(key) && !Array.isArray(item[key])) {
					let header:GridViewHeader = <GridViewHeader>{
						key: key,
						type: item[key] == null ? 'string' : typeof(item[key]),
						decimals: typeof(item[key]) == 'number' ? 2 : 0,
						class: typeof(item[key]) == 'number' ? 'text-right' : ''
					};
					
					if (key == 'name') table.headers.unshift(header);
					else table.headers.push(header);
				}
			}
		}
	}

	async function doSort(newSortByKey:string) {
		let dir = table.sortBy[1] === 'asc' ? 'desc' : 'asc';
		table.sortBy = [newSortByKey, dir];
		await get(false);
	}

	function getNumPages() {
		return Math.ceil(data.total / table.itemsPerPage);
	}

	async function filterChange() {
		table.page = 1;
		_.debounce(await get(false), 500);
	}

	onMounted(async () => {
		page.loading = true;
		await get(true);
		page.loading = false;
	});

	watch(() => route.name, async () => await get(true))
</script>

<template>
	<project-container :loading="page.loading">
		<div class="d-flex align-end mb-4">
			<div>
				<v-text-field density="compact" variant="solo" append-inner-icon="fas fa-magnifying-glass" single-line hide-details
					class="mb-0" style="width:300px"
					label="Search..." v-model="table.filter" @input="filterChange"></v-text-field>
			</div>
			<div v-if="!props.hideSummary" class="ml-auto text-right text-body-2">
				Showing {{showFirst}} - {{showLast}} of {{data.matches}} {{formatters.isNullOrEmpty(table.filter) ? 'rows' : 'matches'}}
			</div>
		</div>
		<v-card>
			<v-table class="data-table" fixed-header :height="tableHeight" density="compact">
				<thead>
					<tr class="bg-surface">
						<th v-if="!props.hideEdit" class="bg-secondary-tonal min"></th>
						<th v-for="header in table.headers" :key="header.key" :class="`${header.class} pointer bg-secondary-tonal`" @click="doSort(header.key)">
							{{ formatters.isNullOrEmpty(header.label) ? header.key : header.label }}
							<v-icon v-if="!header.noSort && table.sortBy[0] === header.key && table.sortBy[1] === 'asc'" class="fa-xs ms-2">fas fa-arrow-up</v-icon>
							<v-icon v-if="!header.noSort && table.sortBy[0] === header.key && table.sortBy[1] === 'desc'" class="fa-xs ms-2">fas fa-arrow-down</v-icon>
						</th>
						<th v-if="!props.hideDelete" class="bg-secondary-tonal min"></th>
					</tr>
				</thead>
				<tbody v-if="table.loading">
					<tr v-for="i in loaderArray" :key="i">
						<td v-if="!props.hideEdit" class="min"></td>
						<td v-for="header in table.headers" :key="header.key"><v-skeleton-loader type="text" max-width="150"></v-skeleton-loader></td>
						<td v-if="!props.hideDelete" class="min"></td>
					</tr>
				</tbody>
				<tbody v-else>
					<tr v-for="item in data.items">
						<td v-if="!props.hideEdit" class="min">
							<router-link :to="utilities.appendRoute(`edit/${item.id}`)" class="text-decoration-none text-primary" title="Edit/View">
								<font-awesome-icon :icon="['fas', 'edit']"></font-awesome-icon>
							</router-link>
						</td>
						<td v-for="header in table.headers" :key="header.key" :class="header.class">
							<div v-if="header.type === 'number'">
								{{ formatters.toNumberFormat(item[header.key], header.decimals||2, '', '-') }}
							</div>
							<div v-else-if="header.type === 'boolean'">
								{{ item[header.key] ? 'Y' : 'N' }}
							</div>
							<div v-else-if="header.type === 'object'">
								<span v-if="formatters.isNullOrEmpty(item[header.key])">-</span>
								<router-link v-else-if="!formatters.isNullOrEmpty(header.objectRoutePath)" class="text-primary text-decoration-none" 
									:to="`${header.objectRoutePath}${item[header.objectValueField||'id']}`">
									{{ item[header.key][header.objectTextField||'name'] }}
								</router-link>
								<span v-else>
									{{ item[header.key][header.objectTextField||'name'] }}
								</span>
							</div>
							<div v-else>
								{{ formatters.isNullOrEmpty(item[header.key]) ? '-' : item[header.key] }}
							</div>	
						</td>
						<td v-if="!props.hideDelete" class="min">
							<font-awesome-icon :icon="['fas', 'times']" class="text-error pointer" title="Delete"></font-awesome-icon>
						</td>
					</tr>
				</tbody>
			</v-table>
		</v-card>
		<action-bar v-if="!props.noActionBar" :full-width="props.fullWidthActionBar">
			<v-btn v-if="!props.hideCreate" variant="flat" color="primary" :to="utilities.appendRoute('create')">Create Record</v-btn>
			<v-pagination v-model="table.page" @update:modelValue="get(false)" :total-visible="6"
				:length="getNumPages()" class="ml-auto" size="small"></v-pagination>
		</action-bar>
	</project-container>
</template>