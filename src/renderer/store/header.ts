import { defineStore } from 'pinia';

export const useHeaderStore = defineStore('header', {
    state: () => ({
        headerImage: 'default.png', // Gambar default
        title: 'SWAT+ Editor'
    }),
    actions: {
        setHeader(image: string, title: string) {
            this.headerImage = image;
            this.title = title;
        }
    }
})