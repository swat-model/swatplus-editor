<script setup lang="ts">
	import { reactive, computed } from 'vue';
	import { useVuelidate } from '@vuelidate/core';
	import { numeric, required } from '@vuelidate/validators';
	import { useRouter } from 'vue-router';
	import { useHelpers } from '@/helpers';

	const router = useRouter();
	const { api, currentProject, errors, formatters } = useHelpers();

	interface Props {
		item: any,
		isUpdate?: boolean
	}

	const props = withDefaults(defineProps<Props>(), {
		item: { id: 0 },
		isUpdate: false
	});

	let table:any = {
		apiUrl: 'regions/ls_units/elements',
		editPathPrefix: '/edit/regions/ls_units/elements/',
		headers: [
			{ key: 'name', label: 'Name' },
			{ key: 'obj_typ', label: 'Type' },
			{ key: 'obj_name', label: 'Object', type: 'variable-object' },
			{ key: 'bsn_frac', label: 'Basin Fraction', type: 'number', decimals: 6, class: 'text-right' },
			{ key: 'sub_frac', label: 'Subbasin Fraction', type: 'number', decimals: 6, class: 'text-right' },
			{ key: 'reg_frac', label: 'Region Fraction', type: 'number', decimals: 6, class: 'text-right' }
		]
	};

	let page:any = reactive({
		loading: true,
		error: <string|null>null,
		saving: false,
		saveSuccess: false,
		
	});

	const itemRules = computed(() => ({
		name: { required },
		area: { required, numeric }
	}))
	const v$ = useVuelidate(itemRules, props.item);

	function putDb(data:any) {
		if (props.isUpdate)
			return api.put(`regions/ls_units/${props.item.id}`, data, currentProject.getApiHeader());
		else
			return api.post(`regions/ls_units`, data, currentProject.getApiHeader());
	}

	async function save() {
		page.error = null;
		page.saving = true;
		page.saveSuccess = false;

		const valid = await v$.value.$validate();
		if (!valid) {
			page.error = 'Please fix the errors below and try again.';
		} else {
			let data = {
				name: formatters.toValidName(props.item.name),
				area: props.item.area
			};
			
			try {
				const response = await putDb(data);
				
				if (props.isUpdate)
					page.saveSuccess = true;
				else
					router.push({ name: 'LandscapeUnitsEdit', params: { id: response.data.id } });
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
		
		<v-form @submit.prevent="save">
			<v-row>
				<v-col>
					<div class="form-group">
						<v-text-field v-model="item.name" 
							label="Name" hint="Must be unique"
							:error-messages="v$.name.$errors.map(e => e.$message).join(', ')"
							@input="v$.name.$touch" @blur="v$.name.$touch"></v-text-field>
					</div>
				</v-col>
				<v-col>
					<div class="form-group">
						<v-text-field v-model.number="item.area" type="number" step="any"
							label="Area (ha)"
							:error-messages="v$.area.$errors.map(e => e.$message).join(', ')"
							@input="v$.area.$touch" @blur="v$.area.$touch"></v-text-field>
					</div>
				</v-col>
			</v-row>

			<div v-if="isUpdate">
				<h2 class="text-h5 my-3">Elements in this landscape unit</h2>
				<div v-if="!item.elements || item.elements.length < 1" class="alert alert-primary">
					This unit does not have any elements. 
				</div>
				<div v-else>
					<grid-view :api-url="table.apiUrl" :headers="table.headers" :edit-path-prefix="table.editPathPrefix"></grid-view>
				</div>
			</div>

			<action-bar>
				<v-btn type="submit" :loading="page.saving" variant="flat" color="primary" class="mr-2">
					Save Changes
				</v-btn>
				<v-btn type="button" variant="flat" color="info" class="mr-2"
					v-if="isUpdate" to="/edit/regions/ls_units/elements/create/">Add New Element</v-btn>
				<back-button></back-button>
			</action-bar>
		</v-form>
	</div>
</template>
