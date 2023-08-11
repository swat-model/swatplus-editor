<script setup lang="ts">
	const electron = window.electronApi;
	interface Props {
		filePath: string,
		class?: string,
		text?: string,
		button?: boolean,
		color?: string,
		variant?: "text" | "elevated" | "flat" | "tonal" | "outlined" | "plain" | undefined
		block?: boolean,
		icon?: string,
		size?: string
	}

	const props = defineProps<Props>();

	function open(e:any) {
		e.preventDefault();
		if (props.filePath !== undefined && props.filePath !== null && props.filePath !== '') electron.openFileOnSystem(props.filePath);
	}
</script>

<template>
	<v-btn v-if="props.button && props.icon" @click="open" :title="filePath" :color="props.color" :variant="variant" :icon="icon" :size="size"></v-btn>
	<v-btn v-else-if="props.button" @click="open" :title="filePath" :color="props.color" :variant="variant" :block="block" :size="size">{{ text }}<slot></slot></v-btn>
	<a v-else :href="filePath" @click="open" :class="class" :title="filePath">{{ text }}<slot></slot></a>
</template>