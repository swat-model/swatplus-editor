<template>
	<project-container :loading="page.loading" :load-error="page.error">
		<file-header input-file="hru-lte.con" docs-path="connections/hrus">
			<router-link to="/edit/hrus-lte">HRUs</router-link>
			/ Create
		</file-header>

		<hrus-lte-form :item="item" :api-url="apiUrl" :vars="vars"></hrus-lte-form>
	</project-container>
</template>

<script>
import HrusLteForm from './HrusLteForm.vue';

export default {
	name: 'HrusLteCreate',
	components: {
		HrusLteForm
	},
	data() {
		return {
			apiUrl: 'hrus-lte',
			paths: {
				vars: 'hru_lte_hru'
			},
			page: {
				loading: true,
				error: null
			},
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
			},
			vars: []
		}
	},
	async created() {
		if (this.currentProjectSupported) await this.get();
	},
	methods: {
		async get() {
			this.page.loading = true;
			this.page.error = null;

            try {
				const response = await this.$http.get(`vars/${this.paths.vars}/${this.appPath}`);
                this.vars = response.data;
                
                let keys = Object.keys(this.vars);
                for (let k of keys) {
					let v = this.vars[k];
                    this.item.props[k] = v.type == 'string' ? v.default_text : v.default_value;
                }
			} catch (error) {
				this.page.error = this.logError(error, 'Unable to get table metadata from database.');
			}
				
			this.page.loading = false;
		}
	}
}
</script>