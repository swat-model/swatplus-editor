<script setup lang="ts">
    import { ref, watch, computed } from 'vue';
    import { useTheme } from 'vuetify'; // 1. Import useTheme
    import { parseIklimContent } from '@/helpers/iklim_parse';

    const electron = (window as any).electronApi;
    const theme = useTheme(); // 2. Inisialisasi theme

    const props = defineProps<{ show: boolean, filePath: string, fileName: string, fileType: string }>();
    const emit = defineEmits(['update:show']);
    const internalShow = ref(props.show);
    const loaded = ref(false);
    const rawData = ref<any>(null); // Simpan data mentah agar bisa dihitung ulang


    const dialogTitle = computed(() => {
        const titles: Record<string, string> = {
        pcp: 'Data Curah Hujan (PCP) Stasiun',
        slr: 'Data Radiasi Matahari (SLR) Stasiun',
        wnd: 'Data Kecepatan Angin (WND) Stasiun',
        hmd: 'Data Kelembaban Udara (HMD) Stasiun',
        tem: 'Data Suhu (TEM) Stasiun'
        };
        return titles[props.fileType] || 'Data Iklim';
    });

    const chartOptions = computed(() => {
        // Pastikan data valid
        if (!rawData.value || !rawData.value.values || rawData.value.values.length === 0) return {};

        const rawValues = JSON.parse(JSON.stringify(rawData.value.values));
        const rawLabels = JSON.parse(JSON.stringify(rawData.value.labels));
        
        const isDark = theme.global.current.value.dark;
        const textColor = isDark ? '#FFFFFF' : '#333333';
        const bgColor = isDark ? '#333333' : '#FFFFFF';

        const yAxisLabels: Record<string, string> = {
            pcp: 'Curah Hujan (mm/hari)',
            slr: 'Radiasi Matahari (Mj/m²/hari)',
            wnd: 'Kecepatan Angin (m/s)',
            hmd: 'Kelembaban Udara Relatif',
            tem: 'Temperature (°C)'
        };
        const labelTitle = yAxisLabels[props.fileType] || 'Value';

        const datetimeLabels = rawLabels.map((label: string) => {
        const [doy, year] = label.split('-').map(Number);
        return doyToTimestamp(doy, year);
        });

        const processedSeries = props.fileType === 'tem' 
            ? rawValues // Jika .tem, ambil semua (T-Max dan T-Min)
            : rawValues.slice(0, 1); // Jika bukan .tem, HANYA ambil baris pertama (index 0)

        return {
            time:{
                useUTC: true
            },
            chart: { 
                type: 'line', 
                backgroundColor: 'transparent', 
                height: 400, 
                animation: false,
                styledMode: false,
                // scrollbar: {
                //     enabled: true,
                //     showFull: false
                // },
                zoomType:'x',
                panning: {
                    enabled: true,
                    type: 'x'
                },
                panKey: 'shift',
                
            },
            title: { 
                text: null, 
                style: { 
                    color: textColor 
                } 
            },
            legend: {
                enabled: false
            },
            tooltip: { 
                xDateFormat: '%e %b %Y',
                shared: true,
                backgroundColor: bgColor, 
                borderColor: textColor, 
                style: { 
                    color: textColor 
                } 
            },
            xAxis: { 
                // categories: rawLabels, 
                type: 'datetime',
                labels: { 
                    format: '{value:%e %b %Y}',
                    style: { 
                        color: textColor 
                    } 
                },
                gridLineWidth: 1,
                // gridLineColor: isDark ? '#444444' : '#E0E0E0',
                gridLineColor: '#FF0000',
                gridZIndex: 4,
                gridLineDashStyle: 'Solid'
            },
            yAxis: {
                // gridLineWidth: 1,
                // gridLineColor: isDark ? '#444444' : '#E0E0E0',
                // gridZIndex: 4,
                title: { 
                    text: labelTitle,
                    style: { color: textColor, fontWeight:'bold', fontSize:'14px' } 
                },
                labels: { style: { color: textColor, fontWeight:'bold' } }
            },

            series: processedSeries.map((data: number[], index: number) => ({
                name: props.fileType === 'tem' ? (index === 0 ? 'T-Max' : 'T-Min') : 'Data',
                color: props.fileType === 'tem' ? (index === 0 ? '#FF5722' : '#2196F3') : '#4CAF50',
                data: data.map((val, i) => [datetimeLabels[i], val]),
                connectNulls: true
            }))
        };
    });

    function doyToTimestamp(doy: number, year: number): number {
        // Membuat tanggal dari tahun dan hari ke-doy
        // const date = new Date(year, 0); // 0 = Januari
        // date.setDate(doy); // Menambah hari ke tanggal 1 Januari
        // return date.getTime(); // Mengembalikan milidetik
        return Date.UTC(year, 0, doy);
    }
    function formatDate(timestamp: number): string {
        const date = new Date(timestamp);
        const year = date.getUTCFullYear();
        const month = String(date.getUTCMonth() + 1).padStart(2, '0'); // +1 karena bulan dimulai dari 0
        const day = String(date.getUTCDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    }

    watch(() => [props.show, props.filePath], ([newShow, newPath]) => {
        internalShow.value = newShow as boolean;
        // console.log("File Type yang diterima:", props.fileType);
        // Jika dialog terbuka dan path valid
        if (newShow && newPath) {
            try {
                const content = electron.readFile(newPath as string);
                if (content) {
                    // Gunakan props.fileType terbaru
                    const parsedData = parseIklimContent(content, props.fileType);
                    rawData.value = parsedData;
                    loaded.value = true;
                }
            } catch (err) {
                console.error("Gagal membaca file:", err);
            }
        }
        }, { immediate: true }
    );

    watch(internalShow, (newVal) => {
        emit('update:show', newVal);
    });
</script>

<template>
  <v-dialog v-model="internalShow" width="95%" max-width="1500px" v-if="props.show" scrollable persistent transition="dialog-transition">
    <v-card>
        <v-card-title >
        {{ dialogTitle }}: {{ props.fileName }}
        </v-card-title>

        <v-card-text >
            <div v-if="loaded" style="width: 100%; height: 100%;">
                <highcharts :key="loaded ? 'rendered' : 'loading'" :options="chartOptions"></highcharts>
            </div>
            <div v-else class="d-flex justify-center align-center" style="height: 100%;">
                <v-progress-circular indeterminate color="primary"></v-progress-circular>
            </div>
        </v-card-text>

        <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="primary" variant="text" @click="internalShow = false">Tutup</v-btn>
        </v-card-actions>
    </v-card>
  </v-dialog>
</template>