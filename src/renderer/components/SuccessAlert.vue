<script setup lang="ts">
	import { ref, watch } from 'vue';
	import { useFormatters } from '@/helpers/formatters';
	const formatters = useFormatters();

	interface Props {
		text?: string | null,
		type?: "error" | "success" | "warning" | "info" | undefined,
		hideIcon?: boolean,
		variant?: "text" | "elevated" | "flat" | "tonal" | "outlined" | "plain" | undefined,
		border?: boolean | "top" | "bottom" | "start" | "end" | undefined,
		noPopup?: boolean,
		show?: boolean,
		timeout?: number
	}

	const props = withDefaults(defineProps<Props>(), {
		text: 'Changes saved.',
		type: 'success',
		variant: undefined,
		hideIcon: false,
		border: 'start',
		noPopup: false,
		show: false,
		timeout: 3000
	});

	const showAlert = ref(props.show);

	watch(() => props.show, (newValue) => {
		showAlert.value = newValue;
	})
</script>

<template>
	<div>
		<v-alert v-if="props.noPopup && !formatters.isNullOrEmpty(props.text)" 
			:type="props.type" :icon="hideIcon ? false : '$' + props.type" :variant="props.variant" :border="props.border"
			class="mb-4">
			{{ props.text }}
		</v-alert>
		<v-snackbar v-else v-model="showAlert" :timeout="props.timeout" location="top" :color="props.type">
			{{ props.text }}
			<template v-slot:actions>
				<v-btn variant="text" @click="showAlert = false">Close</v-btn>
			</template>
		</v-snackbar>
	</div>
</template>