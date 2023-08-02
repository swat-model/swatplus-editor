<script setup lang="ts">
	const electron = window.electronApi;
	interface Props {
		url: string,
		class?: string,
		text: string
	}

	const props = defineProps<Props>();

	function open(e:any) {
		e.preventDefault();
		electron.openUrl(props.url);
	}
</script>

<template>
	<a :href="url" @click="open" :class="class" :title="url">{{ text }}</a>
</template>