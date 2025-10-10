import {app, BrowserWindow, ipcMain, session, Menu, dialog, shell, nativeTheme} from 'electron';
import {join, dirname} from 'path';
import fs from 'fs';

import windowStateKeeper from 'electron-window-state';
import parseArgs from 'electron-args';
import Store from 'electron-store';
import child_process from 'child_process';
import axios from 'axios';
import portfinder from 'portfinder';
import kill from 'tree-kill';
import { autoUpdater } from 'electron-updater';
autoUpdater.autoDownload = false;

const store = new Store();
let DEV_MODE = process.env.NODE_ENV === 'development';

let pids:any = [];
let pythonProcess: any = null;

const cli = parseArgs(`
		swatpluseditor
 
		Usage
			$ swatpluseditor [path_to_project_database]
 
		Options
			--help                      show help
			--version                   show version
			--cmd-only                  run in command line only mode (all options following are for this mode)
			--weather-dir               full path of weather files location (required if --cmd-only)
			--weather-import-format     weather files import format (plus or old; default plus)
			--weather-save-dir          if weather files import format is old, provide the path to save your plus weather files (defaults to input files directory)
			--wgn-import-method         weather generator import method (database or csv; default database)
			--wgn-db                    full path of wgn database (defaults to default install location)
			--wgn-table                 table name in wgn database (default wgn_cfsr_world)
			--wgn-csv-sta-file          wgn stations csv file, if import method = csv
			--wgn-csv-mon-file          wgn monthly values csv file, if import method = csv
			--year-start                starting year of simulation (defaults to weather files dates)
			--day-start                 starting day of simulation (defaults to weather files dates)
			--year-end                  ending year of simulation (defaults to weather files dates)
			--day-end                   ending day of simulation (defaults to weather files dates)
			--input-files-dir           full path of where to write input files (defaults to Scenarios/Default/TxtInOut)
 
		Examples
			$ swatpluseditor path/to/project-database.sqlite
			$ swatpluseditor path/to/project-database.sqlite --cmd-only --weather-dir=path/to/weather_files
`, {
		alias: {
			h: 'help'
		},
		default: {
			cmdOnly: false,
			weatherDir: '',
			weatherImportFormat: 'plus',
			weatherSaveDir: null,
			wgnImportMethod: 'database',
			wgnDb: 'C:/SWAT/SWATPlus/Databases/swatplus_wgn.sqlite',
			wgnTable: 'wgn_cfsr_world',
			wgnCsvStaFile: null,
			wgnCsvMonFile: null,
			yearStart: null,
			dayStart: null,
			yearEnd: null,
			dayEnd: null,
			inputFilesDir: null
		}
});
global.project_db = !DEV_MODE ? cli.input[0] : null;

let appsettings = require(join(app.getAppPath(), 'static/appsettings.json').replace('app.asar', 'app.asar.unpacked'));

const getScriptPath = (scriptName = 'swatplus_rest_api') => {
	if (DEV_MODE) {
		return join(app.getAppPath(), '..', '..', 'src', 'api', scriptName + '.py')
	} else if (appsettings.python) {
		return join(app.getAppPath(), 'static', 'api', scriptName + '.py').replace('app.asar', 'app.asar.unpacked')
	} else {
		if (process.platform === 'darwin') return join(app.getAppPath(), 'static', 'api_dist', scriptName, scriptName).replace('app.asar', 'app.asar.unpacked')
		return join(app.getAppPath(), 'static', 'api_dist', scriptName).replace('app.asar', 'app.asar.unpacked')
	}
}

const getSwatExeDirectory = () => {
	return join(app.getAppPath(), 'static', 'swat_exe').replace('app.asar', 'app.asar.unpacked');
}

const getSwatExeFile = (debug:boolean) => {
	let d = debug ? 'debug' : 'rel';
	if (process.platform === 'linux') d += '_linux';
	else if (process.platform === 'darwin') d += '_mac';

	return join(app.getAppPath(), 'static', 'swat_exe', 'rev' + appsettings.swatplus + '_64' + d).replace('app.asar', 'app.asar.unpacked');
}

