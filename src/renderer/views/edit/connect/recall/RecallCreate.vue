<script setup lang="ts">
import { reactive } from 'vue';
import RecallForm from './RecallForm.vue';

let data:any = reactive({
	apiUrl: 'recall',
	item: {
		connect: {
			name: null,
			area: 0,
			lat: 0,
			lon: 0,
			elev: null,
			wst_name: null
		},
		props: {},
		outflow: []
	}
});
</script>

<template>
	<project-container>
		<file-header input-file="recall.con" docs-path="connections/recall">
			<router-link to="/edit/cons/recall">Point Source</router-link>
			/ Create
		</file-header>

		<recall-form :item="data.item" :api-url="data.apiUrl"></recall-form>
	</project-container>
</template>
