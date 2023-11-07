<script setup lang="ts">
	import { reactive, onMounted, computed, watch } from 'vue';
	import { useHelpers } from '@/helpers';
	const { api, currentProject, errors, formatters } = useHelpers();

	interface Props {
		table: string,
		name: string,
		isHru?: boolean,
		noGis?: boolean
	}

	const props = withDefaults(defineProps<Props>(), {
		table: '',
		name: '',
		isHru: false,
		noGis: false
	});

	let page:any = reactive({
		error: null,
		loading: {
			subbasins: false,
			landuse: false,
			soils: false,
			objects: false
		}
	});

	let options:any = reactive({
		subbasins: [],
		landuse: [],
		soils: [],
		objects: []
	});

	let selection:any = reactive({
		subbasins: [],
		landuse: [],
		soils: [],
		objects: [],
		all: {
			subbasins: false,
			landuse: false,
			soils: false,
			objects: false
		}
	});

	async function get() {
		if (!props.noGis) page.loading.subbasins = true;
		page.error = null;

		try {
			if (props.noGis) {
				await getObjects();
			} else {
				const response = await api.get(`auto_complete/subbasins`, currentProject.getApiHeader());
				errors.log(response.data);
				options.subbasins = response.data;

				if (options.subbasins.length < 1) await getObjects();
			}
		} catch (error) {
			page.error = errors.logError(error, 'Unable to get objects from database.');
		}

		page.loading.subbasins = false;
	}

	async function getLanduse() {
		page.error = null;
		page.loading.landuse = true;
		options.landuse = [];
		selection.landuse = [];
		options.soils = [];
		selection.soils = [];
		options.objects = [];
		selection.objects = [];

		try {
			let data = {
				selected_subs: selection.subbasins
			};
			const response = await api.post(`auto_complete/landuse`, data, currentProject.getApiHeader());
			options.landuse = response.data;
		} catch (error) {
			page.error = errors.logError(error, 'Unable to get subbasins from database.');
		}

		page.loading.landuse = false;
	}

	async function getSoils() {
		page.error = null;
		page.loading.soils = true;
		options.soils = [];
		selection.soils = [];
		options.objects = [];
		selection.objects = [];

		try {
			let data = {
				selected_subs: selection.subbasins,
				selected_landuse: selection.landuse
			};
			const response = await api.post(`auto_complete/soils`, data, currentProject.getApiHeader());
			options.soils = response.data;
		} catch (error) {
			page.error = errors.logError(error, 'Unable to get subbasins from database.');
		}

		page.loading.soils = false;
	}

	async function getObjects() {
		page.error = null;
		page.loading.objects = true;
		options.objects = [];
		selection.objects = [];

		try {
			let data = {
				selected_subs: selection.subbasins,
				selected_landuse: selection.landuse,
				selected_soils: selection.soils
			};
			errors.log(data);
			const response = await api.post(`auto_complete/objects/${props.table}`, data, currentProject.getApiHeader());
			options.objects = response.data;
		} catch (error) {
			page.error = errors.logError(error, 'Unable to get subbasins from database.');
		}

		page.loading.objects = false;
	}

	function toggleAllSubbasins() {
		selection.subbasins = selection.all.subbasins ? options.subbasins.map(function (i:any) { return i.value }) : [];
	}
	function toggleAllLanduse() {
		selection.landuse = selection.all.landuse ? options.landuse.map(function (i:any) { return i.value }) : [];
	}
	function toggleAllSoils() {
		selection.soils = selection.all.soils ? options.soils.map(function (i:any) { return i.value }) : [];
	}
	function toggleAllObjects() {
		selection.objects = selection.all.objects ? options.objects.map(function (i:any) { return i.value }) : [];
	}

	const selectedSubbasins = computed(() => { return selection.subbasins; });
	const selectedLanduse = computed(() => { return selection.landuse; });
	const selectedSoils = computed(() => { return selection.soils; });
	const selectedObjects = computed(() => { return selection.objects; });
	const isHru = computed(() => { return props.isHru; });

	const emit = defineEmits(['change'])

	watch(selectedSubbasins, async () => {
		if (selection.subbasins.length > 0) {
			if (props.isHru) await getLanduse();
			else {
				await getObjects();
				selection.all.objects = true;
				toggleAllObjects();
			}
		} else {
			options.objects = [];
			selection.objects = [];
		}
	})

	watch(selectedLanduse, async () => {
		if (selection.landuse.length > 0)
			await getSoils();
	})

	watch(selectedSoils, async () => {
		if (selection.soils.length > 0) {
			await getObjects();
			selection.all.objects = true;
			toggleAllObjects();
		}
	})

	watch(selectedObjects, async () => {
		emit('change', selection.objects);
	})

	watch(isHru, () => {
		options.objects = [];
		selection.objects = [];
		selection.subbasins = [];
	})

	onMounted(async () => await get());
