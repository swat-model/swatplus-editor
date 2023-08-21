<script setup lang="ts">
	
</script>

<template>
	<v-sheet elevation="2" max-width="600" rounded="lg" width="100%" class="my-4 pa-4 text-center mx-auto">
		<v-icon class="mb-5" color="primary" icon="fas fa-magnifying-glass" size="112" ></v-icon>

		<h2 class="text-h5 mb-6">Page Not Found</h2>

		<p class="mb-4 text-medium-emphasis">
			The item you clicked does not go to an active page.
			This is a bug in the editor. Please report the route: <strong>{{ $route.path }}</strong>
			to the <open-in-browser url="https://groups.google.com/d/forum/swatplus-editor" text="SWAT+ Editor user group"></open-in-browser>.
		</p>

		<v-divider class="mb-4"></v-divider>

		<div>
		<v-btn class="text-none" color="primary" rounded variant="flat" @click="$router.go(-1)">Go Back</v-btn>
		</div>
	</v-sheet>
</template>