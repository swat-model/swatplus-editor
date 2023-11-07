import path from 'path'
import vue from '@vitejs/plugin-vue'
import vuetify, { transformAssetUrls } from 'vite-plugin-vuetify'

import { defineConfig } from 'vite'
import { fileURLToPath, URL } from 'node:url'

/**
 * https://vitejs.dev/config
 */
const config = defineConfig({
    root: path.join(__dirname, 'src', 'renderer'),
    publicDir: 'public',
    server: {
        port: 8080,
    },
    open: false,
    build: {
        outDir: path.join(__dirname, 'build', 'renderer'),
        emptyOutDir: true,
    },
    plugins: [
        vue({
            template: { transformAssetUrls }
        }),
        // https://github.com/vuetifyjs/vuetify-loader/tree/next/packages/vite-plugin
        vuetify({
            autoImport: true
        }),
    ],
	resolve: {
        alias: {
            '@': path.resolve(__dirname, './src/renderer')
        },
        extensions: [
            '.js',
            '.json',
            '.jsx',
            '.mjs',
            '.ts',
            '.tsx',
            '.vue',
        ],
    }
});

module.exports = config;
