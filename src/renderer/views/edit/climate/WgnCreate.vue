<script setup lang="ts">
import { reactive } from "vue";
import WgnForm from "./WgnForm.vue";

let data: any = reactive({
	name: null as string | null,
	lat: null as number | null,
	lon: null as number | null,
	elev: null as number | null,
	rain_yrs: null as number | null,
	monthly_values: [] as any[],
});
</script>

<template>
	<project-container>
		<file-header input-file="weather-wgn.cli" docs-path="climate">
			<router-link to="/edit/climate/wgn">Weather Generator</router-link>
			/ Create
		</file-header>

		<wgn-form :item="data"></wgn-form>
	</project-container>
</template>
