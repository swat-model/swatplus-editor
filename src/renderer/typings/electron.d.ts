import { ElectronAppSettings, ElectronGlobals } from ".";

/**
 * Should match main/preload.ts for typescript support in renderer
 */
export default interface ElectronApi {
	//Komunikasi Dasar
	sendMessage: (message: string) => void;
	setWindowTitle: (message: string) => void;
	getGlobals: () => ElectronGlobals;
	getAppSettings: () => ElectronAppSettings;

	//Store Manajemen	
	addToStore: (key: string, value:any) => void;
	getStoreSetting: (key:string) => any;
	deleteFromStore: (key:string) => void;

	//File System
	getAppPath: () => string;
	quitApp: () => void;
	pathExists: (directory:string) => boolean;
	joinPaths: (paths:string[]) => string;
	pathDirectoryName: (directory:string) => string;
	readDirectory: (dirPath: string) => string[];
	readFile: (filePath: string) => string;
	openFileOnSystem: (key:string) => void;
	openUrl: (key:string) => void;
	openFileDialog: (options:any) => string[];
	saveFileDialog: (options:any) => string[];

	//Process Control
	spawnProcess: (proc_name:string, script_name:string, args:string[]) => any;
	processStdout: (proc_name:string, callback:any) => void;
	processStderr: (proc_name:string, callback:any) => void;
	processClose: (proc_name:string, callback:any) => void;
	killProcess: (pid:any) => void;

	//Swat+ spesifik
	runSwat: (inputDir:string, modelExe:string) => any;
	getSwatExeOptions: () => Promise<any>;
	getSwatPlusToolboxPath: () => string;
	launchSwatPlusToolbox: (projectDb:string) => string;
	getIahrisPath: () => string;
	launchIahris: (scenariosPath:string) => string;

	//UI & Theme
	setColorTheme: (colorTheme:string) => void;
	getColorTheme: () => string;
	loadFromContextMenu: (callback: (data: any) => void) => () => void;

	//Auto Update
	appUpdateStatus: (callback: (data: any) => void) => () => void;
	appUpdateDownloading: (callback: (data: any) => void) => () => void;
	appUpdateDownloaded: (callback: (data: any) => void) => void;
	downloadUpdate: () => void;
	quitAndInstallUpdate: () => void;
	manualUpdateCheck: () => void;
}

declare global {
	interface Window {
		electronApi: ElectronApi;
	}
}

