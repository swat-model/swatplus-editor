<script setup lang="ts">
	import { reactive, ref } from 'vue';
	import { useRouter } from 'vue-router';
	import { useHelpers } from '@/helpers';
	const router = useRouter();
	const { api, constants, currentProject, errors, formatters, utilities } = useHelpers();

	interface Props {
		apiUrl: string,
		item: any,
		isUpdate?: boolean
	}

	const props = withDefaults(defineProps<Props>(), {
		apiUrl: '',
		item: { id: 0 },
		isUpdate: false
	});

	const dataGrid = ref();

	let page:any = reactive({
		error: null,
		validated: false,
		saving: false,
		saveSuccess: false,
		redirectRoute: 'ConstituentsSaltsRecallEdit'
	});

	let data:any = reactive({
		recTypOptions: [
			{ value: 1, text: 'Daily' },
			{ value: 2, text: 'Monthly' },
			{ value: 3, text: 'Yearly' }
		],
		changedRecTyp: false,
		originalRecTyp: props.item?.props?.rec_typ,
		dataTotal: 0
	});

	function putPropsDb(data:any) {
		if (props.isUpdate)
			return api.put(`${props.apiUrl}/${props.item.id}`, data, currentProject.getApiHeader());
		else
			return api.post(`${props.apiUrl}`, data, currentProject.getApiHeader());
	}

	async function save() {
		page.error = null;
		page.saving = true;
		page.saveSuccess = false;
		page.validated = true;

		let name = formatters.toValidName(props.item.name);
		props.item.name = name;

		try {
			const response = await putPropsDb(props.item);
			page.validated = false;
			
			if (props.isUpdate) {
				page.saveSuccess = true;
				await dataGrid?.value?.get(false);
				data.changedRecTyp = false;
				data.originalRecTyp = props.item.rec_typ;
			} else
				router.push({ name: page.redirectRoute, params: { id: response.data.id } });
		} catch (error) {
			page.error = errors.logError(error, 'Unable to save changes to database.');
		}
		
		page.saving = false;
	}
	
	function getTableTotal(total:number) {
		data.dataTotal = total;
	}
</script>

<template>
	<div>
		<error-alert :text="page.error"></error-alert>
		<success-alert v-model="page.saveSuccess" :show="page.saveSuccess"></success-alert>

		<v-form @submit.prevent="save">
			<div>
				<div class="form-group">
					<v-text-field v-model="item.name" :rules="[constants.formRules.required, constants.formRules.nameLength]" 
						label="Name" hint="Must be unique"></v-text-field>
				</div>

				<div class="form-group">
					<v-select label="Time Step" v-model="item.rec_typ"
						:items="data.recTypOptions" item-title="text" item-value="value" 
						@update:model-value="data.changedRecTyp = true" :rules="[constants.formRules.required]"></v-select>
				</div>

				<v-alert type="info" variant="tonal" class="mb-4" v-if="isUpdate && data.changedRecTyp && data.dataTotal > 0">
					Warning: changing the time step will delete any existing data for the record. 
					Please export it first if you need to retain it. Click the save changes button before modifying any data below.
				</v-alert>

				<div v-if="isUpdate && item.id !== undefined">
					<grid-view ref="dataGrid" auto-height @change="getTableTotal"
						:api-url="`salts/recall-data-list/${item.id}`"
						delete-api-url="salts/recall-data"
						:default-sort="['yr','asc']"
						use-dynamic-headers :hide-fields="['id','recall_rec']"
						no-action-bar :hide-create="data.originalRecTyp === 4 && data.dataTotal > 0"
						:show-import-export="data.originalRecTyp !== 4" :default-csv-file="`salt_${item.name}.csv`" table-name="salt_rec_dat"
						:import-export-related-id="item.id" import-export-delete-existing></grid-view>
				</div>

				<action-bar>
					<v-btn type="submit" :loading="page.saving" variant="flat" color="primary" class="mr-2">Save Changes</v-btn>
					<back-button></back-button>
				</action-bar>
			</div>
		</v-form>
	</div>
</template>