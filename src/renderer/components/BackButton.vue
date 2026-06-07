<script setup lang="ts">
	import { useRouter } from 'vue-router';

	const router = useRouter();
	const goBack = () => {
  		router.go(-1);
	};
</script>

<template>
	<v-btn variant="tonal" @click="goBack" class="mr-2">Back</v-btn>
</template>