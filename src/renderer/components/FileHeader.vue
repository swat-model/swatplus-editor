<script setup lang="ts">
	import { useFormatters } from '../plugins/formatters';
	const formatters = useFormatters();
	const electron = window.electronApi;

	interface Props {
		docsPath?: string | null,
		inputFile?: string | null,
		useIo?: boolean
	}

	const props = withDefaults(defineProps<Props>(), {
		docsPath: null,
		inputFile: null,
		useIo: false
	});

	function open(e:any) {
		if (!formatters.isNullOrEmpty(props.docsPath)) {
			e.preventDefault();
			if (props.useIo)
				electron.openUrl('https://swatplus.gitbook.io/swat+-documentation/introduction/' + props.docsPath);
			else
				electron.openUrl('https://swatplus.gitbook.io/docs/user/editor/inputs/' + props.docsPath);
		}
	}
</script>

<template>
	<h1 class="file-header text-h5 d-flex align-end mb-6">
		<span class="heading mr-1">
			<slot></slot>
		</span>
		<span class="info ml-auto">
			{{inputFile}}
			<a @click.prevent="open" v-if="props.docsPath != ''">
				<font-awesome-icon :icon="['fas', 'book']" class="ml-2 pointer" />
			</a>
		</span>
	</h1>
</template>