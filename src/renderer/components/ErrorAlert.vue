<script setup lang="ts">
	import { useFormatters } from '../plugins/formatters';
	const formatters = useFormatters();

	interface Props {
		text: string | null,
		type?: "error" | "success" | "warning" | "info" | undefined,
		hideIcon?: boolean,
		variant?: "text" | "elevated" | "flat" | "tonal" | "outlined" | "plain" | undefined,
		border?: boolean | "top" | "bottom" | "start" | "end" | undefined
	}

	const props = withDefaults(defineProps<Props>(), {
		text: null,
		type: 'error',
		variant: 'tonal',
		hideIcon: false,
		border: 'start'
	});
</script>

<template>
	<v-alert v-if="!formatters.isNullOrEmpty(props.text)" 
		:type="props.type" :icon="hideIcon ? false : '$' + props.type" :variant="props.variant" :border="props.border"
		class="mb-4">
		{{ props.text }}
	</v-alert>
</template>