const getSwatExeFileNew = (debug:boolean) => {
	let d = debug ? '-debug' : '';

	let p = '-win-amd64';
	if (process.platform === 'linux') p = '-lin-x86_64';
	else if (process.platform === 'darwin') p = '-mac-x86_64';

	return join(app.getAppPath(), 'static', 'swat_exe', 'swatplus-' + appsettings.swatplus + p + d).replace('app.asar', 'app.asar.unpacked');
}

const getLibPath = () => {
	let osqual = 'win';
	if (process.platform === 'linux') osqual = 'linux';
	else if (process.platform === 'darwin') osqual = 'mac';

	return join(app.getAppPath(), 'static', 'lib', osqual).replace('app.asar', 'app.asar.unpacked');
}

const getSwatPlusToolboxPath = () => {
	let path = join(app.getAppPath(), '../../../', 'SWATPlusToolbox', 'SWATPlusToolbox.exe');
	if (!fs.existsSync(path)) path = 'C:/SWAT/SWATPlus/SWATPlusToolbox/SWATPlusToolbox.exe';

	if (process.platform === 'linux') path = '';
	else if (process.platform === 'darwin') path = '';

	return path;
}

const getIahrisPath = () => {
	let path =
		findIahrisExe(join(__dirname, '../../../SWATPlus-IAHRIS')) ||
		findIahrisExe('C:/Program Files/SWATPlus-IAHRIS');

	if (process.platform === 'linux') path = '';
	else if (process.platform === 'darwin') path = '';

	return path;
}

function findIahrisExe(directory: string): string {
	if (!fs.existsSync(directory)) {
		return '';
	}

	const files = fs.readdirSync(directory);
	const exeRegex = /^SWATPlus-IAHRIS_v[\d.]+\.exe$/i;

	for (const file of files) {
		if (exeRegex.test(file)) {
			return join(directory, file);
		}
	}

	return '';
}

let mainWindow:BrowserWindow;

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
		title: 'SWAT+ Editor',
		icon: join(app.getAppPath(), 'static/256x256.ico'),
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

	mainWindow.webContents.setWindowOpenHandler(({ url }) => {
		return {
			action: 'allow',
			overrideBrowserWindowOptions: {
				title: 'SWAT+ Editor',
				icon: join(app.getAppPath(), 'static/256x256.ico'),
				webPreferences: {
					preload: join(__dirname, 'preload.js'),
					nodeIntegration: false,
					contextIsolation: true,
				}
			}
		}
	})
}

function setMainWindowLocation(location:string) {
	if (process.env.NODE_ENV === 'development') {
		const rendererPort = process.argv[2];
		mainWindow.loadURL(`http://localhost:${rendererPort}/#/${location}`);
	}
	else {
		mainWindow.loadFile(join(app.getAppPath(), 'renderer', `index.html/#/${location}`));
	}
}

