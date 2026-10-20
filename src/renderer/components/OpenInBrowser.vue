<script setup lang="ts">
const electron = window.electronApi;
interface Props {
	url: string;
	class?: string;
	text?: string;
	button?: boolean;
	color?: string;
	variant?: "text" | "elevated" | "flat" | "tonal" | "outlined" | "plain" | undefined;
}

const props = defineProps<Props>();

function open(e: any) {
	e.preventDefault();
	electron.openUrl(props.url);
}
</script>

<template>
	<v-btn v-if="props.button" @click="open" :title="props.url" :color="props.color" :variant="props.variant">{{ props.text }}</v-btn>
	<a v-else :href="props.url" @click="open" :class="props.class" :title="props.url">{{ props.text }}</a>
</template>
