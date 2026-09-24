<script setup lang="ts">
import { reactive } from "vue";
import StationsForm from "./StationsForm.vue";

let data: any = reactive({
	name: null as string | null,
	lat: null as number | null,
	lon: null as number | null,
	wgn: null as string | null,
	pcp: "sim" as string | null,
	tmp: "sim" as string | null,
	slr: "sim" as string | null,
	hmd: "sim" as string | null,
	wnd: "sim" as string | null,
	pet: null as string | null,
	atmo_dep: null as string | null,
});
</script>

<template>
	<project-container>
		<file-header input-file="weather-sta.cli" docs-path="climate">
			<router-link to="/edit/climate/stations"
				>Weather Stations</router-link
			>
			/ Create
		</file-header>

		<stations-form :item="data"></stations-form>
	</project-container>
</template>