</script>

<template>
	<div>
		<v-alert type="info" variant="tonal">
			You are in bulk edit mode. Select the objects you want to edit then check the fields to which you 
			want to apply to the selected.
		</v-alert>

		<error-alert :text="page.error"></error-alert>
		<div class="d-flex mt-4 mb-6">
			<div>
				<page-loading :loading="page.loading.subbasins"></page-loading>
				<div v-if="!page.loading.subbasins && options.subbasins.length > 0" class="scroll-check mb-4">
					<div class="check-all">
						<v-checkbox v-model="selection.all.subbasins" @change="toggleAllSubbasins" class="d-inline" hide-details>
							<template #label>
								Select Subbasins
								<v-tooltip :text="`Filter ${name.toLowerCase()} by subbasin.`">
									<template v-slot:activator="{ props }">
										<font-awesome-icon v-bind="props" :icon="['fas', 'question-circle']" class="text-info pointer ml-1"></font-awesome-icon>
									</template>
								</v-tooltip>
							</template>
						</v-checkbox>
						
					</div>
					<div class="items">
						<div class="item" v-for="o in options.subbasins" :key="o.value">
							<v-checkbox v-model="selection.subbasins" :value="o.value" :label="o.text" hide-details></v-checkbox>
						</div>
					</div>
				</div>
			</div>
			<div v-if="isHru && !page.loading.subbasins">
				<page-loading :loading="page.loading.landuse"></page-loading>
				<div v-if="!page.loading.landuse && options.landuse.length > 0" class="scroll-check mb-4 ml-3">
					<div class="check-all">
						<v-checkbox v-model="selection.all.landuse" @change="toggleAllLanduse" class="d-inline" label="Select Land Use" hide-details></v-checkbox>
					</div>
					<div class="items">
						<div class="item" v-for="o in options.landuse" :key="o.value">
							<v-checkbox v-model="selection.landuse" :value="o.value" :label="o.text" hide-details></v-checkbox>
						</div>
					</div>
				</div>
			</div>
			<div v-if="isHru && !page.loading.subbasins && !page.loading.landuse">
				<page-loading :loading="page.loading.soils"></page-loading>
				<div v-if="!page.loading.soils && options.landuse.length > 0 && options.soils.length > 0" class="scroll-check mb-4 ml-3">
					<div class="check-all">
						<v-checkbox v-model="selection.all.soils" @change="toggleAllSoils" class="d-inline" label="Select Soils" hide-details></v-checkbox>
					</div>
					<div class="items">
						<div class="item" v-for="o in options.soils" :key="o.value">
							<v-checkbox v-model="selection.soils" :value="o.value" :label="o.text" hide-details></v-checkbox>
						</div>
					</div>
				</div>
			</div>
			<div v-if="!page.loading.subbasins && !page.loading.landuse && !page.loading.soils">
				<page-loading :loading="page.loading.objects"></page-loading>
				<div v-if="!page.loading.objects && options.objects.length > 0 && (noGis || !isHru || (options.landuse.length > 0 && options.soils.length > 0))" 
					:class="noGis || options.subbasins.length < 1 ? 'scroll-check mb-4' : 'scroll-check mb-4 ml-3'">
					<div class="check-all">
						<v-checkbox v-model="selection.all.objects" @change="toggleAllObjects" class="d-inline" hide-details>
							<template #label>
								Select {{ name }}
								<v-tooltip :text="`${name} in this list are based on your ${isHru ? 'subbasin/landuse/soil' : 'subbasin'} selections. Check the ${name.toLowerCase()} to which to apply your changes.`">
								<template v-slot:activator="{ props }">
									<font-awesome-icon v-bind="props" v-if="options.subbasins.length > 0" :icon="['fas', 'question-circle']" class="text-info pointer ml-1"></font-awesome-icon>
								</template>
							</v-tooltip>
							</template>
						</v-checkbox>
						
					</div>
					<div class="items">
						<div class="item" v-for="o in options.objects" :key="o.value">
							<v-checkbox v-model="selection.objects" :value="o.value" :label="o.text" hide-details></v-checkbox>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>
</template>