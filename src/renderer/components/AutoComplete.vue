<script setup lang="ts">
	import { ref, reactive, watch, onMounted } from 'vue';
	import { useRouter } from 'vue-router';
	// @ts-ignore
	import _ from 'underscore';
	import { usePlugins } from '../plugins';
	const { api, constants, currentProject, errors, formatters, utilities } = usePlugins();
	const router = useRouter();

	const props = defineProps({
		value: {
			type: String,
			required: false,
			default: ''
		},
		label: {
			type: String,
			required: false,
			default: ''
		},
		required: {
			type: Boolean,
			required: false
		},
		invalidFeedback: {
			type: String,
			required: false,
			default: 'Required'
		},
		hint: {
			type: String,
			required: false,
			default: ''
		},
		persistentHint: {
			type: Boolean,
			required: false
		},
		tableName: {
			type: String,
			required: true
		},
		routeName: {
			type: String,
			required: true
		},
		apiUrl: {
			type: String,
			required: false
		},
		section: {
			type: String,
			required: false,
			default: ''
		},
		helpFile: {
			type: String,
			required: false,
			default: ''
		},
		helpDb: {
			type: String,
			required: false,
			default: ''
		},
		showItemLink: {
			type: Boolean,
			default: false
		}
	})

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

	const emit = defineEmits([
		'update:modelValue',
		'change',
		'blur',
		'focus',
		'keyup',
	])

	function updateModelValue($event:any) {
		model.value = $event.target.value;
    	emit('update:modelValue', $event.target.value);
	}

	async function get() {
		data.loading = true;
		const response = await utilities.getAutoComplete(props.tableName, data.search);
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

	onMounted(async () => await get())
</script>

<template>
	<div>
		<v-autocomplete v-model="model" :value="model" :label="props.label" :rules="appliedRules"
			:hint="props.hint" :persistent-hint="props.persistentHint"
			:loading="data.loading" v-model:search="data.search" :items="data.items" auto-select-first
			@input="updateModelValue"
			@change="$emit('change', $event.target.value)"
			@focus="$emit('focus', $event.target.value)"
			@blur="$emit('blur', $event.target.value)"
			@keyup="$emit('keyup', $event.target.value)">
			<template v-slot:append>
				<v-menu open-on-hover>
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
								:href="`/table-browser?apiUrl=${props.apiUrl}&section=${props.section}&projectDb=${currentProject.projectDbUrl}`" target="_blank">
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