interface ElectronGlobals {
	dev_mode: boolean;
	platform: string|null;
	project_db: string|null;
	api_port: number|null;
}

interface ElectronAppSettings {
	version: string;
	swatplus: string;
	python: boolean;
	pythonPath: string;
}

interface ProjectSettings {
	projectDb: string|null;
	datasetsDb: string|null;
	name: string|null;
	description: string|null;
	version: string|null;
	isLte: boolean;
}