<script setup lang="ts">
	const electron = window.electronApi;
	interface Props {
		url: string,
		class?: string,
		text: string,
		button: boolean,
		color?: string,
		variant?: "text" | "elevated" | "flat" | "tonal" | "outlined" | "plain" | undefined
	}

	const props = defineProps<Props>();

	function open(e:any) {
		e.preventDefault();
		electron.openUrl(props.url);
	}
</script>

<template>
	<v-btn v-if="props.button" @click="open" :title="url" :color="props.color" :variant="variant">{{ text }}</v-btn>
	<a v-else :href="url" @click="open" :class="class" :title="url">{{ text }}</a>
</template>