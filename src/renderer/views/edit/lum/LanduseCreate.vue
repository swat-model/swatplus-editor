<script setup lang="ts">
	import { reactive } from 'vue';
	import LanduseForm from './LanduseForm.vue';

	let data:any = reactive({
		id: null,
		name: null,
		cal_group: null,
		urb_ro: null,
		plnt_com_name: null,
		mgt_name: null,
		cn2_name: null,
		cons_prac_name: null,
		urban_name: null,
		ov_mann_name: null,
		tile_name: null,
		sep_name: null,
		vfs_name: null,
		grww_name: null,
		bmp_name: null,
		description: null
	});
</script>

<template>
	<project-container>
		<file-header input-file="landuse.lum" docs-path="land-use-management">
			<router-link to="/edit/lum/landuse">Land Use Management</router-link>
			/ Create
		</file-header>

		<landuse-form :item="data"></landuse-form>
	</project-container>
</template>
