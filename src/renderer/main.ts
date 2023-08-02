import { createApp } from 'vue';
import App from './App.vue';

//Font Awesome
import { library } from '@fortawesome/fontawesome-svg-core';
import { fas } from '@fortawesome/free-solid-svg-icons';
import { far } from '@fortawesome/free-regular-svg-icons';
import { fab } from '@fortawesome/free-brands-svg-icons';
import { FontAwesomeIcon, FontAwesomeLayers, FontAwesomeLayersText } from '@fortawesome/vue-fontawesome';

//Custom Components
import OpenInBrowser from './components/OpenInBrowser.vue';
import BootstrapModal from './components/BootstrapModal.vue';

const app = createApp(App);

//Font Awesome
library.add(fas, far, fab);
app.component('font-awesome-icon', FontAwesomeIcon);
app.component('font-awesome-layers', FontAwesomeLayers);
app.component('font-awesome-layers-text', FontAwesomeLayersText);

//Custom Components
app.component('open-in-browser', OpenInBrowser);
app.component('b-modal', BootstrapModal);

app.mount('#app');
