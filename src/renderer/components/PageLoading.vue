<script setup lang="ts">
	const props = defineProps({
		loading: { type: Boolean, required: false, default: false },
		message: { type: String, required: false, default: '' },
	})
</script>

<template>
	<div v-if="props.loading" class="text-center pa-5">
		<v-progress-circular indeterminate></v-progress-circular>
		<div v-if="props.message && props.message !== ''" class="mt-1">{{ props.message }}</div>
	</div>
</template>
