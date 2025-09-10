<script setup lang="ts">
	import { reactive, ref, onMounted, onUnmounted, watch } from 'vue';
	import { useRoute } from 'vue-router';
	import { useHelpers } from '@/helpers';

	const route = useRoute();
	const { api, constants, errors, formatters, currentProject, utilities } = useHelpers();

	const recallGrid = ref();

	let table:any = {
		apiUrl: 'db/urban',
		headers: [
			{ key: 'name', label: 'Name' },
			{ key: 'description', label: 'Description' }
		]
	};

	let data:any = reactive({
		page: {
			error: null,
			loading: false,
			saving: false,
			saveSuccess: false,
			showError: false,
			showGrid: false
		},
		form: {
			urban: false
		},
		options: [
			{ value: false, title: 'Disable salt urban module' },
			{ value: true, title: 'Enable salt urban module' }
		]
	});

	async function get() {
		data.page.loading = true;
		data.page.error = null;
		data.page.showError = false;

		try {
			const response = await api.get(`salts/enable-urban`, currentProject.getApiHeader());
			data.form = response.data;
			data.showGrid = data.form.urban;
		} catch (error) {
			data.page.error = errors.logError(error, 'Unable to get project information from database.');
		}
			
		data.page.showError = data.page.error !== null;
		data.page.loading = false;
	}

	async function save() {
		data.page.error = null;
		data.page.saving = true;
		data.page.showError = false;

		try {
			const response = await api.put(`salts/enable-urban`, data.form, currentProject.getApiHeader());

			data.showGrid = data.form.urban;
			if (data.showGrid) await recallGrid?.value?.get(false);
		} catch (error) {
			data.page.error = errors.logError(error, 'Unable to save changes to database.');
		}

		data.page.saving = false;
		data.page.showError = data.page.error !== null;
	}

	onMounted(async () => await get())
	watch(() => route.path, async () => await get())
</script>

<template>
	<project-container :loading="data.page.loading">
		<div v-if="route.name == 'ConstituentsSaltsUrban'">
			<file-header input-file="constituents.cs" docs-path="constituents" use-io>
				<router-link to="/edit/constituents/salts">Salt Constituents</router-link>
				/ Urban Runoff
			</file-header>
			
			<v-form @submit.prevent="save">
				<error-alert as-popup v-model="data.page.showError" :show="data.page.showError" :text="data.page.error" :timeout="-1"></error-alert>
				<success-alert v-model="data.page.saveSuccess" :show="data.page.saveSuccess"></success-alert>

				<div class="form-group">
					<v-select label="Turn salt urban module on/off" v-model="data.form.urban" :items="data.options">
						<template v-slot:append>
							<v-btn type="submit" :loading="data.page.saving" variant="flat" color="primary">Save Changes</v-btn>
						</template>
					</v-select>
				</div>
			</v-form>

			<grid-view v-if="data.showGrid" ref="recallGrid" :api-url="table.apiUrl" :headers="table.headers" hide-create hide-delete
				show-import-export default-csv-file="salt_urban.csv" table-name="salt_urban">
			</grid-view>
		</div>
		<router-view></router-view>
	</project-container>
</template>
