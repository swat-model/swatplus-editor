// Components
import App from './App.vue'

// Composables
import { createApp } from 'vue'
// import { createPinia } from 'pinia'
import pinia from '@/store'

// Plugins
import { registerPlugins } from '@/plugins'

const app = createApp(App)

app.use(pinia)

registerPlugins(app)

app.mount('#app')