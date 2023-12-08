<script setup lang="ts">
	import { reactive, onMounted, watch } from 'vue';
	import { useRoute } from 'vue-router';
	import { useHelpers } from '@/helpers';
	import LanduseForm from './LanduseForm.vue';

	const route = useRoute();
	const { api, currentProject, errors } = useHelpers();

	let data:any = reactive({
		page: {
			loading: false,
			error: null
		},
		item: {}
	});

	async function get() {
		if (route.params.id === undefined) return;
		data.page.loading = true;
		data.page.error = null;

		try {
			const response = await api.get(`lum/landuse/${route.params.id}`, currentProject.getApiHeader());
			errors.log(response.data);

			data.item = {
				id: response.data.id,
				name: response.data.name,
				cal_group: response.data.cal_group,
				urb_ro: response.data.urb_ro,
				plnt_com_name: response.data.plnt_com != null ? response.data.plnt_com.name : '',
				mgt_name: response.data.mgt != null ? response.data.mgt.name : '',
				cn2_name: response.data.cn2 != null ? response.data.cn2.name : '',
				cons_prac_name: response.data.cons_prac != null ? response.data.cons_prac.name : '',
				urban_name: response.data.urban != null ? response.data.urban.name : '',
				ov_mann_name: response.data.ov_mann != null ? response.data.ov_mann.name : '',
				tile_name: response.data.tile != null ? response.data.tile.name : '',
				sep_name: response.data.sep != null ? response.data.sep.name : '',
				vfs_name: response.data.vfs != null ? response.data.vfs.name : '',
				grww_name: response.data.grww != null ? response.data.grww.name : '',
				bmp_name: response.data.bmp != null ? response.data.bmp.name : '',
				description: response.data.description
			};
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
		<file-header input-file="landuse.lum" docs-path="land-use-management">
			<router-link to="/edit/lum/landuse">Land Use Management</router-link>
			/ Edit
		</file-header>

		<landuse-form is-update :item="data.item"></landuse-form>
	</project-container>
</template>
