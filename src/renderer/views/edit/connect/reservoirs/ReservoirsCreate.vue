<script setup lang="ts">
import { reactive } from 'vue';
import ReservoirsForm from './ReservoirsForm.vue';

let data:any = reactive({
	apiUrl: 'reservoirs',
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
		<file-header input-file="reservoir.con" docs-path="reservoirs/reservoir.res" use-io>
			<router-link to="/edit/cons/reservoirs">Reservoirs</router-link>
			/ Create
		</file-header>

		<reservoirs-form :item="data.item" :api-url="data.apiUrl"></reservoirs-form>
	</project-container>
</template>
