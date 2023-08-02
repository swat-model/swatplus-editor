import {contextBridge, ipcRenderer} from 'electron';

contextBridge.exposeInMainWorld('electronApi', {
	runApi: (projectPath:string, readDb:boolean) => {return ipcRenderer.sendSync('run-api', projectPath, readDb) },
	processStdout: (callback:any) => ipcRenderer.on('process-stdout', callback),
	processStderr: (callback:any) => ipcRenderer.on('process-stderr', callback),
	processClose: (callback:any) => ipcRenderer.on('process-close', callback),
	killProcess: (pid:any) => ipcRenderer.send('kill-process', pid),
	getGlobals: () => { return ipcRenderer.sendSync('globals', '') },
	quitApp: () => ipcRenderer.send('quit-app', ''),
	openFileOnSystem: (key:string) => ipcRenderer.send('open-file-on-system', key),
	openUrl: (key:string) => ipcRenderer.send('open-url', key),
	openFileDialog: (options:any) => { return ipcRenderer.sendSync('open-file-dialog', options) },
	setWindowTitle: (message:string) => ipcRenderer.send('set-window-title', message),
	readSwatCheck: (projectPath:string) => {return ipcRenderer.sendSync('read-swatcheck', projectPath) },
	setColorTheme: (colorTheme:string) => {return ipcRenderer.send('set-color-theme', colorTheme) }
})
