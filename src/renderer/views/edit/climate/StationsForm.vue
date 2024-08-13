<script setup lang="ts">
	import { reactive, computed, onMounted } from 'vue';
	import { useVuelidate } from '@vuelidate/core';
	import { decimal, required, maxLength } from '@vuelidate/validators';
	import { useRouter } from 'vue-router';
	import { useHelpers } from '@/helpers';

	const router = useRouter();
	const { api, constants, currentProject, errors, formatters, utilities } = useHelpers();

	interface Props {
		item: any,
		isUpdate?: boolean
	}

	const props = withDefaults(defineProps<Props>(), {
		item: { id: 0 },
		isUpdate: false
	});

	let page:any = reactive({
		loading: true,
		error: <string|null>null,
		saving: false,
		saveSuccess: false,
		form: {
			isSim: {
				pcp: true,
				tmp: true,
				slr: true,
				hmd: true,
				wnd: true
			},
			obsNote: 'If the observed file is left blank, simulated is used by default'
		}
	});

	const itemRules = computed(() => ({
		name: { required },
		lat: { required, decimal },
		lon: { required, decimal },
		wgn_name: {},
		pcp: {},
		tmp: {},
		slr: {},
		hmd: {},
		wnd: {},
		pet: {},
		atmo_dep: {}
	}))
	const v$ = useVuelidate(itemRules, props.item);

	onMounted(() => {
		get();
	});

	function get() {
		if (props.isUpdate) {
			page.form.isSim = {
				pcp: isSim(props.item.pcp),
				tmp: isSim(props.item.tmp),
				slr: isSim(props.item.slr),
				hmd: isSim(props.item.hmd),
				wnd: isSim(props.item.wnd)
			};
		}
	}

	function isSim(value:any) {
		if (value == 'sim' || value == '' || value == null || value == undefined)
			return true;

		return false;
	}

	function checkSim() {
		if (page.form.isSim.pcp) props.item.pcp = null;
		if (page.form.isSim.tmp) props.item.tmp = null;
		if (page.form.isSim.slr) props.item.slr = null;
		if (page.form.isSim.hmd) props.item.hmd = null;
		if (page.form.isSim.wnd) props.item.wnd = null;
	}

	function putDb(data:any) {
		if (props.isUpdate)
			return api.put(`climate/stations/${props.item.id}`, data, currentProject.getApiHeader());
		else
			return api.post(`climate/stations`, data, currentProject.getApiHeader());
	}

	function getFilesUrl(type:string) {
		return `climate/files/${type}`;
	}

	async function save() {
		page.error = null;
		page.saving = true;
		page.saveSuccess = false;

		const valid = await v$.value.$validate();
		if (formatters.isNullOrEmpty(props.item.wgn_name)) {
			page.error = 'Please select a weather generator and try again.';
		} else if (!valid) {
			page.error = 'Please fix the errors below and try again.';
		} else {
			let data = props.item;
			data.name = formatters.toValidName(data.name);
			
			try {
				const response = await putDb(data);
				
				if (props.isUpdate)
					page.saveSuccess = true;
				else
					router.push({ name: 'StationsEdit', params: { id: response.data.id } });
			} catch (error) {
				page.error = errors.logError(error, 'Unable to save changes to database.');
			}
		}

		page.saving = false;
	}
</script>

