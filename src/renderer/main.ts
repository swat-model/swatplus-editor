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
import OpenFile from './components/OpenFile.vue';
import OpenInBrowser from './components/OpenInBrowser.vue';
import PageLoading from './components/PageLoading.vue';

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
					primary: '#0068C1'
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
app.component('open-file', OpenFile);
app.component('open-in-browser', OpenInBrowser);
app.component('page-loading', PageLoading);

app.use(router);
app.use(pinia);
app.use(vuetify);
app.mount('#app');
