<script setup lang="ts">
	import { ref, watch } from 'vue';
	import { useFormatters } from '@/helpers/formatters';
	const formatters = useFormatters();

	interface Props {
		text: string | null,
		type?: "error" | "success" | "warning" | "info" | undefined,
		hideIcon?: boolean,
		variant?: "text" | "elevated" | "flat" | "tonal" | "outlined" | "plain" | undefined,
		border?: boolean | "top" | "bottom" | "start" | "end" | undefined,
		asPopup?: boolean,
		show?: boolean,
		timeout?: number,
		modelValue?: boolean
	}

	const props = withDefaults(defineProps<Props>(), {
		text: null,
		type: 'error',
		variant: 'tonal',
		hideIcon: false,
		border: 'start',
		asPopup: false,
		show: false,
		timeout: 3000,
		modelValue: false
	});

	const emit = defineEmits(['update:modelValue'])

	const showAlert = ref(props.modelValue);

	function closeAlert() {
		emit('update:modelValue', false);
		showAlert.value = false;
	}

	watch(() => props.modelValue, (newValue) => {
		showAlert.value = newValue;
	})

	watch(showAlert, (newValue) => {
		emit('update:modelValue', newValue);
	})
</script>

<template>
	<div>
		<v-alert v-if="!props.asPopup && !formatters.isNullOrEmpty(props.text)" 
			:type="props.type" :icon="hideIcon ? false : '$' + props.type" :variant="props.variant" :border="props.border"
			class="mb-4">
			{{ props.text }}
		</v-alert>
		<v-snackbar v-else v-model="showAlert" :timeout="props.timeout" location="top" :color="props.type">
			{{ props.text }}
			<template v-slot:actions>
				<v-btn variant="text" @click="closeAlert">Close</v-btn>
			</template>
		</v-snackbar>
	</div>
</template>