<template>
	<div>
		<error-alert :text="page.error"></error-alert>
		<success-alert v-model="page.saveSuccess" :show="page.saveSuccess"></success-alert>

		<v-alert type="info" icon="$info" variant="tonal" border="start" class="mb-4">
			When creating a weather station manually, it does not automatically get assigned to your spatial objects.
			You will need to edit each spatial object and assign it this weather station in order to use it.
			To automatically assign weather stations, use the import function for weather generators or observed weather data.
		</v-alert>

		<v-form @submit.prevent="save">
			<div class="form-group">
				<v-text-field v-model="item.name" 
					label="Name" hint="Must be unique"
					:error-messages="v$.name.$errors.map(e => e.$message).join(', ')"
					@input="v$.name.$touch" @blur="v$.name.$touch"></v-text-field>
			</div>

			<div class="form-group">
				<auto-complete label="Weather generator"
					v-model="item.wgn_name" :value="item.wgn_name" :show-item-link="props.isUpdate" required
					table-name="wgn" route-name="WgnEdit"
					section="Climate / Weather Generator" help-file="weather-wgn.cli" help-db="weather_wgn_cli"
					api-url="climate/wgn"></auto-complete>
			</div>

			<v-row>
				<v-col cols="12" md="6">
					<div class="form-group mb-0">
						<v-text-field v-model.number="item.lat" 
							label="Latitude" type="number" step="any"
							:error-messages="v$.lat.$errors.map(e => e.$message).join(', ')"
							@input="v$.lat.$touch" @blur="v$.lat.$touch"></v-text-field>
					</div>
				</v-col>
				<v-col cols="12" md="6">
					<div class="form-group mb-0">
						<v-text-field v-model.number="item.lon" 
							label="Longitude" type="number" step="any"
							:error-messages="v$.lon.$errors.map(e => e.$message).join(', ')"
							@input="v$.lon.$touch" @blur="v$.lon.$touch"></v-text-field>
					</div>
				</v-col>
			</v-row>

			<v-alert type="info" icon="$info" variant="tonal" border="start" class="mb-4">
				Important: when entering an observed weather file name below, you may start typing to search for existing weather files adding during the import step.
				If adding observed files manually, just type the name of the file (e.g., p326953.pcp), and put that file in the directory you plan to write input files (e.g., your TxtInOut).
				Files must be in SWAT+ format. If your weather data is in SWAT2012 format or from the Global Weather CFSR website, please use the import step to convert them to SWAT+.
			</v-alert>

			<v-table class="table-editor" density="compact">
				<thead>
					<tr class="bg-surface">
						<th class="bg-secondary-tonal"></th>
						<th class="bg-secondary-tonal text-center min">Simulated</th>
						<th class="bg-secondary-tonal">Observed data file name</th>
					</tr>
				</thead>
				<tbody>
					<tr>
						<th>Precipitation</th>
						<td class="text-center"><v-checkbox v-model="page.form.isSim.pcp" @update:model-value="checkSim" hide-details></v-checkbox></td>
						<td><auto-complete v-if="!page.form.isSim.pcp" v-model="item.pcp" :value="item.pcp" :custom-search-url="getFilesUrl('pcp')" hide-details></auto-complete></td>
					</tr>
					<tr>
						<th>Temperature</th>
						<td class="text-center"><v-checkbox v-model="page.form.isSim.tmp" @update:model-value="checkSim" hide-details></v-checkbox></td>
						<td><auto-complete v-if="!page.form.isSim.tmp" v-model="item.tmp" :value="item.tmp" :custom-search-url="getFilesUrl('tmp')" hide-details></auto-complete></td>
					</tr>
					<tr>
						<th>Solar radiation</th>
						<td class="text-center"><v-checkbox v-model="page.form.isSim.slr" @update:model-value="checkSim" hide-details></v-checkbox></td>
						<td><auto-complete v-if="!page.form.isSim.slr" v-model="item.slr" :value="item.slr" :custom-search-url="getFilesUrl('slr')" hide-details></auto-complete></td>
					</tr>
					<tr>
						<th>Relative humidity</th>
						<td class="text-center"><v-checkbox v-model="page.form.isSim.hmd" @update:model-value="checkSim" hide-details></v-checkbox></td>
						<td><auto-complete v-if="!page.form.isSim.hmd" v-model="item.hmd" :value="item.hmd" :custom-search-url="getFilesUrl('hmd')" hide-details></auto-complete></td>
					</tr>
					<tr>
						<th>Wind speed</th>
						<td class="text-center"><v-checkbox v-model="page.form.isSim.wnd" @update:model-value="checkSim" hide-details></v-checkbox></td>
						<td><auto-complete v-if="!page.form.isSim.wnd" v-model="item.wnd" :value="item.wnd" :custom-search-url="getFilesUrl('wnd')" hide-details></auto-complete></td>
					</tr>
					<tr>
						<th>Potential evapotranspiration</th>
						<td class="text-center"></td>
						<td><auto-complete v-model="item.pet" :value="item.pet" :custom-search-url="getFilesUrl('pet')" hide-details></auto-complete></td>
					</tr>
					<tr>
						<th class="min">Atmospheric deposition</th>
						<td class="text-center"></td>
						<td>
							<auto-complete :show-item-link="props.isUpdate" hide-details
								v-model="item.atmo_dep"
								:value="item.atmo_dep"
								table-name="atmo_sta" route-name="StationsAtmoEdit"
								section="Climate / Weather Stations / Atmospheric Deposition" help-file="atmo.cli" help-db="atmo_cli"
								api-url="climate/atmo/stations"></auto-complete>
						</td>
					</tr>
				</tbody>
			</v-table>

			<action-bar>
				<v-btn type="submit" :loading="page.saving" variant="flat" color="primary" class="mr-2">
					Save Changes
				</v-btn>
				<back-button></back-button>
			</action-bar>
		</v-form>
	</div>
</template>