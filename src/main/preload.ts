import {contextBridge, ipcRenderer} from 'electron';

contextBridge.exposeInMainWorld('electronApi', {
	sendMessage: (message:string) => ipcRenderer.send('message', message),
	setWindowTitle: (message:string) => ipcRenderer.send('set-window-title', message),
	getGlobals: () => { return ipcRenderer.sendSync('globals', '') },
	getAppSettings: () => { return ipcRenderer.sendSync('get-app-settings', '') },
	addToStore: (key: string, value:any) => ipcRenderer.send('add-to-store', key, value),
	getStoreSetting: (key:string) => { return ipcRenderer.sendSync('get-store-setting', key) },
	deleteFromStore: (key:string) => ipcRenderer.send('delete-from-store', key),
	getAppPath: () => { return ipcRenderer.sendSync('get-app-path', '') },
	quitApp: () => ipcRenderer.send('quit-app', ''),

	pathExists: (directory:string) => { return ipcRenderer.sendSync('path-exists', directory) },
	joinPaths: (paths:string[]) => { return ipcRenderer.sendSync('join-paths', paths) },
	pathDirectoryName: (directory:string) => { return ipcRenderer.sendSync('path-directory-name', directory) },

	openFileOnSystem: (key:string) => ipcRenderer.send('open-file-on-system', key),
	openUrl: (key:string) => ipcRenderer.send('open-url', key),
	openFileDialog: (options:any) => { return ipcRenderer.sendSync('open-file-dialog', options) },
	saveFileDialog: (options:any) => { return ipcRenderer.sendSync('save-file-dialog', options) },

	spawnProcess: (script_name:string, args:string[]) => { return ipcRenderer.sendSync('spawn-process', script_name, args) },
	processStdout: (callback:any) => ipcRenderer.on('process-stdout', callback),
	processStderr: (callback:any) => ipcRenderer.on('process-stderr', callback),
	processClose: (callback:any) => ipcRenderer.on('process-close', callback),
	killProcess: (pid:any) => ipcRenderer.send('kill-process', pid),
	runSwat: (debug:boolean, inputDir:string) => {return ipcRenderer.sendSync('run-swat', debug, inputDir) },
	getSwatPlusToolboxPath: () => {return ipcRenderer.sendSync('get-swatplustoolbox-path') },
	launchSwatPlusToolbox: (projectDb:string) => {return ipcRenderer.sendSync('launch-swatplustoolbox', projectDb) },
	setColorTheme: (colorTheme:string) => {return ipcRenderer.send('set-color-theme', colorTheme) },
	getColorTheme: () => {return ipcRenderer.sendSync('get-color-theme') }
})
