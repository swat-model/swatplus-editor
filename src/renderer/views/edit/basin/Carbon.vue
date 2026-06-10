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

			const response = await api.get(`basin/carbon`, currentProject.getApiHeader());
			errors.log(response.data);
			data.item = response.data;

			const response2 = await api.get(`definitions/vars/carbon_bsn/${utilities.appPathUrl}`);
			errors.log(response2.data);
			data.vars = response2.data;
		} catch (error) {
			data.page.error = errors.logError(error, 'Unable to get project information from database.');
		}
			
		data.page.loading = false;
	}

    async function save() {
		if (!data.hasCarbon) {
            await confirmDelete();
            return;
        }

		data.page.loading = true;
		data.page.error = null;

        try {
            const responseCheck = await api.put(`basin/has-carbon`, {}, currentProject.getApiHeader());
            errors.log(responseCheck);
            await get();
		} catch (error) {
			data.page.error = errors.logError(error, 'Unable to get project information from database.');
		}
			
		data.page.loading = false;
	}

    async function confirmDelete() {
		data.page.delete.errors = [];
		data.page.delete.saving = true;

		try {
			const response = await api.delete(`basin/carbon`, currentProject.getApiHeader());
			errors.log(response);
			data.page.delete.show = false;
			await get();
		} catch (error) {
			data.page.delete.error = errors.logError(error, 'Unable to delete from database.');
		}

		data.page.delete.saving = false;
	}

	onMounted(async () => await get())
	watch(() => route.name, async () => await get())
</script>

<template>
	<project-container :loading="data.page.loading" :load-error="data.page.error">
        <div v-if="route.name == 'BasinCarbon'">
            <file-header input-file="carbon.bsn" docs-path="basin-1" use-io>
                Basin Carbon Inputs
            </file-header>

            <v-switch v-model="data.hasCarbon" label="Enable carbon module?" color="success" class="my-0" @update:modelValue="save"></v-switch>

            <edit-form v-if="data.hasCarbon"
                is-update hide-name no-id hide-copy
                :item="data.item" 
                :vars="data.vars" :nullable-fields="['pet_file']"
                api-url="basin/carbon"
                redirect-route="BasinCarbon"></edit-form>

            <v-dialog v-model="data.page.delete.show" :max-width="constants.dialogSizes.md">
                <v-card title="Confirm delete">
                    <v-card-text>
                        <error-alert :text="data.page.delete.error"></error-alert>

                        <p>
                            Are you sure you want to delete <strong>your basin carbon inputs</strong>?
                            This action is permanent and cannot be undone. 
                        </p>
                    </v-card-text>
                    <v-divider></v-divider>
                    <v-card-actions>
                        <v-btn @click="confirmDelete" :loading="data.page.delete.saving" color="error" variant="text">Delete</v-btn>
                        <v-btn @click="data.page.delete.show = false">Cancel</v-btn>
                    </v-card-actions>
                </v-card>
            </v-dialog>
        </div>
		<router-view></router-view>
	</project-container>    
</template>