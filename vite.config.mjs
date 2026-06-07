import path from 'path'
import vue from '@vitejs/plugin-vue'
import vuetify, { transformAssetUrls } from 'vite-plugin-vuetify'

import { defineConfig } from 'vite'
import { fileURLToPath, URL } from 'node:url'

/**
 * https://vitejs.dev/config
 */
export default defineConfig({
    root: path.join(__dirname, 'src', 'renderer'),
    publicDir: 'public',
    server: {
        port: 8080,
        // TAMBAHKAN BLOK PROXY INI:
        proxy: {
            // Jika API Anda di backend dipanggil dengan awalan '/api'
            // atau Anda bisa menyesuaikan path-nya
            '/api': {
                target: 'http://localhost:5001',
                changeOrigin: true,
                secure: false,
                rewrite: (path) => path.replace(/^\/api/, '')
            }
        }
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
