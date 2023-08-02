<script setup lang="ts">
	import { onMounted, ref } from 'vue';
	// @ts-ignore
	import { Modal } from 'bootstrap';

	defineProps({
		title: {
			type: String,
			default: '',
		},
		size: {
			type: String,
			default: 'lg',
		},
	});

	let modalEle = ref(null);
	let thisModalObj:any = null;

	onMounted(() => {
		// @ts-ignore
		thisModalObj = new Modal(modalEle.value);
	});

	function _show() {
		thisModalObj.show();
	}

	defineExpose({ show: _show });
</script>

<template>
	<div class="modal fade" id="bsModal" tabindex="-1" aria-labelledby="bsModalLabel" aria-hidden="true" ref="modalEle">
		<div :class="`modal-dialog modal-${size} modal-dialog-scrollable`">
			<div class="modal-content">
				<div class="modal-header">
					<h5 class="modal-title" id="bsModalLabel">{{ title }}</h5>
					<button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
				</div>
				<div class="modal-body">
					<slot name="body" />
				</div>
				<div class="modal-footer">
					<slot name="footer"></slot>
					<button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
				</div>
			</div>
		</div>
	</div>
</template>