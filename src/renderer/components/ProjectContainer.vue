<script setup lang="ts">
	import { useHelpers } from '@/helpers';
	const { formatters, currentProject } = useHelpers();

	interface Props {
		loading?: boolean,
		loadError?: string | null,
		addErrorFrame?: boolean
	}

	const props = withDefaults(defineProps<Props>(), {
		loading: false,
		loadError: null,
		addErrorFrame: false
	});

	let errorMessage = 'No project open. Please go to project setup to continue.';
</script>

<template>
	<div>
		<page-loading :loading="props.loading"></page-loading>
		<div v-if="!props.loading">
			<div v-if="currentProject.hasCurrentProject && currentProject.isSupported && formatters.isNullOrEmpty(props.loadError)">
				<slot></slot>
			</div>
			<div v-else-if="props.addErrorFrame">
				<v-main>
					<div class="py-3 px-6">
						<error-alert :text="!formatters.isNullOrEmpty(props.loadError) ? props.loadError : errorMessage"></error-alert>
					</div>
				</v-main>
			</div>
			<div v-else>
				<error-alert :text="!formatters.isNullOrEmpty(props.loadError) ? props.loadError : errorMessage"></error-alert>
			</div>
		</div>
	</div>
</template>