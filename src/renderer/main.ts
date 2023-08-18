import { createApp } from 'vue';
import { createPinia } from 'pinia';
import App from './App.vue';
import router from './router';

//Font Awesome
import { library } from '@fortawesome/fontawesome-svg-core';
import { fas } from '@fortawesome/free-solid-svg-icons';
import { far } from '@fortawesome/free-regular-svg-icons';
import { fab } from '@fortawesome/free-brands-svg-icons';
import { FontAwesomeIcon, FontAwesomeLayers, FontAwesomeLayersText } from '@fortawesome/vue-fontawesome';

// Vuetify
import 'vuetify/styles'
import './app.scss'
import { createVuetify } from 'vuetify';
import * as components from 'vuetify/components';
import * as directives from 'vuetify/directives';
import { aliases, fa } from 'vuetify/iconsets/fa-svg';

//Highcharts
import HighchartsVue from 'highcharts-vue';
import Highcharts from 'highcharts';
import HighchartsMore from 'highcharts/highcharts-more';
import exportingInit from 'highcharts/modules/exporting';
import exportDataInit from 'highcharts/modules/export-data';
import offlineExportInit from 'highcharts/modules/offline-exporting';

//Custom Components
import ActionBar from './components/ActionBar.vue';
import ErrorAlert from './components/ErrorAlert.vue';
import FileHeader from './components/FileHeader.vue';
import GridView from './components/GridView.vue';
import OpenFile from './components/OpenFile.vue';
import OpenInBrowser from './components/OpenInBrowser.vue';
import PageLoading from './components/PageLoading.vue';
import ProjectContainer from './components/ProjectContainer.vue';
import SelectFolderInput from './components/SelectFolderInput.vue';
import SelectFileInput from './components/SelectFileInput.vue';
import StackTraceError from './components/StackTraceError.vue';

const pinia = createPinia();
const app = createApp(App);

//Font Awesome
library.add(fas, far, fab);
app.component('font-awesome-icon', FontAwesomeIcon);
app.component('font-awesome-layers', FontAwesomeLayers);
app.component('font-awesome-layers-text', FontAwesomeLayersText);

//Vuetify
const vuetify = createVuetify({
    components,
    directives,
    icons: {
        defaultSet: 'fa',
        aliases,
        sets: {
            fa,
        },
    },
    theme: {
        themes: {
            dark: {
                dark: true,
                colors: {
                    background: '#031a33',
                    surface: '#092d54',
					primary: '#81D4FA'
                }
            },
			light: {
				colors: {
					primary: '#0068C1',
					secondary: '#607D8B'
				}
			}
        }
    }
});

//Highcharts
// @ts-ignore
app.use(HighchartsVue);
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
exportingInit(Highcharts);
exportDataInit(Highcharts);
offlineExportInit(Highcharts);

//Custom Components
app.component('action-bar', ActionBar);
app.component('error-alert', ErrorAlert);
app.component('file-header', FileHeader);
app.component('grid-view', GridView);
app.component('open-file', OpenFile);
app.component('open-in-browser', OpenInBrowser);
app.component('page-loading', PageLoading);
app.component('project-container', ProjectContainer);
app.component('select-folder-input', SelectFolderInput);
app.component('select-file-input', SelectFileInput);
app.component('stack-trace-error', StackTraceError);

app.use(router);
app.use(pinia);
app.use(vuetify);
app.mount('#app');
