<script setup lang="ts">
	import { reactive, onMounted, watch } from 'vue';
	import { useRoute } from 'vue-router';
	import { useHelpers } from '@/helpers';
	import ElementsForm from './ElementsForm.vue';

	const route = useRoute();
	const { api, currentProject, errors, utilities } = useHelpers();

	let data:any = reactive({
		paths: {
			data: 'regions/ls_units'
		},
		page: {
			loading: false,
			error: null
		},
		item: <any>{
			obj_typ: 'hru',
			bsn_frac: 0,
			sub_frac: 0,
			reg_frac: 0
		},
		objTypes: <any[]>[]
	});

	async function get() {
		data.page.loading = true;
		data.page.error = null;

		try {
			const response = await api.get(`definitions/codes/connect/obj_typ/${utilities.appPathUrl}`);
			data.objTypes = response.data;
		} catch (error) {
			data.page.error = errors.logError(error, 'Unable to get project information from database.');
		}
			
		data.page.loading = false;
	}

	onMounted(async () => await get())
</script>

<template>
	<project-container :loading="data.page.loading" :load-error="data.page.error">
		<file-header input-file="ls_unit.ele" docs-path="landscape-units/ls_unit.ele" use-io>
			<router-link to="/edit/regions/ls_units">Landscape Units</router-link> /
			<router-link to="/edit/regions/ls_units/elements">Elements</router-link>
			/ Create
		</file-header>

		<elements-form :item="data.item" :obj-types="data.objTypes"></elements-form>
	</project-container>
</template>