app.whenReady().then(() => {
	if (cli.flags.cmdOnly) {
		const swat_exe = getSwatExeFile(false);

		var script_args = [
			'run',
			'--project_db_file=' + cli.input[0],
			'--editor_version=' + appsettings.version,
			'--swat_exe_file=' + swat_exe,
			'--weather_dir=' + cli.flags.weatherDir,
			'--weather_import_format=' + cli.flags.weatherImportFormat,
			'--wgn_import_method=' + cli.flags.wgnImportMethod,
			'--wgn_db=' + cli.flags.wgnDb,
			'--wgn_table=' + cli.flags.wgnTable
		]

		if (cli.flags.weatherSaveDir !== null) script_args.push('--weather_save_dir=' + cli.flags.weatherSaveDir);
		if (cli.flags.wgnCsvStaFile !== null) script_args.push('--wgn_csv_sta_file=' + cli.flags.wgnCsvStaFile);
		if (cli.flags.wgnCsvMonFile !== null) script_args.push('--wgn_csv_mon_file=' + cli.flags.wgnCsvMonFile);
		if (cli.flags.yearStart !== null) script_args.push('--year_start=' + cli.flags.yearStart);
		if (cli.flags.dayStart !== null) script_args.push('--day_start=' + cli.flags.dayStart);
		if (cli.flags.yearEnd !== null) script_args.push('--year_end=' + cli.flags.yearEnd);
		if (cli.flags.dayEnd !== null) script_args.push('--day_end=' + cli.flags.dayEnd);
		if (cli.flags.inputFilesDir !== null) script_args.push('--input_files_dir=' + cli.flags.inputFilesDir);

		let script = getScriptPath('swatplus_api');

		if (DEV_MODE || appsettings.python) {
			script_args.unshift(script);
			pythonProcess = child_process.spawn(appsettings.pythonPath, script_args);
		} else {
			pythonProcess = child_process.spawn(script, script_args);
		}
		pids.push(pythonProcess.pid);

		console.log(script);
		console.log(script_args);

		pythonProcess.stdout.on('data', (data) => {
			console.log(data.toString());
		});
		
		pythonProcess.stderr.on('data', (data) => {
			console.log(`stderr: ${data}`);
		});
		
		pythonProcess.on('close', (code) => {
			console.log('Done.');
			app.quit();
		});
	} else {
		let script = getScriptPath();

		portfinder.basePort = 5000;
		portfinder.getPortPromise()
			.then((port) => {
				global.api_port = port;
				
				if (DEV_MODE || appsettings.python) {
					pythonProcess = child_process.spawn(appsettings.pythonPath, [script, port.toString()]);
				} else {
					pythonProcess = child_process.spawn(script, [port.toString()]);
				}
				pids.push(pythonProcess.pid);
			
				if (pythonProcess != null) {
					console.log('SWAT+ API started: ' + port + ', process ID: ' + pythonProcess.pid);

					pythonProcess.stdout.on('data', (data) => {
						console.log(`stdout: ${data}`);
					});
				
					pythonProcess.stderr.on('data', (data) => {
						console.log(`stderr: ${data}`);
					});
				} else {
					console.log('SWAT+ API failed to start.');
				}
			
				createWindow();
				initColorTheme();

				if (process.platform === 'win32') {
					console.log('Checking for updates...');
					autoUpdater.checkForUpdates();
				}
			})
			.catch((err) => {
				console.log('Could not find port: ' + err);
			});
		

		session.defaultSession.webRequest.onHeadersReceived((details, callback) => {
			callback({
				responseHeaders: {
					...details.responseHeaders,
					'Content-Security-Policy': ['script-src \'self\'']
				}
			})
		})
	}
});

async function closeProcesses() {
	try {
		await axios.create({ baseURL: `http://127.0.0.1:${global.api_port}/` }).get('shutdown');
	} catch(error) {
		//console.log(error)
	}

	console.log('Killing API processes...');
	for (let pid of pids) {
		if (pid != undefined) {
			try {
				kill(pid);
			} catch(error) {}
		}
	}

	console.log('Press CTRL+C to exit');
}

app.on('window-all-closed', function () {
	//closeProcesses();
	if (process.platform !== 'darwin') app.quit()
});

app.on('before-quit', async () => {
	await closeProcesses();
});

//Auto Updater
function sendUpdateStatus(message:any, isAvailable:boolean) {
	let data = {
		message: message,
		isAvailable: isAvailable
	};
	mainWindow.webContents.send('app-update-status', JSON.stringify(data));
}

autoUpdater.on('checking-for-update', () => {
	sendUpdateStatus('Checking for updates...', false);
});

autoUpdater.on('update-available', (info) => {
	sendUpdateStatus(info.releaseNotes, true);
});

autoUpdater.on('update-not-available', (info) => {
	sendUpdateStatus('You are using the most recent version of SWAT+ Editor.', false);
});

autoUpdater.on('error', (err) => {
	sendUpdateStatus('Error in auto-updater. ' + err, false);
});

autoUpdater.on('download-progress', (progressObj) => {
	let data = {
		percent: progressObj.percent,
		message: `Downloading update ${Math.round(progressObj.percent)}%`
	};
	mainWindow.webContents.send('app-update-downloading', JSON.stringify(data));
});

autoUpdater.on('update-downloaded', (info) => {
	mainWindow.webContents.send('app-update-downloaded', 'Update downloaded.');
});

/*app.on('ready', function()  {
	if (process.platform === 'win32') {
		console.log('Checking for updates...');
		autoUpdater.checkForUpdates();
	}
});*/

ipcMain.on('download-update', (event, arg) => {
	autoUpdater.downloadUpdate();
});

ipcMain.on('quit-and-install-update', async (event, arg) => {
	await closeProcesses();
	autoUpdater.quitAndInstall();
});

ipcMain.on('manual-update-check', (event, arg) => {
	console.log('Checking for updates...');
	autoUpdater.checkForUpdates();
});

