<script setup lang="ts">
	import { computed } from 'vue';
	import { useFormatters } from '@/helpers/formatters';
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

	const docsUrl = computed(() => {
		if (props.useIo) return 'https://swatplus.gitbook.io/io-docs/introduction/' + props.docsPath;		
		return 'https://swatplus.gitbook.io/docs/user/editor/inputs/' + props.docsPath;
	})

	function open(e:any) {
		if (!formatters.isNullOrEmpty(props.docsPath)) {
			e.preventDefault();
			electron.openUrl(docsUrl.value);
		}
	}
</script>

<template>
	<h1 class="file-header text-h5 d-flex align-end mb-6">
		<span class="heading mr-1">
			<slot></slot>
		</span>
		<span class="info ml-auto">
			<a @click.prevent="open" v-if="props.docsPath != ''" :title="docsUrl" href="#" class="text-decoration-none text-medium-emphasis">
				{{inputFile}}
				<font-awesome-icon :icon="['fas', 'book']" class="ml-2 pointer" />
			</a>
		</span>
	</h1>
</template>