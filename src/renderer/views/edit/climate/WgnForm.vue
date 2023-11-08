<script setup lang="ts">
	import { reactive, onMounted, computed, watch } from 'vue';
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
		error: null,
		saving: false,
		saveSuccess: false
	});

	function putDb(data:any) {
		if (props.isUpdate)
			return api.put(`climate/wgn/${props.item.id}`, data, currentProject.getApiHeader());
		else
			return api.post(`climate/wgn`, data, currentProject.getApiHeader());
	}

	async function save() {
		page.error = null;
		page.saving = true;
		page.saveSuccess = false;

		let data = {
			name: formatters.toValidName(props.item.name),
			lat: props.item.lat,
			lon: props.item.lon,
			elev: props.item.elev,
			rain_yrs: props.item.rain_yrs
		};
		
		try {
			await putDb(data);
			
			if (props.isUpdate)
				page.saveSuccess = true;
			else
				router.push({ name: 'Wgn'});
		} catch (error) {
			page.error = errors.logError(error, 'Unable to save changes to database.');
		}

		page.saving = false;
	}
</script>

<template>
	<div>
		<error-alert :text="page.error"></error-alert>
		<success-alert v-model="page.saveSuccess" :show="page.saveSuccess"></success-alert>

		<v-form @submit.prevent="save">
			<div class="form-group">
				<v-text-field v-model="item.name" :rules="[constants.formRules.required, constants.formRules.nameLength]" 
					label="Name" hint="Must be unique"></v-text-field>
			</div>

			<v-row>
				<v-col cols="12" md="6">
					<div class="form-group mb-0">
						<v-text-field v-model="item.lat" :rules="[constants.formRules.required]" 
							label="Latitude" type="number" step="any"></v-text-field>
					</div>
				</v-col>
				<v-col cols="12" md="6">
					<div class="form-group mb-0">
						<v-text-field v-model="item.lon" :rules="[constants.formRules.required]" 
							label="Longitude" type="number" step="any"></v-text-field>
					</div>
				</v-col>
			</v-row>

			<v-row>
				<v-col cols="12" md="6">
					<div class="form-group mb-0">
						<v-text-field v-model="item.elev" :rules="[constants.formRules.required]" 
							label="Elevation (m)" type="number" step="any"></v-text-field>
					</div>
				</v-col>
				<v-col cols="12" md="6">
					<div class="form-group mb-0">
						<v-text-field v-model="item.rain_yrs" :rules="[constants.formRules.required]" 
							label="Years of recorded max monthly 0.5h rainfall data" type="number" step="any"></v-text-field>
					</div>
				</v-col>
			</v-row>

			<action-bar>
				<v-btn type="submit" :loading="page.saving" variant="flat" color="primary" class="mr-2">
					Save Changes
				</v-btn>
				<back-button></back-button>
			</action-bar>
		</v-form>		
	</div>
</template>