//IPC functions to connect to renderer
ipcMain.on('message', (event, message) => {
	console.log(message);
})

ipcMain.on('set-window-title', (event, message:string) => {
	mainWindow.setTitle(message);
})

ipcMain.on('globals', (event, arg) => {
	event.returnValue = {
		dev_mode: DEV_MODE,
		platform: process.platform,
		project_db: global.project_db,
		api_port: global.api_port,
		locale: app.getLocale(),
		swat_path: getSwatExeDirectory(),
	};
})

ipcMain.on('get-app-settings', (event, arg) => {
	event.returnValue = appsettings;
})

ipcMain.on('add-to-store', (event, key, value) => {
	if (store.has(key))
		store.delete(key);
	store.set(key, value);
})

ipcMain.on('get-store-setting', (event, key) => {
	let value:any = store.get(key);
	event.returnValue = value;
})

ipcMain.on('delete-from-store', (event, key) => {
	if (store.has(key))
		store.delete(key);
})

ipcMain.on('get-app-path', (event, arg) => {
	event.returnValue = join(app.getAppPath(), 'static');
})

ipcMain.on('quit-app', (event, arg) => {
	app.quit();
})

ipcMain.on('path-exists', (event, directory) => {
	if (directory === undefined || directory === null || directory === '') event.returnValue = false;
	event.returnValue = fs.existsSync(directory);
})

ipcMain.on('join-paths', (event, paths) => {
	if (paths.length == 0) event.returnValue = '';
	let dir = paths[0];
	for (let i = 1; i < paths.length; i++) {
		dir = join(dir, paths[i]);
	}
	event.returnValue = dir;
})

ipcMain.on('path-directory-name', (event, directory) => {
	if (directory === undefined || directory === null || directory === '') event.returnValue = false;
	event.returnValue = dirname(directory);
})

