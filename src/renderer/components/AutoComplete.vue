<script setup lang="ts">
	import { ref, reactive, watch, onMounted } from 'vue';
	import { useRouter } from 'vue-router';
	// @ts-ignore
	import _ from 'underscore';
	import { useHelpers } from '@/helpers';
	const { api, constants, currentProject, errors, formatters, utilities } = useHelpers();
	const router = useRouter();

	interface Props {
		value?: string,
		label?: string,
		required?: boolean,
		invalidFeedback?: string,
		hint?: string,
		persistentHint?: boolean,
		tableName?: string,
		routeName?: string,
		apiUrl?: string,
		section?: string,
		helpFile?: string,
		helpDb?: string,
		showItemLink?: boolean,
		customSearchUrl?: string,
		hideDetails?: boolean,
		disabled?: boolean,
		noRouteId?: boolean
	}

	const props = withDefaults(defineProps<Props>(), {
		value: '',
		label: '',
		required: false,
		invalidFeedback: 'Required',
		hint: '',
		persistentHint: false,
		tableName: '',
		routeName: '',
		apiUrl: '',
		section: '',
		helpFile: '',
		helpDb: '',
		showItemLink: false,
		customSearchUrl: '',
		hideDetails: false,
		disabled: false,
		noRouteId: false
	});

	let model = ref(props.value);

	let data:any = reactive({
		loading: false,
		items: [],
		search: null
	})

	let rules = {
		required: (value:string) => !!value || props.invalidFeedback
	}

	let appliedRules = props.required ? [rules.required] : [];

	const emit = defineEmits(['update:modelValue'])

	async function get() {
		data.loading = true;
		let query;
		if (!formatters.isNullOrEmpty(props.customSearchUrl)) {
			if (formatters.isNullOrEmpty(data.search)) {
				data.loading = false;
				return;
			}

			query = api.get(`${props.customSearchUrl}/${data.search}`, currentProject.getApiHeader());
		} else {
			query = utilities.getAutoComplete(props.tableName, data.search);
		}
		const response = await query;
		errors.log(response.data);
		data.items = response.data;
		data.loading = false;
	}

	async function goToProp() {
		let name = model.value;
		if (!formatters.isNullOrEmpty(name)) {
			try {
				const response = await utilities.getAutoCompleteId(props.tableName, name);
				var id = response.data.id;
				
				if (props.noRouteId)
					router.push({ name: props.routeName });
				else
					router.push({ name: props.routeName, params: { id: id }});
			} catch (error) {
				errors.logError(error, `Cannot find ${name} in database table ${props.tableName}.`);
			}
		}
	}

	watch(
		() => data.search,
		async () => {
			_.debounce(await get(), 500);
		}
	)

	watch(
		() => props.apiUrl,
		async () => {
			_.debounce(await get(), 500);
		}
	)

	watch(model, (newModel) => {
		emit('update:modelValue', newModel);
	})

	//onMounted(async () => await get())
</script>

<template>
	<div>
		<v-autocomplete v-model="model" :label="props.label" :rules="appliedRules" :hide-details="props.hideDetails" :readonly="props.disabled"
			:hint="props.hint" :persistent-hint="props.persistentHint" :no-data-text="data.loading ? 'Loading...' : 'No data available'"
			:loading="data.loading" v-model:search.sync="data.search" :items="data.items" auto-select-first>
			<template v-slot:append>
				<v-menu open-on-hover v-if="!formatters.isNullOrEmpty(props.section)">
					<template v-slot:activator="{ props }">
						<v-btn v-bind="props" icon="fas fa-database" variant="text"></v-btn>
					</template>

					<v-card>
						<v-card-text>
							This field references a row in the <mark>{{ props.section }}</mark> section.
						</v-card-text>
						<v-divider></v-divider>
						<v-card-text>
							<div>Input file: <code class="font-weight-bold">{{ props.helpFile }}</code></div>
							<div>Database table: <code class="font-weight-bold">{{ props.helpDb }}</code></div>
						</v-card-text>
						<v-card-actions>
							<v-btn v-if="!formatters.isNullOrEmpty(props.apiUrl)" 
								color="primary"
								:href="`/#/table-browser?apiUrl=${props.apiUrl}&section=${props.section}&projectDb=${currentProject.projectDbUrl}`" target="_blank">
								Browse Table
								<font-awesome-icon :icon="['fas', 'up-right-from-square']" class="ml-1"></font-awesome-icon>
							</v-btn>
							<v-btn v-if="props.showItemLink" :disabled="formatters.isNullOrEmpty(model)" @click="goToProp">Edit Item</v-btn>
						</v-card-actions>
					</v-card>
				</v-menu>
			</template>
		</v-autocomplete>
	</div>
</template>