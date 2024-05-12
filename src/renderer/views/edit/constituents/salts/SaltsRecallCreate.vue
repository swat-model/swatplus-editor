<script setup lang="ts">
import { reactive } from 'vue';
import SaltsRecallForm from './SaltsRecallForm.vue';

let data:any = reactive({
	apiUrl: 'salts/recall',
	item: {
		name: null,
		rec_typ: 3,
	}
});
</script>

<template>
	<project-container>
		<file-header input-file="constituents.cs" docs-path="constituents" use-io>
			<router-link to="/edit/constituents/salts">Salt Constituents</router-link>
			/ <router-link to="/edit/constituents/salts/recall">Point Source</router-link>
			/ Create
		</file-header>

		<salts-recall-form :item="data.item" :api-url="data.apiUrl"></salts-recall-form>
	</project-container>
</template>
