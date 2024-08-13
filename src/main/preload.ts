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

	spawnProcess: (proc_name:string, script_name:string, args:string[]) => { return ipcRenderer.sendSync('spawn-process', proc_name, script_name, args) },
	processStdout: (proc_name:string, callback:(data:any) => any) => {
		let channel = `process-stdout-${proc_name}`;
		const subscription = (_event:any, data:any) => callback(data);
		ipcRenderer.on(channel, subscription);
		return () => {
			ipcRenderer.removeListener(channel, subscription);
		}
	},
	processStderr: (proc_name:string, callback:(data:any) => any) => {
		let channel = `process-stderr-${proc_name}`;
		const subscription = (_event:any, data:any) => callback(data);
		ipcRenderer.on(channel, subscription);
		return () => {
			ipcRenderer.removeListener(channel, subscription);
		}
	},
	processClose: (proc_name:string, callback:(code:any) => any) => {
		let channel = `process-close-${proc_name}`;
		const subscription = (_event:any, code:any) => callback(code);
		ipcRenderer.on(channel, subscription);
		return () => {
			ipcRenderer.removeListener(channel, subscription);
		}
	},
	//processStderr: (proc_name:string, callback:(_event:any, data:any) => any) => ipcRenderer.on(`process-stderr-${proc_name}`, (_event:any, code:any) => callback(_event, code)),
	//processClose: (proc_name:string, callback:(_event:any, data:any) => any) => ipcRenderer.on(`process-close-${proc_name}`, (_event:any, code:any) => callback(_event, code)),
	killProcess: (pid:any) => ipcRenderer.send('kill-process', pid),
	runSwat: (debug:boolean, inputDir:string) => {return ipcRenderer.sendSync('run-swat', debug, inputDir) },
	getSwatPlusToolboxPath: () => {return ipcRenderer.sendSync('get-swatplustoolbox-path') },
	launchSwatPlusToolbox: (projectDb:string) => {return ipcRenderer.sendSync('launch-swatplustoolbox', projectDb) },
	setColorTheme: (colorTheme:string) => {return ipcRenderer.send('set-color-theme', colorTheme) },
	getColorTheme: () => {return ipcRenderer.sendSync('get-color-theme') },

	loadFromContextMenu: (callback:(data:any) => any) => {
		let channel = `load-from-context-menu`;
		const subscription = (_event:any, data:any) => callback(data);
		ipcRenderer.on(channel, subscription);
		return () => {
			ipcRenderer.removeListener(channel, subscription);
		}
	},

	//Auto update
	appUpdateStatus: (callback:(data:any) => any) => {
		let channel = `app-update-status`;
		const subscription = (_event:any, data:any) => callback(data);
		ipcRenderer.on(channel, subscription);
		return () => {
			ipcRenderer.removeListener(channel, subscription);
		}
	},
	appUpdateDownloading: (callback:(data:any) => any) => {
		let channel = `app-update-downloading`;
		const subscription = (_event:any, data:any) => callback(data);
		ipcRenderer.on(channel, subscription);
		return () => {
			ipcRenderer.removeListener(channel, subscription);
		}
	},
	appUpdateDownloaded: (callback:(data:any) => any) => {
		let channel = `app-update-downloaded`;
		const subscription = (_event:any, data:any) => callback(data);
		ipcRenderer.on(channel, subscription);
		return () => {
			ipcRenderer.removeListener(channel, subscription);
		}
	},
	downloadUpdate: () => ipcRenderer.send('download-update', ''),
	quitAndInstallUpdate: () => ipcRenderer.send('quit-and-install-update', ''),
})
