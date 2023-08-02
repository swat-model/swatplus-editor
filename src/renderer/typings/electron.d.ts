/**
 * Should match main/preload.ts for typescript support in renderer
 */
export default interface ElectronApi {
	runApi: (projectPath:string, readDb:boolean) => any,
	processStdout: (callback:any) => void,
	processStderr: (callback:any) => void,
	processClose: (callback:any) => void,
	killProcess: (pid:any) => void,
	getGlobals: () => any,
	quitApp: () => void,
	openFileOnSystem: (key:string) => void,
	openUrl: (key:string) => void,
	openFileDialog: (options:any) => string[],
	setWindowTitle: (message: string) => void,
	readSwatCheck: (projectPath:string) => any
}

declare global {
	interface Window {
		electronApi: ElectronApi,
	}
}
