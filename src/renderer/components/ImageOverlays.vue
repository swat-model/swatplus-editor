<script setup lang="ts">
    import { reactive, ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue';
	import { useTheme, useDisplay } from 'vuetify';
    import { useHelpers } from '@/helpers';

    const theme = useTheme();
    const display = useDisplay();
    const { api, constants, errors, formatters, runProcess, utilities, currentProject } = useHelpers();

    const containerRef = ref<HTMLDivElement | null>(null);

    interface Props {
		imagePath: string,
		darkImagePath?: string,
		imageRatio: number,
        overlays: Array<{ x: number, y: number, slot: string, calculatedLeft?: string, calculatedTop?: string }>,
        class?: string,
        id?: string,
	}

	const props = withDefaults(defineProps<Props>(), {
		imagePath: '',
		darkImagePath: '',
		imageRatio: 16/9,
        overlays: () => [],
        class: '',
        id: '',
	});

    interface Position {
        left: string;
        top: string;
    }

    const overlayPositions = ref<Position[]>([]);

    const currentImage = computed(() => {
        if (formatters.isNullOrEmpty(props.darkImagePath)) return props.imagePath;
        return isDark.value ? props.darkImagePath : props.imagePath;
    });

    const isDark = computed(() => {
        return theme.global.name.value === 'dark';
    });

    const positionOverlays = () => {
        if (!containerRef.value) return;

        const container = containerRef.value;
        const containerRatio = container.offsetWidth / container.offsetHeight;
        const imageRatio = props.imageRatio;

        const newPositions: Position[] = props.overlays.map((overlay:any) => {
            let left: number;
            let top: number;

            if (containerRatio > imageRatio) {
                left = overlay.x * 100;
                const visibleHeight: number = container.offsetWidth / imageRatio;
                const offset: number = (container.offsetHeight - visibleHeight) / 2;
                top = (overlay.y * visibleHeight + offset) / container.offsetHeight * 100;
            } else {
                top = overlay.y * 100;
                const visibleWidth: number = container.offsetHeight * imageRatio;
                const offset: number = (container.offsetWidth - visibleWidth) / 2;
                left = (overlay.x * visibleWidth + offset) / container.offsetWidth * 100;
            }

            return {
                left: `${left}%`,
                top: `${top}%`
            };
        });

        overlayPositions.value = newPositions;
    };

    watch(() => theme.global.name.value, () => {
        nextTick(positionOverlays);
    });

    watch(() => [props.imagePath, props.darkImagePath], () => {
        nextTick(positionOverlays);
    });

    watch(() => props.overlays, () => {
        nextTick(positionOverlays);
    }, { deep: true });

    onMounted(async () => {
        await nextTick();
        positionOverlays();
        window.addEventListener('resize', positionOverlays);
    });

    onUnmounted(() => {
        window.removeEventListener('resize', positionOverlays);
    });
</script>

<template>
    <div ref="containerRef" :class="`image-overlay-container ${props.class}`" :id="props.id" :style="{ backgroundImage: `url(${utilities.publicPath}${currentImage})` }">
        <slot name="mainContent"></slot>
        <div v-for="(overlay, index) in props.overlays" 
            :key="`${isDark ? 'dark' : 'light'}-${index}`" 
            class="text-overlay" 
            :style="{
                '--overlay-left': overlayPositions[index]?.left || '0%',
                '--overlay-top': overlayPositions[index]?.top || '0%'
            }">
            <slot :name="overlay.slot || `overlay-${index}`"></slot>
        </div>
    </div>
</template>

<style lang="scss" scoped>
    .image-overlay-container {
        position: relative;
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;

        .text-overlay {
            position: absolute;
            left: var(--overlay-left);
            top: var(--overlay-top);
            z-index: 350;
            font-size: 0.9rem;
            font-weight: bold;
            text-shadow: 0px 0px 8px rgba(var(--v-theme-surface), 1);
        }
    }
</style>