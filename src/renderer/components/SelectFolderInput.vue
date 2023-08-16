<script setup lang="ts">
	import { ref } from 'vue';

	const electron = window.electronApi;
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
		id: {
			type: String
		},
		hint: {
			type: String,
			required: false,
			default: 'Click the folder icon on the right to browse'
		},
		persistentHint: {
			type: Boolean,
			required: false
		}
	})

	let model = ref(props.value);
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

	function selectDirectory() {
		var files = electron.openFileDialog({properties: ['openDirectory']});
		if (files !== undefined) {
			model.value = files[0];
			emit('update:modelValue', model.value);
		}
	}
</script>

<template>
	<v-text-field :value="model" :label="props.label" :id="props.id" :rules="appliedRules" 
		:hint="props.hint" :persistent-hint="props.persistentHint"
		@click:append="selectDirectory" append-icon="fas fa-folder-open"
		@input="updateModelValue"
		@change="$emit('change', $event.target.value)"
		@focus="$emit('focus', $event.target.value)"
		@blur="$emit('blur', $event.target.value)"
		@keyup="$emit('keyup', $event.target.value)"></v-text-field>
</template>