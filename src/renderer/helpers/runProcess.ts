import { useErrorHandling } from './errorHandling';
import { useFormatters } from './formatters';
import { useUtilities } from './utilities';

export function useRunProcess() {
	const electron = window.electronApi;
	const errors = useErrorHandling();
	const formatters = useFormatters();
	const utilities = useUtilities();

	function runApiProc(proc_name:string, script_name:string, args:string[]) {
		return electron.spawnProcess(proc_name, script_name, args);
	}
	
	function runSwatProc(inputDir:string, debug:boolean) {
		return electron.runSwat(debug, inputDir);
	}
	
	const processStdout = (proc_name:string, callback:(_event:any, data:any) => any) => electron.processStdout(proc_name, callback);
	const processStderr = (proc_name:string, callback:(_event:any, data:any) => any) => electron.processStderr(proc_name, callback);
	const processClose = (proc_name:string, callback:(_event:any, code:any) => any) => electron.processClose(proc_name, callback);

	function killProcess(pid:any) {
		electron.killProcess(pid);
	}

	function getApiOutput(data:any) {
		try {
			return JSON.parse(data);
		} catch (error) {
			return data;
		}
	}

	function resultsPath(inputDir:any) {
		if (formatters.isNullOrEmpty(inputDir)) return '';
		let d = inputDir.replace(/\\/g,"/");
		let resultsPath = electron.joinPaths([d, '../', 'Results']);

		if (!utilities.pathExists(resultsPath))
			resultsPath = inputDir;

		return resultsPath;
	}

	function outputDbPath(inputDir:string) {
		return electron.joinPaths([resultsPath(inputDir), 'swatplus_output.sqlite']);
	}

	const appUpdateStatus = (callback:(_event:any, data:any) => any) => electron.appUpdateStatus(callback);
	const appUpdateDownloading = (callback:(_event:any, data:any) => any) => electron.appUpdateDownloading(callback);
	const appUpdateDownloaded = (callback:(_event:any, data:any) => any) => electron.appUpdateDownloaded(callback);

	function downloadUpdate() {
		electron.downloadUpdate();
	}

	function quitAndInstallUpdate() {
		electron.quitAndInstallUpdate();
	}

	return {
		runApiProc,
		runSwatProc,
		processStdout,
		processStderr,
		processClose,
		killProcess,
		getApiOutput,
		resultsPath,
		outputDbPath,
		appUpdateStatus,
		appUpdateDownloading,
		appUpdateDownloaded,
		downloadUpdate,
		quitAndInstallUpdate
	}
}