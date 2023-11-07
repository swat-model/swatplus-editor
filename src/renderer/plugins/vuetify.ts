/**
 * plugins/vuetify.ts
 *
 * Framework documentation: https://vuetifyjs.com`
 */

// Styles
import 'vuetify/styles'
import '../app.scss'

// Composables
import { createVuetify } from 'vuetify'
import { aliases, fa } from 'vuetify/iconsets/fa-svg'

// https://vuetifyjs.com/en/introduction/why-vuetify/#feature-guides
export default createVuetify({
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
})
