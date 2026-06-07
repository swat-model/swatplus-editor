import { defineStore } from 'pinia';
import { reactive } from 'vue';
import { useHelpers } from '@/helpers';
import { useAppUpdate } from '@/store/appUpdate'; // Import store status Anda

export const useUpdateManager = defineStore('updateManager', () => {
    const { runProcess } = useHelpers();
    const appUpdate = useAppUpdate(); // Akses store status

    const data = reactive({
        task: {
            progress: { percent: 0, message: null },
            isDownloading: false,
            isDownloaded: false,
        }
    });

    // Inisialisasi listener
    const init = () => {
        runProcess.appUpdateDownloading((stdData: any) => {
            data.task.progress = runProcess.getApiOutput(stdData);
        });

        runProcess.appUpdateDownloaded(() => {
            data.task.isDownloaded = true;
            data.task.isDownloading = false;
        });

        runProcess.appUpdateStatus((stdData: any) => {
            let status = runProcess.getApiOutput(stdData);
            appUpdate.setStatus(status.message, status.isAvailable);
        });
    };

    const download = () => {
        data.task.isDownloading = true;
        runProcess.downloadUpdate();
    };

    return { data, init, download };
});