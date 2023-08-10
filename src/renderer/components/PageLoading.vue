<script setup lang="ts">
	const props = defineProps({
		loading: { type: Boolean, required: false, default: false },
	})
</script>

<template>
	<div v-if="props.loading" class="text-center pa-5">
		<font-awesome-icon :icon="['fas', 'spinner']" spin size="2x" />
	</div>
</template>
