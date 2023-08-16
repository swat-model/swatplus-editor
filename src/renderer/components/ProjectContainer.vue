<script setup lang="ts">
	import { usePlugins } from '../plugins';
	const { formatters, currentProject } = usePlugins();

	interface Props {
		loading: boolean,
		loadError?: string | null
	}

	const props = withDefaults(defineProps<Props>(), {
		loading: false,
		loadError: null
	});

	let errorMessage = !formatters.isNullOrEmpty(props.loadError) ? props.loadError : 'No project open. Please go to project setup to continue.';
</script>

<template>
	<div>
		<page-loading :loading="props.loading"></page-loading>
		<div v-if="!loading">
			<div v-if="currentProject.hasCurrentProject && currentProject.isSupported && formatters.isNullOrEmpty(props.loadError)">
				<slot></slot>
			</div>
			<div v-else>
				<error-alert :text="errorMessage"></error-alert>
			</div>
		</div>
	</div>
</template>