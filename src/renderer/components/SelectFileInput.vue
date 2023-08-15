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
		fileType: {
			type: String,
			required: true
		},
		saveDialog: {
			type: Boolean,
			default: false
		},
		defaultFileName: {
			type: String,
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

	function selectFile() {
		var filters;

		if (props.fileType == "json") {
			filters = [{ name: 'Json', extensions: ['json'] }];
		} else if (props.fileType == "sqlite") {
			filters = [{ name: 'SQLite', extensions: ['sqlite','db'] },{ name: 'All files', extensions: ['*'] }]
		} else if (props.fileType == "exe") {
			filters = [{ name: 'Executable', extensions: ['exe'] }];
		} else if (props.fileType == "csv") {
			filters = [{ name: 'CSV (Comma delimited)', extensions: ['csv'] }];
		} else if (props.fileType == "cli") {
			filters = [{ name: 'Cli/Text', extensions: ['txt','cli'] },{ name: 'All files', extensions: ['*'] }]
		} else {
			filters = [{ name: 'All files', extensions: ['*'] }]
		}

		var files;
		if (props.saveDialog) {
			files = electron.saveFileDialog({filters: filters, defaultPath: props.defaultFileName});
		} else {
			files = electron.openFileDialog({filters: filters});
		}
		console.log(files);

		if (files !== undefined) {
			model.value = files[0];
			emit('update:modelValue', model.value);
		}
	}
</script>

<template>
	<v-text-field :value="model" :label="props.label" :id="props.id" :rules="appliedRules" hint="Click the folder icon on the right to browse"
		@click:append="selectFile" append-icon="fas fa-folder-open"
		@input="updateModelValue"
		@change="$emit('change', $event.target.value)"
		@focus="$emit('focus', $event.target.value)"
		@blur="$emit('blur', $event.target.value)"
		@keyup="$emit('keyup', $event.target.value)"></v-text-field>
</template>