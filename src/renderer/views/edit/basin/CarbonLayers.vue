<script setup lang="ts">
	import { reactive, onMounted, watch } from 'vue';
	import { useRoute } from 'vue-router';
	import { useHelpers } from '@/helpers';
	import EditForm from '@/components/EditForm.vue';

	const route = useRoute();
	const { api, constants, currentProject, errors, utilities } = useHelpers();

	let data:any = reactive({
		page: {
			loading: false,
			error: null,
            delete: {
                show: false,
                error: null,
                saving: false,
            },
		},
		item: {},
		vars: [],
        hasCarbon: false
	});

	async function get() {
		data.page.loading = true;
		data.page.error = null;

		try {
            const responseCheck = await api.get(`basin/has-carbon`, currentProject.getApiHeader());
            data.hasCarbon = responseCheck.data.has_carbon;
		} catch (error) {
			data.page.error = errors.logError(error, 'Unable to get project information from database.');
		}
			
		data.page.loading = false;
	}

    onMounted(async () => await get())
	watch(() => route.name, async () => await get())
</script>

<template>
	<project-container :loading="data.page.loading" :load-error="data.page.error">
		<div v-if="route.name == 'BasinCarbonLayers'">
			<file-header input-file="carbon_lyr.bsn" docs-path="basin-1" use-io>
				Carbon Layers
			</file-header>

            <v-alert v-if="!data.hasCarbon" type="info" icon="$info" variant="tonal" border="start" class="mb-4">
                Enable the <router-link to="/edit/basin/carbon">carbon module here</router-link> to view and edit carbon layers.
            </v-alert>

			<grid-view v-if="data.hasCarbon" hide-create hide-delete
				api-url="basin/carbon/lyrs" :default-sort="['layer','asc']"
				use-dynamic-headers
				table-name="carbon_lyr_bsn" />
		</div>
		<router-view></router-view>
	</project-container>
</template>