import {app, BrowserWindow, ipcMain, session, Menu, dialog, shell} from 'electron';
import child_process from 'child_process';
import {join} from 'path';
import fs from 'fs';

import windowStateKeeper from 'electron-window-state';
import parseArgs from 'electron-args';
import Store from 'electron-store';
import kill from 'tree-kill';

const store = new Store();
let DEV_MODE = process.env.NODE_ENV === 'development';
let mainWindow:BrowserWindow;
let pids:any = [];

const cli = parseArgs(`
		swatcheck
 
		Usage
			$ swatcheck [path_to_project]
 
		Options
			--help                      show help
			--version                   show version
 
		Examples
			$ swatcheck path/to/project
`, {
		alias: {
			h: 'help'
		}
});
global.project_path = !DEV_MODE ? cli.input[0] : null;

let appsettings = require(join(app.getAppPath(), 'static/appsettings.json').replace('app.asar', 'app.asar.unpacked'));

const getApiPath = () => {
	let exeName = 'SWAT.Check.exe';

	if (DEV_MODE) {
		return join(app.getAppPath(), '..', '..', 'src', 'api', 'bin', 'Debug', 'net7.0', exeName)
	} else {
		return join(app.getAppPath(), 'static', 'api_dist', exeName).replace('app.asar', 'app.asar.unpacked')
	}
}

function createWindow () {
	let mainWindowState = windowStateKeeper({
		defaultWidth: 1200,
		defaultHeight: 800
	});

	mainWindow = new BrowserWindow({
		width: mainWindowState.width, 
		height: mainWindowState.height,
		x: mainWindowState.x,
		y: mainWindowState.y,
		title: 'SWAT Check ' + appsettings.version,
		icon: join(app.getAppPath(), 'static/256x256.png'),
		webPreferences: {
			preload: join(__dirname, 'preload.js'),
			nodeIntegration: false,
			contextIsolation: true,
		}
	});

	mainWindowState.manage(mainWindow);

	if (process.env.NODE_ENV === 'development') {
		const rendererPort = process.argv[2];
		mainWindow.loadURL(`http://localhost:${rendererPort}`);
	}
	else {
		mainWindow.loadFile(join(app.getAppPath(), 'renderer', 'index.html'));
	}
}

app.whenReady().then(() => {
	createWindow();

	session.defaultSession.webRequest.onHeadersReceived((details, callback) => {
		callback({
			responseHeaders: {
				...details.responseHeaders,
				'Content-Security-Policy': ['script-src \'self\'']
			}
		})
	})

	app.on('activate', function () {
		// On macOS it's common to re-create a window in the app when the
		// dock icon is clicked and there are no other windows open.
		if (BrowserWindow.getAllWindows().length === 0) {
			createWindow();
		}
	});
});

app.on('window-all-closed', function () {
	if (process.platform !== 'darwin') app.quit()
});

app.on('before-quit', () => {
	for (let pid of pids) {
		if (pid != undefined) {
			try {
				kill(pid);
			} catch(error) {}
		}
	}
});

ipcMain.on('run-api', (event, projectPath:string, readDb:boolean) => {
	let apiPath = getApiPath();
	let skipDbRead = readDb ? '0' : '1';
	
	let ipcProcess = child_process.spawn(apiPath, [projectPath, skipDbRead]);
	pids.push(ipcProcess.pid);
	let stderrChunks = [];
	
	ipcProcess.stdout.on('data', (data) => {
		if (DEV_MODE) console.log(`stdout: ${data}`);
		mainWindow.webContents.send('process-stdout', data.toString());
	});

	ipcProcess.stderr.on('data', (data) => {
		if (DEV_MODE) console.log(`stderr: ${data}`);
		mainWindow.webContents.send('process-stderr', data.toString());
	});
	
	ipcProcess.on('close', (code) => {
		mainWindow.webContents.send('process-close', code);
	});

	event.returnValue = ipcProcess.pid;
})

ipcMain.on('kill-process', (event, pid) => {
	console.log('Killing process: ' + pid);
	if (pid != undefined) {
		try {
			kill(pid);
		} catch(error) { console.log('Error killing process: ' + error) }
	}
})

ipcMain.on('globals', (event, arg) => {
	event.returnValue = {
		dev_mode: DEV_MODE,
		platform: process.platform,
		project_path: global.project_path,
		version: appsettings.version
	};
})

ipcMain.on('quit-app', (event, arg) => {
	app.quit();
})

ipcMain.on('open-file-on-system', (event, file) => {
	shell.openPath(file);
})

ipcMain.on('open-url', (event, url) => {
	shell.openExternal(url);
})

ipcMain.on('open-file-dialog', (event, options) => {
	event.returnValue = dialog.showOpenDialogSync(mainWindow, options);
})

ipcMain.on('set-window-title', (event, message:string) => {
	mainWindow.setTitle(message);
})

ipcMain.on('read-swatcheck', (event, projectPath:string) => {
	const data = fs.readFileSync(join(projectPath, 'SWATCheck.json'), 'utf8');
	//console.log(data);
	event.returnValue = data;
})

//Set Menu
const template: Electron.MenuItemConstructorOptions[] = [
	{
		label: 'File',
		submenu: [
			{role: 'quit'}
		]
	},
	{
		label: 'Edit',
		submenu: [
			{role: 'undo'},
			{role: 'redo'},
			{type: 'separator'},
			{role: 'cut'},
			{role: 'copy'},
			{role: 'paste'}
		]
	},
	{
		label: 'View',
		submenu: [
			{role: 'toggleDevTools'},
			{type: 'separator'},
			{role: 'resetZoom'},
			{role: 'zoomIn'},
			{role: 'zoomOut'},
			{type: 'separator'},
			{role: 'togglefullscreen'},
			{role: 'minimize'},
			{role: 'forceReload'}
		]
	},
	{
		role: 'help',
		submenu: [
			{
				label: 'SWAT Check Information',
				click () { shell.openExternal('https://swat.tamu.edu/software/swat-check/') }
			},
			{
				label: 'SWAT Website',
				click () { shell.openExternal('https://swat.tamu.edu') }
			},
			{type: 'separator'},
			{
				label: 'Report a model error',
				click () { shell.openExternal('https://groups.google.com/g/swatuser') }
			}
		]
	}
];

const menu = Menu.buildFromTemplate(template);
Menu.setApplicationMenu(menu);