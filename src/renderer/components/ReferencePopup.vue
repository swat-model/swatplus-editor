<script setup lang="ts">
	import { useHelpers } from '@/helpers';
	const { currentProject, formatters } = useHelpers();

	interface Props {
		apiUrl?: string,
		section?: string,
		helpFile?: string,
		helpDb?: string,
	}

	const props = withDefaults(defineProps<Props>(), {
		apiUrl: '',
		section: '',
		helpFile: '',
		helpDb: '',
	});
</script>

<template>
	<v-menu open-on-hover>
		<template v-slot:activator="{ props }">
			<font-awesome-icon v-bind="props" :icon="['fas', 'question-circle']" class="text-info pointer"></font-awesome-icon>
		</template>

		<v-card>
			<v-card-text>
				This field references a row in the <mark>{{ props.section }}</mark> section.
			</v-card-text>
			<v-divider></v-divider>
			<v-card-text>
				<div>Input file: <code class="font-weight-bold">{{ props.helpFile }}</code></div>
				<div>Database table: <code class="font-weight-bold">{{ props.helpDb }}</code></div>
			</v-card-text>
			<v-card-actions>
				<v-btn v-if="!formatters.isNullOrEmpty(props.apiUrl)" 
					color="primary"
					:href="`/#/table-browser?apiUrl=${props.apiUrl}&section=${props.section}&projectDb=${currentProject.projectDbUrl}`" target="_blank">
					Browse Table
					<font-awesome-icon :icon="['fas', 'up-right-from-square']" class="ml-1"></font-awesome-icon>
				</v-btn>
			</v-card-actions>
		</v-card>
	</v-menu>
</template>