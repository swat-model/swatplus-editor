<script setup lang="ts">
	import { reactive, computed, onMounted, watch } from 'vue';
	import { useRoute } from 'vue-router';
	import { useVuelidate } from '@vuelidate/core';
	import { numeric, required } from '@vuelidate/validators';
	import { useHelpers } from '@/helpers';

	const route = useRoute();
	const { api, currentProject, errors, utilities } = useHelpers();

	let data:any = reactive({
		page: {
			loading: false,
			error: null,
			validated: false,
			saving: false,
			saveSuccess: false,
			saveError: null
		},
		item: {}
	});

	const itemRules = computed(() => ({
		abs_min: { required, numeric },
		abs_max: { required, numeric }
	}))
	const v$ = useVuelidate(itemRules, data.item);

	async function get() {
		if (route.params.id === undefined) return;
		data.page.loading = true;
		data.page.error = null;

		try {
			const response = await api.get(`change/cal_parms/${route.params.id}`, currentProject.getApiHeader());
			data.item = response.data;
		} catch (error) {
			data.page.error = errors.logError(error, 'Unable to get project information from database.');
		}
			
		data.page.loading = false;
	}

	async function save() {
		data.page.saveError = null;
		data.page.saving = true;
		data.page.saveSuccess = false;

		const valid = await v$.value.$validate();
		if (!valid) {
			data.page.saveError = 'Please fix the errors below and try again.';
		} else {
			try {
				await api.put(`change/cal_parms/${route.params.id}`, data.item, currentProject.getApiHeader());				
				data.page.saveSuccess = true;
			} catch (error) {
				data.page.saveError = errors.logError(error, 'Unable to save changes to database.');
			}
		}

		data.page.saving = false;
	}

	onMounted(async () => await get())
	watch(() => route.path, async () => await get())
</script>

<template>
	<project-container :loading="data.page.loading" :load-error="data.page.error">
		<file-header input-file="cal_parms.cal" docs-path="calibration/cal_parms.cal" use-io>
			<router-link to="/edit/change/hard">Hard Calibration</router-link>
			/ <router-link to="/edit/change/hard/parms">Parameters</router-link>
			/ Edit
		</file-header>

		<error-alert :text="data.page.saveError"></error-alert>
		<success-alert v-model="data.page.saveSuccess" :show="data.page.saveSuccess"></success-alert>

		<p>
			Object type: {{data.item.obj_typ}}
		</p>
		<v-form @submit.prevent="save">
			<div class="form-group">
				<v-text-field label="Absolute Minimum" :suffix="data.item.units"
					v-model.number="data.item.abs_min" type="number" step="any" class="limwid" 
					:error-messages="v$.abs_min.$errors.map(e => e.$message).join(', ')"
					@input="v$.abs_min.$touch" @blur="v$.abs_min.$touch"></v-text-field>
			</div>

			<div class="form-group">
				<v-text-field label="Absolute Maximum" :suffix="data.item.units"
					v-model.number="data.item.abs_max" type="number" step="any" class="limwid"
					:error-messages="v$.abs_max.$errors.map(e => e.$message).join(', ')"
					@input="v$.abs_max.$touch" @blur="v$.abs_max.$touch"></v-text-field>
			</div>

			<action-bar>
				<v-btn type="submit" :loading="data.page.saving" variant="flat" color="primary" class="mr-2">
					Save Changes
				</v-btn>
				<back-button></back-button>
			</action-bar>
		</v-form>
	</project-container>
</template>

<style scoped>
.limwid {
	max-width: 200px;
}
</style>
