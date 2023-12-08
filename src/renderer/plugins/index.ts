import vuetify from './vuetify'
import pinia from '../store'
import router from '../router'

//Font Awesome
import { library } from '@fortawesome/fontawesome-svg-core';
import { fas } from '@fortawesome/free-solid-svg-icons';
import { far } from '@fortawesome/free-regular-svg-icons';
import { fab } from '@fortawesome/free-brands-svg-icons';
import { FontAwesomeIcon, FontAwesomeLayers, FontAwesomeLayersText } from '@fortawesome/vue-fontawesome';

//Highcharts
import HighchartsVue from 'highcharts-vue';
import Highcharts from 'highcharts';
import HighchartsMore from 'highcharts/highcharts-more';
import accessibilityInit from 'highcharts/modules/accessibility';
import exportingInit from 'highcharts/modules/exporting';
import exportDataInit from 'highcharts/modules/export-data';
import offlineExportInit from 'highcharts/modules/offline-exporting';

//Custom Components
import ActionBar from '@/components/ActionBar.vue';
import AutoComplete from '@/components/AutoComplete.vue';
import BackButton from '@/components/BackButton.vue';
import ErrorAlert from '@/components/ErrorAlert.vue';
import FileHeader from '@/components/FileHeader.vue';
import GridView from '@/components/GridView.vue';
import ObjectSelector from '@/components/ObjectSelector.vue';
import OpenFile from '@/components/OpenFile.vue';
import OpenInBrowser from '@/components/OpenInBrowser.vue';
import PageLoading from '@/components/PageLoading.vue';
import ProjectContainer from '@/components/ProjectContainer.vue';
import ReferencePopup from '@/components/ReferencePopup.vue';
import SelectFolderInput from '@/components/SelectFolderInput.vue';
import SelectFileInput from '@/components/SelectFileInput.vue';
import StackTraceError from '@/components/StackTraceError.vue';
import SuccessAlert from '@/components/SuccessAlert.vue';

import type { App } from 'vue'

export function registerPlugins(app: App) {
	library.add(fas, far, fab);
    app
        .use(vuetify)
        .use(router)
        .use(pinia)
		.component('font-awesome-icon', FontAwesomeIcon)
		.component('font-awesome-layers', FontAwesomeLayers)
		.component('font-awesome-layers-text', FontAwesomeLayersText)
		.component('action-bar', ActionBar)
		.component('auto-complete', AutoComplete)
		.component('back-button', BackButton)
		.component('error-alert', ErrorAlert)
		.component('file-header', FileHeader)
		.component('grid-view', GridView)
		.component('object-selector', ObjectSelector)
		.component('open-file', OpenFile)
		.component('open-in-browser', OpenInBrowser)
		.component('page-loading', PageLoading)
		.component('project-container', ProjectContainer)
		.component('reference-popup', ReferencePopup)
		.component('select-folder-input', SelectFolderInput)
		.component('select-file-input', SelectFileInput)
		.component('stack-trace-error', StackTraceError)
		.component('success-alert', SuccessAlert)
		// @ts-ignore
		.use(HighchartsVue);

	Highcharts.setOptions({
		chart: {
			style: {
				fontFamily: '"Roboto", sans-serif'
			}
		},
		lang: {
			thousandsSep: '\u002c'
		},
		title: {
			style: {
				fontSize: '16px',
				fontWeight: 'bold'
			}
		}
	});
	HighchartsMore(Highcharts);
	accessibilityInit(Highcharts);
	exportingInit(Highcharts);
	exportDataInit(Highcharts);
	offlineExportInit(Highcharts);
}