import { defineStore } from 'pinia';
import {useCurrentProject} from '@/store/currentProject';
import { useTaskStore } from '@/store/task';




export const useShpGeoJsonStore = defineStore('shpgeojson', () => {


    async function exportGeoJson() {
        const currentProject = useCurrentProject();
        const taskStore = useTaskStore();


        const dbPath = currentProject.projectDb;
        

        if (!dbPath) {
            console.error("Path database tidak ditemukan (null)");
            return;
        }

        const normalizedPath = dbPath.replace(/\//g, '\\');
        const projectFolder = window.electronApi.pathDirectoryName(normalizedPath);

        // Path file
        const shpPath = window.electronApi.joinPaths([projectFolder, 'Watershed', 'Shapes', 'subs1.shp']);
        const jsonPath = window.electronApi.joinPaths([projectFolder, 'geojson_data', 'subs1.geojson']);

        if (!window.electronApi.pathExists(shpPath)) {
            console.error("File SHP tidak ditemukan di:", shpPath);
            throw new Error("File SHP sumber tidak ditemukan.");
        }

        const args = [
            'sync_geojson',
            `--shapefile_path=${shpPath}`,
            `--geojson_path=${jsonPath}`
        ];

        try {
            console.log("Triggering task sync_geojson ke backend...");
            // Asumsi taskStore.runTask menerima args dan project state
            await taskStore.runTask(args, currentProject.getObject());
            console.log("Task berhasil di-trigger.");
        } catch (err) {
            console.error("FATAL ERROR pada taskStore.runTask:", err);
            throw err; // Lempar balik agar UI bisa menangani error
        }
    }



    // async function bulkExportGeoJson() {
    //     const currentProject = useCurrentProject();
    //     const taskStore = useTaskStore();
    //     const dbPath = currentProject.projectDb;
    
    //     if (!dbPath) return;

    //     const projectFolder = window.electronApi.pathDirectoryName(dbPath.replace(/\//g, '\\'));
    
    //     const shapesDir = window.electronApi.joinPaths([projectFolder, 'Watershed', 'Shapes']);
    //     const outputDir = window.electronApi.joinPaths([projectFolder, 'geojson_data']);

    //     // Argumen untuk fungsi bulk
    //     const args = [
    //         'bulk_sync_geojson', // Nama aksi baru di backend
    //         `--shapes_dir=${shapesDir}`,
    //         `--output_dir=${outputDir}`
    //     ];
    //     // Gunakan 'bulk-converter' sebagai proc_name agar sinkron dengan setup.vue
    //     const procName = 'bulk-converter';

    //     try {
    //         // Kita menggunakan spawnProcess langsung jika taskStore tidak mendukung progress tracking
    //         // Jika taskStore sudah membungkus spawnProcess, Anda harus menyesuaikan taskStore tersebut.
    //         // Di sini kita gunakan cara langsung yang sudah terdaftar di preload.js Anda:
    //         // window.electronApi.spawnProcess(procName, 'shpgeojson', args);
    //         await taskStore.runGenericTask('bulk-converter', 'shpgeojson', args, currentProject.getObject());
    //     } catch (err) {
    //         throw err;
    //     }
    // }

        return { exportGeoJson };


});