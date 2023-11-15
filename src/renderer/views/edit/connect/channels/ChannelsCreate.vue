<script setup lang="ts">
	import { reactive } from 'vue';
	import ChannelsForm from './ChannelsForm.vue';

	let data:any = reactive({
		apiUrl: 'channels',
		item: {
			connect: {
				name: null,
				area: 0,
				lat: 0,
				lon: 0,
				elev: null,
				wst_name: null
			},
			props: {},
			outflow: []
		}
	});
</script>

<template>
	<project-container>
		<file-header input-file="chandeg.con" docs-path="channels/channel-lte.cha" use-io>
			<router-link to="/edit/cons/channels">Channels</router-link>
			/ Create
		</file-header>

		<channels-form :item="data.item" :api-url="data.apiUrl"></channels-form>
	</project-container>
</template>