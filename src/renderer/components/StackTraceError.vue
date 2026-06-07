<script setup lang="ts">
	import { useFormatters } from '@/helpers/formatters';
	const formatters = useFormatters();

	interface Props {
		errorTitle?: string | null,
		stackTrace: string | null
	}

	const props = withDefaults(defineProps<Props>(), {
		errorTitle: 'SWAT+ Editor has encountered an error.',
		stackTrace: null
	});
</script>

<template>
	<div>
		<error-alert :text="props.errorTitle"></error-alert>

		<p>
			Jika Anda tidak mengetahui penyebab kesalahan tersebut, silakan salin dan tempel log di bawah ini ke dalam <open-in-browser url="https://groups.google.com/d/forum/swatplus-editor" text="SWAT+ Editor user group" />.
			Harap sertakan basis data proyek Anda dan file relevan lainnya.
		</p>

		<v-textarea v-model="props.stackTrace" rows="3" max-rows="6" readonly class="mb-4" @focus="$event.target.select()"></v-textarea>
	</div>
</template>