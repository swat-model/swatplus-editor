import { ElectronAppSettings, ElectronGlobals } from ".";

/**
 * Should match main/preload.ts for typescript support in renderer
 */
export default interface ElectronApi {
	sendMessage: (message: string) => void,
	setWindowTitle: (message: string) => void,
	getGlobals: () => ElectronGlobals,
	getAppSettings: () => ElectronAppSettings,
	addToStore: (key: string, value:any) => void,
	getStoreSetting: (key:string) => any,
	deleteFromStore: (key:string) => void,
	getAppPath: () => string,
	quitApp: () => void,
	pathExists: (directory:string) => boolean,
	joinPaths: (paths:string[]) => string,
	pathDirectoryName: (directory:string) => string,
	openFileOnSystem: (key:string) => void,
	openUrl: (key:string) => void,
	openFileDialog: (options:any) => string[],
	saveFileDialog: (options:any) => string[],
	spawnProcess: (proc_name:string, script_name:string, args:string[]) => any,
	processStdout: (proc_name:string, callback:any) => void,
	processStderr: (proc_name:string, callback:any) => void,
	processClose: (proc_name:string, callback:any) => void,
	killProcess: (pid:any) => void,
	runSwat: (debug:boolean, inputDir:string) => any,
	getSwatPlusToolboxPath: () => string,
	launchSwatPlusToolbox: (projectDb:string) => string,
	getIahrisPath: () => string,
	launchIahris: (scenariosPath:string) => string,
	setColorTheme: (colorTheme:string) => void,
	getColorTheme: () => string,
	loadFromContextMenu: (callback:any) => void,
	appUpdateStatus: (callback:any) => void,
	appUpdateDownloading: (callback:any) => void,
	appUpdateDownloaded: (callback:any) => void,
	downloadUpdate: () => void,
	quitAndInstallUpdate: () => void,
	manualUpdateCheck: () => void,
}

declare global {
	interface Window {
		electronApi: ElectronApi,
	}
}
