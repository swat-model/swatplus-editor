<script setup lang="ts">
	import { reactive, onMounted, watch } from 'vue';
	import { useRoute } from 'vue-router';
	import { useHelpers } from '@/helpers';
	import CalibrationForm from './CalibrationForm.vue';

	const route = useRoute();
	const { api, currentProject, errors } = useHelpers();

	let data:any = reactive({
		page: {
			loading: false,
			error: null
		},
		item: {},
		initObjs: [],
		initConds: [],
		initialSelection: {}
	});

	async function get() {
		if (route.params.id === undefined) return;
		data.page.loading = true;
		data.page.error = null;

		try {
			const response = await api.get(`change/calibration/${route.params.id}`, currentProject.getApiHeader());
			errors.log(response.data);

			data.item = response.data.item;
			data.item.cal_parm_name = data.item.cal_parm != null ? data.item.cal_parm.name : '';
			data.initialSelection = response.data.initialSelection;

			if (data.item.elements) {
				for (let i = 0; i < data.item.elements.length; i++) {
					data.initObjs.push(data.item.elements[i].obj_id);
				}
			}

			//For some reason, this wasn't loading correctly just setting the array to = this.items.conditions; iterating and making a copy fixes it
			if (data.item.conditions) {
				for (let i = 0; i < data.item.conditions.length; i++) {
					data.initConds.push(data.item.conditions[i]);
				}
			}
		} catch (error) {
			data.page.error = errors.logError(error, 'Unable to get properties from database.');
		}
		
		data.page.loading = false;
	}

	onMounted(async () => await get())
	watch(() => route.name, async () => await get())
	watch(() => route.params.id, async () => await get())
</script>

<template>
	<project-container :loading="data.page.loading" :load-error="data.page.error">
		<file-header input-file="calibration.cal" docs-path="calibration/calibration.cal" use-io>
			<router-link to="/edit/change/hard">Hard Calibration</router-link>
			/ Edit
		</file-header>

		<calibration-form is-update :item="data.item" :init-objs="data.initObjs" :init-conds="data.initConds" :initial-selection="data.initialSelection" />
	</project-container>
</template>
