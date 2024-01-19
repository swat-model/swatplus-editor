<script setup lang="ts">
	import { reactive, onMounted, watch, computed } from 'vue';
	import { useHelpers } from '@/helpers';
	const { api, constants, currentProject, errors, formatters, utilities } = useHelpers();

	interface Props {
		value: any,
		required?: boolean,
		varDef: any,
		id: string,
		showRange?: boolean,
		datasetValue?: any,
		showDatasets?: boolean,
		bulkMode?: boolean,
	}

	const props = withDefaults(defineProps<Props>(), {
		value: {},
		required: false,
		varDef: {},
		id: '',
		showRange: false,
		datasetValue: {},
		showDatasets: false,
		bulkMode: false,
	});

	const data:any = reactive({
		model: props.value,
		lookupOptions: [],
		lookupError: null,
		boolOptions: [
			{ value: true, text: "Yes" },
			{ value: false, text: "No"}
		],
		varSelected: false,
		rules: props.required ? [constants.formRules.required] : []
	})

	const emit = defineEmits(['update:modelValue', 'change'])

	watch(() => data.model, (newModel) => {
		emit('update:modelValue', newModel);
	})

	watch(() => data.varSelected, (value) => {
		let data = {
			name: props.varDef.name,
			value: value
		};
		emit('change', data);
	})

	async function get() {
		if (props.varDef.type === 'lookup') {
			try {
				const response = await api.get(`auto_complete/select-list/${props.varDef.default_text}/id`, currentProject.getApiHeader());

				data.lookupOptions = response.data;
				errors.log(response.data);
			} catch (error) {
				data.lookupError = errors.logError(error, `Unable to get ${props.varDef.default_text} options from database.`);
			}
		}
	}

	function writeUnits(value:any) {
		if (!formatters.isNullOrEmpty(value) && value.includes("^")) {
			return value.replace(/\^\{(.*?)\}/g, "<sup>$1</sup>");
		}

		return value;
	}

	function writeDefault(value:any) {
		if (value.type == 'lookup')
			return '';
		else if (value.default_text)
			return value.default_text;
		else
			return value.default_value;
	}

	const inputDisabled = computed(() => {
		return props.bulkMode && !data.varSelected;
	})

	onMounted(async () => await get())
</script>

<template>
	<tr>
		<td v-if="bulkMode" class="text-center min">
			<v-checkbox v-model="data.varSelected" hide-details></v-checkbox>
		</td>
		<td v-if="showDatasets" :class="(datasetValue === value || (props.varDef.type === 'lookup' && props.datasetValue?.name === props.value?.name) ? 'text-info' : 'text-warning') + ' text-right min'">
			{{ props.varDef.type === 'lookup' ? props.datasetValue?.name : datasetValue }}
		</td>
		<td class="field">
			<v-text-field density="compact" v-if="props.varDef.type === 'float'" :rules="data.rules" 
				v-model.number="data.model" type="number" step="any" :disabled="inputDisabled" hide-details="auto">
				<template v-slot:append-inner v-if="props.varDef.units && props.varDef.units.length < 10"><div v-html="writeUnits(props.varDef.units)"></div></template>
			</v-text-field>

			<v-text-field density="compact" v-else-if="props.varDef.type === 'int'" :rules="data.rules" :id="id" 
				v-model.number="data.model" type="number" :disabled="inputDisabled" hide-details="auto">
				<template v-slot:append-inner v-if="props.varDef.units && props.varDef.units.length < 10"><div v-html="writeUnits(props.varDef.units)"></div></template>
			</v-text-field>

			<v-select density="compact" v-else-if="props.varDef.type === 'select'" :rules="data.rules" v-model="data.model" :items="props.varDef.options" item-title="text" item-value="value" :disabled="inputDisabled" hide-details="auto"></v-select>
			<v-select density="compact" v-else-if="props.varDef.type === 'lookup'" :rules="data.rules" v-model="data.model.id" :items="data.lookupOptions" item-title="text" item-value="value" :disabled="inputDisabled" hide-details="auto"></v-select>
			<v-select density="compact" v-else-if="props.varDef.type === 'bool'" :rules="data.rules" v-model="data.model" :items="data.boolOptions" item-title="text" item-value="value" :disabled="inputDisabled" hide-details="auto"></v-select>
			
			<v-text-field density="compact" v-else 
				v-model="data.model" type="text" class="form-control" :disabled="inputDisabled" hide-details="auto" :rules="data.rules">
				<template v-slot:append-inner v-if="props.varDef.units && props.varDef.units.length < 10"><div v-html="writeUnits(props.varDef.units)"></div></template>
			</v-text-field>
		</td>
		<td>
			{{ props.varDef.description }}
			<div v-if="props.varDef.units && props.varDef.units.length >= 10" v-html="writeUnits(props.varDef.units)" class="text-body-2 text-medium-emphasis"></div>
		</td>
		<td><code>{{ props.varDef.name }}</code></td>
		<td v-if="!showDatasets">{{ writeDefault(props.varDef) }}</td>
		<td v-if="props.showRange">
			<span v-if="props.varDef.min_value != props.varDef.max_value">
				{{ props.varDef.min_value }} - {{ props.varDef.max_value }}
			</span>
		</td>
	</tr>
</template>