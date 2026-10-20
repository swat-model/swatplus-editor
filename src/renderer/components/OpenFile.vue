<script setup lang="ts">
const electron = window.electronApi;
interface Props {
	filePath: string;
	class?: string;
	text?: string;
	button?: boolean;
	color?: string;
	variant?: "text" | "elevated" | "flat" | "tonal" | "outlined" | "plain" | undefined;
	block?: boolean;
	icon?: string;
	rounded?: string | number | boolean | undefined;
	size?: string;
	asListItem?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
	filePath: "",
	class: "",
	text: "",
	button: false,
	color: undefined,
	variant: "flat",
	block: false,
	icon: undefined,
	rounded: undefined,
	size: undefined,
	asListItem: false,
});

function open(e: any) {
	e.preventDefault();
	if (props.filePath !== undefined && props.filePath !== null && props.filePath !== "") electron.openFileOnSystem(props.filePath);
}
</script>

<template>
	<v-list-item v-if="asListItem" @click="open">
		<v-list-item-title>{{ text }}<slot></slot></v-list-item-title>
	</v-list-item>
	<v-btn
		v-else-if="props.button && props.icon"
		@click="open"
		:title="props.filePath"
		:color="props.color"
		:variant="props.variant"
		:icon="props.icon"
		:size="props.size"
		:class="props.class"
	></v-btn>
	<v-btn
		v-else-if="props.button"
		@click="open"
		:title="props.filePath"
		:color="props.color"
		:variant="props.variant"
		:block="props.block"
		:size="props.size"
		:rounded="props.rounded"
		>{{ props.text }}<slot></slot
	></v-btn>
	<a v-else :href="props.filePath" @click="open" :class="props.class" :title="props.filePath">{{ props.text }}<slot></slot></a>
</template>
