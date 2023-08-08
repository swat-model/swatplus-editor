import { useErrorHandling } from './errorHandling';
import { useFormatters } from './formatters';
import { useUtilities } from './utilities';

export function useRunProcess() {
	const electron = window.electronApi;
	const errors = useErrorHandling();
	const formatters = useFormatters();
	const utilities = useUtilities();

	function runApiProc(script_name:string, args:string[]) {
		errors.log("starting process");
		return electron.spawnProcess(script_name, args);
	}
	
	function runSwatProc(inputDir:string, debug:boolean) {
		return electron.runSwat(debug, inputDir);
	}
	
	const processStdout = (callback:any) => electron.processStdout(callback);
	const processStderr = (callback:any) => electron.processStderr(callback);
	const processClose = (callback:any) => electron.processClose(callback);

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

	return {
		runApiProc,
		runSwatProc,
		processStdout,
		processStderr,
		processClose,
		killProcess,
		getApiOutput,
		resultsPath,
		outputDbPath
	}
}