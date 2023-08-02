# README #

Desktop interface to SWAT+ allowing the user to import a project from GIS, modify SWAT+ input, write the text files, and run the model.

Read the documentation at [swatplus.gitbook.io/docs](https://swatplus.gitbook.io/docs) and [join the user group](https://groups.google.com/g/swatplus-editor) to be notified of new releases.

## Installing and running the source code ##

### Back-end development stack ###

1. Install [Python 3](https://www.python.org/) (version 3.10 and up)
2. Install required Python packages
    * From command prompt, go to source code `/src/api` directory
    * Run `pip install -r requirements.txt` (might be `pip3` on Linux and MacOS)
3. Update the `/src/main/static/appsettings.json` file with your python PATH variable (typically `python` on Windows and `python3` on Linux and MacOS)

### Front-end development stack ###

1. Install [Node.js](https://nodejs.org/en/) (version 18 LTS)
2. Install required Node.js packages
    * From command prompt, go to the root directory of the source code
    * Run `npm install`

### Running the source code ###

1. If needed, adjust the `pythonPath` setting in `/src/main/static/appsettings.json`; change to `python` (Windows) or `python3` (Linux/MacOS)
1. From command prompt, go to the root directory of the source code
2. Run `npm run dev`

### Development tools ###

1. [Visual Studio Code](https://code.visualstudio.com/)

### Build the source code ###

1. From `/src/api` run the following depending on your OS:
	* Windows: `python-build-windows`
	* Linux: `sh python-build-linux.sh`
	* MacOS: `sh python-build-mac.sh`
2. From the root of the source code directory run the following depending on your OS:
	* Windows: `npm run build:win`
	* Linux: `npm run build:linux`
	* MacOS: `npm run build:mac`
3. Program will be in `/release/dist`
