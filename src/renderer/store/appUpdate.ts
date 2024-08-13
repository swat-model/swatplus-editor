import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useAppUpdate = defineStore('appUpdate', () => {
	const message = ref<string>('');
	const isAvailable = ref<boolean>(false);

	function setStatus(m:string, a:boolean):void {
		message.value = m;
		isAvailable.value = a;
	}

	return {
		message, isAvailable, setStatus
	}
})