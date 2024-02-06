<script setup lang="ts">
	import { reactive, computed } from 'vue';
	import { useHelpers } from '@/helpers';

	const { constants, formatters, currentProject, utilities } = useHelpers();

	const electron = window.electronApi;

	interface Props {
		text?: string | null,
		ranSwat?: boolean,
		noIcon?: boolean,
		variant?: "text" | "elevated" | "flat" | "tonal" | "outlined" | "plain" | undefined,
		color?: string | undefined,
		block?: boolean,
		rounded?: string | number | boolean | undefined,
		size?: string | number | undefined,
		class?: string | undefined
	}

	const props = withDefaults(defineProps<Props>(), {
		text: 'SWAT+ Toolbox',
		ranSwat: false,
		noIcon: false,
		variant: undefined,
		color: undefined,
		block: false,
		rounded: undefined,
		size: undefined,
		class: undefined
	});

	let unavailable = reactive({
		show: false,
		norun: false,
		notinstalled: false,
		error: ''
	});

	const unavailableTitle = computed(() => {
		if (unavailable.norun) return 'Not ready to run SWAT+ Toolbox';
		if (unavailable.notinstalled) return 'SWAT+ Toolbox is not installed';
		return 'Error opening SWAT+ Toolbox';
	})

	function open() {
		unavailable.norun = false;
		unavailable.notinstalled = false;
		unavailable.show = false;
		let path = electron.getSwatPlusToolboxPath();

		if (!props.ranSwat) {
			unavailable.norun = true;
			unavailable.show = true;
		} else if (!utilities.pathExists(path)) {
			unavailable.notinstalled = true;
			unavailable.show = true;
		} else {
			unavailable.error = electron.launchSwatPlusToolbox(currentProject.projectDb||'');
			if (!formatters.isNullOrEmpty(unavailable.error)) {
				unavailable.show = true;
			}
		}
	}
</script>

<template>
	<v-btn v-if="constants.globals.platform === 'win32' && !noIcon" @click="open" :active="false">
		<v-icon>fas fa-toolbox</v-icon> {{ props.text }}
	</v-btn>
	<v-btn v-else-if="constants.globals.platform === 'win32' && noIcon" @click="open" :variant="variant" :color="color" :block="block" :rounded="rounded" :size="size" :class="class">
		{{ props.text }}
	</v-btn>

	<v-dialog v-model="unavailable.show" width="auto">
		<v-card :title="unavailableTitle">
			<v-card-text>
				<p v-if="unavailable.norun" class="py-5">
					You must run the model before opening your project in SWAT+ Toolbox.
				</p>
				<p v-else-if="unavailable.notinstalled" class="py-5">
					SWAT+ Toolbox can be used for sensitivity analysis, model calibration, evaluation, and validation.
					Click the button below to download.
				</p>
			</v-card-text>
			<v-divider></v-divider>
			<v-card-actions>
				<v-btn v-if="unavailable.norun" color="primary" variant="text" to="/run">Configure Model Run</v-btn>
				<open-in-browser v-else-if="unavailable.notinstalled" url="https://swat.tamu.edu/software/plus/" text="Install SWAT+ Toolbox" button color="primary" />
				<v-btn @click="unavailable.show = false">Cancel</v-btn>
			</v-card-actions>
		</v-card>
	</v-dialog>
</template>