ipcMain.on('open-file-on-system', (event, file) => {
	let sanFile = file;
	if (process.platform === 'win32') sanFile = sanFile.replace(/\//ig, '\\');
	shell.openPath(sanFile);
})

ipcMain.on('open-url', (event, url) => {
	shell.openExternal(url);
})

ipcMain.on('open-file-dialog', (event, options) => {
	event.returnValue = dialog.showOpenDialogSync(mainWindow, options);
})

ipcMain.on('save-file-dialog', (event, options) => {
	event.returnValue = dialog.showSaveDialogSync(mainWindow, options);
})

ipcMain.on('spawn-process', (event, proc_name:string, script_name:string, args:string[]) => {
	console.log(`proc_name: ${proc_name}`)
	console.log(`script_name: ${script_name}`)
	console.log(`args: ${args}`)
	let script = getScriptPath(script_name);
	if (DEV_MODE || appsettings.python) {
		args.unshift(script);
		script = appsettings.pythonPath;
	} 
	
	let ipcProcess = child_process.spawn(script, args);
	pids.push(ipcProcess.pid);
	let stderrChunks = [];
	ipcProcess.stdout.on('data', (data) => {
		console.log(`stdout: ${data}`);
		mainWindow.webContents.send(`process-stdout-${proc_name}`, data.toString());
	});

	ipcProcess.stderr.on('data', (data) => {
		console.log(`stderr: ${data}`);
		stderrChunks = stderrChunks.concat(data);
	});
	ipcProcess.stderr.on('end', () => {
		let stderrContent = Buffer.concat(stderrChunks).toString();
		if (stderrContent === undefined || stderrContent === null || stderrContent.trim() === '') {
			//mainWindow.webContents.send('process-close', 1);
		} else {
			mainWindow.webContents.send(`process-stderr-${proc_name}`, stderrContent);
		}
	});
	
	ipcProcess.on('close', (code) => {
		mainWindow.webContents.send(`process-close-${proc_name}`, code);
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

ipcMain.on('run-swat', (event, debug:boolean, inputDir:string) => {
	let swatExe = getSwatExeFile(debug);

	//Set env var for linking to libiomp5 library
	if (process.platform === 'darwin') {
		process.env.DYLD_FALLBACK_LIBRARY_PATH = getLibPath();
	}
	
	let ipcProcess = child_process.spawn(swatExe, [], { cwd: inputDir });
	pids.push(ipcProcess.pid);
	let stderrChunks = [];
	
	ipcProcess.stdout.on('data', (data) => {
		mainWindow.webContents.send('process-stdout-run-swat', data.toString());
	});

	ipcProcess.stderr.on('data', (data) => {
		console.log(`stderr: ${data}`);
		stderrChunks = stderrChunks.concat(data);
	});
	ipcProcess.stderr.on('end', () => {
		let stderrContent = Buffer.concat(stderrChunks).toString();
		if (stderrContent === undefined || stderrContent === null || stderrContent.trim() === '') {
			//mainWindow.webContents.send('process-close', 1);
		} else {
			mainWindow.webContents.send('process-stderr-run-swat', stderrContent);
		}
	});
	
	ipcProcess.on('close', (code) => {
		mainWindow.webContents.send('process-close-run-swat', code);
	});

	event.returnValue = ipcProcess.pid;
})

ipcMain.on('get-swatplustoolbox-path', (event) => {
	event.returnValue = getSwatPlusToolboxPath();
})

ipcMain.on('launch-swatplustoolbox', (event, projectDb:string) => {
	if (process.platform !== 'win32') event.returnValue = 'SWAT+ Toolbox is currently only available on Windows.';
	else {
		let path = getSwatPlusToolboxPath();
		if (!fs.existsSync(path)) event.returnValue = `Could not find SWAT+ Toolbox at "${path}"`;
		else {
			child_process.exec(`"${path}" "${projectDb}"`)
			event.returnValue = null;
		}
	}
})

ipcMain.on('get-iahris-path', (event) => {
	event.returnValue = getIahrisPath();
})

ipcMain.on('launch-iahris', (event, scenariosPath:string) => {
	if (process.platform !== 'win32') event.returnValue = 'SWATPlus-IAHRIS is currently only available on Windows.';
	else {
		let path = getIahrisPath();
		if (!fs.existsSync(path)) event.returnValue = `Could not find SWATPlus-IAHRIS at "${path}"`;
		else {
			child_process.exec(`"${path}" "${scenariosPath}"`)
			event.returnValue = null;
		}
	}
})

ipcMain.on('set-color-theme', (event, colorTheme:string) => {
	setColorTheme(colorTheme);
})

ipcMain.on('get-color-theme', (event) => {
	if (nativeTheme.shouldUseDarkColors) event.returnValue = 'dark';
	else event.returnValue = nativeTheme.themeSource;
})

function setColorTheme(colorTheme:string) {
	switch(colorTheme) //while this seems redundant, themeSource can't be set to a variable
	{
		case 'dark':
			nativeTheme.themeSource = 'dark';
			break;
		case 'light':
			nativeTheme.themeSource = 'light';
			break;
		default:
			nativeTheme.themeSource = 'system';
			break;
	}
}

function initColorTheme() {
	let colorTheme = 'light';
	if (nativeTheme.themeSource === 'dark' || nativeTheme.shouldUseDarkColors) colorTheme = 'dark';
	setColorTheme(colorTheme);
}

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
				label: 'Help Using SWAT+ Editor',
				click () { mainWindow.webContents.send('load-from-context-menu', 'help') }
			},
			{
				label: 'SWAT+ Editor Documentation',
				click () { shell.openExternal('https://swatplus.gitbook.io/docs/') }
			},
			{
				label: 'SWAT+ Input/Output Documentation',
				click () { shell.openExternal('https://swatplus.gitbook.io/io-docs/') }
			},
			{
				label: 'SWAT+ Release Notes',
				click () { shell.openExternal('https://swatplus.gitbook.io/docs/release-notes') }
			},
			{
				label: 'SWAT Website',
				click () { shell.openExternal('https://swat.tamu.edu') }
			},
			{type: 'separator'},
			{
				label: 'Report a problem using the editor',
				click () { shell.openExternal('https://groups.google.com/d/forum/swatplus-editor') }
			},
			{
				label: 'Report a model error',
				click () { shell.openExternal('https://groups.google.com/d/forum/swatplus') }
			},
			{type: 'separator'},
			{
				label: 'Check for updates...',
				click () { mainWindow.webContents.send('load-from-context-menu', 'update') }
			},
			{
				label: 'See releases on Github',
				click () { shell.openExternal('https://github.com/swat-model/swatplus-editor/releases') }
			}
		]
	}
];

const menu = Menu.buildFromTemplate(template);
Menu.setApplicationMenu(menu);
