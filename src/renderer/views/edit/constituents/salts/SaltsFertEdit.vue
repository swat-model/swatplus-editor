<script setup lang="ts">
	import { reactive, onMounted, watch, computed } from 'vue';
	import { useRoute } from 'vue-router';
	import { useHelpers } from '@/helpers';
	import { useVuelidate } from '@vuelidate/core';
	import { decimal, required } from '@vuelidate/validators';

	const route = useRoute();
	const { api, constants, currentProject, errors, formatters, utilities } = useHelpers();

	let data:any = reactive({
		page: {
			loading: false,
			error: null,
			saveError: null,
			showError: false,
			saving: false,
			saveSuccess: false,
		},
		name: '',
		item: {
			id: 0,
			name_id: 0,
			so4: 0,
			ca: 0,
			mg: 0,
			na: 0,
			k: 0,
			cl: 0,
			co3: 0,
			hco3: 0
		}
	});

	const rules = computed(() => ({
		so4: { required, decimal },
		ca: { required, decimal },
		mg: { required, decimal },
		na: { required, decimal },
		k: { required, decimal },
		cl: { required, decimal },
		co3: { required, decimal },
		hco3: { required, decimal }
	}))
	const v$ = useVuelidate(rules, data.item);

	async function get() {
		if (route.params.id === undefined) return;
		data.page.loading = true;
		data.page.error = null;

		try {
			const response = await api.get(`salts/fert/${route.params.id}`, currentProject.getApiHeader());
			errors.log(response.data);
			data.name = response.data.name;
			utilities.assignReactiveObject(data.item, response.data.item);
		} catch (error) {
			data.page.error = errors.logError(error, 'Unable to get project information from database.');
		}

		data.page.loading = false;
	}

	async function save() {
		data.page.saveError = null;
		data.page.saving = true;
		data.page.showError = false;
		data.page.saveSuccess = false;

		try {
			const response = await api.put(`salts/fert/${data.item.id}`, data.item, currentProject.getApiHeader());
			errors.log(response.data);
			data.page.saveSuccess = true;
		} catch (error) {
			data.page.saveError = errors.logError(error, 'Unable to save changes to database.');
		}

		data.page.saving = false;
		data.page.showError = data.page.saveError !== null;
	}

	onMounted(async () => await get())
	watch(() => route.name, async () => await get())
	watch(() => route.params.id, async () => await get())
</script>

<template>
	<project-container :loading="data.page.loading" :load-error="data.page.error">
		<file-header input-file="constituents.cs" docs-path="constituents" use-io>
				<router-link to="/edit/constituents/salts">Salt Constituents</router-link>
				/ <router-link to="/edit/constituents/salts/fert">Fertilizer</router-link>
				/ Edit
			</file-header>

			<error-alert as-popup v-model="data.page.showError" :show="data.page.showError" :text="data.page.saveError" :timeout="-1"></error-alert>
			<success-alert v-model="data.page.saveSuccess" :show="data.page.saveSuccess"></success-alert>

			<div class="form-group">
				<v-text-field v-model="data.name" label="Name" readonly hint="Name cannot be modified. Matches one of your existing fertilizers."></v-text-field>
			</div>

			<v-form @submit.prevent="save">
				<div class="form-group mb-0">
					<v-text-field v-model="data.item.so4" 
						label="Fraction sulfate (so4)" type="number" step="any"
						:error-messages="v$.so4.$errors.map(e => e.$message).join(', ')"
						@input="v$.so4.$touch" @blur="v$.so4.$touch"></v-text-field>
				</div>
				<div class="form-group mb-0">
					<v-text-field v-model="data.item.ca" 
						label="Fraction calcium (ca)" type="number" step="any"
						:error-messages="v$.ca.$errors.map(e => e.$message).join(', ')"
						@input="v$.ca.$touch" @blur="v$.ca.$touch"></v-text-field>
				</div>
				<div class="form-group mb-0">
					<v-text-field v-model="data.item.mg" 
						label="Fraction magnesium (mg)" type="number" step="any"
						:error-messages="v$.mg.$errors.map(e => e.$message).join(', ')"
						@input="v$.mg.$touch" @blur="v$.mg.$touch"></v-text-field>
				</div>
				<div class="form-group mb-0">
					<v-text-field v-model="data.item.na" 
						label="Fraction sodium (na)" type="number" step="any"
						:error-messages="v$.na.$errors.map(e => e.$message).join(', ')"
						@input="v$.na.$touch" @blur="v$.na.$touch"></v-text-field>
				</div>
				<div class="form-group mb-0">
					<v-text-field v-model="data.item.k" 
						label="Fraction potassium (k)" type="number" step="any"
						:error-messages="v$.k.$errors.map(e => e.$message).join(', ')"
						@input="v$.k.$touch" @blur="v$.k.$touch"></v-text-field>
				</div>
				<div class="form-group mb-0">
					<v-text-field v-model="data.item.cl" 
						label="Fraction chlorine (cl)" type="number" step="any"
						:error-messages="v$.cl.$errors.map(e => e.$message).join(', ')"
						@input="v$.cl.$touch" @blur="v$.cl.$touch"></v-text-field>
				</div>
				<div class="form-group mb-0">
					<v-text-field v-model="data.item.co3" 
						label="Fraction carbonate (co3)" type="number" step="any"
						:error-messages="v$.co3.$errors.map(e => e.$message).join(', ')"
						@input="v$.co3.$touch" @blur="v$.co3.$touch"></v-text-field>
				</div>
				<div class="form-group mb-0">
					<v-text-field v-model="data.item.hco3" 
						label="Fraction hydrogen carbonate (hco3)" type="number" step="any"
						:error-messages="v$.hco3.$errors.map(e => e.$message).join(', ')"
						@input="v$.hco3.$touch" @blur="v$.hco3.$touch"></v-text-field>
				</div>

				<action-bar>
					<v-btn type="submit" :loading="data.page.saving" variant="flat" color="primary" class="mr-2">Save Changes</v-btn>
					<back-button></back-button>
				</action-bar>
			</v-form>
	</project-container>
</template>