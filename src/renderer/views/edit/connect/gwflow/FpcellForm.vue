<script setup lang="ts">
	import { reactive, onMounted, computed, watch } from 'vue';
	import { useRouter } from 'vue-router';
	import { useHelpers } from '@/helpers';

	const router = useRouter();
	const { api, constants, currentProject, errors, formatters, utilities } = useHelpers();

	interface Props {
		item: any,
		isUpdate?: boolean
	}

	const props = withDefaults(defineProps<Props>(), {
		apiUrl: '',
		item: { id: 0 },
		isUpdate: false
	});

	let page:any = reactive({
		loading: true,
		error: null,
		validated: false,
		saving: false,
		saveSuccess: false
	});

	function putDb(data:any) {
		if (props.isUpdate)
			return api.put(`gwflow/fpcell/${props.item.id}`, data, currentProject.getApiHeader());
		else
			return api.post(`gwflow/fpcell`, data, currentProject.getApiHeader());
	}

	async function save() {
		page.error = null;
		page.saving = true;
		page.saveSuccess = false;
		page.validated = true;
		let val_error = false;
		
		if (!val_error) {
			try {
				const response = await putDb(props.item);

				if (props.isUpdate)
					page.saveSuccess = true;
				else
					router.push({ name: 'GwflowFpcell' });
			} catch (error) {
				page.error = errors.logError(error, 'Unable to save changes to database.');
			}
		}
		
		page.saving = false;
		page.validated = false;
	}
</script>

<template>
	<div>
		<error-alert :text="page.error"></error-alert>
		<success-alert v-model="page.saveSuccess" :show="page.saveSuccess"></success-alert>

		<v-form @submit.prevent="save">
			<div class="form-group">
				<v-text-field v-model="item.name" :rules="[constants.formRules.required, constants.formRules.nameLength]" 
					label="Name" hint="Must be unique"></v-text-field>
			</div>

			<div class="form-group">
				<auto-complete label="Channel"
					v-model="item.channel_name" :value="item.channel_name" :show-item-link="props.isUpdate"
					table-name="chandeg_con" route-name="ChannelsEdit"
					section="Connections / Channels" help-file="chandeg.con" help-db="chandeg_con"
					api-url="channels/items"></auto-complete>
			</div>

			<action-bar>
				<v-btn type="submit" :loading="page.saving" variant="flat" color="primary" class="mr-2">Save Changes</v-btn>
				<back-button></back-button>
			</action-bar>
		</v-form>
	</div>
</template>