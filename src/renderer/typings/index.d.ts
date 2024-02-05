export interface ElectronGlobals {
	dev_mode: boolean;
	platform: string|null;
	project_db: string|null;
	api_port: number|null;
	locale: string|null;
}

export interface ElectronAppSettings {
	version: string;
	swatplus: string;
	python: boolean;
	pythonPath: string;
}

export interface ProjectSettings {
	projectDb: string|null;
	datasetsDb: string|null;
	name: string|null;
	description: string|null;
	version: string|null;
	isLte: boolean;
}

export interface GridViewHeader {
	key: string;
	label?: string|null;
	noSort?: boolean|null;
	class?: string|null;
	type?: 'string'|'int'|'number'|'boolean'|'object'|'file'|'variable-object'|null;
	decimals?: number|null;
	objectValueField?: string|null;
	objectTextField?: string|null;
	objectRoutePath?: string|null;
	filePath?: string|null;
	defaultIfNull?: string|null;
	formatter?: (value:any) => string;
}