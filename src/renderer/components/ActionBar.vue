<script setup lang="ts">
	const props = defineProps({
		fullWidth: {
			type: Boolean,
			required: false
		}
	})
</script>

<template>
	<div style="height:80px"></div>
	<div :class="props.fullWidth ? 'page-action-bar full' : 'page-action-bar'">
		<div class="d-flex align-center px-6 py-2">
			<slot></slot>
		</div>
	</div>
</template>